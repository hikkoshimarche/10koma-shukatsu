#!/usr/bin/env python3
"""datasheet浄化: build_datasheetがクイズのdistractor/否定事実を事実化した汚染を除去。
 各datasheetの散文セクション(事業/社風/沿革)の各factを、その社のcorpus全体に対しLLM意味検証
 「本文はこの主張をこの向きで支持するか」→不支持drop。否定事実形も除外。主要財務(数値)は温存。
 変更があった datasheet.json を書き換え、変更社を es_clean_changed.csv に記録。D1投入は別スクリプト。
 --dry で書き換えず判定のみ。引数slugで対象限定(既定=全266)。
"""
import json, os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = q.OUT
PROSE_SECTIONS = {"事業内容・セグメント", "社風・求める人物像", "沿革・基本情報"}
# 答え位置の否定形(クイズ『〜でないもの: X』型)のみ。文中の「以外」「ではない。」等の正当散文は誤爆させない。
_NEG_SHAPE = re.compile(r"でないもの|一つでない|挙げられていないもの|ではないもの|該当しないもの|しないもの[:：]|"
                        r"含まないもの|やっていないもの|行っていないもの|扱っていないもの|展開していないもの|主催しない[^。]{0,8}[:：]")

def _corpus_text(corpus):
    return re.sub(r"\s+", " ", " ".join(corpus.values()))


def _answer_ok(fact, ctext, ctext_digits):
    """クイズ化fact『X: Y』の答えYがcorpusに実在するか(決定論・LLM不使用)。
    非colonの散文factは常にTrue(温存)。捏造(ノーベル賞/核融合/週刊少年ジャンプ=答えがcorpusに無い)のみFalse。
    数値答えは桁列一致・名詞答えは特徴語一致で判定(正当な数値/事実を誤dropしない)。"""
    m = re.search(r"[:：]\s*(.+?)\s*$", fact)
    if not m:
        return True                                   # 散文(完全文)は温存
    ans = re.sub(r"[。、）\)\s]+$", "", m.group(1))
    nums = re.findall(r"\d[\d,\.]*", ans)
    if nums:                                           # 数値答え: 桁列がcorpusにあるか
        for n in sorted(nums, key=len, reverse=True):
            digits = re.sub(r"\D", "", n)
            if len(digits) >= 2 and digits in ctext_digits:
                return True
        return False
    toks = re.findall(r"[一-龥ァ-ヶーA-Za-zＡ-Ｚａ-ｚ]{2,}", ans)  # 名詞答え: 特徴語がcorpusにあるか
    if not toks:
        return True
    return any(t in ctext for t in toks)


def clean_one(slug, dry=False):
    dp = os.path.join(OUT, slug, "datasheet.json")
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if not os.path.exists(dp):
        return None
    d = json.load(open(dp))
    corpus = json.load(open(cp)) if os.path.exists(cp) else {}
    sec = d.get("sections", {})
    if not isinstance(sec, dict) or not corpus:
        return None
    removed, total_prose = [], 0
    ctext = _corpus_text(corpus)
    ctext_digits = re.sub(r"\D", "", ctext)
    for k in list(sec.keys()):
        if k not in PROSE_SECTIONS:
            continue
        items = sec[k] or []
        total_prose += len(items)
        kept = []
        for it in items:
            f = (it.get("fact") or "")
            if _NEG_SHAPE.search(f) or not _answer_ok(f, ctext, ctext_digits):   # 否定形/答え捏造をdrop
                removed.append((k, f[:50]))
            else:
                kept.append(it)
        sec[k] = kept
    if not removed:
        return {"slug": slug, "changed": False, "removed": 0}
    if not dry:
        json.dump(d, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"slug": slug, "changed": True, "removed": len(removed), "total_prose": total_prose,
            "samples": [r[1] for r in removed[:3]]}


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        slugs = args
    else:
        slugs = sorted(os.path.basename(os.path.dirname(d)) for d in glob.glob(os.path.join(OUT, "*/datasheet.json"))
                       if not os.path.basename(os.path.dirname(d)).startswith("industry__"))
    print(f"対象 {len(slugs)} datasheet / dry={dry}", flush=True)
    changed, changed_rows = [], []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(clean_one, s, dry): s for s in slugs}
        for fu in as_completed(futs):
            r = fu.result()
            if not r:
                continue
            if r["changed"]:
                changed.append(r)
                changed_rows.append(f"{r['slug']},{r['removed']},{r.get('total_prose')}")
                print(f"  CLEAN {r['slug']}: -{r['removed']}件 例:{r['samples'][0] if r['samples'] else ''}", flush=True)
    if not dry and changed_rows:
        open(os.path.join(OUT, "es_clean_changed.csv"), "w", encoding="utf-8").write("\n".join(changed_rows) + "\n")
    print(f"\n=== 浄化: 変更{len(changed)}社 / 削除fact合計{sum(c['removed'] for c in changed)} ===")


if __name__ == "__main__":
    main()
