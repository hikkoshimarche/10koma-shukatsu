#!/usr/bin/env python3
"""鮮度更新27社の D1 UPDATE を安全に構築。
 (1) 現行D1行(quiz_questions + datasheets)を復元用SQLにbackup
 (2) ローカル鮮度版(quiz_30q_locked_v3.json + datasheet.json)から UPDATE SQL を生成
     - quiz: DELETE(company/slug) → INSERT OR REPLACE(id=slug_NN, ord=index)
     - datasheet: datasheet.html形状(SEC_MAP)へ変換して INSERT OR REPLACE
本スクリプトは D1 に書き込まない。生成物: .backups/pre_freshness_<ts>.sql と scratchpad/freshness_update.sql
"""
import json, os, sys, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
BACKUP = os.path.join(ROOT, ".backups", f"pre_freshness_{TS}.sql")
UPDATE = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/freshness_update.sql"

SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務",
           "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}


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


updated = json.load(open(os.path.join(OUT, "_quiz_freshness_state.json")))["updated"]
print(f"updated companies: {len(updated)}")

# ── (1) backup 現行D1行 ──
QCOLS = "id,set_type,set_id,category,q_text,options,correct,explanation,source_url,as_of,ord"
bak = ["-- 鮮度更新 前 backup (復元用). quiz_questions + datasheets, %d社" % len(updated)]
for slug in updated:
    rows = d1_json(f"SELECT {QCOLS} FROM quiz_questions WHERE set_type='company' AND set_id='{slug}'")
    bak.append(f"DELETE FROM quiz_questions WHERE set_type='company' AND set_id='{slug}';")
    for r in rows:
        vals = ",".join(q(r[c]) if not isinstance(r[c], int) else str(r[c])
                        for c in QCOLS.split(","))
        bak.append(f"INSERT OR REPLACE INTO quiz_questions ({QCOLS}) VALUES ({vals});")
    ds = d1_json(f"SELECT company_id,data,updated_at FROM datasheets WHERE company_id='{slug}'")
    for r in ds:
        ua = r.get("updated_at")
        ua = str(ua) if isinstance(ua, int) else (q(ua) if ua is not None else "NULL")
        bak.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({q(r['company_id'])},{q(r['data'])},{ua});")
open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")
print(f"backup -> {BACKUP} ({len(bak)} stmts)")

# ── (2) 鮮度版 UPDATE SQL ──
upd = ["-- 鮮度更新 UPDATE (2026年3月期). %d社" % len(updated)]
nq = 0
for slug in updated:
    qz = json.load(open(os.path.join(OUT, slug, "quiz_30q_locked_v3.json")))
    upd.append(f"DELETE FROM quiz_questions WHERE set_type='company' AND set_id='{slug}';")
    for i, it in enumerate(qz):
        qid = f"{slug}_{i+1:02d}"
        opts = json.dumps(it["options"], ensure_ascii=False)
        vals = ",".join([q(qid), "'company'", q(slug), q(it.get("category", "その他")),
                         q(it["q_text"]), q(opts), str(int(it["correct"])),
                         q(it.get("explanation", "")), q(it.get("source_url", "")),
                         q(it.get("as_of") or ""), str(i)])
        upd.append(f"INSERT OR REPLACE INTO quiz_questions ({QCOLS}) VALUES ({vals});")
        nq += 1
    # datasheet 変換
    dp = os.path.join(OUT, slug, "datasheet.json")
    if os.path.exists(dp):
        dj = json.load(open(dp))
        name = dj.get("name") or dj.get("company") or slug
        sections = []
        src = dj.get("sections", {})
        if isinstance(src, dict):
            for k, items in src.items():
                title = SEC_MAP.get(k, k)
                sec_items = []
                for it in (items or []):
                    if isinstance(it, dict):
                        sec_items.append({"label": "", "value": it.get("fact", it.get("value", "")),
                                          "source_url": it.get("source_url", "")})
                if sec_items:
                    sections.append({"title": title, "items": sec_items})
        data = json.dumps({"name": name, "sections": sections}, ensure_ascii=False)
        upd.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({q(slug)},{q(data)},unixepoch());")
open(UPDATE, "w", encoding="utf-8").write("\n".join(upd) + "\n")
print(f"update -> {UPDATE} ({len(upd)} stmts, {nq} quiz rows)")
