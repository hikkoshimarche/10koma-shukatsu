#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_salary.py — 年収共通ルールを全商社に本番反映(通常ゲート)。三井除外。

ゲート: apply(台本SQL修正+lint) → D1バックアップ → 他社(mitsui)ハッシュ確認 →
        台本列のみUPDATE(image_url不変) → mitsuiハッシュ再確認 → 本番API検証。

  --apply   : 台本SQL修正 + lint のみ (D1非反映・backup付き)
  --deploy  : 上記 + D1へ台本列UPDATE反映 (バックアップ+canary)

安全: 台本列(dialogue/script_json/main_copy/sub_copy)のみUPDATEしimage_urlは触らない。
      全変更を .backups/ に保存し可逆。mitsui-bussanは除外かつcanary監視。
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import salary_rule_dryrun as S   # noqa: E402

DB = "10koma-shukatsu-db"
WRANGLER_CONFIG = "api/wrangler.toml"
API_BASE = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
BACKUP = REPO / ".backups"
CANARY = "mitsui-bussan"  # 三井=対象外。変化しないことをcanaryで監視


import shutil as _shutil


def _npx():
    """npx を PATH or 既知のnvm/homebrew位置から解決(launchdの最小PATHでもnpxを見つける・恒久対策)。"""
    p = _shutil.which("npx")
    if p:
        return p
    import glob
    for pat in (str(Path.home() / ".nvm/versions/node/*/bin/npx"),
                "/opt/homebrew/bin/npx", "/usr/local/bin/npx"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return "npx"  # 最後の砦(見つからなければ従来通り→明示的にエラー)


def _cloudflare_token():
    """CLOUDFLARE_API_TOKEN を env→loginキーチェーンの順で解決。値はログに出さない。
    launchd等の非対話環境は ~/.zshrc を読まず env が空 → OAuthフォールバックも無く 400 で毎時死ぬ
    (2026-08の12日沈黙・PATH→npx と同型の『launchd実行環境≠ログインシェル』障害)。
    キーチェーン(security)を非対話参照することで、plistに値を焼かず(=public repo露出なし)に解決する。"""
    # 2026-11-18: 解決ロジックは cf_env.token() に一本化(同型の取りこぼし防止)。挙動は同一(env→keychain)。
    import sys as _s
    _d = str(Path(__file__).resolve().parent)
    if _d not in _s.path:
        _s.path.append(_d)
    import cf_env
    return cf_env.token()


def wrangler(sql_args, timeout=120):
    import os
    npx = _npx()
    # npxが内部で呼ぶnodeも同じbinディレクトリにある → 子プロセスPATHに注入(launchd最小PATHでも動く恒久対策)
    env = dict(os.environ)
    env["PATH"] = str(Path(npx).parent) + os.pathsep + env.get("PATH", "")
    tok = _cloudflare_token()                     # env→keychain。値はログに出さない。
    if tok:
        env["CLOUDFLARE_API_TOKEN"] = tok         # 非対話(launchd)でも認証を通す恒久対策
    cmd = [npx, "wrangler", "d1", "execute", DB, "--remote", "--config", WRANGLER_CONFIG] + sql_args
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout, env=env)


def _parse_d1_results(proc):
    """成功判定は exit code/stderr でなく **stdout の JSON結果** で行う。
    macOS互換警告等の stderr ノイズ(returncode=0でも出る)を成功/失敗判定に混ぜない。
    返り値: results(list) or None(=有効なJSON結果が無い=真の失敗)。"""
    txt = proc.stdout or ""
    s = txt.find("[")
    if s == -1:
        return None
    try:
        data = json.loads(txt[s:])
    except Exception:
        return None
    if isinstance(data, list) and data and isinstance(data[0], dict) and "results" in data[0]:
        return data[0]["results"]
    return None


def d1_query(sql, retries=2):
    """stdoutのJSON結果で成功判定(stderr警告は無視)。一過性失敗は最大 retries 回リトライ。"""
    import time as _t
    last = None
    for attempt in range(retries + 1):
        proc = wrangler(["--command", sql, "--json"])
        res = _parse_d1_results(proc)
        if res is not None:
            return res
        last = proc
        if attempt < retries:
            _t.sleep(1.5)
    # 有効なJSON結果が最後まで得られなかった=真の失敗。原因は stdout優先で出す(stderrはmacOS警告で埋もれる)。
    raise RuntimeError(f"d1 query失敗(rc={last.returncode}): "
                       f"stdout={(last.stdout or '')[-200:].strip()!r} / stderr={(last.stderr or '')[-200:].strip()!r}")


