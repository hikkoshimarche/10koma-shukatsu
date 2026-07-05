#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_fanout_gen.py — 画像未整備∩lint0 の全社を1社ハーネスで並列生成(本番未反映・review保存)。

- 生成は generate_images.py(Gemini・char-ref=chars_reference・視覚フック背景・独立画像・文字焼込なし)。
  char-ref制約は見た目のみ(prompt_lintの.jpg等を踏まない)。生成物は output/<slug>/ に出て、review へコピー。
- 本番 D1/R2/public-images には一切書かない(検分後の別ブロックで反映)。
- 並列度3(Gemini 429を避ける保守値)。各社独立=1社失敗で全体を止めない(失敗隔離)。
- QAは generate_images 内部で最大3回リトライ。3回でも ok=False のコマは人レビュー隔離リストへ。
- チェックポイント: review/<slug>/ に10コマ揃う社はスキップ(再実行で続きから)。
- 進捗: 20社ごとに git commit→push。進捗と隔離は fanout ディレクトリの *.json/*.log に随時書く。
用法: python tools/image_fanout_gen.py            (全対象)
      環境変数 FANOUT_WORKERS で並列度変更可(既定3)。
"""
import json
import os
import subprocess
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
PY = str(TOK / ".venv" / "bin" / "python")
FAN = REPO / "review" / "image_gen_fanout_20260705"  # 公開URLは10koma repo経由(jsDelivr)
WORKERS = int(os.environ.get("FANOUT_WORKERS", "3"))
TARGETS = json.loads(Path("/tmp/fanout149.json").read_text())
OVER = {"itochu": "itochu-shoji"}


def tslug(s):
    return OVER.get(s, s)


def done(slug):
    d = FAN / slug
    return d.exists() and len(list(d.glob("koma*.png"))) >= 10


def gen_one(slug):
    """1社生成。戻り: {slug, ok_komas, fail_komas(隔離), copied, cost, sec, rate_limited}."""
    ts = tslug(slug)
    t0 = time.time()
    proc = subprocess.run([PY, "scripts/generate_images.py", "--company", ts],
                          cwd=str(TOK), capture_output=True, text=True, timeout=2400)
    out = (proc.stdout or "") + (proc.stderr or "")
    rate = ("429" in out) or ("rate" in out.lower() and "limit" in out.lower())
    import re
    m = re.search(r"概算コスト[:：]\s*\$?([0-9.]+)", out)
    cost = float(m.group(1)) if m else 0.0
    qp = TOK / "output" / ts / "qa_report.json"
    ok_k, fail_k = [], []
    if qp.exists():
        try:
            rep = json.load(open(qp, encoding="utf-8"))
            for r in rep.get("results", []):
                (ok_k if r.get("ok") else fail_k).append(r.get("koma_number"))
        except Exception:
            pass
    (FAN / slug).mkdir(parents=True, exist_ok=True)
    copied = 0
    for k in range(1, 11):
        src = TOK / "output" / ts / f"koma{k:02d}.png"
        if src.exists():
            shutil.copy2(src, FAN / slug / f"koma{k:02d}.png")
            copied += 1
    # 隔離: qaでok=False + 出力に無いコマ
    present = {int(p.stem.replace("koma", "")) for p in (FAN / slug).glob("koma*.png")}
    isolate = sorted(set(fail_k) | (set(range(1, 11)) - present))
    return {"slug": slug, "ok": sorted(ok_k), "isolate": isolate, "copied": copied,
            "cost": round(cost, 3), "sec": round(time.time() - t0, 1), "rate": rate,
            "rc": proc.returncode}


def git_push(msg):
    try:
        subprocess.run(["git", "add", "review/image_gen_fanout_20260705"], cwd=str(REPO), check=False)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(REPO), check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO), check=False,
                       capture_output=True, text=True, timeout=180)
    except Exception as e:
        log(f"[git] push失敗: {e}")


LOG = FAN / "fanout_progress.log"


def log(m):
    FAN.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%H:%M:%S')} {m}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    todo = [s for s in TARGETS if not done(s)]
    log(f"=== fanout開始 対象{len(TARGETS)} / 未生成{len(todo)} / 並列{WORKERS} ===")
    results = []
    isolation = []
    done_ct = 0
    last_commit = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(gen_one, s): s for s in todo}
        for fut in as_completed(futs):
            s = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {"slug": s, "ok": [], "isolate": list(range(1, 11)), "copied": 0,
                     "cost": 0, "sec": 0, "rate": False, "err": str(e)[:100]}
            results.append(r)
            if r["isolate"]:
                isolation.append({"slug": s, "komas": r["isolate"]})
            done_ct += 1
            log(f"[{done_ct}/{len(todo)}] {s:18} ok{len(r['ok'])}/10 隔離{r['isolate']} "
                f"${r['cost']:.2f} {r['sec']}s{' ⚠429' if r.get('rate') else ''}")
            # 20社ごとにcommit
            if done_ct - last_commit >= 20:
                (FAN / "isolation.json").write_text(json.dumps(isolation, ensure_ascii=False, indent=2))
                (FAN / "manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str))
                git_push(f"chore(fanout): 画像生成 {done_ct}/{len(todo)}社 中間push(本番未反映)")
                last_commit = done_ct
                log(f"  --- 中間commit {done_ct}社 ---")
    # 最終集計
    tot_img = sum(r["copied"] for r in results)
    tot_cost = sum(r["cost"] for r in results)
    tot_sec = sum(r["sec"] for r in results)
    iso_komas = sum(len(x["komas"]) for x in isolation)
    (FAN / "isolation.json").write_text(json.dumps(isolation, ensure_ascii=False, indent=2))
    (FAN / "manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    git_push(f"chore(fanout): 画像生成 完了 {len(results)}社/{tot_img}枚(本番未反映)")
    log(f"=== 完了: {len(results)}社 生成{tot_img}枚 隔離{iso_komas}コマ({len(isolation)}社) "
        f"総${tot_cost:.2f} 総{tot_sec/3600:.1f}h(実時間は並列で短縮) ===")
    log("DONE")


if __name__ == "__main__":
    main()
