#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quiz_lint.py — 理解度チェッククイズの品質ゲート（Source-or-Silence 思想）。

room / scenario_lints_v5_ext の加算式 findings＋severity＋selftest の流儀を踏襲。
error = 出荷不可（捨てるか直す）/ warning = 人間レビュー（ブロックしない）。

■ 思想（Source-or-Silence）
  クイズの数値/日付は「一次情報の取得本文に文字列として実在する」ものだけ出す。
  照合できない＝出さない（捏造で埋めない）。誤答(distractor)の数値も同じ本文に
  実在必須 → 必然的に「同一ソース内の別年度/別セグメントの実数」を誤答に使う設計になる。

■ 入力
  quiz.json  : 設問リスト（下記スキーマ）
  corpus.json: {source_url: 取得本文(verbatim), ...}  ← 数値/日付/順位照合の台帳
                無指定/該当url無し → 照合不能 = error（Source-or-Silence）

■ 設問スキーマ
  {
    "id":          "mitsui-bussan_01",
    "category":    "財務数値",          # 必須。ALLOWED_CATEGORIES のいずれか
    "q_text":      "設問文",
    "options":     ["A","B","C","D"],   # ちょうど4択
    "correct":     0,                     # 正解の options インデックス(int)
    "explanation": "解説文",
    "source_url":  "https://...",         # 一次情報URL(必須)
    "as_of":       "2025年3月期",          # 数字設問は必須(時期)。非数字設問は "" 可
    "type":        "rank",                # 任意。順位主張設問のとき指定
    "competitors": [ {"name":"三菱商事","value":"18,617,601","source_url":"..."}, ... ],
                                          # type=rank のとき必須(全競合の実数+出典)
    "source_excerpt": "…",                # 任意（人間検分用の該当本文抜粋）
  }

■ lint（10種）
  source_required          : source_url 空 → error
  asof_required_if_number   : 設問文に数字を含むのに as_of 空 → error
  single_correct            : 正解がちょうど1つ(correctが0..len-1のint、options4件) でない → error
  distractor_plausibility   : 誤答3つが 空/重複/明らかに無関係 → warning
  no_ratio                  : 倍率(数値付き)混入 → error（RATIO_WHITELIST 例外のみ warning）
  no_fabrication_number     : 設問・誤答・解説・as_of の数値が引用本文に実在しない → error
  no_fabrication_date       : 完全な日付(M月D日/Y年M月D日)が引用本文に verbatim 実在しない → error   ★強化①
  banned_schedule_topic     : 総会日/配当支払日/有報提出日 等の日程トリビア設問 → error          ★強化②
  rank_claim                : 順位主張は competitors 全社の値が corpus 実在必須 / 株数依存指標(EPS等)禁止 → error ★強化③
  category_valid            : category が ALLOWED_CATEGORIES 外/欠落 → error                        ★強化④

CLI:  python quiz_lint.py <quiz.json> [--corpus corpus.json]
      python quiz_lint.py --selftest
