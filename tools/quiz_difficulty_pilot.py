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
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot_v23_final")
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


def _naturalize(qt):
    """#4c 不自然な問文を日本語らしく軽微修正(例: LNG輸送に関する特徴は?)。"""
    import quiz_fanout as q
    try:
        r = q.openai_chat([{"role": "system", "content": "就活クイズの問文を、意味を変えず日本語として自然な1文に直す。固有名詞・数値は保持。"},
                           {"role": "user", "content": f"問文: 「{qt}」\n自然な問文だけを出力(前置き無し)"}], max_tokens=120, temperature=0)
        r = re.sub(r"^[「『]|[」』]$", "", (r or "").strip().splitlines()[0]) if r else qt
        return r or qt
    except Exception:
        return qt


def main():
    os.makedirs(HANDOFF, exist_ok=True)
    summary = []
    SHA_LIST = []
    import quiz_lint as QL, re
    # #4a 人名差替用: 全5社の既存人名選択肢を実在名プールに収集
    name_pool = []
    for slug, _ in PILOT:
        for x in json.load(open(os.path.join(OUT, slug, "quiz_30q_locked_v3.json"))):
            for o in x.get("options", []):
                if D._is_person(o) and o not in name_pool:
                    name_pool.append(o)
    for slug, name in PILOT:
        f = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        quiz = json.load(open(f))
        corpus = json.load(open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")))
        levels = D.classify(slug, quiz)
        for x, lv in zip(quiz, levels):
            x["difficulty"] = lv
        # #4c 不自然な問文(『〜に関する特徴は？』等)を自然化
        for x in quiz:
            if re.search(r"に関する特徴|について正しい|に関して正しい|の特徴は？$", x.get("q_text", "")):
                x["q_text"] = _naturalize(x["q_text"]); x["_qfixed"] = True
        n_before = len(quiz)
        quiz, dropped, inactive = D.clean_existing(quiz, corpus, name_pool=name_pool)   # #3④a
        pool = D._source_pool(slug)
        used, sused = set(), set()
        for x in quiz:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        gen1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
        for x in gen1:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        gen2 = D.gen_lv(slug, name, 2, 10, exclude=used, sem_used=sused, pool=pool)
        out = {"existing": quiz, "gen_lv1": gen1, "gen_lv2": gen2,
               "dropped_existing": dropped, "inactive_existing": inactive}
        json.dump(out, open(os.path.join(OUT, slug, "quiz_difficulty_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        _md = md_company(slug, name, quiz, gen1, gen2)
        import hashlib as _hl
        _sha8 = _hl.sha256(_md.encode()).hexdigest()[:8]
        open(os.path.join(HANDOFF, f"{slug}__{_sha8}.md"), "w", encoding="utf-8").write(_md)
        SHA_LIST.append((f"{slug}__{_sha8}.md", _sha8))
        d = Counter(x["difficulty"] for x in quiz if x.get("active", True))
        summary.append((slug, name, dict(d), len(gen1), len(gen2), n_before, len(dropped), len(inactive)))
        print(f"{slug}: 既存{n_before}→有効{len(quiz)}(drop{len(dropped)}/inactive{len(inactive)}) Lv3/4={d.get(3,0)}/{d.get(4,0)} 新規Lv1={len(gen1)} Lv2={len(gen2)}", flush=True)
    print("\n=== SHA8 ===")
    for fn, sh in SHA_LIST:
        print(f"  {fn}  {sh}")
    print("=== SUMMARY ===", json.dumps(summary, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
