#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase3: +0未達社(corpusに公式ドメイン無し)に、手動シードした公式ドメインで augment を再試行。
domain_seed.json の公式ドメインを渡して QUAL_PATHS を fetch → enrich → cleanse → 材料再計数。
取れなかった社は理由付きで報告(無理に埋めない)。"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import gen_es_kit as G
import clean_datasheets as CL
import augment_corpus as A
import enrich_datasheet as E
import rollout_enrich as R

OUT = q.OUT
SC = R.SC
SEED = json.load(open(f"{SC}/domain_seed.json"))


def main():
    res = json.load(open(f"{SC}/rollout_result.json"))
    # +0未達(pages無し) + +pあり未達 も seed で再試行(取れていない社全部)
    targets = sorted([s for s, d in res.items()
                      if d.get("status") == "ok" and not d.get("pass") and s in SEED])
    print(f"=== Phase3 seed再試行: {len(targets)}社 ===", flush=True)
    p3 = {}
    for i, slug in enumerate(targets, 1):
        before = R.material_count(slug)
        try:
            aug = A.augment(slug, seed_domain=SEED[slug])
            E.enrich_one(slug)
            R._cleanse_one(slug)
        except Exception as e:
            p3[slug] = {"status": "err", "err": str(e)[:120]}; continue
        after = R.material_count(slug)
        viol = [v for v in R.quality_violations(slug) if v[0] in ("人名は誰", "採用フロー")]
        p3[slug] = {"before": before, "after": after, "pass": after >= 5 and not viol,
                    "added_pages": aug["added_pages"], "added_chars": aug["added_chars"],
                    "seed": SEED[slug]}
        print(f"  [{i}/{len(targets)}] {slug:20s} {before}→{after} {'✓' if after>=5 else '未達'} "
              f"+{aug['added_pages']}p seed={SEED[slug][:40]}", flush=True)
    json.dump(p3, open(f"{SC}/phase3_result.json", "w"), ensure_ascii=False)
    ok = [s for s, d in p3.items() if d.get("pass")]
    print(f"=== Phase3 done: seedで通過{len(ok)}/{len(targets)} ===", flush=True)
    for s, d in p3.items():
        if not d.get("pass"):
            print(f"  未達: {s} {d.get('before')}→{d.get('after')} (+{d.get('added_pages',0)}p) seed={d.get('seed','')}")


if __name__ == "__main__":
    main()
