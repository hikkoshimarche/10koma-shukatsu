#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_avatar_gen.py — ルームv3 人格アバター(顔ポートレート)生成。Gemini gemini-3.1-flash-image。
ハウススタイル=三井GOLDアバター(clean headshot/plain bg/business attire/親しみやすい/架空の人物像)。
出荷条件: 並列3・$300総額ガード(暴走防止)・日次$キャップなし・429自動リトライ・20枚毎push。
スタイル承認ゲート: 既定はパイロット(--slug 1社)。--all はフル(承認後)。
使い方: room_avatar_gen.py --slug sumitomo-corp [--pilot-dir <検分用フォルダ>]
        room_avatar_gen.py --all   (承認後・全社)
"""
import argparse
import io
import os
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
PSCR = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts"))
sys.path.insert(0, str(PSCR)); sys.path.insert(0, str(REPO / "tools"))
try:
    from dotenv import load_dotenv as _ld; _ld(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
except Exception:
    pass
import room_industry_roles_v3 as V3
from google import genai
from google.genai import types
from PIL import Image
import subprocess, json, csv

# ---- 出荷条件(リミット) ----
PARALLEL = 3
TOTAL_COST_GUARD_USD = 300.0        # 暴走防止の総額ガード(超えたら停止)
COST_PER_IMAGE = 0.0672             # tokyari config.COST_PER_IMAGE_USD 実値
NO_DAILY_CAP = True                 # 日次$キャップは設けない(一気に回す)
MODEL = "gemini-3.1-flash-image"    # tokyari config.MODEL_IMAGE 実値
ASPECT = "1:1"                      # 顔ポートレート=正方形(GOLD準拠)
RETRY = 4
WCONF = REPO / "api" / "wrangler.toml"

_LOCK = threading.Lock()
CONC = threading.Semaphore(PARALLEL)
_STATE = {"spent": 0.0, "n_ok": 0, "n_fail": 0, "r429": 0, "downgraded": False}
_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
client = genai.Client(api_key=_KEY)

# 三井GOLDアバターをハウススタイル参照に(性別一致)
STYLE_REF_MALE = REPO / "public/images/mitsui/personas/r1_sato.png"
STYLE_REF_FEMALE = REPO / "public/images/mitsui/personas/r4_suzuki.png"


def _age_band(label):
    l = label
    if any(k in l for k in ("事業部長", "部長", "パートナー", "プリンシパル", "局長", "支店長", "創業", "VPoE")):
        return "in their early 50s, experienced and composed"
    if any(k in l for k in ("退職", "OB")):
        return "in their mid 40s, calm and reflective"
    if any(k in l for k in ("中堅", "マネージャー", "シニア", "PM", "MD", "バイヤー")):
        return "in their late 30s, capable and steady"
    if any(k in l for k in ("若手", "修士新卒", "新卒", "1年", "アソシエイト", "窓口", "一般職", "業務職")):
        return "in their mid 20s, fresh and energetic"
    return "in their early 30s, professional"


def build_prompt(company, name, label, female):
    gender = "woman" if female else "man"
    age = _age_band(label)
    return (
        f"A clean professional corporate headshot portrait of a fictional Japanese {gender} {age}, "
        f"depicted as the '{label}' at a company. Head-and-shoulders framing, facing the camera, "
        f"friendly approachable natural smile, neat business attire appropriate to the role "
        f"(dark suit or smart office wear), soft even studio lighting, plain very light gray/white background. "
        f"Match the visual house style of the reference image (same clean photoreal look, framing and lighting). "
        f"IMPORTANT: this is a generic FICTIONAL person for an AI OB-visit simulation — do NOT depict any real "
        f"identifiable person or celebrity. Do NOT add any text, logos, watermarks, or badges. "
        f"Single person only, square 1:1 composition."
    )


def _guard_ok(cost_next):
    with _LOCK:
        return (_STATE["spent"] + cost_next) <= TOTAL_COST_GUARD_USD


def gen_one(company, slug, role, name, label, female, pilot_dir=None):
    if not _guard_ok(COST_PER_IMAGE):
        return {"role": role, "ok": False, "note": f"総額ガード${TOTAL_COST_GUARD_USD}到達→停止"}
    out_dir = REPO / "public/images" / slug / "personas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{role.lower()}.png"
    ref = Image.open(STYLE_REF_FEMALE if female else STYLE_REF_MALE)
    prompt = build_prompt(company, name, label, female)
    CONC.acquire()
    try:
        for attempt in range(1, RETRY + 1):
            try:
                resp = client.models.generate_content(
                    model=MODEL, contents=[ref, prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        image_config=types.ImageConfig(aspect_ratio=ASPECT)))
                img_bytes = None
                for p in resp.candidates[0].content.parts:
                    if getattr(p, "inline_data", None) and p.inline_data.data:
                        img_bytes = p.inline_data.data; break
                if not img_bytes:
                    raise RuntimeError("no image part")
                Image.open(io.BytesIO(img_bytes)).verify()
                out_path.write_bytes(img_bytes)
                with _LOCK:
                    _STATE["spent"] += COST_PER_IMAGE; _STATE["n_ok"] += 1
                if pilot_dir:
                    shutil.copy(out_path, Path(pilot_dir) / f"{slug}_{role.lower()}_{name.replace(' ','')}.png")
                return {"role": role, "ok": True, "name": name, "label": label, "path": str(out_path),
                        "bytes": len(img_bytes), "attempts": attempt}
            except Exception as e:
                msg = str(e)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    with _LOCK:
                        _STATE["r429"] += 1
                    if not _STATE["downgraded"]:
                        _STATE["downgraded"] = True; CONC.acquire()  # 並列3→2降格
                time.sleep(min(2 ** attempt, 20))
        with _LOCK:
            _STATE["n_fail"] += 1
        return {"role": role, "ok": False, "note": "生成失敗(リトライ尽き)"}
    finally:
        CONC.release()


def roster_for(slug):
    cj = json.loads((REPO / "public/companies.json").read_text(encoding="utf-8"))
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    roster = {r["role_key"]: r for r in V3.roles_for_company(slug, id2ind.get(slug, ""))}
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--json", "--command", f"SELECT role, persona_name FROM room_personas WHERE company_slug='{slug}' ORDER BY role"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=90)
    rows = json.loads(p.stdout[p.stdout.find("["):])[0]["results"]
    out = []
    for x in rows:
        rd = roster.get(x["role"], {})
        out.append((x["role"], x["persona_name"], rd.get("label", x["role"]), bool(rd.get("female"))))
    return id2name.get(slug, slug), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pilot-dir")
    ap.add_argument("--show-limits", action="store_true")
    args = ap.parse_args()

    print("=== [出荷条件・実効リミット] ===")
    print(f"  MODEL={MODEL} / $/枚={COST_PER_IMAGE} / 並列={PARALLEL}(429で2へ自動降格)")
    print(f"  日次$キャップ={'なし(一気に回す)' if NO_DAILY_CAP else 'あり'} / 時間枚数上限=なし / 総額ガード=${TOTAL_COST_GUARD_USD}(超で停止)")
    if args.show_limits:
        return 0

    slug = args.slug or "sumitomo-corp"
    company, roster = roster_for(slug)
    pilot_dir = args.pilot_dir
    if pilot_dir:
        Path(pilot_dir).mkdir(parents=True, exist_ok=True)
    print(f"\n=== アバター生成 パイロット: {company}({slug}) {len(roster)}枚 ===", flush=True)
    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        futs = [ex.submit(gen_one, company, slug, role, name, label, female, pilot_dir)
                for role, name, label, female in roster]
        for f in as_completed(futs):
            r = f.result(); results.append(r)
            mark = "✅" if r["ok"] else "❌"
            print(f"  {mark} {r['role']} {r.get('name','')} [{r.get('label','')}] "
                  f"{r.get('bytes','')}B att={r.get('attempts','')}{'' if r['ok'] else ' '+r.get('note','')}", flush=True)
    ok = [r for r in results if r["ok"]]
    dt = round(time.time() - t0)
    print(f"\n  生成: {len(ok)}/{len(roster)}枚 OK / 実費 ${_STATE['spent']:.4f} (${_STATE['spent']/max(len(ok),1):.4f}/枚) / {dt}s / 429={_STATE['r429']}")
    # 総額概算(全社)
    total_personas = 0
    if args.all or True:
        cj = json.loads((REPO / "public/companies.json").read_text(encoding="utf-8"))
        id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}
        pr = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                             "--json", "--command", "SELECT COUNT(*) n FROM room_personas WHERE company_slug!='mitsui-bussan'"],
                            cwd=str(REPO), capture_output=True, text=True, timeout=60)
        try:
            total_personas = json.loads(pr.stdout[pr.stdout.find("["):])[0]["results"][0]["n"]
        except Exception:
            total_personas = 2500
    per = _STATE["spent"] / max(len(ok), 1)
    print(f"  ★全社概算: 総人格{total_personas} × ${per:.4f}/枚 = ${total_personas*per:.0f} (総額ガード${TOTAL_COST_GUARD_USD}内)")
    if pilot_dir:
        print(f"  検分フォルダ: {pilot_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
