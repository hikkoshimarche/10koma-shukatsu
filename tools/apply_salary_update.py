#!/usr/bin/env python3
"""EDINET年収スイープ 採用値の一括反映。_salary_sweep_result.json の adopt_list を、
10コマscenario koma5(年収文脈のみ安全置換=dialogue+script_json同期)/datasheet/shindan avg_salary に反映。
出典=有報docID・as_of=2026年3月期。company_panelsは scenario_to_panels 再生成で同期(別段)。lint error0のみ採用。
  python tools/apply_salary_update.py --dry     # 検出のみ(置換内容を表示)
  python tools/apply_salary_update.py           # 実行(scenario/datasheet/shindan 書換 + 反映対象listを出力)
"""
import os, sys, json, re

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
RESULT = os.path.join(OUT, "_salary_sweep_result.json")
APPLIED = os.path.join(OUT, "_salary_applied.json")

# 年収コマ判定 & 旧年収値検出(平均/年収の直後の万円)
_SALARY_KOMA = re.compile(r"年収|給与|平均年間給与")
_OLD_SAL = re.compile(r"平均(?:年収)?[^0-9]{0,12}([\d,]+)万円")


def _fmt_man(man):
    return f"{man:,}万円" if man >= 1000 else f"{man}万円"


def detect_old(scenario_raw, d):
    """年収コマ(principle_focus~年収)内の平均年収直後の万円値(man整数)と原文字列を返す。"""
    for p in d.get("koma", []):
        pf = (p.get("principle_focus", "") or "") + (p.get("emotional_arc", "") or "")
        if "年収" not in pf:
            continue
        blob = json.dumps(p, ensure_ascii=False)
        m = _OLD_SAL.search(blob)
        if m:
            man = int(m.group(1).replace(",", ""))
            if 200 <= man <= 8000:                 # 妥当な平均年収(万円)
                return man, m.group(1) + "万円"
    return None, None


def apply_one(rec, dry):
    slug = rec["slug"]; yen = rec["yen"]; new_man = round(yen / 10000)
    sc = os.path.join(OUT, slug, "scenario_v4.json")
    if not os.path.exists(sc):
        return {"slug": slug, "status": "no_scenario"}
    raw = open(sc, encoding="utf-8").read()
    d = json.loads(raw)
    old_man, old_str = detect_old(raw, d)
    if not old_str:
        return {"slug": slug, "status": "no_old_salary(10koma)"}
    if abs(old_man - new_man) <= max(1, new_man * 0.005):
        # 変化なし: 10コマは据置だが datasheet/shindan は as_of/docID 付与のため更新
        chg_scenario = 0
    else:
        chg_scenario = raw.count(old_str)
    new_str = _fmt_man(new_man)
    as_of = rec.get("as_of", "2026年3月期")         # 決算月が3月でない社は実期(例2025年12月期/2026年2月期)
    # (1) 10コマ scenario: 旧年収文字列 → 新(全出現=dialogue/script_json同期)。出典有報年度もas_ofへ。
    if not dry and chg_scenario:
        raw = raw.replace(old_str, new_str)
        # 有報を含むsource文字列内の 20XX年X月期 → as_of (JSON walk・財務決算タグは非改変)
        dd0 = json.loads(raw)

        def _fix(v):
            if isinstance(v, str) and ("有報" in v or "有価証券報告書" in v):
                return re.sub(r"20\d\d年\d{1,2}月期", as_of, v)
            return v

        def _walk(o):
            if isinstance(o, dict):
                return {k: _walk(_fix(x)) for k, x in o.items()}
            if isinstance(o, list):
                return [_walk(_fix(x)) for x in o]
            return _fix(o)
        json.dump(_walk(dd0), open(sc, "w", encoding="utf-8"), ensure_ascii=False)
    # (2) shindan avg_salary(円)
    sh = os.path.join(ROOT, "shindan", "attributes", f"{slug}.json")
    shchg = None
    if os.path.exists(sh):
        sd = json.load(open(sh))
        old = sd.get("facts", {}).get("avg_salary")
        if not dry:
            sd.setdefault("facts", {})["avg_salary"] = yen
            sd["facts"]["avg_salary_as_of"] = as_of
            sd["facts"]["avg_salary_source"] = f"EDINET:{rec['docid']}"
            json.dump(sd, open(sh, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        shchg = f"{old}→{yen}"
    # (3) datasheet: 待遇/財務に平均年収を追記/更新(as_of 2026年3月期・出典docID)
    dp = os.path.join(OUT, slug, "datasheet.json")
    dschg = None
    if os.path.exists(dp):
        dd = json.load(open(dp))
        secs = dd.setdefault("sections", {})
        arr = secs.setdefault("社風・求める人物像", [])
        fact = f"{as_of}(有報)の平均年間給与は{new_str}({yen:,}円)。"
        arr[:] = [it for it in arr if not (isinstance(it, dict) and "平均年間給与" in it.get("fact", ""))]
        arr.append({"fact": fact, "source_url": f"https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{rec['docid']}.pdf",
                    "as_of": as_of})
        if not dry:
            json.dump(dd, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        dschg = new_str
    return {"slug": slug, "status": "ok", "old_man": old_man, "new_man": new_man,
            "scenario_repl": chg_scenario, "shindan": shchg, "datasheet": dschg}


def main():
    dry = "--dry" in sys.argv
    src = RESULT
    if "--from" in sys.argv:
        src = sys.argv[sys.argv.index("--from") + 1]
    res = json.load(open(src))
    adopt = res["adopt_list"]
    print(f"採用{len(adopt)}社を反映 {'[DRY]' if dry else '[実行]'}", flush=True)
    applied, skipped = [], []
    for rec in adopt:
        r = apply_one(rec, dry)
        if r["status"] == "ok":
            applied.append(r)
            print(f"  {r['slug']:16} {r['old_man']}→{r['new_man']}万円 (10コマ置換{r['scenario_repl']} / shindan{'✓' if r['shindan'] else '-'} / ds{'✓' if r['datasheet'] else '-'})", flush=True)
        else:
            skipped.append(r)
            print(f"  SKIP {r['slug']}: {r['status']}", flush=True)
    scen_changed = [r["slug"] for r in applied if r["scenario_repl"]]
    if not dry:
        json.dump({"applied": applied, "skipped": skipped, "scenario_changed": scen_changed},
                  open(APPLIED, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n反映{len(applied)}社 / scenario変更{len(scen_changed)}社 / skip{len(skipped)}社")
    print("scenario_changed:", scen_changed)


if __name__ == "__main__":
    main()
