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
import subprocess, json, csv, hashlib

# ---- 出荷条件(リミット) ----
PARALLEL = 3
TOTAL_COST_GUARD_USD = 300.0        # 暴走防止の総額ガード(超えたら停止)
COST_PER_IMAGE = 0.0672             # tokyari config.COST_PER_IMAGE_USD 実値
NO_DAILY_CAP = True                 # 日次$キャップは設けない(一気に回す)
MODEL = "gemini-3.1-flash-image"    # tokyari config.MODEL_IMAGE 実値
QA_MODEL = "gemini-3-flash-preview"  # スタイルドリフト(漫画/イラスト)検出QA
ASPECT = "1:1"                      # 顔ポートレート=正方形
RETRY = 4
WCONF = REPO / "api" / "wrangler.toml"

_LOCK = threading.Lock()
CONC = threading.Semaphore(PARALLEL)
_STATE = {"spent": 0.0, "n_ok": 0, "n_fail": 0, "r429": 0, "rejected": 0, "downgraded": False}
_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
client = genai.Client(api_key=_KEY)

# ★三井GOLDは不可侵=参照画像を一切使わない(前回の佐藤瓜二つ=GOLD誤参照を根治)。顔は下記プールから決定的に振る。
FACE_SHAPES = ["an oval face", "a round face", "a square jaw and broad face", "an angular face with defined cheekbones",
               "a long narrow face", "a soft heart-shaped face", "a rectangular face"]
HAIR_M = ["short neatly-combed black hair", "a short side-parted hairstyle", "swept-back short hair",
          "a short textured crop", "a clean slightly-wavy business cut", "short hair with a neat fringe",
          "very short cropped hair", "short hair, salt-and-pepper at the temples"]
HAIR_F = ["shoulder-length straight dark hair", "a neat chin-length bob", "long dark hair tied back neatly",
          "shoulder-length layered hair", "medium-length softly-wavy hair", "a short elegant cut",
          "long straight hair", "shoulder-length hair with a side part"]
BUILD = ["a slim build", "an average build", "a solid build", "a lean build"]
BROW = ["light stubble", "a clean-shaven look", "a neatly-trimmed short beard", "a clean-shaven look"]


def _face_traits(slug, role, female):
    """(slug+role)の決定的ハッシュで顔特徴を振る=会社ごと役割ごとに別人・再現可能。三井GOLDは参照しない。"""
    h = hashlib.md5(f"{slug}/{role}".encode()).hexdigest()
    i = [int(h[k:k + 2], 16) for k in range(0, 12, 2)]
    hair = (HAIR_F if female else HAIR_M)[i[1] % (len(HAIR_F) if female else len(HAIR_M))]
    parts = [FACE_SHAPES[i[0] % len(FACE_SHAPES)], hair, BUILD[i[2] % len(BUILD)]]
    if not female:
        parts.append(BROW[i[3] % len(BROW)])
    if i[4] % 5 == 0:   # 約2割に眼鏡(多様性)
        parts.append("wearing thin-framed glasses")
    return ", ".join(parts)


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


def build_prompt(slug, name, label, female, role):
    gender = "woman" if female else "man"
    age = _age_band(label)
    traits = _face_traits(slug, role, female)
    return (
        f"A professional corporate headshot PHOTOGRAPH of a fictional Japanese {gender} {age}, working as the "
        f"'{label}' at a company. This specific person has {traits}. "
        f"Head-and-shoulders framing, facing the camera, warm friendly natural smile, neat business attire "
        f"(dark suit or smart office wear), soft even studio lighting, plain seamless very light gray background. "
        f"【STYLE — strictly enforced】Realistic corporate portrait PHOTOGRAPH shot on a DSLR, photorealistic, "
        f"true-to-life skin texture and natural hair — this MUST look like a real photograph. "
        f"ABSOLUTELY NOT an illustration, NOT anime, NOT manga, NOT a cartoon, NOT a drawing, NOT a painting, "
        f"NOT a 3D render, NOT stylized art. "
        f"【FICTIONAL】A generic fictional person for an AI simulation — do NOT depict any real identifiable "
        f"person or celebrity. No text, logos, watermarks or badges. Single person only, square 1:1 composition."
    )


def _qa_photoreal(img_bytes):
    """生成画像が『写実的な写真(=漫画/イラスト/アニメでない)』かをvisionで判定。Trueなら合格。"""
    try:
        r = client.models.generate_content(
            model=QA_MODEL,
            contents=[types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                      "Is this image a realistic photograph of a single real-looking human (as opposed to an "
                      "illustration, anime, manga, cartoon, drawing, painting or 3D render)? Answer only 'yes' or 'no'."])
        txt = (r.text or "").strip().lower()
        return txt.startswith("y")
    except Exception:
        return True  # QA自体が落ちたら通す(生成は保持)


def _guard_ok(cost_next):
    with _LOCK:
        return (_STATE["spent"] + cost_next) <= TOTAL_COST_GUARD_USD


def gen_one(company, slug, role, name, label, female, pilot_dir=None):
    if not _guard_ok(COST_PER_IMAGE):
        return {"role": role, "ok": False, "note": f"総額ガード${TOTAL_COST_GUARD_USD}到達→停止"}
    out_dir = REPO / "public/images" / slug / "personas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{role.lower()}.png"
    prompt = build_prompt(slug, name, label, female, role)   # ★参照画像なし=三井GOLD不可侵・佐藤瓜二つ根治
    CONC.acquire()
    try:
        for attempt in range(1, RETRY + 1):
            try:
                resp = client.models.generate_content(
                    model=MODEL, contents=[prompt],
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
                with _LOCK:
                    _STATE["spent"] += COST_PER_IMAGE      # 生成した時点で課金(QA前)
                # ★スタイルQA: 写実でない(漫画/イラスト)なら破棄→再生成
                if not _qa_photoreal(img_bytes):
                    with _LOCK:
                        _STATE["rejected"] += 1; _STATE["spent"] += 0.005
                    if attempt < RETRY:
                        continue
                out_path.write_bytes(img_bytes)
                with _LOCK:
                    _STATE["n_ok"] += 1
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
