#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""overnight_wave.py — デプロイ可業界(既存industry_id)を自動でwave処理。

各業界: 画像生成(drive_images_industry) → public/images公開+commit+push → D1投入(deploy_bank
--v4ゲート+一般化canary+API) → 記録。Geminiクレジット切れで画像段階停止(以降は台本+画像済のみ
デプロイし、未画像は朝へ)。新id業界(industries行なし)は対象外。三井含む既存社除外。
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, "/Users/oscardodds/oscar-ai/tokyari-pipeline/scripts")
import phase_c_autoloop as A   # noqa: E402 env
import deploy_salary as D      # noqa: E402
import company_master as cm    # noqa: E402

TOK = Path("/Users/oscardodds/oscar-ai/tokyari-pipeline")
TPY = str(TOK / ".venv" / "bin" / "python")
OUT = TOK / "output"
PUB = REPO / "public" / "images"
LOG = REPO / ".backups" / f"overnight_{time.strftime('%Y%m%d')}.log"

# デプロイ可(既存industry_id)業界・小さい順
WAVE = ["専門商社", "航空・運輸・物流", "食品・飲料", "不動産・建設", "小売・流通", "広告・メディア", "IT・通信・SaaS"]


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M')}] {msg}\n")
    print(msg, flush=True)


def imaged_ok(slug):
    n = len(list((OUT / slug).glob("koma*.png")))
    qa = OUT / slug / "qa_report.json"
    if n < 10 or not qa.exists():
        return False
    try:
        r = json.load(open(qa, encoding="utf-8"))
        return len(r.get("results", [])) >= 10 and all(x.get("ok") for x in r["results"])
    except Exception:
        return False


def publish(slugs):
    n = 0
    for s in slugs:
        (PUB / s).mkdir(parents=True, exist_ok=True)
        for k in range(1, 11):
            src = OUT / s / f"koma{k:02d}.png"
            if src.exists():
                shutil.copy2(src, PUB / s / f"panel_{k:02d}.png"); n += 1
    return n


def git_push_images(industry):
    subprocess.run(["git", "add", "public/images/"], cwd=str(REPO), capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", f"feat(wave): {industry} 画像公開(D1投入用)"],
                   cwd=str(REPO), capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=str(REPO),
                         capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO), capture_output=True)
    return sha


def deploy(slugs, ref, label):
    proc = subprocess.run([TPY, "tools/deploy_bank.py", "--ref", ref, "--slugs", ",".join(slugs),
                          "--label", label], cwd=str(REPO), capture_output=True, text=True, timeout=2400)
    out = proc.stdout
    # canary異常検知
    drift = "🛑" in out or "対象外が変化" in out
    # 投入数
    inv = 0
    for line in out.splitlines():
        if line.strip().startswith("投入 "):
            try:
                inv = int(line.split("投入")[1].split("/")[0].strip())
            except Exception:
                pass
    ng = "ライブNG: ['" in out
    return inv, drift, ng, out


def main():
    d1 = {r["id"] for r in D.d1_query("SELECT id FROM companies")}
    credits_stopped = False
    for ind in WAVE:
        comps = cm.companies_in_industry(ind)
        todo = [c["slug"] for c in comps if c["slug"] not in d1]
        if not todo:
            log(f"[{ind}] 全社D1済 skip"); continue
        log(f"=== [{ind}] 開始 {len(comps)}社 / 未投入{len(todo)} ===")

        # 1. 画像生成(冪等・クレジット切れstop)
        if not credits_stopped:
            p = subprocess.run([TPY, "scripts/drive_images_industry.py", ind],
                               cwd=str(TOK), capture_output=True, text=True, timeout=14400)
            if "STOPPED_CREDITS" in p.stdout:
                credits_stopped = True
                log(f"[{ind}] 🛑Geminiクレジット枯渇 → 以降は画像済のみデプロイ")

        # 2. 画像済(QA ok)かつ未投入 を抽出
        dep = [s for s in todo if imaged_ok(s)]
        nodep = [s for s in todo if not imaged_ok(s)]
        if not dep:
            log(f"[{ind}] 画像済0 → デプロイなし(未画像{len(nodep)}は朝へ)")
            if credits_stopped:
                break
            continue

        # 3. 公開 + push
        publish(dep)
        sha = git_push_images(ind)

        # 4. デプロイ(pilot3 → 残り)。pilotで異常なら業界停止
        pilot = dep[:3]; rest = dep[3:]
        inv_p, drift_p, ng_p, _ = deploy(pilot, sha, f"{ind}-pilot")
        if drift_p:
            log(f"[{ind}] 🛑pilot canary異常 → 業界停止・記録(次業界へ)"); continue
        log(f"[{ind}] pilot {inv_p}/{len(pilot)}投入" + (" (一部gate却下/未投入)" if inv_p < len(pilot) else ""))
        inv_r = 0
        if rest:
            inv_r, drift_r, ng_r, _ = deploy(rest, sha, f"{ind}-rest")
            if drift_r:
                log(f"[{ind}] 🛑rest canary異常 → 業界停止"); continue
        # 最終確認
        d1 = {r["id"] for r in D.d1_query("SELECT id FROM companies")}
        live = sum(1 for c in comps if c["slug"] in d1)
        log(f"[{ind}] 完了: D1 {live}/{len(comps)} (今回投入{inv_p+inv_r}/{len(dep)}, gate却下/未画像は保留) sha={sha}")

        if credits_stopped:
            log("クレジット枯渇のため画像未済業界は朝へ。wave終了。"); break

    log("=== overnight_wave 終了 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
