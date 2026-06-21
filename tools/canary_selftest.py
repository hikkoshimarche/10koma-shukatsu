#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""canary_selftest.py — 一般化canaryの検出能力を確認(read-only)。

『今サイクル対象社"以外"が1社でも変化したら検出(→ループは停止)』を実D1スナップショットで検証。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase_c_autoloop as A  # noqa: E402 (loads .env.phase_c)
import deploy_salary as D     # noqa: E402


def main():
    targets = {"sumitomo-corp"}  # 仮の今サイクル対象
    before = D.canary_snapshot(targets)
    assert before, "snapshotが空"
    assert "sumitomo-corp" not in before, "対象社がsnapshotに含まれている"
    print(f"監視対象(対象外) {len(before)}社 / 対象社={sorted(targets)} は除外 ✅")

    # 1) 同一 → 変化なし(安全)
    assert D.canary_diff(before, dict(before)) == [], "同一なのにdiff検出"
    print("① 同一スナップショット → diff空(安全) ✅")

    # 2) 非対象社が1社変化 → 検出
    victim = sorted(s for s in before if s != "sumitomo-corp")[0]
    after = dict(before); after[victim] = "0000DEADBEEF0000"
    diff = D.canary_diff(before, after)
    assert diff == [victim], f"検出失敗 {diff}"
    print(f"② 非対象社 '{victim}' のhash変化 → diff={diff} 検出 ✅ (ループはreturn 2で停止)")

    # 3) 非対象社が消失 → 検出
    after2 = dict(before); after2.pop(victim)
    assert victim in D.canary_diff(before, after2), "消失を検出できない"
    print(f"③ 非対象社 '{victim}' の消失 → 検出 ✅")

    # 4) 三井固有参照が撤去されているか(コード上)
    src = (Path(__file__).resolve().parent / "deploy_fb.py").read_text(encoding="utf-8")
    assert "canary_snapshot" in src and "canary_hash()" not in src, "deploy_fbがまだ三井固有canary"
    print("④ deploy_fbの三井固有canary参照 撤去済 ✅")

    print("\nSELFTEST PASS: 対象外が1社でも変化→検出→停止 を確認")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
