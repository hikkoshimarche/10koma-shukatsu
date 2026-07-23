#!/usr/bin/env python3
"""ES kit 出荷257社を es_kits テーブルへ投入するSQLを構築(書き込みはしない)。
 API想定スキーマ: es_kits(company_id PK, data TEXT) / data={name, motivation:[{text,source_url}], questions:[{text,note}]}
 出力: scratchpad/eskit_insert.sql (CREATE TABLE IF NOT EXISTS + INSERT OR REPLACE)。es_kitsは新規=backup不要。"""
import json, os, glob

OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
INS = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/eskit_insert.sql"


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


rows = ["-- ES kit 投入",
        "CREATE TABLE IF NOT EXISTS es_kits (company_id TEXT PRIMARY KEY, data TEXT, updated_at INTEGER);"]
n = 0
for p in sorted(glob.glob(os.path.join(OUT, "*/es_kit.json"))):
    slug = os.path.basename(os.path.dirname(p))
    if slug.startswith("industry__"):
        continue
    kit = json.load(open(p))
    mats = kit.get("motivation_sheet", {}).get("materials", [])
    motivation = [{"text": (m.get("fact", "") + ("　→ " + m["prompt"] if m.get("prompt") else "")),
                   "source_url": m.get("source_url", "")} for m in mats]
    questions = [{"text": iq.get("q", ""), "note": iq.get("hint", "")}
                 for iq in kit.get("interview_questions", [])]
    data = json.dumps({"name": kit.get("name", slug), "motivation": motivation, "questions": questions},
                      ensure_ascii=False)
    rows.append(f"INSERT OR REPLACE INTO es_kits (company_id,data,updated_at) VALUES ({qq(slug)},{qq(data)},unixepoch());")
    n += 1
open(INS, "w", encoding="utf-8").write("\n".join(rows) + "\n")
print(f"insert -> {INS} ({n} es_kits, {len(rows)} stmts)")
