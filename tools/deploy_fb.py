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


def main():
    _load_env()
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")
    items = [it for it in A.fetch_attention() if it.get("content") == "10コマ"]
    print(f"=== 4社FB 本番反映 (対象 {len(items)}社・三井除外) ===\n")

    recs = []
    for it in items:
        company = it.get("company", "")
        slug = A.resolve_slug(company)
        if not slug or slug in A.L.EXCLUDED_SLUGS:
            print(f"  {company}: skip(slug={slug})"); continue
        fb_raw = it.get("fb", "")
        triage = L.triage_fb(company, fb_raw)
        changed, escalate, investigate = [], [], []
        from collections import OrderedDict
        by_koma = OrderedDict()
        for b in triage.get("script_bugs", []):
            koma = b.get("koma")
            detail = b.get("detail", "")
            concern = classify_concern(detail)
            if concern == "preference":
                # 真にオスカー判断(好み/トーン/方向性)のみ → 要判断(オスカー)へ
                escalate.append(f"要判断(好み/方向性): koma{koma or '?'} {detail[:40]}")
                continue
            if concern == "factcheck":
                # 事実確認/調査系 → オスカーに戻さず Claude裏取りで反映を試みる(取れなければ据置)。
                # 数字捏造はfix_script_koma側ルール(出典なき数字禁止)で防止。
                investigate.append(f"要調査(Claude裏取り): koma{koma or '?'} {detail[:40]}")
                if koma:
                    by_koma.setdefault(koma, []).append("【要調査=公式/有報で裏取りの上、取れた事実のみ反映。"
                                                        "取れなければ現行維持】" + detail)
                continue
            if not koma:
                escalate.append(f"台本:{detail[:40]}"); continue
            by_koma.setdefault(koma, []).append(detail)
        factcheck_komas = {int(re.search(r"koma(\d+)", s).group(1))
                           for s in investigate if re.search(r"koma(\d+)", s)}
        for koma, details in by_koma.items():
            instr = "このコマへの指摘(全て反映):\n" + "\n".join(f"- {d}" for d in details)
            res = L.fix_script_koma(slug, koma, instr, rules, dry=False)
            if res.get("changed"):
                changed.append(koma)
        # 裏取りできず未変更の要調査koma = 据置(オスカーには出さない)
        unresolved = sorted(factcheck_komas - set(changed))
        # 画像バグは現状エスカレーション(画像再生成はGemini/別工程)
        for b in triage.get("image_bugs", []):
            escalate.append(f"画像koma{b.get('koma','?')}:{b.get('detail','')[:30]}")
        e, w, _ = L.lint_company(slug)
        recs.append({"company": company, "slug": slug, "changed": changed,
                     "escalate": escalate, "investigate": investigate,
                     "unresolved": unresolved, "lint": (e, w)})
        print(f"  {company:8}({slug:14}) 変更koma={changed} 要調査{len(investigate)}(未解決koma{unresolved}) "
              f"lint:err={e},warn={w} escalate={len(escalate)}")

    deployable = [r for r in recs if r["changed"] and r["lint"][0] == 0]
    print(f"\n→ deploy対象: {[r['slug'] for r in deployable]}")
    if not deployable:
        print("deploy対象なし"); return 0

    target_slugs = {r["slug"] for r in deployable}
    print("\n[canary before] 一般化: 対象外の全社をhash監視")
    c_before = D.canary_snapshot(target_slugs)
    print(f"  対象外 {len(c_before)}社を監視 (対象={sorted(target_slugs)})")

    print("\n[backup + UPDATE 台本列(image_url不変)]")
    for r in deployable:
        D.backup_d1(r["slug"])
        for koma in r["changed"]:
            sql = A.L.parse_migration_sql(r["slug"])
            panel = next(x for x in sql["panels"] if x["panel_num"] == koma)
            after = {"script": json.loads(panel["script_json"] or "[]"),
                     "main_copy": panel["main_copy"], "sub_copy": panel["sub_copy"]}
            proc = D.wrangler(["--command", D.update_sql(r["slug"], koma, after)])
            print(f"  {r['slug']:14} koma{koma} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:100]}")

    c_after = D.canary_snapshot(target_slugs)
    drift = D.canary_diff(c_before, c_after)
    if drift:
        print(f"\n[canary after] 🛑 対象外が変化: {drift} → 異常!即停止。書き戻しせず手動確認を。")
        gas({"mode": "addcommonfix", "rule": f"[CANARY異常] 対象外社が変化: {drift} (要調査)", "scope": "system"})
        return 2
    print(f"\n[canary after] 対象外 {len(c_after)}社 全hash不変 ✅ (他社を壊していない)")

    print("\n[API検証]")
    for r in deployable:
        try:
            jr = requests.get(f"{D.API_BASE}/api/companies/{r['slug']}", timeout=30).json()
            print(f"  {r['slug']:14} API200 panels={len(jr.get('panels',[]))} 変更koma={r['changed']}")
        except Exception as ex:
            print(f"  {r['slug']:14} 検証失敗 {ex}")

    # 書き戻し(必須): AIが触ったらスプシが必ず動く。
    #  - escalate(好み/方向性=要判断オスカー or koma不明/画像) を含む → setescalated。
    #  - 要調査(factcheck)が裏取りできず未解決 → 据置(FB対応中のまま・オスカーには出さない)+要調査ログ。
    #  - 上記なく台本deploy済 → setreflected(反映済+N次完了)。
    print("\n[書き戻し]")
    for r in recs:
        deployed = r["slug"] in {d["slug"] for d in deployable}
        if r["escalate"]:
            res = gas({"mode": "setescalated", "company": r["company"],
                       "reason": "; ".join(r["escalate"][:3])})
            print(f"  {r['slug']:14} 要判断(オスカー): {res}")
        elif r.get("unresolved"):
            # 事実確認が取れず未解決 → オスカーに出さず据置。要調査キューに記録のみ。
            gas({"mode": "addcommonfix",
                 "rule": f"[要調査] {r['company']} koma{r['unresolved']}: 公式/有報で裏取り要(取れたら反映)",
                 "scope": "system", "note": "; ".join(r.get("investigate", [])[:3])})
            print(f"  {r['slug']:14} 据置(要調査koma{r['unresolved']}・オスカー非通知)")
        elif deployed:
            res = gas({"mode": "setreflected", "company": r["company"]})
            print(f"  {r['slug']:14} 反映済: {res}")

    # LINEレポート(プレビュー)。実際の定時LINEはGAS line3hSummaryが反映済を読んで送る
    reflected = [r for r in deployable if not r["escalate"]]
    esc = [r for r in recs if r["escalate"]]
    print("\n=== LINEレポート(プレビュー) ===")
    lines = [f"【トーキャリ自動修正】台本反映 {len(reflected)}社 / 要対応(手動) {len(esc)}社"]
    for r in reflected:
        lines.append(f"・{r['company']}: koma{r['changed']} 反映済")
    for r in esc:
        lines.append(f"⚠{r['company']}: {'; '.join(r['escalate'][:2])}")
    print("\n".join(lines))
    print("\n完了。巻き戻しは .backups/d1_*.json から。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
