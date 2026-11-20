#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ph1ガード: public/taxonomy.json(構造) と tools/taxonomy_companies.csv(個社割当) の整合検証。
- CSVの全中分類が taxonomy.json に存在
- CSVの大分類が taxonomy.json の対応と一致
- 400社ちょうど・slug重複なし
- 各中分類→有効なgyokai16
- taxonomy側で個社0件の中分類を警告(空バケツ検知)
オスカーがCSVで個社を差し替えた後、このバリデータが通ればPh2ビルド可。"""
import json, csv, sys, collections

TAX = "/Users/oscardodds/projects/10koma-shukatsu/public/taxonomy.json"
CSV = "/Users/oscardodds/projects/10koma-shukatsu/tools/taxonomy_companies.csv"

tax = json.load(open(TAX))
chu2dai = {}; chu2g16 = {}
for d in tax["daibunrui"]:
    for c in d["chubunrui"]:
        chu2dai[c["name"]] = d["name"]; chu2g16[c["name"]] = c["gyokai16"]
valid_tags = {t["label"] for t in tax["tags"]}

errs = []; seen = set(); rows = 0
csv_chu = collections.Counter()
with open(CSV, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows += 1
        slug = r["slug"]; dai = r["新・大分類"]; chu = r["新・中分類"]; tags = r.get("横断タグ","")
        if slug in seen: errs.append(f"slug重複: {slug}")
        seen.add(slug); csv_chu[chu]+=1
        if chu not in chu2dai:
            errs.append(f"[{slug}] 未知の中分類: {chu}"); continue
        if chu2dai[chu] != dai:
            errs.append(f"[{slug}] 大分類不一致: CSV='{dai}' vs taxonomy='{chu2dai[chu]}' (中={chu})")
        for t in filter(None, tags.split("/")):
            if t not in valid_tags: errs.append(f"[{slug}] 未知タグ: {t}")

# 社数は固定値(旧: 400)でなく companies.json との双方向一致で見る(2026-11-20 新規社追加に対応)
_cj = json.load(open("/Users/oscardodds/projects/10koma-shukatsu/public/companies.json"))
_cj_ids = {c["id"] for arr in _cj.values() for c in arr}
if not _cj_ids: errs.append("companies.json の社が0件(空=失敗)")
_miss_csv = sorted(_cj_ids - seen)   # 未分類 = companies.json にあるが CSV に無い
_miss_cj = sorted(seen - _cj_ids)    # 欠落 = CSV にあるが companies.json に無い(生成し忘れ)
print(f"未分類(companies.jsonにあってCSVに無い)={len(_miss_csv)} / 欠落(CSVにあってcompanies.jsonに無い)={len(_miss_cj)} (分母: CSV {rows}社・companies.json {len(_cj_ids)}社)")
if _miss_csv: errs.append(f"未分類: {_miss_csv}")
if _miss_cj: errs.append(f"欠落(build_companies_taxonomy.py 未実行?): {_miss_cj}")

# 空バケツ(taxonomyにあるがCSVに個社0の中分類)
empty = [c for c in chu2dai if csv_chu.get(c,0)==0]

print(f"CSV社数={rows}  中分類(CSV使用)={len(csv_chu)}  中分類(taxonomy定義)={len(chu2dai)}")
if empty:
    print("⚠ 個社0件の中分類(空バケツ):")
    for c in empty: print(f"    - {c}  [大={chu2dai[c]}, gyokai16={chu2g16[c]}]")
if errs:
    print("\n❌ 整合エラー:")
    for e in errs: print("   ", e)
    sys.exit(1)
print("\n✅ 整合OK (空バケツ以外の不整合なし)")
