#!/usr/bin/env python3
"""scenario_writer — 台本の唯一の書き込み口(ファイル先行・2026-11-19 ⑤ オスカー承認)。

台本の列(dialogue/script_json/main_copy/sub_copy/character)を本番 D1 に書く処理は、必ず apply() を通す。
D1 を直接 UPDATE してから scenario_v4.json に書き戻さない旧経路(deploy_fb 等)が 216社のズレを生んだため。

apply(slug, edits, reason) の順序:
  1. 対象 scenario_v4.json に未コミット変更があれば拒否(持ち主不明の変更を巻き込まない)
  2. edits({koma: {"script":[...], "main_copy":str|None, "sub_copy":str|None}})を台本に当てる
  3. 全部入り lint(scenario_to_panels.run_lint_gate)= error 0 でなければ中止(ファイルも D1 も書かない)
  4. D1関所(plan_guarded)で計画。編集したコマの台本列以外に差分がある・拒否がある → 中止
     (その社に未解決のズレがある=先に解消する。黙って他の列まで出さない)
  5. scenario_v4.json を書いて tokyari-pipeline に commit
  6. D1 backup → canary(前) → 旧値一致条件付き UPDATE → changes が文数と一致するか照合 → canary(後)
     canary の変化が対象社以外に出たら例外(要調査)
  D1 書込が失敗してもファイルは先に進んでいるだけ=次回 apply/関所で揃う(D1 が新しい状態は作らない)。

current(slug) は台本ファイルを正として現行値を返す(api/migration_v4_<slug>.sql は元データに使わない)。
"""
import copy
import contextlib
import io
import json
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
PIPE = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PIPE / "scripts"))
with contextlib.redirect_stdout(io.StringIO()):
    import scenario_to_panels as S2P  # noqa: E402
import deploy_salary as D  # noqa: E402  (wrangler/_parse_d1_results: cf_env・npx 解決済み)

TEXT_FIELDS = ("character", "dialogue", "script_json", "main_copy", "sub_copy")
SYNC_FIELDS = TEXT_FIELDS + ("source_url",)   # sync_from_file で出してよい列(画像系は除く)
BACKUP = REPO / ".backups"


class WriterError(RuntimeError):
    """apply の中止(書き込み前の検査で止まった/書き込み後の照合が合わない)。"""


def tok_of(slug: str) -> str:
    rev = {v: k for k, v in S2P.SLUG_MAP.items()}
    return rev.get(slug, slug)


def scenario_rel(slug: str) -> str:
    return f"output/{tok_of(slug)}/scenario_v4.json"


def _git(*a, check=True):
    return subprocess.run(["git", "-C", str(PIPE), *a], capture_output=True, text=True, check=check)


def _dirty(rel: str) -> bool:
    return subprocess.run(["git", "-C", str(PIPE), "diff", "--quiet", "HEAD", "--", rel]).returncode != 0


def _dump_like(text: str, data) -> str:
    """元ファイルの書式(indent2 / compact・末尾改行)を保って書く(差分ノイズを出さない)。"""
    for f in (lambda d: json.dumps(d, ensure_ascii=False, indent=2), lambda d: json.dumps(d, ensure_ascii=False)):
        try:
            if f(json.loads(text)) == text.rstrip("\n"):
                return f(data) + text[len(text.rstrip("\n")):]
        except Exception as e:  # 元ファイル不正は上で json.loads 済のため起きない想定 → 握り潰さない
            raise WriterError(f"書式判定に失敗: {e}")
    raise WriterError("元ファイルの書式を再現できない(indent2/compact 以外)→ 書かない")


def current(slug: str) -> dict:
    """台本ファイル(scenario_v4.json)の現行 {koma: {script, main_copy, sub_copy}}。"""
    p = PIPE / scenario_rel(slug)
    if not p.exists():
        raise WriterError(f"台本ファイルが無い: {p}")
    scn = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for k in scn["koma"]:
        ov = k.get("overlay_text") or {}
        out[int(k["koma_number"])] = {"script": list(k.get("script") or []),
                                      "main_copy": ov.get("main_copy") or None,
                                      "sub_copy": (ov.get("sub") or ov.get("sub_copy")) or None}
    if not out:
        raise WriterError(f"{slug}: 台本のコマが0件(空=失敗)")
    return out


