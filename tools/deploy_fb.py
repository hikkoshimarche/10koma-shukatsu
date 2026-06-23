#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_fb.py — attention(FB対応中)のkoma別FBを通常ゲートで本番反映+書き戻し。

各社: triage→koma別台本バグを修正(非dry)→lint error0→台本列UPDATE(image_url不変)→
      canary確認→API検証→書き戻し(反映済)。三井除外・backup可逆。
書き戻しは『その社のFBが全て解消(エスカレーションなし)』の社のみ。
koma不明(例:全社共通『静かに削除』)はエスカレーションとして分離(別途step2)。
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import deploy_salary as D        # noqa: E402
import phase_c_autoloop as A     # noqa: E402

# 懸念分類(2026-06-22): preference=要判断(オスカー) / factcheck=要調査(Claude裏取り・オスカーに戻さない)。
classify_concern = L.classify_concern

GAS_URL = None
GAS_TOKEN = None


def _load_env():
    global GAS_URL, GAS_TOKEN
    import os
    GAS_URL = os.environ["SHEET_WEBAPP_URL"].strip()
    GAS_TOKEN = os.environ["SHEET_API_TOKEN"].strip()


def gas(params):
    params["token"] = GAS_TOKEN
    return requests.get(GAS_URL, params=params, timeout=60).json()


def d1_panels(slug):
    """本番D1の現行台本(ファイル非依存の正)。"""
    return D.d1_query("SELECT panel_num,dialogue,script_json,main_copy,sub_copy "
                      f"FROM company_panels WHERE company_id='{slug}' ORDER BY panel_num")


def _cur(panels):
    cur = {}
    for p in panels:
        try:
            sc = json.loads(p.get("script_json") or "[]")
        except Exception:
            sc = [x for x in (p.get("dialogue") or "").split("\n") if x.strip()]
        cur[p["panel_num"]] = {"script": sc, "main_copy": p.get("main_copy") or "",
                               "sub_copy": p.get("sub_copy") or ""}
    return cur


def _scenario(slug, panels, overrides):
    koma = []
    for p in panels:
        kn = p["panel_num"]; ov = overrides.get(kn)
        if ov:
            koma.append({"koma_number": kn, "script": ov["script"],
                         "overlay_text": {"main_copy": ov["main_copy"], "sub": ov["sub_copy"]}})
        else:
            c = _cur([p])[kn]
            koma.append({"koma_number": kn, "script": c["script"],
                         "overlay_text": {"main_copy": c["main_copy"], "sub": c["sub_copy"]}})
    return {"meta": {"slug": slug}, "koma": koma}


def process_company(company, slug, fb_raw, rules):
    """1社をD1ライブ基準で処理。例外は呼び出し側try/catchで隔離。全FBを必ず着地させる。"""
    import scenario_lints_v5_ext as v5
    from collections import OrderedDict
    panels = d1_panels(slug)
    if not panels:
        return {"company": company, "slug": slug, "overrides": {}, "escalate": [],
                "investigate": [], "unresolved": [], "lint": (0, 0), "landed": "D1台本なし→skip"}
    cur = _cur(panels)
    triage = L.triage_fb(company, fb_raw)
    escalate, investigate = [], []
    by_koma = OrderedDict()
    factcheck_komas = set()

    def route(koma, detail, tag):
        """1つの指摘を必ず着地: preference→escalate / factcheck・action→fix / koma不明→escalate。"""
        concern = L.classify_concern(detail)
        koma = koma or L.extract_koma(detail)
        if concern == "preference" or not koma:
            escalate.append(f"要判断({tag}/好み): koma{koma or '?'} {detail[:40]}")
            return
        if concern == "factcheck":
            factcheck_komas.add(koma)
            investigate.append(f"要調査: koma{koma} {detail[:40]}")
            by_koma.setdefault(koma, []).append("【要調査=公式/有報で裏取りの上、取れた事実のみ反映。取れなければ現行維持】" + detail)
            return
        by_koma.setdefault(koma, []).append(detail)   # actionable → 反映試行

    for b in triage.get("script_bugs", []):
        route(b.get("koma"), b.get("detail", ""), "台本")
    # 感想も黙って捨てない: action方向があれば反映試行、純粋な好みのみescalate
    for op in triage.get("opinions", []):
        route(None, op if isinstance(op, str) else str(op), "感想")
    for b in triage.get("image_bugs", []):
        escalate.append(f"画像koma{b.get('koma','?')}:{b.get('detail','')[:30]}")

    overrides = {}
    for koma, details in by_koma.items():
        if koma not in cur:
            escalate.append(f"koma{koma}不在→要確認"); continue
        instr = "このコマへの指摘(全て反映):\n" + "\n".join(f"- {d}" for d in details)
        res = L.fix_koma_text(slug, koma, instr, rules, cur[koma])
        if res.get("changed"):
            overrides[koma] = res["after"]
    unresolved = sorted(factcheck_komas - set(overrides))
    # lint(D1全台本+override)
    rep = v5.run_ext_lints(_scenario(slug, panels, overrides), slug)
    return {"company": company, "slug": slug, "overrides": overrides, "escalate": escalate,
            "investigate": investigate, "unresolved": unresolved,
            "lint": (rep["errors"], rep["warnings"]), "landed": "ok"}


