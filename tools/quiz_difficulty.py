#!/usr/bin/env python3
"""クイズ難易度4段階(Lv1入門/Lv2基礎/Lv3応用/Lv4実践)の分類・lint・Lv1/2生成。
分類=ルール(強シグナル)＋OpenAI(nuance)。Lv1/2生成=既存datasheet/quiz-corpus範囲のみ(捏造禁止・出典必須)。
本番D1は触らない。--classify <slug...> / --gen <slug...> / --selftest。
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import quiz_lint as QL

OUT = q.OUT
# 決算数値・専門用語の強シグナル(Lv1に混ざったらerror)
_NUM = re.compile(r"[0-9０-９][0-9０-９,\.]*\s*(円|%|％|百万|億|兆|倍|株|名|人|ヶ所|拠点|年3月期|億円|万円)")
_FIN_TERM = re.compile(r"決算|売上高|収益|営業利益|純利益|経常利益|税引前|ROE|EPS|時価総額|自己資本|"
                       r"セグメント利益|キャッシュフロー|配当|株価|有価証券|資本金|総資産|営業CF")
_JARGON = re.compile(r"ROE|EPS|ROIC|IFRS|EBITDA|セグメント|コーポレートガバナンス|サステナビリティ|"
                     r"バリューチェーン|M&A|のれん|持分法|連結子会社")

CLS_SYS = (
 "就活クイズを難易度4段階に分類する。Lv1入門=会社/業界の基本(10コマ漫画や動画を1回見れば解ける・専門用語や決算数値なし)。"
 "Lv2基礎=事業と強み・社風の理解。Lv3応用=働き方・戦略・競合比較。Lv4実践=決算・数字。"
 "各設問を1〜4で判定。財務数値/決算期/専門用語を含む問いは3か4。事業/製品/理念/沿革の基本は1か2。")
CLS_USER = ("各設問の難易度Lvを判定:\n{items}\n\n出力JSON: {{\"levels\":[{{\"i\":<番号>,\"lv\":1|2|3|4}}]}}")


def rule_level(qd):
    """強シグナルによる下限Lv(これ未満にはしない)。財務=4, 数値/専門=3。"""
    txt = (qd.get("q_text", "") + " " + " ".join(qd.get("options", [])))
    cat = qd.get("category", "")
    if cat == "財務数値" or _FIN_TERM.search(txt) or (qd.get("as_of") and "年3月期" in str(qd.get("as_of"))):
        return 4
    if cat == "業界順位":
        return 3
    if _NUM.search(txt) or _JARGON.search(txt):
        return 3
    return 1


def classify(slug, quiz):
    items = "\n".join(f"[{i}] ({x.get('category')}) {x.get('q_text')}" for i, x in enumerate(quiz))
    data = q._parse_json(q.openai_chat([{"role": "system", "content": CLS_SYS},
                        {"role": "user", "content": CLS_USER.format(items=items)}], max_tokens=1200, temperature=0))
    llm = {v["i"]: int(v.get("lv", 2)) for v in (data.get("levels", []) if isinstance(data, dict) else [])
           if isinstance(v.get("i"), int)}
    out = []
    for i, x in enumerate(quiz):
        rl = rule_level(x)
        lv = max(rl, llm.get(i, rl)) if rl >= 3 else min(llm.get(i, 2), 2) if rl == 1 else llm.get(i, 2)
        # 財務(rl=4)は4固定、数値(rl=3)は3以上、基本(rl=1)はLLMだが1-2に収める
        if rl == 4:
            lv = 4
        elif rl == 3:
            lv = max(3, llm.get(i, 3))
        else:
            lv = min(2, max(1, llm.get(i, 2)))
        out.append(lv)
    return out


# ── 難易度lint: Lv1に数値/決算/専門用語が混入したらerror ──
def lint_difficulty(quiz_with_lv):
    errs = []
    for x in quiz_with_lv:
        if x.get("difficulty") != 1:
            continue
        txt = x.get("q_text", "") + " " + " ".join(x.get("options", []))
        if _NUM.search(txt):
            errs.append(("num", x.get("id"), x.get("q_text", "")[:40]))
        elif _FIN_TERM.search(txt):
            errs.append(("fin", x.get("id"), x.get("q_text", "")[:40]))
        elif _JARGON.search(txt):
            errs.append(("jargon", x.get("id"), x.get("q_text", "")[:40]))
    return errs


GEN_SYS = (
 "就活初心者向けの『入門・基礎クイズ』を、提供された企業の一次情報(datasheet)の範囲だけで作る。"
 "絶対規則: (1)datasheetに実在する内容のみ(捏造・新規リサーチ禁止)。(2)★決算数値・金額・年3月期・専門用語"
 "(ROE/EPS/セグメント/IFRS等)は使わない。(3)4択・正解1つ。★選択肢は4つとも『同じ形式の短い名詞句』で揃える"
 "(例: 事業なら『ゲーム』『自動車』『銀行』『医薬品』のような名詞。『〜する』等の文や会社名・人名は入れない)。"
 "誤答は正解と明らかに区別できる他業界/他分野の名詞。(4)各問にsource_url(根拠factの出典)。"
 "Lv1=会社が何をする会社か/主力事業・製品/業界の基本(10コマ漫画を1回見れば解ける)。Lv2=事業の強み・社風・求める人物像の理解。")
GEN_USER = ("企業: {name} / 難易度: Lv{lv}\n以下は datasheet の事実(出典付)。この範囲だけで Lv{lv} を{n}問。\n\n{facts}\n\n"
            "出力JSON: {{\"questions\":[{{\"q_text\":\"..\",\"options\":[\"正解\",\"誤1\",\"誤2\",\"誤3\"],\"correct\":0,"
            "\"explanation\":\"..\",\"source_url\":\"<上記出典>\",\"category\":\"会社概要|事業セグメント|製品・サービス|沿革|その他\"}}]}}\n"
            "categoryは必ずこの5つのどれか(社風・理念・人物像は『その他』)。correctは0-3でばらけさせる。"
            "選択肢は『ゲーム』『自動車』のような単一名詞(『〜の製造』『〜する』は避ける)。決算数値/年3月期/専門用語は禁止。")


def _ds_facts(ds):
    out = []
    for k, items in (ds.get("sections", {}) or {}).items():
        if k == "主要財務":
            continue
        for it in (items or []):
            f = (it.get("fact") or "").strip()
            if f and not _NUM.search(f) and not _FIN_TERM.search(f):
                out.append({"fact": f, "source_url": it.get("source_url", "")})
    return out


def _scenario_facts(slug):
    """10コマ台本(scenario_v4)の script/overlay_text を Lv1/2の追加ソースに(会社の基本ナラティブ)。"""
    p = os.path.join(OUT, slug, "scenario_v4.json")
    if not os.path.exists(p):
        return []
    try:
        s = json.load(open(p))
    except Exception:
        return []
    out = []
    for k in s.get("koma", []):
        for fld in ("script", "overlay_text"):
            t = k.get(fld)
            if isinstance(t, str):
                t = re.sub(r"\s+", " ", t).strip()
                if len(t) >= 10 and not _NUM.search(t):
                    out.append({"fact": t[:160], "source_url": f"10コマ台本({slug})"})
    return out


def gen_lv(slug, name, level, n=10):
    dp = os.path.join(OUT, slug, "datasheet.json")
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if not os.path.exists(dp):
        return []
    ds = json.load(open(dp))
    corpus = json.load(open(cp)) if os.path.exists(cp) else {}
    facts = _ds_facts(ds) + _scenario_facts(slug)      # datasheet + 10コマ台本
    if len(facts) < 3:
        return []
    # lint用corpus: fact を出典別に束ねる(Lv1/2はdatasheet/台本範囲で接地=source_required充足)
    for x in facts:
        u = x["source_url"] or "ds://local"
        corpus[u] = (corpus.get(u, "") + " " + x["fact"])
    fl = "\n".join(f"- {x['fact']} <出典:{x['source_url']}>" for x in facts[:20])
    data = q._parse_json(q.openai_chat([{"role": "system", "content": GEN_SYS},
                        {"role": "user", "content": GEN_USER.format(name=name, lv=level, n=n + 4, facts=fl)}],
                        max_tokens=2600, temperature=0.4))
    raw = data.get("questions", []) if isinstance(data, dict) else []
    ok = []
    for i, x in enumerate(raw):
        if not (isinstance(x.get("options"), list) and len(x["options"]) == 4):
            continue
        x["id"] = f"{slug}_lv{level}_{i+1:02d}"
        x["difficulty"] = level
        x["as_of"] = x.get("as_of") or ""
        x["explanation"] = x.get("explanation") or ""
        x["source_url"] = x.get("source_url") or ""
        rep = QL.run_quiz_lints([x], corpus)            # quiz-lint v3.3 全通過必須
        if rep["errors"] > 0:
            continue
        if lint_difficulty([x]):                        # Lv1/2に数値/決算/専門→drop
            continue
        ok.append(x)
    return ok[:n]


def selftest():
    good = {"difficulty": 1, "id": "t1", "q_text": "任天堂の主力事業は何ですか", "options": ["ゲーム", "鉄道", "銀行", "石油"]}
    bad = {"difficulty": 1, "id": "t2", "q_text": "2026年3月期の売上高は？", "options": ["1兆円", "2兆円", "3兆円", "4兆円"]}
    e = lint_difficulty([good, bad])
    ok = len(e) == 1 and e[0][1] == "t2"
    print(f"[selftest] Lv1に決算混入をerror検出={ok} ({e})")
    print("=== SELFTEST:", "PASS ===" if ok else "FAIL ===")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")]
    dist = {}
    for slug in slugs:
        f = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        if not os.path.exists(f):
            print(f"SKIP {slug}"); continue
        quiz = json.load(open(f))
        levels = classify(slug, quiz)
        from collections import Counter
        c = Counter(levels)
        dist[slug] = dict(c)
        # 分類結果を保存
        for x, lv in zip(quiz, levels):
            x["difficulty"] = lv
        json.dump(quiz, open(os.path.join(OUT, slug, "quiz_classified_v1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{slug}: Lv1={c[1]} Lv2={c[2]} Lv3={c[3]} Lv4={c[4]} (計{len(quiz)})")
    print("\n=== 分布 ===", json.dumps(dist, ensure_ascii=False))