def canary_hash():
    rows = d1_query(f"SELECT panel_num,dialogue,main_copy,sub_copy,image_url FROM company_panels WHERE company_id='{CANARY}' ORDER BY panel_num")
    blob = json.dumps(rows, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def canary_snapshot(exclude_slugs):
    """一般化canary: 今サイクルの対象社を除く『全社』の台本ハッシュ {slug: hash}。

    三井固有参照を撤去。対象外の全社をhash照合する番人。
    """
    ex = ",".join("'" + str(s).replace("'", "''") + "'" for s in exclude_slugs) or "''"
    rows = d1_query(
        "SELECT company_id,panel_num,dialogue,main_copy,sub_copy,image_url "
        f"FROM company_panels WHERE company_id NOT IN ({ex}) ORDER BY company_id,panel_num")
    by = {}
    for r in rows:
        by.setdefault(r["company_id"], []).append(r)
    return {slug: hashlib.sha256(json.dumps(rs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
            for slug, rs in by.items()}


def canary_diff(before: dict, after: dict):
    """変化した『対象外』社のリストを返す。空=安全(他社を壊していない)。"""
    changed = []
    for slug in set(before) | set(after):
        if before.get(slug) != after.get(slug):
            changed.append(slug)
    return sorted(changed)


def sqlq(v):
    if v is None:
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def apply_salary(slug):
    """年収コマを修正(非dry)。toyota-tsushoはkoma10の生Markdownも除去。
    戻り: {'slug','changed_komas':[(koma,after)],'lint':(e,w)} or None。"""
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8") + "\n\n" + S.SALARY_RULE
    koma = S.find_salary_koma(slug)
    sal = S.factsheet_salary(slug)
    changed = []
    if koma:
        instr = (f"{S.SALARY_RULE}\n\n【有報/factsheet年収】{sal}\n上記ルールで年収コマ修正。"
                 "金額は有報(単体)平均年収＋出典。他社比較の生数字回避。正しく低いだけなら盛らず構造で。変更不要なら『変更なし』。")
        res = L.fix_script_koma(slug, koma, instr, rules, dry=False)
        if res.get("changed"):
            changed.append((koma, res["after"]))
    # toyota-tsusho: koma10の生Markdown ** を除去(内容保持・Claude不使用)
    if slug == "toyota-tsusho":
        res2 = strip_markdown_koma(slug, 10)
        if res2:
            changed.append((10, res2))
    e, w, _ = L.lint_with_overrides(slug, dict(changed))   # 修正案を当てた台本で全部入り lint
    return {"slug": slug, "changed": changed, "lint": (e, w)}


def strip_markdown_koma(slug, koma_num):
    """指定コマの script/main_copy/sub_copy から ** を除去した案を返す(内容は保持・書込なし)。
    元データ = scenario_v4.json(⑤)。反映は呼び出し側が scenario_writer.apply で行う。"""
    import scenario_writer as SW
    cur = SW.current(slug).get(koma_num)
    if not cur:
        return None
    def clean(s):
        return (s or "").replace("**", "").replace("__", "")
    after = {"script": [clean(x) for x in cur["script"]], "main_copy": clean(cur["main_copy"]) or None,
             "sub_copy": clean(cur["sub_copy"]) or None}
    if after == cur:
        return None
    return after


def update_sql(slug, koma, after):
    """【廃止 2026-11-19 ⑤】D1 の台本列を直接 UPDATE する SQL は作らない(216社ズレの真因)。
    台本の書き込みは scenario_writer.apply(slug, {koma: after}, reason) を使う(ファイル先行→lint→関所UPDATE)。"""
    raise RuntimeError("deploy_salary.update_sql は廃止: scenario_writer.apply を使う(ファイル先行・関所経由)")


def backup_d1(slug):
    BACKUP.mkdir(exist_ok=True)
    rows = d1_query(f"SELECT * FROM company_panels WHERE company_id='{slug}' ORDER BY panel_num")
    ts = time.strftime("%Y%m%d_%H%M%S")
    p = BACKUP / f"d1_{slug}_{ts}.json"
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true", help="D1へ反映(既定はapplyのみ)")
    args = ap.parse_args()

    print("=== 年収共通ルール 本番反映 (三井除外) ===")
    print("[1] 台本SQL修正 + lint")
    applied = []
    for slug in S.SHOSHA:  # 三井は含まれない
        r = apply_salary(slug)
        e, w = r["lint"]
        komas = [k for k, _ in r["changed"]]
        ok = (e == 0) and bool(r["changed"])
        print(f"  {slug:16} 変更koma={komas} lint:err={e},warn={w} {'✅deploy可' if ok else ('— 変更なし' if not r['changed'] else '❌lint error')}")
        if ok:
            applied.append(r)
    print(f"\n→ deploy可: {len(applied)}社")

    if not args.deploy:
        print("\n(--deploy 未指定: D1へは反映していません)")
        return 0

    print("\n[2-3] scenario_writer.apply(ファイル先行→lint→commit→関所の列UPDATE→changes照合→canary)")
    import scenario_writer as SW
    c_before = canary_hash()
    for r in list(applied):
        try:
            wr = SW.apply(r["slug"], {k: a for k, a in r["changed"]}, reason="年収共通ルール反映")
            print(f"  {r['slug']:16} ✅ commit={wr['commit']} UPDATE koma={sorted(wr['updates'])}")
        except SW.WriterError as ex:
            print(f"  {r['slug']:16} ❌ scenario_writer 中止(D1未書込): {str(ex)[:160]}")
            applied.remove(r)

    print("\n[4] canary(after) 確認")
    c_after = canary_hash()
    print(f"  canary({CANARY}) after = {c_after} {'✅不変' if c_after==c_before else '⚠️変化!(要確認)'}")

    print("\n[5] 本番API検証")
    import requests
    for r in applied:
        try:
            jr = requests.get(f"{API_BASE}/api/companies/{r['slug']}", timeout=30).json()
            panels = jr.get("panels", [])
            kp = {k for k, _ in r["changed"]}
            print(f"  {r['slug']:16} API200 name={jr.get('name')} panels={len(panels)} 変更koma={sorted(kp)}")
        except Exception as ex:
            print(f"  {r['slug']:16} API検証失敗: {ex}")
    print("\n完了。巻き戻しは .backups/d1_*.json から復元可。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