def _apply_edits(scn: dict, edits: dict) -> dict:
    new = copy.deepcopy(scn)
    km = {int(k["koma_number"]): k for k in new["koma"]}
    for n, after in edits.items():
        n = int(n)
        if n not in km:
            raise WriterError(f"koma{n} が台本に無い")
        k = km[n]
        if "script" in after:
            if not isinstance(after["script"], list) or not all(isinstance(x, str) for x in after["script"]):
                raise WriterError(f"koma{n}: script は文字列の配列であること")
            k["script"] = list(after["script"])
        if "source" in after:   # overlay_text.source → D1 source_url(2026-11-20: 数字の出典docIDを付けるため)
            ov = k.setdefault("overlay_text", {})
            if after["source"] in (None, ""):
                ov.pop("source", None)
            else:
                ov["source"] = after["source"]
        if "main_copy" in after or "sub_copy" in after:
            ov = k.setdefault("overlay_text", {})
            if "main_copy" in after:
                if after["main_copy"] in (None, ""):
                    ov.pop("main_copy", None)
                else:
                    ov["main_copy"] = after["main_copy"]
            if "sub_copy" in after:
                key = "sub" if ("sub" in ov or "sub_copy" not in ov) else "sub_copy"
                if after["sub_copy"] in (None, ""):
                    ov.pop("sub", None)
                    ov.pop("sub_copy", None)
                else:
                    ov[key] = after["sub_copy"]
                    if key == "sub":
                        ov.pop("sub_copy", None)
    return new


def plan(slug: str, edits: dict, ref: str | None = None, d1_rows=None, image_komas=None):
    """書き込み前の検査と計画(ファイル/D1 を書かない)。WriterError で中止理由を返す。
    戻り値: (new_scenario, updates{n:{f:(new,old)}}, sql_list)"""
    rel = scenario_rel(slug)
    if _dirty(rel):
        raise WriterError(f"{rel} に未コミット変更あり → 拒否(先に内容を確認して commit する)")
    tok = tok_of(slug)
    path = PIPE / rel
    scn = json.loads(path.read_text(encoding="utf-8"))
    new = _apply_edits(scn, edits)
    errs = S2P.run_lint_gate(new, tok)
    if errs:
        raise WriterError(f"[lint] {slug}: error {len(errs)}件 → 中止\n" + "\n".join(errs))
    ref = ref or subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    exp_new = S2P._expected_rows(new, slug, ref)
    exp_old = S2P._expected_rows(scn, slug, ref)
    rows = S2P._d1_current(slug) if d1_rows is None else d1_rows
    if not rows:
        raise WriterError(f"{slug}: D1 に行が無い(新規社は scenario_to_panels で INSERT する)")
    # 現在のファイルと D1 が編集対象外の列/コマでも一致していること(未解決のズレがある社には書かない)
    _u0, ref0 = S2P.plan_guarded(tok, slug, exp_old, rows, ref, None, [])
    if _u0 or ref0:
        pend = [f"panel{n}.{f}" for n, v in _u0.items() for f in v] + ref0
        raise WriterError(f"{slug}: 書込前から ファイルとD1 にズレ {len(pend)}件 → 先に解消: {pend[:6]}")
    # 上の検査で D1 == 現行ファイル(全列)が確定 → 差分は「新しい台本 − 現行台本」だけ。旧値=D1 現在値。
    live = {int(r["panel_num"]): r for r in rows}
    updates = {}
    for n in exp_new:
        for f in S2P.GUARD_FIELDS:
            if f == "image_url":
                if n in (image_komas or ()) and S2P._norm(f, exp_new[n][f]) == S2P._norm(f, live[n][f]) \
                        and (live[n][f] or "") != exp_new[n][f]:
                    rel = S2P._image_relation(live[n][f], ref, slug, n)
                    if rel not in ("older", "same"):
                        raise WriterError(f"{slug} panel{n}: 画像 ref が新 ref の祖先でない({rel})→ 中止")
                    if rel == "older":
                        updates.setdefault(n, {})[f] = (exp_new[n][f], live[n][f])
                continue
            if S2P._norm(f, exp_new[n][f]) != S2P._norm(f, exp_old[n][f]):
                updates.setdefault(n, {})[f] = (exp_new[n][f], live[n][f])
    for n, v in updates.items():
        if any(f in v for f in S2P.IMAGE_COUPLED_FIELDS) and "image_url" not in v:
            raise WriterError(f"{slug} panel{n}: 画像とセットの列だけが変わる → 画像と同時でなければ書かない")
    allowed = {(int(n), f) for n in edits for f in TEXT_FIELDS}
    allowed |= {(int(n), "source_url") for n, a in edits.items() if "source" in a}
    allowed |= {(int(n), f) for n in (image_komas or ()) for f in ("image_url",) + S2P.IMAGE_COUPLED_FIELDS}
    extra = [(n, f) for n, v in updates.items() for f in v if (n, f) not in allowed]
    if extra:
        raise WriterError(f"{slug}: 編集対象外の列に差分 {extra} → 中止")
    sql = []
    for n in sorted(updates):
        sets = ", ".join(f"{f}={S2P.sql_quote(a)}" for f, (a, _b) in updates[n].items())
        conds = " AND ".join(f"{f} IS {S2P.sql_quote(b)}" for f, (_a, b) in updates[n].items())
        sql.append(f"UPDATE company_panels SET {sets} WHERE company_id={S2P.sql_quote(slug)} "
                   f"AND panel_num={n} AND {conds};")
    return new, updates, sql