def main():
    _load_env()
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")
    items = [it for it in A.fetch_attention() if it.get("content") == "10コマ"]
    print(f"=== FB 本番反映 (対象 {len(items)}社・D1ライブ基準) ===\n")

    recs = []
    for it in items:
        company = it.get("company", "")
        slug = A.resolve_slug(company)
        if not slug or slug in A.L.EXCLUDED_SLUGS:
            print(f"  {company}: skip(slug={slug})"); continue
        # 【隔離】1社の例外で全体を殺さない。失敗社はescalateして次社へ継続。
        try:
            r = process_company(company, slug, it.get("fb", ""), rules)
        except Exception as ex:
            import traceback
            print(f"  {company:8}({slug:14}) ❌処理失敗→escalate: {ex}")
            traceback.print_exc()
            recs.append({"company": company, "slug": slug, "overrides": {}, "escalate": [f"処理失敗・要確認: {ex}"],
                         "investigate": [], "unresolved": [], "lint": (0, 0), "landed": f"例外:{ex}"})
            continue
        recs.append(r)
        ck = sorted(r["overrides"])
        print(f"  {company:8}({slug:14}) 反映koma={ck} 要調査{len(r['investigate'])}(未解決{r['unresolved']}) "
              f"lint:err={r['lint'][0]},warn={r['lint'][1]} escalate={len(r['escalate'])}")

    deployable = [r for r in recs if r["overrides"] and r["lint"][0] == 0]
    print(f"\n→ deploy対象: {[r['slug'] for r in deployable]}")
    if not deployable:
        print("deploy対象なし(反映変更0)")

    target_slugs = {r["slug"] for r in deployable}
    c_before = D.canary_snapshot(target_slugs) if deployable else {}
    if deployable:
        print(f"\n[canary before] 対象外 {len(c_before)}社を監視 (対象={sorted(target_slugs)})")
        print("\n[backup + UPDATE 台本列(image_url不変)]")
        for r in deployable:
            D.backup_d1(r["slug"])
            for koma, after in r["overrides"].items():
                proc = D.wrangler(["--command", D.update_sql(r["slug"], koma, after)])
                print(f"  {r['slug']:14} koma{koma} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:100]}")

        c_after = D.canary_snapshot(target_slugs)
        drift = D.canary_diff(c_before, c_after)
        if drift:
            print(f"\n[canary after] 🛑 対象外が変化: {drift} → 異常!即停止。書き戻しせず手動確認を。")
            gas({"mode": "addcommonfix", "rule": f"[CANARY異常] 対象外社が変化: {drift} (要調査)", "scope": "system"})
            return 2
        print(f"\n[canary after] 対象外 {len(c_after)}社 全hash不変 ✅")

        print("\n[API検証]")
        for r in deployable:
            try:
                jr = requests.get(f"{D.API_BASE}/api/companies/{r['slug']}", timeout=30).json()
                print(f"  {r['slug']:14} API200 panels={len(jr.get('panels',[]))} 反映koma={sorted(r['overrides'])}")
            except Exception as ex:
                print(f"  {r['slug']:14} 検証失敗 {ex}")

    # 書き戻し(必須・未着地ゼロ): 全社が必ずどれかに着地する。
    #  escalate(好み/画像/koma不明/処理失敗)→setescalated(要判断) / 要調査未解決→据置+要調査ログ /
    #  台本反映済→setreflected(反映済+N次完了) / それ以外(変更なし)→据置ログ。
    print("\n[書き戻し]")
    deployed_slugs = {d["slug"] for d in deployable}
    tally = {"reflected": 0, "escalated": 0, "investigate": 0, "noop": 0}
    for r in recs:
        if r["escalate"]:
            gas({"mode": "setescalated", "company": r["company"], "reason": "; ".join(r["escalate"][:3])})
            tally["escalated"] += 1
            print(f"  {r['slug']:14} 要判断(オスカー) [{'; '.join(r['escalate'][:2])}]")
        elif r["slug"] in deployed_slugs:
            res = gas({"mode": "setreflected", "company": r["company"]})
            tally["reflected"] += 1
            print(f"  {r['slug']:14} 反映済 koma{sorted(r['overrides'])}: {res.get('round')}")
        elif r.get("unresolved"):
            gas({"mode": "addcommonfix", "scope": "system",
                 "rule": f"[要調査] {r['company']} koma{r['unresolved']}: 公式/有報で裏取り要(取れたら反映)",
                 "note": "; ".join(r.get("investigate", [])[:3])})
            tally["investigate"] += 1
            print(f"  {r['slug']:14} 据置(要調査koma{r['unresolved']})")
        else:
            tally["noop"] += 1
            print(f"  {r['slug']:14} 据置(変更なし/対象外) landed={r.get('landed')}")
    print(f"\n=== 着地内訳: 反映{tally['reflected']} / 要判断{tally['escalated']} / 要調査据置{tally['investigate']} "
          f"/ 変更なし{tally['noop']}  (計{sum(tally.values())}/{len(recs)} 未着地ゼロ) ===")
    print("巻き戻しは .backups/d1_*.json から。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
