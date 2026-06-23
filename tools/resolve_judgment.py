#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resolve_judgment.py — 「要判断(オスカー)」を構造的に解消(オスカーに戻さず自律処理)。

【全体】FBで対象コマ不明→要判断 になっていた社を、Claudeでコマ別(a)(b)(c)に再分類して自律処理:
  (a)明確修正(他社比較削除/(静かに)/読点/年数/旧字体) → 即反映
  (b)事実追記 → 裏取り(公式定性事実のみ・出典なき数字は捏造せずdata_caveatへ据置=Source-or-Silence)
  (c)固有名詞の1文補足 → 追記
反映: lint=0 → D1台本UPDATE(image_url不変) → before-keys canary → 200検証 → setreflected(要判断→N次完了)。
画像未完なら台本反映せず画像生成キューへ(本タスク対象は投入済=画像あり)。
使い方: resolve_judgment.py 社名:slug 社名:slug ...
"""
import json
import re
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOK / "scripts"))
import phase_c_lib as L      # noqa: E402
import deploy_salary as D    # noqa: E402
import scenario_lints_v5_ext as v5  # noqa: E402
import persona_review as PR  # noqa: E402 (data_caveat queue)

import os
ENV = REPO / "tools" / ".env.phase_c"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
GAS_URL = os.environ["SHEET_WEBAPP_URL"].strip()
GAS_TOKEN = os.environ["SHEET_API_TOKEN"].strip()
RULES = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")

MAP_SYS = (
    "あなたはトーキャリ10コマFBの自律処理担当。人間の【全体】FBを、各コマに紐づく実行可能な指示へ"
    "マッピングし分類する。分類: (a)明確修正(他社比較で自社が下に見える表現削除/(静かに)等ト書き削除/"
    "読点誤り/旧字体/年数計算ミス) (b)事実追記(公式の定性事実を該当コマに追記。**出典なき数字は禁止**) "
    "(c)固有名詞の1文補足(読者が知らない製品名等)。各指示に対象コマ番号を必ず付ける(台本を見て最適なコマ)。"
    "数字の裏取りが要る項目は needs_factcheck=true。JSONのみ。")


def gas(params):
    return requests.get(GAS_URL, params={**params, "token": GAS_TOKEN}, timeout=60).json()


def human_fb(company):
    d = gas({"mode": "companyrow", "company": company})
    fbs = [r["fb"] for r in d.get("rounds", []) if r.get("fb")]
    return "\n---\n".join(fbs), d.get("status", "")


def d1_cur(slug):
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


def map_fb(company, fb, cur):
    blob = "\n".join(f"[コマ{n}] {json.dumps(c['script'],ensure_ascii=False)} / main={c['main_copy']}"
                     for n, c in sorted(cur.items()))
    prompt = (f"会社: {company}\n【台本】\n{blob}\n\n【人間FB(全体)】\n{fb}\n\n"
              '次のJSONで: {"items":[{"koma":int,"type":"a|b|c","instruction":"該当コマへの実行指示",'
              '"needs_factcheck":bool}]}')
    txt = L._anthropic(prompt, system=MAP_SYS, max_tokens=2000)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0)).get("items", [])
    except Exception:
        return []


def scenario(slug, cur, overrides):
    koma = []
    for n, c in sorted(cur.items()):
        ov = overrides.get(n)
        koma.append({"koma_number": n, "script": ov["script"] if ov else c["script"],
                     "overlay_text": {"main_copy": ov["main_copy"] if ov else c["main_copy"],
                                      "sub": ov["sub_copy"] if ov else c["sub_copy"]}})
    return {"meta": {"slug": slug}, "koma": koma}


def process(company, slug):
    rec = {"company": company, "slug": slug, "a": 0, "b": 0, "c": 0, "komas": [],
           "caveats": 0, "reflected": False, "note": ""}
    fb, status = human_fb(company)
    if not fb:
        rec["note"] = "FB無し"; return rec
    cur = d1_cur(slug)
    if not cur:
        rec["note"] = "D1台本なし(画像/投入待ち)"; return rec
    items = map_fb(company, fb, cur)
    from collections import OrderedDict
    by_koma = OrderedDict()
    held = []
    for it in items:
        koma = it.get("koma")
        typ = it.get("type", "a")
        if koma not in cur:
            continue
        rec[typ] = rec.get(typ, 0) + 1
        guard = ("【公式の定性事実のみ・出典なき数字は載せない(載せられないなら追記しない)】"
                 if it.get("needs_factcheck") else "")
        by_koma.setdefault(koma, []).append((typ, guard + it.get("instruction", ""), it.get("needs_factcheck")))
    overrides = {}
    for koma, lst in by_koma.items():
        instr = "このコマへの指示(全て反映・捏造/出典なき数字禁止):\n" + "\n".join(f"- {x[1]}" for x in lst)
        res = L.fix_koma_text(slug, koma, instr, RULES, cur[koma])
        if res.get("changed"):
            overrides[koma] = res["after"]; rec["komas"].append(koma)
        else:
            for x in lst:
                if x[2]:  # needs_factcheck かつ未反映 → caveat据置
                    held.append({"koma": koma, "detail": x[1][:180], "persona": "resolve(b)"})
    if held:
        rec["caveats"] = PR.queue_factcheck(slug, company, held)
    # lint
    rep = v5.run_ext_lints(scenario(slug, cur, overrides), slug)
    rec["lint"] = rep["errors"]
    if rep["errors"] > 0 or not overrides:
        rec["note"] = f"lint err={rep['errors']} / 反映{len(overrides)}" + ("(変更なし)" if not overrides else "")
        return rec
    # D1反映 + canary + setreflected
    cb = D.canary_snapshot({slug}); D.backup_d1(slug)
    for koma, after in overrides.items():
        D.wrangler(["--command", D.update_sql(slug, koma, after)])
    ca = D.canary_snapshot({slug})
    drift = [s for s in cb if cb[s] != ca.get(s)]
    if drift:
        rec["note"] = f"🛑canary異常{drift}"; return rec
    try:
        j = requests.get(f"{D.API_BASE}/api/companies/{slug}", timeout=30).json()
        rec["api200"] = len(j.get("panels", [])) == 10
    except Exception:
        rec["api200"] = False
    if rec["api200"]:
        gas({"mode": "setreflected", "company": company})  # 要判断→N次完了
        rec["reflected"] = True
    return rec


def main():
    targets = [a.split(":", 1) for a in sys.argv[1:]]
    print(f"=== 要判断 自律解消 {len(targets)}社 ===\n")
    results = []
    for company, slug in targets:
        try:
            r = process(company, slug)
        except Exception as e:
            import traceback; traceback.print_exc()
            r = {"company": company, "slug": slug, "note": f"例外:{e}", "reflected": False,
                 "a": 0, "b": 0, "c": 0, "komas": [], "caveats": 0}
        results.append(r)
        print(f"  {company:10}({slug:16}) (a){r.get('a',0)}(b){r.get('b',0)}(c){r.get('c',0)} "
              f"反映koma{r['komas']} caveat{r['caveats']} setreflected={r['reflected']} {r.get('note','')}")
    refl = sum(1 for r in results if r["reflected"])
    print(f"\n=== 要判断から外せた: {refl}/{len(results)}社 / caveat据置 {sum(r['caveats'] for r in results)}件 ===")
    (REPO / "tools" / "_resolve_judgment_last.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
