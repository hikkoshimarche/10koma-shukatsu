#!/usr/bin/env python3
"""drift_monitor — 毎晩のズレ監視(⑤-⑤ 2026-11-19)。読取のみ(D1・ファイルに書かない)。

本番 D1 company_panels と台本ファイル(scenario_v4.json)を全社・全列で比較し、方向を判定する:
  D1新   = D1 の値が台本ファイルのどの版にも無い(=D1 が直接書かれた) → 1件でも緊急通知(LINE pushoscar)
  file新 = D1 の値がファイルの過去版 → 未反映(警告・ログのみ)
  例外   = drift_exceptions.json に理由・期限付きで登録したもの。期限切れは自動で警告に戻す。
あわせて check_d1_writers(許可外の company_panels 書込経路)を実行し、FAIL も緊急通知。
結果は logs/drift_monitor_last.json に保存。
"""
import contextlib
import datetime as dt
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
PIPE = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PIPE / "scripts"))
with contextlib.redirect_stdout(io.StringIO()):
    import scenario_to_panels as S2P  # noqa: E402
import deploy_salary as D  # noqa: E402
import check_d1_writers as CW  # noqa: E402

EXC = TOOLS / "drift_exceptions.json"
OUT = REPO / "logs" / "drift_monitor_last.json"
TEXT_PAIR = {"dialogue": "script_json", "script_json": "dialogue"}


def load_exceptions(today):
    items = json.loads(EXC.read_text(encoding="utf-8"))["items"]
    active, expired = {}, []
    for x in items:
        for k in ("slug", "panel", "fields", "reason", "expires"):
            if not x.get(k):
                raise SystemExit(f"drift_exceptions.json: {k} が無い項目 {x}(理由・期限は必須)")
        fs = set(x["fields"]) | {TEXT_PAIR[f] for f in x["fields"] if f in TEXT_PAIR}
        if dt.date.fromisoformat(x["expires"]) < today:
            expired.append(x)
            continue
        for f in fs:
            active[(x["slug"], int(x["panel"]), f)] = x
    return active, expired


def main(argv):
    today = dt.date.today()
    active, expired = load_exceptions(today)
    n_expect = D.d1_query("SELECT COUNT(*) n FROM company_panels")[0]["n"]
    rows = D.d1_query("SELECT company_id,panel_num," + ",".join(S2P.GUARD_FIELDS) + " FROM company_panels")
    if not rows or len(rows) != n_expect:
        raise SystemExit(f"D1取得件数不一致 {len(rows) if rows else 0}/{n_expect}(空≠不在)→ 判定しない")
    live = defaultdict(dict)
    for r in rows:
        live[r["company_id"]][int(r["panel_num"])] = r
    rev = {v: k for k, v in S2P.SLUG_MAP.items()}
    res = {"at": dt.datetime.now().isoformat(timespec="seconds"), "companies": len(live), "rows": len(rows),
           "d1_new": [], "file_new": [], "excepted": [], "no_file": [], "dirty_file": [],
           "expired_exceptions": [f"{x['slug']}#{x['panel']} {x['fields']} 期限{x['expires']}" for x in expired]}
    for slug in sorted(live):
        tok = rev.get(slug, slug)
        rel = f"output/{tok}/scenario_v4.json"
        fp = PIPE / rel
        if not fp.exists():
            res["no_file"].append(slug)
            continue
        scn = json.loads(fp.read_text(encoding="utf-8"))
        exp = S2P._expected_rows(scn, slug, "REF")
        hist = None
        dirty = subprocess.run(["git", "-C", str(PIPE), "diff", "--quiet", "HEAD", "--", rel]).returncode != 0
        if dirty:
            res["dirty_file"].append(slug)
        for n, l in sorted(live[slug].items()):
            e = exp.get(n)
            if e is None:
                res["d1_new"].append(f"{slug}#{n}: ファイルに無いコマ")
                continue
            for f in S2P.GUARD_FIELDS:
                if S2P._norm(f, e[f]) == S2P._norm(f, l[f]):
                    continue
                if hist is None:
                    hist = [S2P._expected_rows(h, slug, "REF") for h in S2P._history_scenarios(tok)]
                    if dirty:
                        head = subprocess.run(["git", "-C", str(PIPE), "show", f"HEAD:{rel}"],
                                              capture_output=True, text=True)
                        if head.returncode == 0:
                            hist.append(S2P._expected_rows(json.loads(head.stdout), slug, "REF"))
                key = f"{slug}#{n}.{f}"
                if (slug, n, f) in active:
                    res["excepted"].append(key)
                elif S2P._norm(f, l[f]) in {S2P._norm(f, h.get(n, {}).get(f)) for h in hist}:
                    res["file_new"].append(key)
                else:
                    res["d1_new"].append(key)
    bad, seen = CW.scan()
    res["writer_check"] = {"files": seen, "fail": bad}
    import nen_lint as NL   # 会社年齢「◯年」の陳腐化(創業年マスタ照合)。ログのみ・LINE通知しない
    res["nen_lint"] = NL.run_all()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    cnt = {k: len(v) for k, v in res.items() if isinstance(v, list)}
    print(f"[drift_monitor] {res['at']} 社{res['companies']} 行{res['rows']} " + " ".join(f"{k}={v}" for k, v in cnt.items())
          + f" writer_fail={len(bad)} nen_error={len(res['nen_lint']['error'])} nen_warning={len(res['nen_lint']['warning'])}")
    for x in res["nen_lint"]["error"][:20]:
        print(f"  [nen_error] {x}")
    for k in ("d1_new", "expired_exceptions", "no_file", "dirty_file"):
        for x in res[k][:20]:
            print(f"  [{k}] {x}")
    if res["file_new"]:
        print("  [file_new 社別]", dict(Counter(x.split("#")[0] for x in res["file_new"])))
    alerts = []
    if res["d1_new"]:
        alerts.append(f"D1が台本ファイルより新しい項目 {len(res['d1_new'])}件(D1直書きの疑い): {res['d1_new'][:5]}")
    if bad:
        alerts.append(f"許可外の company_panels 書込経路 {len(bad)}件: {bad[:3]}")
    if alerts and "--no-alert" not in argv:
        import phase_c_image_fix as PCI
        PCI.push_line("🛑【トーキャリ ズレ監視】\n" + "\n".join(alerts) + "\n詳細: logs/drift_monitor_last.json",
                      emergency=True)
    return 2 if alerts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
