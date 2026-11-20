#!/usr/bin/env python3
"""難易度fanoutのD1反映SQLを構築(書き込みはしない)。
 (1) 既存問: quiz_difficulty_full.json の分類difficultyを D1 quiz_questions に UPDATE(set_id+q_text一致)。
 (2) 新規問: gen_lv1/2/3(full) + add_lv2_philosophy/add_lv4_deals(extra) を INSERT(difficulty/explanation/source/as_of付き)。
生成物: .backups/pre_difficulty_<ts>.sql(既存quiz_questions backup) と scratchpad/difficulty_apply.sql
"""
import json, os, sys, glob, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
BACKUP = os.path.join(ROOT, ".backups", f"pre_difficulty_{TS}.sql")
APPLY = os.path.join(os.environ.get("TK_SCRATCH") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / ".backups" / "scratch"), "difficulty_apply.sql")
QCOLS = "id,set_type,set_id,category,q_text,options,correct,explanation,source_url,as_of,ord,difficulty"


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql], cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    if i < 0:
        return []
    rows = []
    for blk in json.loads(t[i:]):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


def _settype(slug):
    return "industry" if slug.startswith("industry__") else "company"


upd, ins = [], []
n_upd, n_ins = 0, 0
stats = {}
# backup: 既存 quiz_questions(全difficulty対象=全社) — 件数が多いので id,difficulty のみ復元用に保存
allrows = d1_json("SELECT id, difficulty FROM quiz_questions")
bak = ["-- 難易度反映 前 backup(id,difficulty 復元用)"]
for r in allrows:
    d = r.get("difficulty")
    bak.append(f"UPDATE quiz_questions SET difficulty={('NULL' if d is None else int(d))} WHERE id={qq(r['id'])};")
open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")

for full in sorted(glob.glob(os.path.join(OUT, "*/quiz_difficulty_full.json"))):
    slug = os.path.basename(os.path.dirname(full))
    st = _settype(slug)
    sid = slug if st == "industry" else slug
    d = json.load(open(full))
    # (1) 既存difficulty UPDATE (set_id+q_text一致)
    for x in d.get("existing", []):
        lv = x.get("difficulty")
        if lv and x.get("q_text"):
            upd.append(f"UPDATE quiz_questions SET difficulty={int(lv)} WHERE set_type={qq(st)} AND set_id={qq(sid)} AND q_text={qq(x['q_text'])};")
            n_upd += 1
    # (2) 新規INSERT
    ordbase = 100
    newq = []
    for key, lv in (("gen_lv1", 1), ("gen_lv2", 2), ("gen_lv3", 3)):
        for x in d.get(key, []):
            newq.append((lv, x))
    ex = os.path.join(OUT, slug, "quiz_difficulty_extra.json")
    if os.path.exists(ex):
        e = json.load(open(ex))
        for x in e.get("add_lv2_philosophy", []):
            newq.append((2, x))
        for x in e.get("add_lv4_deals", []):
            newq.append((4, x))
    for i, (lv, x) in enumerate(newq):
        qid = f"{sid}_d{lv}_{i+1:02d}"
        opts = json.dumps(x.get("options", []), ensure_ascii=False)
        vals = ",".join([qq(qid), qq(st), qq(sid), qq(x.get("category", "その他")), qq(x.get("q_text", "")),
                         qq(opts), str(int(x.get("correct", 0))), qq(x.get("explanation", "")),
                         qq(x.get("source_url", "")), qq(x.get("as_of") or ""), str(ordbase + i), str(lv)])
        ins.append(f"INSERT OR REPLACE INTO quiz_questions ({QCOLS}) VALUES ({vals});")
        n_ins += 1
    stats[slug] = {"upd": len(d.get("existing", [])), "new": len(newq)}

open(APPLY, "w", encoding="utf-8").write("\n".join(upd + ins) + "\n")
print(f"backup -> {BACKUP} ({len(allrows)} rows)")
print(f"apply -> {APPLY} (UPDATE {n_upd} / INSERT {n_ins})")
print(f"社数 {len(stats)}")
