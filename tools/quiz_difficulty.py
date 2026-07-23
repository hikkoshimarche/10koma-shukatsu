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
        # v2.6-0(2) 経営者・役員の人名問は全社Lv2に統一
        if _PERSON_Q.search(x.get("q_text", "")) or x.get("category") == "人名・役員":
            out.append(2); continue
        # 財務(rl=4)は4固定、数値(rl=3)は3以上、基本(rl=1)はLLMだが1-2に収める
        if rl == 4:
            lv = 4
        elif rl == 3:
            lv = max(3, llm.get(i, 3))
        else:
            lv = min(2, max(1, llm.get(i, 2)))
        out.append(lv)
    return out


_PERSON_Q = re.compile(r"社長|代表取締役|代表者|会長|役員|取締役|CEO|COO|CFO|氏名|(の名前|は誰)")


_FOREIGN_CO = re.compile(r"\b(AS|Inc|Ltd|GmbH|Corp|S\.?A\.?|AG|PLC|LLC|N\.?V\.?)\b|Finnmark|Holding|Group\b")


# 製品・事業・一般語の接尾辞(人名でない=name_pool/差替から除外)
_NOTNAME = re.compile(r"(器|機|械|装置|システム|事業|削減|費|品|業務|サービス|処理|技術|部門|"
                      r"製造|販売|開発|投資|資源|エネルギー|ガス|化学|金属|食品|銀行|保険|証券|"
                      r"商社|会社|工業|産業|センター|ソリューション|ネットワーク|プラットフォーム)$")


def _is_person(o):
    s = str(o).replace(" ", "").replace("　", "").strip()
    # 日本語の経営者名は漢字(＋﨑等異体字)のみの姓名2-6字。ひらがな(助詞『の』等)/カタカナ/英字/数字/
    #  製品・事業接尾辞を含むものは人名でない(測定器・新技術の研究・スマートフォン等を排除)。
    return (2 <= len(s) <= 6) and bool(re.fullmatch(r"[一-龥々〆ヶ㐀-鿿豈-﫿]+", s)) \
        and not QL.COMPANY_SUF.search(s) and not _FOREIGN_CO.search(s) and not _NOTNAME.search(s)


def clean_existing(quiz_with_lv, corpus, name_pool=None):
    """v2.1③+v2.3③④a 既存問の機械clean: (broken選択肢)(人名問の社名混入=日本語人名に差替/不可ならdrop)
    (unit_consistency不一致)(#3 レベル内fact-key重複→inactive)。返り: (kept, dropped, inactive)."""
    kept, dropped, inactive = [], [], []
    seen_by_lv = {}
    name_pool = list(name_pool or [])
    for x in quiz_with_lv:
        opts = x.get("options") or []
        ci = x.get("correct", 0)
        if len(opts) == 4 and any(_broken_option(o) for o in opts):
            dropped.append((x.get("id"), "broken_option")); continue
        # #4a/v2.4① 人名問(多数が人名)の非人名誤答(社名/外国法人/『スマートフォン』等)は
        #   同一カテゴリ=corpus実在の人名にのみ差替。差替不可ならdrop。
        persons = [o for o in opts if _is_person(o)]
        if len(persons) >= 2:
            for k, o in enumerate(opts):
                if k == ci or _is_person(o):
                    continue
                repl = next((nm for nm in name_pool if nm not in opts and nm != opts[ci]), None)
                if repl:
                    opts[k] = repl
                    x["_fixed"] = "person_distractor_replaced"
            if any((k != ci) and not _is_person(opts[k]) for k in range(4)):   # なお非人名が残る→drop
                dropped.append((x.get("id"), "category_mismatch_distractor")); continue
        if QL.lint_unit_consistency(x):
            dropped.append((x.get("id"), "category_mismatch_distractor")); continue
        # #3 レベル内 重複(言い換え含む)→ inactive(削除でなく記録)。fact-key＋意味シグネチャで捕捉
        lv = x.get("difficulty", 2)
        fk = frozenset(QL._fact_keys(x))
        sig = _sem_sig(x)
        st = seen_by_lv.setdefault(lv, {"fk": set(), "sigs": []})
        dup = (fk and fk & st["fk"]) or (sig and any(len(sig & s) >= max(2, min(len(sig), len(s)) - 1) for s in st["sigs"]))
        if dup:
            x["active"] = False
            inactive.append((x.get("id"), f"intra_lv{lv}_dup")); continue
        st["fk"] |= fk; st["sigs"].append(sig)
        x["active"] = True
        kept.append(x)
    return kept, dropped, inactive


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
 "★誤答は『当社が事業として一切やっていない別業界の固有領域』(例: 商社の誤答にゲーム開発/医薬品製造/アニメ制作)"
 "のみにする。★総合商社・多角化企業(コングロマリット)では『やっていない事業』型の誤答は禁止(当社は多くの事業を持つため"
 "紛らわしい)=不動産/エネルギー/食品/金融等の当社が実際に関与し得る分野を誤答に使わない。(4)各問にsource_url。"
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


