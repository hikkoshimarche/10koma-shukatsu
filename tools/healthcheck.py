#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""healthcheck.py — 本番全ページ/全API 夜間巡回(検知と報告のみ・修正しない)。

対象: 全400社 company ページ+API+画像10枚 / 全業界ハブ / 主要ページ / 全APIエンドポイント。
検知: HTTP!=200(404等) / 壊れ画像(画像URL!=200) / 空レスポンス / 応答3秒超 / console error(Chrome headless+CDP・best-effort)。
出力: reports/health_<日時>.md (異常0なら「全て正常」1行・異常あれば 社名/URL/種別 のリスト)。
運用: 1req/秒 / checkpoint(_state.json・--resumeで再開) / caffeinate はrunner側。修正は一切しない。

レポートは public repo に push しない(内部レポート=commit禁止ルール)。reports/ は .gitignore 済。
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
HDIR = ROOT / "health"
RDIR = HDIR / "reports"
STATE = HDIR / "_state.json"
REPO = ROOT.parent
COMPANIES_JSON = REPO / "public" / "companies.json"

PAGES = "https://10koma-shukatsu.pages.dev"
API = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
SAMPLE_COMPANY = "mitsubishi-corp"
DATA_COMPANY = "abeam"          # datasheet/es_kit を実際に持つ社(真の200プローブ)
SAMPLE_INDUSTRY = "sogo-shosha"
HC_USER = "__healthcheck__"

# 実在する業界10コマ(業界ハブAPI /api/industries/<slug> はこの16のみ・ハイフン形式)。
# 変化時は D1: SELECT replace(id,'industry_10koma__','') FROM companies WHERE id LIKE 'industry_10koma__%'
INDUSTRY_10KOMA_SLUGS = [
    "ad-media", "consulting", "deeptech-space-ai", "education-hr", "finance", "food-beverage",
    "infra-energy", "it-ai-saas-game", "manufacturer", "medical-healthcare",
    "realestate-construction", "retail", "senmon-shosha", "sogo-shosha", "startup", "transport-logistics",
]

TIMEOUT = 12
SLOW = 3.0            # 秒: これ超過で slow
RATE = 1.0           # 1 req/秒
EMPTY_PAGE_BYTES = 500   # HTMLページがこれ未満なら空疑い
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

JST = timezone(timedelta(hours=9))
_last_req = [0.0]


def throttle():
    dt = time.time() - _last_req[0]
    if dt < RATE:
        time.sleep(RATE - dt)
    _last_req[0] = time.time()


def hit(url, kind, label, expect="ok", want_panels=False):
    """1 URL を検査し issue リストを返す。
    expect: 'ok'=200必須(空はOK) / 'data'=200かつ非空JSON必須 / 'graceful'=5xx/timeoutのみ異常(4xx/空はOK)。"""
    throttle()
    issues = []
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "tokyari-healthcheck/1"})
        dt = r.elapsed.total_seconds()
        code = r.status_code
        body = r.content or b""
    except requests.Timeout:
        return _ret([{"kind": "timeout", "type": f">{TIMEOUT}s timeout", "label": label, "url": url, "target_kind": kind}], want_panels)
    except Exception as e:
        return _ret([{"kind": "error", "type": f"req失敗:{type(e).__name__}", "label": label, "url": url, "target_kind": kind}], want_panels)

    if dt > SLOW:
        issues.append({"kind": "slow", "type": f"slow {dt:.1f}s", "label": label, "url": url, "target_kind": kind})
    if code != 200:
        # graceful は 4xx(データ未投入の正常応答)を異常にしない。5xx とページ系は常に異常。
        if expect == "graceful" and 400 <= code < 500:
            return _ret(issues, want_panels)
        issues.append({"kind": "status", "type": f"HTTP {code}", "label": label, "url": url, "target_kind": kind})
        return _ret(issues, want_panels)
    # ページ空
    if kind in ("page", "hub", "company_page") and len(body) < EMPTY_PAGE_BYTES:
        issues.append({"kind": "empty", "type": f"空/極小 {len(body)}B", "label": label, "url": url, "target_kind": kind})
    # JSON検査
    if expect in ("data",) or want_panels:
        try:
            j = r.json()
        except Exception:
            issues.append({"kind": "empty", "type": "JSON parse不可", "label": label, "url": url, "target_kind": kind})
            return _ret(issues, want_panels)
        if isinstance(j, dict) and (j.get("error") or j.get("Error")):
            issues.append({"kind": "api_error", "type": f"error:{str(j.get('error'))[:40]}", "label": label, "url": url, "target_kind": kind})
        if expect == "data" and (j is None or (isinstance(j, (list, dict)) and len(j) == 0)):
            issues.append({"kind": "empty", "type": "空JSON([]/{})", "label": label, "url": url, "target_kind": kind})
        if want_panels:
            panels = (j.get("panels") if isinstance(j, dict) else None) or []
            if len(panels) != 10:
                issues.append({"kind": "panels", "type": f"panels={len(panels)}(≠10)", "label": label, "url": url, "target_kind": kind})
            return issues, [p.get("image_url") for p in panels if p.get("image_url")]
    return _ret(issues, want_panels)


