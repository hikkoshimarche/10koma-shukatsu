#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""find_shizukani.py — 全商社からナナの『(静かに)』ト書きを検出し削除後の文を提示(dry-run)。

決定的処理(Claude不使用)。検出のみで書込まない。--apply で実反映用の差分を作る。
三井(mitsui-bussan)は対象外。
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L  # noqa: E402

SHOSHA = ["mitsubishi-corp", "itochu", "sumitomo-corp", "marubeni", "kanematsu",
          "shinkokusyoji", "iwatani", "sojitz", "toyota-tsusho"]  # 三井除外

# (静かに) / （静かに…） などのト書きを除去。全角/半角括弧・読点込みに対応。
PAT = re.compile(r"[（(]\s*静かに[^）)]*[）)]\s*")


def clean_line(line: str) -> str:
    s = PAT.sub("", line)
    # 「[nana] 　」のような二重空白を整える
    s = re.sub(r"(\[[^\]]+\])\s+", r"\1 ", s)
    return s.strip()


def scan(slug):
    p = L.parse_migration_sql(slug)
    hits = []
    for r in p["panels"]:
        try:
            script = json.loads(r.get("script_json") or "[]")
        except Exception:
            continue
        for i, line in enumerate(script):
            if "静かに" in line:
                cleaned = clean_line(line)
                hits.append({"koma": r["panel_num"], "idx": i, "before": line, "after": cleaned,
                             "removed": line != cleaned})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    print("=== 全商社『静かに』検出 (三井除外・dry-run) ===\n")
    total = 0
    for slug in SHOSHA:
        hits = scan(slug)
        if not hits:
            continue
        print(f"#### {slug}")
        for h in hits:
            total += 1
            mark = "✂除去" if h["removed"] else "⚠静かに含むが括弧ト書きでない(要確認)"
            print(f"  koma{h['koma']} [{mark}]")
            print(f"    現行: {h['before']}")
            print(f"    削除後: {h['after']}")
        print()
    print(f"検出合計: {total}件")
    if not args.apply:
        print("(--apply 未指定: 検出のみ。本番反映はしていません)")


if __name__ == "__main__":
    main()
