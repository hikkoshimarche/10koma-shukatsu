#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reconcile_register.py — 本番D1↔進捗スプシ「10コマ」を突合し、未登録社を自動起票(冪等)。

waveがD1へ投入するたび、毎時このスクリプトが:
  1. D1全社(slug/industry/script_json=v4) を取得
  2. スプシ10コマの行(name→row, 公開URL有無)を取得
  3. 公開URL空のD1社を正規化name照合で行特定(孤児3除外)
  4. GAS bulkregister(行指定)で 公開URL記入 + gemini=状態1空(CFオレンジ) / old=Note『要Gemini再生成』
冪等: 公開URL既設の行はskip。read-onlyのD1 SELECTのみ(D1書込/デプロイはしない)。
env: SHEET_WEBAPP_URL, SHEET_API_TOKEN (tools/.env.phase_c)。
"""
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import deploy_salary as D  # noqa: E402 (d1_query)

ENV = REPO / "tools" / ".env.phase_c"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

URL = os.environ["SHEET_WEBAPP_URL"].strip()
TOKEN = os.environ["SHEET_API_TOKEN"].strip()
COMPANIES_JSON = REPO / "public" / "companies.json"
ORPHANS = {"mitsubishi_corp", "toyota_motor", "ana"}  # 削除予定の孤児(除外)
LOG = REPO / ".backups" / "sheet_sync.log"


def norm(s):
    s = unicodedata.normalize("NFKC", str(s))
    s = re.sub(r"[（(].*?[)）]", "", s)              # 括弧内除去
    s = s.replace("株式会社", "").replace("証券", "證券")  # 證/証統一
    s = re.sub(r"\s|・|ホールディングス|HD|グループ", "", s)
    return s.strip().lower()


def gas(params):
    return requests.get(URL, params={**params, "token": TOKEN}, timeout=90).json()


def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] {msg}\n")
    print(msg, flush=True)


def main():
    # 1. D1全社 + v4
    d1 = D.d1_query(
        "SELECT c.id, c.industry_id, MAX(CASE WHEN p.script_json IS NOT NULL AND length(p.script_json)>2 "
        "THEN 1 ELSE 0 END) v4 FROM companies c JOIN company_panels p ON p.company_id=c.id GROUP BY c.id")
    # id→name
    cj = json.loads(COMPANIES_JSON.read_text(encoding="utf-8"))
    id2name = {x["id"]: x["name"] for lst in cj.values() for x in lst}
    # 2. スプシ
    sd = gas({"mode": "readsheet", "sheet": "10コマ"})["values"]
    srow, existing_url = {}, {}
    for i, r in enumerate(sd):
        if i < 2 or len(r) < 2 or not str(r[1]).strip():
            continue
        key = norm(r[1])
        srow.setdefault(key, i + 1)
        existing_url[key] = str(r[3]).strip() if len(r) > 3 else ""
    # 3. 未登録(公開URL空)を照合
    payload, nomatch = [], []
    for r in d1:
        slug = r["id"]
        if slug in ORPHANS:
            continue
        key = norm(id2name.get(slug, slug))
        row = srow.get(key)
        if not row:
            nomatch.append(slug); continue
        if existing_url.get(key, "").startswith("http"):
            continue  # 冪等: 既設skip
        payload.append({"row": row, "slug": slug, "kind": "gemini" if r["v4"] == 1 else "old"})
    if not payload:
        log(f"未登録なし(D1 {len(d1)}社・全て掲載済 / nomatch {len(nomatch)})"); return 0
    # 4. bulkregister(25件/バッチ)
    items = [f"{x['row']}|{x['slug']}|{x['kind']}" for x in payload]
    tot = {"matched": 0, "oranged": 0, "noted": 0}
    for i in range(0, len(items), 25):
        r = gas({"mode": "bulkregister", "rows": ";;".join(items[i:i + 25])})
        for k in ("matched", "oranged", "noted"):
            tot[k] += r.get(k, 0)
        time.sleep(1)
    log(f"起票 {tot['matched']}社 (gemini/orange {tot['oranged']} / old/note {tot['noted']}) "
        f"D1総数{len(d1)} nomatch{len(nomatch)}{('='+str(nomatch)) if nomatch else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