def _ret(issues, want_panels):
    return (issues, []) if want_panels else issues


def check_image(url, label):
    throttle()
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True, headers={"User-Agent": "tokyari-healthcheck/1"})
        code = r.status_code
        clen = r.headers.get("Content-Length")
        r.close()
    except Exception as e:
        return {"kind": "broken_image", "type": f"img req失敗:{type(e).__name__}", "label": label, "url": url, "target_kind": "image"}
    if code != 200:
        return {"kind": "broken_image", "type": f"画像 HTTP {code}", "label": label, "url": url, "target_kind": "image"}
    if clen is not None and int(clen) < 1000:
        return {"kind": "broken_image", "type": f"画像 極小 {clen}B", "label": label, "url": url, "target_kind": "image"}
    return None


# ---------------- console error (Chrome headless + CDP, best-effort) ----------------
def console_errors_for(urls, port=9333):
    """urls の各ページで JS console error / 未捕捉例外 を収集。失敗時は ('skipped', reason)。"""
    import tempfile, shutil
    try:
        import asyncio
        import websockets  # noqa
    except Exception as e:
        return None, f"websockets未導入:{e}"
    if not Path(CHROME).exists():
        return None, "Chrome.app無し"
    udir = tempfile.mkdtemp(prefix="hc_chrome_")
    proc = subprocess.Popen(
        [CHROME, "--headless=new", f"--remote-debugging-port={port}", f"--user-data-dir={udir}",
         "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-extensions",
         "--mute-audio", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = {}
    try:
        base = f"http://127.0.0.1:{port}"
        for _ in range(40):
            try:
                requests.get(base + "/json/version", timeout=1); break
            except Exception:
                time.sleep(0.25)
        else:
            return None, "CDP起動せず"
        import asyncio
        result = asyncio.run(_cdp_run(base, urls))
    except Exception as e:
        return None, f"CDP例外:{type(e).__name__}:{str(e)[:60]}"
    finally:
        proc.terminate()
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(udir, ignore_errors=True)
    return result, None


async def _cdp_run(base, urls):
    import asyncio, websockets
    out = {}
    for label, url in urls:
        errs = []
        try:
            tab = requests.get(base + "/json/new?about:blank", timeout=5).json()
            ws_url = tab["webSocketDebuggerUrl"]; tid = tab["id"]
        except Exception as e:
            out[label] = {"url": url, "skipped": f"tab作成失敗:{e}"}; continue
        try:
            async with websockets.connect(ws_url, max_size=8_000_000, open_timeout=8) as ws:
                mid = [0]
                async def send(method, params=None):
                    mid[0] += 1
                    await ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
                await send("Runtime.enable"); await send("Log.enable"); await send("Page.enable")
                await send("Page.navigate", {"url": url})
                deadline = time.time() + 8
                while time.time() < deadline:
                    try:
                        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(0.2, deadline - time.time())))
                    except (asyncio.TimeoutError, Exception):
                        break
                    m = msg.get("method")
                    if m == "Runtime.exceptionThrown":
                        d = msg["params"].get("exceptionDetails", {})
                        txt = d.get("exception", {}).get("description") or d.get("text") or "exception"
                        errs.append(str(txt).split("\n")[0][:160])
                    elif m == "Runtime.consoleAPICalled" and msg["params"].get("type") == "error":
                        args = msg["params"].get("args", [])
                        txt = " ".join(str(a.get("value") or a.get("description") or "") for a in args)
                        if txt.strip(): errs.append("console.error: " + txt[:160])
                    elif m == "Log.entryAdded":
                        e = msg["params"].get("entry", {})
                        if e.get("level") == "error":
                            errs.append("log: " + str(e.get("text", ""))[:160])
        except Exception as e:
            out[label] = {"url": url, "skipped": f"ws失敗:{type(e).__name__}"}
        else:
            # 重複除去
            seen = []
            for x in errs:
                if x not in seen: seen.append(x)
            out[label] = {"url": url, "errors": seen}
        finally:
            try: requests.get(base + f"/json/close/{tid}", timeout=3)
            except Exception: pass
    return out


