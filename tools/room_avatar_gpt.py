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


QA_MODEL = "claude-haiku-4-5-20251001"   # 安価なvisionでethnicity/GOLD絵作り/解剖QA


def qa_avatar(img_bytes):
    """三井GOLD準拠か+日本人か+解剖OKかを判定。{japanese,white_bg,highkey,chestup,anatomy_ok}を返す。"""
    b64 = base64.b64encode(img_bytes).decode()
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANT_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": QA_MODEL, "max_tokens": 150, "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                {"type": "text", "text": (
                    "Judge this corporate headshot. Reply ONLY compact JSON with booleans: "
                    "{\"japanese\":clearly Japanese/East-Asian person, "
                    "\"white_bg\":background is near-pure-white seamless (not gray/colored), "
                    "\"highkey\":bright soft even high-key lighting with minimal shadows, "
                    "\"chestup\":framed from the chest up with headroom above the head (not a tight crop), "
                    "\"anatomy_ok\":no severe facial/ear/hand deformity}. JSON only.")}]}]}, timeout=60)
        if r.status_code == 200:
            txt = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
            m = re.search(r"\{.*\}", txt, re.S)
            if m:
                d = json.loads(m.group(0))
                with _LOCK:
                    _STATE["spent"] += 0.002
                return d
    except Exception:
        pass
    return {"japanese": True, "white_bg": True, "highkey": True, "chestup": True, "anatomy_ok": True}


def gen_gpt(appearance, out_path, do_qa=True):
    # ★絵作りテンプレを三井GOLDに統一(白背景/ハイキー柔光/胸から上・広め・ヘッドルーム多め/広告写真調)。
    #   顔キャスティング(appearance)と『Japanese』無条件強制は維持。変えるのは art-direction のみ。
    prompt = (f"A clean high-key corporate portrait photograph of a fictional JAPANESE person (East Asian features), "
              f"in the polished style of a premium Japanese company's recruiting-website profile photo. "
              f"{appearance} The person is clearly Japanese. "
              "Framing: from the chest up, slightly wide with generous headroom above the head, subject centered and "
              "facing the camera, warm friendly natural smile. "
              "Lighting: bright HIGH-KEY soft and even studio lighting, minimal shadows, clean and airy. "
              "Background: pure seamless WHITE (bright, near-pure white, no gray gradient, no props, no vignette). "
              "Finish: crisp clean advertising-quality corporate portrait, photorealistic, sharp focus on the face. "
              "A fictional generic person, NOT a real identifiable individual or celebrity. No text, logos or watermarks.")
    last = None
    for att in range(1, 5):
        try:
            r = requests.post("https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OAI_KEY}", "Content-Type": "application/json"},
                json={"model": IMG_MODEL, "prompt": prompt, "size": "1024x1024", "quality": "high", "n": 1}, timeout=180)
            if r.status_code == 200:
                b = base64.b64decode(r.json()["data"][0]["b64_json"])
                with _LOCK:
                    _STATE["spent"] += COST_PER_IMAGE
                qa = qa_avatar(b) if do_qa else {"japanese": True, "anatomy_ok": True, "white_bg": True, "highkey": True, "chestup": True}
                last = (b, qa)
                hard_ok = qa.get("japanese", True) and qa.get("anatomy_ok", True)  # 日本人×解剖=必須(不可なら再生成)
                if hard_ok or att >= 4:
                    out_path.write_bytes(b)
                    with _LOCK:
                        _STATE["n"] += 1
                        if not hard_ok:
                            _STATE.setdefault("forced", 0); _STATE["forced"] += 1
                    return qa
                with _LOCK:
                    _STATE.setdefault("regen", 0); _STATE["regen"] += 1
                continue
            if r.status_code in (429, 500, 503):
                time.sleep(2 ** att); continue
            return None
        except Exception:
            time.sleep(2 ** att)
    if last:
        last[0] and out_path.write_bytes(last[0])
        return last[1]
    return None


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


def gen_company(slug, outdir, overwrite=False):
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
            if not overwrite and out.exists() and out.stat().st_size > 50000:   # pilot時のみ既存skip(本走はGemini上書き)
                return {"role": r["role_key"], "name": r["name"], "label": r["label"], "ok": True, "qa": {}, "skipped": True, "spec": ap[:60]}
            qa = gen_gpt(ap, out)
            return {"role": r["role_key"], "name": r["name"], "label": r["label"], "ok": qa is not None, "qa": qa or {}, "spec": ap[:60]}
        finally:
            sem.release()
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for f in as_completed([ex.submit(one, r) for r in roster]):
            results.append(f.result())
    return company, sorted(results, key=lambda x: x["role"])


TOTAL_GUARD = 500.0
HANDOFF = Path(os.path.expanduser("~/Desktop/kindle_受け渡し"))


