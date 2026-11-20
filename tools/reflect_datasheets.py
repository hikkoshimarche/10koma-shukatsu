#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""増強済み local datasheet.json → D1 datasheets へ反映(対象slug限定)。
・format変換: dict(事業内容・セグメント/fact) → D1 list(事業/value)。SEC_MAP。
・今日確定の除外ルールを適用(D1を汚さない): 「◯◯は誰」人名trivia / 採用フロー・選考フロー・採用サイトメタ を除去。
  年号羅列(c)は残す。財務は温存。空セクションは出さない。
・安全: backup(現D1) → INSERT OR REPLACE(company_id限定) → canary は呼び出し側。
使い方: python3 reflect_datasheets.py <slug...>  → scratchpad に reflect.sql と reflect_backup.sql を生成(適用は別)。
"""
import json, os, sys, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
SCRATCH = os.environ.get("TK_SCRATCH") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / ".backups" / "scratch")  # 旧: 別セッションの scratchpad(消滅)→ .backups/scratch(gitignore)
SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}
SEC_ORDER = ["事業", "財務", "社風", "沿革"]
RECRUIT_META = ["選考フロー", "選考プロセス", "選考ステップ", "採用フロー", "エントリーシート", "エントリー",
                "募集要項", "採用サイト", "新卒採用サイト", "採用情報サイト", "採用活動", "採用選考方法",
                "インターンシップ", "マイページ", "本エントリー", "採用担当者", "採用ページ"]
# 非公式源(Source-or-Silence): これらを出典とするfactはD1に載せない(dropする)
NONOFFICIAL = re.compile(r"wikipedia|\.ac\.jp|\.edu|prtimes|note\.com|ameblo|hatena|toyokeizai|"
                         r"diamond|president\.jp|newspicks|wantedly|itmedia|reuters|bloomberg|"
                         r"kabutan|minkabu|nikkei\.com|yahoo|jiji|tdnet", re.I)


def _excluded(value, source_url=""):
    t = str(value or "")
    if "は誰" in t:
        return True
    if any(k in t for k in RECRUIT_META):
        return True
    if source_url and NONOFFICIAL.search(str(source_url)):   # 非公式源=Source-or-Silenceでdrop
        return True
    return False


def to_d1(slug, d1_current):
    """local の質的セクション(事業/社風/沿革)を変換・除外適用。財務は D1既存を verbatim 温存。"""
    dj = json.load(open(os.path.join(OUT, slug, "datasheet.json")))
    name = dj.get("name", slug)
    secs = dj.get("sections", {})
    out_sections = []
    # 質的セクションのみ local から(財務=主要財務 は使わない)
    for local_title in ["事業内容・セグメント", "社風・求める人物像", "沿革・基本情報"]:
        items = secs.get(local_title, []) or []
        d1_items = []
        for it in items:
            v = (it.get("fact") or it.get("value") or "").strip()
            su = it.get("source_url", "")
            if not v or _excluded(v, su):
                continue
            d1_items.append({"label": it.get("label", ""), "value": v, "source_url": su})
        if d1_items:
            out_sections.append({"title": SEC_MAP[local_title], "items": d1_items})
    # 財務: D1既存の「財務」セクションをそのまま温存(無ければ追加しない)
    fin = next((s for s in (d1_current.get("sections") or []) if s.get("title") == "財務"), None)
    if fin:
        out_sections.append(fin)
    out_sections.sort(key=lambda s: SEC_ORDER.index(s["title"]) if s["title"] in SEC_ORDER else 9)
    return {"name": name, "sections": out_sections}


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    # backup 現D1(対象slug)
    inlist = ",".join(qq(s) for s in slugs)
    r = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json",
                        "--command", f"SELECT company_id,data,updated_at FROM datasheets WHERE company_id IN ({inlist})"],
                       cwd=os.path.expanduser("~/projects/10koma-shukatsu"), capture_output=True, text=True)
    rows = json.loads(r.stdout)[0]["results"]
    bak = [f"-- reflect backup {len(rows)}社"]
    have = {row["company_id"] for row in rows}
    d1_by_slug = {row["company_id"]: json.loads(row["data"]) for row in rows}
    for row in rows:
        ua = row.get("updated_at") or "unixepoch()"
        bak.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES "
                   f"({qq(row['company_id'])},{qq(row['data'])},{qq(ua) if not str(ua).isdigit() else ua});")
    open(f"{SCRATCH}/reflect_backup.sql", "w").write("\n".join(bak) + "\n")
    # 安全: D1に既存の社のみUPDATE(新規INSERTしない=Tab Dと衝突回避)。非D1社はskip報告。
    skipped = [s for s in slugs if s not in have]
    slugs = [s for s in slugs if s in have]
    if skipped:
        print(f"  [skip] D1未存在={len(skipped)}社(UPDATE対象外): {skipped}")
    # update SQL(company_id限定・既存社のみ・INSERT OR REPLACE)
    upd = [f"-- reflect {len(slugs)}社"]
    manifest = []
    for slug in slugs:
        d1 = to_d1(slug, d1_by_slug.get(slug, {}))
        facts = sum(len(s["items"]) for s in d1["sections"])
        data = json.dumps(d1, ensure_ascii=False)
        upd.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES "
                   f"({qq(slug)},{qq(data)},unixepoch());")
        manifest.append({"slug": slug, "name": d1["name"], "sections": [(s["title"], len(s["items"])) for s in d1["sections"]],
                         "facts": facts, "in_d1_before": slug in have})
    open(f"{SCRATCH}/reflect.sql", "w").write("\n".join(upd) + "\n")
    json.dump(manifest, open(f"{SCRATCH}/reflect_manifest.json", "w"), ensure_ascii=False, indent=1)
    for m in manifest:
        print(f"  {m['name']}({m['slug']}): {m['sections']} 計{m['facts']}fact "
              f"{'(D1既存→UPDATE)' if m['in_d1_before'] else '(D1新規→INSERT)'}")
    print(f"backup {len(rows)}社 / reflect.sql {len(slugs)}社")


if __name__ == "__main__":
    main()
