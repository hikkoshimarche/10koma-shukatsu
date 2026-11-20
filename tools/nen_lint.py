#!/usr/bin/env python3
"""nen_lint — 会社年齢「◯年」型の陳腐化 lint(2026-11-20)。

年数lint(scenario_lints)は「N年前」しか見ないため、「創業N年」「N年続く」「N年間」「N年の歴史」は
毎年1つずつ古くなるのに拾えなかった(kawasaki/森永/honda/IBM の4件目で作成)。

創業年マスタ tools/founding_year_master.csv(slug×起点年・公式出典)と、台本の表示欄
(script / main_copy / sub_copy。meta は対象外)の年数を照合する:
  期待値 E = 今年 − 起点年。台本の数値 N が E と違い、かつ |N−E| ≤ WINDOW のとき検出
  (WINDOW 外の数字は会社年齢ではない別の期間とみなす)。
  - 「N年目」は E+1 と比較。「N年前」は E と比較(起点年からの年前表現に限る)。
  - 「約N年」は±5年か10年単位の切り下げなら通す。「N年以上」「N年超」は下限として正しければ通す(N ≤ E)。
  「100年」「150年」等50の倍数の節目表現は丸めとみなし機械判定しない。別起点の表現は nen_lint_allow.json(理由必須)。
  status=official の社 → error / secondary・needs_judgment の社 → warning(公式未確認のため)。
使い方:
  python3 tools/nen_lint.py              # 全マスタ社を検査(error があれば exit 1)
  python3 tools/nen_lint.py --slug ihi    # 1社
  python3 tools/nen_lint.py --selftest
"""
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
MASTER = TOOLS / "founding_year_master.csv"
ALLOW = TOOLS / "nen_lint_allow.json"
PIPE = Path.home() / "oscar-ai" / "tokyari-pipeline"
WINDOW = 10
PAT = re.compile(r"(?P<pre>約)?(?<!\d)(?P<n>\d{1,3})年(?P<post>目|前|以上|超|間)?")


def load_master():
    rows = list(csv.DictReader(open(MASTER, encoding="utf-8")))
    if not rows:
        raise SystemExit("founding_year_master.csv が空(空=失敗)")
    return {r["slug"]: r for r in rows}


def load_allow():
    items = json.loads(ALLOW.read_text(encoding="utf-8"))["items"] if ALLOW.exists() else []
    for x in items:
        if not (x.get("slug") and x.get("context") and x.get("reason")):
            raise SystemExit(f"nen_lint_allow.json: slug/context/reason 必須 {x}")
    return items


def check_text(text, origin, year):
    """text 中の会社年齢表現のうち、期待値と食い違うものを返す [(found, expected)]。"""
    e = year - origin
    out = []
    for m in PAT.finditer(text or ""):
        n = int(m.group("n"))
        post = m.group("post") or ""
        # 西暦の一部(例 "1878年")は (?<!\d) で除外済み・4桁は \d{1,3} に掛からない
        exp = e + 1 if post == "目" else e
        if abs(n - exp) > WINDOW:
            continue
        if m.group("pre"):
            if abs(n - exp) <= 5 or (n <= exp and n % 10 == 0 and exp - n < 10):
                continue            # 「約N年」= 丸め(±5年、または10年単位への切り下げ)
        elif post in ("以上", "超"):
            if n <= exp:
                continue            # 下限として正しい
        elif n == exp:
            continue
        elif n % 50 == 0 and not post:
            continue                # 「100年」「150年」= 丸めの節目表現は機械判定しない
        out.append((m.group(0), f"{exp}年{post if post in ('目', '前', '間') else ''}"))
    return out


def scan_slug(slug, row, year):
    fp = PIPE / "output" / slug / "scenario_v4.json"
    if not fp.exists():
        return None
    scn = json.loads(fp.read_text(encoding="utf-8"))
    origin = int(row["origin_year"])
    allow = [x["context"] for x in load_allow() if x["slug"] == slug]
    hits = []
    for k in scn.get("koma", []):
        n = k.get("koma_number")
        ov = k.get("overlay_text") or {}
        fields = [("script", "\n".join(k.get("script") or []))] + \
                 [(f, ov.get(f)) for f in ("main_copy", "sub", "sub_copy") if ov.get(f)]
        for f, t in fields:
            for found, exp in check_text(t, origin, year):
                if any(c in t and found in c for c in allow):
                    continue
                hits.append(f"koma{n}.{f}: 「{found}」→ 期待 {exp}(起点{origin}{row['basis']})")
    return hits


def run_all(year=None):
    """全マスタ社を検査し {"error": [...], "warning": [...], "scanned": n} を返す(drift_monitor から呼ぶ)。"""
    year = year or dt.date.today().year
    master = load_master()
    res = {"error": [], "warning": [], "scanned": 0, "year": year}
    for slug, row in sorted(master.items()):
        hits = scan_slug(slug, row, year)
        if hits is None:
            continue
        res["scanned"] += 1
        res["error" if row["status"] == "official" else "warning"] += [f"{slug} {h}" for h in hits]
    if res["scanned"] == 0:
        raise SystemExit("検査対象 0 社(空=失敗)")
    return res


def main(argv):
    if "--selftest" in argv:
        return selftest()
    year = dt.date.today().year
    master = load_master()
    only = argv[argv.index("--slug") + 1] if "--slug" in argv else None
    n_err = n_warn = n_scanned = 0
    for slug, row in sorted(master.items()):
        if only and slug != only:
            continue
        hits = scan_slug(slug, row, year)
        if hits is None:
            print(f"  [skip] {slug}: scenario_v4.json なし")
            continue
        n_scanned += 1
        lvl = "ERROR" if row["status"] == "official" else "WARN"
        for h in hits:
            print(f"  {lvl} {slug} {h}")
        if lvl == "ERROR":
            n_err += len(hits)
        else:
            n_warn += len(hits)
    if n_scanned == 0:
        raise SystemExit("検査対象 0 社(空=失敗)")
    print(f"[nen_lint] {year}年基準 検査{n_scanned}社(マスタ{len(master)}社) error={n_err} warning={n_warn}")
    return 1 if n_err else 0


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("  ✅ " if cond else "  ❌ ") + name)
    chk("正しい年数は通す", check_text("1878年創業、148年続く", 1878, 2026) == [])
    chk("陳腐化を検出", check_text("146年続く企業", 1878, 2026) == [("146年", "148年")])
    chk("N年目は E+1", check_text("147年目を作る", 1878, 2026) == [("147年目", "149年目")])
    chk("N年前(正)", check_text("115年前の THINK", 1911, 2026) == [])
    chk("N年前(陳腐)", check_text("113年前!?", 1911, 2026) == [("113年前", "115年前")])
    chk("N年以上(下限として正)は通す", check_text("創業130年以上", 1888, 2026) == [])
    chk("約N年(丸め)は通す", check_text("約130年の歴史", 1890, 2026) == [])
    chk("窓外の期間は無視", check_text("10年後の自分", 1878, 2026) == [])
    chk("西暦は無視", check_text("1911年、THINK", 1911, 2026) == [])
    chk("約N年は±5で通す", check_text("約150年の歴史", 1878, 2026) == [])
    chk("節目の丸め(100年)は通す", check_text("100年の技術", 1916, 2026) == [])
    chk("節目でない陳腐化は検出", check_text("80年の施工史", 1944, 2026) == [("80年", "82年")])
    print("=== nen_lint selftest:", "ALL PASS ✅" if ok else "FAIL ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
