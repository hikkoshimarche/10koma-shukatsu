#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bairitsu_sweep.py — 原則D(採用倍率は出さない)違反の一括是正ハーネス。

D1ライブ基準で「倍率」語を含むコマを検出し、LLM(fix_koma_text)で『見てるのは社風/覚悟』の
主旨を保ったまま倍率言及を自然に除去。lint error0→台本列UPDATE(image_url不変)→canary→
has_effective_change(実D1が変化したコマのみ)で完了扱い。20社ごとにバッチ(--start/--count)。

業務比率(bain『市場平均の4倍』等=採用倍率でない)は『倍率』語を含まないため対象外。
whitelist(sumitomo-corp/iwatani)は除外。失敗社は隔離して継続(止めない)。

使い方:
  python3 tools/bairitsu_sweep.py --list                 # 対象社を出すだけ(実行しない)
  python3 tools/bairitsu_sweep.py --start 0 --count 20    # 先頭20社を処理(D1書込あり)
  python3 tools/bairitsu_sweep.py --start 0 --count 3 --dry  # LLM修正案の生成のみ(D1書込なし)
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L          # noqa: E402
import deploy_salary as D        # noqa: E402
import scenario_lints_v5_ext as v5  # noqa: E402

WHITELIST = {"sumitomo-corp", "iwatani"}   # scenario_lints_v5_ext.RATIO_WHITELIST と一致
INSTRUCTION = (
    "この台本に含まれる『倍率』への言及を、原則D(採用倍率は出さない方針)に沿って自然な日本語で"
    "除去してください。ただし『見てるのは社風/覚悟/人物』といった、選考で重視する主旨は必ず保持し、"
    "倍率を消して中身まで消さないこと。倍率以外の数値・事実・話者タグ・他のセリフは一切変えない。"
    "例:『倍率は高いけど、見てるのは社風』→『選考は厳しいけど、見てるのは社風』/"
    "『倍率じゃなくて、覚悟があるか』→『見てるのは、覚悟があるか』/『倍率より社風』→『見るのは社風』。"
    "『倍率は…?』のような問いは『選考、厳しいんですか…?』等、倍率語を使わない自然な問いに。生Markdown禁止。"
)


def d1_cur(slug):
    """D1ライブ台本を {koma: {script, main_copy, sub_copy}} で返す。"""
    rows = D.d1_query("SELECT panel_num,dialogue,script_json,main_copy,sub_copy "
                      f"FROM company_panels WHERE company_id='{slug}' ORDER BY panel_num")
    cur = {}
    for p in rows:
        try:
            sc = json.loads(p.get("script_json") or "[]")
        except Exception:
            sc = [x for x in (p.get("dialogue") or "").split("\n") if x.strip()]
        cur[p["panel_num"]] = {"script": sc, "main_copy": p.get("main_copy") or "",
                               "sub_copy": p.get("sub_copy") or ""}
    return cur


def bairitsu_komas(cur):
    """『倍率』語を含むコマ番号(dialogue/overlay)。数字+倍のみ(業務比率)は含めない。"""
    out = []
    for kn, c in cur.items():
        blob = "\n".join(c["script"]) + "\n" + c["main_copy"] + "\n" + c["sub_copy"]
        if "倍率" in blob:
            out.append(kn)
    return sorted(out)


def target_companies():
    """D1全社から『倍率』語を含む社(whitelist除外)を返す [(slug, [komas])]。"""
    rows = D.d1_query("SELECT DISTINCT company_id FROM company_panels "
                      "WHERE dialogue LIKE '%倍率%' OR main_copy LIKE '%倍率%' OR sub_copy LIKE '%倍率%' "
                      "ORDER BY company_id")
    res = []
    for r in rows:
        slug = r["company_id"]
        if slug in WHITELIST or slug.startswith("industry_10koma__"):
            continue
        res.append(slug)
    return res


def update_sql(slug, koma, after):
    def q(s):
        return "'" + str(s).replace("'", "''") + "'"
    dlg = "\n".join(after["script"])
    sj = json.dumps(after["script"], ensure_ascii=False)
    cols = [f"dialogue={q(dlg)}", f"script_json={q(sj)}",
            f"main_copy={q(after['main_copy'])}", f"sub_copy={q(after['sub_copy'])}"]
    return f"UPDATE company_panels SET {', '.join(cols)} WHERE company_id='{slug}' AND panel_num={koma};"


