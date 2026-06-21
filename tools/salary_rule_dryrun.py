#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""salary_rule_dryrun.py — 年収共通ルールを全商社にdry-run適用(本番非反映)。

共通修正案ハンドラの年収版。各商社の年収コマを、有報(単体)平均年収＋出典で構造的に語る形へ
修正する提案を作り、提案反映後lintまで見せる。岩谷は据置/構造化を確認(盛らない)。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L  # noqa: E402

TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
TOKYARI_SLUG = {"itochu": "itochu-shoji"}
SHOSHA = ["mitsubishi-corp", "itochu", "sumitomo-corp", "marubeni", "kanematsu",
          "shinkokusyoji", "iwatani", "sojitz", "toyota-tsusho"]  # 三井(mitsui-bussan)除外

SALARY_RULE = (
    "【年収の共通ルール(原則C)】\n"
    "1. 年収は『額』でなく『構造・背景』で語ることを最優先する。\n"
    "2. 金額を出す場合のみ、有価証券報告書(単体)の平均年収を、出典を明示して使う。"
    "有報(単体)が無ければ四季報をフォールバック。どちらも無ければ金額は出さず構造のみで語る。\n"
    "3. 他社比較で『低い/高い』と見える生数字(例: ○○の数十分の1、○倍 等)は避ける。\n"
    "4. 正しく低い年収を盛って高く見せない(捏造禁止)。低さは事業構造・専業性などの背景で意味づける。\n"
    "5. 既に上記を満たすなら『変更なし(反映済)』。"
)


def factsheet_salary(slug: str) -> str:
    tslug = TOKYARI_SLUG.get(slug, slug)
    fp = TOKYARI / "output" / tslug / "factsheet.md"
    if not fp.exists():
        return "(factsheet無し)"
    lines = []
    for ln in fp.read_text(encoding="utf-8").splitlines():
        if "平均年収" in ln or ("年収" in ln and "万円" in ln):
            lines.append(ln.strip())
    return " / ".join(lines[:3]) or "(年収記載なし)"


def find_salary_koma(slug: str):
    p = L.parse_migration_sql(slug)
    for r in p["panels"]:
        sj = r.get("script_json") or ""
        if "年収" in sj or "万円" in sj:
            return r["panel_num"]
    return None


def main():
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8") + "\n\n" + SALARY_RULE
    print("=== 年収共通ルール dry-run (全商社・三井除外・本番非反映) ===\n")
    for slug in SHOSHA:
        koma = find_salary_koma(slug)
        sal = factsheet_salary(slug)
        print(f"\n#### {slug}  (年収コマ=koma{koma})")
        print(f"  有報/factsheet年収: {sal}")
        if not koma:
            print("  年収コマ検出できず → スキップ")
            continue
        instr = (f"{SALARY_RULE}\n\n【この社の有報/factsheet年収(出典付与の根拠)】{sal}\n"
                 "上記ルールに沿って年収コマを修正。金額を出すなら有報(単体)平均年収＋出典。"
                 "他社比較の生数字は避ける。正しく低いだけなら盛らず構造で意味づけ、変更不要なら『変更なし』。")
        res = L.fix_script_koma(slug, koma, instr, rules, dry=True)
        if not res.get("changed"):
            print(f"  → 変更なし(反映済): {res.get('note')}")
            continue
        print(f"  現行: {res['before']['script']}")
        print(f"  新案: {res['after']['script']}")
        print(f"  main_copy: {res['before'].get('main_copy')} → {res['after'].get('main_copy')}")
        print(f"  理由: {res.get('note')}")
        e, w, _ = L.lint_with_overrides(slug, {koma: res["after"]})
        print(f"  lint(提案反映後): errors={e} warnings={w} {'✅' if e==0 else '❌'}")


if __name__ == "__main__":
    main()
