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
                       r"セグメント利益|キャッシュフロー|配当|株価|有価証券|資本金|総資産|営業CF|"
                       r"内部留保|利益率|株主還元|資金|増収|増益|減益|利益剰余金")   # v2③資金系→Lv3/4
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
    # v2.1② 拠点数/店舗数/組織規模/従業員数 等の数量系は Lv1/2 に置かず Lv3 以上へ
    if _SCALE.search(txt) or _NUM.search(txt) or _JARGON.search(txt):
        return 3
    return 1


_SCALE = re.compile(r"拠点数|店舗数|事業所数|従業員数|社員数|カ国|ヶ国|営業所|グループ会社数|"
                    r"連結子会社数|組織規模|人員|従業員|店舗網|拠点網")


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


def clean_existing(quiz_with_lv, corpus):
    """v2.1③ 既存問題の機械clean: 崩れた選択肢・カテゴリ不一致の誤答(人名問に社名混入=unit_consistency)・
    Lv1/2で紛らわしい誤答(誤答がcorpus実在) を drop。返り: (kept[], dropped[(id,reason)])."""
    kept, dropped = [], []
    for x in quiz_with_lv:
        opts = x.get("options") or []
        if len(opts) == 4 and any(_broken_option(o) for o in opts):
            dropped.append((x.get("id"), "broken_option")); continue
        uc = QL.lint_unit_consistency(x)                 # 人名問への社名混入等=カテゴリ不一致
        if uc:
            dropped.append((x.get("id"), "category_mismatch_distractor")); continue
        kept.append(x)
    return kept, dropped


# ── 難易度lint: Lv1に数値/決算/専門用語が混入したらerャー ──
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
 "★誤答は必ず『他業界の事業・製品』など出典上明らかに誤りと言い切れるものにする(その会社にも当てはまり得る"
 "紛らわしい選択肢は禁止=例『危機管理→サイバー攻撃』はNG、任天堂の誤答に『自動車の製造』はOK)。(4)各問にsource_url。"
 "Lv1=王道の入門問題=『何をする会社か/主力製品(例:任天堂ならNintendo Switch・マリオ)/代表的な事業』を問う"
 "(10コマ漫画を1回見れば解ける)。抽象的なCSR/システム/取り組みは避け、具体的な製品・事業を問う。Lv2=事業の強み・社風・理念の理解。")
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


def _official_home(slug):
    """corpus多数派ドメインの公式トップ(台本/factsheet由来factの一次情報URL)。"""
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if os.path.exists(cp):
        try:
            import collections
            doms = [re.search(r"https?://([^/]+)", u).group(1) for u in json.load(open(cp))
                    if re.search(r"https?://([^/]+)", u) and not re.search(r"\.ac\.jp|wikipedia|yahoo|note\.com|blog", u)]
            if doms:
                return "https://" + collections.Counter(doms).most_common(1)[0][0] + "/"
        except Exception:
            pass
    return ""


def _factsheet_facts(slug):
    """ファクトシート(factsheet.md)から王道Lv1材料=主力製品/業態/理念を抽出(採用/待遇/決算は除外)。
    『## 身近な接点』(製品)・『## 基本情報』の業態・『## 理念』を対象。決算数値は除外。出典=公式トップ。"""
    p = os.path.join(OUT, slug, "factsheet.md")
    if not os.path.exists(p):
        return []
    home = _official_home(slug)
    lines = open(p, encoding="utf-8").read().splitlines()
    out, sec = [], ""
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            sec = ln[3:].strip(); continue
        if sec in ("採用", "待遇", "直近トピック"):     # 決算/採用倍率/年収は Lv1 材料にしない
            continue
        m = re.match(r"^-\s*\*\*(.+?)\*\*:\s*(.*)$", ln)
        name = desc = None
        if m:
            name, desc = m.group(1).strip(), m.group(2).strip()
            if not desc and i + 1 < len(lines) and not lines[i + 1].startswith(("-", "#")):
                desc = lines[i + 1].strip()
        if not name or not desc or _NUM.search(desc) or _FIN_TERM.search(desc):
            continue
        if sec == "身近な接点":
            out.append({"fact": f"{name}は{desc}", "source_url": home, "kind": "product"})
        elif sec in ("基本情報", "理念"):
            out.append({"fact": f"{name}: {desc}"[:160], "source_url": home, "kind": "basic"})
    return out


