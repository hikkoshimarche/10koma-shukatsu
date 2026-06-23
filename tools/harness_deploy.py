#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness_deploy.py — 横展開の標準経路: 初稿 → persona_review(合成レビュー) → 自己修正反映
                       → lint=0 → deploy。電機・鉄鋼・製薬以降のデフォルト経路。

各社: persona_review.run(4人格→AI自己修正→factcheck裏取りキュー→lint) →
      自己修正overrideを scenario_v4.json に反映(初稿を底上げ) → deploy_slugs(Gemini画像で本番)。
人間レビュー面に出る初稿が既にクリーン。本番ゲート(v5_ext/canary/backup)は deploy_slugs 側で不変。
使い方: harness_deploy.py --slug X --company 社名 [--no-deploy]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
import persona_review as PR  # noqa: E402

TPY = str(TOK / ".venv" / "bin" / "python")


def apply_overrides_to_scenario(slug, overrides):
    """persona自己修正の overrides を scenario_v4.json に反映(script/overlay)。backup付き。"""
    p = TOK / "output" / slug / "scenario_v4.json"
    import shutil
    import time
    shutil.copy2(p, str(p) + f".bak_persona_{time.strftime('%Y%m%d_%H%M%S')}")
    sc = json.loads(p.read_text(encoding="utf-8"))
    for k in sc.get("koma", []):
        ov = overrides.get(k["koma_number"])
        if ov:
            k["script"] = ov["script"]
            ot = k.setdefault("overlay_text", {})
            ot["main_copy"] = ov["main_copy"]
            ot["sub"] = ov["sub_copy"]
    p.write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(overrides)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--no-deploy", action="store_true", help="persona_reviewと反映のみ(deployしない)")
    args = ap.parse_args()

    print(f"=== harness_deploy: {args.company} ({args.slug}) ===")
    print("\n[STAGE 1] persona_review(4人格合成レビュー → AI自己修正)")
    out = PR.run(args.slug, args.company)
    overrides = out["result"]["overrides"]

    print(f"\n[STAGE 2] 自己修正を初稿(scenario_v4.json)へ反映")
    if overrides:
        n = apply_overrides_to_scenario(args.slug, overrides)
        print(f"  {n}コマを初稿に反映(backup付き)")
    else:
        print("  反映なし(自己修正0)")

    print(f"\n[STAGE 3] lint確認: errors={out['lint']['errors']} "
          f"{'✅' if out['lint']['errors']==0 else '❌ deploy中止'}")
    if out["lint"]["errors"] > 0:
        print("  lint error → deployしない"); return 1

    if args.no_deploy:
        print("\n[STAGE 4] --no-deploy: deployスキップ")
        return 0
    print(f"\n[STAGE 4] deploy(Gemini画像で本番・lint/canary/backupゲート不変)")
    proc = subprocess.run([TPY, "tools/deploy_slugs.py", args.slug, "--label", "harness"],
                          cwd=str(REPO))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
