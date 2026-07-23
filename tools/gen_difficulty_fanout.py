#!/usr/bin/env python3
"""クイズ難易度 fanout: 全社(quiz保有)＋16業界。既存問を難易度分類＋不足Lv1/Lv2/Lv3を新規生成。
resumable(checkpoint式)・実費ガード$60・LINE送信なし(line()はテキストのみ)。本番D1は別ステップ。
出力: output/<slug>/quiz_difficulty_full.json  state: output/_difficulty_state.json
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_difficulty as D
import quiz_lint as QL
import quiz_fanout as q
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

OUT = q.OUT
CP_EVERY = 20
PARALLEL = 3
NAME = {}   # slug->display name(あれば)


def _name_pool_all(slugs):
    np = []
    for slug in slugs:
        f = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        if not os.path.exists(f):
            continue
        for x in json.load(open(f)):
            for o in x.get("options", []):
                if D._is_person(o) and o not in np:
                    np.append(o)
    return np


def process(slug, name, name_pool):
    qf = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
    if not os.path.exists(qf):
        return {"slug": slug, "status": "no_quiz"}
    try:
        quiz = json.load(open(qf))
        corpus = json.load(open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json"))) \
            if os.path.exists(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")) else {}
        for x, lv in zip(quiz, D.classify(slug, quiz)):
            x["difficulty"] = lv
        quiz, dropped, inactive = D.clean_existing(quiz, corpus, name_pool=name_pool)
        pool = D._source_pool(slug)
        used, sused = set(), set()
        for x in quiz:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        g1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
        for x in g1:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        g2 = D.gen_lv(slug, name, 2, 10, exclude=used, sem_used=sused, pool=pool)
        for x in g2:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        g3 = D.gen_lv3(slug, name, 3, exclude=used, sem_used=sused, pool=pool)
        out = {"existing": quiz, "gen_lv1": g1, "gen_lv2": g2, "gen_lv3": g3,
               "dropped_existing": dropped, "inactive_existing": inactive}
        json.dump(out, open(os.path.join(OUT, slug, "quiz_difficulty_full.json"), "w", encoding="utf-8"),
                  ensure_ascii=False)
        from collections import Counter
        dist = Counter(x["difficulty"] for x in quiz if x.get("active", True))
        return {"slug": slug, "status": "ok", "lv1n": len(g1), "lv2n": len(g2), "lv3n": len(g3),
                "existing_lv": dict(dist), "inactive": len(inactive)}
    except Exception as e:
        return {"slug": slug, "status": "err", "err": str(e)[:80]}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    companies = sorted(os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(OUT, "*/quiz_30q_locked_v3.json")))
    industries = [s for s in companies if s.startswith("industry__")]
    comps = [s for s in companies if not s.startswith("industry__")]
    targets = args if args else (comps + industries)
    stp = os.path.join(OUT, "_difficulty_state.json")
    st = json.load(open(stp)) if os.path.exists(stp) else {"done": [], "cost": 0.0, "cp": 0, "newq": 0}
    with q._lock:
        q._cost["usd"] = st.get("cost", 0.0)
    todo = [s for s in targets if s not in set(st["done"])]
    for s in targets:                                    # 生成プロンプト用の会社名(datasheetから)
        dp = os.path.join(OUT, s, "datasheet.json")
        if os.path.exists(dp):
            try:
                NAME[s] = json.load(open(dp)).get("name") or s
            except Exception:
                NAME[s] = s
    name_pool = _name_pool_all(comps)
    q.line(f"📊 難易度fanout 開始/再開: 対象{len(todo)}(全{len(targets)}・完了{len(st['done'])}) 並列{PARALLEL}・${q.MAX_USD}ガード")
    batch, stop = [], None

    def cp():
        st["cp"] += 1; st["cost"] = round(q._cost["usd"], 4)
        json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False)
        try:
            q.git("add", "output/_difficulty_state.json", "output/*/quiz_difficulty_full.json", cwd=q.PIPE)
            q.git("-c", "user.email=quiz@local", "-c", "user.name=quiz-diff", "commit", "-q",
                  "-m", f"difficulty-fanout CP{st['cp']}: 完了{len(st['done'])} 新規{st['newq']} ${st['cost']}", cwd=q.PIPE)
            q.git("push", "-q", "origin", "HEAD", cwd=q.PIPE)
        except Exception as e:
            print("[commit ERR]", e)
        q.line(f"[難易度CP{st['cp']}] 完了{len(st['done'])}/{len(targets)} 新規{st['newq']} ${st['cost']:.2f}")

    it = iter(todo); inflight = {}
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for _ in range(PARALLEL):
            t = next(it, None)
            if t: inflight[ex.submit(process, t, NAME.get(t, t), name_pool)] = t
        while inflight:
            done, _p = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fu in done:
                inflight.pop(fu, None)
                r = fu.result()
                with q._lock:
                    if r["slug"] not in st["done"]: st["done"].append(r["slug"])
                    st["newq"] += r.get("lv1n", 0) + r.get("lv2n", 0) + r.get("lv3n", 0)
                batch.append(r)
                print(f"  {r['status']:7} {r['slug']:22} Lv1+{r.get('lv1n')} Lv2+{r.get('lv2n')} Lv3+{r.get('lv3n')} 既存{r.get('existing_lv')} ${q._cost['usd']:.2f}", flush=True)
                if not q.cost_ok(): stop = "cost"
                if len(batch) >= CP_EVERY:
                    cp(); batch = []
                if stop is None:
                    nt = next(it, None)
                    if nt: inflight[ex.submit(process, nt, NAME.get(nt, nt), name_pool)] = nt
            if stop: break
    if batch:
        cp()
    json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False)
    q.line(f"[難易度fanout {stop or 'done'}] 完了{len(st['done'])} 新規{st['newq']} ${q._cost['usd']:.2f}")
    print(f"=== done {len(st['done'])} 新規{st['newq']} ${q._cost['usd']:.2f} ===")


if __name__ == "__main__":
    main()