def _exec(sql_list):
    """--file で一括実行し、wrangler 出力 JSON の meta.changes 合計を返す(--file は文ごとでなく集計1件を返す)。"""
    p = BACKUP / "writer_tmp.sql"
    BACKUP.mkdir(exist_ok=True)
    p.write_text("\n".join(sql_list) + "\n", encoding="utf-8")
    try:
        proc = D.wrangler(["--file", str(p), "--json"], timeout=180)
        txt = proc.stdout or ""
        try:
            data = json.loads(txt[txt.index("["):])
            if not data or not all(x.get("success") for x in data):
                raise ValueError("success でない")
            return sum(int((x.get("meta") or {})["changes"]) for x in data)
        except Exception as e:
            raise WriterError(f"D1 実行失敗/結果不明({e}): {txt[-300:]} {(proc.stderr or '')[-300:]}")
    finally:
        p.unlink(missing_ok=True)


def _canary_snapshot(tag):
    out = BACKUP / "canary" / f"{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(TOOLS / "_canary.py"), "snapshot", str(out)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise WriterError(f"canary snapshot 失敗: {r.stderr[-300:]}")
    return out


def _canary_changed(before, after):
    a, b = json.loads(before.read_text()), json.loads(after.read_text())
    if not a or not b:
        raise WriterError("canary が空(空=失敗)")
    return sorted({k for k in set(a) | set(b) if a.get(k) != b.get(k)})


def apply(slug: str, edits: dict, reason: str, dry: bool = False, image_komas=None, ref=None, push=True) -> dict:
    """台本の唯一の書き込み口。dry=True は検査と計画のみ(ファイル/D1/git に一切書かない)。"""
    if not edits:
        raise WriterError("edits が空(空=失敗。書くものが無いなら呼ばない)")
    new, updates, sql = plan(slug, edits, ref=ref, image_komas=image_komas)
    res = {"slug": slug, "komas": sorted(int(n) for n in edits), "updates": {n: list(v) for n, v in updates.items()},
           "sql": sql, "dry": dry, "commit": None, "changes": None, "canary_changed": None}
    if dry or not sql:
        res["note"] = "dry(書込なし)" if dry else "変更なし(D1 と一致)"
        return res
    rel = scenario_rel(slug)
    path = PIPE / rel
    text = path.read_text(encoding="utf-8")
    path.write_text(_dump_like(text, new), encoding="utf-8")
    _git("add", "--", rel)
    _git("commit", "-q", "-m", f"fix(台本/{slug}): {reason[:120]}\n\nscenario_writer.apply(ファイル先行→lint→関所UPDATE) "
         f"komas={res['komas']}")
    res["commit"] = _git("rev-parse", "--short", "HEAD").stdout.strip()
    if push:
        pr = _git("push", "-q", "origin", "HEAD", check=False)
        res["push"] = "ok" if pr.returncode == 0 else f"失敗(後で push): {pr.stderr[-200:]}"
    _write_d1(slug, sql, res)
    return res


