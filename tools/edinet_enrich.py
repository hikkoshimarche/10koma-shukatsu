#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EDINET有報の質的節(沿革/事業の内容/従業員/経営方針/サステナ/研究開発)から散文factを抽出し
datasheetを増強。gather_proseをEDINET節に差し替えてenrich_oneを再利用(検証/財務温存はそのまま)。
material検証用にlocked corpusへもEDINET節をマージ。source_url=EDINET直PDF(金融庁・公式一次)。
usage: python edinet_enrich.py <slug>=<docID> [...]"""
import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import build_edinet_corpus as BEC
import enrich_datasheet as E
import rollout_enrich as R

OUT = q.OUT


def edinet_prose(docid):
    text = BEC.extract_text(docid)
    if len(text) < 3000:
        return {}, len(text)
    text = re.sub(r"[ \t]+", " ", text)
    src = BEC.PDF.format(docid)
    prose = {}
    for pat, ln in BEC.SECTIONS:
        m = re.search(pat, text)
        if not m:
            continue
        chunk = text[m.start():m.start() + ln].strip()
        digits = len(re.findall(r"\d", chunk))
        if len(chunk) > 300 and digits / max(len(chunk), 1) < 0.35:   # 表(数字だらけ)除外=散文のみ
            label = re.sub(r"\\|\||\s", "", pat)[:12]
            prose[f"{src}#{label}"] = chunk[:8000]
    return prose, len(text)


def run(slug, docid):
    before = R.material_count(slug)
    prose, tlen = edinet_prose(docid)
    if not prose:
        return {"slug": slug, "status": "edinet_extract_fail", "textlen": tlen, "before": before}
    # locked corpusへマージ(材料検証_answer_okがEDINET本文を参照できるように)
    lp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    locked = json.load(open(lp)) if os.path.exists(lp) else {}
    locked.update(prose)
    json.dump(locked, open(lp, "w"), ensure_ascii=False)
    # gather_proseをEDINET節へ差し替えてenrich_one再利用
    orig = E.gather_prose
    E.gather_prose = lambda s, n: prose
    try:
        res = E.enrich_one(slug)
    finally:
        E.gather_prose = orig
    R._cleanse_one(slug)
    after = R.material_count(slug)
    viol = [v for v in R.quality_violations(slug) if v[0] in ("人名は誰", "採用フロー")]
    return {"slug": slug, "status": res.get("status"), "before": before, "after": after,
            "pass": after >= 5 and not viol, "edinet_sections": len(prose), "added": res.get("added")}


def main():
    docs = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
    out = {}
    for slug, docid in docs.items():
        r = run(slug, docid)
        out[slug] = r
        print(f"  {slug:16s} 材料{r.get('before')}→{r.get('after')} {'✓' if r.get('pass') else '未達'} "
              f"EDINET節{r.get('edinet_sections','-')} added={r.get('added','-')} ({r.get('status')})", flush=True)
    json.dump(out, open(f"{R.SC}/edinet_result.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
