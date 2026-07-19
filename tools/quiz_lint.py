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

# ★強化② 禁止=日程トリビア(会社の実態理解に資さない開催日/支払日)
BANNED_SCHEDULE_KW = ("株主総会", "配当支払開始", "配当支払予定", "支払開始予定", "支払開始日",
                      "有価証券報告書提出", "有報提出", "提出予定日", "開催予定日",
                      "決算発表日", "決算発表予定", "権利確定日", "配当基準日", "基準日")

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
    hit = [k for k in BANNED_SCHEDULE_KW if k in qt]
    if hit:
        return [_f("banned_schedule_topic", "error", q.get("id"),
                   f"日程トリビア設問は禁止: {hit} — {qt[:36]}")]
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


def run_quiz_lints(quiz, corpus=None):
    findings = []
    seen_ids = {}
    for q in quiz:
        for fn in PER_Q:
            findings += fn(q)
        findings += lint_no_fabrication_number(q, corpus)
        findings += lint_no_fabrication_date(q, corpus)
        findings += lint_rank_claim(q, corpus)
        qid = q.get("id")
        seen_ids[qid] = seen_ids.get(qid, 0) + 1
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
         "q_text": "2025年3月期に連結収益が最も大きい商社は？",
         "options": ["三菱商事", "三井物産", "伊藤忠商事", "住友商事"], "correct": 0,
         "explanation": "三菱商事が最大。", "source_url": "http://src/a", "as_of": "2025年3月期",
         "competitors": [{"name": "三菱商事", "value": "18,617,601", "source_url": "http://src/a"},
                         {"name": "三井物産", "value": "14,662,620", "source_url": "http://src/b"}]},
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
