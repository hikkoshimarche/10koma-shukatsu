#!/usr/bin/env python3
"""未反映社の datasheet.json を rendered_corpus.json から生成/増強(Anthropic・Source-or-Silence)。
enrich_datasheet.enrich_one の 生成(DSQ)→浄化(否定形/答え捏造drop)→意味検証(出典が主張を支持) を再利用し、
corpus源だけ rendered_corpus.json に差替え(既存パイプはquiz_corpus_locked_v3.json前提のため)。
datasheet.json 無ければ空sectionsでseed。主要財務セクションは非PROSEのため温存。
usage: QUIZ_LLM=anthropic QUIZ_MAX_USD=20 python gen_datasheet_missing.py <slug...>
"""
import os, sys, json, re
os.environ.setdefault("QUIZ_LLM", "anthropic")
os.environ.setdefault("QUIZ_MAX_USD", "20")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrich_datasheet as E

OUT = E.OUT
_cj = json.load(open(os.path.expanduser("~/projects/10koma-shukatsu/public/companies.json")))
NAME_BY = {c["id"]: c["name"] for v in _cj.values() for c in v}


def my_gather(slug, name):
    """corpus源を rendered_corpus.json(+quiz_corpus)に。質的ページ優先で最大10頁。"""
    prose = {}
    for fn in ("rendered_corpus.json", "quiz_corpus_locked_v3.json"):
        f = os.path.join(OUT, slug, fn)
        if not os.path.exists(f):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for u, v in d.items():
            txt = v.get("text") if isinstance(v, dict) else v
            if not txt or "/dam/" in u:
                continue
            # Access-Denied除外 + 実財務ドキュメント(短信/有報)だけ除外(決算はnav語なので除外しない)
            if len(txt) > 400 and "Access Denied" not in txt[:60] \
               and "permission to access" not in txt[:120] \
               and not re.search(r"短信|有価証券報告書", txt[:200]):
                prose.setdefault(u, txt[:8000])
    items = list(prose.items())
    qual = [x for x in items if any(k in x[0].lower() for k in E.QUAL_KW)]
    rest = [x for x in items if x not in qual]
    return dict((qual + rest)[:10])


E.gather_prose = my_gather   # monkeypatch: corpus源を差替え


def _gen_qual_facts_4k(name, prose):
    """max_tokens=2000だと日本語で長文factがJSON途中truncate→parseで0factになる回帰。4000へ拡張。"""
    src = "\n\n".join(f"===== source_url: {u} =====\n{b[:3500]}" for u, b in list(prose.items())[:8])
    txt = E.q.openai_chat([{"role": "system", "content": E.DSQ_SYS},
                           {"role": "user", "content": E.DSQ_USER.format(name=name, sources=src)}],
                          max_tokens=4000, temperature=0.2)
    data = E.q._parse_json(txt)
    return data.get("facts", []) if isinstance(data, dict) else []


E.gen_qual_facts = _gen_qual_facts_4k   # monkeypatch: truncation回避


def main():
    targets = sys.argv[1:]
    for slug in targets:
        dp = os.path.join(OUT, slug, "datasheet.json")
        if not os.path.exists(dp):
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            json.dump({"name": NAME_BY.get(slug, slug), "sections": {}},
                      open(dp, "w", encoding="utf-8"), ensure_ascii=False)
        try:
            r = E.enrich_one(slug)
        except Exception as e:
            r = {"slug": slug, "status": f"ERR:{str(e)[:80]}"}
        try:
            ds = json.load(open(dp))
            tot = sum(len(v) for v in ds.get("sections", {}).values())
        except Exception:
            tot = -1
        print(json.dumps({**r, "total_facts": tot}, ensure_ascii=False), flush=True)
        if not E.q.cost_ok():
            print("COST_GUARD STOP", flush=True)
            break
    print(f"=== COST ${E.q._cost['usd']:.3f} / calls {E.q._cost['calls']} ===", flush=True)


if __name__ == "__main__":
    main()
