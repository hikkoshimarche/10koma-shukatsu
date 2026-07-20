#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/refresh_facts.py — ②表示ファクト(avg_salary/starting_salary)のみ再抽出して
既存 attributes/<slug>.json を in-place 更新。①ソフト属性/trend_note(LLM生成分)は保持=再課金なし。
extract.py の抽出ロジック改善後に走らせる。
"""
import json, os
from pathlib import Path
import extract

ATTR = Path(__file__).resolve().parent / "attributes"
caveats = extract.load_caveats()
changed = 0
now_av = now_st = 0
for f in sorted(os.listdir(ATTR)):
    if not f.endswith(".json"):
        continue
    d = json.load(open(ATTR / f))
    factsheet, corpus = extract.load_company(d["slug"])
    av = extract.extract_avg_salary(d["name"], caveats, factsheet, corpus)
    st = extract.extract_starting_salary(factsheet, corpus)
    o_av = bool(d["facts"].get("avg_salary")); o_st = bool(d["facts"].get("starting_salary"))
    d["facts"]["avg_salary"] = av
    d["facts"]["starting_salary"] = st
    notes = [n for n in d.get("lint", {}).get("notes", []) if "salary" not in n]
    if av is None:
        notes.append("avg_salary: 有報grade出典なし→null(定性提案)")
    if st is None:
        notes.append("starting_salary: 抽出/照合不可→null")
    d.setdefault("lint", {})["notes"] = notes
    json.dump(d, open(ATTR / f, "w"), ensure_ascii=False, indent=1)
    if bool(av) != o_av or bool(st) != o_st:
        changed += 1
    now_av += bool(av); now_st += bool(st)
print(f"refresh完了: 変更{changed}社 / avg_salary={now_av}社 starting_salary={now_st}社")
