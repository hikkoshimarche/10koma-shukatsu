#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_orphan_delete.py — 孤児3件削除の破壊的適用(Go受領後・wave完了後に手動実行)。

手順3-6: canary before(wave後の最終D1から) → migration適用(remote) → canary after →
         検証(孤児3=404 / 正3=200新v4 / 再ポイントbookmark 2件=正slugで200) → 結果。
STOP: canary不一致 or 正3社404 → 即停止 + backupからrevertガイド表示(自動revertはしない=人間確認)。
git push は本スクリプト外(wave後に別途)。
"""
import json
import subprocess
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_autoloop as A  # noqa: E402 (env)
import deploy_salary as D     # noqa: E402

ORPH = ["mitsubishi_corp", "toyota_motor", "ana"]
CANON = {"mitsubishi_corp": "mitsubishi-corp", "toyota_motor": "toyota-motor", "ana": "ana-hd"}
REPOINT_BOOKMARK = ["mitsubishi-corp", "toyota-motor"]  # 実際に再ポイントされる2件

MIG = sys.argv[1] if len(sys.argv) > 1 else None
BK = sys.argv[2] if len(sys.argv) > 2 else None


def api_status(slug):
    try:
        r = requests.get(f"{D.API_BASE}/api/companies/{slug}", timeout=30)
        if r.status_code != 200:
            return r.status_code, None, 0
        j = r.json()
        p = j.get("panels", [])
        d1 = p[0]["dialogue"] if p else ""
        is_v4 = d1.startswith("[")
        return 200, is_v4, len(p)
    except Exception as ex:
        return f"ERR:{ex}", None, 0


def main():
    if not MIG or not Path(MIG).exists():
        print(f"❌ migration不在: {MIG}"); return 1
    print(f"=== 孤児3件削除 適用 mig={MIG} ===")
    print(f"  backup={BK}")

    # [3-pre] canary before (孤児3件を除外した全社=wave後の最終状態が基準)
    print("\n[before] canary snapshot (孤児3件以外の全社)")
    cb = D.canary_snapshot(set(ORPH))
    print(f"  対象外 {len(cb)}社を監視 (wave完了後の最終D1基準)")

    # [3] migration適用
    print("\n[apply] migration実行(remote)")
    proc = D.wrangler(["--file", MIG], timeout=120)
    if proc.returncode != 0:
        print(f"  ❌ 適用失敗: {proc.stderr[:300]}"); return 2
    print("  ✅ 適用完了")

    # [4] canary after
    print("\n[after] canary diff")
    ca = D.canary_snapshot(set(ORPH))
    drift = D.canary_diff(cb, ca)
    if drift:
        print(f"  🛑 STOP: 対象外が変化 {drift} → backup({BK})からrevert要")
        return 3
    print(f"  ✅ 対象外 {len(ca)}社 全hash不変")

    # [5] 検証: 孤児3=404 / 正3=200新v4
    print("\n[verify] 孤児3=404 / 正3=200新v4")
    bad = []
    for o in ORPH:
        st, _, _ = api_status(o)
        ok = st == 404
        print(f"  孤児 {o:18} http={st} {'✅404' if ok else '❌期待404'}")
        if not ok:
            bad.append(("orphan_not_404", o, st))
    for o, c in CANON.items():
        st, v4, n = api_status(c)
        ok = st == 200 and v4 and n == 10
        print(f"  正   {c:18} http={st} v4={v4} panels={n} {'✅' if ok else '❌'}")
        if not ok:
            bad.append(("canonical_bad", c, st))

    # [5b] 再ポイントbookmark: 正slugで200(=保存リストが生きている)
    print("\n[verify] 再ポイントbookmark 2件が正slugで200")
    for c in REPOINT_BOOKMARK:
        st, v4, n = api_status(c)
        ok = st == 200 and n == 10
        print(f"  bookmark→ {c:18} http={st} panels={n} {'✅生存' if ok else '❌'}")
        if not ok:
            bad.append(("bookmark_dead", c, st))
    # bookmarksが正しく移動したかD1直接確認
    rows = D.d1_query("SELECT company_id, COUNT(*) n FROM bookmarks WHERE company_id IN "
                      "('mitsubishi_corp','toyota_motor','ana','mitsubishi-corp','toyota-motor','ana-hd') "
                      "GROUP BY company_id")
    bm = {r["company_id"]: r["n"] for r in rows}
    orphan_left = sum(bm.get(o, 0) for o in ORPH)
    print(f"  bookmarks D1: 孤児残={orphan_left} 正側={ {k:v for k,v in bm.items() if k not in ORPH} }")
    if orphan_left > 0:
        bad.append(("bookmark_orphan_remains", str(bm), 0))

    if bad:
        print(f"\n🛑 STOP: 検証NG {bad} → backup({BK})からrevert検討")
        return 4
    print("\n✅ 全検証パス。孤児3件削除完了・bookmark再ポイント生存・canary不変。")
    print("   次: git add/commit/push origin main (wave後・手動)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
