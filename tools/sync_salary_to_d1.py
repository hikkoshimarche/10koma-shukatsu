#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_salary_to_d1.py — 修正済み台本SQL(年収コマ+toyota koma10)を本番D1へ冪等同期。

Claudeは呼ばない。SQLが正。各商社の年収コマ(+toyota koma10)について、
D1の現値とSQLの値が異なる場合のみ台本列(dialogue/script_json/main_copy/sub_copy)をUPDATE。
image_urlは触らない。backup+canary付き。三井除外。
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import salary_rule_dryrun as S   # noqa: E402
import deploy_salary as D        # noqa: E402


def main():
    """台本ファイル(scenario_v4.json)が先行している年収コマを D1 へ出す(冪等)。
    2026-11-19 ⑤: 旧版は api/migration_v4_<slug>.sql を正として D1 を直接 UPDATE していた(巻き戻し経路)。
    今は scenario_writer.sync_from_file(関所: D1 が履歴に無い新しい値なら拒否・旧値一致 UPDATE)。"""
    import scenario_writer as SW
    print("=== 台本ファイル→D1 冪等同期 (年収コマ+toyota koma10・三井除外・関所経由) ===")
    targets = {}
    for slug in S.SHOSHA:
        k = S.find_salary_koma(slug)
        if k:
            targets.setdefault(slug, set()).add(k)
        if slug == "toyota-tsusho":
            targets.setdefault(slug, set()).add(10)
    if not targets:
        raise SystemExit("対象0社(空=失敗: S.SHOSHA/find_salary_koma を確認)")
    rc = 0
    for slug, komas in targets.items():
        try:
            r = SW.sync_from_file(slug, komas, reason="年収コマ同期", dry="--dry" in sys.argv)
            print(f"  {slug:16} koma{sorted(komas)}: {r.get('note') or ('UPDATE ' + str(sorted(r['updates'])))}")
        except SW.WriterError as ex:
            rc = 1
            print(f"  {slug:16} ❌ 中止: {str(ex)[:160]}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
