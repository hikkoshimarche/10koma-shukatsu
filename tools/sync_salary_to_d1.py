#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_salary_to_d1.py — 修正済み台本SQL(年収コマ+toyota koma10)を本番D1へ冪等同期。

Claudeは呼ばない。SQLが正。各商社の年収コマ(+toyota koma10)について、
D1の現値とSQLの値が異なる場合のみ台本列(dialogue/script_json/main_copy/sub_copy)をUPDATE。
image_urlは触らない。backup+canary付き。三井除外。
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import salary_rule_dryrun as S   # noqa: E402
import deploy_salary as D        # noqa: E402


def koma_from_sql(slug, koma):
    p = L.parse_migration_sql(slug)
    r = next((x for x in p["panels"] if x["panel_num"] == koma), None)
    if not r:
        return None
    try:
        script = json.loads(r.get("script_json") or "[]")
    except Exception:
        script = []
    return {"script": script, "main_copy": r.get("main_copy"), "sub_copy": r.get("sub_copy"),
            "dialogue": r.get("dialogue")}


def koma_from_d1(slug, koma):
    rows = D.d1_query(f"SELECT panel_num,dialogue,main_copy,sub_copy,script_json FROM company_panels WHERE company_id='{slug}' AND panel_num={koma}")
    if not rows:
        return None
    r = rows[0]
    try:
        script = json.loads(r.get("script_json") or "[]")
    except Exception:
        script = []
    return {"script": script, "main_copy": r.get("main_copy"), "sub_copy": r.get("sub_copy"),
            "dialogue": r.get("dialogue")}


def main():
    print("=== 修正済みSQL→D1 冪等同期 (年収コマ+toyota koma10・三井除外) ===")
    targets = []  # (slug, koma)
    for slug in S.SHOSHA:
        k = S.find_salary_koma(slug)
        if k:
            targets.append((slug, k))
        if slug == "toyota-tsusho":
            targets.append((slug, 10))

    c_before = D.canary_hash()
    print(f"canary({D.CANARY}) before = {c_before}\n")

    to_update = []
    for slug, koma in targets:
        sql = koma_from_sql(slug, koma)
        d1 = koma_from_d1(slug, koma)
        if not sql or not d1:
            print(f"  {slug} koma{koma}: 取得不可"); continue
        same = (sql["script"] == d1["script"] and sql["main_copy"] == d1["main_copy"]
                and sql["sub_copy"] == d1["sub_copy"])
        print(f"  {slug:16} koma{koma}: {'一致(skip)' if same else '差分→UPDATE予定'}")
        if not same:
            to_update.append((slug, koma, sql))

    if not to_update:
        print("\n全て一致。D1反映済み。")
        return 0

    # backup(対象社) + UPDATE
    print(f"\n[backup] {len({s for s,_,_ in to_update})}社")
    for slug in {s for s, _, _ in to_update}:
        p = D.backup_d1(slug)
        print(f"  {p.name}")

    print("\n[UPDATE] 台本列のみ(image_url不変)")
    for slug, koma, sql in to_update:
        after = {"script": sql["script"], "main_copy": sql["main_copy"], "sub_copy": sql["sub_copy"]}
        stmt = D.update_sql(slug, koma, after)
        proc = D.wrangler(["--command", stmt])
        print(f"  {slug:16} koma{koma} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:120]}")

    c_after = D.canary_hash()
    print(f"\ncanary({D.CANARY}) after = {c_after} {'✅不変' if c_after==c_before else '⚠️変化!'}")
    print("完了。巻き戻しは .backups/d1_*.json から。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