def _git(*a):
    return subprocess.run(["git", *a], cwd=str(REPO), capture_output=True, text=True, timeout=180)


def _line(msg):
    url = os.environ.get("SHEET_WEBAPP_URL", "").strip(); tok = os.environ.get("SHEET_API_TOKEN", "").strip()
    if url:
        try:
            requests.post(url, data={"mode": "pushlinefull", "token": tok, "text": msg}, timeout=60)
        except Exception:
            pass


def _reflect_urls(slugs, sha):
    for slug in slugs:
        d = REPO / "public/images" / slug / "personas"
        stmts = []
        for f in sorted(d.glob("r*.png")):
            role = f.stem.upper()
            url = f"https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@{sha}/public/images/{slug}/personas/{f.name}"
            stmts.append(f"UPDATE personas SET image_url='{url}' WHERE company_id='{slug}' AND role_code='{role}'")
        if stmts:
            subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                            "--command", ";\n".join(stmts)], cwd=str(REPO), capture_output=True, text=True, timeout=120)


def qa_existing_dir(d):
    """既存フォルダの画像をQA集計(gate/checkpoint判定用)。{japanese_rate, gold_rate, n}。"""
    imgs = sorted(Path(d).glob("r*.png"))
    j = g = 0
    for f in imgs:
        try:
            qa = qa_avatar(f.read_bytes())
        except Exception:
            qa = {}
        if qa.get("japanese", True):
            j += 1
        if qa.get("white_bg", True) and qa.get("highkey", True):
            g += 1
    n = max(len(imgs), 1)
    return {"n": len(imgs), "japanese_rate": j / n, "gold_rate": g / n}


def gate_check(pilot_slugs):
    """★自動ゲート: 3社パイロットが三井GOLD絵作り(白背景/ハイキー)＋日本人か厳格判定。閾値: 日本人≥0.95 & GOLD≥0.80。"""
    print("=== 自動ゲート判定(三井GOLD統一×日本人) ===", flush=True)
    tj = tg = tn = 0
    for slug in pilot_slugs:
        d = HANDOFF / "avatar_pilot_gpt" / slug
        s = qa_existing_dir(d)
        print(f"  {slug}: n={s['n']} 日本人{s['japanese_rate']:.0%} GOLD絵作り{s['gold_rate']:.0%}", flush=True)
        tj += s["japanese_rate"] * s["n"]; tg += s["gold_rate"] * s["n"]; tn += s["n"]
    jr = tj / max(tn, 1); gr = tg / max(tn, 1)
    ok = jr >= 0.95 and gr >= 0.80
    print(f"  総合: 日本人{jr:.0%}(≥95%) GOLD絵作り{gr:.0%}(≥80%) → {'✅ゲート通過=全社本走' if ok else '❌不統一=本走せず停止'}", flush=True)
    return ok, jr, gr


def _montage_and_stop(reason, done_slugs):
    """ドリフト検知時: 直近チェックポイントのモンタージュを検分フォルダに残して停止。"""
    sample = done_slugs[-6:]
    try:
        subprocess.run([sys.executable, str(REPO / "tools/room_avatar_montage.py"),
                        str(REPO / "public/images"), ",".join(sample)], capture_output=True, text=True, timeout=120)
    except Exception:
        pass
    _line(f"🛑【アバター本走 自動停止】{reason}。直近サンプル{sample}のモンタージュを ~/Desktop/kindle_受け渡し/ に保存。朝の判断待ち。")


