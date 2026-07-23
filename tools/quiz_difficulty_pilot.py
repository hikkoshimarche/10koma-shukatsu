#!/usr/bin/env python3
"""難易度パイロット: 5社の既存問題を分類＋Lv1/Lv2を新規生成し、Lv別一覧mdを受け渡しへ。
本番D1は触らない。出力: output/<slug>/quiz_difficulty_v1.json + 受け渡し/quiz_difficulty_pilot/*.md
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_difficulty as D
import quiz_fanout as q
from collections import Counter

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_difficulty_pilot_v2")
PILOT = [("mitsubishi-corp", "三菱商事"), ("keyence", "キーエンス"), ("nintendo", "任天堂"),
         ("mufg", "三菱UFJ銀行"), ("meiji-hd", "明治ホールディングス")]
LVN = {1: "Lv1入門", 2: "Lv2基礎", 3: "Lv3応用", 4: "Lv4実践"}


def md_company(slug, name, existing, gen1, gen2):
    L = [f"# {name}（{slug}） 難易度別クイズ", ""]
    # 分類分布
    dist = Counter(x["difficulty"] for x in existing)
    L.append(f"既存{len(existing)}問の分類: Lv1={dist[1]} / Lv2={dist[2]} / Lv3={dist[3]} / Lv4={dist[4]}")
    L.append(f"新規生成: Lv1入門={len(gen1)}問 / Lv2基礎={len(gen2)}問（出典付・既存datasheet/corpus範囲・決算数値なし）")
    L.append("")
    # Lv別に既存＋新規を並べる
    allq = [(x["difficulty"], x, "既存") for x in existing] + \
           [(1, x, "新規") for x in gen1] + [(2, x, "新規") for x in gen2]
    for lv in (1, 2, 3, 4):
        items = [(x, tag) for d, x, tag in allq if d == lv]
        L.append(f"## {LVN[lv]}（{len(items)}問）")
        if not items:
            L.append("_（なし）_\n")
            continue
        for x, tag in items:
            opts = x.get("options", [])
            ci = x.get("correct", 0)
            L.append(f"- [{tag}] {x.get('q_text','')}")
            for j, o in enumerate(opts):
                L.append(f"    {'★' if j == ci else '　'} {o}")
            if tag == "新規" and x.get("source_url"):
                L.append(f"    出典: {x['source_url']}")
        L.append("")
    return "\n".join(L)


def main():
    os.makedirs(HANDOFF, exist_ok=True)
    summary = []
    import quiz_lint as QL
    for slug, name in PILOT:
        f = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        quiz = json.load(open(f))
        corpus = json.load(open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")))
        levels = D.classify(slug, quiz)
        for x, lv in zip(quiz, levels):
            x["difficulty"] = lv
        n_before = len(quiz)
        quiz, dropped = D.clean_existing(quiz, corpus)      # v2.1③ 既存clean
        pool = D._source_pool(slug)                         # #4 公式本文プール(1社1回)
        # レベル間dedup: 既存→gen1→gen2 を fact-key＋意味シグネチャで排他
        used, sused = set(), set()
        for x in quiz:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        gen1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
        for x in gen1:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        gen2 = D.gen_lv(slug, name, 2, 10, exclude=used, sem_used=sused, pool=pool)
        out = {"existing": quiz, "gen_lv1": gen1, "gen_lv2": gen2, "dropped_existing": dropped}
        json.dump(out, open(os.path.join(OUT, slug, "quiz_difficulty_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        open(os.path.join(HANDOFF, f"{slug}.md"), "w", encoding="utf-8").write(md_company(slug, name, quiz, gen1, gen2))
        d = Counter(x["difficulty"] for x in quiz)
        summary.append((slug, name, dict(d), len(gen1), len(gen2), n_before, len(dropped), dropped[:2]))
        print(f"{slug}: 既存{n_before}→{len(quiz)}(drop{len(dropped)}) Lv1={d[1]}/Lv2={d[2]}/Lv3={d[3]}/Lv4={d[4]} 新規Lv1={len(gen1)} Lv2={len(gen2)} drop例={dropped[:1]}", flush=True)
    print("\n=== SUMMARY ===", json.dumps(summary, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
