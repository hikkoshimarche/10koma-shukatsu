#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_industry.py — 1業界の画像完成社を本番D1へ反映(wave並走安全)。

各社: 画像公開(public/imagesへcopy+pathspec commit) → scenario_to_panels --v4(lint0ゲート内蔵)
      → migration → wrangler INSERT → before-keys一般化canary(wave新規INSERT誤検知なし) → 200検証。
公開URLは既設sheetsync(毎時)が自動起票。画像未完社・旧ChatGPT社は除外(404防止)。
使い方: deploy_industry.py "電機・精密・重工" [--limit N]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOK / "scripts"))
import phase_c_autoloop as A   # noqa: E402 (env)
import deploy_salary as D      # noqa: E402
import company_master as cm    # noqa: E402

TPY = str(TOK / ".venv" / "bin" / "python")
OUT = TOK / "output"
PUB = REPO / "public" / "images"


def imaged_ok(slug):
    import json
    d = OUT / slug
    if len(list(d.glob("koma*.png"))) < 10 or not (d / "qa_report.json").exists():
        return False
    try:
        r = json.load(open(d / "qa_report.json", encoding="utf-8"))
        return len(r.get("results", [])) >= 10 and all(x.get("ok") for x in r["results"])
    except Exception:
        return False


def publish_and_commit(slugs, industry):
    paths = []
    for s in slugs:
        (PUB / s).mkdir(parents=True, exist_ok=True)
        for k in range(1, 11):
            src = OUT / s / f"koma{k:02d}.png"
            if src.exists():
                shutil.copy2(src, PUB / s / f"panel_{k:02d}.png")
        paths.append(f"public/images/{s}")
    # pathspec commit: 指定パスのみcommit(wave同時stageと混ざらない)
    subprocess.run(["git", "add"] + paths, cwd=str(REPO), capture_output=True)
    subprocess.run(["git", "commit", "-m", f"feat({industry}): 画像公開(D1投入用)", "--"] + paths,
                   cwd=str(REPO), capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=str(REPO),
                         capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO), capture_output=True)
    return sha


def gen_sql(slug, ref):
    sqlp = f"/tmp/mig_ind_{slug}.sql"
    p = subprocess.run([TPY, "scripts/scenario_to_panels.py", "--slug", slug, "--ref", ref,
                        "--out", sqlp, "--v4", "--no-schema"], cwd=str(TOK),
                       capture_output=True, text=True, timeout=120)
    return (p.returncode == 0, sqlp, (p.stderr or p.stdout)[-200:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("industry")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    comps = cm.companies_in_industry(args.industry)
    d1 = {r["id"] for r in D.d1_query("SELECT id FROM companies")}
    ready = [c["slug"] for c in comps if c["slug"] not in d1 and imaged_ok(c["slug"])]
    skipped = [c["slug"] for c in comps if c["slug"] not in d1 and not imaged_ok(c["slug"])]
    if args.limit:
        ready = ready[:args.limit]
    print(f"=== {args.industry}: {len(comps)}社 / 投入可(画像完成){len(ready)} / 画像未完skip{len(skipped)} ===")
    if not ready:
        print("投入可なし"); return 0

    print("\n[1] 画像公開 + commit")
    sha = publish_and_commit(ready, args.industry)
    print(f"  sha={sha}")

    print("\n[2] SQL生成(lint0ゲート)")
    todo = []
    for s in ready:
        ok, sqlp, msg = gen_sql(s, sha)
        print(f"  {s:22} {'✅' if ok else '❌ '+msg}")
        if ok:
            todo.append((s, sqlp))
    if not todo:
        print("lint通過なし"); return 1

    targets = {s for s, _ in todo}
    print(f"\n[3] canary before (対象外スナップショット)")
    cb = D.canary_snapshot(targets)

    print("[4] D1 INSERT(migration)")
    for s, sqlp in todo:
        proc = D.wrangler(["--file", sqlp])
        print(f"  {s:22} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:120]}")

    ca = D.canary_snapshot(targets)
    changed = [s for s in cb if cb[s] != ca.get(s)]   # before-keysのみ=wave新規INSERT無視
    print(f"\n[5] canary after: 反映前存在の対象外変化={changed or 'なし(全不変)'}")
    if changed:
        print("  🛑 対象外変化 → 異常"); return 2

    print("\n[6] 200検証")
    ng = []
    for s, _ in todo:
        try:
            j = requests.get(f"{D.API_BASE}/api/companies/{s}", timeout=30).json()
            ok = len(j.get("panels", [])) == 10
            if not ok:
                ng.append(s)
        except Exception:
            ng.append(s)
    print(f"  200(panels=10): {len(todo)-len(ng)}/{len(todo)}  NG={ng or 'なし'}")
    print(f"\n✅ {args.industry}: {len(todo)-len(ng)}社 本番投入 (公開URLは毎時sheetsyncが起票)")
    if skipped:
        print(f"   画像未完 {len(skipped)}社は据置(Gemini生成待ち): {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
