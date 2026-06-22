#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_bank.py — 銀行未投入社を --v4ゲート経由でD1投入(本番ゲート)。

各社: scenario_to_panels.py --v4 (lint error0ゲート内蔵) → migration SQL生成 →
      wrangler d1 execute --remote(api/wrangler.toml) → 本番API 200確認。
一般化canary: 今回対象"以外"の既存全社hash不変。三井除外は無関係(銀行のみ)。
使い方: deploy_bank.py --ref <sha> --slugs a,b,c
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_autoloop as A  # noqa: E402 (env)
import deploy_salary as D     # noqa: E402

TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
TPY = str(TOKYARI / ".venv" / "bin" / "python")


def gen_sql(slug, ref):
    """scenario_to_panels --v4 でSQL生成(lint error0ゲート内蔵)。(ok, sqlpath, msg)。"""
    sqlp = f"/tmp/mig_bank_{slug}.sql"
    proc = subprocess.run(
        [TPY, "scripts/scenario_to_panels.py", "--slug", slug, "--ref", ref,
         "--out", sqlp, "--v4", "--no-schema"],
        cwd=str(TOKYARI), capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return False, sqlp, f"scenario_to_panels失敗(lint error?): {(proc.stderr or proc.stdout)[-200:]}"
    return True, sqlp, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--slugs", required=True, help="カンマ区切り")
    ap.add_argument("--label", default="bank")
    args = ap.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]

    print(f"=== 銀行D1投入 [{args.label}] {len(slugs)}社 ref={args.ref} ===")
    print("\n[1] SQL生成 + lintゲート")
    ready = []
    for slug in slugs:
        ok, sqlp, msg = gen_sql(slug, args.ref)
        print(f"  {slug:18} {'✅SQL生成(lint0)' if ok else '❌ '+msg}")
        if ok:
            ready.append((slug, sqlp))
    if not ready:
        print("デプロイ可なし"); return 1

    print("\n[2] canary before (対象以外の全社)")
    targets = {s for s, _ in ready}
    cb = D.canary_snapshot(targets)
    print(f"  対象外 {len(cb)}社を監視")

    print("\n[3] D1 migration 実行(remote)")
    for slug, sqlp in ready:
        proc = D.wrangler(["--file", sqlp], timeout=120)
        print(f"  {slug:18} {'✅投入' if proc.returncode==0 else '❌ '+proc.stderr[:150]}")

    print("\n[4] canary after")
    ca = D.canary_snapshot(targets)
    drift = D.canary_diff(cb, ca)
    if drift:
        print(f"  🛑 対象外が変化: {drift} → 異常!調査要")
        return 2
    print(f"  対象外 {len(ca)}社 全hash不変 ✅")

    print("\n[5] 本番API 200確認(LIFFライブ)")
    ng = []
    for slug, _ in ready:
        try:
            r = requests.get(f"{D.API_BASE}/api/companies/{slug}", timeout=30)
            j = r.json()
            ok = r.status_code == 200 and j.get("name") and len(j.get("panels", [])) == 10
            print(f"  {slug:18} {'✅200 '+str(j.get('name'))+' panels='+str(len(j.get('panels',[]))) if ok else '❌ '+str(r.status_code)}")
            if not ok:
                ng.append(slug)
        except Exception as ex:
            print(f"  {slug:18} ❌ {ex}"); ng.append(slug)
    print(f"\n投入 {len(ready)-len(ng)}/{len(slugs)}  ライブNG: {ng or 'なし'}")
    return 0 if not ng else 3


if __name__ == "__main__":
    raise SystemExit(main())
