#!/usr/bin/env python3
import sys, os, json, hashlib, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_difficulty as D
import quiz_difficulty_pilot as P
import quiz_lint as QL

OUT = D.OUT
V24 = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot_v24_final")
V25 = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot_v25_final")
os.makedirs(V25, exist_ok=True)
REGEN = {"mitsubishi-corp": "三菱商事", "mufg": "三菱UFJ銀行"}   # 実在誤答検出社のみ再生成

name_pool = []
for slug, _ in P.PILOT:
    for x in json.load(open(f"{OUT}/{slug}/quiz_30q_locked_v3.json")):
        for o in x.get("options", []):
            if D._is_person(o) and o not in name_pool:
                name_pool.append(o)

changed = []
for slug, name in REGEN.items():
    quiz = json.load(open(f"{OUT}/{slug}/quiz_30q_locked_v3.json"))
    for x, lv in zip(quiz, D.classify(slug, quiz)):
        x["difficulty"] = lv
    corpus = json.load(open(f"{OUT}/{slug}/quiz_corpus_locked_v3.json"))
    quiz, dropped, inactive = D.clean_existing(quiz, corpus, name_pool=name_pool)
    pool = D._source_pool(slug)
    used, sused = set(), set()
    for x in quiz:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    g1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
    for x in g1:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    g2 = D.gen_lv(slug, name, 2, 10, exclude=used, sem_used=sused, pool=pool)
    json.dump({"existing": quiz, "gen_lv1": g1, "gen_lv2": g2, "dropped_existing": dropped,
               "inactive_existing": inactive}, open(f"{OUT}/{slug}/quiz_difficulty_v2.json", "w"),
              ensure_ascii=False, indent=1)
    md = P.md_company(slug, name, quiz, g1, g2)
    sha8 = hashlib.sha256(md.encode()).hexdigest()[:8]
    open(f"{V25}/{slug}__{sha8}.md", "w").write(md)
    changed.append((slug, sha8, len(g1), len(g2)))
    print(f"再生成 {slug}: Lv1={len(g1)} Lv2={len(g2)} sha8={sha8}")
    # 実在誤答が残っていないか検証
    ft = D._full_corpus_text(slug, pool)
    viol = [x["q_text"][:22] for x in g1 + g2 if not D._distractor_ok(x, ft)]
    print(f"   実在誤答残存: {len(viol)} {viol[:2]}")

# 無変更3社: v24→v25 バイト不変コピー + sha8一致明記
print("=== 無変更3社(v24からバイト不変) ===")
for f in sorted(glob.glob(f"{V24}/*.md")):
    bn = os.path.basename(f)
    slug = bn.split("__")[0]
    if slug in REGEN or bn.startswith("README"):
        continue
    shutil.copy2(f, f"{V25}/{bn}")
    v = hashlib.sha256(open(f"{V25}/{bn}", "rb").read()).hexdigest()[:8]
    print(f"  {bn}  sha8={v} (v24名={bn.split('__')[1][:8]}) {'一致✓' if v == bn.split('__')[1][:8] else '✗'}")