def _full_corpus_text(slug, pool=None):
    """v2.5 その社の《全資料》本文を連結(全クロールページ＋datasheet＋factsheet＋10コマ台本＋quiz_corpus)。
    誤答が『自社資料のどこかに事業・製品として実在』するかを判定するための土台=『ページに無い≠事実でない』を根治。"""
    parts = []
    if pool is None:
        pool = _source_pool(slug)
    parts.extend(pool.values())                          # 全クロール(rendered+curl)ページ
    dp = os.path.join(OUT, slug, "datasheet.json")
    if os.path.exists(dp):
        for k, items in (json.load(open(dp)).get("sections", {}) or {}).items():
            for it in items:
                parts.append(it.get("fact", ""))
    fp = os.path.join(OUT, slug, "factsheet.md")
    if os.path.exists(fp):
        parts.append(open(fp, encoding="utf-8").read())
    for x in _factsheet_facts(slug) + _scenario_facts(slug):
        parts.append(x.get("fact", ""))
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    if os.path.exists(cp):
        try:
            parts.extend(json.load(open(cp)).values())
        except Exception:
            pass
    return re.sub(r"\s+", "", " ".join(str(p) for p in parts))


def _distractor_ok(x, full_text=""):
    """v2.5 誤答が『自社資料のどこかに事業・製品として実在』したら使用禁止(=当社が実際にやっている→誤答に不適)。
    誤答の特徴語(4字以上・共通語除く)が full_text(全corpus)にあれば不可。明確に別業界の固有領域
    (ゲーム開発/医薬品製造 等・当社資料のどこにも現れない)のみ誤答として許可。カテゴリ整合(人名問)も維持。"""
    ci = x.get("correct", 0)
    opts = x.get("options", [])
    if sum(1 for o in opts if _is_person(o)) >= 2:       # 人名問の誤答は人名のみ
        if any((j != ci) and not _is_person(o) for j, o in enumerate(opts)):
            return False
    ft = full_text if isinstance(full_text, str) else re.sub(r"\s+", "", " ".join(full_text.values()))
    for j, o in enumerate(opts):
        if j == ci:
            continue
        os_ = re.sub(r"\s", "", str(o))
        if len(os_) >= 4 and os_ in ft:                  # 誤答の完全名が自社資料に実在→不可
            return False
        for t in re.findall(r"[一-龥ァ-ヶーA-Za-z]{3,}", str(o)):   # 3字以上の特徴語も判定
            if t in _STOP:
                continue
            if t in ft:
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
    # バグ#2: datasheet出典(PDF含む)は各factの該当ページ=最優先で取り込む(q.fetch_urlはfitzでPDF本文抽出)
    ds_urls = []
    dp = os.path.join(OUT, slug, "datasheet.json")
    if os.path.exists(dp):
        for k, items in (json.load(open(dp)).get("sections", {}) or {}).items():
            for it in items:
                u = it.get("source_url", "")
                if u and not _NONOFF.search(u):
                    ds_urls.append(u)
    for u in dict.fromkeys(ds_urls):                      # datasheet出典を先に(上限に関係なく)
        if u in pool:
            continue
        raw = q.fetch_url(u)
        if raw and len(raw) > 300:
            pool[u] = re.sub(r"\s+", "", raw)
    # 製品/事業/会社系URLを優先し、広めに取得(総上限32ページ)
    def _pri(u):
        return 0 if re.search(r"/(software|products?|business|lineup|service|brand|company|about|hardware)", u, re.I) else 1
    for u in sorted(dict.fromkeys(urls), key=_pri):
        if u in pool or len(pool) >= 32:
            continue
        raw = q.fetch_url(u)
        if raw and len(raw) > 300:
            pool[u] = re.sub(r"\s+", "", raw)
    return pool