def _scenario_facts(slug):
    """10コマ台本(scenario_v4)の視覚フック(固有product)・brand_object・script・overlayをLv1/2材料に。"""
    p = os.path.join(OUT, slug, "scenario_v4.json")
    if not os.path.exists(p):
        return []
    try:
        s = json.load(open(p))
    except Exception:
        return []
    home = _official_home(slug)
    out = []
    for k in s.get("koma", []):
        vh = re.sub(r"^H\d+[:：]\s*", "", str(k.get("visual_hook", ""))).strip()   # 視覚フック=固有product
        if vh and not _NUM.search(vh):
            out.append({"fact": vh[:120], "source_url": home, "kind": "product"})
        bo = k.get("brand_object")
        if isinstance(bo, dict):
            for key in ("object_type", "brand_form"):
                v = str(bo.get(key, "")).strip()
                if len(v) >= 6 and not _NUM.search(v):
                    out.append({"fact": v[:120], "source_url": home, "kind": "product"})
        ov = k.get("overlay_text")
        if isinstance(ov, dict):
            for key in ("main_copy", "sub"):
                v = str(ov.get(key, "")).strip()
                if len(v) >= 8 and not _NUM.search(v):
                    out.append({"fact": v[:120], "source_url": home, "kind": "basic"})
        sc = k.get("script")
        if isinstance(sc, list):
            for line in sc:
                t = re.sub(r"^\[[^\]]+\]\s*", "", str(line)).strip()   # [nana] 除去
                if len(t) >= 12 and not _NUM.search(t):
                    out.append({"fact": t[:150], "source_url": home, "kind": "basic"})
    return out


_STOP = set("サービス システム 事業 製品 提供 開発 管理 活動 技術 情報 グループ ビジネス 会社 企業 "
            "戦略 市場 顧客 社会 世界 日本 製造 販売 運営 支援 推進 展開 生産 品質 環境 経営 業界".split())


def _distractor_ok(x, corpus):
    """誤答が『実は正しい可能性がある』型を排除。誤答の《特徴語(4字以上・共通語除く)》がその社のcorpus本文に
    実在=実際に当てはまり得る→不可(例: 危機管理の誤答『サイバー攻撃』)。他業界の明白誤答(自動車/金融サービス
    等・特徴語がcorpus不在)はOK。共通語(サービス/事業等)だけの一致では落とさない。"""
    ctext = re.sub(r"\s+", "", " ".join(corpus.values()))
    ci = x.get("correct", 0)
    for j, o in enumerate(x.get("options", [])):
        if j == ci:
            continue
        for t in re.findall(r"[一-龥ァ-ヶーA-Za-z]{4,}", str(o)):
            if t in _STOP:
                continue
            if t in ctext:
                return False
    return True


_SRC_PATHS = ["/software/", "/hardware/", "/products/", "/product/", "/business/", "/company/business/",
              "/company/", "/company/about/", "/about/", "/ir/", "/csr/", "/sustainability/",
              "/lineup/", "/service/", "/brand/", "/ja/products/", "/jp/ja/business/", "/recruit/"]