"""
import json, os, re, sys

RATIO_WHITELIST = set()  # 設問idの接頭辞で判定。クイズでは原則ゼロ。

RATIO_RE = re.compile(r"(約)?\d+(\.\d+)?\s*[〜~–-]?\s*(\d+)?\s*倍")
NEG_RE   = re.compile(r"倍率(の話)?(じゃ|では|でなく|より)|何倍(か|も)?(は|を)?(?:問|聞|示|出)さ")
SELECTIVITY_CTX = ("倍率", "採用", "応募", "競争", "選考", "難関", "内定", "エントリー", "志望", "選抜")

# 数値トークン: 先頭が数字で、内部に桁区切りカンマ/小数点/中黒を許す
NUM_RE = re.compile(r"\d[\d,，.．]*")
DIGIT_RE = re.compile(r"[0-9０-９]")
# 完全な日付(Y年任意 + M月D日)。PDF抽出の空白ゆれを許容。
DATE_RE = re.compile(r"(?:\d+\s*年\s*)?\d+\s*月\s*\d+\s*日")

JUNK_DISTRACTOR = {"", "なし", "n/a", "na", "―", "-", "－", "？", "?", "不明", "わからない", "該当なし"}

# ★強化④ カテゴリ統制語彙
ALLOWED_CATEGORIES = {"財務数値", "会社概要", "事業セグメント", "沿革",
                      "製品・サービス", "人名・役員", "業界順位", "その他"}

# ★強化② 禁止トリビア(会社の実態理解に資さない: 日程 + 電話/取引所/住所断片 等)
BANNED_SCHEDULE_KW = ("株主総会", "配当支払開始", "配当支払予定", "支払開始予定", "支払開始日",
                      "有価証券報告書提出", "有報提出", "提出予定日", "開催予定日",
                      "決算発表日", "決算発表予定", "権利確定日", "配当基準日", "基準日",
                      # v3追加: 電話・上場取引所・住所(現実に存在しない誤答を生みやすい単純転記)
                      "電話番号", "tel", "電話", "上場取引所", "上場している取引所", "証券取引所",
                      "上場市場", "上場している市場", "どの取引所", "郵便番号", "丁目", "番地", "所在地の住所",
                      "本店所在地", "本社所在地", "所在地はどこ", "本店はどこ", "本社はどこ", "住所は",
                      # v3-3① URL・掲載場所を問う設問(兼松Q7型)を禁止
                      "url", "どのページ", "どこに掲載", "どこに記載", "掲載場所", "掲載ページ",
                      "何ページ", "どのリンク", "リンク先", "掲載されているページ", "どこで公開")

# ★強化③ 順位主張の検出 / 株数依存(社間比較で歪む)指標の禁止
RANK_KW = ("最も大きい", "最も高い", "最も多い", "最大", "最高", "最多", "首位", "トップ",
           "第1位", "1位", "一位", "最下位", "最も低い", "最も小さい", "最も少ない", "ランキング")
PERSHARE_KW = ("eps", "bps", "1株当たり", "一株当たり", "１株当たり", "株当たり",
               "1株につき", "1株当り", "株価", "一株当り")


def _f(lint, sev, qid, detail):
    return {"lint": lint, "severity": sev, "id": qid, "detail": detail}


def _slug_prefix(qid):
    return (qid or "").rsplit("_", 1)[0]


Z2H = str.maketrans("０１２３４５６７８９，．　", "0123456789,. ")


def _norm_num(s):
    """桁区切り(カンマ)除去・全角数字半角化・前後の点/カンマ剥がし。"""
    return s.translate(Z2H).replace(",", "").strip(".")


def _norm_date(s):
    """日付照合用: 全角半角化し空白除去(年月日は保持)。"""
    return re.sub(r"\s+", "", s.translate(Z2H))


def _num_tokens(text):
    out = set()
    for m in NUM_RE.finditer(text or ""):
        t = _norm_num(m.group(0))
        if t:
            out.add(t)
    return out


def _date_tokens(text):
    return {_norm_date(m.group(0)) for m in DATE_RE.finditer(text or "")}


def _q_text_fields(q):
    """数値/日付照合の対象(id/source_url/source_excerpt/category/type は除外)。"""
    parts = [q.get("q_text", ""), q.get("explanation", ""), q.get("as_of", "")]
    parts += [str(o) for o in (q.get("options") or [])]
    return parts


# ── lint 各種 ─────────────────────────────────────────────
def lint_source_required(q):
    if not (q.get("source_url") or "").strip():
        return [_f("source_required", "error", q.get("id"), "source_url 空（一次情報URL必須）")]
    return []


def lint_asof_required_if_number(q):
    if DIGIT_RE.search(q.get("q_text", "") or "") and not (q.get("as_of") or "").strip():
        return [_f("asof_required_if_number", "error", q.get("id"),
                   f"設問に数字を含むのに as_of 空: {q.get('q_text','')[:40]}")]
    return []


def lint_single_correct(q):
    opts = q.get("options") or []
    c = q.get("correct")
    if len(opts) != 4:
        return [_f("single_correct", "error", q.get("id"), f"選択肢が4件でない(={len(opts)})")]
    if not isinstance(c, int) or isinstance(c, bool) or not (0 <= c < len(opts)):
        return [_f("single_correct", "error", q.get("id"), f"correctが単一の有効index(0..3)でない: {c!r}")]
    return []


def lint_category_valid(q):  # ★強化④
    cat = q.get("category")
    if cat not in ALLOWED_CATEGORIES:
        return [_f("category_valid", "error", q.get("id"),
                   f"category不正/欠落: {cat!r} (許可={sorted(ALLOWED_CATEGORIES)})")]
    return []


def lint_distractor_plausibility(q):
    opts = [str(o).strip() for o in (q.get("options") or [])]
    c = q.get("correct")
    res = []
    seen = {}
    for i, o in enumerate(opts):
        seen.setdefault(o.lower(), []).append(i)
    for val, idxs in seen.items():
        if len(idxs) > 1:
            res.append(_f("distractor_plausibility", "warning", q.get("id"),
                          f"選択肢重複: {opts[idxs[0]]!r} @index{idxs}"))
    if isinstance(c, int) and 0 <= c < len(opts):
        for i, o in enumerate(opts):
            if i == c:
                continue
            if o.lower() in JUNK_DISTRACTOR:
                res.append(_f("distractor_plausibility", "warning", q.get("id"),
                              f"誤答が空/無関係プレースホルダ: index{i}={o!r}"))
    return res


def lint_no_ratio(q):
    wl = _slug_prefix(q.get("id")) in RATIO_WHITELIST
    res = []
    for field in _q_text_fields(q):
        if "倍率" not in field and not RATIO_RE.search(field or ""):
            continue
        if NEG_RE.search(field):
            continue
        num = RATIO_RE.search(field)
        has_sel = any(cx in field for cx in SELECTIVITY_CTX)
        if num and has_sel:
            sev = "warning" if wl else "error"
            note = "(whitelist)" if wl else "(倍率数値は出さない)"
            res.append(_f("no_ratio", sev, q.get("id"), f"倍率数値『{num.group(0)}』{note}: {field[:30]}"))
        elif "倍率" in field:
            res.append(_f("no_ratio", "warning", q.get("id"), f"『倍率』言及(数値なし・要確認): {field[:30]}"))
    return res


def lint_banned_schedule_topic(q):  # ★強化②
    qt = q.get("q_text", "") or ""
    ql = qt.lower()
    hit = [k for k in BANNED_SCHEDULE_KW if k in qt or k in ql]
    if hit:
        return [_f("banned_schedule_topic", "error", q.get("id"),
                   f"禁止トリビア(日程/電話/取引所/住所/URL): {hit} — {qt[:36]}")]
    return []


def lint_no_fabrication_number(q, corpus):
    qid, url = q.get("id"), (q.get("source_url") or "").strip()
    wanted = set()
    for field in _q_text_fields(q):
        wanted |= _num_tokens(field)
    if not wanted:
        return []
    if corpus is None:
        return [_f("no_fabrication_number", "error", qid, "corpus未指定→数値照合不能(Source-or-Silence)")]
    body = corpus.get(url)
    if not body:
        return [_f("no_fabrication_number", "error", qid, f"corpusに該当url本文なし→照合不能: {url}")]
    body_norm = _norm_num(body)
    missing = sorted(t for t in wanted if t not in body_norm)
    if missing:
        return [_f("no_fabrication_number", "error", qid, f"引用本文に不在の数値: {missing} (url={url})")]
    return []


def lint_no_fabrication_date(q, corpus):  # ★強化①
    qid, url = q.get("id"), (q.get("source_url") or "").strip()
    wanted = set()
    for field in _q_text_fields(q):
        wanted |= _date_tokens(field)
    if not wanted:
        return []
    if corpus is None:
        return [_f("no_fabrication_date", "error", qid, "corpus未指定→日付照合不能(Source-or-Silence)")]
    body = corpus.get(url)
    if not body:
        return [_f("no_fabrication_date", "error", qid, f"corpusに該当url本文なし→日付照合不能: {url}")]
    body_norm = _norm_date(body)
    missing = sorted(d for d in wanted if d not in body_norm)
    if missing:
        return [_f("no_fabrication_date", "error", qid,
                   f"引用本文に不在の完全日付: {missing} (url={url})")]
    return []


def lint_rank_claim(q, corpus):  # ★強化③
    qid = q.get("id")
    qt = q.get("q_text", "") or ""
    is_rank = q.get("type") == "rank" or any(k in qt for k in RANK_KW)
    if not is_rank:
        return []
    res = []
    low = qt.lower()
    ps = [k for k in PERSHARE_KW if k in low]
    if ps:
        res.append(_f("rank_claim", "error", qid,
                      f"株数依存指標の社間比較は禁止(EPS/BPS/1株当たり等): {ps}"))
    comps = q.get("competitors") or []
    if len(comps) < 2:
        res.append(_f("rank_claim", "error", qid,
                      "順位主張は competitors(全競合の値+出典) 必須(>=2)"))
        return res
    if corpus is None:
        res.append(_f("rank_claim", "error", qid, "順位検証に corpus 必須"))
        return res
    for c in comps:
        name = c.get("name", "?")
        curl = (c.get("source_url") or "").strip()
        val = str(c.get("value", ""))
        body = corpus.get(curl)
        if not body:
            res.append(_f("rank_claim", "error", qid, f"競合[{name}]のsource_url本文がcorpus不在: {curl}"))
            continue
        bn = _norm_num(body)
        miss = sorted(t for t in _num_tokens(val) if t not in bn)
        if miss:
            res.append(_f("rank_claim", "error", qid, f"競合[{name}]の値{val}がcorpus不在: {miss}"))
    return res


PER_Q = [lint_source_required, lint_asof_required_if_number, lint_single_correct,
         lint_category_valid, lint_distractor_plausibility, lint_no_ratio,
         lint_banned_schedule_topic]


# ── 作りの品質(v2): 単位整合 / 概念dedup / ドライトリビア上限 ──
UNIT_RE = re.compile(r"(百万円|億円|兆円|千円|円|%|名|社|株|拠点|カ国・地域|カ国|人|件|ドル|ポイント|年間)\s*$")
# ★v3-2① 会社名(法人)判定: 人名問に社名が混じる型整合違反を検出するため
COMPANY_SUF = re.compile(
    r"(株式会社|（株）|\(株\)|ホールディングス|ホールディング|ＨＤ|グループ|"
    r"工業|商事|商会|物産|通商|化学|化工|建設|銀行|信託|保険|証券|製作所|電機|重工|"
    r"自動車|産業|製鉄|製薬|海運|商船|石油|電力|ガス|鉄道|食品|製菓|飲料|繊維|"
    r"Corporation|Corp\.?|Inc\.?|Ltd\.?|LIMITED|Company|&\s*Co|PLC|LLC)")
def _unit_class(opt):
    """選択肢の型/単位クラス。text/date/year/money-unit/percent/名/社/株/company … を返す。"""
    s = str(opt).translate(Z2H).replace("％", "%").strip()
    if not DIGIT_RE.search(s):
        return "company" if COMPANY_SUF.search(s) else "text"   # 社名 vs 人名/その他テキスト
    if re.search(r"\d+\s*月\s*\d+\s*日", s):
        return "date"
    m = UNIT_RE.search(s)
    if m:
        return "percent" if m.group(1) == "%" else m.group(1)
    if re.search(r"\d{3,4}\s*年", s):
        return "year"
    if COMPANY_SUF.search(s):
        return "company"
    return "number"

def lint_unit_consistency(q):
    opts = q.get("options") or []
    if len(opts) != 4:
        return []
    classes = {_unit_class(o) for o in opts}
    if len(classes) > 1:
        detail = " / ".join(f"{_unit_class(o)}:{str(o)[:14]}" for o in opts)
        return [_f("unit_consistency", "error", q.get("id"),
                   f"選択肢の型/単位が不揃い({sorted(classes)}): {detail}")]
    return []

# 概念グループ(canonical, [検出語])。優先順(specific first)で最初に一致した canonical を採用。
CONCEPT_MAP = [
    ("経営者", ("代表取締役", "社長", "ceo", "coo", "代表者", "会長")),
    ("従業員数", ("従業員", "社員数")),
    ("連結子会社数", ("連結子会社数", "子会社数", "グループ会社数")),
    ("設立", ("設立", "創業", "創立")),
    ("資本金", ("資本金",)),
    ("本店所在地", ("本店", "本社所在地", "所在地", "本社は")),
    ("株式数", ("発行済株式", "自己株式", "期中平均株式", "株式数")),
    ("証券コード", ("証券コード", "コード番号")),
    ("英文社名", ("英文", "商号")),
    ("拠点", ("拠点", "カ国", "事業所数")),
    ("帰属利益", ("帰属する当期", "帰属当期利益", "当社株主に帰属")),
    ("税引前利益", ("税引前利益",)),
    ("包括利益", ("包括利益",)),
    ("営業利益", ("営業利益",)),
    ("当期利益", ("当期利益", "純利益")),
    ("収益", ("収益", "売上高", "売上収益")),
    ("総資産", ("総資産", "資産合計")),
    ("純資産資本", ("純資産", "資本合計")),
    ("自己資本比率", ("自己資本比率", "帰属持分比率")),
    ("ROE", ("roe", "当期利益率")),
    ("配当", ("配当性向", "配当金", "年間配当", "1株当たり配当", "配当")),
    ("CF", ("キャッシュ・フロー", "営業活動による", "現金及び現金同等物")),
    ("1株当たり指標", ("1株当たり", "eps", "bps")),
    ("持分法", ("持分法",)),
    ("セグメント事業", ("セグメント", "事業本部", "事業内容", "事業領域", "事業分野")),
    ("経営理念", ("経営理念", "企業理念", "ミッション", "バリュー", "ビジョン")),
]
DRY_CONCEPTS = {"本店所在地", "資本金", "株式数"}   # 登記/単純転記トリビア(合計2問まで)
DRY_CAP = 2

def _concept_of(q):
    t = (q.get("q_text", "") or "").lower()
    for canon, terms in CONCEPT_MAP:
        if any(term.lower() in t for term in terms):
            return canon
    return None

def _fact_keys(q):
    """設問の『事実キー』集合。表記ゆれ耐性のため concept と『正解値』の両方を鍵にする。
    → 言い回しが違っても同じ事実(例: 連結子会社数)を問えば重複検出できる。"""
    asof = (q.get("as_of") or "").strip()
    keys = set()
    c = _concept_of(q)
    if c:
        keys.add(("c:" + c, asof))
    # 正解の値(数値)も鍵に。同じ答え=同じ事実の強いシグナル。
    # ★as_of非依存: 三綱領1934年をas_of=''と'2025年'(誤)で問う等、as_ofの不整合で
    #   重複がすり抜けるのを防ぐ(値そのものが十分に特定的)。
    opts = q.get("options") or []
    ci = q.get("correct")
    if isinstance(ci, int) and 0 <= ci < len(opts):
        corr = str(opts[ci]).strip()
        nums = _num_tokens(corr)
        if nums:
            keys.add("v:" + ",".join(sorted(nums)))
        else:
            # ★v3-3② 否定事実(含まない/やっていない)と製品・サービス名は正解名で1問に集約。
            #   兼松の不動産3連発、同一製品名(KG ZAICO等)の重複を捕捉。順位設問(社名が
            #   指標ごとに正当に繰り返す)は対象外にして誤検出を避ける。
            qt = q.get("q_text", "") or ""
            is_neg = any(k in qt for k in ("含まない", "含まれない", "やっていない", "行っていない",
                                           "展開していない", "扱っていない", "該当しない", "していない事業"))
            is_prod = q.get("category") == "製品・サービス"
            if q.get("type") != "rank" and c != "業界順位" and (is_neg or is_prod):
                keys.add("name:" + re.sub(r"\s", "", corr))
    return keys

def lint_concept_dedup(quiz):
    """同じ事実(概念 or 正解値)×同じas_of を問う設問が複数 → 2つ目以降 error(1つに集約)。
    表記ゆれ耐性: 『連結子会社数はいくつ/子会社は何社/グループ会社数』等を同一視。"""
    seen, res = {}, []
    for q in quiz:
        dup_key = None
        for k in _fact_keys(q):
            if k in seen:
                dup_key = k; break
        if dup_key is not None:
            res.append(_f("concept_dedup", "error", q.get("id"),
                          f"事実重複{dup_key} 既出={seen[dup_key]} → 1問に集約"))
        else:
            for k in _fact_keys(q):
                seen[k] = q.get("id")
    return res

def lint_dry_trivia_cap(quiz):
    """本店所在地・資本金・株式数(発行済/自己/平均)の登記トリビアは合計DRY_CAP問まで。"""
    dry = [q for q in quiz if _concept_of(q) in DRY_CONCEPTS]
    res = []
    if len(dry) > DRY_CAP:
        for q in dry[DRY_CAP:]:
            res.append(_f("dry_trivia_cap", "error", q.get("id"),
                          f"ドライトリビア({_concept_of(q)})が上限{DRY_CAP}超過({len(dry)}問) → 事業/セグメント/財務へ差し替え"))
    return res

# ★v3-2② 可変事実は as_of 必須(社長・従業員数・会社数・株式数・拠点・資本金)
VARIABLE_CONCEPTS = {"経営者", "従業員数", "連結子会社数", "株式数", "拠点", "資本金"}
def lint_variable_asof(q):
    if _concept_of(q) in VARIABLE_CONCEPTS and not (q.get("as_of") or "").strip():
        return [_f("variable_asof", "error", q.get("id"),
                   f"可変事実({_concept_of(q)})は as_of(時点)必須: {q.get('q_text','')[:32]}")]
    return []

# ★v3-2③ 派生値(合計=構成要素の和)の設問は落とす
def _answer_int(q):
    opts = q.get("options") or []
    ci = q.get("correct")
    if not (isinstance(ci, int) and 0 <= ci < len(opts)):
        return None, None
    nums = _num_tokens(str(opts[ci]))
    ints = [int(t) for t in nums if t.isdigit()]
    if len(ints) != 1:
        return None, None
    return ints[0], _unit_class(str(opts[ci]))

def lint_derived_value(quiz):
    """ある設問の正解値が、他の2問の正解値の和になっている(例 1,182=833+349)なら派生値=落とす。"""
    vals = []
    for q in quiz:
        v, u = _answer_int(q)
        if v is not None:
            vals.append((q.get("id"), v, u))
    res = []
    for qid, v, u in vals:
        if v < 50:                     # 微小値は偶然の和が起きやすいので対象外
            continue
        others = [(oid, ov) for oid, ov, ou in vals if oid != qid and ov >= 20]  # 単位非依存(1,182と833社の書式差を吸収)
        found = False
        for i in range(len(others)):
            for j in range(i + 1, len(others)):
                if others[i][1] + others[j][1] == v and others[i][1] != v and others[j][1] != v:
                    res.append(_f("derived_value", "error", qid,
                                  f"派生値: 正解{v}={others[i][1]}+{others[j][1]}({others[i][0]},{others[j][0]}) → 冗長で落とす"))
                    found = True; break
            if found: break
    return res

# ★v3-2④ 同一リストの「含む/含まない」ペアは1問に
INCL_RE = re.compile(r"(.{2,20}?)(に(?:含まれ|含む|該当|当てはま))")
def _list_subject(q):
    m = INCL_RE.search(q.get("q_text", "") or "")
    return re.sub(r"[のに、。]", "", m.group(1)).strip() if m else None

def lint_list_membership_dedup(quiz):
    """同じリスト(事業セグメント/企業行動指針 等)の含む/含まない設問が複数 → 1問に集約。"""
    seen, res = {}, []
    for q in quiz:
        s = _list_subject(q)
        if not s:
            continue
        if s in seen:
            res.append(_f("list_membership_dedup", "error", q.get("id"),
                          f"同一リスト『{s}』の含む/含まない重複 既出={seen[s]} → 1問に"))
        else:
            seen[s] = q.get("id")
    return res


def run_quiz_lints(quiz, corpus=None):
    findings = []
    seen_ids = {}
    for q in quiz:
        for fn in PER_Q:
            findings += fn(q)
        findings += lint_unit_consistency(q)
        findings += lint_variable_asof(q)     # ④可変事実はas_of必須
        findings += lint_no_fabrication_number(q, corpus)
        findings += lint_no_fabrication_date(q, corpus)
        findings += lint_rank_claim(q, corpus)
        qid = q.get("id")
        seen_ids[qid] = seen_ids.get(qid, 0) + 1
    findings += lint_concept_dedup(quiz)      # リスト全体で概念重複
    findings += lint_dry_trivia_cap(quiz)     # リスト全体でトリビア上限
    findings += lint_derived_value(quiz)      # ③派生値(合計=和)
    findings += lint_list_membership_dedup(quiz)  # ②含む/含まないペア
    for qid, c in seen_ids.items():
        if c > 1:
            findings.append(_f("single_correct", "error", qid, f"id重複×{c}"))
    e = sum(1 for f in findings if f["severity"] == "error")
    w = sum(1 for f in findings if f["severity"] == "warning")
    return {"findings": findings, "errors": e, "warnings": w, "n": len(quiz)}


def format_report(r, label=""):
    out = [f"[{label}] n={r['n']} errors={r['errors']} warnings={r['warnings']}"]
    for f in r["findings"]:
        out.append(f"  {f['severity'].upper():7} {f['lint']:24} {str(f['id']):18} {f['detail']}")
    return "\n".join(out)


# ── selftest ─────────────────────────────────────────────
def _corpus():
    return {
        "http://src/a": ("2025年3月期の連結収益は18,617,601百万円、前期は19,567,601百万円、"
                         "総資産21,496,104百万円、親会社帰属当期利益950,709百万円、ROEは10.3%。"
                         "設立は1918年10月1日。主な日付: 2024年7月1日、2025年6月18日、2025年5月2日、"
                         "2025年6月20日。定時株主総会は2025年6月20日開催。"),
        "http://src/b": "2025年3月期の連結収益は14,662,620百万円、親会社帰属当期利益900,342百万円、ROEは11.9%。",
    }


def _fixtures():
    corpus = _corpus()
    C = "財務数値"
    base = {"category": C, "options": ["A", "B", "C", "D"], "correct": 0,
            "explanation": "", "source_url": "http://src/a", "as_of": "2025年3月期"}
    cases = {
        "source_required": {**base, "id": "fx_src", "q_text": "本社は？",
                            "options": ["東京", "大阪", "名古屋", "札幌"], "category": "会社概要",
                            "source_url": "", "as_of": ""},
        "asof_required_if_number": {**base, "id": "fx_asof", "q_text": "収益は18,617,601百万円か？",
                                    "options": ["はい", "いいえ", "不明", "半分"], "as_of": ""},
        "single_correct": {**base, "id": "fx_single", "q_text": "本社は？",
                           "options": ["東京", "大阪", "名古屋"], "category": "会社概要"},
        "category_valid": {**base, "id": "fx_cat", "q_text": "本社は？",
                           "options": ["東京", "大阪", "名古屋", "札幌"], "category": "雑学", "as_of": ""},
        "distractor_plausibility": {**base, "id": "fx_dist", "q_text": "本社は？",
                                    "options": ["東京", "なし", "東京", "?"], "category": "会社概要", "as_of": ""},
        "no_ratio": {**base, "id": "fx_ratio", "q_text": "採用倍率は100倍か？",
                     "options": ["はい", "いいえ", "不明", "半分"], "correct": 1},
        "banned_schedule_topic": {**base, "id": "fx_sched",
                                  "q_text": "定時株主総会の開催予定日はいつか？",
                                  "options": ["6月20日", "6月18日", "6月19日", "6月17日"], "as_of": "2025年"},
        "no_fabrication_number": {**base, "id": "fx_fab",
                                  "q_text": "2025年3月期の連結収益は？",
                                  "options": ["18,617,601百万円", "18,600,000百万円", "950,709百万円", "10百万円"]},
        "no_fabrication_date": {**base, "id": "fx_date", "category": "沿革",
                                "q_text": "設立年月日は？",
                                "options": ["1918年10月2日", "1918年10月1日", "1900年1月1日", "1950年5月5日"],
                                "correct": 1, "as_of": "設立"},
        "rank_claim": {**base, "id": "fx_rank", "category": "業界順位", "type": "rank",
                       "q_text": "2025年3月期にEPSが最も高い商社は？",
                       "options": ["三菱商事", "三井物産", "伊藤忠商事", "住友商事"]},
        "unit_consistency": {**base, "id": "fx_unit", "category": "会社概要", "q_text": "資本金は？",
                             "options": ["344,163,332,347円", "5,333名", "2,905,248,272株", "62カ国"],
                             "as_of": "2026年"},
        "variable_asof": {**base, "id": "fx_var", "category": "人名・役員", "q_text": "社長は誰か？",
                          "options": ["中西勝也", "堀健一", "石井敬太", "上野真吾"], "as_of": ""},
    }
    return corpus, cases


def _positive():
    corpus = _corpus()
    qs = [
        {"id": "pos_num", "category": "財務数値", "q_text": "三菱商事の2025年3月期の連結収益は？",
         "options": ["18,617,601百万円", "19,567,601百万円", "21,496,104百万円", "950,709百万円"],
         "correct": 0, "explanation": "収益18,617,601百万円。", "source_url": "http://src/a",
         "as_of": "2025年3月期"},
        {"id": "pos_date", "category": "沿革", "q_text": "設立年月日は？",
         "options": ["1918年10月1日", "2024年7月1日", "2025年6月18日", "2025年5月2日"],
         "correct": 0, "explanation": "1918年10月1日設立。", "source_url": "http://src/a", "as_of": "設立"},
        {"id": "pos_rank", "category": "業界順位", "type": "rank",
         "q_text": "2025年3月期にROEが最も高い商社は？",
         "options": ["三井物産", "三菱商事", "伊藤忠商事", "住友商事"], "correct": 0,
         "explanation": "三井物産が最高。", "source_url": "http://src/b", "as_of": "2025年3月期",
         "competitors": [{"name": "三菱商事", "value": "10.3", "source_url": "http://src/a"},
                         {"name": "三井物産", "value": "11.9", "source_url": "http://src/b"}]},
    ]
    return corpus, qs


def selftest():
    ok = True
    print("=== 負例フィクスチャ：各lint発火 ===")
    corpus, cases = _fixtures()
    for name, q in cases.items():
        r = run_quiz_lints([q], corpus)
        fired = any(f["lint"] == name for f in r["findings"])
        print(f"  {'OK ' if fired else 'NG '} {name}: {'発火' if fired else '発火せず(NG)'}")
        if not fired:
            print("      " + format_report(r, name))
        ok = ok and fired
    print("\n=== リスト全体lint(概念dedup / ドライトリビア上限) ===")
    base = {"category": "会社概要", "correct": 0, "explanation": "", "source_url": "http://src/a", "as_of": ""}
    dup_list = [{**base, "id": "d1", "q_text": "社長は誰か？", "options": ["A", "B", "C", "D"]},
                {**base, "id": "d2", "q_text": "代表取締役社長は誰か？", "options": ["A", "B", "C", "D"]}]
    fired_dup = any(f["lint"] == "concept_dedup" for f in run_quiz_lints(dup_list, corpus)["findings"])
    print(f"  {'OK ' if fired_dup else 'NG '} concept_dedup(社長×2): {'発火' if fired_dup else 'NG'}")
    # 表記ゆれ耐性: 同じ正解値を別の言い回しで問う → dedup
    val_list = [{**base, "id": "v1", "category": "会社概要", "q_text": "連結子会社は何社か？",
                 "options": ["1,234社", "1,200社", "1,300社", "1,100社"], "as_of": "2025年"},
                {**base, "id": "v2", "category": "会社概要", "q_text": "グループの連結子会社数はいくつか？",
                 "options": ["1,234社", "1,240社", "1,250社", "1,260社"], "as_of": "2025年"}]
    fired_val = any(f["lint"] == "concept_dedup" for f in run_quiz_lints(val_list, corpus)["findings"])
    print(f"  {'OK ' if fired_val else 'NG '} concept_dedup(表記ゆれ・同一正解値): {'発火' if fired_val else 'NG'}")
    phone = {**base, "id": "ph", "category": "会社概要", "q_text": "本店の電話番号はどれか？",
             "options": ["03-1", "03-2", "03-3", "03-4"], "as_of": "2025年"}
    fired_phone = any(f["lint"] == "banned_schedule_topic" for f in run_quiz_lints([phone], corpus)["findings"])
    print(f"  {'OK ' if fired_phone else 'NG '} banned(電話番号): {'発火' if fired_phone else 'NG'}")
    # ①人名問に社名混入 → unit_consistency
    pc_mix = {**base, "id": "pc", "category": "人名・役員", "q_text": "社長は誰か？",
              "options": ["中西勝也", "堀健一", "三菱自動車工業", "上野真吾"], "as_of": "2025年"}
    fired_pc = any(f["lint"] == "unit_consistency" for f in run_quiz_lints([pc_mix], corpus)["findings"])
    print(f"  {'OK ' if fired_pc else 'NG '} unit_consistency(人名に社名混入): {'発火' if fired_pc else 'NG'}")
    # ③派生値(1182=833+349)
    dv = [{**base, "id": "a", "category": "会社概要", "q_text": "連結子会社数は？", "options": ["833社", "800社", "850社", "900社"], "as_of": "2025年"},
          {**base, "id": "b", "category": "会社概要", "q_text": "持分法適用会社数は？", "options": ["349社", "300社", "400社", "320社"], "as_of": "2025年"},
          {**base, "id": "c", "category": "会社概要", "q_text": "連結対象会社の合計は？", "options": ["1,182社", "1,000社", "1,200社", "1,100社"], "as_of": "2025年"}]
    fired_dv = any(f["lint"] == "derived_value" for f in run_quiz_lints(dv, corpus)["findings"])
    print(f"  {'OK ' if fired_dv else 'NG '} derived_value(1182=833+349): {'発火' if fired_dv else 'NG'}")
    # ②含む/含まないペア
    lm = [{**base, "id": "in", "category": "事業セグメント", "q_text": "事業セグメントに含まれるものはどれか？", "options": ["A", "B", "C", "D"], "as_of": ""},
          {**base, "id": "out", "category": "事業セグメント", "q_text": "事業セグメントに含まれないものはどれか？", "options": ["A", "B", "C", "D"], "as_of": ""}]
    fired_lm = any(f["lint"] == "list_membership_dedup" for f in run_quiz_lints(lm, corpus)["findings"])
    print(f"  {'OK ' if fired_lm else 'NG '} list_membership_dedup(含む/含まない): {'発火' if fired_lm else 'NG'}")
    urlq = {**base, "id": "u", "category": "会社概要", "q_text": "会社概要はどのURLに掲載されているか？", "options": ["A", "B", "C", "D"], "as_of": ""}
    fired_url = any(f["lint"] == "banned_schedule_topic" for f in run_quiz_lints([urlq], corpus)["findings"])
    print(f"  {'OK ' if fired_url else 'NG '} banned(URL/掲載場所): {'発火' if fired_url else 'NG'}")
    neg = [{**base, "id": "n1", "category": "事業セグメント", "q_text": "兼松が展開していない事業はどれか？", "options": ["不動産", "電子", "食料", "鉄鋼"], "as_of": ""},
           {**base, "id": "n2", "category": "事業セグメント", "q_text": "兼松の事業に含まれないものはどれか？", "options": ["不動産", "電子", "食料", "鉄鋼"], "as_of": ""}]
    fired_neg = any(f["lint"] == "concept_dedup" for f in run_quiz_lints(neg, corpus)["findings"])
    print(f"  {'OK ' if fired_neg else 'NG '} name_dedup(否定事実:不動産×2): {'発火' if fired_neg else 'NG'}")
    prod = [{**base, "id": "p1", "category": "製品・サービス", "q_text": "兼松の在庫管理サービスは？", "options": ["KG ZAICO", "A社", "B社", "C社"], "as_of": ""},
            {**base, "id": "p2", "category": "製品・サービス", "q_text": "兼松が提供するSaaSはどれか？", "options": ["KG ZAICO", "X", "Y", "Z"], "as_of": ""}]
    fired_prod = any(f["lint"] == "concept_dedup" for f in run_quiz_lints(prod, corpus)["findings"])
    print(f"  {'OK ' if fired_prod else 'NG '} name_dedup(製品名×2): {'発火' if fired_prod else 'NG'}")
    ok = ok and fired_val and fired_phone and fired_pc and fired_dv and fired_lm and fired_url and fired_neg and fired_prod
    dry_list = [{**base, "id": f"t{i}", "q_text": q, "options": ["A", "B", "C", "D"]}
                for i, q in enumerate(["本店所在地は？", "資本金は？", "発行済株式数は？"])]
    fired_dry = any(f["lint"] == "dry_trivia_cap" for f in run_quiz_lints(dry_list, corpus)["findings"])
    print(f"  {'OK ' if fired_dry else 'NG '} dry_trivia_cap(登記3問>上限2): {'発火' if fired_dry else 'NG'}")
    ok = ok and fired_dup and fired_dry
    print("\n=== 正例：error=0 で通過するか ===")
    pc, pqs = _positive()
    pr = run_quiz_lints(pqs, pc)
    pass_pos = pr["errors"] == 0
    print(f"  {'OK ' if pass_pos else 'NG '} positive: errors={pr['errors']} warnings={pr['warnings']}")
    if not pass_pos:
        print(format_report(pr, "positive"))
    ok = ok and pass_pos
    print("\n=== SELFTEST:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1


def main(argv):
    if not argv or argv[0] == "--selftest":
        return selftest()
    quiz_path = argv[0]
    corpus = None
    if "--corpus" in argv:
        with open(argv[argv.index("--corpus") + 1], encoding="utf-8") as fh:
            corpus = json.load(fh)
    with open(quiz_path, encoding="utf-8") as fh:
        quiz = json.load(fh)
    r = run_quiz_lints(quiz, corpus)
    print(format_report(r, os.path.basename(quiz_path)))
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
