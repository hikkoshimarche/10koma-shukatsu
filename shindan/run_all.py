#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/run_all.py — 400社ローリング属性抽出。

・1社ハーネス(extract.extract_company)をローリング投入
・resumable: attributes/<id>.json が既存かつvalidならskip
・20社毎チェックポイント: git add/commit/push + カバレッジ記録
・LINE送信は一切しない(テキスト/ファイルのみ)
・カバレッジ実値を coverage_report.md に出力(属性×充足社数 + 判定不能社リスト)

使い方: python3 run_all.py [--limit N] [--no-git]
"""
import os, re, json, sys, subprocess, time, traceback
from pathlib import Path
import extract

ROOT = Path(__file__).resolve().parent
ATTR = ROOT / "attributes"
ATTR.mkdir(exist_ok=True)
PIPE = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline"))
REPO = ROOT.parent
CP_EVERY = 20
NO_GIT = "--no-git" in sys.argv
LIMIT = None
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])


def companies():
    comp = json.load(open(PIPE / "data" / "companies.json"))
    out = []
    for ind, lst in comp.items():
        for c in lst:
            out.append((c["id"], c["name"], ind))
    return out


def is_done(cid):
    p = ATTR / f"{cid}.json"
    if not p.exists():
        return False
    try:
        json.load(open(p)); return True
    except Exception:
        return False


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=120)
    except Exception as e:
        print("  git err:", e); return None


def checkpoint(done_count, total):
    write_coverage()
    if NO_GIT:
        print(f"  [CP] {done_count}/{total} (git skip)"); return
    git("add", "shindan/attributes", "shindan/coverage_report.md")
    r = git("commit", "-q", "-m", f"data(shindan): 属性抽出CP {done_count}/{total}社\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    push = git("push")
    if push and push.returncode != 0:
        git("pull", "--rebase"); push = git("push")
    ok = "ok" if (push and push.returncode == 0) else "push保留"
    print(f"  [CP] {done_count}/{total} commit+{ok}")


SOFT = extract.SOFT_KEYS + ["bunri", "job_tags"]


def write_coverage():
    rows = [json.load(open(ATTR / f)) for f in os.listdir(ATTR) if f.endswith(".json")]
    n = len(rows)
    if n == 0:
        return
    cov = {"avg_salary": 0, "starting_salary": 0, "trend_note": 0}
    for k in SOFT:
        cov[f"soft.{k}"] = 0
    by_ind = {}
    no_salary = []
    for d in rows:
        by_ind.setdefault(d["industry"], {"n": 0, "avg_salary": 0})
        by_ind[d["industry"]]["n"] += 1
        if d["facts"]["avg_salary"]:
            cov["avg_salary"] += 1; by_ind[d["industry"]]["avg_salary"] += 1
        else:
            no_salary.append(f"{d['name']}({d['industry']})")
        if d["facts"]["starting_salary"]:
            cov["starting_salary"] += 1
        if d.get("trend_note"):
            cov["trend_note"] += 1
        for k in SOFT:
            v = d["soft"].get(k, {}).get("value")
            if v not in (None, [], ""):
                cov[f"soft.{k}"] += 1
    lines = ["# shindan カバレッジレポート", "",
             f"生成時点: 抽出済 **{n}社** / 全400社", "",
             "## 表示ファクト②(出典必須・数字表示)", "",
             "| 属性 | 充足社数 | 充足率 |", "|---|---|---|"]
    for k in ["avg_salary", "starting_salary"]:
        lines.append(f"| {k} | {cov[k]} | {cov[k]*100//n}% |")
    lines += ["", "## ソフト属性①(推定OK・マッチング用)", "",
              "| 属性 | 充足社数 | 充足率 |", "|---|---|---|"]
    for k in SOFT:
        lines.append(f"| {k} | {cov['soft.'+k]} | {cov['soft.'+k]*100//n}% |")
    lines.append(f"| trend_note | {cov['trend_note']} | {cov['trend_note']*100//n}% |")
    lines += ["", "## 業界別 平均年収(有報grade)充足", "",
              "| 業界 | 社数 | 年収充足 |", "|---|---|---|"]
    for ind, v in sorted(by_ind.items(), key=lambda x: -x[1]["n"]):
        lines.append(f"| {ind} | {v['n']} | {v['avg_salary']} |")
    lines += ["", f"## 平均年収を数字表示できない社(定性提案) — {len(no_salary)}社", "",
              "（Source-or-Silence: 有報grade出典が無いため数字を出さず定性文で薦める）", ""]
    lines += ["- " + s for s in sorted(no_salary)]
    (ROOT / "coverage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    allc = companies()
    total = len(allc)
    todo = [(c, n, i) for c, n, i in allc if not is_done(c)]
    if LIMIT:
        todo = todo[:LIMIT]
    done0 = total - len([1 for c, n, i in allc if not is_done(c)])
    print(f"=== shindan run_all: 全{total} / 済{done0} / 今回対象{len(todo)} ===", flush=True)
    processed = 0
    for cid, name, ind in todo:
        try:
            data = extract.extract_company(cid, name, ind)
            json.dump(data, open(ATTR / f"{cid}.json", "w"), ensure_ascii=False, indent=1)
            sal = data["facts"]["avg_salary"]
            processed += 1
            print(f"  [{done0+processed}/{total}] {name}({ind}) 年収={'○'+str(sal['value']) if sal else '×'} "
                  f"初任給={'○' if data['facts']['starting_salary'] else '×'} tags={data['soft']['job_tags']['value']}",
                  flush=True)
        except Exception as e:
            print(f"  ERR {cid}: {e}"); traceback.print_exc()
            continue
        if processed % CP_EVERY == 0:
            checkpoint(done0 + processed, total)
    checkpoint(done0 + processed, total)
    print(f"=== 完了: 今回{processed}社処理 / 抽出済{len(os.listdir(ATTR))}社 ===", flush=True)


if __name__ == "__main__":
    main()
