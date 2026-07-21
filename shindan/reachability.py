#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/reachability.py — 全社到達性テスト。

回答パターンを網羅的にシミュレーションし、400社それぞれが「どこかのパターンで
おすすめ上位(top-N)に登場するか」を実測。一度も登場しない社と原因を出し、
多様性補正(max_per_industry)の before/after 到達率を報告 → reachability_report.md。

方式:
 (A) 各社の「理想回答」プローブ: その社の属性に最も一致する回答を作り、top-Nに入るか。
 (B) 大規模ランダムサンプリング: N_RANDOM 件のランダム回答でtop-Nを集計。
 到達 = (A)∪(B) で一度でもtop-Nに入った社。
"""
import json, os, random
from pathlib import Path
import matching

ROOT = Path(__file__).resolve().parent
Q = matching.QS
TOPN = 10
N_RANDOM = 4000
random.seed(42)   # 決定論(再現可能)


def ideal_answer(d):
    """会社dの属性に最も一致する回答パターンを構築。"""
    ans = {}
    soft = d.get("soft", {}); facts = d.get("facts", {})
    for q in Q:
        k = q["kind"]; qid = q["id"]; opts = q["options"]
        if k == "soft":
            v = soft.get(q["attr"], {}).get("value")
            if not isinstance(v, int):
                continue
            best, bd = None, 99
            for i, o in enumerate(opts):
                t = o.get("target")
                if t is None:
                    continue
                if abs(t - v) < bd:
                    bd = abs(t - v); best = i
            if best is not None:
                ans[qid] = best
        elif k == "salary_wlb":
            av = facts.get("avg_salary")
            if av and matching._avg_band(av["value"]) >= 4:
                ans[qid] = 0        # 高年収側
            else:
                rf = soft.get("remote_flex", {}).get("value")
                if isinstance(rf, int) and rf >= 4:
                    ans[qid] = 4     # WLB側
        elif k == "bunri":
            v = soft.get("bunri", {}).get("value")
            for i, o in enumerate(opts):
                if o.get("target") == v:
                    ans[qid] = i; break
        elif k == "tags":
            have = set(soft.get("job_tags", {}).get("value") or [])
            picks = [i for i, o in enumerate(opts) if o.get("target") and set(o["target"]) & have]
            if picks:
                ans[qid] = picks[:2]
        elif k == "industry":
            for i, o in enumerate(opts):
                if o.get("target") and d["industry"] in o["target"]:
                    ans[qid] = [i]; break
    return ans


def random_answer():
    ans = {}
    for q in Q:
        if random.random() < 0.25:      # 一部は無回答(欠損)
            continue
        opts = q["options"]
        if q.get("multi"):
            k = random.randint(1, 2)
            ans[q["id"]] = random.sample(range(len(opts)), min(k, len(opts)))
        else:
            ans[q["id"]] = random.randrange(len(opts))
    return ans


def measure(topn=TOPN, tiebreak_eps=0.0):
    rows = matching._load_all()
    seen = set()
    kw = {"top_companies": topn, "tiebreak_eps": tiebreak_eps}
    # (A) 理想プローブ
    for d in rows:
        for c in matching.recommend(ideal_answer(d), **kw)["top_companies"]:
            seen.add(c["slug"])
    # (B) ランダム
    for _ in range(N_RANDOM):
        for c in matching.recommend(random_answer(), **kw)["top_companies"]:
            seen.add(c["slug"])
    return seen, rows


def cause(d, seen_ideal):
    """未登場社の原因推定。"""
    if d["slug"] not in seen_ideal:
        # 理想回答でも登場しない=同業により強い同型社に支配されている
        return "同業のより高スコア社に支配(strictly dominated)"
    return "ランダム空間では出にくいが理想回答では登場(ニッチ)"


def main():
    rows = matching._load_all()
    total = len(rows)

    # BEFORE(補正なし=tiebreakなし)
    seen_b, _ = measure(tiebreak_eps=0.0)
    # 理想プローブのみの到達(原因分析用・tiebreakなし)
    seen_ideal = set()
    for d in rows:
        for c in matching.recommend(ideal_answer(d), top_companies=TOPN, tiebreak_eps=0.0)["top_companies"]:
            seen_ideal.add(c["slug"])

    # AFTER(補正=決定論tie-breaker eps=0.01)
    seen_a, _ = measure(tiebreak_eps=0.01)

    never_b = [d for d in rows if d["slug"] not in seen_b]
    never_a = [d for d in rows if d["slug"] not in seen_a]

    L = ["# shindan 全社到達性レポート", "",
         f"- top-N = **{TOPN}** / ランダム試行 = **{N_RANDOM}** + 理想プローブ400 / seed=42(決定論)", "",
         "## 到達率 before / after", "",
         "| 条件 | 登場社数 | 到達率 |", "|---|---|---|",
         f"| before(補正なし・純スコア順/同点は固定順) | {len(seen_b)} | **{len(seen_b)*100//total}%** ({len(seen_b)}/{total}) |",
         f"| after(決定論tie-breaker eps=0.01) | {len(seen_a)} | **{len(seen_a)*100//total}%** ({len(seen_a)}/{total}) |",
         "", f"改善: +{len(seen_a)-len(seen_b)}社", "",
         f"## before の未登場社 — {len(never_b)}社", ""]
    # 業界別の未登場数
    from collections import Counter
    cb = Counter(d["industry"] for d in never_b)
    L += ["未登場の業界内訳(before): " + " / ".join(f"{k}:{v}" for k, v in cb.most_common()), ""]
    for d in sorted(never_b, key=lambda x: x["industry"]):
        L.append(f"- {d['name']}（{d['industry']}）— {cause(d, seen_ideal)}")
    L += ["", f"## after(補正後) の未登場社 — {len(never_a)}社", ""]
    ca = Counter(d["industry"] for d in never_a)
    if never_a:
        L += ["未登場の業界内訳(after): " + " / ".join(f"{k}:{v}" for k, v in ca.most_common()), ""]
        for d in sorted(never_a, key=lambda x: x["industry"]):
            L.append(f"- {d['name']}（{d['industry']}）— {cause(d, seen_ideal)}")
    else:
        L.append("**なし＝全社に登場チャンスあり(100%)を達成** 🎉")
    (ROOT / "reachability_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"before {len(seen_b)}/{total} ({len(seen_b)*100//total}%) → after {len(seen_a)}/{total} ({len(seen_a)*100//total}%)")
    print(f"未登場 before={len(never_b)} after={len(never_a)}")
    print("→ reachability_report.md")


if __name__ == "__main__":
    main()