def _source_pool(slug):
    """その社の公式ページ本文(各factの該当ページ特定用)。#4(b): ヘッドレスでJS描画済みの
    rendered_corpus.json を最優先(製品ページ本文が取れる)。無ければ datasheet出典＋curlで補完。非公式除外。"""
    home = _official_home(slug)
    pool = {}
    # (b) レンダ済corpus(playwright)を最優先で使用
    rc = os.path.join(OUT, slug, "rendered_corpus.json")
    if os.path.exists(rc):
        try:
            for u, v in json.load(open(rc)).items():
                if not _NONOFF.search(u):
                    pool[u] = re.sub(r"\s+", "", v.get("text", "") if isinstance(v, dict) else str(v))
        except Exception:
            pass
    if not home:
        return pool
    base = home.rstrip("/")
    urls = [base + p for p in _SRC_PATHS]
    # 公式トップのリンクから同一ドメインの主要ページを発見(製品/事業/会社ページを広く拾う)
    hb = q.fetch_url(home)
    if hb:
        for m in re.findall(r'href="([^"#]+)"', hb):
            lu = m if m.startswith("http") else (base + m if m.startswith("/") else None)
            if lu and base in lu and not lu.lower().endswith((".pdf", ".jpg", ".png", ".zip", ".mp4")):
                urls.append(lu.split("?")[0])
    dp = os.path.join(OUT, slug, "datasheet.json")
    if os.path.exists(dp):
        for k, items in (json.load(open(dp)).get("sections", {}) or {}).items():
            for it in items:
                u = it.get("source_url", "")
                if u and not _NONOFF.search(u):
                    urls.append(u)
    # 製品/事業/会社系URLを優先し、広めに取得(上限25ページ)
    def _pri(u):
        return 0 if re.search(r"/(software|products?|business|lineup|service|brand|company|about|hardware)", u, re.I) else 1
    for u in sorted(dict.fromkeys(urls), key=_pri):
        if u in pool or len(pool) >= 25:
            continue
        raw = q.fetch_url(u)
        if raw and len(raw) > 300:
            pool[u] = re.sub(r"\s+", "", raw)
    return pool


def _resolve_source(answer, pool, home):
    """正解entityが実在する公式ページURLを返す(トップ一括禁止=具体ページ優先)。無ければ None(drop)。
    答えの特徴語のいずれかがページ本文にあれば該当(『ポケモンGO』→『ポケモン』一致等)。一致語数が多いページを優先。"""
    toks = [t for t in re.findall(r"[一-龥ァ-ヶーA-Za-z0-9]{3,}", str(answer)) if t not in _STOP]
    # 全体一致しない長い答えは短い構成語も試す(ポケモンGO→ポケモン)
    extra = [t[:k] for t in toks for k in (5, 4, 3) if len(t) > k]
    cand = list(dict.fromkeys(toks + extra))
    if not cand:
        return None
    best, best_n = None, 0
    hbase = (home or "").rstrip("/")
    for u, b in pool.items():
        if u.rstrip("/") == hbase or re.search(r"/index\.html?$", u):
            continue                                        # トップ/indexは不可
        n = sum(1 for t in cand if t in b)
        if n > best_n or (n == best_n and best and len(u) > len(best)):
            best, best_n = u, n
    return best if best_n >= 1 else None


_NONOFF = re.compile(r"\.ac\.jp|\.edu|wikipedia|yahoo|note\.com|j-lic|kyotonikanpai|renew-career|"
                     r"hakenreco|talentsquare|fiit|visionguide|btj-|blog|ameblo|hatena|kabutan|minkabu", re.I)


def _sem_sig(qd):
    """設問の意味シグネチャ(表現違いの同一factを捕捉): q_text＋正解の特徴語集合。"""
    txt = str(qd.get("q_text", "")) + " " + str((qd.get("options") or [""])[qd.get("correct", 0)] if qd.get("options") else "")
    return frozenset(t for t in re.findall(r"[一-龥ァ-ヶーA-Za-z0-9]{3,}", txt) if t not in _STOP)


