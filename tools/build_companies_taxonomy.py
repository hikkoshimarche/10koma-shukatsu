#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""companies.json を tools/taxonomy_companies.csv(=分類の唯一の正) から【生成】する。
分類は手で二重に持たない。CSVを直して本スクリプトを回せば companies.json が必ず追従する。

companies.json は2つの分類表現を持つが、どちらも CSV 由来＝二重管理ではない:
  (1) トップレベル18キー = CSV「現行分類(18)」列から生成する【凍結コンテナ】。
      ★なぜ残すか: ルーム(room_v3_complete.py 等)が id2ind={id:トップキー} を作り
        その18-JP名を IND18_TO_V3 に渡してアーキタイプを決めている。notion_sync /
        gen_selection_info / edinet_salary_sweep も18キー依存。ここを新中分類で再キーすると
        ルーム400社のペルソナが既定役割に落ちて壊れる(実証済)。
        よって18キーは「ルームのPhase3移行までの橋渡し」として凍結保持する。学生画面は
        (2)の各社フィールドを読む(company-list/compare/home/quiz/quiz-list/today で修正済)。
  (2) 各社 dai_slug/dai_name/chu_slug/chu_name/tags = CSV「新・大分類/中分類/横断タグ」から。
      = 新タクソノミーの正。学生が見る一覧・比較・検索・クイズはこれを読む。
D1 companies.industry_id は tools/build_d1_industry_from_csv.py が同じCSVから生成(別スクリプト)。
"""
import json, csv

ROOT = "/Users/oscardodds/projects/10koma-shukatsu"
TAX  = f"{ROOT}/public/taxonomy.json"
CSVF = f"{ROOT}/tools/taxonomy_companies.csv"
CJ   = f"{ROOT}/public/companies.json"

tax = json.load(open(TAX))
chu_idx = {c["name"]: (c["slug"], d["slug"], d["name"])
           for d in tax["daibunrui"] for c in d["chubunrui"]}   # 中分類name -> (chu_slug,dai_slug,dai_name)
tag_label2id = {t["label"]: t["id"] for t in tax["tags"]}

# CSV: id -> (現行分類18, 中分類name, [tag_id])
row_of = {}
for r in csv.DictReader(open(CSVF, encoding="utf-8-sig")):
    tag_ids = [tag_label2id[t] for t in filter(None, r.get("横断タグ", "").split("/"))]
    row_of[r["slug"]] = (r["現行分類(18)"], r["新・中分類"], tag_ids)

old = json.load(open(CJ))
# id -> 既存の基礎フィールド(liff/video等)と、現在のトップキー(整合チェック用)
base = {}; cur_key = {}; order = []
for topkey, arr in old.items():
    for c in arr:
        base[c["id"]] = {k: c[k] for k in ("id", "name", "jukoma_liff_id", "room_liff_id", "video_url", "kessan_url") if k in c}
        cur_key[c["id"]] = topkey
        order.append(c["id"])

# 生成: 現行分類(18)でグルーピング(=現状キーと一致するはず)。順序は既存を保持=差分最小。
errs = []
grouped = {}  # topkey -> [company]
for cid in order:
    if cid not in row_of:
        errs.append(f"CSVに無い社: {cid}"); continue
    genkou18, chu_name, tag_ids = row_of[cid]
    if genkou18 != cur_key[cid]:
        errs.append(f"{cid}: 現行分類(18)='{genkou18}' が現トップキー='{cur_key[cid]}' と不一致(コンテナ破壊回避のため停止)")
        continue
    if chu_name not in chu_idx:
        errs.append(f"{cid}: 未知の中分類 '{chu_name}'"); continue
    chu_slug, dai_slug, dai_name = chu_idx[chu_name]
    obj = dict(base[cid])
    obj.update({"dai_slug": dai_slug, "dai_name": dai_name,
                "chu_slug": chu_slug, "chu_name": chu_name, "tags": tag_ids})
    grouped.setdefault(genkou18, []).append(obj)

if errs:
    print("❌ 生成中止:"); [print("  ", e) for e in errs]; raise SystemExit(1)

# トップキーの順序は既存 companies.json の順序を踏襲
new = {k: grouped[k] for k in old.keys() if k in grouped}
with open(CJ, "w", encoding="utf-8") as f:
    json.dump(new, f, ensure_ascii=False, indent=2); f.write("\n")

n = sum(len(v) for v in new.values())
print(f"✅ companies.json 生成: {n}社 / トップキー{len(new)} / 各社に新dai_chu+tags(CSV由来)")
