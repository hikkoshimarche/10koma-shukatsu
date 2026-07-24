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


_FIN_METRICS = [("売上高", "売上高|売上収益|営業収益|経常収益"), ("営業利益", "営業利益|事業利益"),
                ("当期純利益", "親会社株主に帰属する当期純利益|親会社の所有者に帰属する\\s*当期利益|当期純利益"),
                ("純資産", "純資産(?:額)?|資本合計"), ("総資産", "総資産(?:額)?|資産合計")]


def _fy_label(period_end):
    m = re.match(r"(\d{4})-(\d{2})", period_end or "")
    return f"{m.group(1)}年{int(m.group(2))}月期" if m else "最新期"


def _edinet_financial_corpus(slug, name):
    """EDINET有報『主要な経営指標等の推移』から最新年度の財務値を抽出し『2026年3月期の売上高は…』と明示。
    ①Lv4財務問を最新期(2026年3月期)に固定するため、複数年系列でなく最新列を取り出して素材化。"""
    if not os.environ.get("EDINET_API_KEY"):
        return {}
    try:
        idx = ES2.build_index()
        e = ES2.match(slug, idx)
        if not e:
            return {}
        text = ES2.fetch_text(e["docid"])
        i = text.find("主要な経営指標")
        seg = text[i:i + 2600] if i >= 0 else ""
        if not seg or not re.search(r"売上|営業利益|経常|純利益", seg):
            return {}
        fy = _fy_label(e.get("periodEnd"))
        unit = 1000 if re.search(r"主要な経営指標[^百]{0,60}千円", seg) else 1_000_000  # 表の単位(百万円が既定)
        facts = []
        for label, pat in _FIN_METRICS:
            m = re.search(f"(?:{pat})[^\\d]{{0,12}}((?:[△▲-]?[\\d,]+\\s*){{2,7}})", seg)
            if not m:
                continue
            nums = [x for x in re.findall(r"[△▲-]?[\d,]+", m.group(1)) if len(re.sub(r"\D", "", x)) >= 2]
            if not nums:
                continue
            latest = nums[-1]                              # 最新年度=系列の最後
            v = int(re.sub(r"\D", "", latest))
            sign = "-" if re.match(r"[△▲-]", latest) else ""
            yen = v * (unit)
            oku = f"{sign}{yen/100_000_000:,.0f}億円"
            facts.append(f"{fy}の{name}の{label}は{oku}。")
        if not facts:
            return {}
        url = f"https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{e['docid']}.pdf"
        return {url + "#最新期財務": f"{name} {fy} 有報(最新年度・一次): " + " ".join(facts)}
    except Exception:
        return {}


def _corpus_from_rendered(slug):
    f = os.path.join(OUT, slug, "rendered_corpus.json")
    if not os.path.exists(f):
        return {}
    rc = json.load(open(f))
    return {u: (v.get("text", "") if isinstance(v, dict) else str(v)) for u, v in rc.items() if (v.get("text") if isinstance(v, dict) else v)}


_TRIVIA = re.compile(r"ブログ|SNS|Twitter|X\(旧|Instagram|Facebook|ロゴ(の|は|マーク|カラー|色)|"
                     r"何色|色は|キャラクター(の名前|は誰)|マスコット|ゆるキャラ|"
                     r"社章|シンボルマーク|コーポレートカラー|創業者の(出身|趣味|好物)|"
                     r"本社ビルの(高さ|階数)|電話番号|郵便番号|住所は|Cookie|プライバシー")


def _is_trivia(x):
    """Lv2の些末事実(就活で価値の低いトリビア)を除外。事業/理念/社風/人物像/製品の理解は残す。"""
    qt = x.get("q_text", "")
    if _TRIVIA.search(qt):
        return True
    ci = x.get("correct", 0); opts = x.get("options", [])
    ans = str(opts[ci]) if ci < len(opts) else ""
    return bool(re.search(r"^(赤|青|緑|黄|白|黒|金|銀|橙|紫)色?$", ans.strip()))   # 色だけの答え


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
    # ② Lv1(王道=主力製品/何する会社)を4問以上確保: 不足なら追試(最大2回)
    g1 = D.gen_lv(slug, name, 1, 10, exclude=used, sem_used=sused, pool=pool)
    existing_lv1 = sum(1 for x in quiz2 if x.get("difficulty") == 1)
    for _ in range(2):
        if existing_lv1 + len(g1) >= 4:
            break
        for x in g1:
            used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
        more = D.gen_lv(slug, name, 1, 6, exclude=used, sem_used=sused, pool=pool)
        if not more:
            break
        g1 += more
    for x in g1:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    # ③ Lv2 トリビアガード: 些末事実(ブログ名/ロゴ色/細かい年号等)を除外
    g2 = [x for x in D.gen_lv(slug, name, 2, 12, exclude=used, sem_used=sused, pool=pool) if not _is_trivia(x)]
    for x in g2:
        used |= set(QL._fact_keys(x)); sused.add(D._sem_sig(x))
    # ② Lv3 文章択(「正しい説明はどれ」)を確保
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
    # 検分用md(sha8)
    import hashlib
    L = ["# 新規社パイロット 再生成（差し戻し3点反映）検分用", "",
         "①Lv4財務問=2026年3月期に固定(EDINET有報の最新年度値を明示) ②Lv1王道≥4＋Lv3文章択を確保 ③Lv2トリビアガード。", ""]
    for r in out:
        if r.get("status") != "ok":
            L.append(f"## {r['slug']}: {r['status']}"); continue
        dq = json.load(open(os.path.join(OUT, r["slug"], "quiz_difficulty_full.json")))
        allq = dq["existing"] + dq.get("gen_lv1", []) + dq.get("gen_lv2", []) + dq.get("gen_lv3", [])
        L.append(f"## {r['slug']} — DS{r['datasheet_items']} / クイズ{r['quiz_total']} {r['lv']} / ES{r['es_materials']}")
        for lv, lab in ((4, "Lv4財務(2026)"), (1, "Lv1王道"), (3, "Lv3文章択"), (2, "Lv2")):
            cs = [x for x in allq if x.get("difficulty") == lv]
            if cs:
                x = cs[0]; ci = x.get("correct", 0); op = x.get("options", [])
                L.append(f"- **{lab}**({len(cs)}問): {x['q_text'][:46]} → 「{op[ci] if ci < len(op) else '?'}」")
        L.append("")
    body = "\n".join(L); sha8 = hashlib.sha256(body.encode()).hexdigest()[:8]
    hd = os.path.expanduser("~/Desktop/kindle_受け渡し")
    os.makedirs(hd, exist_ok=True)
    fn = f"新規社パイロット再生成_検分用__{sha8}.md"
    open(os.path.join(hd, fn), "w", encoding="utf-8").write(body)
    print(f"\nmd: {fn}")


if __name__ == "__main__":
    main()
