#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/matching.py — 決定論マッチング(AI課金不要・即応答)。

回答 → 属性フィルタ+重み付けスコア → 業界おすすめ上位 + 企業おすすめ複数。
設計:
 ・欠損属性は減点しない = その設問の重みを分母から除外(判定対象外)。
 ・スコアは適用重みで正規化(0-1) → 欠損の多寡で不利にならない。
 ・トーン=参考提案。結果には根拠(①trend / ②数字+出典)を必ず添える。

API: recommend(answers, top_companies=8, top_industries=5) -> dict
     answers = {question_id: option_index}  (multi設問は {id:[idx,...]})
"""
import os, json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ATTR = ROOT / "attributes"
QS = json.load(open(ROOT / "questions.json"))["questions"]
QBYID = {q["id"]: q for q in QS}


_CACHE = None


def _load_all():
    global _CACHE
    if _CACHE is None:
        out = []
        for f in os.listdir(ATTR):
            if f.endswith(".json"):
                try:
                    out.append(json.load(open(ATTR / f)))
                except Exception:
                    pass
        _CACHE = out
    return _CACHE


def _avg_band(man):
    for thr, b in [(1200, 5), (900, 4), (700, 3), (550, 2)]:
        if man >= thr:
            return b
    return 1


def _start_band(yen):
    for thr, b in [(280000, 5), (250000, 4), (220000, 3), (200000, 2)]:
        if yen >= thr:
            return b
    return 1


def _sel(answers, qid):
    """回答をoptionリストへ正規化(単一/複数/未回答)。"""
    if qid not in answers:
        return []
    v = answers[qid]
    idxs = v if isinstance(v, list) else [v]
    return [QBYID[qid]["options"][i] for i in idxs if 0 <= i < len(QBYID[qid]["options"])]


def _closeness(v, target):
    return 1.0 - abs(v - target) / 4.0


# 年収重視回答時、有報grade年収が無い社に与える低スコア(欠損補正)。0=完全除外, 1=満点扱い。
MISSING_SALARY_SCORE = 0.25


def score_company(d, answers):
    """会社1社の(正規化スコア, 一致根拠list, meta)。適用重み0なら(0, [], meta)。"""
    wsum = 0.0
    acc = 0.0
    matched = []
    meta = {"missing_salary_pref": False}
    soft = d.get("soft", {})
    facts = d.get("facts", {})
    for q in QS:
        opts = _sel(answers, q["id"])
        if not opts:
            continue
        w = q.get("weight", 1.0)
        kind = q["kind"]

        if kind == "soft":
            target = opts[0].get("target")
            if target is None:
                continue
            v = soft.get(q["attr"], {}).get("value")
            if not isinstance(v, int):
                continue  # 欠損 → 対象外
            m = _closeness(v, target)
            acc += w * m; wsum += w
            if m >= 0.75:
                matched.append(_why(q, opts[0]))

        elif kind == "salary_avg":
            target = opts[0].get("target")
            if target is None:
                continue
            av = facts.get("avg_salary")
            if av:
                m = _closeness(_avg_band(av["value"]), target)
                acc += w * m; wsum += w
                if m >= 0.75:
                    matched.append(f"年収志向に合致(平均年収{av['value']}万円)")
            elif target >= 4:
                # 年収を重視する回答なのに有報grade年収が無い社は優先度を下げる
                # (年収不明社が高年収狙いの上位に来る誤りを是正)。target<=3(不問)は欠損=対象外。
                acc += w * MISSING_SALARY_SCORE; wsum += w
                meta["missing_salary_pref"] = True

        elif kind == "salary_start":
            target = opts[0].get("target")
            if target is None:
                continue
            st = facts.get("starting_salary")
            if st:
                m = _closeness(_start_band(st["value"]), target)
                acc += w * m; wsum += w
                if m >= 0.75:
                    matched.append(f"初任給重視に合致(初任給{st['value']:,}円)")
            elif target >= 4:
                acc += w * MISSING_SALARY_SCORE; wsum += w

        elif kind == "salary_wlb":
            # 両極1軸: 年収側=avg_salary(+初任給補助)/WLB側=remote_flex。中庸({})=判定対象外。
            tgt = opts[0].get("target") or {}
            if tgt.get("salary"):
                s_t = tgt["salary"]
                av = facts.get("avg_salary")
                if av:
                    m = _closeness(_avg_band(av["value"]), s_t)
                    acc += w * m; wsum += w
                    if m >= 0.75:
                        matched.append(f"年収志向に合致(平均年収{av['value']}万円)")
                elif s_t >= 4:
                    acc += w * MISSING_SALARY_SCORE; wsum += w
                    meta["missing_salary_pref"] = True
                st = facts.get("starting_salary")
                if st:  # 初任給は補助シグナル(半分の重み)
                    m2 = _closeness(_start_band(st["value"]), s_t)
                    acc += w * 0.5 * m2; wsum += w * 0.5
            elif tgt.get("wlb"):
                w_t = tgt["wlb"]
                v = soft.get("remote_flex", {}).get("value")
                if isinstance(v, int):
                    m = _closeness(v, w_t)
                    acc += w * m; wsum += w
                    if m >= 0.75:
                        matched.append("柔軟な働き方(WLB)を重視する傾向に合致")
            # tgt空(バランス)=シグナルなし=判定対象外

        elif kind == "bunri":
            target = opts[0].get("target")
            if target is None:
                continue
            v = soft.get("bunri", {}).get("value")
            if not v:
                continue
            m = 1.0 if v == target else (0.6 if v == "文理両方" else 0.2)
            acc += w * m; wsum += w

        elif kind == "tags":
            want = set()
            for o in opts:
                if o.get("target"):
                    want.update(o["target"])
            if not want:
                continue
            have = set(soft.get("job_tags", {}).get("value") or [])
            if not have:
                continue
            ov = len(want & have)
            m = min(1.0, ov / max(1, len(want)))
            acc += w * m; wsum += w
            if ov:
                matched.append(f"希望職種と重なり({'・'.join(sorted(want & have))})")

        elif kind == "industry":
            want = set()
            for o in opts:
                if o.get("target"):
                    want.update(o["target"])
            if not want:
                continue
            m = 1.0 if d.get("industry") in want else 0.0
            acc += w * m; wsum += w
            if m:
                matched.append(f"きになる業界に該当({d.get('industry')})")

    if wsum == 0:
        return 0.0, [], meta
    return acc / wsum, matched, meta


def _why(q, opt):
    return f"{q['text'].rstrip('？?')}→「{opt['label']}」に合致"


def _rationale(d, matched, meta=None):
    facts = d.get("facts", {})
    r = {"trend": d.get("trend_note", ""), "matched": matched[:4], "facts": {}, "notes": []}
    av = facts.get("avg_salary")
    if av:
        r["facts"]["avg_salary"] = {"text": f"平均年収 約{av['value']}万円", "source": av["evidence"].get("source_url", ""),
                                    "as_of": av.get("as_of", "")}
    elif meta and meta.get("missing_salary_pref"):
        # 年収重視の回答なのに出典年収が無い社=根拠欄に明示(数字は出さない=Source-or-Silence)
        r["notes"].append("年収データなし（出典のある平均年収が非公開のため、年収面は参考程度に）")
    st = facts.get("starting_salary")
    if st:
        r["facts"]["starting_salary"] = {"text": f"初任給 {st['value']:,}円/月", "source": st["evidence"].get("source_url", "")}
    return r


def _tiebreak(slug, answers, eps):
    """決定論の微小tie-breaker(0〜eps)。回答パターンと会社slugのhashで一意。
    同点社の順位を回答ごとに入れ替え、どの会社も『どこかの回答で上位に出る』を担保。
    epsは実スコア差(通常0.05+)より十分小さく、真に優れた社の順位は動かさない。"""
    if not eps:
        return 0.0
    h = int(hashlib.md5((json.dumps(answers, sort_keys=True, ensure_ascii=False) + "|" + slug).encode("utf-8")).hexdigest()[:8], 16)
    return (h % 100000) / 100000.0 * eps


def recommend(answers, top_companies=8, top_industries=5, max_per_industry=None, tiebreak_eps=0.01):
    """tiebreak_eps: 同点社を回答パターン依存で決定論的に入れ替える微小ノイズ(全社到達性の補正)。
    max_per_industry: 企業おすすめに同一業界をこの数までに制限(通常はNone推奨=深さを潰さない)。"""
    rows = _load_all()
    scored = []
    for d in rows:
        s, matched, meta = score_company(d, answers)
        sort_key = s + _tiebreak(d["slug"], answers, tiebreak_eps)
        scored.append((sort_key, s, matched, meta, d))
    scored.sort(key=lambda x: x[0], reverse=True)

    # 企業おすすめ(多様性capあり時は業界ごとの出現数を制限しつつ上位から採用)
    comps = []
    ind_count = {}
    for sort_key, s, matched, meta, d in scored:
        if len(comps) >= top_companies:
            break
        if max_per_industry:
            c = ind_count.get(d["industry"], 0)
            if c >= max_per_industry:
                continue
            ind_count[d["industry"]] = c + 1
        comps.append({"name": d["name"], "slug": d["slug"], "industry": d["industry"],
                      "score": round(s, 3), "rationale": _rationale(d, matched, meta)})

    # 業界おすすめ = 所属企業スコアの集計(平均)。有効スコア(適用重み>0)社のみ。
    ind_acc = {}
    for sort_key, s, matched, meta, d in scored:
        ind_acc.setdefault(d["industry"], []).append(s)
    ind_rank = [{"industry": k, "score": round(sum(v) / len(v), 3), "n": len(v)}
                for k, v in ind_acc.items()]
    ind_rank.sort(key=lambda x: x["score"], reverse=True)

    return {
        "top_industries": ind_rank[:top_industries],
        "top_companies": comps,
        "disclaimer": "この診断は公式公開情報と業界傾向に基づく参考提案です。断定・優劣付けではありません。",
        "answered": len([1 for q in QS if q["id"] in answers]),
    }


if __name__ == "__main__":
    import sys
    # デモ: 海外志向×成長×若手裁量×コンサル/IT
    demo = {"q_kaigai": 0, "q_growth": 0, "q_young": 0, "q_stability": 2,
            "q_jobtags": [4, 2], "q_industry": [4, 3]}
    print(json.dumps(recommend(demo), ensure_ascii=False, indent=2))