def _resolve_source(answer, pool, home, product=True):
    """正解が実在する公式の具体ページURLを返す(トップ一括禁止・無ければNone=drop)。
    product=True(Lv1製品問): 固有名詞トークンが本文にあれば該当(ポケモンGO→ポケモン)。
    product=False(Lv2等): #2 正解の『語句(フレーズ)』が本文に実在(固有名詞は不要)。"""
    hbase = (home or "").rstrip("/")
    pages = [(u, b) for u, b in pool.items() if u.rstrip("/") != hbase and not re.search(r"/index\.html?$", u)]
    if product:
        toks = [t for t in re.findall(r"[一-龥ァ-ヶーA-Za-z0-9]{3,}", str(answer)) if t not in _STOP]
        extra = [t[:k] for t in toks for k in (5, 4, 3) if len(t) > k]
        cand = list(dict.fromkeys(toks + extra))
        if not cand:
            return None
        best, best_n = None, 0
        for u, b in pages:
            n = sum(1 for t in cand if t in b)
            if n > best_n or (n == best_n and best and len(u) > len(best)):
                best, best_n = u, n
        return best if best_n >= 1 else None
    # Lv2: 正解フレーズ(空白除去)が本文に実在。長ければ先頭substringでも可(表記ゆれ吸収)
    ph = re.sub(r"\s", "", str(answer))
    if len(ph) < 4:
        return None
    subs = [ph] + ([ph[:12], ph[:8]] if len(ph) >= 8 else [])
    best = None
    for u, b in pages:
        if any(s in b for s in subs):
            if best is None or len(u) > len(best):
                best = u
    return best


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
            "★消費者向け製品が無い会社(商社・銀行等)は、業態(例『何をする会社か→総合商社』)や"
            "関与する事業分野・投資先(例 天然ガス/金属資源/食品/自動車/コンビニ等)を問う王道問題を作る。"
            "★知名度の高いBtoC企業は『へぇと思う豆知識』(祖業・意外な創業の歴史。沿革ページの範囲・数値/専門用語なし)を1〜2問含める。"
            if level == 1 else "Lv2は事業の強み・社風・理念の理解。経営者・役員の人名問はLv2で作ってよい。")
    fl = "\n".join(f"- {x['fact']} <出典:{x['source_url']}>" for x in facts[:24])
    if pool is None:
        pool = _source_pool(slug)                       # #4 該当ページ特定用の公式本文プール
    home = _official_home(slug)
    full_text = _full_corpus_text(slug, pool)            # v2.5 誤答判定=自社の全資料に実在するか
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
            src = _resolve_source(ans, pool, home, product=(level == 1))   # #2 Lv1=固有名詞/Lv2=フレーズ実在
            if not src:
                continue
            x["source_url"] = src
            if QL.run_quiz_lints([x], corpus)["errors"] > 0:
                continue
            if lint_difficulty([x]) or not _distractor_ok(x, full_text):   # v2.5 誤答が自社全資料に実在→drop
                continue
            if not _explanation_ok(x, full_text):        # 解説も本文照合ゲート通過必須
                continue
            fk = frozenset(QL._fact_keys(x))
            sig = _sem_sig(x)
            if fk & used or (sig and any(len(sig & s) >= max(2, min(len(sig), len(s)) - 1) for s in sused)):
                continue
            used |= fk; sused.add(sig); covered.append(str(ans)[:20]); ok.append(x)
            if len(ok) >= n:
                break
    return ok[:n]


L3_SYS = (
 "就活生向けLv3(応用)の『正しい説明はどれ』型クイズを、提供された企業の一次情報の範囲だけで作る。"
 "4つの選択肢は全て『会社/事業の説明文(1文)』。正解1つは本文で裏取りできる正確な説明、誤答3つは"
 "『当社が実際にやっていない別業界の事業説明』(当社資料に現れない領域)にする。決算数値・専門用語は避ける。"
 "各問に1〜2文の解説(本文で裏取りできる範囲)と source_url を付す。多角化企業の事業説明はこの型で。")
L3_USER = ("企業: {name}\n以下は一次情報の事実(出典付)。この範囲だけで『正しい説明はどれ』型を{n}問。\n\n{facts}\n\n"
           "出力JSON: {{\"questions\":[{{\"q_text\":\"{name}の説明として正しいものはどれですか？\","
           "\"options\":[\"正しい説明(1文)\",\"誤り説明1\",\"誤り説明2\",\"誤り説明3\"],\"correct\":0,"
           "\"explanation\":\"1〜2文の解説\",\"source_url\":\"<上記出典>\",\"category\":\"事業セグメント\"}}]}}\n"
           "誤答は当社がやっていない別業界の事業説明のみ。決算数値/年3月期/専門用語は禁止。")


