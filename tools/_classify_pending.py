#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""滞留505コマを型別に仕分ける（着手前レポート）。生成・反映は一切しない。
実データ = 共通の修正案[要画像再生成] + imageqa_list(混在型人QA) を _pending_image_map で
dedup+drained除外した「本当の未反映集合」に対し classify_image_bug_cats を全件適用。"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, ".")
import phase_c_image_fix as PCI
import phase_c_auto as PA
import phase_c_autoloop as A

SAFE = {"meta_frame", "white_band", "hline"}   # 真の安全型(自動反映可)= AUTO_SAFE_TYPES 既定(text_leak除外後)
FRAGILE = {"scale", "hands", "accuracy"}       # physical_plausibility/props_and_hands/scale 系(人レビュー必須)
# text_leak(焼き込み文字/吹き出し)は独立バケット「目視必須」= mixed候補生成→人QA後反映(自動反映しない)

cf_items = PCI.commonfixes_fast().get("items", [])
qa_items = PCI.gas({"mode": "imageqa_list"}).get("items", [])
pmap = PA._pending_image_map(cf_items=cf_items, qa_items=qa_items)   # {slug: set(koma)} dedup+drained除外

# 各(slug,koma)の detail 本文を common-fixes から回収（複数行あれば連結）
detail_map = {}   # (slug,koma) -> concatenated detail
for x in cf_items:
    m = re.match(r"\[要画像再生成\]\s*([^:：]+?)[:：]\s*(.*)", str(x.get("rule", "")), re.S)
    if not m:
        continue
    slug = A.resolve_slug(m.group(1).strip())
    if not slug:
        continue
    for km in re.split(r"(?:^|;|；)\s*(?=koma\s*\d+|コマ\s*\d+)", m.group(2)):
        kk = re.search(r"(?:koma|コマ)\s*0*(\d+)\s*[:：]?\s*(.*)", km, re.S)
        if not kk:
            continue
        detail_map.setdefault((slug, int(kk.group(1))), []).append(kk.group(2).strip())
# 混在型人QA由来の detail
for it in qa_items:
    slug = it.get("slug"); koma = it.get("koma")
    if slug and koma is not None:
        d = it.get("detail") or it.get("note") or ""
        if d:
            detail_map.setdefault((slug, int(koma)), []).append(str(d))

buckets = {"safe": [], "review_text": [], "fragile": [], "unknown": []}
per_type = {}
by_company_type = {}   # slug -> set of bucket
rows = []
total = 0
for slug, komas in pmap.items():
    for koma in sorted(komas):
        total += 1
        detail = " / ".join(detail_map.get((slug, koma), []))
        cats = PCI.classify_image_bug_cats(detail)
        if not cats:
            bucket = "unknown"
        elif set(cats) & FRAGILE:            # scale/hands/accuracy を含むなら崩れやすい優先
            bucket = "fragile"
        elif "text_leak" in cats:            # 焼き込み文字/吹き出し = 目視必須(自動反映しない)
            bucket = "review_text"
        elif set(cats) <= SAFE:              # meta_frame/white_band/hline のみ = 自動反映可
            bucket = "safe"
        else:
            bucket = "unknown"
        buckets[bucket].append((slug, koma))
        key_t = "+".join(cats) if cats else "(未分類)"
        per_type[key_t] = per_type.get(key_t, 0) + 1
        by_company_type.setdefault(slug, set()).add(bucket)
        rows.append({"slug": slug, "koma": koma, "cats": cats, "bucket": bucket,
                     "detail": detail[:120]})

def ncomp(bkt):
    return len(set(s for s, k in buckets[bkt]))

label = {"safe": "安全型auto", "review_text": "焼き込み文字=目視必須",
         "fragile": "崩れやすい(人レビュー)", "unknown": "要調査"}
print(f"=== 滞留 pending 総数: {total} コマ / {len(pmap)} 社 ===\n")
for b in ("safe", "review_text", "fragile", "unknown"):
    print(f"[{label[b]}] {len(buckets[b])} コマ / {ncomp(b)} 社")
print("\n--- 型内訳(cats組合せ別) ---")
for t, n in sorted(per_type.items(), key=lambda x: -x[1]):
    grp = "safe" if t != "(未分類)" and set(t.split("+")) <= SAFE else ("unknown" if t == "(未分類)" else "fragile")
    print(f"  {n:>4}  {t:<28} [{grp}]")

# 純安全社（その社の pending が全て safe）= まとめて自走できる社
pure_safe = [s for s in pmap if by_company_type.get(s) == {"safe"}]
print(f"\n--- 純・安全型のみの社(全pendingがsafe): {len(pure_safe)} 社 ---")
print(", ".join(sorted(pure_safe)[:40]) + (" ..." if len(pure_safe) > 40 else ""))

out = Path("_pending_classification.json")
json.dump({"total": total, "companies": len(pmap), "as_of": "2026-08-24",
           "safe": len(buckets["safe"]), "review_text": len(buckets["review_text"]),
           "fragile": len(buckets["fragile"]), "unknown": len(buckets["unknown"]),
           "safe_companies": ncomp("safe"), "review_text_companies": ncomp("review_text"),
           "fragile_companies": ncomp("fragile"), "unknown_companies": ncomp("unknown"),
           "pure_safe_companies": sorted(pure_safe),
           "per_type": per_type, "rows": rows},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n詳細 → {out}")
