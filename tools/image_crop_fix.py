"""image_crop_fix.py — 白帯(white_band)FBを「描き直し」でなく「crop」で直す消化役の安全経路(2026-11-19 承認)。

背景: phasec 安全型の自動修正は FB の型に関係なくパネルを丸ごと再生成していた(承認済みの絵を破棄。
  ezaki-glico#1 / ibm-consulting#8 で実証・hard_gate は構図/服装/ロゴ焼込みを素通し)。
  白帯は上端/下端の純白余白を切れば直る。決定的で、絵は1pxも描き変わらない。

判定(すべて機械・保守側。1つでも満たさなければ人のレビューへ):
  1. 余白か絵の一部か: 帯は画像の端(上端 or 下端)から連続し、各行が **全幅で** ほぼ純白
     (>=WHITE が行の ROW_WHITE_MIN 以上・左右端の列も白・行内のばらつき小)。
     窓枠の内側の白のように左右に絵(枠)がある白は「余白でない」=人へ。
  2. 帯の直後は境界線(均一な細い線)を最大 SEAM_MAX 行まで含めて切る。その次の行は明確に絵
     (白比率 <= CONTENT_WHITE_MAX)。だらだら白が続く=グラデーション/絵の白=人へ。
  3. 上限: 切る量の合計が CROP_MAX_FRAC(既定15%)を超えたら人へ(lester-hd#1 の25%は自動不可)。
  4. 文字の焼き込み: Gemini に吹き出し/文字の有無だけ聞く。有り・判定不能・エラーは人へ。
  5. repo の panel ファイルが配信中(D1 image_url)の画像とバイト一致しない=人へ(どの絵を切るのか不定)。
反映(live): 台帳begin → D1 backup → canary before → crop を public/images へ → 当該1ファイルのみ commit
  → push(origin が先行していたら中止) → jsDelivr 40桁SHAで配信・ハッシュ一致確認 → D1 は当該1行の image_url
  のみ UPDATE(旧URL一致条件付き・changes==1 を確認) → canary after(対象外の全社 差分0) → API 確認 → drained。
CLI: python tools/image_crop_fix.py <slug> <koma> [--live]   (既定 dry: 判定と候補画像の保存のみ)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

WHITE = 245
ROW_WHITE_MIN = 0.995
EDGE_COLS = 4
ROW_STD_MAX = 6.0
SEAM_MAX = 4
SEAM_STD_MAX = 14.0
SEAM_CONTRAST_MIN = 30.0
CONTENT_WHITE_MAX = 0.85
MIN_BAND_FRAC = 0.01
CROP_MAX_FRAC = float(os.environ.get("IMG_CROP_MAX_FRAC", "0.15"))
CAND_DIR = REPO / ".backups" / "crop_candidates"
CDN = "https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@{sha}/public/images/{slug}/panel_{koma:02d}.png"
API = "https://10koma-shukatsu-api.oscar-dodds.workers.dev/api/companies/{slug}"


# ---------------------------------------------------------------- 判定(純関数・PIL のみ)
def _row_stats(g, y):
    w = g.size[0]
    px = [g.getpixel((x, y)) for x in range(w)]
    white = sum(1 for p in px if p >= WHITE) / w
    mean = sum(px) / w
    std = (sum((p - mean) ** 2 for p in px) / w) ** 0.5
    edges = all(p >= WHITE for p in px[:EDGE_COLS] + px[-EDGE_COLS:])
    return white, std, edges


def _band(g, rows):
    """rows(端から内側への行番号列)に沿って 余白行数, 境界線行数, 判定メモ を返す。"""
    n = 0
    for y in rows:
        white, std, edges = _row_stats(g, y)
        if white >= ROW_WHITE_MIN and edges and std <= ROW_STD_MAX:
            n += 1
        else:
            break
    if n == 0:
        white, std, edges = _row_stats(g, rows[0])
        note = None
        if white >= 0.85 and not edges:
            note = "端の行は大半が白だが左右端に絵(枠等)がある=絵の内側の白で余白でない"
        elif white >= 0.85:
            note = "端の行は大半が白だが全幅純白でない(グラデーション/絵の白)=余白と断定不可"
        return 0, 0, note
    seam = 0
    for y in rows[n:n + SEAM_MAX]:
        white, std, _ = _row_stats(g, y)
        if white < ROW_WHITE_MIN and std <= SEAM_STD_MAX:
            seam += 1
        else:
            break
    if seam:
        # 境界線は「直後の絵の行と明度が明確に違う細線」に限る(空など均一な絵の先頭行を線と誤認して削らない)
        m = lambda y: sum(g.getpixel((x, y)) for x in range(g.size[0])) / g.size[0]
        nx = rows[n + seam] if n + seam < len(rows) else None
        if nx is None or abs(m(rows[n + seam - 1]) - m(nx)) < SEAM_CONTRAST_MIN:
            seam = 0
    nxt = rows[n + seam] if n + seam < len(rows) else None
    if nxt is None:
        return n, seam, "画像全体が白"
    white, _, _ = _row_stats(g, nxt)
    if white > CONTENT_WHITE_MAX:
        return n, seam, f"余白の直後も白が続く(白比率{white:.2f})=余白と絵の境界が不明確"
    return n, seam, None


def analyze(img_bytes: bytes) -> dict:
    from PIL import Image
    im = Image.open(io.BytesIO(img_bytes))
    im.load()
    g = im.convert("L")
    w, h = g.size
    top, tseam, tnote = _band(g, list(range(h)))
    bot, bseam, bnote = _band(g, list(range(h - 1, -1, -1)))
    res = {"size": [w, h], "top": top, "top_seam": tseam, "bottom": bot, "bottom_seam": bseam,
           "notes": [x for x in (tnote and f"上端: {tnote}", bnote and f"下端: {bnote}") if x]}
    cut_t = top + tseam if top >= MIN_BAND_FRAC * h else 0
    cut_b = bot + bseam if bot >= MIN_BAND_FRAC * h else 0
    res["cut_top"], res["cut_bottom"] = cut_t, cut_b
    res["cut_frac"] = round((cut_t + cut_b) / h, 4)
    if res["notes"]:
        # 余白と断定できない側が1つでもあれば自動で切らない(切る量は参考値)
        res["decision"] = "human"; res["reason"] = " / ".join(res["notes"])
    elif not (cut_t or cut_b):
        res["decision"] = "none"; res["reason"] = f"上端/下端に純白余白なし(>= {MIN_BAND_FRAC:.0%})"
    elif res["cut_frac"] > CROP_MAX_FRAC:
        res["decision"] = "human"; res["reason"] = f"切る量 {res['cut_frac']:.1%} が上限 {CROP_MAX_FRAC:.0%} 超"
    else:
        res["decision"] = "crop"; res["reason"] = f"上{cut_t}行/下{cut_b}行({res['cut_frac']:.1%})を切除"
    return res


def crop_bytes(img_bytes: bytes, cut_top: int, cut_bottom: int) -> bytes:
    from PIL import Image
    im = Image.open(io.BytesIO(img_bytes))
    im.load()
    w, h = im.size
    out = im.crop((0, cut_top, w, h - cut_bottom))
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


_TEXT_PROMPT = (
    "この漫画パネル画像に、画像として描き込まれた(焼き込まれた)文字はありますか。"
    "吹き出しの中の文字・ナレーション文字・キャプション・看板やロゴの読める文字を含みます。"
    "1文字でも読める文字や吹き出しがあれば has_text=true。確信が持てなければ true。\n"
    'JSONのみ: {"has_text": true|false, "confidence": 0.0-1.0, "what": "短い日本語"}'
)


def text_check(img_bytes: bytes) -> dict:
    """焼き込み文字/吹き出しの有無。エラー・判定不能は has_text=True(安全側=人へ)。"""
    from PIL import Image
    from google.genai import types
    import image_staleness as ST
    try:
        img = Image.open(io.BytesIO(img_bytes)); img.load()
        r = ST._client().models.generate_content(
            model="gemini-3-flash-preview", contents=[img, _TEXT_PROMPT],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0))
        d = json.loads((r.text or "").strip() or "{}")
        if not isinstance(d.get("has_text"), bool):
            return {"has_text": True, "what": "判定不能→安全側"}
        return {"has_text": d["has_text"], "confidence": float(d.get("confidence", 0)), "what": str(d.get("what", ""))[:80]}
    except Exception as e:
        return {"has_text": True, "what": f"error→安全側:{type(e).__name__}: {e}"[:160]}


# ---------------------------------------------------------------- 反映
def _git(*a, check=True):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=check)


def _d1_exec(sql: str) -> dict:
    import deploy_salary as D
    p = D.wrangler(["--command", sql, "--json"])
    s = (p.stdout or "").find("[")
    try:
        data = json.loads(p.stdout[s:])
        return data[0]
    except Exception:
        raise RuntimeError(f"D1 exec 失敗 rc={p.returncode} stdout={(p.stdout or '')[-200:]!r} stderr={(p.stderr or '')[-200:]!r}")


def _fetch(url, tries=1):
    import requests
    r = requests.get(url, timeout=60)
    return r.status_code, r.content


def to_human(key: str, company: str, reason: str, gas=None) -> None:
    import image_fix_ledger as LG
    LG.escalate_human(key, f"[crop判定] {reason}", company=company, gas=gas)


def crop_fix_one(slug: str, koma: int, company: str = "", detail: str = "", dry: bool = True, gas=None) -> dict:
    import image_fix_ledger as LG
    import image_staleness as ST
    k = LG.key(slug, koma)
    rec = {"slug": slug, "koma": koma, "company": company, "method": "crop", "deployed": False,
           "escalate": None, "dry": dry}
    blk, why = LG.blocked(k)
    if blk:
        rec["escalate"] = f"台帳: {why}"; rec["ledger_blocked"] = True
        return rec
    url = ST.deployed_image_url(slug, koma)
    if not url:
        raise RuntimeError(f"D1 に image_url 無し {k}(取得失敗か不在かを区別できない→例外)")
    code, served = _fetch(url)
    if code != 200 or not served:
        raise RuntimeError(f"配信画像取得失敗 {code} {url}")
    rec["served_url"], rec["served_sha1"] = url, hashlib.sha1(served).hexdigest()[:8]
    a = analyze(served)
    rec["analysis"] = a
    if a["decision"] == "none":
        rec["note"] = a["reason"]          # 白帯なし=陳腐化。再生成もしない
        return rec
    if a["decision"] == "human":
        rec["escalate"] = f"人レビュー: {a['reason']}"
        if not dry:
            to_human(k, company, a["reason"], gas)
        return rec
    tc = text_check(served)
    rec["text_check"] = tc
    if tc["has_text"]:
        reason = f"焼き込み文字/吹き出しの可能性({tc.get('what')})=text_leak は人の目視必須"
        rec["escalate"] = f"人レビュー: {reason}"
        if not dry:
            to_human(k, company, reason, gas)
        return rec
    out = crop_bytes(served, a["cut_top"], a["cut_bottom"])
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    cand = CAND_DIR / f"{slug}_panel_{koma:02d}_crop.png"
    cand.write_bytes(out)
    rec["candidate"] = str(cand)
    dst = REPO / "public" / "images" / slug / f"panel_{koma:02d}.png"
    if not dst.exists() or dst.read_bytes() != served:
        reason = "repo の panel ファイルが配信中の画像と不一致(どの絵を切るか不定)"
        rec["escalate"] = f"人レビュー: {reason}"
        if not dry:
            to_human(k, company, reason, gas)
        return rec
    import image_approval as IA          # 【承認台帳 2026-11-20 ■4】切る元の絵が承認済みであること
    old_blob = IA.blob_of_file(dst)
    if not IA.is_approved(str(dst.relative_to(REPO)), old_blob):
        reason = "配信中の絵が承認台帳に無い(人QA待ち候補の可能性)=切らずに人へ"
        rec["escalate"] = f"人レビュー: {reason}"
        if not dry:
            to_human(k, company, reason, gas)
        return rec
    if dry:
        rec["note"] = f"DRY: {a['reason']} → 候補 {cand.name}(live なら push→D1→canary)"
        return rec

    # ===== live =====
    import deploy_salary as D
    rec["_ledger_keys"] = [k]
    rec["ledger_attempt"] = LG.begin(k, "crop", detail, company)
    D.backup_d1(slug)
    before = D.canary_snapshot({slug})
    _git("fetch", "-q", "origin", "main")
    ahead = _git("rev-list", "--count", "HEAD..origin/main").stdout.strip()
    if ahead != "0":
        rec["escalate"] = f"origin/main が {ahead} コミット先行 → 中止(次回)"; return rec
    dst.write_bytes(out)
    rel = str(dst.relative_to(REPO))
    IA.approve(rel, IA.blob_of_file(rel), "派生(白帯crop)", f"承認済み {old_blob[:12]} の白帯を機械的に除去({a['reason']})",
               derived_from=old_blob)
    led = str(IA.LEDGER.relative_to(REPO))
    _git("add", rel, led)
    msg = (f"fix(image:{slug}): koma{koma:02d} 白帯をcrop除去(自動・{a['reason']})\n\n"
           f"再生成なし(絵は配信中のまま)。image_crop_fix.py\n\n"
           f"Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    c = _git("commit", "-m", msg, "--", rel, led, check=False)
    if c.returncode != 0:
        raise RuntimeError(f"commit 失敗: {(c.stdout + c.stderr)[-300:]}")
    sha = _git("rev-parse", "HEAD").stdout.strip()
    _git("push", "-q", "origin", "main")
    rec["commit"] = sha
    LG.note(k, last_commit=sha)
    new = CDN.format(sha=sha, slug=slug, koma=koma)
    for _ in range(36):
        code, b = _fetch(new)
        if code == 200 and b == out:
            break
        time.sleep(5)
    else:
        rec["escalate"] = f"jsDelivr 未配信/不一致(180s) {new}"; return rec
    old = url.replace("'", "''")
    r = _d1_exec(f"UPDATE company_panels SET image_url='{new}' WHERE company_id='{slug}' "
                 f"AND panel_num={int(koma)} AND image_url='{old}'")
    ch = (r.get("meta") or {}).get("changes")
    rec["d1_changes"], rec["d1_written_at"] = ch, time.strftime("%Y-%m-%d %H:%M:%S")
    if not r.get("success") or ch != 1:
        rec["escalate"] = f"D1 UPDATE changes={ch}(期待1) → 未反映"; return rec
    after = D.canary_snapshot({slug})
    drift = D.canary_diff(before, after)
    rec["canary_drift"] = drift
    if drift:
        rec["escalate"] = f"🛑canary: 対象外変化 {drift}"; return rec
    code, j = _fetch(API.format(slug=slug) + f"?_cb={int(time.time())}")
    try:
        p = [x for x in json.loads(j).get("panels", []) if int(x["panel_num"]) == int(koma)][0]
        api_ok = p.get("image_url") == new
    except Exception:
        api_ok = False
    rec["api_ok"] = api_ok
    if not api_ok:
        rec["escalate"] = "API の image_url 未更新"; return rec
    rec["deployed"] = True
    return rec


def selftest() -> int:
    from PIL import Image, ImageDraw
    def img(draw):
        im = Image.new("RGB", (480, 640), (255, 255, 255))
        draw(ImageDraw.Draw(im))
        b = io.BytesIO(); im.save(b, format="PNG"); return b.getvalue()
    def art(d, y0):   # y0 から下は絵(暗い・ばらつきあり)
        for y in range(y0, 640, 4):
            d.rectangle([0, y, 479, y + 3], fill=((y * 7) % 200, 90, 120))
    cases = [
        ("純白余白10%→crop", lambda d: art(d, 64), "crop"),
        ("余白+境界線2行→線ごとcrop", lambda d: (art(d, 66), d.rectangle([0, 64, 479, 65], fill=(40, 40, 40))), "crop"),
        ("窓枠内の白(左右に枠)→人", lambda d: (art(d, 160), d.rectangle([0, 0, 20, 160], fill=(120, 80, 40)),
                                         d.rectangle([459, 0, 479, 160], fill=(120, 80, 40))), "human"),
        ("余白25%→上限超で人", lambda d: art(d, 160), "human"),
        ("余白なし→none", lambda d: art(d, 0), "none"),
        ("余白の直後も白が続く→人", lambda d: (art(d, 200), [d.point((x, y), fill=(0, 0, 0)) for y in range(64, 200)
                                                 for x in (100,)]), "human"),
        ("均一な空(先頭行)を境界線と誤認しない", lambda d: (art(d, 70), d.rectangle([0, 64, 479, 69], fill=(150, 190, 230))), "crop"),
    ]
    ok = True
    for name, dr, want in cases:
        a = analyze(img(dr))
        good = a["decision"] == want
        ok &= good
        print(f"  {'✅' if good else '❌'} {name}: {a['decision']} ({a['reason'][:60]})")
    b = img(lambda d: art(d, 64)); a = analyze(b)
    from PIL import Image as _I
    out = _I.open(io.BytesIO(crop_bytes(b, a["cut_top"], a["cut_bottom"])))
    good = out.size == (480, 576)
    ok &= good
    print(f"  {'✅' if good else '❌'} crop後サイズ {out.size}(期待 480x576・絵は不変)")
    src = (TOOLS / "phase_c_auto.py").read_text(encoding="utf-8")
    body = src[src.index("def _run_batch_body"):]
    body = body[:body.index("\ndef ")]
    good = "PCI.run_one(" not in body and "CROP.crop_fix_one(" in body
    ok &= good
    print(f"  {'✅' if good else '❌'} 消化役の安全型経路に再生成(PCI.run_one)が無く crop のみ")
    print("=== image_crop_fix selftest:", "ALL PASS ✅" if ok else "FAIL ❌", "===")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    if len(sys.argv) < 3:
        print(__doc__); raise SystemExit(2)
    import phase_c_image_fix as PCI
    PCI._load_env()
    import image_fix_ledger as LG
    r = crop_fix_one(sys.argv[1], int(sys.argv[2]), dry="--live" not in sys.argv, gas=PCI.gas)
    for _k in r.get("_ledger_keys") or []:
        LG.succeed(_k, r.get("commit") or "") if r.get("deployed") else LG.fail(_k, r.get("escalate") or "未反映", PCI.gas)
    print(json.dumps({k: v for k, v in r.items() if k != "_ledger_keys"}, ensure_ascii=False, indent=1))
