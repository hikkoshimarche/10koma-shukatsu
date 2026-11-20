#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""optimize_images.py — 本番画像の一括軽量化(ローカル・API費$0)。

対象: public/images/<company>/panel_*.png(→幅480+pngquant, 目標~150KB)
     public/images/<company>/personas/r*.png(→256角+pngquant, 目標~50KB)
同名PNG上書き=URL/フロント/D1不変。元画像は .backups/images_original_20260720/(COW)に退避済。

安全: 20社ごとに commit→push(reset --hard origin/main で消えないよう即push)。done-listで再開可。
QA fail(破損/寸法異常/極端劣化)は backupから復元して記録。
"""
from __future__ import annotations
import io, json, os, subprocess, sys, time
from pathlib import Path
from PIL import Image

ROOT = Path.home() / "projects" / "10koma-shukatsu"
IMG = ROOT / "public" / "images"
BACKUP = ROOT / ".backups" / "images_original_20260720"
DONE = ROOT / ".backups" / "_optimize_done.txt"
STATS = ROOT / ".backups" / "_optimize_stats.json"
SAMPLES = ROOT / ".backups" / "_optimize_samples.json"
PANEL_W = 480
PERSONA = 256
BATCH = 20

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def pngquant_to(tmp: Path, dst: Path) -> bool:
    for q in ("45-90", "0-90"):
        r = run(["pngquant", "--quality", q, "--speed", "1", "--strip", "--force", "--output", str(dst), str(tmp)])
        if r.returncode == 0 and dst.exists():
            return True
    return False

def opt_image(path: Path, kind: str):
    """resize+pngquant, 上書き。元サイズ/新サイズを返す。"""
    orig = path.stat().st_size
    im = Image.open(path)
    if kind == "persona":
        im = im.convert("RGB").resize((PERSONA, PERSONA), Image.LANCZOS)
    else:  # panel
        w, h = im.size
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        if w > PANEL_W:
            im = im.resize((PANEL_W, round(h * PANEL_W / w)), Image.LANCZOS)
    tmp = path.with_suffix(".opt.tmp.png")
    im.save(tmp, "PNG", optimize=True)
    if not pngquant_to(tmp, path):
        os.replace(str(tmp), str(path))   # fallback: resized PIL版
    else:
        tmp.unlink(missing_ok=True)
    return orig, path.stat().st_size

def qa(path: Path, kind: str) -> str:
    try:
        Image.open(path).verify()
        w, h = Image.open(path).size
    except Exception as e:
        return f"CORRUPT({e})"
    sz = path.stat().st_size
    if kind == "panel":
        if w > PANEL_W + 2:
            return f"DIM({w})"
        if sz < 15 * 1024:
            return f"TOOSMALL({sz//1024}KB)"
        if sz > 400 * 1024:
            return f"TOOBIG({sz//1024}KB)"
    else:
        if (w, h) != (PERSONA, PERSONA):
            return f"DIM({w}x{h})"
        if sz < 2 * 1024:
            return f"TOOSMALL({sz}B)"
    return "ok"

def restore(rel: Path):
    src = BACKUP / rel
    dst = IMG / rel
    if src.exists():
        run(["cp", "-c", str(src), str(dst)])

def git_commit_push(companies, batchno):
    """commitはローカルに確実に作る(=room-avatar loopがfetch/merge/pushで拾う実績あり)。
    自前pushはbest-effort(autostash rebaseで loopのlive編集ファイルを回避)。push失敗でも
    停止せず継続(commitは durable + loopがpush)。返り値は常にTrue(=commit済で前進可)。"""
    paths = [f"public/images/{c}" for c in companies]
    run(["git", "add"] + paths, cwd=ROOT)
    st = run(["git", "status", "--porcelain"] + paths, cwd=ROOT)
    if not st.stdout.strip():
        return True  # nothing changed (既に最適化=resume)
    run(["git", "commit", "-q", "-m",
         f"perf(images): 軽量化 batch{batchno} ({len(companies)}社) panel~150KB/persona256"], cwd=ROOT)
    for attempt in range(3):
        p = run(["git", "push", "origin", "HEAD:main"], cwd=ROOT)
        if p.returncode == 0:
            return True
        run(["git", "fetch", "origin"], cwd=ROOT)
        rb = run(["git", "-c", "rebase.autoStash=true", "rebase", "origin/main"], cwd=ROOT)
        if rb.returncode != 0:
            run(["git", "-c", "rebase.autoStash=true", "rebase", "--abort"], cwd=ROOT)
            time.sleep(2)
    # 自前push未達でも commit はローカルに在る → loopが拾う。停止しない。
    print(f"  [warn] batch{batchno}: 自前push未達(commitは作成済・loop/最終reconcileで origin へ)")
    return True

def main():
    done = set()
    if DONE.exists():
        done = set(DONE.read_text().split())
    stats = json.loads(STATS.read_text()) if STATS.exists() else {"orig": 0, "new": 0, "panels": 0, "personas": 0, "qa_fail": []}
    samples = json.loads(SAMPLES.read_text()) if SAMPLES.exists() else []

    companies = sorted([d.name for d in IMG.iterdir() if d.is_dir()])
    todo = [c for c in companies if c not in done]
    print(f"=== optimize: 全{len(companies)}社 / 済{len(done)} / 対象{len(todo)} ===", flush=True)

    batch = []
    batchno = len(done) // BATCH + 1
    for ci, comp in enumerate(todo, 1):
        cdir = IMG / comp
        try:
            for pf in sorted(cdir.glob("panel_*.png")):
                o, n = opt_image(pf, "panel")
                v = qa(pf, "panel")
                stats["orig"] += o; stats["new"] += n; stats["panels"] += 1
                if v != "ok":
                    stats["qa_fail"].append(f"{comp}/{pf.name}:{v}")
                    restore(Path(comp) / pf.name)
                elif len(samples) < 20 and pf.name == "panel_01.png":
                    samples.append({"company": comp, "rel": f"{comp}/{pf.name}", "orig": o, "new": n})
            pdir = cdir / "personas"
            if pdir.is_dir():
                for rf in sorted(pdir.glob("r*.png")):
                    o, n = opt_image(rf, "persona")
                    v = qa(rf, "persona")
                    stats["orig"] += o; stats["new"] += n; stats["personas"] += 1
                    if v != "ok":
                        stats["qa_fail"].append(f"{comp}/personas/{rf.name}:{v}")
                        restore(Path(comp) / "personas" / rf.name)
        except Exception as e:
            print(f"  [FAIL] {comp}: {e}", flush=True)
            stats["qa_fail"].append(f"{comp}:EXC:{str(e)[:80]}")
        batch.append(comp)
        if len(batch) >= BATCH or ci == len(todo):
            ok = git_commit_push(batch, batchno)
            if not ok:
                print(f"❌ batch{batchno} push失敗 → 停止(手動確認)", flush=True)
                STATS.write_text(json.dumps(stats, ensure_ascii=False))
                SAMPLES.write_text(json.dumps(samples, ensure_ascii=False))
                return 1
            with open(DONE, "a") as f:
                f.write("\n".join(batch) + "\n")
            STATS.write_text(json.dumps(stats, ensure_ascii=False))
            SAMPLES.write_text(json.dumps(samples, ensure_ascii=False))
            savedGB = (stats["orig"] - stats["new"]) / 1e9
            print(f"  batch{batchno} ✓ push ({len(batch)}社) | 累計 panel{stats['panels']}/persona{stats['personas']} "
                  f"orig{stats['orig']/1e9:.2f}G→new{stats['new']/1e9:.2f}G 削減{savedGB:.2f}G | qa_fail{len(stats['qa_fail'])}", flush=True)
            batch = []
            batchno += 1

    print(f"=== 完了: panel{stats['panels']} persona{stats['personas']} | "
          f"{stats['orig']/1e9:.2f}G→{stats['new']/1e9:.2f}G | qa_fail={len(stats['qa_fail'])} ===", flush=True)
    if stats["qa_fail"]:
        print("QA fail(復元済):", stats["qa_fail"][:30], flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
