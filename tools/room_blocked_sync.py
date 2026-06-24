#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_blocked_sync.py — 恒久lintブロック社を「ルーム要個別対応」タブへ自動転記(冪等)。

恒久ブロック = room_sync_state.csv で "lint error" かつ D1 room_personas に6/6未登録の社。
transient(factpack抽出失敗/anthropic一時失敗) は retry対象なので**混ぜない**。
fanoutで解消(D1登録)した社は incoming から外れ→GAS側で状態=解消に。
使い方: room_blocked_sync.py
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
REPO10 = Path("/Users/oscardodds/projects/10koma-shukatsu")
WCONF = REPO10 / "api" / "wrangler.toml"
GAS = "https://script.google.com/macros/s/AKfycbyhe5TuRbl0I8zV6-BUCmDGGL3MITkoqJSJZy_JzpkgPJWtSQNuPK9E7PDsPleCaQdYbw/exec"
TOKEN = "tokyari-7h2k9q4w8z"
PLAN = "factpackから倍率・出典なき数値を除去 or 出典付きに置換 → 再fanoutで解消"
# 個別に判明している理由(無ければ汎用)
REASON = {
    "mitsubishi-corp": "倍率混入(プレエントリー14,512名→採用139名の出典なき倍率がfactpackに混入)",
}
GENERIC = "倍率/出典なき数値混入(source_or_silence)"


def d1_done():
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", str(WCONF), "--command",
                        "SELECT company_slug FROM room_personas GROUP BY company_slug HAVING COUNT(*)=6",
                        "--json"], cwd=str(REPO10), capture_output=True, text=True, timeout=90)
    s = p.stdout.find("[")
    return set(x["company_slug"] for x in json.loads(p.stdout[s:])[0]["results"])


def main():
    done = d1_done()
    state = {}
    sc = ROOT / "output" / "room_sync_state.csv"
    for r in csv.reader(open(sc, encoding="utf-8")):
        if len(r) >= 2 and r[0] != "slug":
            state[r[0]] = r[1]  # 最終状態(後勝ち)
    cj = json.loads((REPO10 / "public" / "companies.json").read_text(encoding="utf-8"))
    name = {x["id"]: x["name"] for l in cj.values() for x in l}

    blocked = []
    for slug, st in state.items():
        if "lint error" in st and slug not in done:   # 恒久ブロックのみ(transient除外)
            blocked.append(slug)
    blocked.sort()
    rows = []
    for slug in blocked:
        rows.append("\t".join([name.get(slug, slug), slug, "source_or_silence(lint5)",
                               REASON.get(slug, GENERIC), PLAN]))
    payload = ";;".join(rows)
    print(f"=== 恒久lintブロック {len(blocked)}社 → ルーム要個別対応タブ転記 ===")
    for slug in blocked:
        print(f"  {name.get(slug, slug)} ({slug})")
    res = requests.get(GAS, params={"mode": "roomblockedtab", "rows": payload, "token": TOKEN}, timeout=90)
    try:
        print("  GAS応答:", res.json())
    except Exception:
        print("  GAS応答(非JSON):", res.text[:120])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
