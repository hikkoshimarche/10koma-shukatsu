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


def wrangler(sql_args, timeout=120):
    cmd = ["npx", "wrangler", "d1", "execute", DB, "--remote", "--config", WRANGLER_CONFIG] + sql_args
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout)


def d1_query(sql):
    proc = wrangler(["--command", sql, "--json"])
    if proc.returncode != 0:
        raise RuntimeError(f"d1 query失敗: {proc.stderr[:300]}")
    txt = proc.stdout
    s = txt.find("[")
    return json.loads(txt[s:])[0]["results"]


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
    e, w, _ = L.lint_company(slug)
    return {"slug": slug, "changed": changed, "lint": (e, w)}


def strip_markdown_koma(slug, koma_num):
    """指定コマの script_json/main_copy/sub_copy から ** を除去(内容は保持)。backup付き。"""
    parsed = L.parse_migration_sql(slug)
    target = next((r for r in parsed["panels"] if r["panel_num"] == koma_num), None)
    if not target:
        return None
    try:
        script = json.loads(target.get("script_json") or "[]")
    except Exception:
        return None
    def clean(s):
        return (s or "").replace("**", "").replace("__", "")
    new_script = [clean(x) for x in script]
    after = {"script": new_script, "main_copy": clean(target.get("main_copy")),
             "sub_copy": clean(target.get("sub_copy"))}
    before = {"script": script, "main_copy": target.get("main_copy"), "sub_copy": target.get("sub_copy")}
    if after == before:
        return None
    L.backup_file(parsed["path"], f"{slug}_koma{koma_num}_mdstrip")
    new_raw = L._replace_panel_fields(parsed["raw"], slug, koma_num, after, "\n".join(new_script))
    parsed["path"].write_text(new_raw, encoding="utf-8")
    L.append_diff_log({"slug": slug, "koma": koma_num, "kind": "md_strip", "before": before, "after": after})
    return after


def update_sql(slug, koma, after):
    """台本列のみUPDATE(image_url不変)。"""
    dialogue = "\n".join(after["script"])
    return (f"UPDATE company_panels SET "
            f"dialogue={sqlq(dialogue)}, "
            f"script_json={sqlq(json.dumps(after['script'], ensure_ascii=False))}, "
            f"main_copy={sqlq(after.get('main_copy'))}, "
            f"sub_copy={sqlq(after.get('sub_copy'))} "
            f"WHERE company_id='{slug}' AND panel_num={koma};")


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

    print("\n[2] D1バックアップ + canary(before)")
    for r in applied:
        p = backup_d1(r["slug"])
        print(f"  backup: {p.name}")
    c_before = canary_hash()
    print(f"  canary({CANARY}) before = {c_before}")

    print("\n[3] 台本列UPDATE(image_url不変)を本番D1へ")
    for r in applied:
        stmts = [update_sql(r["slug"], k, a) for k, a in r["changed"]]
        sql = " ".join(stmts)
        proc = wrangler(["--command", sql])
        ok = proc.returncode == 0
        print(f"  {r['slug']:16} UPDATE {len(stmts)}件 {'✅' if ok else '❌ '+proc.stderr[:120]}")

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