def process(slug, rules, dry=False):
    """1社処理。戻り: {slug, changed_komas, held, error}。例外は呼び出し側で隔離。"""
    cur = d1_cur(slug)
    komas = bairitsu_komas(cur)
    if not komas:
        return {"slug": slug, "changed_komas": [], "held": [], "note": "倍率語なし(既に是正済?)"}
    overrides = {}
    for kn in komas:
        res = L.fix_koma_text(slug, kn, INSTRUCTION, rules, cur[kn])
        # 実効変化 かつ 倍率が実際に消えた場合のみ採用(消し残しは hold)
        if res.get("changed"):
            after = res["after"]
            still = ("倍率" in ("\n".join(after["script"]) + after["main_copy"] + after["sub_copy"]))
            if not still:
                overrides[kn] = after
    # lint: override適用後の scenario で error0 を確認
    def _scenario():
        koma = []
        for kn, c in sorted(cur.items()):
            a = overrides.get(kn)
            s = a["script"] if a else c["script"]
            mc = a["main_copy"] if a else c["main_copy"]
            sb = a["sub_copy"] if a else c["sub_copy"]
            koma.append({"koma_number": kn, "script": s, "overlay_text": {"main_copy": mc, "sub": sb}})
        return {"meta": {"slug": slug}, "koma": koma}
    rep = v5.run_ext_lints(_scenario(), slug)
    if rep["errors"]:
        return {"slug": slug, "changed_komas": [], "held": komas,
                "error": f"lint error {rep['errors']}件→反映せずhold"}
    held = [k for k in komas if k not in overrides]   # 消し残り/変化なし=hold
    if dry:
        return {"slug": slug, "changed_komas": sorted(overrides), "held": held,
                "dry_after": {k: overrides[k]["script"] for k in overrides}}
    # 台本ソース(scenario_v4.json)も同期(将来の再生成で倍率が復活しないように)。
    _sync_scenario(slug, overrides)
    # D1反映(image_url不変)
    for kn, after in overrides.items():
        D.wrangler(["--command", update_sql(slug, kn, after)])
    return {"slug": slug, "changed_komas": sorted(overrides), "held": held}


def _sync_scenario(slug, overrides):
    """fix結果を output/<slug>/scenario_v4.json の該当komaに反映(script/overlay)。無ければskip。"""
    p = os.path.expanduser(f"~/oscar-ai/tokyari-pipeline/output/{slug}/scenario_v4.json")
    if not os.path.exists(p):
        return
    d = json.load(open(p))
    km = {k.get("koma_number"): k for k in d.get("koma", [])}
    for kn, after in overrides.items():
        k = km.get(kn)
        if not k:
            continue
        k["script"] = after["script"]
        ov = k.setdefault("overlay_text", {})
        ov["main_copy"] = after["main_copy"]
        ov["sub"] = after["sub_copy"]
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    slugs = target_companies()
    if args.list:
        print(f"倍率対象社数: {len(slugs)}")
        for i, s in enumerate(slugs):
            print(f"  [{i}] {s}")
        return 0
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")
    batch = slugs[args.start:args.start + args.count]
    print(f"=== 倍率スイープ batch [{args.start}:{args.start+args.count}] = {len(batch)}社 (全{len(slugs)}社) ===")
    tally = {"changed_komas": 0, "companies_changed": 0, "held": 0, "error": 0}
    for slug in batch:
        try:
            r = process(slug, rules, dry=args.dry)
        except Exception as ex:
            print(f"  {slug:22} ❌隔離: {ex}")
            tally["error"] += 1
            continue
        ck = r.get("changed_komas", [])
        held = r.get("held", [])
        if ck:
            tally["companies_changed"] += 1
            tally["changed_komas"] += len(ck)
        tally["held"] += len(held)
        note = r.get("error") or r.get("note") or ""
        print(f"  {slug:22} 変更koma{ck} hold{held} {note}")
    print(f"\n[batch集計] 変更社={tally['companies_changed']} 変更koマ={tally['changed_komas']} "
          f"hold={tally['held']} 隔離={tally['error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
