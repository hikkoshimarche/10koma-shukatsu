#!/usr/bin/env python3
"""selection_info.json → company_selection(タブC正テーブル) へ変換投入するSQLを構築。
表示ルール適用: (a)締切・イベント系スケジュールは未来日付のみ(終了受付/過去イベント除外・告知系は60日以内可)
              (b)曖昧日付(9月末等)は年明示に正規化(例2026年9月末)。
evidence/token_coverageはD1に入れない(パイプライン側selection_info.jsonで監査継続)。link_onlyは3項目null時に1。
生成物: .backups/pre_company_selection_<ts>.sql と scratchpad/company_selection.sql
"""
import json, os, sys, glob, re, datetime, subprocess

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TS = sys.argv[1] if len(sys.argv) > 1 else "manual"
BACKUP = os.path.join(ROOT, ".backups", f"pre_company_selection_{TS}.sql")
SQL = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/company_selection.sql"
TODAY = datetime.date(2026, 7, 24)
FLOOR60 = TODAY - datetime.timedelta(days=60)
# 締切・イベント(未来のみ) vs 告知(60日以内可)
_DEADLINE_EVENT = re.compile(r"締切|締め切り|受付|エントリー期限|説明会|セミナー|面接|選考会|イベント|開催|試験|WEBテスト|適性")
_ANNOUNCE = re.compile(r"公開|告知|開始|更新|募集要項|プレエントリー")


def qq(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def _norm_date(dt):
    """曖昧日付に年を補う(9月末→2026年9月末)。既に年があればそのまま。"""
    dt = str(dt or "").strip()
    if not dt or re.search(r"20\d\d", dt):
        return dt
    m = re.search(r"(\d{1,2})月", dt)
    if m:
        mo = int(m.group(1))
        yr = TODAY.year if mo >= TODAY.month else TODAY.year + 1   # 直近の該当月
        return f"{yr}年{dt}"
    return dt


def _parse_date(dt):
    ym = re.search(r"(20\d\d)\D+(\d{1,2})(?:\D+(\d{1,2}))?", dt)
    if not ym:
        return None
    try:
        return datetime.date(int(ym.group(1)), int(ym.group(2)), int(ym.group(3) or 28))
    except ValueError:
        return None


def _filter_schedule(sched):
    """締切・イベント=未来のみ / 告知=60日以内。日付は年正規化。"""
    out = []
    for it in (sched or []):
        if not isinstance(it, dict):
            continue
        label = str(it.get("label", ""))
        it = dict(it)
        it["date"] = _norm_date(it.get("date"))
        d = _parse_date(it["date"])
        if d is None:
            continue                         # 日付不明は表示しない(締切誤り防止)
        if _DEADLINE_EVENT.search(label):
            keep = d >= TODAY                # 締切/イベントは未来のみ
        elif _ANNOUNCE.search(label):
            keep = d >= FLOOR60              # 告知は60日以内
        else:
            keep = d >= TODAY                # 既定は未来のみ(保守)
        if keep:
            out.append(it)
    return out


def _val(x):
    """fallback/None → None(=jsonに入れない), listはそのまま。"""
    if not x or (isinstance(x, dict) and "fallback" in x):
        return None
    return x


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql], cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    rows = []
    for blk in (json.loads(t[i:]) if i >= 0 else []):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT, "*/selection_info.json"))):
        slug = os.path.basename(os.path.dirname(f))
        if slug.startswith("industry"):
            continue
        info = json.load(open(f)).get("selection_info", {})
        flow = _val(info.get("senko_flow"))
        sched = _filter_schedule(_val(info.get("schedule")))
        jobs = _val(info.get("shokushu"))
        link_only = 1 if not (flow or sched or jobs) else 0
        rows.append((slug, info.get("as_of", ""), info.get("source_url", ""), link_only,
                     json.dumps(flow, ensure_ascii=False) if flow else None,
                     json.dumps(sched, ensure_ascii=False) if sched else None,
                     json.dumps(jobs, ensure_ascii=False) if jobs else None))
    # backup 現行 company_selection
    bak = ["-- company_selection 反映 前 backup"]
    try:
        for r in d1_json("SELECT company_id,as_of,source_url,link_only,flow_json,schedule_json,jobs_json FROM company_selection"):
            bak.append("INSERT OR REPLACE INTO company_selection (company_id,as_of,source_url,link_only,flow_json,schedule_json,jobs_json,updated_at) "
                       f"VALUES ({qq(r['company_id'])},{qq(r.get('as_of'))},{qq(r.get('source_url'))},{r.get('link_only',0)},"
                       f"{qq(r.get('flow_json'))},{qq(r.get('schedule_json'))},{qq(r.get('jobs_json'))},datetime('now'));")
    except Exception:
        pass
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    open(BACKUP, "w", encoding="utf-8").write("\n".join(bak) + "\n")
    # upsert
    ins = []
    for slug, asof, src, lo, fj, sj, jj in rows:
        ins.append("INSERT OR REPLACE INTO company_selection (company_id,as_of,source_url,link_only,flow_json,schedule_json,jobs_json,updated_at) "
                   f"VALUES ({qq(slug)},{qq(asof)},{qq(src)},{lo},{qq(fj)},{qq(sj)},{qq(jj)},datetime('now'));")
    open(SQL, "w", encoding="utf-8").write("\n".join(ins) + "\n")
    nflow = sum(1 for r in rows if r[4])
    nsched = sum(1 for r in rows if r[5])
    print(f"backup -> {BACKUP} ({len(bak)-1} rows) / upsert -> {SQL} ({len(rows)} 社: flow{nflow} schedule{nsched} link_only{sum(1 for r in rows if r[3])})")


if __name__ == "__main__":
    main()
