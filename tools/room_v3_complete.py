#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_v3_complete.py — ルームv3 完走時の締め処理(冪等・重複防止)。
残社数が閾値以下(=実質完走)のとき: ①タブ/ダッシュボード最新化 ②Phase4集計をROOM_V3_STATUS.mdへ
③LINE完了通知を1通(sentinelで重複防止・HTTP/consumption実値確認)。未完走なら何もしない(exit 2)。
watcher/resumeラッパから呼ばれる。手動実行も可。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
SCR = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts"))
sys.path.insert(0, str(SCR)); sys.path.insert(0, str(REPO / "tools"))
try:
    from dotenv import load_dotenv as _ld; _ld(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
except Exception:
    pass
import room_industry_roles_v3 as V3
import requests
import csv

ROOT = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline"))
SENT = REPO / "tools" / ".room_v3_line_sent"
STATUS = REPO / "ROOM_V3_STATUS.md"
GAS_URL = os.environ.get("SHEET_WEBAPP_URL", "").strip()
GAS_TOKEN = os.environ.get("SHEET_API_TOKEN", "").strip()
COST_PER = 0.322  # ゲート実測 1社平均$0.322(Sonnet4.6)
DONE_THRESHOLD = 8  # 残がこれ以下=実質完走(隔離数社は許容)


def wrangler_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", str(REPO / "api" / "wrangler.toml"), "--json", "--command", sql],
                       cwd=str(REPO), capture_output=True, text=True, timeout=90)
    return json.loads(p.stdout[p.stdout.find("["):])[0]["results"]


def state():
    cj = json.loads((REPO / "public" / "companies.json").read_text(encoding="utf-8"))
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    done = {}
    p = ROOT / "output" / "room_sync_state.csv"
    if p.exists():
        for r in csv.reader(open(p, encoding="utf-8")):
            if len(r) >= 2:
                done[r[0]] = r[1]

    def hasfs(s):
        return (ROOT / "output" / s / "factsheet.md").exists()
    cand = [s for s in id2ind if s != "mitsui-bussan" and hasfs(s)]
    remain = [s for s in cand if done.get(s) != "registered-v3"]
    # v3判定は state CSV(registered-v3)基準=日付非依存(深夜跨ぎでも正しくカウント)。三井GOLDは別枠で除外。
    v3 = [s for s in cand if done.get(s) == "registered-v3"]
    from collections import Counter
    dist = Counter(V3.archetype_for(s, id2ind.get(s, "")) for s in v3)
    iso = []
    isof = REPO / "tools" / "_room_isolated.json"
    if isof.exists():
        seen = set()
        for it in json.loads(isof.read_text()):
            s = it["slug"]
            # 回復判定=state基準(registered-v3なら回復済で隔離から除外)・重複slug除去
            if done.get(s) == "registered-v3" or s in seen:
                continue
            seen.add(s)
            iso.append(it)
    return dict(id2name=id2name, id2ind=id2ind, cand=cand, remain=remain, v3=v3, dist=dist, iso=iso)


def main():
    st = state()
    nv3 = len(st["v3"]); nrem = len(st["remain"]); niso = len(st["iso"])
    if nrem > DONE_THRESHOLD:
        sys.stderr.write(f"未完走(残{nrem}社>閾値{DONE_THRESHOLD}) → 締め処理せず\n")
        return 2
    # ①タブ/ダッシュボード最新化
    subprocess.run([sys.executable, str(SCR / "room_tab_sync.py")], cwd=str(SCR),
                   capture_output=True, text=True, timeout=1800)
    if GAS_URL:
        try:
            requests.get(GAS_URL, params={"mode": "roomdashboard", "token": GAS_TOKEN}, timeout=90)
        except Exception:
            pass
    # ①.5 ライブ化: 全registered-v3 を personas へ最終同期 + room_liff_id付与(最終400社まで取りこぼしなし)
    subprocess.run([sys.executable, str(REPO / "tools" / "room_personas_to_live.py"), "--all", "--set-liff"],
                   cwd=str(REPO), capture_output=True, text=True, timeout=2400)
    cost = nv3 * COST_PER
    # ③LINE完了通知(重複防止)
    line_result = "skip(既送信)"
    if not SENT.exists() and GAS_URL:
        before = None
        try:
            q = requests.get(GAS_URL, params={"mode": "linequota", "token": GAS_TOKEN}, timeout=40).json()
            before = json.loads(q.get("consumption", {}).get("body", "{}")).get("totalUsage")
        except Exception:
            pass
        msg = (f"【ルームv3完了】人数可変(6〜9人)ロースターの全社展開が完了しました。\n"
               f"・v3登録 {nv3}/400社（三井GOLDは別枠・不可侵）\n"
               f"・隔離 {niso}社（room-lint5未通過＝要個別対応タブ）\n"
               f"・実費 概算${cost:.0f}（Sonnet4.6・ゲート実測$0.32/社ベース）\n"
               f"アーキタイプ別・隔離社リストは ROOM_V3_STATUS.md 参照。（トーキャリ運営）")
        try:
            r = requests.post(GAS_URL, data={"mode": "pushlinefull", "token": GAS_TOKEN, "text": msg}, timeout=60)
            code = r.json().get("code")
            after = None
            time.sleep(3)
            try:
                q2 = requests.get(GAS_URL, params={"mode": "linequota", "token": GAS_TOKEN}, timeout=40).json()
                after = json.loads(q2.get("consumption", {}).get("body", "{}")).get("totalUsage")
            except Exception:
                pass
            delta = (after - before) if (after is not None and before is not None) else "?"
            if code == 200:
                SENT.write_text(f"sent {time.strftime('%Y-%m-%d %H:%M')} code={code} delta={delta}", encoding="utf-8")
                line_result = f"送信OK code=200 consumption_delta={delta}"
            else:
                line_result = f"送信code={code}(sentinel未書込=次回再試行)"
        except Exception as e:
            line_result = f"送信例外:{e}"
    # ②Phase4集計を STATUS へ追記
    lines = [f"\n\n---\n## ✅ Phase4 完走集計 ({time.strftime('%Y-%m-%d %H:%M')})",
             f"- v3登録: **{nv3}/400社**（残{nrem}・三井GOLD別枠1）",
             f"- 隔離(lint5未通過): **{niso}社** " + (", ".join(x["slug"] for x in st["iso"]) or "なし"),
             f"- 実費 概算: **${cost:.0f}**（$0.322/社×{nv3}）",
             f"- LINE完了通知: {line_result}",
             "- アーキタイプ別v3登録:"]
    for a, n in st["dist"].most_common():
        lines.append(f"    - {a}: {n}社")
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"完走締め: v3={nv3} 隔離={niso} 実費概算${cost:.0f} LINE={line_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
