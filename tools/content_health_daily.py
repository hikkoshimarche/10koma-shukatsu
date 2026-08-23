#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""content_health_daily.py — 毎日のコンテンツ健全性チェック(read-only・修正しない)。

チェック:
  (1) 全社10コマ画像の実在(HEAD・非200=壊れ画像)
  (2) 全400社×機能(company/datasheet/es_kit/quiz/room)のURL健全性(非200)
  (3) 各機能の充足数(datasheets/es_kits/quiz社/room社/panels社)
  (4) 前回実行との差分(新規404・充足数の増減)

通知(既存 LINE経路 GAS pushoscar):
  ・異常0の日は送らない(ノイズ抑制)
  ・「新規404が出た」or「充足数が減った」時のみ送る(何が/何件/いつから を含む)
  ・--force-notify で強制送信(テスト用)。送信は応答 sent=true を実値確認するまで成功としない。

過去の教訓:
  ・launchd はPATHが違う(2026-07-01/07-24障害) → npx/wrangler は shutil.which / nvm glob で絶対解決。
  ・「成功応答なのに中身が空」の罠 → LINE送信は sent:true、D1/HTTPは実値を確認。
状態: tools/content_health/state.json (failing{url:first_seen}, counts, last_run)。
"""
from __future__ import annotations
import argparse, glob, json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests

ROOT = Path(__file__).resolve().parent.parent
HDIR = Path(__file__).resolve().parent / "content_health"
HDIR.mkdir(exist_ok=True)
STATE = HDIR / "state.json"
LOG = HDIR / "runs.log"
ENV_PHASE_C = Path(__file__).resolve().parent / ".env.phase_c"

PAGES = "https://10koma-shukatsu.pages.dev"
API = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
JST = timezone(timedelta(hours=9))
NOW = datetime.now(JST)
NOW_S = NOW.strftime("%Y-%m-%d %H:%M")
UA = {"User-Agent": "tokyari-content-health/1"}
WORKERS = 14


def log(msg):
    line = f"[{NOW_S}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------- PATH安全な npx/wrangler 解決(launchd対策) ----------
def resolve_npx():
    p = shutil.which("npx")
    if p:
        return p
    cands = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/npx")))
    if cands:
        return cands[-1]
    for c in ("/opt/homebrew/bin/npx", "/usr/local/bin/npx"):
        if os.path.exists(c):
            return c
    raise RuntimeError("npx が見つからない(PATH解決失敗)")


NPX = resolve_npx()


def d1(sql):
    r = subprocess.run([NPX, "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    t = r.stdout or ""
    i = t.find("[")
    if i < 0:
        raise RuntimeError(f"D1 read失敗: {(r.stderr or t)[-400:]}")
    rows = []
    for b in json.loads(t[i:]):
        if isinstance(b, dict):
            rows.extend(b.get("results", []))
    return rows


def load_env():
    for f in (ENV_PHASE_C,):
        if f.exists():
            for line in f.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())


# ---------- LINE通知(GAS pushoscar・sent実値確認) ----------
def notify_oscar(text):
    url = os.environ.get("SHEET_WEBAPP_URL", "").strip()
    tok = os.environ.get("SHEET_API_TOKEN", "").strip()
    if not url:
        log("LINE未設定(SHEET_WEBAPP_URL無し) → 送信skip"); return False
    try:
        r = requests.get(url, params={"mode": "pushoscar", "token": tok, "text": text[:4900]}, timeout=40)
        j = r.json()
    except Exception as e:
        log(f"LINE送信例外: {e}"); return False
    sent = bool(j.get("sent"))
    log(f"LINE pushoscar 応答: sent={sent} reason={j.get('reason','')} (http={r.status_code})")
    return sent


def _head_once(url):
    r = requests.head(url, timeout=12, headers=UA, allow_redirects=True)
    if r.status_code == 405:  # HEAD不可はGETで再確認
        r = requests.get(url, timeout=12, headers=UA, stream=True); r.close()
    return r.status_code


def _get_once(url):
    return requests.get(url, timeout=12, headers=UA, allow_redirects=True).status_code


def confirmed_status(url, fn, tries=3):
    """非200は一過性のネット/CDN瞬断を疑い、最大tries回リトライして確定する
    (無人ジョブが人にアラートを出すので誤検知を潰す)。1回でも200が出れば200を返す。"""
    last = "ERR"
    for i in range(tries):
        try:
            s = fn(url)
        except Exception:
            s = "ERR"
        if s == 200:
            return 200
        last = s
        if i < tries - 1:
            time.sleep(0.6)
    return last


def head(url):
    return confirmed_status(url, _head_once)


def get_status(url):
    return confirmed_status(url, _get_once)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-notify", action="store_true", help="異常有無に関わらず結果を送信(テスト用)")
    args = ap.parse_args()
    load_env()
    log(f"=== content_health 開始 (npx={NPX}) ===")

    # (3) 充足数
    counts = {}
    counts["datasheets"] = d1("SELECT count(*) n FROM datasheets")[0]["n"]
    counts["es_kits"] = d1("SELECT count(*) n FROM es_kits")[0]["n"]
    counts["quiz_companies"] = d1("SELECT count(DISTINCT set_id) n FROM quiz_questions WHERE set_type='company'")[0]["n"]
    counts["room_companies"] = d1("SELECT count(DISTINCT company_slug) n FROM room_personas")[0]["n"]
    counts["panel_companies"] = d1("SELECT count(DISTINCT company_id) n FROM company_panels WHERE company_id NOT LIKE 'industry_10koma__%'")[0]["n"]
    log(f"充足数: {counts}")

    # (1) 画像実在: 全10コマ image_url を HEAD
    imgs = [r["image_url"] for r in d1("SELECT image_url FROM company_panels WHERE company_id NOT LIKE 'industry_10koma__%' AND image_url IS NOT NULL")]
    log(f"画像HEAD対象: {len(imgs)}枚")
    img_fail = {}
    def chk_img(u):
        s = head(u)
        return (u, s) if s != 200 else None
    for res in ThreadPoolExecutor(max_workers=WORKERS).map(chk_img, imgs):
        if res:
            img_fail[f"img::{res[0]}"] = res[1]
    log(f"壊れ画像(非200): {len(img_fail)}枚")

    # (2) URL健全性: 全社 company page + datasheet/es_kit/quiz/room API
    comps = [(r["id"]) for r in d1("SELECT DISTINCT id FROM companies WHERE id NOT LIKE 'industry_10koma__%'")]
    log(f"URL健全性対象: {len(comps)}社 × 5機能")
    url_fail = {}
    def chk_urls(cid):
        out = []
        checks = [
            (f"company::{cid}", f"{PAGES}/company?id={cid}", get_status),
            (f"datasheet::{cid}", f"{API}/api/datasheet?id={cid}", get_status),
            (f"es_kit::{cid}", f"{API}/api/es-kit?id={cid}", get_status),
            (f"quiz::{cid}", f"{API}/api/quiz?company_id={cid}", get_status),
            (f"room::{cid}", f"{API}/api/room/personas/{cid}", get_status),
        ]
        for key, u, fn in checks:
            s = fn(u)
            if s != 200:
                out.append((key, s))
        return out
    for res in ThreadPoolExecutor(max_workers=WORKERS).map(chk_urls, comps):
        for key, s in res:
            url_fail[key] = s

    # 現在の失敗集合(画像 + URL)
    current_fail = {**img_fail, **{f"url::{k}": v for k, v in url_fail.items()}}
    log(f"URL非200: {len(url_fail)}件 / 現在の失敗合計(画像+URL): {len(current_fail)}")

    # (4) 前回との差分
    prev = {}
    if STATE.exists():
        try:
            prev = json.loads(STATE.read_text())
        except Exception:
            prev = {}
    prev_fail = prev.get("failing", {})     # {key: {"code":..,"since":..}}
    prev_counts = prev.get("counts", {})
    first_run = not bool(prev)

    # 新規失敗(前回に無い) + since付与(既存はsince保持)
    failing_out = {}
    new_fail = {}
    for key, code in current_fail.items():
        if key in prev_fail:
            failing_out[key] = {"code": code, "since": prev_fail[key].get("since", NOW_S)}
        else:
            failing_out[key] = {"code": code, "since": NOW_S}
            if not first_run:
                new_fail[key] = code

    # 充足数の減少
    count_drops = {}
    for k, v in counts.items():
        pv = prev_counts.get(k)
        if pv is not None and v < pv:
            count_drops[k] = (pv, v)

    # 状態保存
    STATE.write_text(json.dumps({"failing": failing_out, "counts": counts, "last_run": NOW_S,
                                 "img_fail": len(img_fail), "url_fail": len(url_fail)}, ensure_ascii=False, indent=1))

    # 画像レビュー待ち滞留(snapshot+stateのみ・消化役/GAS/D1非依存)。2026-08の12日沈黙の再発防止。
    try:
        import image_stall_report as ISR
        stall = ISR.stall_summary()
        stall_block = ISR.format_report(stall)
        log(f"画像滞留: {stall['total_koma']}コマ/{stall['total_comp']}社 alert={stall['alert']} "
            f"consumer_stale={stall['consumer_stale_days']}日")
    except Exception as e:
        stall, stall_block = {"alert": False}, ""
        log(f"画像滞留チェック失敗(非致命): {e}")

    # 異常判定 + 通知
    anomaly = bool(new_fail) or bool(count_drops) or bool(stall.get("alert"))
    lines = [f"🩺 トーキャリ コンテンツ健全性 {NOW_S}"]
    if stall_block and stall.get("alert"):
        lines.append(stall_block)
    if count_drops:
        lines.append("― 充足数の減少 ―")
        for k, (pv, v) in count_drops.items():
            lines.append(f"・{k}: {pv} → {v} (▼{pv - v})")
    if new_fail:
        # 種別ごとに件数 + いつから(最古since=今回なので NOW)
        by_kind = {}
        for key, code in new_fail.items():
            kind = "画像" if key.startswith("img::") else key.split("::")[1] if key.startswith("url::") else "その他"
            by_kind.setdefault(kind, []).append(key)
        lines.append("― 新規404/壊れ ―")
        for kind, keys in sorted(by_kind.items(), key=lambda x: -len(x[1])):
            lines.append(f"・{kind}: {len(keys)}件 (発生 {NOW_S}〜)")
        # 代表例を数件
        ex = list(new_fail.keys())[:5]
        for e in ex:
            lines.append("   例: " + e.replace("url::", "").replace("img::", "img ")[:80])
    if not anomaly:
        lines.append(f"✅ 異常なし(画像{len(imgs)}枚・URL{len(comps)*5}件・充足{counts})")

    text = "\n".join(lines)
    log("判定: " + ("⚠異常あり" if anomaly else "異常なし") +
        f" (新規失敗{len(new_fail)} / 充足減{len(count_drops)} / first_run={first_run})")

    sent = None
    if anomaly or args.force_notify:
        sent = notify_oscar(text)
        log(f"通知送信: {'成功(sent=true)' if sent else '未達(sent=false/skip)'}")
    else:
        log("異常なし → 通知しない(設計どおり)")

    log(f"=== 完了 anomaly={anomaly} notified={sent} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
