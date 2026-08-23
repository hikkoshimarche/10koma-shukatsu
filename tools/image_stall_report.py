#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_stall_report.py — 画像レビュー待ちキューの滞留を『消化役の稼働に依存せず』日次可視化する。

背景(2026-08 障害): 画像FBキュー505コマが12日間、誰にも気づかれず滞留した。真因は二重の見えなさ:
  (1) 消化役 phase_c_auto.run_batch が deploy_fb 経由で毎時LIVE起動していたが、launchd環境の
      CLOUDFLARE_API_TOKEN 不備で D1 query が毎回 400 で落ち、try/except に握り潰されていた
      (=state.day が凍結・1件も消化されない)。
  (2) 件数がスプシに出るのは消化役が setimgstall/setpartial を呼んだ時だけ → 消化役が死ぬと件数も消える。
この二重依存を断つため、本モジュールは **snapshot と state を読むだけ**で滞留と消化役の健全性を判定する
(GAS/D1/消化役に一切依存しない)。日次で content_health_daily に載り、異常時のみ人に通知される。

出力する3指標:
  ・待ち件数 / 社数          … .image_pending_snapshot.json の count 合計
  ・最古の滞留日数            … since の最小(最も古い)からの経過日数
  ・消化役の鮮度(stale日数)  … .image_fix_state.json の day から今日までの日数。
                              pending>0 かつ stale>=STALE_ALERT_DAYS で「消化役が止まっている」= 赤信号。
型別内訳は best-effort(_pending_classification.json のキャッシュがあれば付す。無くても核指標は出る)。
"""
from __future__ import annotations
import json
from datetime import datetime, date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "tools" / ".image_pending_snapshot.json"
STATE = REPO / "tools" / ".image_fix_state.json"
CLASSIFY_CACHE = REPO / "tools" / "_pending_classification.json"

STALE_ALERT_DAYS = 2      # 消化役の state.day がこの日数以上古く、かつ pending>0 なら赤信号
OLD_ALERT_DAYS = 3        # 最古の滞留がこの日数以上なら赤信号(setpartialのbumpに影響されない停滞検知)


def _days_since(ts: str, today: date | None = None) -> int | None:
    """ISO文字列/日付から今日までの経過日数。パース不能は None。"""
    if not ts:
        return None
    today = today or datetime.now().date()
    s = str(ts).strip().replace("Z", "")
    for parse in (lambda x: datetime.fromisoformat(x).date(),
                  lambda x: datetime.strptime(x[:10], "%Y-%m-%d").date()):
        try:
            return (today - parse(s)).days
        except Exception:
            continue
    return None


def stall_summary(today: date | None = None) -> dict:
    """snapshot+state のみから滞留サマリを返す。消化役/GAS/D1 に依存しない。"""
    today = today or datetime.now().date()
    snap = {}
    if SNAPSHOT.exists():
        try:
            snap = json.load(open(SNAPSHOT, encoding="utf-8"))
        except Exception:
            snap = {}
    total_koma = sum(int(v.get("count", 0)) for v in snap.values())
    total_comp = sum(1 for v in snap.values() if int(v.get("count", 0)) > 0)
    # 最古の滞留日数
    ages = [d for d in (_days_since(v.get("since", ""), today) for v in snap.values()
                        if int(v.get("count", 0)) > 0) if d is not None]
    oldest_days = max(ages) if ages else None

    # 消化役の鮮度: state.day から今日までの日数
    st = {}
    if STATE.exists():
        try:
            st = json.load(open(STATE, encoding="utf-8"))
        except Exception:
            st = {}
    consumer_day = st.get("day")
    consumer_stale = _days_since(consumer_day, today)
    consumer_paused = bool(st.get("paused"))

    # 型別内訳(best-effort・キャッシュがあれば)
    types = None
    if CLASSIFY_CACHE.exists():
        try:
            c = json.load(open(CLASSIFY_CACHE, encoding="utf-8"))
            types = {"safe": c.get("safe"), "fragile": c.get("fragile"),
                     "unknown": c.get("unknown"), "as_of": c.get("as_of")}
        except Exception:
            types = None

    # 赤信号判定: 待ちがあり、かつ(消化役が止まっている OR 最古滞留が閾値超 OR 消化役pause中)
    consumer_dead = (total_koma > 0 and consumer_stale is not None
                     and consumer_stale >= STALE_ALERT_DAYS)
    old_backlog = (oldest_days is not None and oldest_days >= OLD_ALERT_DAYS and total_koma > 0)
    alert = bool(consumer_dead or old_backlog or (consumer_paused and total_koma > 0))

    return {
        "total_koma": total_koma, "total_comp": total_comp, "oldest_days": oldest_days,
        "consumer_day": consumer_day, "consumer_stale_days": consumer_stale,
        "consumer_paused": consumer_paused, "consumer_dead": consumer_dead,
        "old_backlog": old_backlog, "alert": alert, "types": types,
    }


def format_report(s: dict) -> str:
    """人が読む1ブロック。content_health の通知にそのまま連結できる短さ。"""
    head = "🖼️ 画像レビュー待ち滞留"
    if s["total_koma"] == 0:
        return f"{head}: 0件 ✅"
    L = [f"{head}: {s['total_koma']}コマ / {s['total_comp']}社",
         f"・最古の滞留: {s['oldest_days']}日" + ("　⚠️" if s["old_backlog"] else "")]
    if s["types"] and s["types"].get("safe") is not None:
        t = s["types"]
        L.append(f"・型別: 安全{t['safe']} / 崩れやすい{t['fragile']} / 要調査{t['unknown']}"
                 + (f" (as_of {t['as_of']})" if t.get("as_of") else ""))
    cs = s["consumer_stale_days"]
    if s["consumer_dead"]:
        L.append(f"🔴 消化役が {cs}日 停止中(state.day={s['consumer_day']})"
                 "＝自動消化されていません。D1認証(CLOUDFLARE_API_TOKEN)を要確認。")
    elif s["consumer_paused"]:
        L.append("🔴 消化役 paused=True(上限/QA連続失敗で自動停止)。要確認。")
    else:
        L.append(f"消化役 稼働: state.day={s['consumer_day']}(stale {cs}日)")
    return "\n".join(L)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="JSONで出力")
    args = ap.parse_args()
    s = stall_summary()
    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
    else:
        print(format_report(s))
        print(f"\n[alert={s['alert']}]  (alert=True の日は content_health 経由でオスカーに日次通知)")
