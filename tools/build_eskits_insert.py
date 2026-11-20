#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""es_kit.json → es_kits テーブルの INSERT OR IGNORE SQL(行が無い社のみ挿入)を構築。
対象= 引数slug(無ければ全es_kit.json)。書き込みはしない(SQL出力のみ)。
data={name, motivation:[{text,source_url}], questions:[{text,note}]}(既存build_eskit_d1と同形式)。"""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
SC = os.environ.get("TK_SCRATCH") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / ".backups" / "scratch")  # 旧: 別セッションの scratchpad(消滅)→ .backups/scratch(gitignore)


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def build(slugs=None):
    rows = ["CREATE TABLE IF NOT EXISTS es_kits (company_id TEXT PRIMARY KEY, data TEXT, updated_at INTEGER);"]
    n = 0
    made = []
    paths = ([os.path.join(OUT, s, "es_kit.json") for s in slugs] if slugs
             else sorted(glob.glob(os.path.join(OUT, "*/es_kit.json"))))
    for p in paths:
        slug = os.path.basename(os.path.dirname(p))
        if slug.startswith("industry__") or not os.path.exists(p):
            continue
        kit = json.load(open(p))
        mats = kit.get("motivation_sheet", {}).get("materials", [])
        motivation = [{"text": (m.get("fact", "") + ("　→ " + m["prompt"] if m.get("prompt") else "")),
                       "source_url": m.get("source_url", "")} for m in mats]
        questions = [{"text": iq.get("q", ""), "note": iq.get("hint", "")}
                     for iq in kit.get("interview_questions", [])]
        data = json.dumps({"name": kit.get("name", slug), "motivation": motivation, "questions": questions},
                          ensure_ascii=False)
        rows.append(f"INSERT OR IGNORE INTO es_kits (company_id,data,updated_at) VALUES ({qq(slug)},{qq(data)},unixepoch());")
        made.append(slug); n += 1
    open(f"{SC}/eskits_insert.sql", "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print(f"eskits_insert.sql: {n}社 INSERT OR IGNORE")
    return made


if __name__ == "__main__":
    build([a for a in sys.argv[1:] if not a.startswith("-")] or None)
