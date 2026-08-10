#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""companies.json に二層メタ(dai_slug/dai_name/chu_slug/chu_name/tags)を後方互換(加算)で反映。
源泉= public/taxonomy.json(構造/slug) + tools/taxonomy_companies.csv(個社割当)。
既存18キー構造・各社の既存フィールドは不変(追記のみ)。CSV差替→validator→本スクリプト の順で再生成。"""
import json, csv

ROOT = "/Users/oscardodds/projects/10koma-shukatsu"
TAX  = f"{ROOT}/public/taxonomy.json"
CSVF = f"{ROOT}/tools/taxonomy_companies.csv"
CJ   = f"{ROOT}/public/companies.json"

tax = json.load(open(TAX))
chu_idx = {}   # 中分類name -> (chu_slug, dai_slug, dai_name)
for d in tax["daibunrui"]:
    for c in d["chubunrui"]:
        chu_idx[c["name"]] = (c["slug"], d["slug"], d["name"])
tag_label2id = {t["label"]: t["id"] for t in tax["tags"]}

assign = {}   # id -> (chu_name, [tag_id])
with open(CSVF, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        tag_ids = [tag_label2id[t] for t in filter(None, r.get("横断タグ", "").split("/"))]
        assign[r["slug"]] = (r["新・中分類"], tag_ids)

comp = json.load(open(CJ))
n = 0; missing = []
for arr in comp.values():
    for c in arr:
        a = assign.get(c["id"])
        if not a:
            missing.append(c["id"]); continue
        chu_name, tag_ids = a
        chu_slug, dai_slug, dai_name = chu_idx[chu_name]
        c["dai_slug"] = dai_slug; c["dai_name"] = dai_name
        c["chu_slug"] = chu_slug; c["chu_name"] = chu_name
        c["tags"] = tag_ids
        n += 1

if missing:
    print("❌ 未割当:", missing); raise SystemExit(1)

with open(CJ, "w", encoding="utf-8") as f:
    json.dump(comp, f, ensure_ascii=False, indent=2); f.write("\n")

base = {'id', 'name', 'jukoma_liff_id', 'room_liff_id', 'video_url', 'kessan_url'}
chk = json.load(open(CJ)); bad = sum(1 for arr in chk.values() for c in arr if not base.issubset(c))
print(f"✅ {n}社に二層メタ反映。既存フィールド保持: {'OK' if bad==0 else f'欠落{bad}社'}")
