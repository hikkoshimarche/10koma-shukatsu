#!/usr/bin/env python3
"""浄化済みdatasheet(130社)を D1 datasheets へ反映するSQLを構築(書き込みはしない)。
 backup(現行D1 datasheets) + INSERT OR REPLACE(datasheet.html形状へ変換)。
生成物: .backups/pre_dsall_<ts>.sql と scratchpad/dsall_update.sql"""
import json, os, sys, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
BACKUP = os.path.join(ROOT, ".backups", f"pre_dsall_{TS}.sql")
UPD = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/dsall_update.sql"
SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql],
                       cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    if i < 0:
        raise SystemExit("d1 read fail: " + t[-200:])
    rows = []
    for blk in json.loads(t[i:]):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


import glob
changed = sorted(os.path.basename(os.path.dirname(d)) for d in glob.glob(os.path.join(OUT, "*/datasheet.json"))
                 if not os.path.basename(os.path.dirname(d)).startswith("industry__"))
print("浄化済み対象:", len(changed))

# backup(単一IN句で一括取得=高速)
inlist = ",".join(qq(s) for s in changed)
rows = d1_json(f"SELECT company_id,data,updated_at FROM datasheets WHERE company_id IN ({inlist})")
bak = ["-- datasheet浄化 前 backup (%d社)" % len(rows)]
for r in rows:
    ua = r.get("updated_at")
    ua = str(ua) if isinstance(ua, int) else (qq(ua) if ua is not None else "NULL")
    bak.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({qq(r['company_id'])},{qq(r['data'])},{ua});")
open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")
print(f"backup -> {BACKUP} ({len(bak)-1} rows)")

# update (浄化済み local datasheet.json → D1形状)
upd = ["-- datasheet浄化 UPDATE"]
for slug in changed:
    dj = json.load(open(os.path.join(OUT, slug, "datasheet.json")))
    name = dj.get("name") or slug
    sections = []
    for k, items in dj.get("sections", {}).items():
        title = SEC_MAP.get(k, k)
        sec_items = [{"label": "", "value": it.get("fact", ""), "source_url": it.get("source_url", "")}
                     for it in (items or []) if isinstance(it, dict) and it.get("fact")]
        if sec_items:
            sections.append({"title": title, "items": sec_items})
    data = json.dumps({"name": name, "sections": sections}, ensure_ascii=False)
    upd.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({qq(slug)},{qq(data)},unixepoch());")
open(UPD, "w", encoding="utf-8").write("\n".join(upd) + "\n")
print(f"update -> {UPD} ({len(upd)-1} rows)")
