#!/usr/bin/env python3
"""新規社(クイズ未対応)の一気通貫生成: rendered_corpus → datasheet → 難易度付きクイズ → ESキット。
rendered_corpus を corpus として供給(acquire_corpus_thickの新規crawlを回避)。全lintゲート適用。
本番D1反映はしない(パイロット承認後に別途)。$ガード=QUIZ_MAX_USD。resumable(成果物存在でskip)。LINEなし。
  python tools/gen_new_company.py <slug...>
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import quiz_difficulty as D
import quiz_lint as QL
import gen_es_kit as ES
import edinet_salary_sweep as ES2   # EDINET index/PDF基盤を流用(財務corpus用)

OUT = q.OUT


def _edinet_financial_corpus(slug, name):
    """EDINET有報の『主要な経営指標等の推移』(売上/利益/資産の複数年系列)を財務corpusとして返す。Lv4財務問の素材。"""
    if not os.environ.get("EDINET_API_KEY"):
        return {}
    try:
        idx = ES2.build_index()
        e = ES2.match(slug, idx)
        if not e:
            return {}
        text = ES2.fetch_text(e["docid"])         # 従業員状況まで=主要経営指標(1-2頁)を含む
        # 主要な経営指標等の推移(先頭付近) + 財務語を含む区間を抽出
        i = text.find("主要な経営指標")
        seg = text[i:i + 2500] if i >= 0 else ""
        if not seg or not re.search(r"売上|営業利益|経常|純利益", seg):
            return {}
        url = f"https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{e['docid']}.pdf"
        return {url + "#経営指標": f"{name} {e.get('periodEnd','')} 有報 主要な経営指標等の推移: " + re.sub(r"\s+", " ", seg)}
    except Exception:
        return {}


def _corpus_from_rendered(slug):
    f = os.path.join(OUT, slug, "rendered_corpus.json")
    if not os.path.exists(f):
        return {}
    rc = json.load(open(f))
    return {u: (v.get("text", "") if isinstance(v, dict) else str(v)) for u, v in rc.items() if (v.get("text") if isinstance(v, dict) else v)}


def _name(slug):
    nm = json.load(open("/tmp/uncovered_names.json")).get(slug) if os.path.exists("/tmp/uncovered_names.json") else None
    return nm or slug


def gen_one(slug):
    name = _name(slug)
    res = {"slug": slug, "name": name}
    corpus = _corpus_from_rendered(slug)
    if len(corpus) < 4:
        res["status"] = "thin_corpus"; return res
    fincorp = _edinet_financial_corpus(slug, name)   # EDINET有報の主要経営指標=Lv4財務問素材
    corpus.update(fincorp)
    res["fin_pages"] = len(fincorp)
    # 保存corpus(quiz_corpus_locked_v3.json)
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    json.dump(corpus, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    # (1) クイズ生成(二層ゲート・converge)
    outp = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
    if os.path.exists(outp):
        quiz = json.load(open(outp))
    else:
        final, dropped, rate = q.converge_locked(slug, name, corpus, target=30)
        if len(final) < q.SHIP_MIN:
            res["status"] = "thin_quiz"; res["n"] = len(final); return res
        quiz = final
        json.dump(quiz, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # (2) datasheet生成
    dp = os.path.join(OUT, slug, "datasheet.json")
    if not os.path.exists(dp):
        ds, _cov = q.build_datasheet(slug, name, corpus, quiz)
        json.dump(ds, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ds = json.load(open(dp))
    # (3) 難易度(初めからdifficulty付き): 既存quizを分類 + 不足Lv1/2/3を生成
    name_pool = [o for x in quiz for o in x.get("options", []) if D._is_person(o)]
    for x, lv in zip(quiz, D.classify(slug, quiz)):
        x["difficulty"] = lv
    quiz2, dropped, inactive = D.clean_existing(quiz, corpus, name_pool=name_pool)
    pool = D._source_pool(slug)
    used, sused = set(), set()
    for x in quiz2:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    g1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
    for x in g1:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    g2 = D.gen_lv(slug, name, 2, 10, exclude=used, sem_used=sused, pool=pool)
    for x in g2:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    g3 = D.gen_lv3(slug, name, 3, exclude=used, sem_used=sused, pool=pool)
    allq = quiz2 + g1 + g2 + g3
    json.dump({"existing": quiz2, "gen_lv1": g1, "gen_lv2": g2, "gen_lv3": g3},
              open(os.path.join(OUT, slug, "quiz_difficulty_full.json"), "w", encoding="utf-8"), ensure_ascii=False)
    from collections import Counter
    dist = Counter(x.get("difficulty") for x in allq)
    # (4) ESキット(材料≥5ゲート・意味検証)
    kit, msg, verified = ES.build_kit(slug, name, ds, corpus)
    es_n = len(kit["motivation_sheet"]["materials"]) if kit else 0
    if kit:
        json.dump(kit, open(os.path.join(OUT, slug, "es_kit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # サマリ
    dsec = ds.get("sections", {})
    res.update({"status": "ok", "quiz_total": len(allq),
                "lv": {f"Lv{k}": v for k, v in sorted(dist.items()) if k},
                "datasheet_items": sum(len(v or []) for v in dsec.values()),
                "datasheet_sections": {k: len(v or []) for k, v in dsec.items()},
                "es_materials": es_n, "es_status": ("ship" if kit else msg),
                "cost": round(q._cost["usd"], 2)})
    return res


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")]
    q.line(f"🆕 新規社 一気通貫生成: {len(slugs)}社 / ${q.MAX_USD}ガード")
    out = []
    for s in slugs:
        try:
            r = gen_one(s)
        except Exception as e:
            r = {"slug": s, "status": "error", "err": f"{type(e).__name__}:{str(e)[:80]}"}
        out.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
        if not q.cost_ok():
            print("COST_GUARD到達・停止", flush=True); break
    json.dump(out, open(os.path.join(OUT, "_new_company_pilot.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== サマリ ===")
    for r in out:
        if r.get("status") == "ok":
            print(f"  {r['slug']:16} DS項目{r['datasheet_items']} / クイズ{r['quiz_total']}({r['lv']}) / ES材料{r['es_materials']}({r['es_status']})")
        else:
            print(f"  {r['slug']:16} {r['status']} {r.get('err','')}")


if __name__ == "__main__":
    main()
