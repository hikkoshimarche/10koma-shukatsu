#!/usr/bin/env python3
"""業界セットの「2025年3月期を最新期として提示」財務問を、その構成社の会社セット2026版で置換して2026化。
 業界問はmember会社クイズ由来(同一metric)。会社セットは会社スイープで2026強制済=検証済2026値。捏造せず流用。
 対象=(company, metric)一致する2026会社問。2026版が無い社/metricは2025据置(Source-or-Silence)。歴史型「2025年に」は対象外。
 出力: output/industry__<slug>/quiz_30q_locked_v3.json を更新(置換分のみ)。--dry で判定のみ。引数=GYOKAIスラグ(既定=5対象)。
"""
import json, os, sys, re, glob

OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
DEFAULT = ["sogo-shosha", "finance", "manufacturer", "realestate-construction", "it-ai-saas-game"]
# 財務metric→canonical(表記ゆれ吸収)。値は正規化キー。長い順に評価。
METRIC_CANON = {
    "親会社の所有者に帰属する当期利益": "親会社帰属利益", "親会社株主に帰属する当期純利益": "親会社帰属利益",
    "親会社所有者帰属持分比率": "持分比率", "自己資本比率": "持分比率",
    "1株当たり親会社所有者帰属持分": "1株当持分", "1株当たり当期純利益": "1株当利益", "1株当たり": "1株当利益",
    "当期包括利益合計額": "包括利益", "包括利益": "包括利益",
    "営業活動によるキャッシュ・フロー": "営業CF", "キャッシュ・フロー": "営業CF",
    "持分法による投資損益": "持分法損益", "持分法投資損益": "持分法損益",
    "経常収益": "経常収益", "経常利益": "経常利益", "税引前利益": "税引前利益",
    "当期純利益": "当期利益", "当期利益": "当期利益", "純利益": "当期利益",
    "営業利益": "営業利益", "売上高": "売上高", "収益": "収益",
    "資産合計": "総資産", "総資産": "総資産", "純資産": "純資産", "資本合計": "資本合計", "自己資本": "資本合計",
    "配当金総額": "配当", "年間配当金合計": "配当", "年間配当金": "配当", "配当": "配当",
    "ROE": "ROE", "従業員数": "従業員数", "資本金": "資本金",
    "代表取締役社長": "社長", "IR部長": "IR部長", "問合せ先責任者": "IR責任者",
}
_METRIC_KEYS = sorted(METRIC_CANON, key=len, reverse=True)


def _metric(qt):
    for m in _METRIC_KEYS:
        if m in qt:
            return METRIC_CANON[m]
    return None


def _company_token(qt):
    """問文から会社名トークンを抽出・正規化(株式会社/・除去)。年・metric表記に依存せず社を同定。"""
    # 「年3月期(の|における|の)<社名>の<metric>」/ 「<社名>株式会社の」 等
    m = re.search(r"(?:期の|における|期)\s*([一-龥ァ-ヶA-Za-z0-9Ａ-Ｚａ-ｚ・－ー]{2,20}?)(?:株式会社)?の", qt)
    tok = m.group(1) if m else ""
    return tok.replace("株式会社", "").replace("・", "").replace("－", "").strip()


def _company_names(members):
    """member slug→表示名(datasheet)。会社名で業界問と会社問を紐付け。"""
    nm = {}
    for s in members:
        dp = os.path.join(OUT, s, "datasheet.json")
        if os.path.exists(dp):
            try:
                nm[s] = json.load(open(dp)).get("name", s)
            except Exception:
                nm[s] = s
    return nm


