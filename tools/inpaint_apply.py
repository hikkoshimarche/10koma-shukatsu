#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inpaint_apply.py — 局所修正(真のinpaint)本適用フロー。

方式: gpt-image-1 の mask付きedit(指定領域のみ再生成) → マスク合成(元画像へα合成)。
  マスク外は元画像のピクセルを保持(差分を数値で検証)。gpt-image-1 が使えない時は Gemini
  image-to-image(全体再レンダ)を fallback で使い、同様にマスク領域のみ合成する。

フロー: インターンが領域(bbox)指示 → candidate生成(--candidate) → before/after/zoom を受け渡しへ
        → 人/Web Claude 承認 → --apply で per-panel canary付き反映(public/images→push→D1 image_url更新)。

jobs JSON(配列)の各要素:
  {"slug":"seiko-epson","koma":3,"bbox":[365,185,480,305],
   "prompt":"...修正内容...","feather":6,"label":"頭部アーチファクト除去"}

使い方:
  python inpaint_apply.py --jobs jobs.json --candidate --review-dir <dir>
  python inpaint_apply.py --jobs jobs.json --apply --only seiko-epson#3   # 承認後
"""
from __future__ import annotations
import argparse, base64, io, json, os, subprocess, sys, time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageChops

REPO = Path.home() / "projects" / "10koma-shukatsu"
IMG = REPO / "public" / "images"
API_WORKER = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
GH = "https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu"
TOKY = Path.home() / "oscar-ai" / "tokyari-pipeline"

STYLE_SUFFIX = ("。元画像と同じアニメ調・線画の太さ・彩色・トーンを厳密に踏襲し、"
                "修正領域を周囲(背景・人物・什器)と継ぎ目なく自然に連続させる。"
                "指定領域の外は変更しない。")


def load_env():
    for f in (TOKY / ".env", REPO / "tools" / ".env.phase_c"):
        if f.exists():
            for line in f.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())


def d1(cmd, json_out=True):
    args = ["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote"]
    if json_out: args.append("--json")
    args += ["--command", cmd]
    r = subprocess.run(args, cwd=str(REPO / "api"), capture_output=True, text=True, timeout=150)
    if json_out:
        try: return json.loads(r.stdout)[0]["results"]
        except Exception: return []
    return r.stdout


def live_image(slug, koma):
    rows = d1(f"SELECT image_url FROM company_panels WHERE company_id='{slug}' AND panel_num={koma};")
    if not rows: raise RuntimeError(f"D1にpanel無し {slug}#{koma}")
    url = rows[0]["image_url"]
    img = Image.open(io.BytesIO(requests.get(url, timeout=30).content)).convert("RGB")
    return img, url


def _boxes(bbox):
    """bbox は単一 [x0,y0,x1,y1] または複数 [[..],[..]] を受ける。常にリスト化して返す。"""
    return list(bbox) if (bbox and isinstance(bbox[0], (list, tuple))) else [bbox]


def _envelope(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def build_mask(size, bbox):
    """OpenAI edits用: 透明(alpha0)=編集領域 / 不透明=保持。複数bbox対応。"""
    w, h = size
    m = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(m)
    for b in _boxes(bbox):
        d.rectangle(tuple(b), fill=(0, 0, 0, 0))
    return m


def gpt_edit(orig, mask, prompt, retries=4):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key: return None, "OPENAI_API_KEY無"
    w, h = orig.size
    size = "1024x1536" if h >= w else "1536x1024"
    bo = io.BytesIO(); orig.save(bo, "PNG"); bo.seek(0)
    bm = io.BytesIO(); mask.save(bm, "PNG"); bm.seek(0)
    for att in range(retries):
        bo.seek(0); bm.seek(0)
        try:
            r = requests.post("https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {key}"},
                files={"image": ("i.png", bo, "image/png"), "mask": ("m.png", bm, "image/png")},
                data={"model": "gpt-image-1", "prompt": prompt + STYLE_SUFFIX, "size": size, "n": "1"},
                timeout=240)
            if r.status_code == 200:
                b64 = r.json()["data"][0]["b64_json"]
                return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB"), None
            err = f"HTTP {r.status_code} {r.text[:80]}"
        except Exception as e:
            err = f"{type(e).__name__}:{str(e)[:80]}"
        time.sleep(5)
    return None, err


def gemini_edit(orig, prompt):
    """fallback: 全体再レンダ(image-to-image)。合成でマスク領域のみ使う。"""
    try:
        sys.path.insert(0, str(TOKY / "scripts"))
        from google import genai
        from google.genai import types
        import config
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip())
        resp = client.models.generate_content(model=config.MODEL_IMAGE,
            contents=[orig, prompt + STYLE_SUFFIX + "画像全体は現状を可能な限り保持する。"],
            config=types.GenerateContentConfig(response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=config.EXPECTED_ASPECT)))
        for part in resp.candidates[0].content.parts:
            inl = getattr(part, "inline_data", None)
            if inl and getattr(inl, "data", None):
                return Image.open(io.BytesIO(inl.data)).convert("RGB"), None
        return None, "no image part"
    except Exception as e:
        return None, f"{type(e).__name__}:{str(e)[:80]}"


def color_match(edited, orig, bbox):
    """編集画像(全体)の色分布を、元画像の bbox「周囲リング」の per-channel 平均/標準偏差へ線形整合。
    除去系では bbox 内=アーチファクト(元の色が不正)なので、正しいシーン色である周囲リングを参照する。
    gpt-image-1 の暖色カースト/不整合トーンを正しい背景色へ寄せる(合成前に適用)。"""
    from PIL import ImageStat, ImageDraw
    er = edited.resize(orig.size, Image.LANCZOS)
    w, h = orig.size
    env = _envelope(_boxes(bbox))
    # 周囲リング(envelope を pad 拡張した枠 − 各box) を参照領域に
    pad = max(24, (env[2] - env[0]) // 4, (env[3] - env[1]) // 4)
    ring = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(ring)
    d.rectangle((max(0, env[0]-pad), max(0, env[1]-pad), min(w, env[2]+pad), min(h, env[3]+pad)), fill=255)
    for b in _boxes(bbox):
        d.rectangle(tuple(b), fill=0)
    eb = er.crop(tuple(env))
    se = ImageStat.Stat(eb)
    so = ImageStat.Stat(orig, ring)          # 参照=元画像のリング
    bands = []
    for ci, ch in enumerate("RGB"):
        me, sde = se.mean[ci], (se.stddev[ci] or 1.0)
        mo, sdo = so.mean[ci], (so.stddev[ci] or 1.0)
        gain = max(0.5, min(2.0, sdo / sde)); bias = mo - me * gain
        bands.append(er.getchannel(ch).point(lambda x, g=gain, b=bias: int(max(0, min(255, x * g + b)))))
    return Image.merge("RGB", bands)


def composite(orig, edited, bbox, feather=6):
    w, h = orig.size
    edited = edited.resize((w, h), Image.LANCZOS)
    em = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(em)
    for b in _boxes(bbox):
        d.rectangle(tuple(b), fill=255)
    em = em.filter(ImageFilter.GaussianBlur(feather))
    result = Image.composite(edited, orig, em)
    # マスク外保持の検証(各box を feather 余白ぶん外した領域の最大差分)
    pad = feather * 2 + 4
    outside = Image.new("L", (w, h), 255)
    od = ImageDraw.Draw(outside)
    for b in _boxes(bbox):
        od.rectangle((b[0]-pad, b[1]-pad, b[2]+pad, b[3]+pad), fill=0)
    diff = ImageChops.multiply(ImageChops.difference(orig, result).convert("L"), outside)
    return result, diff.getextrema()[1]


def render_review(rdir, job, orig, result):
    slug, koma = job["slug"], job["koma"]
    bbox = _envelope(_boxes(job["bbox"]))
    w, h = orig.size
    key = f"{slug}_{koma:02d}"
    orig.save(rdir / f"{key}_BEFORE.png")
    result.save(rdir / f"{key}_AFTER.png")
    # zoom(領域±余白)
    pad = 30
    zb = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(w, bbox[2]+pad), min(h, bbox[3]+pad))
    zo = orig.crop(zb); zr = result.crop(zb)
    sc = 320 / max(1, zo.width)
    zo = zo.resize((int(zo.width*sc), int(zo.height*sc))); zr = zr.resize((int(zr.width*sc), int(zr.height*sc)))
    zoom = Image.new("RGB", (zo.width + zr.width + 30, max(zo.height, zr.height) + 24), "white")
    dz = ImageDraw.Draw(zoom); dz.text((5, 2), "before", fill="black"); dz.text((zo.width+25, 2), "after", fill="black")
    zoom.paste(zo, (5, 22)); zoom.paste(zr, (zo.width+25, 22))
    zoom.save(rdir / f"{key}_ZOOM.png")


def optimize_png(img, dst, width=480):
    w, h = img.size
    if w > width:
        img = img.resize((width, round(h*width/w)), Image.LANCZOS)
    tmp = dst.with_suffix(".tmp.png"); img.save(tmp, "PNG")
    r = subprocess.run(["pngquant", "--quality", "45-90", "--speed", "1", "--strip", "--force",
                        "--output", str(dst), str(tmp)])
    if r.returncode != 0: os.replace(tmp, dst)
    else: tmp.unlink(missing_ok=True)


def canary_snapshot():
    rows = d1("SELECT company_id||'#'||panel_num k, length(dialogue)+length(script_json) h FROM company_panels;")
    return {r["k"]: r["h"] for r in rows}


def apply_one(job, result):
    slug, koma = job["slug"], job["koma"]
    dst = IMG / slug / f"panel_{koma:02d}.png"
    before = canary_snapshot()
    optimize_png(result, dst)
    subprocess.run(["git", "add", str(dst)], cwd=str(REPO))
    subprocess.run(["git", "commit", "-q", "-m",
                    f"fix(image:inpaint): {slug} koma{koma:02d} 局所修正(mask合成・{job.get('label','')})"], cwd=str(REPO))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    for att in range(3):
        p = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=str(REPO), capture_output=True, text=True)
        if p.returncode == 0: break
        subprocess.run(["git", "fetch", "origin"], cwd=str(REPO))
        subprocess.run(["git", "-c", "rebase.autoStash=true", "rebase", "origin/main"], cwd=str(REPO))
    url = f"{GH}@{sha}/public/images/{slug}/panel_{koma:02d}.png"
    for _ in range(20):
        if requests.get(url, timeout=20).status_code == 200: break
        time.sleep(3)
    d1(f"UPDATE company_panels SET image_url='{url}' WHERE company_id='{slug}' AND panel_num={koma};", json_out=False)
    after = canary_snapshot()
    drift = [k for k in before if before[k] != after.get(k)]
    api_ok = requests.get(f"{API_WORKER}/api/companies/{slug}", timeout=20).status_code == 200
    return {"slug": slug, "koma": koma, "sha": sha[:10], "canary_drift": drift, "api_ok": api_ok, "url": url}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--candidate", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", default="", help="slug#koma をカンマ区切りで限定")
    ap.add_argument("--review-dir", default=str(Path.home()/"Desktop"/"kindle_受け渡し"/"inpaint_candidates"))
    ap.add_argument("--engine", default="gpt", choices=["gpt", "gemini"])
    ap.add_argument("--no-color-match", action="store_true", help="編集領域の色温度整合を無効化")
    args = ap.parse_args()
    load_env()
    jobs = json.load(open(args.jobs, encoding="utf-8"))
    only = set(x.strip() for x in args.only.split(",") if x.strip())
    if only: jobs = [j for j in jobs if f"{j['slug']}#{j['koma']}" in only]
    rdir = Path(args.review_dir); rdir.mkdir(parents=True, exist_ok=True)
    results = []
    for j in jobs:
        key = f"{j['slug']}#{j['koma']}"
        # --apply: 承認済みの RESULT png をそのまま反映(再生成しない=承認された画そのものを本番へ)
        result_png = rdir / f"{j['slug']}_{j['koma']:02d}_RESULT.png"
        if args.apply and not args.candidate and result_png.exists():
            from PIL import Image as _I
            result = _I.open(result_png).convert("RGB")
            print(f"[{key}] 承認済みRESULT反映 …", flush=True)
            ap_rec = apply_one(j, result)
            ok = ap_rec["api_ok"] and not ap_rec["canary_drift"]
            print(f"   {'✓反映' if ok else '⚠要確認'} sha={ap_rec['sha']} canary_drift={ap_rec['canary_drift']} api={ap_rec['api_ok']}", flush=True)
            results.append({"key": key, **ap_rec}); continue
        print(f"[{key}] {j.get('label','')} …", flush=True)
        orig, _ = live_image(j["slug"], j["koma"])
        mask = build_mask(orig.size, j["bbox"])
        edited = err = None
        if args.engine == "gpt":
            edited, err = gpt_edit(orig, mask, j["prompt"])
            if edited is None:
                print(f"   gpt-image-1不可({err}) → Gemini fallback", flush=True)
                edited, err = gemini_edit(orig, j["prompt"])
        else:
            edited, err = gemini_edit(orig, j["prompt"])
        if edited is None:
            print(f"   ✗ 生成失敗: {err}", flush=True); results.append({**{"key": key}, "error": err}); continue
        if not args.no_color_match:
            edited = color_match(edited, orig, j["bbox"])
        result, outside_diff = composite(orig, edited, j["bbox"], j.get("feather", 6))
        rec = {"key": key, "outside_diff": outside_diff, "engine": args.engine}
        if args.candidate:
            render_review(rdir, j, orig, result)
            (rdir / f"{j['slug']}_{j['koma']:02d}_RESULT.png").write_bytes(b"") if False else result.save(rdir / f"{j['slug']}_{j['koma']:02d}_RESULT.png")
            print(f"   ✓ 候補生成 outside_diff={outside_diff}/255 → {rdir.name}/", flush=True)
        if args.apply:
            if outside_diff > 12:
                print(f"   ⚠ outside_diff={outside_diff}>12 → 反映中止(マスク外が変化)", flush=True)
                rec["skipped"] = "outside_diff過大"; results.append(rec); continue
            ap_rec = apply_one(j, result)
            rec.update(ap_rec)
            ok = ap_rec["api_ok"] and not ap_rec["canary_drift"]
            print(f"   {'✓反映' if ok else '⚠要確認'} sha={ap_rec['sha']} canary_drift={ap_rec['canary_drift']} api={ap_rec['api_ok']}", flush=True)
        results.append(rec)
    print("\n=== まとめ ===")
    for r in results: print(" ", r)
    (rdir / "_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
