"""watch_content_health.py — 検知役の検知役(F・2026-11-18)。毎晩 healthcheck(run_nightly.sh, 3:00)から呼ぶ。

背景: content_health_daily は 2026-08-05 から毎朝「開始」だけ書いて wrangler 認証エラーで落ち続け、
  3ヶ月半誰も気づかなかった(検知役が死ぬと、検知役が出すはずの警告も全部消える)。
  phasec 消化役も『毎時正常起動・反映0』を311回続けた。
→ 別ジョブから「最終完了時刻」と「進捗」を見て、異常なら緊急アラート(LINE pushoscar・緊急のみ可)。

検査:
  1. content_health の heartbeat.last_complete が 2日超 / 無い → 🔴緊急
     (last_start が新しいのに last_complete が古い = 起動はするが完走しない、を区別して表示)
  2. 画像消化役 health: status in (no_progress, crashed) が 3回以上連続 → 🔴緊急
     (phasec を意図的に止めている間は last_attempt が古くなるだけ=ここでは鳴らさない。停止の可視化は stall_report)
  3. check_wrangler_auth.py が FAIL → 🔴緊急(launchd で認証の無い wrangler 経路が再発)
終了コード: 異常あり=1(launchd err/レポートに残す)、なし=0。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
HB = TOOLS / "content_health" / "heartbeat.json"
IMG_HEALTH = TOOLS / ".image_consumer_health.json"
ENV = TOOLS / ".env.phase_c"
JST = timezone(timedelta(hours=9))
MAX_AGE = timedelta(days=2)
NO_PROGRESS_RUNS = 3


def _parse(ts):
    if not ts:
        return None
    try:
        d = datetime.fromisoformat(ts)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=JST)


def check(now=None):
    now = now or datetime.now(JST)
    issues = []
    # 1. content_health 完了鮮度
    if not HB.exists():
        issues.append("content_health heartbeat 無し(一度も完走記録なし)")
    else:
        try:
            hb = json.loads(HB.read_text())
        except Exception as e:
            hb = None
            issues.append(f"content_health heartbeat 読込失敗: {type(e).__name__}")
        if hb is not None:
            lc, ls = _parse(hb.get("last_complete")), _parse(hb.get("last_start"))
            if lc is None or now - lc > MAX_AGE:
                age = "不明" if lc is None else f"{(now - lc).days}日"
                started = ls and (lc is None or ls > lc)
                issues.append(f"content_health 最終完了から{age}(last_complete={hb.get('last_complete')})"
                              + ("・起動はしているが完走していない" if started else "・起動自体していない可能性"))
    # 2. 画像消化役の進捗ゼロ連続
    if IMG_HEALTH.exists():
        try:
            h = json.loads(IMG_HEALTH.read_text())
            if h.get("status") in ("no_progress", "crashed") and int(h.get("bad_streak") or 0) >= NO_PROGRESS_RUNS:
                issues.append(f"画像消化役 進捗ゼロ{h.get('bad_streak')}回連続(status={h.get('status')}・"
                              f"since {h.get('bad_since')}・err={str(h.get('error') or h.get('item_error_samples'))[:120]})")
        except Exception as e:
            issues.append(f"画像消化役 health 読込失敗: {type(e).__name__}")
    # 3. wrangler 認証ガード
    r = subprocess.run([sys.executable, str(TOOLS / "check_wrangler_auth.py")], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        fails = [l.strip() for l in r.stdout.splitlines() if "❌" in l][:5]
        issues.append("check_wrangler_auth FAIL: " + (" / ".join(fails) or r.stderr[-200:]))
    return issues


def _notify(text):
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    url = os.environ.get("SHEET_WEBAPP_URL", "").strip()
    if not url:
        print("⚠ SHEET_WEBAPP_URL 無し → 通知不可(このログが唯一の記録)", file=sys.stderr)
        return False
    import requests
    try:
        j = requests.get(url, params={"mode": "pushoscar", "token": os.environ.get("SHEET_API_TOKEN", ""),
                                      "text": text[:4900]}, timeout=40).json()
        print(f"pushoscar sent={j.get('sent')} reason={j.get('reason', '')}")
        return bool(j.get("sent"))
    except Exception as e:   # 404 でも送信済の場合あり(memory gas-pushline-404-is-success)。再送しない。
        print(f"pushoscar 例外: {type(e).__name__}: {e}", file=sys.stderr)
        return False


def main():
    issues = check()
    now_s = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    if not issues:
        print(f"[watch_content_health {now_s}] OK: 検知役/消化役/wrangler認証 異常なし")
        return 0
    text = f"🚨【緊急】トーキャリ 監視系の異常 {now_s}\n・" + "\n・".join(issues)
    print(text)
    if "--no-notify" not in sys.argv:
        _notify(text)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
