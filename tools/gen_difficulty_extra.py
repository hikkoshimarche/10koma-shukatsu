#!/usr/bin/env python3
"""難易度 追加生成バッチ(インターンFB第2弾): Lv2理念/パーパス + Lv4大型投資/買収/提携/新事業。
本体fanout(quiz_difficulty_full.json)は止めず後追い。既存問＋本体新規とdedup(言い換え重複排除)。
案件が本文に無い社はスキップ(実数記録)。resumable・$ガード・LINEなし。出力: output/<slug>/quiz_difficulty_extra.json
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
NAME = {}


def process(slug, name, name_pool):
    try:
        full = os.path.join(OUT, slug, "quiz_difficulty_full.json")
        used, sused = set(), set()
        if os.path.exists(full):                         # 本体fanout結果とdedup
            d = json.load(open(full))
            for key in ("existing", "gen_lv1", "gen_lv2", "gen_lv3"):
                for x in d.get(key, []):
                    used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        pool = D._source_pool(slug)
        p2 = D.gen_lv2_philosophy(slug, name, 3, exclude=used, sem_used=sused, pool=pool)
        for x in p2:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        d4 = D.gen_lv4_deals(slug, name, 2, exclude=used, sem_used=sused, pool=pool)
        json.dump({"add_lv2_philosophy": p2, "add_lv4_deals": d4},
                  open(os.path.join(OUT, slug, "quiz_difficulty_extra.json"), "w", encoding="utf-8"), ensure_ascii=False)
        return {"slug": slug, "status": "ok", "phil": len(p2), "deals": len(d4),
                "deals_skip": 1 if len(d4) == 0 else 0}
    except Exception as e:
        return {"slug": slug, "status": "err", "err": str(e)[:80]}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    companies = sorted(os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(OUT, "*/quiz_30q_locked_v3.json")))
    targets = args if args else companies
    stp = os.path.join(OUT, "_difficulty_extra_state.json")
    st = json.load(open(stp)) if os.path.exists(stp) else {"done": [], "cost": 0.0, "cp": 0, "phil": 0, "deals": 0, "skip": 0}
    with q._lock:
        q._cost["usd"] = st.get("cost", 0.0)
    todo = [s for s in targets if s not in set(st["done"])]
    name_pool = []
    for s in companies:
        dp = os.path.join(OUT, s, "datasheet.json")
        if os.path.exists(dp):
            try:
                NAME[s] = json.load(open(dp)).get("name") or s
            except Exception:
                NAME[s] = s
        f = os.path.join(OUT, s, "quiz_30q_locked_v3.json")
        if os.path.exists(f) and not s.startswith("industry__"):
            for x in json.load(open(f)):
                for o in x.get("options", []):
                    if D._is_person(o) and o not in name_pool:
                        name_pool.append(o)
    q.line(f"📊 難易度 追加バッチ(理念+案件) 開始/再開: 対象{len(todo)}(全{len(targets)}・完了{len(st['done'])}) ${q.MAX_USD}ガード")
    batch, stop = [], None

    def cp():
        st["cp"] += 1; st["cost"] = round(q._cost["usd"], 4)
        json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False)
        try:
            q.git("add", "output/_difficulty_extra_state.json", "output/*/quiz_difficulty_extra.json", cwd=q.PIPE)
            q.git("-c", "user.email=quiz@local", "-c", "user.name=quiz-diff", "commit", "-q",
                  "-m", f"difficulty-extra CP{st['cp']}: 理念{st['phil']} 案件{st['deals']} skip{st['skip']} ${st['cost']}", cwd=q.PIPE)
            q.git("push", "-q", "origin", "HEAD", cwd=q.PIPE)
        except Exception as e:
            print("[commit ERR]", e)
        q.line(f"[追加CP{st['cp']}] 完了{len(st['done'])}/{len(targets)} 理念{st['phil']} 案件{st['deals']} skip{st['skip']} ${st['cost']:.2f}")

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
                    st["phil"] += r.get("phil", 0); st["deals"] += r.get("deals", 0); st["skip"] += r.get("deals_skip", 0)
                batch.append(r)
                print(f"  {r['status']:7} {r['slug']:22} 理念+{r.get('phil')} 案件+{r.get('deals')} ${q._cost['usd']:.2f}", flush=True)
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
    q.line(f"[追加バッチ {stop or 'done'}] 理念{st['phil']} 案件{st['deals']} 案件skip{st['skip']} ${q._cost['usd']:.2f}")
    print(f"=== done {len(st['done'])} 理念{st['phil']} 案件{st['deals']} skip{st['skip']} ${q._cost['usd']:.2f} ===")


if __name__ == "__main__":
    main()
