#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_avatar_gpt.py — 三井GOLD方式(OpenAI gpt-image-1)+会社ごとLLM appearance spec で全社別人アバター。
金型調査結論: 三井GOLDアバターのPNGにC2PA/JUMBF+OpenAI/gpt署名=gpt-image-1製。同モデル・同質で作り直す。
会社ごとに Claude が『別々の人物像セット』を生成(_face_traits微振りを置換)=会社A7人とB7人が全員別人。
パイロット: --slugs a,b,c → personas_gpt/ に出力(既存Gemini版を上書きせず)+モンタージュ。★承認までフル生成しない。
"""
import argparse, base64, io, json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
sys.path.insert(0, os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts")); sys.path.insert(0, str(REPO / "tools"))
try:
    from dotenv import load_dotenv as _ld; _ld(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
except Exception:
    pass
import room_industry_roles_v3 as V3
import requests
from PIL import Image, ImageDraw, ImageFont

WCONF = REPO / "api" / "wrangler.toml"
OAI_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
ANT_KEY = re.sub(r"\s", "", os.environ.get("ANTHROPIC_API_KEY", ""))
IMG_MODEL = "gpt-image-1"
COST_PER_IMAGE = 0.167   # high品質1024²の実測(94in+4160imgout)
PARALLEL = 3
_LOCK = threading.Lock(); _STATE = {"spent": 0.0, "n": 0}


def claude(prompt, system, max_tokens=2000):
    for _ in range(4):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANT_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-6", "max_tokens": max_tokens, "system": system,
                      "messages": [{"role": "user", "content": prompt}]}, timeout=120)
            if r.status_code == 200:
                return "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
        except Exception:
            time.sleep(2)
    return ""


def company_specs(company, industry, roster):
    """Claudeが会社ごとに『別々の人物像セット』を生成。役割の年齢帯/性別整合維持・全員別人・実在人物非依拠。"""
    rl = "\n".join(f"- {r['role_key']}: {r['label']} ({'女性' if r['female'] else '男性'})" for r in roster)
    sysp = ("You are a casting director creating a set of DISTINCT fictional Japanese business people for one "
            "company's AI OB-visit avatars. Each role is a DIFFERENT individual — vary face shape, build, hair, "
            "skin tone, age within band, and vibe so no two look alike. Keep each role's gender and age-band. "
            "Do NOT resemble any real identifiable person/celebrity. Output ONLY JSON.")
    usr = (f"Company: {company} (industry: {industry}). Create the cast for these roles:\n{rl}\n\n"
           f"For each role output a concise ENGLISH appearance spec (one sentence) covering: age (specific, within "
           f"the role's band), gender, face shape, build, hairstyle, skin tone, distinctive feature, and business "
           f"attire fitting the role/industry. Make this company's cast visually cohesive as colleagues but every "
           f"person clearly a different individual. JSON: {{\"R1\":\"...\", ...}} using the role keys above.")
    txt = claude(usr, sysp)
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


def gen_gpt(appearance, out_path):
    # ★『Japanese』をハードコード強制(specがethnicity省略しても東アジア顔がぶれない=住友行の白人寄りドリフト根治)。
    prompt = (f"A professional corporate headshot photograph of a fictional JAPANESE person (East Asian features). "
              f"{appearance} The person is clearly Japanese. "
              "Warm friendly natural smile, head-and-shoulders, facing camera, soft studio lighting, plain white "
              "seamless background (like the mitsui reference). Photorealistic corporate profile photo. "
              "A fictional generic person, NOT a real identifiable individual or celebrity. No text, logos or watermarks.")
    for att in range(1, 4):
        try:
            r = requests.post("https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OAI_KEY}", "Content-Type": "application/json"},
                json={"model": IMG_MODEL, "prompt": prompt, "size": "1024x1024", "quality": "high", "n": 1}, timeout=180)
            if r.status_code == 200:
                b = base64.b64decode(r.json()["data"][0]["b64_json"])
                out_path.write_bytes(b)
                with _LOCK:
                    _STATE["spent"] += COST_PER_IMAGE; _STATE["n"] += 1
                return True
            if r.status_code in (429, 500, 503):
                time.sleep(2 ** att); continue
            return False
        except Exception:
            time.sleep(2 ** att)
    return False


def roster_for(slug):
    cj = json.loads((REPO / "public/companies.json").read_text(encoding="utf-8"))
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}; id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    roster = V3.roles_for_company(slug, id2ind.get(slug, ""))
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--json", "--command", f"SELECT role, persona_name FROM room_personas WHERE company_slug='{slug}' ORDER BY role"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=90)
    names = {x["role"]: x["persona_name"] for x in json.loads(p.stdout[p.stdout.find("["):])[0]["results"]}
    for r in roster:
        r["name"] = names.get(r["role_key"], r["role_key"])
    return id2name.get(slug, slug), id2ind.get(slug, ""), roster


def gen_company(slug, outdir):
    company, industry, roster = roster_for(slug)
    specs = company_specs(company, industry, roster)
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    sem = threading.Semaphore(PARALLEL)

    def one(r):
        sem.acquire()
        try:
            ap = specs.get(r["role_key"]) or f"a Japanese {'woman' if r['female'] else 'man'}, the {r['label']}"
            out = outdir / f"{r['role_key'].lower()}.png"
            ok = gen_gpt(ap, out)
            return {"role": r["role_key"], "name": r["name"], "label": r["label"], "ok": ok, "spec": ap[:60]}
        finally:
            sem.release()
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for f in as_completed([ex.submit(one, r) for r in roster]):
            results.append(f.result())
    return company, sorted(results, key=lambda x: x["role"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", required=True)
    ap.add_argument("--outbase", default=os.path.expanduser("~/Desktop/kindle_受け渡し/avatar_pilot_gpt"))
    args = ap.parse_args()
    print(f"=== gpt-image-1 パイロット(会社ごとLLM spec・${COST_PER_IMAGE}/枚・並列{PARALLEL}) ===")
    allres = {}
    for slug in args.slugs.split(","):
        outdir = Path(args.outbase) / slug
        company, res = gen_company(slug, outdir)
        nok = sum(1 for r in res if r["ok"])
        print(f"  {company}({slug}): {nok}/{len(res)}枚 累計${_STATE['spent']:.2f}")
        for r in res:
            print(f"    {r['role']} {r['name']} [{r['label']}] {'✅' if r['ok'] else '❌'} spec={r['spec']}")
        allres[slug] = (company, res, outdir)
    print(f"\n  合計 {_STATE['n']}枚 / 実費${_STATE['spent']:.2f} / $/枚={_STATE['spent']/max(_STATE['n'],1):.3f}")
    print(f"  ★全社概算(2918枚 high): ${2918*COST_PER_IMAGE:.0f}")
    (Path(args.outbase) / "_pilot_result.json").write_text(json.dumps({k: [v[0]] + [v[1]] for k, v in allres.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
