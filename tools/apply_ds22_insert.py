#!/usr/bin/env python3
"""未反映22社のうち fact≥5 の社を datasheets へ INSERT OR IGNORE(既存は不変=UPDATEしない)。
local output/<slug>/datasheet.json {name,sections:{key:[{fact,source_url}]}} → D1形状 {name,sections:[{title,items:[{label,value,source_url}]}]}。
backup(現行全datasheets) → 一般化canary(対象外の全hash不変) → INSERT → 実API200/件数/対象存在 確認。
usage: python apply_ds22_insert.py            (dry: SQL生成のみ)
       python apply_ds22_insert.py --apply    (実行)
"""
import json, os, sys, subprocess, hashlib, time

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}
# 第3便: 追加IR資料(統合レポート/事業会社)でisetan/pola救済。fact<5は自動SKIP。
TARGETS = ["isetan-mitsukoshi", "pola-orbis-hd"]
TS = time.strftime("%Y%m%d_%H%M%S")
BACKUP = os.path.join(ROOT, ".backups", f"pre_ds22insert_{TS}.sql")
SQLF = "/tmp/ds22_insert.sql"


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def d1(sql, write=False):
    cmd = ["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
           "--config", "api/wrangler.toml", "--json", "--command", sql]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""
    i = t.find("[")
    if i < 0:
        raise SystemExit(f"d1 fail: {p.stdout[-300:]} {p.stderr[-300:]}")
    rows = []
    for blk in json.loads(t[i:]):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


import re
# 品質ルール(今日確定): 穴埋め形式・登記情報・人名trivia(◯◯は誰)・年号羅列 を除外
_BAD_KW = re.compile(r"(本社所在地|所在地は|本店|資本金|従業員数|設立年月日|設立日|代表取締役|代表者は|社長は|会長は|は誰|"
                     r"の名称[:：]|の一つ[:：]|を務め(るのは|ているのは)|株式数|上場|証券コード)")


def _is_bad_fact(v):
    v = (v or "").strip()
    if len(v) < 10:
        return True
    if _BAD_KW.search(v):
        return True
    # 穴埋め形式:「ラベル: 値」で述語(。/です/ます/した/ている/する等)で終わらない
    if re.search(r"[:：]", v) and not re.search(r"(です|ます|でした|した|ている|いる|する|なる|れる|られる|ない|た|。)$", v):
        return True
    return False


def to_d1_shape(dj):
    name = dj.get("name")
    sections = []
    for k, items in dj.get("sections", {}).items():
        title = SEC_MAP.get(k, k)
        sec_items = [{"label": "", "value": it.get("fact", ""), "source_url": it.get("source_url", "")}
                     for it in (items or []) if isinstance(it, dict) and it.get("fact")
                     and not _is_bad_fact(it.get("fact", ""))]
        if sec_items:
            sections.append({"title": title, "items": sec_items})
    return {"name": name, "sections": sections}, sum(len(s["items"]) for s in sections)


def main():
    apply = "--apply" in sys.argv
    # 反映対象の datasheet.json → D1形状(fact数再確認: ≥5のみ)
    inserts = []
    for slug in TARGETS:
        dp = os.path.join(OUT, slug, "datasheet.json")
        if not os.path.exists(dp):
            print(f"  SKIP {slug}: datasheet.json無(corpus取得不可)"); continue
        dj = json.load(open(dp))
        shape, nf = to_d1_shape(dj)
        if nf < 5:
            print(f"  SKIP {slug}: fact{nf}<5"); continue
        data = json.dumps(shape, ensure_ascii=False)
        inserts.append((slug, nf, data))
    print(f"INSERT対象 {len(inserts)}社: " + ", ".join(f"{s}({n})" for s, n, _ in inserts))

    # backup(現行全datasheets) + before snapshot(全hash)
    rows = d1("SELECT company_id,data,updated_at FROM datasheets")
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    with open(BACKUP, "w", encoding="utf-8") as f:
        f.write(f"-- backup datasheets {len(rows)}行 {TS}\n")
        for r in rows:
            ua = r.get("updated_at")
            ua = str(ua) if isinstance(ua, int) else (qq(ua) if ua is not None else "NULL")
            f.write(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({qq(r['company_id'])},{qq(r['data'])},{ua});\n")
    before = {r["company_id"]: hashlib.md5((r["data"] or "").encode()).hexdigest() for r in rows}
    print(f"backup → {BACKUP} ({len(rows)}行) / before {len(before)}社")

    # INSERT OR IGNORE SQL
    lines = ["-- ds22 INSERT OR IGNORE (fact≥5, 対象限定)"]
    for slug, nf, data in inserts:
        lines.append(f"INSERT OR IGNORE INTO datasheets (company_id,data,updated_at) VALUES ({qq(slug)},{qq(data)},unixepoch());")
    open(SQLF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"SQL → {SQLF} ({len(inserts)}文)")

    already = [s for s, _, _ in inserts if s in before]
    if already:
        print(f"⚠️ 既存(INSERT OR IGNOREでskip)= {already}")

    if not apply:
        print("\n=== DRY-RUN (--apply で実行) ===")
        return

    # 実行(1文ずつ=API200確認)
    ok = 0
    for slug, nf, data in inserts:
        sql = f"INSERT OR IGNORE INTO datasheets (company_id,data,updated_at) VALUES ({qq(slug)},{qq(data)},unixepoch());"
        p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                            "--config", "api/wrangler.toml", "--json", "--command", sql],
                           cwd=ROOT, capture_output=True, text=True)
        good = '"success": true' in p.stdout or '"changes"' in p.stdout
        print(f"  {'✅' if good else '❌'} {slug}")
        if good:
            ok += 1
    # after snapshot + 一般化canary
    rows2 = d1("SELECT company_id,data FROM datasheets")
    after = {r["company_id"]: hashlib.md5((r["data"] or "").encode()).hexdigest() for r in rows2}
    changed_nontarget = [c for c in before if c not in set(TARGETS) and before[c] != after.get(c)]
    added = [c for c in after if c not in before]
    cnt = d1("SELECT COUNT(*) c FROM datasheets")[0]["c"]
    print(f"\n=== 結果 ===")
    print(f"INSERT成功 {ok}/{len(inserts)} / datasheets件数 {len(before)}→{cnt}")
    print(f"新規追加 {len(added)}社: {sorted(added)}")
    print(f"canary(対象外hash変化) = {changed_nontarget if changed_nontarget else '0件=不変✅'}")
    miss = [s for s, _, _ in inserts if s not in after]
    print(f"対象で未挿入: {miss if miss else 'なし=全12社存在✅'}")


if __name__ == "__main__":
    main()
