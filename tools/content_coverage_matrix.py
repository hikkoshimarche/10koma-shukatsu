#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""400社 x datasheet/quiz/es_kit 充足マトリクス。read-only（書き込みはCSVのみ）。
OK=D1にある / SYNC_GAP=ローカルにあるがD1に無い（反映だけで解消） / MISSING=生成が必要。"""
import csv, json, os, subprocess, sys

REPO = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
CSV_PATH = os.path.join(OUT, "content_coverage.csv")
QUIZ_F = ("quiz_30q.json", "quiz.json", "quiz_questions.json")
DS_F = ("datasheet.json",)
EK_F = ("es_kit.json", "eskit.json")


def d1(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql],
                       cwd=REPO, capture_output=True, text=True)
    t = p.stdout or ""
    i = t.find("[")
    if i < 0:
        sys.exit("D1 read fail:\n" + (p.stderr or t)[-800:])
    rows = []
    for b in json.loads(t[i:]):
        if isinstance(b, dict):
            rows.extend(b.get("results", []))
    return rows


def local(slug, names):
    for n in names:
        p = os.path.join(OUT, slug, n)
        if os.path.exists(p) and os.path.getsize(p) > 2:
            return n
    return ""


def st(loc, ind1):
    return "OK" if ind1 else ("SYNC_GAP" if loc else "MISSING")


comp = json.load(open(os.path.join(REPO, "public/companies.json"), encoding="utf-8"))
cs = [(c.get("slug") or c.get("id"), c.get("name", ""), k) for k, a in comp.items() for c in a]
cs = [x for x in cs if x[0]]
print("companies.json 社数: %d" % len(cs))

ds1 = {r["company_id"] for r in d1("SELECT company_id FROM datasheets")}
ek1 = {r["company_id"] for r in d1("SELECT company_id FROM es_kits")}
qv = {}
for r in d1("SELECT set_id, COALESCE(difficulty,2) lv, COUNT(*) n FROM quiz_questions "
            "WHERE set_type='company' GROUP BY set_id, COALESCE(difficulty,2)"):
    qv.setdefault(r["set_id"], {})[int(r["lv"])] = int(r["n"])
print("D1実測: datasheets=%d / es_kits=%d / quiz(社)=%d" % (len(ds1), len(ek1), len(qv)))

rows = []
for slug, name, ind in cs:
    ld, lq, le = local(slug, DS_F), local(slug, QUIZ_F), local(slug, EK_F)
    lv = qv.get(slug, {})
    rows.append({"slug": slug, "name": name, "industry": ind,
                 "datasheet": st(ld, slug in ds1), "quiz": st(lq, bool(lv)),
                 "es_kit": st(le, slug in ek1), "quiz_q_total": sum(lv.values()),
                 "lv1": lv.get(1, 0), "lv2": lv.get(2, 0), "lv3": lv.get(3, 0), "lv4": lv.get(4, 0),
                 "local_ds": ld, "local_quiz": lq, "local_ek": le})

os.makedirs(OUT, exist_ok=True)
with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("\nCSV -> %s (%d行)\n" % (CSV_PATH, len(rows)))

print("===== 充足サマリー =====")
for k in ("datasheet", "quiz", "es_kit"):
    t = {"OK": 0, "SYNC_GAP": 0, "MISSING": 0}
    for r in rows:
        t[r[k]] += 1
    print("%-10s OK=%3d  SYNC_GAP=%3d  MISSING=%3d" % (k, t["OK"], t["SYNC_GAP"], t["MISSING"]))

thin = [r["slug"] for r in rows if r["quiz"] == "OK" and min(r["lv1"], r["lv2"], r["lv3"], r["lv4"]) == 0]
print("\nquiz: D1にあるがLv1-4のどれかが0問の社 = %d" % len(thin))
if thin:
    print("  例: " + ", ".join(thin[:15]))

for k in ("datasheet", "quiz", "es_kit"):
    g = [r["slug"] for r in rows if r[k] == "SYNC_GAP"]
    if g:
        print("\n[%s] SYNC_GAP（生成済み・D1未反映）%d社:\n  %s" % (k, len(g), " ".join(g)))

md = [r["slug"] for r in rows if r["datasheet"] == "MISSING"]
mq = [r["slug"] for r in rows if r["quiz"] == "MISSING"]
both = sorted(set(md) & set(mq))
print("\n[生成が必要] datasheet MISSING=%d / quiz MISSING=%d / 両方=%d" % (len(md), len(mq), len(both)))
if both:
    print("  両方MISSING（quiz_fanoutが対で作れる社）:\n  " + " ".join(both))
