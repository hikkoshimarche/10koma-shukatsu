#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_shizukani.py — 全商社のナナ『(静かに)』ト書きを除去し本番反映(決定的・三井除外)。

scan→該当komaのscript_jsonを除去版に書換(backup)→lint→台本列UPDATE(image_url不変)
→canary確認→API検証。Claude不使用。
"""
import json
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import deploy_salary as D        # noqa: E402
import find_shizukani as F       # noqa: E402


def apply_one(slug):
    """該当komaのscriptを除去版に書換(backup)。戻り: 変更したkoma番号list。"""
    hits = F.scan(slug)
    if not any(h["removed"] for h in hits):
        return []
    parsed = L.parse_migration_sql(slug)
    by_koma = {}
    for h in hits:
        if h["removed"]:
            by_koma.setdefault(h["koma"], []).append(h)
    changed = []
    L.backup_file(parsed["path"], f"{slug}_shizukani")
    raw = parsed["raw"]
    for koma, hs in by_koma.items():
        panel = next(x for x in parsed["panels"] if x["panel_num"] == koma)
        script = json.loads(panel["script_json"] or "[]")
        new_script = [F.clean_line(x) if "静かに" in x else x for x in script]
        after = {"script": new_script, "main_copy": panel["main_copy"], "sub_copy": panel["sub_copy"]}
        raw = L._replace_panel_fields(raw, slug, koma, after, "\n".join(new_script))
        changed.append(koma)
        L.append_diff_log({"slug": slug, "koma": koma, "kind": "shizukani_remove",
                           "before": script, "after": new_script})
    parsed["path"].write_text(raw, encoding="utf-8")
    return changed


def main():
    print("=== 全商社『静かに』除去 本番反映 (三井除外・決定的) ===\n")
    recs = []
    for slug in F.SHOSHA:
        changed = apply_one(slug)
        if not changed:
            continue
        e, w, _ = L.lint_company(slug)
        recs.append({"slug": slug, "changed": changed, "lint": (e, w)})
        print(f"  {slug:16} 除去koma={changed} lint:err={e},warn={w} {'✅' if e==0 else '❌'}")

    deployable = [r for r in recs if r["lint"][0] == 0]
    print(f"\n→ deploy対象: {len(deployable)}社")
    if not deployable:
        return 0

    c_before = D.canary_hash()
    print(f"\n[canary before] {D.CANARY} = {c_before}")
    print("\n[backup + UPDATE 台本列(image_url不変)]")
    for r in deployable:
        D.backup_d1(r["slug"])
        for koma in r["changed"]:
            parsed = L.parse_migration_sql(r["slug"])
            panel = next(x for x in parsed["panels"] if x["panel_num"] == koma)
            after = {"script": json.loads(panel["script_json"] or "[]"),
                     "main_copy": panel["main_copy"], "sub_copy": panel["sub_copy"]}
            proc = D.wrangler(["--command", D.update_sql(r["slug"], koma, after)])
            print(f"  {r['slug']:16} koma{koma} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:100]}")
    c_after = D.canary_hash()
    print(f"\n[canary after] {D.CANARY} = {c_after} {'✅不変' if c_after==c_before else '⚠️変化!'}")

    print("\n[API検証]")
    for r in deployable:
        jr = requests.get(f"{D.API_BASE}/api/companies/{r['slug']}", timeout=30).json()
        # 除去確認: 変更komaのdialogueに『静かに』が残っていないか
        ok = True
        for p in jr.get("panels", []):
            if p.get("panel_num") in r["changed"] and "静かに" in (p.get("dialogue") or ""):
                ok = False
        print(f"  {r['slug']:16} API200 除去komaに静かに残存={'なし✅' if ok else 'あり⚠️'}")
    print("\n完了。巻き戻しは .backups/d1_*.json から。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
