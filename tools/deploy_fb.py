#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_fb.py — attention(FB対応中)のkoma別FBを通常ゲートで本番反映+書き戻し。

各社: triage→koma別台本バグを修正(非dry)→lint error0→台本列UPDATE(image_url不変)→
      canary確認→API検証→書き戻し(反映済)。三井除外・backup可逆。
書き戻しは『その社のFBが全て解消(エスカレーションなし)』の社のみ。
koma不明(例:全社共通『静かに削除』)はエスカレーションとして分離(別途step2)。
"""
import json
import sys
import urllib.parse
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import deploy_salary as D        # noqa: E402
import phase_c_autoloop as A     # noqa: E402

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
        triage = L.triage_fb(company, it.get("fb", ""))
        changed, escalate = [], []
        from collections import OrderedDict
        by_koma = OrderedDict()
        for b in triage.get("script_bugs", []):
            koma = b.get("koma")
            if not koma:
                escalate.append(f"台本:{b.get('detail','')[:40]}"); continue
            by_koma.setdefault(koma, []).append(b.get("detail", ""))
        for koma, details in by_koma.items():
            instr = "このコマへの指摘(全て反映):\n" + "\n".join(f"- {d}" for d in details)
            res = L.fix_script_koma(slug, koma, instr, rules, dry=False)
            if res.get("changed"):
                changed.append(koma)
        # 画像バグは現状エスカレーション(画像再生成はGemini/別工程)
        for b in triage.get("image_bugs", []):
            escalate.append(f"画像koma{b.get('koma','?')}:{b.get('detail','')[:30]}")
        e, w, _ = L.lint_company(slug)
        recs.append({"company": company, "slug": slug, "changed": changed,
                     "escalate": escalate, "lint": (e, w)})
        print(f"  {company:8}({slug:14}) 変更koma={changed} lint:err={e},warn={w} escalate={len(escalate)}")

    deployable = [r for r in recs if r["changed"] and r["lint"][0] == 0]
    print(f"\n→ deploy対象: {[r['slug'] for r in deployable]}")
    if not deployable:
        print("deploy対象なし"); return 0

    print("\n[canary before]")
    c_before = D.canary_hash()
    print(f"  {D.CANARY} = {c_before}")

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

    c_after = D.canary_hash()
    print(f"\n[canary after] {D.CANARY} = {c_after} {'✅不変' if c_after==c_before else '⚠️変化!'}")

    print("\n[API検証]")
    for r in deployable:
        try:
            jr = requests.get(f"{D.API_BASE}/api/companies/{r['slug']}", timeout=30).json()
            print(f"  {r['slug']:14} API200 panels={len(jr.get('panels',[]))} 変更koma={r['changed']}")
        except Exception as ex:
            print(f"  {r['slug']:14} 検証失敗 {ex}")

    print("\n[書き戻し 反映済] ※エスカレーション(静かに)が残る社は保留")
    for r in deployable:
        if r["escalate"]:
            print(f"  {r['slug']:14} 保留(静かに残件 {len(r['escalate'])}件→step2後に反映済)")
            continue
        res = gas({"mode": "setreflected", "company": r["company"]})
        print(f"  {r['slug']:14} 反映済セット: {res}")

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
