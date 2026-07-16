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
    import room_industry_roles_v3 as RIRV3
    cj = json.loads((REPO10 / "public" / "companies.json").read_text(encoding="utf-8"))
    companies = [(x["id"], x["name"]) for lst in cj.values() for x in lst]
    id2ind = {x["id"]: ind for ind, lst in cj.items() for x in lst}  # slug→18業界(v3ロースターの引き先)
    # Notion page_id
    pid = {}
    nss = ROOT / "output" / "notion_sync_state.csv"
    if nss.exists():
        for r in csv.reader(open(nss, encoding="utf-8")):
            if len(r) >= 2 and r[1]:
                pid[r[0]] = r[1]
    d1 = d1_personas()

    # スポット確認: 完成社の一部(擬似面接=事業部長/OB)に初回フラグ(全社でない)
    import hashlib
    rows = []
    done_companies = 0
    for slug, name in companies:
        prs = d1.get(slug, {})
        roster = RIRV3.roles_for_company(slug, id2ind.get(slug, ""))  # 人数可変・slug対応(「その他」誤バケツ防止)
        exp = len(roster)
        # 完成 = 期待人数ぶんD1に揃っている(÷6固定を廃止・社ごとの実人数集計)
        complete = exp > 0 and len([r for r in roster if r["role_key"] in prs]) == exp
        if complete:
            done_companies += 1
        for rd in roster:
            role = rd["role_key"]
            yakume = rd["label"]           # 役割名=v3(人数可変)
            p = prs.get(role)
            if p:
                jin = p.get("persona_name", "")   # 氏名(個人名)
                gutai = f"語り口:{rd['tone'][:24]}"
                retire = "退職OB" if rd.get("ob") else ("擬似面接" if rd.get("pseudo_interview") else "")
                kensho = "✓"
                status = "完成" if complete else "未生成"
                gen = (p.get("created_at") or "")[:10]
                # スポット: 完成社の擬似面接/OB役を ~10% フラグ(決定的: slugハッシュ)
                spot = ""
                if complete and (rd.get("pseudo_interview") or rd.get("ob")):
                    h = int(hashlib.md5(slug.encode()).hexdigest(), 16) % 10
                    if h == 0:
                        spot = "要スポット確認"
            else:
                jin = ""; gutai = ""; retire = "退職OB" if rd.get("ob") else ""; kensho = ""; status = "未生成"; gen = ""; spot = ""
            d1link = f"room_personas:{slug}/{role}" if p else ""
            notion = f"https://www.notion.so/{pid[slug].replace('-','')}" if slug in pid else ""
            # 13列: 会社名/slug/役割記号/役割名/氏名/人格具体/退職/検証/ステータス/生成日/D1/Notion/spot
            rows.append([name, slug, role, yakume, jin, gutai, retire, kensho, status, gen, d1link, notion, spot])

    avg = (len(rows) / max(len(companies), 1))
    print(f"=== AI OB訪問タブ再構成: {len(companies)}社(人数可変・平均{avg:.1f}人) = {len(rows)}行 / 完成 {done_companies}社 ===")
    print("[1] ヘッダ+CF刷新")
    print("  ", gas({"mode": "roomtabheader"}))
    print("[2] 旧データclear")
    print("  ", gas({"mode": "roomtabclear"}))
    # ★POST+40行/バッチ: GET(5行)だと~550回HTTPで15分超→タイムアウト。POSTはURL長制限が無いので
    # 大バッチ可(~2740行を~70回で書込・数十秒)。roomtabwriteはdoPost経由でも e.parameter.rows を読む。
    print("[3] N行/社 書込(人数可変・POST・40行/バッチ)")
    start = 3
    fail = 0
    for i in range(0, len(rows), 40):
        chunk = rows[i:i + 40]
        payload = ";;".join("\t".join(str(c) for c in r) for r in chunk)
        res = gas({"mode": "roomtabwrite", "rows": payload, "start": str(start)}, post=True)
        if "next" not in res:
            fail += 1
            print(f"  ⚠ batch start={start} 失敗: {str(res)[:80]}")
        start = res.get("next", start + len(chunk))
    if fail:
        print(f"  ❌ 失敗バッチ {fail}件 → 要調査")
    else:
        print("  全バッチ成功(失敗0)")
    print(f"  書込完了 {len(rows)}行")
    print(f"\n✅ 完成 {done_companies}/{len(companies)}社 (期待人数ぶんlint5通過D1登録・人数可変)。残りは未生成(fanout進行で増加)。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