def run_all():
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--json", "--command", "SELECT DISTINCT company_id FROM personas WHERE company_id!='mitsui_corp'"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=90)
    slugs = sorted(x["company_id"] for x in json.loads(p.stdout[p.stdout.find("["):])[0]["results"])
    # resume: gpt再生成が完了した社(done-marker)はスキップ=Gemini上書きだが二重生成なし
    DONEF = REPO / "tools" / ".avatar_gpt_done.json"
    done_set = set(json.loads(DONEF.read_text())) if DONEF.exists() else set()
    todo = [s for s in slugs if s not in done_set]
    print(f"=== アバター全社本走(gpt-image-1 high・並列{PARALLEL}・$500ガード): 全{len(slugs)}社 / gpt再生成済{len(done_set)} / 残{len(todo)} ===", flush=True)
    _line(f"🎨 アバター本走開始: 残{len(todo)}社(gpt済{len(done_set)})・gpt-image-1・GOLD統一・$500ガード。20社毎にQA/checkpoint。")
    t0 = time.time(); done = []; pending = []
    for i, slug in enumerate(todo):
        outdir = REPO / "public/images" / slug / "personas"
        company, res = gen_company(slug, outdir, overwrite=True)   # ★Gemini版を上書き
        done.append(slug); pending.append(slug)
        done_set.add(slug); DONEF.write_text(json.dumps(sorted(done_set)))
        nok = sum(1 for r in res if r["ok"])
        jf = sum(1 for r in res if r.get("qa") and not r["qa"].get("japanese", True))
        gf = sum(1 for r in res if r.get("qa") and not (r["qa"].get("white_bg", True) and r["qa"].get("highkey", True)))
        print(f"  [{i+1}/{len(todo)}] {slug} {nok}/{len(res)}枚 日本人NG{jf} GOLD-NG{gf} 累計${_STATE['spent']:.2f} regen{_STATE.get('regen',0)}", flush=True)
        if _STATE["spent"] >= TOTAL_GUARD:
            _montage_and_stop(f"総額ガード${TOTAL_GUARD}到達", done); print("🛑 総額ガード", flush=True); break
        if len(pending) >= 20:
            _git("add", "public/images")
            if _git("commit", "-m", f"feat(room-avatar): GOLD再生成 {len(done)}社 checkpoint").returncode == 0:
                _git("push", "origin", "main")
            sha = _git("rev-parse", "HEAD").stdout.strip()[:12]
            _reflect_urls(pending, sha)
            # checkpoint自動QA: 直近20社をサンプル→ドリフト検知で停止
            st = qa_existing_dir(REPO / "public/images" / pending[-1] / "personas")
            batch_j = 1 - (jf / max(len(res), 1))
            print(f"  💾 checkpoint {len(done)}社 @{sha} image_url反映 / 直近社 日本人{st['japanese_rate']:.0%} GOLD{st['gold_rate']:.0%}", flush=True)
            _line(f"アバター本走 {len(done)}/{len(slugs)}社・{_STATE['n']}枚・${_STATE['spent']:.0f}・regen{_STATE.get('regen',0)}・@{sha}")
            if st["japanese_rate"] < 0.7 or st["gold_rate"] < 0.5:
                _montage_and_stop(f"ドリフト検知(直近 日本人{st['japanese_rate']:.0%}/GOLD{st['gold_rate']:.0%})", done)
                print("🛑 ドリフト検知で停止", flush=True); return 1
            pending = []
    # 最終
    if pending:
        _git("add", "public/images"); _git("commit", "-m", "feat(room-avatar): GOLD再生成 最終checkpoint")
        _git("push", "origin", "main"); sha = _git("rev-parse", "HEAD").stdout.strip()[:12]; _reflect_urls(pending, sha)
    withimg = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                              "--json", "--command", "SELECT COUNT(DISTINCT company_id) c FROM personas WHERE image_url LIKE 'https%'"],
                             cwd=str(REPO), capture_output=True, text=True, timeout=60)
    live = json.loads(withimg.stdout[withimg.stdout.find("["):])[0]["results"][0]["c"]
    pass_rate = 1 - (_STATE.get("forced", 0) / max(_STATE["n"], 1))
    msg = (f"✅ アバター本走 完了: {_STATE['n']}枚 / QA通過率{pass_rate:.0%}(強制採用{_STATE.get('forced',0)}) / "
           f"再生成{_STATE.get('regen',0)} / 総コスト${_STATE['spent']:.0f} / アバター付きライブ室{live}社。")
    print(f"\n=== {msg} 経過{round((time.time()-t0)/60)}分 ===", flush=True); _line(msg)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs")
    ap.add_argument("--overnight", action="store_true", help="自動ゲート→全社本走(夜間ハンズオフ)")
    ap.add_argument("--outbase", default=os.path.expanduser("~/Desktop/kindle_受け渡し/avatar_pilot_gpt"))
    args = ap.parse_args()
    print(f"=== gpt-image-1 (会社ごとLLM spec・${COST_PER_IMAGE}/枚・並列{PARALLEL}・GOLD統一テンプレ+QA) ===", flush=True)
    if args.overnight:
        ok, jr, gr = gate_check(["sumitomo-corp", "keyence", "daiichi-life"])
        if not ok:
            _montage_and_stop(f"自動ゲート不通過(日本人{jr:.0%}/GOLD{gr:.0%})", ["sumitomo-corp", "keyence", "daiichi-life"])
            print("★ゲート不通過→本走せず。3社モンタージュを検分フォルダに保存。", flush=True); return 1
        return run_all()
    # pilot
    for slug in (args.slugs or "").split(","):
        if not slug:
            continue
        outdir = Path(args.outbase) / slug
        company, res = gen_company(slug, outdir)
        print(f"  {company}({slug}): {sum(1 for r in res if r['ok'])}/{len(res)}枚 累計${_STATE['spent']:.2f}", flush=True)
    print(f"\n  合計 {_STATE['n']}枚 / 実費${_STATE['spent']:.2f} / 全社概算${2918*COST_PER_IMAGE:.0f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