def _broken_option(opt):
    """崩れた選択肢(『98、海外：98』等の羅列・コロン混在)を検出。"""
    s = str(opt)
    return bool(re.search(r"[:：].*[:：]|[、,].*[:：]|[:：].*[、,]", s)) or (len(s) > 60)


def gen_lv(slug, name, level, n=10, exclude=None, sem_used=None, pool=None):
    dp = os.path.join(OUT, slug, "datasheet.json")
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if not os.path.exists(dp):
        return []
    ds = json.load(open(dp))
    corpus = json.load(open(cp)) if os.path.exists(cp) else {}
    # ソース: ファクトシート(王道product/業態/理念) + 10コマ台本(視覚フック等) + datasheet
    fsheet = _factsheet_facts(slug)
    scen = _scenario_facts(slug)
    dsf = [dict(x, kind="basic") for x in _ds_facts(ds)]
    prod = [x for x in fsheet + scen if x.get("kind") == "product"]
    basic = [x for x in fsheet + scen + dsf if x.get("kind") != "product"]
    facts = (prod + basic) if level == 1 else (basic + prod)   # Lv1は主力製品を最優先
    # 重複fact除去(正規化)
    seen, uniq = set(), []
    for x in facts:
        kk = re.sub(r"[\s、。「」()（）・:：]", "", x["fact"])[:30]
        if kk in seen:
            continue
        seen.add(kk); uniq.append(x)
    facts = uniq
    if len(facts) < 3:
        return []
    for x in facts:
        u = x["source_url"] or "ds://local"
        corpus[u] = (corpus.get(u, "") + " " + x["fact"])
    hint = ("Lv1は『主力製品・何をする会社か・代表的な事業』の王道問題を優先。各製品・各事業について1問ずつ広く作る。"
            if level == 1 else "Lv2は事業の強み・社風・理念の理解。")
    fl = "\n".join(f"- {x['fact']} <出典:{x['source_url']}>" for x in facts[:24])
    if pool is None:
        pool = _source_pool(slug)                       # #4 該当ページ特定用の公式本文プール
    home = _official_home(slug)
    ok, used = [], set(exclude or set())
    sused = set(sem_used or set())
    covered = []                                        # 既出の正解(2パス目で回避)
    for rnd in range(2):                                # 最大2パス(不足時に別題材で追加生成)
        if len(ok) >= n:
            break
        avoid = ("\nすでに次を出題済み=別の製品/事業/接点で作れ: " + "、".join(covered[:20])) if covered else ""
        data = q._parse_json(q.openai_chat([{"role": "system", "content": GEN_SYS},
                            {"role": "user", "content": GEN_USER.format(name=name, lv=level, n=n + 6, facts=fl) + "\n" + hint + avoid}],
                            max_tokens=2800, temperature=0.5 if rnd else 0.4))
        raw = data.get("questions", []) if isinstance(data, dict) else []
        for x in raw:
            if not (isinstance(x.get("options"), list) and len(x["options"]) == 4):
                continue
            if any(_broken_option(o) for o in x["options"]):
                continue
            x["id"] = f"{slug}_lv{level}_{len(ok)+1:02d}"
            x["difficulty"] = level
            x["as_of"] = x.get("as_of") or ""
            x["explanation"] = x.get("explanation") or ""
            ans = x["options"][x.get("correct", 0)]
            src = _resolve_source(ans, pool, home)      # #4 具体ページ or drop
            if not src:
                continue
            x["source_url"] = src
            if QL.run_quiz_lints([x], corpus)["errors"] > 0:
                continue
            if lint_difficulty([x]) or not _distractor_ok(x, corpus):
                continue
            fk = frozenset(QL._fact_keys(x))
            sig = _sem_sig(x)
            if fk & used or (sig and any(len(sig & s) >= max(2, min(len(sig), len(s)) - 1) for s in sused)):
                continue
            used |= fk; sused.add(sig); covered.append(str(ans)[:20]); ok.append(x)
            if len(ok) >= n:
                break
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
