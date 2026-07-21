#!/usr/bin/env python3
"""生成済みGYOKAI業界セットを D1 に安全投入するSQLを構築(書き込みはしない)。
 (1) 現行 industry 行を復元用SQLにbackup
 (2) output/industry__<slug>/quiz_30q_locked_v3.json から DELETE+INSERT SQL 生成
      id = industry__<slug>_NN, set_type='industry', set_id='industry__<slug>', ord=index
生成物: .backups/pre_gyokai_<ts>.sql と scratchpad/gyokai_insert.sql
引数: 対象GYOKAIスラグ(省略時=output配下の全 industry__* で会社セット5本を除く新規)"""
import json, os, sys, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
SLUGS = sys.argv[2:]  # industry__を除いたGYOKAIスラグ列。空なら生成物から自動。
BACKUP = os.path.join(ROOT, ".backups", f"pre_gyokai_{TS}.sql")
INS = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/gyokai_insert.sql"
QCOLS = "id,set_type,set_id,category,q_text,options,correct,explanation,source_url,as_of,ord"


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db",
                        "--remote", "--config", "api/wrangler.toml", "--json", "--command", sql],
                       cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""
    i = t.find("[")
    if i < 0:
        raise SystemExit("d1 read fail: " + t[-200:])
    rows = []
    for blk in json.loads(t[i:]):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


if not SLUGS:
    for d in sorted(os.listdir(OUT)):
        if d.startswith("industry__") and os.path.exists(os.path.join(OUT, d, "quiz_30q_locked_v3.json")):
            SLUGS.append(d[len("industry__"):])
print("対象GYOKAI:", SLUGS)

# (1) backup 現行 industry 行(対象set_idのみ)
bak = ["-- GYOKAI投入 前 backup (industry rows)"]
for slug in SLUGS:
    sid = "industry__" + slug
    rows = d1_json(f"SELECT {QCOLS} FROM quiz_questions WHERE set_type='industry' AND set_id='{sid}'")
    bak.append(f"DELETE FROM quiz_questions WHERE set_type='industry' AND set_id='{sid}';")
    for r in rows:
        vals = ",".join(q(r[c]) if not isinstance(r[c], int) else str(r[c]) for c in QCOLS.split(","))
        bak.append(f"INSERT OR REPLACE INTO quiz_questions ({QCOLS}) VALUES ({vals});")
open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")
print(f"backup -> {BACKUP} ({len(bak)} stmts)")

# (2) INSERT SQL
ins = ["-- GYOKAI業界セット投入"]
nq = 0
for slug in SLUGS:
    sid = "industry__" + slug
    qz = json.load(open(os.path.join(OUT, sid, "quiz_30q_locked_v3.json")))
    ins.append(f"DELETE FROM quiz_questions WHERE set_type='industry' AND set_id='{sid}';")
    for i, it in enumerate(qz):
        qid = f"{sid}_{i+1:02d}"
        opts = json.dumps(it["options"], ensure_ascii=False)
        vals = ",".join([q(qid), "'industry'", q(sid), q(it.get("category", "その他")),
                         q(it["q_text"]), q(opts), str(int(it["correct"])),
                         q(it.get("explanation", "")), q(it.get("source_url", "")),
                         q(it.get("as_of") or ""), str(i)])
        ins.append(f"INSERT OR REPLACE INTO quiz_questions ({QCOLS}) VALUES ({vals});")
        nq += 1
open(INS, "w", encoding="utf-8").write("\n".join(ins) + "\n")
print(f"insert -> {INS} ({len(ins)} stmts, {nq} quiz rows, {len(SLUGS)} sets)")
