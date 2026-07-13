#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bulk_ticket_stranded_candidates.py — FIX3後段: 座礁中の混在型候補(review(image…)push済だが
画像人QA sheetに未起票)を一括で addimageqa 起票する。GAS新mode展開(clasp deploy)後に実行。
冪等(addimageqaが slug+koマで上書きdedup)。--dry で送信せず一覧のみ。"""
import os, re, sys, subprocess, json
from pathlib import Path
import requests

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
sys.path.insert(0, str(REPO / "tools"))
for line in (REPO / "tools" / ".env.phase_c").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
GAS = os.environ["SHEET_WEBAPP_URL"].strip(); TOK = os.environ["SHEET_API_TOKEN"].strip()

def gas(p):
    try:
        return requests.get(GAS, params={**p, "token": TOK}, timeout=40).json()
    except Exception as e:
        return {"error": str(e)}

def company_name(slug):
    try:
        import _d1
        rows = _d1.d1(f"SELECT name FROM companies WHERE id='{slug}'")
        return rows[0]["name"] if rows else slug
    except Exception:
        return slug

def collect():
    """git log から review(image:SLUG): komaNN 候補 を抽出→ slug#koマ ごと最新sha。"""
    out = subprocess.run(["git", "log", "--pretty=%h %s", "--all", "--since=2026-07-11"],
                         cwd=str(REPO), capture_output=True, text=True).stdout
    seen = {}
    for line in out.splitlines():
        m = re.match(r"([0-9a-f]+)\s+review\(image:([a-z0-9-]+)\):\s*koma0*(\d+)", line)
        if not m:
            continue
        sha, slug, koma = m.group(1), m.group(2), int(m.group(3))
        key = (slug, koma)
        if key not in seen:            # git log は新しい順 → 最初=最新sha
            seen[key] = sha
    return seen

def main():
    dry = "--dry" in sys.argv
    # 展開確認: addimageqa/imageqa_list が生きているか(JSON応答か)
    probe = gas({"mode": "imageqa_list"})
    live = isinstance(probe, dict) and "items" in probe
    print(f"GAS人QA mode 展開: {'✅LIVE' if live else '❌未展開(clasp deploy要)'}  probe={str(probe)[:80]}")
    seen = collect()
    print(f"座礁候補(distinct slug#koマ): {len(seen)}")
    if not live and not dry:
        print("→ GAS未展開のため起票中止。clasp deploy 後に再実行。"); return 1
    posted = 0
    for (slug, koma), sha in sorted(seen.items()):
        url = f"https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@{sha}/public/images/{slug}/panel_{koma:02d}.png"
        name = company_name(slug)
        print(f"  {name}({slug}) koマ{koma} @{sha}")
        if not dry:
            r = gas({"mode": "addimageqa", "company": name, "slug": slug, "koma": str(koma),
                     "sha": sha, "url": url, "detail": "混在型候補(自動生成・人QA待ち)"})
            if r.get("ok"):
                posted += 1
    print(f"\n起票: {posted}/{len(seen)} 件 ({'DRY' if dry else 'LIVE'})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