def _explanation_ok(x, full_text):
    """解説も本文照合ゲート: 解説の特徴語(4字以上・共通語除く)が自社全corpusに実在すること。"""
    ex = str(x.get("explanation", ""))
    if not ex:
        return True
    toks = [t for t in re.findall(r"[一-龥ァ-ヶーA-Za-z]{4,}", ex) if t not in _STOP]
    if not toks:
        return True
    hit = sum(1 for t in toks if t in full_text)
    return hit >= max(1, len(toks) // 2)                 # 過半の特徴語が本文に実在


def gen_lv3(slug, name, n=3, exclude=None, sem_used=None, pool=None):
    """Lv3応用: 『正しい説明はどれ』型(文章択)。正解=本文裏取りの正確な説明・誤答=別業界の事業説明。解説+出典付き。"""
    dp = os.path.join(OUT, slug, "datasheet.json")
    if not os.path.exists(dp):
        return []
    ds = json.load(open(dp))
    corpus = json.load(open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json"))) if os.path.exists(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")) else {}
    facts = _factsheet_facts(slug) + _scenario_facts(slug) + [dict(x, kind="basic") for x in _ds_facts(ds)]
    if len(facts) < 3:
        return []
    for x in facts:
        u = x["source_url"] or "ds://local"
        corpus[u] = corpus.get(u, "") + " " + x["fact"]
    if pool is None:
        pool = _source_pool(slug)
    home = _official_home(slug)
    full_text = _full_corpus_text(slug, pool)
    fl = "\n".join(f"- {x['fact']} <出典:{x['source_url']}>" for x in facts[:24])
    data = q._parse_json(q.openai_chat([{"role": "system", "content": L3_SYS},
                        {"role": "user", "content": L3_USER.format(name=name, n=n + 4, facts=fl)}],
                        max_tokens=2600, temperature=0.4))
    raw = data.get("questions", []) if isinstance(data, dict) else []
    ok, used, sused = [], set(exclude or set()), set(sem_used or set())
    for i, x in enumerate(raw):
        if not (isinstance(x.get("options"), list) and len(x["options"]) == 4):
            continue
        x["id"] = f"{slug}_lv3_{len(ok)+1:02d}"; x["difficulty"] = 3
        x["as_of"] = ""; x["explanation"] = x.get("explanation") or ""; x["category"] = x.get("category") or "事業セグメント"
        # 正解説明の該当ページを解決(固有語=product mode。長文はkey entityで該当ページを特定)
        src = _resolve_source(x["options"][x.get("correct", 0)], pool, home, product=True)
        if not src:
            continue
        x["source_url"] = src
        if QL.run_quiz_lints([x], corpus)["errors"] > 0:
            continue
        if not _distractor_ok(x, full_text) or not _explanation_ok(x, full_text):
            continue
        sig = _sem_sig(x); fk = frozenset(QL._fact_keys(x))
        if fk & used or (sig and any(len(sig & s) >= max(2, min(len(sig), len(s)) - 1) for s in sused)):
            continue
        used |= fk; sused.add(sig); ok.append(x)
        if len(ok) >= n:
            break
    return ok[:n]


def selftest():
    good = {"difficulty": 1, "id": "t1", "q_text": "任天堂の主力事業は何ですか", "options": ["ゲーム", "鉄道", "銀行", "石油"]}
    bad = {"difficulty": 1, "id": "t2", "q_text": "2026年3月期の売上高は？", "options": ["1兆円", "2兆円", "3兆円", "4兆円"]}
    e = lint_difficulty([good, bad])
    ok = len(e) == 1 and e[0][1] == "t2"
    # v2.5 誤答が自社全資料に実在→drop / 別業界固有領域→OK。三菱商事は都市開発=不動産を持つ→不動産は誤答不可
    full = "総合商社エネルギー金属都市開発不動産ローソン天然ガス"
    ng = {"correct": 0, "options": ["天然ガス", "不動産", "ゲーム開発", "医薬品製造"]}   # 不動産が自社実在→NG
    okd = {"correct": 0, "options": ["天然ガス", "ゲーム開発", "医薬品製造", "アニメ制作"]}  # 全て別業界→OK
    ok2 = (not _distractor_ok(ng, full)) and _distractor_ok(okd, full)
    print(f"[selftest] Lv1決算error={ok} / 自社実在誤答drop(不動産)={ok2}")
    print("=== SELFTEST:", "PASS ===" if (ok and ok2) else "FAIL ===")
    return ok and ok2


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
