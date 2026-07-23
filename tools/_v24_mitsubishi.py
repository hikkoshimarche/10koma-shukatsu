#!/usr/bin/env python3
import sys, os, json, hashlib, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_difficulty as D
import quiz_difficulty_pilot as P
import quiz_lint as QL

OUT = D.OUT
V23 = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot_v23_final")
V24 = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot_v24_final")
os.makedirs(V24, exist_ok=True)

name_pool = []
for slug, _ in P.PILOT:
    for x in json.load(open(f"{OUT}/{slug}/quiz_30q_locked_v3.json")):
        for o in x.get("options", []):
            if D._is_person(o) and o not in name_pool:
                name_pool.append(o)

# 三菱商事のみ再生成
slug, name = "mitsubishi-corp", "三菱商事"
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
           "inactive_existing": inactive},
          open(f"{OUT}/{slug}/quiz_difficulty_v2.json", "w"), ensure_ascii=False, indent=1)
md = P.md_company(slug, name, quiz, g1, g2)
sha8 = hashlib.sha256(md.encode()).hexdigest()[:8]
open(f"{V24}/{slug}__{sha8}.md", "w").write(md)
print(f"三菱商事: 新規Lv1={len(g1)} Lv2={len(g2)} / drop{len(dropped)} inactive{len(inactive)}")
for x in g1:
    print("  L1:", x["q_text"][:36], "|正:", x["options"][x["correct"]][:14], "|出典:", x["source_url"][-26:])
print(f"FILE mitsubishi-corp__{sha8}.md")

# 同型混入(人名問に非人名誤答)全5社チェック
smart = 0
for s2, _ in P.PILOT:
    qz = json.load(open(f"{OUT}/{s2}/quiz_30q_locked_v3.json"))
    kept, _, _ = D.clean_existing([dict(x, difficulty=2) for x in qz], {}, name_pool=name_pool)
    for x in kept:
        if sum(1 for o in x.get("options", []) if D._is_person(o)) >= 2 \
           and any((k != x.get("correct")) and not D._is_person(o) for k, o in enumerate(x.get("options", []))):
            smart += 1
print("同型混入(人名問の非人名誤答) 全5社:", smart)

# 他4社 v23→v24 バイト不変コピー + sha8自己確認
print("=== 他4社 バイト不変コピー ===")
for f in sorted(glob.glob(f"{V23}/*.md")):
    bn = os.path.basename(f)
    if bn.startswith("mitsubishi") or bn.startswith("README"):
        continue
    shutil.copy2(f, f"{V24}/{bn}")
    v = hashlib.sha256(open(f"{V24}/{bn}", "rb").read()).hexdigest()[:8]
    named = bn.split("__")[1][:8]
    print(f"  {bn}  実sha8={v} 名sha8={named}  {'OK不変' if v == named else '✗変化'}")