def _member_map():
    """gen_gyokai_sets.MAP + 初期5セットのmembersを取得。未MAPは会社名照合で補完。"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_gyokai_sets as G
    mm = {k: v["members"] for k, v in G.MAP.items()}
    # 初期5セット(未MAP)の members: 全会社から、その業界問に名前が出る社を逆引き
    return mm


def _all_company_slugs():
    return [os.path.basename(os.path.dirname(f)) for f in glob.glob(OUT + "/*/datasheet.json")
            if not os.path.basename(os.path.dirname(f)).startswith("industry__")]


def build_global_2026_index():
    """全会社セットの2026財務問を {(会社識別名, canonical_metric): question} で索引。
    会社側2026問は社名を省く場合がある(単一社セット)ため、社の識別名はその社の自問群から収集した
    会社トークン集合(＋datasheet名)で確定し、2026 metric問を全識別名に張る。"""
    idx = {}
    for f in glob.glob(OUT + "/*/quiz_30q_locked_v3.json"):
        slug = os.path.basename(os.path.dirname(f))
        if slug.startswith("industry__"):
            continue
        try:
            quiz = json.load(open(f))
        except Exception:
            continue
        # (1) この社の識別名トークン集合(自問から抽出＋datasheet名)
        ids = set()
        for x in quiz:
            t = _company_token(x.get("q_text", ""))
            if t and len(t) >= 3:
                ids.add(t)
        dp = os.path.join(OUT, slug, "datasheet.json")
        if os.path.exists(dp):
            try:
                nm = json.load(open(dp)).get("name", "")
                nm = nm.replace("株式会社", "").replace("・", "").replace("－", "").strip()
                if len(nm) >= 3:
                    ids.add(nm)
            except Exception:
                pass
        if not ids:
            continue
        # (2) 2026 metric問を全識別名に索引(先勝ち)
        for x in quiz:
            qt = x.get("q_text", "")
            if "2026年3月期" not in qt:
                continue
            mt = _metric(qt)
            if not mt:
                continue
            for idn in ids:
                idx.setdefault((idn, mt), x)
    return idx


def remap_set(islug, gidx, dry=False):
    f = os.path.join(OUT, f"industry__{islug}", "quiz_30q_locked_v3.json")
    if not os.path.exists(f):
        return {"slug": islug, "status": "no_file"}
    quiz = json.load(open(f))
    # セット内で名指しされた会社集合。単一社セットなら空トークン問をその社にフォールバック(多社は曖昧→据置)。
    named = set()
    for q in quiz:
        t = _company_token(q.get("q_text", ""))
        if t and len(t) >= 3:
            named.add(t)
    sole = next(iter(named)) if len(named) == 1 else None
    replaced, held, hist, held_detail = 0, 0, 0, []
    for i, q in enumerate(quiz):
        qt = q.get("q_text", "")
        if "2025年3月期" not in qt:
            continue
        if re.search(r"2025年(に|には|の[0-9])", qt):   # 歴史型「2025年に〜」は対象外
            hist += 1
            continue
        tok, mt = _company_token(qt), _metric(qt)
        if (not tok or len(tok) < 3) and sole:          # 社名省略問は単一社セットの社で補完
            tok = sole
        src = gidx.get((tok, mt)) if (tok and mt) else None
        if not src:
            held += 1
            held_detail.append(f"{tok}/{mt}")           # 2026版が無い→2025据置
            continue
        if not dry:
            quiz[i]["q_text"] = src["q_text"]
            quiz[i]["options"] = src["options"]
            quiz[i]["correct"] = src["correct"]
            quiz[i]["source_url"] = src.get("source_url", q.get("source_url", ""))
            quiz[i]["as_of"] = src.get("as_of", "2026年3月期")
            if "explanation" in src:
                quiz[i]["explanation"] = src["explanation"]
        replaced += 1
    if replaced and not dry:
        json.dump(quiz, open(f, "w", encoding="utf-8"), ensure_ascii=False)
    return {"slug": islug, "status": "ok", "replaced": replaced, "held": held, "hist": hist,
            "total": len(quiz), "held_detail": held_detail}


def main():
    dry = "--dry" in sys.argv
    verbose = "--verbose" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")] or DEFAULT
    print(f"業界2026化 remap {'[DRY]' if dry else '[実走]'} 対象{len(args)}セット", flush=True)
    gidx = build_global_2026_index()
    print(f"  会社2026財務index: {len(gidx)}キー((社,metric))", flush=True)
    for islug in args:
        r = remap_set(islug, gidx, dry)
        if r["status"] != "ok":
            print(f"  {islug}: {r['status']}"); continue
        print(f"  industry__{islug:24} 置換={r['replaced']} 据置(2026版なし)={r['held']} 歴史型={r['hist']} /全{r['total']}", flush=True)
        if verbose and r.get("held_detail"):
            print(f"      据置内訳: {r['held_detail']}", flush=True)


if __name__ == "__main__":
    main()
