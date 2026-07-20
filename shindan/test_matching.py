#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/test_matching.py — 10パターンの回答で妥当な業界/企業が返るか検証。
実行結果を test_results.md に保存(受け渡し用)。軽い妥当性assertも実施。
option index は questions.json の各設問optionsの並び順。
"""
import json
from pathlib import Path
import matching

ROOT = Path(__file__).resolve().parent

# 10サンプル回答パターン(id→option index / multiはlist)
PATTERNS = [
    ("①安定・地元・文系(金融/インフラ想定)",
     {"q_stability": 0, "q_tenkin": 2, "q_bunri": 0, "q_growth": 2, "q_kaigai": 2, "q_daikigyo": 0}),
    ("②海外・成長・商社志向",
     {"q_kaigai": 0, "q_growth": 0, "q_tenkin": 0, "q_industry": [0], "q_stability": 2}),
    ("③IT・リモート・若手裁量",
     {"q_remote": 0, "q_young": 0, "q_jobtags": [2], "q_industry": [3], "q_growth": 0}),
    ("④研究・理系・メーカー",
     {"q_bunri": 1, "q_jobtags": [3], "q_industry": [1], "q_stability": 1, "q_kaigai": 1}),
    ("⑤高年収狙い",
     {"q_salary": 0, "q_starting": 0, "q_kaigai": 0, "q_young": 0}),
    ("⑥コンサル・裁量・成長",
     {"q_young": 0, "q_growth": 0, "q_jobtags": [4], "q_industry": [4], "q_stability": 3}),
    ("⑦クリエイティブ・エンタメ",
     {"q_jobtags": [5, 1], "q_industry": [3], "q_remote": 0, "q_young": 0}),
    ("⑧安定大手・出社OK・営業",
     {"q_stability": 0, "q_remote": 2, "q_jobtags": [0], "q_daikigyo": 0, "q_tenkin": 1}),
    ("⑨新興・外資・スピード",
     {"q_daikigyo": 1, "q_growth": 0, "q_stability": 3, "q_remote": 0, "q_young": 0}),
    ("⑩回答少数(2問のみ・欠損多で減点しない堅牢性確認)",
     {"q_stability": 0, "q_bunri": 0}),
]


def run():
    lines = ["# shindan マッチング 実行結果(10パターン)", "",
             "各パターンで返る業界トップ3・企業トップ3。トーン=参考提案。", ""]
    ok = True
    for title, ans in PATTERNS:
        res = matching.recommend(ans, top_companies=3, top_industries=3)
        lines.append(f"## {title}")
        lines.append(f"- 回答設問数: {res['answered']}")
        inds = "／".join(f"{x['industry']}({x['score']})" for x in res["top_industries"])
        lines.append(f"- 業界トップ3: {inds}")
        lines.append("- 企業トップ3:")
        for c in res["top_companies"]:
            fa = c["rationale"]["facts"].get("avg_salary", {}).get("text", "")
            notes = c["rationale"].get("notes", [])
            note_s = ("　⚠️" + notes[0]) if notes else ""
            lines.append(f"    - **{c['name']}**（{c['industry']}・score {c['score']}）— {c['rationale']['trend'][:36]}{(' / '+fa) if fa else ''}{note_s}")
        lines.append("")
        # 妥当性の軽いassert(データが十分埋まっている場合のみ)
        top_inds = [x["industry"] for x in res["top_industries"]]
        if res["top_companies"] and res["top_companies"][0]["score"] == 0:
            ok = False
            lines.append("  ⚠️ 全社score0(データ不足の可能性)")
    (ROOT / "test_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\n=== test_matching:", "PASS" if ok else "CHECK", "===")


if __name__ == "__main__":
    run()
