#!/usr/bin/env python3
"""年収反映の D1 バッチ: scenario変更社の company_panels を scenario_to_panels --v4(埋込lintゲート)で再生成し
INSERT を収集(lint error社は自動除外)、datasheet(平均年間給与追記166社)も D1 shape へ。統合SQLを出力。
  出力: scratchpad/salary_panels.sql / salary_datasheets.sql / salary_lint_failed.txt
"""
import os, sys, json, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
PIPE = os.path.expanduser("~/oscar-ai/tokyari-pipeline")
APPLIED = os.path.join(OUT, "_salary_applied.json")
SCR = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad"
SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def main():
    ap = json.load(open(APPLIED))
    changed = ap["scenario_changed"]
    applied = ap["applied"]
    panels_sql, lint_failed = [], []
    for i, slug in enumerate(changed):
        p = subprocess.run([sys.executable, "scripts/scenario_to_panels.py", "--slug", slug, "--v4"],
                           cwd=PIPE, capture_output=True, text=True)
        if p.returncode != 0:
            lint_failed.append(slug); continue
        for ln in p.stdout.splitlines():
            pass
        # INSERT開始以降(複数行dialogue対応)
        started = False
        for ln in p.stdout.split("\n"):
            if ln.startswith("INSERT OR REPLACE INTO company_panels"):
                started = True
            if started:
                panels_sql.append(ln)
        if (i + 1) % 30 == 0:
            sys.stderr.write(f"  panels {i+1}/{len(changed)}\n")
    open(os.path.join(SCR, "salary_panels.sql"), "w", encoding="utf-8").write("\n".join(panels_sql) + "\n")
    open(os.path.join(SCR, "salary_lint_failed.txt"), "w").write("\n".join(lint_failed) + "\n")

    # datasheet(166社: 平均年間給与追記済ローカルjson → D1 shape)
    ds_sql = []
    for rec in applied:
        slug = rec["slug"]
        dp = os.path.join(OUT, slug, "datasheet.json")
        if not os.path.exists(dp):
            continue
        d = json.load(open(dp))
        sections = []
        for k, arr in d.get("sections", {}).items():
            it2 = [{"label": "", "value": it.get("fact", ""), "source_url": it.get("source_url", "")}
                   for it in (arr or []) if isinstance(it, dict) and it.get("fact")]
            if it2:
                sections.append({"title": SEC_MAP.get(k, k), "items": it2})
        payload = json.dumps({"name": d.get("name", slug), "sections": sections}, ensure_ascii=False)
        ds_sql.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({qq(slug)},{qq(payload)},unixepoch());")
    open(os.path.join(SCR, "salary_datasheets.sql"), "w", encoding="utf-8").write("\n".join(ds_sql) + "\n")
    print(f"panels INSERT: {sum(1 for l in panels_sql if l.startswith('INSERT'))} / lint_failed: {len(lint_failed)} / datasheet UPDATE: {len(ds_sql)}")
    if lint_failed:
        print("lint_failed:", lint_failed)


if __name__ == "__main__":
    main()
