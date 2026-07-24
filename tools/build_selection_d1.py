#!/usr/bin/env python3
"""selection_info を D1 selection_info テーブルへ反映するSQLを構築(書き込みはしない)。
 CREATE TABLE IF NOT EXISTS + backup(現行行) + INSERT OR REPLACE(全項目JSON)。
 空カード禁止: link_only 社も『採用リンクのみ』の最小情報で保存(表示側で1本表示)。
生成物: .backups/pre_selection_<ts>.sql と scratchpad/selection_insert.sql
"""
import json, os, sys, glob, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
BACKUP = os.path.join(ROOT, ".backups", f"pre_selection_{TS}.sql")
INS = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/selection_insert.sql"


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql], cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    rows = []
    for blk in (json.loads(t[i:]) if i >= 0 else []):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


CREATE = ("CREATE TABLE IF NOT EXISTS selection_info (company_id TEXT PRIMARY KEY, data TEXT, "
          "as_of TEXT, updated_at INTEGER);")

files = sorted(glob.glob(os.path.join(OUT, "*/selection_info.json")))
ins = [CREATE]
n = 0
for f in files:
    slug = os.path.basename(os.path.dirname(f))
    if slug.startswith("industry"):
        continue
    d = json.load(open(f))
    info = d.get("selection_info", {})
    payload = json.dumps({"name": d.get("name", slug), **info}, ensure_ascii=False)
    ins.append(f"INSERT OR REPLACE INTO selection_info (company_id,data,as_of,updated_at) "
               f"VALUES ({qq(slug)},{qq(payload)},{qq(info.get('as_of',''))},unixepoch());")
    n += 1

# backup(現行 selection_info・存在すれば)
bak = ["-- selection_info 反映 前 backup"]
try:
    rows = d1_json("SELECT company_id,data,as_of FROM selection_info")
    for r in rows:
        bak.append(f"INSERT OR REPLACE INTO selection_info (company_id,data,as_of,updated_at) "
                   f"VALUES ({qq(r['company_id'])},{qq(r['data'])},{qq(r.get('as_of',''))},unixepoch());")
except Exception:
    pass
os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")
open(INS, "w", encoding="utf-8").write("\n".join(ins) + "\n")
print(f"backup -> {BACKUP} ({len(bak)-1} rows) / insert -> {INS} ({n} 社)")
