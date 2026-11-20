#!/usr/bin/env python3
"""check_d1_writers — company_panels(台本/画像)を書く経路が許可リスト以外に無いかを検査する(⑤-④・毎晩)。

台本の列は scenario_writer.apply(ファイル先行→lint→関所)だけが書く。直接 UPDATE する経路が増えると
D1 が台本ファイルより新しくなり、生成SQLで巻き戻す事故(2026-11 216社ズレ)が再発するため。

許可:
  - scenario_writer.py              … 台本列の唯一の書き込み口
  - scenario_to_panels.py           … 新規社の INSERT と関所の列 UPDATE(生成SQL)
  - IMAGE_ONLY の各ファイル          … image_url だけを SET する UPDATE に限る(台本ファイルに無い列)
それ以外の .py/.sh/.js/.ts で company_panels への UPDATE/INSERT/REPLACE/DELETE を見つけたら FAIL(exit 1)。
api/*.sql(手動 migration)は履歴として残すもので、実行経路ではないため対象外(運用で関所経由に限る)。
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PIPE = Path.home() / "oscar-ai" / "tokyari-pipeline"
ROOTS = [REPO / "tools", REPO / "api" / "src", REPO / "functions", PIPE / "scripts"]
WRITER_OK = {"scenario_writer.py", "scenario_to_panels.py", "check_d1_writers.py"}
IMAGE_ONLY = {"image_crop_fix.py", "inpaint_apply.py", "fix_and_deploy.py", "phase_c_image_fix.py", "expand_short_refs.py"}
SKIP_PARTS = {"node_modules", ".backups", "archive", "__pycache__"}
PAT = re.compile(r"(UPDATE\s+company_panels\s+SET\s+(?P<cols>.{0,400}?)\s+WHERE|"
                 r"INSERT(?:\s+OR\s+\w+)?\s+INTO\s+company_panels|REPLACE\s+INTO\s+company_panels|"
                 r"DELETE\s+FROM\s+company_panels)", re.I | re.S)
COL = re.compile(r"(\w+)\s*=")


def scan():
    bad, seen = [], 0
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix not in (".py", ".sh", ".js", ".ts", ".mjs") or SKIP_PARTS & set(p.parts):
                continue
            if p.name in WRITER_OK:
                continue
            seen += 1
            text = p.read_text(encoding="utf-8", errors="replace")
            for m in PAT.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                if "d1-writers: allow(" in text.splitlines()[line - 1]:   # 理由必須の明示許可
                    continue
                cols = m.group("cols")
                if cols is not None and p.name in IMAGE_ONLY:
                    names = {c.lower() for c in COL.findall(cols)}
                    if names and names <= {"image_url"}:
                        continue
                bad.append(f"{p}:{line}: {m.group(0)[:90]!r}")
    if seen == 0:
        raise SystemExit("走査対象 0 ファイル(空=失敗): ROOTS を確認")
    return bad, seen


def main():
    bad, seen = scan()
    print(f"[check_d1_writers] 走査 {seen} ファイル / 許可外の company_panels 書込 {len(bad)} 件")
    for b in bad:
        print("  FAIL", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
