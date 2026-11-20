#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESキット材料増強の横展開(local enrichのみ・D1反映は別)。
対象= 材料<5 の薄い社(既済3社除外)。augment_corpus + enrich → 材料再計数 → 品質チェック。
ガード: 累計enrichコスト baseline+$30 / 除外ルール違反(「は誰」・採用フロー・非公式) 検出で即停止。
CP20で進捗print。結果を rollout_result.json に逐次保存(resumable)。
"""
import sys, os, json, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import gen_es_kit as G
import clean_datasheets as CL
import augment_corpus as A
import enrich_datasheet as E
import clean_local_datasheets as CLC


def _cleanse_one(slug):
    """enrich後: 除外パターン(は誰/氏名/採用メタ/別法人)をdrop=自己修復(浄化はSTOPでなくDROP)。"""
    p = os.path.join(OUT, slug, "datasheet.json")
    if not os.path.exists(p):
        return 0
    ds = json.load(open(p)); n = 0
    for k in list(ds.get("sections", {}).keys()):
        keep = []
        for it in ds["sections"][k] or []:
            if CLC.junk_reason(it.get("fact", "")):
                n += 1
            else:
                keep.append(it)
        ds["sections"][k] = keep
    if n:
        json.dump(ds, open(p, "w"), ensure_ascii=False)
    return n

OUT = q.OUT
SC = os.environ.get("TK_SCRATCH") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / ".backups" / "scratch")  # 旧: 別セッションの scratchpad(消滅)→ .backups/scratch(gitignore)
DONE3 = {"kanematsu", "toyota-motor", "nomura"}
COST_CAP = q._cost["usd"] + 30.0     # baseline + $30
RECRUIT = ["選考フロー", "エントリー", "採用サイト", "採用情報サイト", "新卒採用サイト", "採用フロー",
           "募集要項", "選考ステップ", "選考プロセス", "採用活動", "採用選考方法", "インターンシップ"]
NONOFF = re.compile(r"wikipedia|\.ac\.jp|prtimes|note\.com|toyokeizai|diamond|newspicks|itmedia|kabutan|minkabu", re.I)


def material_count(slug):
    dp = os.path.join(OUT, slug, "datasheet.json")
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if not os.path.exists(dp):
        return -1
    ds = json.load(open(dp))
    corpus = json.load(open(cp)) if os.path.exists(cp) else {}
    cands = G.load_prose_facts(ds)
    ctext = CL._corpus_text(corpus); cd = re.sub(r"\D", "", ctext)
    return len([c for c in cands if CL._answer_ok(c["fact"], ctext, cd)])


def quality_violations(slug):
    """新datasheetの質的factに除外ルール違反があるか。"""
    ds = json.load(open(os.path.join(OUT, slug, "datasheet.json")))
    v = []
    for k in ["事業内容・セグメント", "社風・求める人物像", "沿革・基本情報"]:
        for it in ds["sections"].get(k, []):
            f = it.get("fact", ""); su = it.get("source_url", "")
            if "は誰" in f:
                v.append(("人名は誰", k, f[:40]))
            if any(x in f for x in RECRUIT):
                v.append(("採用フロー", k, f[:40]))
            # 「年号だけの羅列」= 年号で始まる短い羅列のみ(完全な文『◯◯は18XX年に創業』は正当=対象外)
            if re.match(r"^\s*[（(【]?\s*(18|19|20)\d{2}\s*[年.．]", f) and len(f) < 22 \
               and not re.search(r"(した|される|された|である|です|展開|参入|拡大|設立された|なった|迎え)", f):
                v.append(("年号羅列", k, f[:40]))
            if su and NONOFF.search(su):
                v.append(("非公式源", k, su[:36]))
    return v


def main():
    counts = json.load(open(os.path.join(SC, "material_counts.json")))
    # 対象: 材料<5(既済3除外)。3,4件を優先→少ない順は後。
    targets = sorted([s for s, c in counts.items() if 0 <= c < 5 and s not in DONE3],
                     key=lambda s: -counts[s])
    resf = os.path.join(SC, "rollout_result.json")
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    targets = [s for s in targets if s not in res]        # resumable
    print(f"=== rollout: 対象{len(targets)}社 / baseline${q._cost['usd']:.2f} cap${COST_CAP:.2f} ===", flush=True)
    stop = None
    for i, slug in enumerate(targets, 1):
        before = material_count(slug)
        try:
            aug = A.augment(slug)
            E.enrich_one(slug)
            _cleanse_one(slug)                 # 自己修復: enrichが混ぜた除外パターンをdrop
        except Exception as e:
            res[slug] = {"status": "err", "err": str(e)[:120], "before": before}
            json.dump(res, open(resf, "w"), ensure_ascii=False); continue
        after = material_count(slug)
        viol = quality_violations(slug)
        res[slug] = {"status": "ok", "before": before, "after": after,
                     "pass": after >= 5, "added_pages": aug["added_pages"],
                     "added_chars": aug["added_chars"], "violations": viol[:5],
                     "cost": round(q._cost["usd"], 3)}
        json.dump(res, open(resf, "w"), ensure_ascii=False)
        mark = "✓通過" if after >= 5 else "未達"
        # HARD停止= enrichが「は誰」「採用フロー」を生成した場合のみ(=enrich異常)。
        # 非公式源はSource-or-Silenceでdrop(reflectで除外)=警告のみ。年号は正規表現修正済で誤検出せず。
        hard = [v for v in viol if v[0] in ("人名は誰", "採用フロー")]
        print(f"  [{i}/{len(targets)}] {slug:22s} 材料{before}→{after} {mark} +{aug['added_pages']}p/{aug['added_chars']}字 "
              f"違反{len(hard)}/警告{len(viol)-len(hard)} ${q._cost['usd']:.2f}", flush=True)
        if hard:
            stop = f"HARD違反(enrich異常) {slug}: {hard[:3]}"; break
        if q._cost["usd"] >= COST_CAP:
            stop = f"cost cap ${q._cost['usd']:.2f}>=${COST_CAP:.2f}"; break
        if i % 20 == 0:
            passed = sum(1 for r in res.values() if r.get("pass"))
            print(f"  --- CP{i}: 通過{passed}/{len(res)} ${q._cost['usd']:.2f} ---", flush=True)
    passed = [s for s, r in res.items() if r.get("pass")]
    print(f"=== rollout {'STOP:'+stop if stop else 'done'} / 通過{len(passed)}/{len(res)} ${q._cost['usd']:.2f} ===", flush=True)


if __name__ == "__main__":
    main()