def sync_from_file(slug: str, komas, reason: str, dry: bool = False) -> dict:
    """台本ファイルが先行しているコマ(D1=ファイル履歴の値)を、そのコマの台本列だけ D1 に出す。
    旧 sync_salary_to_d1(migration SQL→D1)の置換。D1 に履歴に無い値があれば拒否。ファイルは書かない。"""
    komas = {int(k) for k in komas}
    if not komas:
        raise WriterError("komas が空(空=失敗)")
    rel = scenario_rel(slug)
    if _dirty(rel):
        raise WriterError(f"{rel} に未コミット変更あり → 拒否")
    scn = json.loads((PIPE / rel).read_text(encoding="utf-8"))
    errs = S2P.run_lint_gate(scn, tok_of(slug))
    if errs:
        raise WriterError(f"[lint] {slug}: error {len(errs)}件 → 中止\n" + "\n".join(errs))
    ref = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    exp = S2P._expected_rows(scn, slug, ref)
    rows = S2P._d1_current(slug)
    updates, refused = S2P.plan_guarded(tok_of(slug), slug, exp, rows, ref, None, [])
    bad = [r for r in refused if any(r.startswith(f"panel{n}.") for n in komas)]
    if bad:
        raise WriterError(f"{slug}: 関所が拒否(D1 の方が新しい) {bad[:3]}")
    sel = {n: {f: v for f, v in u.items() if f in SYNC_FIELDS} for n, u in updates.items() if n in komas}
    sel = {n: u for n, u in sel.items() if u}
    sql = []
    for n in sorted(sel):
        sets = ", ".join(f"{f}={S2P.sql_quote(a)}" for f, (a, _b) in sel[n].items())
        conds = " AND ".join(f"{f} IS {S2P.sql_quote(b)}" for f, (_a, b) in sel[n].items())
        sql.append(f"UPDATE company_panels SET {sets} WHERE company_id={S2P.sql_quote(slug)} "
                   f"AND panel_num={n} AND {conds};")
    res = {"slug": slug, "komas": sorted(komas), "updates": {n: list(v) for n, v in sel.items()},
           "sql": sql, "dry": dry, "changes": None, "canary_changed": None, "reason": reason}
    if dry or not sql:
        res["note"] = "dry(書込なし)" if dry else "変更なし(D1 と一致)"
        return res
    _write_d1(slug, sql, res)
    return res


def _write_d1(slug, sql, res):
    """backup → canary(前) → 実行 → changes 照合 → canary(後)。res に結果を書く。"""
    ts = time.strftime("%Y%m%d_%H%M%S")
    rows = D.d1_query(f"SELECT * FROM company_panels WHERE company_id='{slug}' ORDER BY panel_num")
    if not rows:
        raise WriterError(f"{slug}: backup 用 D1 読取が空(空=失敗)→ D1 は書いていない")
    (BACKUP / "d1").mkdir(parents=True, exist_ok=True)
    (BACKUP / "d1" / f"writer_{slug}_{ts}.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    cb = _canary_snapshot(f"writer_{slug}_before_{ts}")
    changes = _exec(sql)
    res["changes"] = changes
    ca = _canary_snapshot(f"writer_{slug}_after_{ts}")
    res["canary_changed"] = _canary_changed(cb, ca)
    if changes != len(sql):
        raise WriterError(f"{slug}: changes={changes}(期待 {len(sql)})→ 旧値一致せず=D1 が途中で変わった可能性。要確認")
    if res["canary_changed"] != [slug]:
        raise WriterError(f"{slug}: canary の変化が対象社だけでない {res['canary_changed']} → 要調査")
    return res


def selftest() -> int:
    """書込みなしの回帰(D1 行を注入・lint/関所/対象外列の検査)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✅' if cond else '❌'} {name}")
    slug = "ibm-consulting"
    ref = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    scn = json.loads((PIPE / scenario_rel(slug)).read_text(encoding="utf-8"))
    exp = S2P._expected_rows(scn, slug, ref)
    rows = [{"company_id": slug, "panel_num": n, **v} for n, v in exp.items()]
    cur = current(slug)
    k = 7
    after = {**cur[k], "script": cur[k]["script"][:-1] + [cur[k]["script"][-1].rstrip("。") + "。"]}
    if after["script"] == cur[k]["script"]:
        after["script"] = cur[k]["script"] + ["[nana] なるほど。"]
    _n, u, sql = plan(slug, {k: after}, ref=ref, d1_rows=rows)
    chk("通常の編集 → 該当コマだけ UPDATE(旧値一致条件付き)", list(u) == [k] and len(sql) == 1 and " IS " in sql[0])
    bad = {**cur[k], "script": cur[k]["script"] + ["[nana] 倍率は100倍らしいよ。"]}
    try:
        plan(slug, {k: bad}, ref=ref, d1_rows=rows)
        chk("倍率を入れた編集 → lint で中止", False)
    except WriterError as e:
        chk("倍率を入れた編集 → lint で中止", "[lint]" in str(e))
    drift = copy.deepcopy(rows)
    drift[0]["dialogue"] = "[nana] D1に直接書かれた値"
    try:
        plan(slug, {k: after}, ref=ref, d1_rows=drift)
        chk("他コマに未解決ズレ → 中止", False)
    except WriterError as e:
        chk("他コマに未解決ズレ → 中止", "ズレ" in str(e))
    _n, u, sql = plan(slug, {k: cur[k]}, ref=ref, d1_rows=rows)
    chk("変更なしの編集 → SQL なし", not sql)
    print("=== scenario_writer selftest:", "ALL PASS ✅" if ok else "FAIL ❌", "===")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(__doc__)
