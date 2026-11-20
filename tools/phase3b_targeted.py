#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase3b: 未到達8社(mckinsey/pola-orbis除外)に、site-nav発見付きaugmentで再試行。
公式ドメインは個別に確定(kaga=kaga.co.jp等)。fact5/材料5基準は緩めない。"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import augment_corpus as A
import enrich_datasheet as E
import rollout_enrich as R

SC = R.SC
# 個別確定ドメイン(mckinsey/pola-orbisは除外=タブB結論・重複回避)
DOMAINS = {
    "moneyforward": "https://corp.moneyforward.com",
    "benesse-hd": "https://www.benesse-hd.co.jp",
    "cosmos-pharma": "https://www.cosmospc.co.jp",
    "kaga-electronics": "https://www.kaga.co.jp",
    "kao": "https://www.kao.com/jp",
    "norinchukin": "https://www.nochubank.or.jp",
    "yamazaki-pan": "https://www.yamazakipan.co.jp",
    "openai-japan": "https://openai.com",
}


def main():
    res = {}
    for slug, dom in DOMAINS.items():
        before = R.material_count(slug)
        try:
            aug = A.augment(slug, seed_domain=dom)
            E.enrich_one(slug)
            R._cleanse_one(slug)
        except Exception as e:
            res[slug] = {"status": "err", "err": str(e)[:120]};
            print(f"  {slug}: ERR {e}", flush=True); continue
        after = R.material_count(slug)
        viol = [v for v in R.quality_violations(slug) if v[0] in ("人名は誰", "採用フロー")]
        res[slug] = {"before": before, "after": after, "pass": after >= 5 and not viol,
                     "added_pages": aug["added_pages"], "added_chars": aug["added_chars"], "dom": dom}
        print(f"  {slug:18s} 材料{before}→{after} {'✓' if after>=5 and not viol else '未達'} "
              f"+{aug['added_pages']}p/{aug['added_chars']}字 dom={dom}", flush=True)
    json.dump(res, open(f"{SC}/phase3b_result.json", "w"), ensure_ascii=False)
    ok = [s for s, d in res.items() if d.get("pass")]
    print(f"=== Phase3b: 通過{len(ok)}/{len(DOMAINS)}: {ok} ===", flush=True)


if __name__ == "__main__":
    main()
