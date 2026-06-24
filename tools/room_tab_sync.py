#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_tab_sync.py — スプシ「AI OB訪問（ルーム）」をL4新モデルに再構成(D1=正)。

完成のハード定義: 6/6人格が D1 room_personas に登録済(=room_harnessがlint5通過時のみ登録)。
1社6行(R1-R6)。人FBループ列は持たない。冪等(毎回D1から全社書き直し)。
使い方: room_tab_sync.py
"""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import room_lib as RL  # noqa: E402
try:
    from dotenv import load_dotenv as _ld; _ld(ROOT / ".env")
except Exception:
    pass

REPO10 = Path("/Users/oscardodds/projects/10koma-shukatsu")
WCONF = REPO10 / "api" / "wrangler.toml"
GAS_URL = os.environ.get("SHEET_WEBAPP_URL", "").strip() or \
    "https://script.google.com/macros/s/AKfycbyhe5TuRbl0I8zV6-BUCmDGGL3MITkoqJSJZy_JzpkgPJWtSQNuPK9E7PDsPleCaQdYbw/exec"
GAS_TOKEN = os.environ.get("SHEET_API_TOKEN", "").strip() or "tokyari-7h2k9q4w8z"
ROLE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6"]


def gas(params, post=False):
    p = {**params, "token": GAS_TOKEN}
    # 大きいrowsペイロードはPOST(GET URL長制限を回避)。GASはPOST formもe.parameterに入る。
    r = requests.post(GAS_URL, data=p, timeout=120) if post else requests.get(GAS_URL, params=p, timeout=90)
    try:
        return r.json()
    except Exception:
        return {"text": r.text.strip()[:80]}


def d1_personas():
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", str(WCONF), "--command",
                        "SELECT company_slug,role,persona_name,created_at FROM room_personas",
                        "--json"], cwd=str(REPO10), capture_output=True, text=True, timeout=90)
    s = p.stdout.find("[")
    rows = json.loads(p.stdout[s:])[0]["results"]
    by = {}
    for r in rows:
        by.setdefault(r["company_slug"], {})[r["role"]] = r
    return by


def main():
    cj = json.loads((REPO10 / "public" / "companies.json").read_text(encoding="utf-8"))
    companies = [(x["id"], x["name"]) for lst in cj.values() for x in lst]
    # Notion page_id
    pid = {}
    nss = ROOT / "output" / "notion_sync_state.csv"
    if nss.exists():
        for r in csv.reader(open(nss, encoding="utf-8")):
            if len(r) >= 2 and r[1]:
                pid[r[0]] = r[1]
    d1 = d1_personas()

    # スポット確認: 完成社の一部(R3/R6)に初回フラグ(全社でない)
    import hashlib
    rows = []
    done_companies = 0
    for slug, name in companies:
        prs = d1.get(slug, {})
        complete = len([r for r in ROLE_ORDER if r in prs]) == 6
        if complete:
            done_companies += 1
        for role in ROLE_ORDER:
            rdef = RL.ROLES[role]
            p = prs.get(role)
            if p:
                jin = p.get("persona_name", "")
                gutai = f"{rdef['label']} / 語り口:{rdef['tone'][:20]}"
                retire = "A/B/C(R6のみ)" if role == "R6" else ""
                kensho = "✓"
                status = "完成" if complete else "未生成"
                gen = (p.get("created_at") or "")[:10]
                # スポット: 完成社のR3/R6を ~10% フラグ(決定的: slugハッシュ)
                spot = ""
                if complete and role in ("R3", "R6"):
                    h = int(hashlib.md5(slug.encode()).hexdigest(), 16) % 10
                    if h == 0:
                        spot = "要スポット確認"
            else:
                jin = ""; gutai = rdef["label"]; retire = ""; kensho = ""; status = "未生成"; gen = ""; spot = ""
            d1link = f"room_personas:{slug}/{role}" if p else ""
            notion = f"https://www.notion.so/{pid[slug].replace('-','')}" if slug in pid else ""
            rows.append([name, slug, role, jin, gutai, retire, kensho, status, gen, d1link, notion, spot])

    print(f"=== AI OB訪問タブ再構成: {len(companies)}社×6 = {len(rows)}行 / 完成(6/6 lint通過D1) {done_companies}社 ===")
    print("[1] ヘッダ+CF刷新")
    print("  ", gas({"mode": "roomtabheader"}))
    print("[2] 旧データclear")
    print("  ", gas({"mode": "roomtabclear"}))
    # GET+10行/バッチ: 日本語はURLエンコードで~9byte/字に肥大するため、worst-case完成行でもURL長に収める。
    print("[3] 6行/社 書込(GET・10行/バッチ)")
    start = 3
    fail = 0
    for i in range(0, len(rows), 10):
        chunk = rows[i:i + 10]
        payload = ";;".join("\t".join(str(c) for c in r) for r in chunk)
        res = gas({"mode": "roomtabwrite", "rows": payload, "start": str(start)})
        if "next" not in res:
            fail += 1
            print(f"  ⚠ batch start={start} 失敗: {str(res)[:80]}")
        start = res.get("next", start + len(chunk))
    if fail:
        print(f"  ❌ 失敗バッチ {fail}件 → 要調査")
    else:
        print("  全バッチ成功(失敗0)")
    print(f"  書込完了 {len(rows)}行")
    print(f"\n✅ 完成 {done_companies}/400社 (6/6人格 lint5通過D1登録)。残りは未生成(fanout進行で増加)。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
