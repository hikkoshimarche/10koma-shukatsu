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
import os, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ATTR = ROOT / "attributes"
QS = json.load(open(ROOT / "questions.json"))["questions"]
QBYID = {q["id"]: q for q in QS}


def _load_all():
    out = []
    for f in os.listdir(ATTR):
        if f.endswith(".json"):
            try:
                out.append(json.load(open(ATTR / f)))
            except Exception:
                pass
    return out


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


def score_company(d, answers):
    """会社1社の(正規化スコア, 一致根拠list)。適用重み0なら(0, [])。"""
    wsum = 0.0
    acc = 0.0
    matched = []
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
            if not av:
                continue
            m = _closeness(_avg_band(av["value"]), target)
            acc += w * m; wsum += w
            if m >= 0.75:
                matched.append(f"年収志向に合致(平均年収{av['value']}万円)")

        elif kind == "salary_start":
            target = opts[0].get("target")
            if target is None:
                continue
            st = facts.get("starting_salary")
            if not st:
                continue
            m = _closeness(_start_band(st["value"]), target)
            acc += w * m; wsum += w
            if m >= 0.75:
                matched.append(f"初任給重視に合致(初任給{st['value']:,}円)")

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
        return 0.0, []
    return acc / wsum, matched


def _why(q, opt):
    return f"{q['text'].rstrip('？?')}→「{opt['label']}」に合致"


def _rationale(d, matched):
    facts = d.get("facts", {})
    r = {"trend": d.get("trend_note", ""), "matched": matched[:4], "facts": {}}
    av = facts.get("avg_salary")
    if av:
        r["facts"]["avg_salary"] = {"text": f"平均年収 約{av['value']}万円", "source": av["evidence"].get("source_url", ""),
                                    "as_of": av.get("as_of", "")}
    st = facts.get("starting_salary")
    if st:
        r["facts"]["starting_salary"] = {"text": f"初任給 {st['value']:,}円/月", "source": st["evidence"].get("source_url", "")}
    return r


def recommend(answers, top_companies=8, top_industries=5):
    rows = _load_all()
    scored = []
    for d in rows:
        s, matched = score_company(d, answers)
        scored.append((s, matched, d))
    scored.sort(key=lambda x: x[0], reverse=True)

    # 企業おすすめ
    comps = []
    for s, matched, d in scored[:top_companies]:
        comps.append({"name": d["name"], "slug": d["slug"], "industry": d["industry"],
                      "score": round(s, 3), "rationale": _rationale(d, matched)})

    # 業界おすすめ = 所属企業スコアの集計(平均)。有効スコア(適用重み>0)社のみ。
    ind_acc = {}
    for s, matched, d in scored:
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