# ---------------- targets ----------------
def load_companies():
    d = json.load(open(COMPANIES_JSON, encoding="utf-8"))
    out = []
    for _cat, lst in d.items():
        if isinstance(lst, list):
            for c in lst:
                if c.get("id"):
                    out.append((c["id"], c.get("name", c["id"])))
    # 重複id除去(業界重複掲載対策)
    seen = {}
    for cid, nm in out:
        seen.setdefault(cid, nm)
    return sorted(seen.items())


TOP_PAGES = ["home", "hub", "gyokai", "quiz", "mypage", "shindan", "company-list", "compare",
             "datasheet", "es_kit", "es_guide", "bookmarks", "videos", "room", "chat",
             "obs", "omamori", "howto", "industry", "index"]


def api_targets():
    """(tid, url, expect) — expect: data=非空必須 / ok=200必須 / graceful=5xxのみ異常。"""
    c = SAMPLE_COMPANY; d = DATA_COMPANY; ind = SAMPLE_INDUSTRY
    return [
        ("api:health", f"{API}/api/health", "ok"),
        ("api:industries", f"{API}/api/industries", "data"),
        ("api:companies", f"{API}/api/companies", "data"),
        ("api:company-list", f"{API}/api/company-list", "data"),
        ("api:videos", f"{API}/api/videos", "ok"),
        ("api:recent-companies", f"{API}/api/recent-companies", "ok"),
        (f"api:quiz({c})", f"{API}/api/quiz?company_id={c}", "ok"),
        (f"api:datasheet({d})", f"{API}/api/datasheet?id={d}", "data"),
        (f"api:es-kit({d})", f"{API}/api/es-kit?id={d}", "data"),
        (f"api:company-news({c})", f"{API}/api/company-news?company_id={c}", "graceful"),
        (f"api:company-selection({c})", f"{API}/api/company-selection?company_id={c}", "graceful"),
        (f"api:industry-selection-schedule({ind})", f"{API}/api/industry-selection-schedule?industry_id={ind}", "graceful"),
        ("api:compare", f"{API}/api/compare?ids={c},mitsui-bussan", "ok"),
        ("api:mypage(hc)", f"{API}/api/mypage?user_id={HC_USER}", "graceful"),
        ("api:profile(hc)", f"{API}/api/profile?user_id={HC_USER}", "graceful"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--no-console", action="store_true")
    ap.add_argument("--limit-companies", type=int, default=0, help="動作確認用: 先頭N社のみ")
    ap.add_argument("--console-sample", type=int, default=12)
    args = ap.parse_args()

    HDIR.mkdir(exist_ok=True); RDIR.mkdir(exist_ok=True)
    state = {"issues": [], "done": [], "started": datetime.now(JST).isoformat(), "counts": {}}
    if args.resume and STATE.exists():
        state = json.load(open(STATE, encoding="utf-8"))
    done = set(state["done"])
    issues = state["issues"]
    n_targets = 0

    def save():
        state["done"] = sorted(done); state["issues"] = issues
        json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)

    def do(tid, fn):
        nonlocal n_targets
        n_targets += 1
        if tid in done:
            return
        r = fn()
        if isinstance(r, tuple):
            r = r[0]
        if isinstance(r, list):
            issues.extend(r)
        elif isinstance(r, dict):
            issues.append(r)
        done.add(tid)
        if n_targets % 25 == 0:
            save(); print(f"  ...{n_targets} targets, issues={len(issues)}", flush=True)

    print("=== healthcheck 開始 ===", flush=True)
    # A) 主要ページ
    for p in TOP_PAGES:
        do(f"page:{p}", lambda p=p: hit(f"{PAGES}/{p}", "page", f"page:{p}"))
    # B) 業界ハブ(gyokai メインページ + 実在16業界の gyokai?id ページ + 業界10コマAPI)
    inds = INDUSTRY_10KOMA_SLUGS
    state["counts"]["industries"] = len(inds)
    for s in inds:
        do(f"hub:gyokai:{s}", lambda s=s: hit(f"{PAGES}/gyokai?id={s}", "hub", f"hub:gyokai:{s}"))
        do(f"hub:api:{s}", lambda s=s: hit(f"{API}/api/industries/{s}", "hub", f"業界API:{s}", expect="data"))
    # C) API エンドポイント
    for tid, url, expect in api_targets():
        do(tid, lambda url=url, expect=expect: hit(url, "api", url.replace(API, ""), expect=expect))
    # D) 全社: ページ + API(10panels) + 画像10枚
    comps = load_companies()
    if args.limit_companies:
        comps = comps[:args.limit_companies]
    state["counts"]["companies"] = len(comps)
    for cid, nm in comps:
        do(f"cpage:{cid}", lambda cid=cid, nm=nm: hit(f"{PAGES}/company?id={cid}", "company_page", nm))
        # API + 画像
        if f"capi:{cid}" not in done:
            n_targets += 1
            res = hit(f"{API}/api/companies/{cid}", "api", f"{nm}(API)", expect="data", want_panels=True)
            api_issues, imgs = res if isinstance(res, tuple) else (res, [])
            issues.extend(api_issues)
            for i, iu in enumerate(imgs, 1):
                bad = check_image(iu, f"{nm} 画像{i}")
                if bad: issues.append(bad)
            done.add(f"capi:{cid}")
            if n_targets % 25 == 0:
                save(); print(f"  ...{n_targets} targets ({cid}), issues={len(issues)}", flush=True)

    # E) console error (best-effort・テンプレページ + 業界 + 社サンプル)
    console_note = ""
    if not args.no_console:
        sample_c = [c for c in comps[:: max(1, len(comps)//max(1, args.console_sample))]][:args.console_sample]
        curls = ([(f"page:{p}", f"{PAGES}/{p}") for p in TOP_PAGES] +
                 [(f"gyokai:{s}", f"{PAGES}/gyokai?id={s}") for s in inds[:6]] +
                 [(f"company:{cid}", f"{PAGES}/company?id={cid}") for cid, _ in sample_c])
        print(f"=== console巡回 {len(curls)}ページ (Chrome headless) ===", flush=True)
        cres, cerr = console_errors_for(curls)
        if cres is None:
            console_note = f"console検査 skip: {cerr}"
            print("  " + console_note, flush=True)
        else:
            for label, info in cres.items():
                for e in info.get("errors", []):
                    issues.append({"kind": "console_error", "type": f"console: {e}", "label": label, "url": info["url"], "target_kind": "console"})
            state["counts"]["console_pages"] = len(cres)

    save()
    write_report(issues, n_targets, state, console_note)
    print(f"=== 完了 targets={n_targets} issues={len(issues)} ===", flush=True)


def write_report(issues, n_targets, state, console_note):
    now = datetime.now(JST)
    fn = RDIR / f"health_{now.strftime('%Y%m%d_%H%M')}.md"
    lines = [f"# 夜間ヘルスチェック レポート {now.strftime('%Y-%m-%d %H:%M JST')}", ""]
    lines.append(f"- 巡回対象: {n_targets} targets "
                 f"(社{state['counts'].get('companies','?')} / 業界{state['counts'].get('industries','?')} / "
                 f"主要ページ{len(TOP_PAGES)} / API{len(api_targets())})")
    lines.append(f"- 開始 {state.get('started','')} → 終了 {now.isoformat()}")
    if console_note:
        lines.append(f"- ⚠ {console_note}")
    lines.append("")
    if not issues:
        lines.append("## ✅ 全て正常（異常0）")
    else:
        # 種別ごとに集約
        by_kind = {}
        for it in issues:
            by_kind.setdefault(it["kind"], []).append(it)
        lines.append(f"## ⚠ 異常 {len(issues)}件（{len(by_kind)}種別）")
        lines.append("")
        order = ["status", "broken_image", "panels", "empty", "api_error", "timeout", "slow", "console_error", "error"]
        for k in order + [x for x in by_kind if x not in order]:
            if k not in by_kind: continue
            arr = by_kind[k]
            lines.append(f"### {k} — {len(arr)}件")
            for it in arr[:200]:
                lines.append(f"- **{it.get('label','')}** — {it['type']} — `{it['url']}`")
            if len(arr) > 200:
                lines.append(f"- …他 {len(arr)-200}件")
            lines.append("")
    fn.write_text("\n".join(lines), encoding="utf-8")
    (RDIR / "LATEST.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"レポート: {fn}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
