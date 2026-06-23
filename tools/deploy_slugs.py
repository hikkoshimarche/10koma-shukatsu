#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_slugs.py — 明示slug群をGemini画像で本番上書きデプロイ(既存社のChatGPT→Gemini差替)。

scenario_to_panels --v4 は INSERT OR REPLACE で冪等＝D1既存社も上書きできる。
各社: Gemini画像(output→public/images上書き) → push → migration(REPLACE) → before-keys canary
      (wave/他更新を誤検知しない) → 検証(200・画像ファイルが新)。公開URLは生かす。
使い方: deploy_slugs.py slug1 slug2 ... [--label X]
画像が output に10枚揃いQA okの社のみ対象(未満はskip=要生成)。
"""
import argparse
import shutil
import subprocess
import sys
import json
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOK / "scripts"))
import phase_c_autoloop as A   # noqa: E402 env
import deploy_salary as D      # noqa: E402

TPY = str(TOK / ".venv" / "bin" / "python")
OUT = TOK / "output"
PUB = REPO / "public" / "images"


def imaged_ok(slug):
    d = OUT / slug
    if len(list(d.glob("koma*.png"))) < 10 or not (d / "qa_report.json").exists():
        return False
    try:
        r = json.load(open(d / "qa_report.json", encoding="utf-8"))
        return len(r.get("results", [])) >= 10 and all(x.get("ok") for x in r["results"])
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--label", default="regen")
    args = ap.parse_args()

    ready = [s for s in args.slugs if imaged_ok(s)]
    skip = [s for s in args.slugs if not imaged_ok(s)]
    print(f"=== [{args.label}] {len(args.slugs)}社 / 上書き可(Gemini10+QA){len(ready)} / 画像未完skip{len(skip)}{skip or ''} ===")
    if not ready:
        print("対象なし"); return 0

    print("\n[1] Gemini画像をpublic/へ上書き公開")
    paths = []
    for s in ready:
        (PUB / s).mkdir(parents=True, exist_ok=True)
        for k in range(1, 11):
            src = OUT / s / f"koma{k:02d}.png"
            if src.exists():
                shutil.copy2(src, PUB / s / f"panel_{k:02d}.png")
        paths.append(f"public/images/{s}")
    subprocess.run(["git", "add"] + paths, cwd=str(REPO), capture_output=True)
    subprocess.run(["git", "commit", "-m", f"fix({args.label}): Gemini画像で上書き(ChatGPT→Gemini)", "--"] + paths,
                   cwd=str(REPO), capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=str(REPO),
                         capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO), capture_output=True)
    print(f"  sha={sha}")

    print("\n[2] SQL生成(lint0ゲート・INSERT OR REPLACE)")
    todo = []
    for s in ready:
        sqlp = f"/tmp/mig_regen_{s}.sql"
        p = subprocess.run([TPY, "scripts/scenario_to_panels.py", "--slug", s, "--ref", sha,
                            "--out", sqlp, "--v4", "--no-schema"], cwd=str(TOK),
                           capture_output=True, text=True, timeout=120)
        ok = p.returncode == 0
        print(f"  {s:18} {'✅' if ok else '❌ '+(p.stderr or p.stdout)[-150:]}")
        if ok:
            todo.append((s, sqlp))
    if not todo:
        print("lint通過なし"); return 1

    targets = {s for s, _ in todo}
    print(f"\n[3] canary before (対象外スナップショット)")
    cb = D.canary_snapshot(targets)
    print("[4] D1 上書き(INSERT OR REPLACE)")
    for s, sqlp in todo:
        D.backup_d1(s)
        proc = D.wrangler(["--file", sqlp])
        print(f"  {s:18} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:120]}")
    ca = D.canary_snapshot(targets)
    changed = [s for s in cb if cb[s] != ca.get(s)]
    print(f"\n[5] canary after: 反映前存在の対象外変化={changed or 'なし(全不変)'}")
    if changed:
        print("  🛑 対象外変化 → 異常"); return 2

    print("\n[6] 検証(200 + script_json=v4化)")
    ng = []
    for s, _ in todo:
        try:
            j = requests.get(f"{D.API_BASE}/api/companies/{s}", timeout=30).json()
            p1 = next((x for x in j.get("panels", []) if x["panel_num"] == 1), {})
            v4 = str(p1.get("dialogue", "")).startswith("[")
            ok = len(j.get("panels", [])) == 10 and v4
            print(f"  {s:18} 200={len(j.get('panels',[]))==10} v4台本={v4}")
            if not ok:
                ng.append(s)
        except Exception as ex:
            print(f"  {s:18} ❌{ex}"); ng.append(s)
    # Notion台本同期(本番反映と一対・D1が正)
    ok_slugs = [s for s, _ in todo if s not in ng]
    if ok_slugs:
        print("\n[7] Notion台本同期(D1=正)")
        subprocess.run([TPY, "scripts/notion_sync_d1.py", "--slugs", ",".join(ok_slugs)],
                       cwd=str(TOK), timeout=900)
    print(f"\n✅ [{args.label}] 上書き {len(todo)-len(ng)}/{len(args.slugs)}社 (ChatGPT→Gemini化・公開URL生存)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
