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
import scenario_writer as SW     # noqa: E402  台本の唯一の書き込み口
import find_shizukani as F       # noqa: E402


def apply_one(slug):
    """該当komaの『静かに』除去案を返す(書込なし)。元データ = scenario_v4.json(⑤)。
    戻り: {koma: after}。反映は main が scenario_writer.apply で行う。"""
    hits = F.scan(slug)
    if not any(h["removed"] for h in hits):
        return {}
    cur = SW.current(slug)
    out = {}
    for koma in sorted({h["koma"] for h in hits if h["removed"]}):
        c = cur[koma]
        new_script = [F.clean_line(x) if "静かに" in x else x for x in c["script"]]
        if new_script != c["script"]:
            out[koma] = {"script": new_script, "main_copy": c["main_copy"], "sub_copy": c["sub_copy"]}
    return out


def main():
    print("=== 全商社『静かに』除去 本番反映 (三井除外・決定的) ===\n")
    recs = []
    for slug in F.SHOSHA:
        edits = apply_one(slug)
        if not edits:
            continue
        e, w, _ = L.lint_with_overrides(slug, edits)
        recs.append({"slug": slug, "changed": sorted(edits), "edits": edits, "lint": (e, w)})
        print(f"  {slug:16} 除去koma={sorted(edits)} lint:err={e},warn={w} {'✅' if e==0 else '❌'}")

    deployable = [r for r in recs if r["lint"][0] == 0]
    print(f"\n→ deploy対象: {len(deployable)}社")
    if not deployable:
        return 0

    print("\n[scenario_writer.apply: ファイル先行→lint→commit→関所の列UPDATE→changes照合→canary]")
    for r in list(deployable):
        try:
            wr = SW.apply(r["slug"], r["edits"], reason="『静かに』除去")
            print(f"  {r['slug']:16} ✅ commit={wr['commit']} UPDATE koma={sorted(wr['updates'])}")
        except SW.WriterError as ex:
            print(f"  {r['slug']:16} ❌ scenario_writer 中止(D1未書込): {str(ex)[:160]}")
            deployable.remove(r)

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
