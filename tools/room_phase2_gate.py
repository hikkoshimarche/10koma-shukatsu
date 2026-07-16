#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_phase2_gate.py — Phase2 アーキタイプ・ゲート(無人・自動判定)。
8アーキタイプ各1社を v3生成→room-lint5→自己チェック→D1登録(pass時)。実トークン計測→×400概算。
全通過=exit0(Phase3継続可)/1つでも失敗=exit1(停止)。1社ぶんペルソナ全文ダンプ。
"""
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
SCR = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts"))
# scripts/(runtime・ROOT=tokyari-pipeline=factsheet所在)を優先。tools/はv3等の補助のみ後段に。
sys.path.insert(0, str(REPO / "tools")); sys.path.insert(0, str(SCR))
try:
    from dotenv import load_dotenv as _ld; _ld(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
except Exception:
    pass
import room_lib as RL
import room_harness as H
import room_industry_roles_v3 as V3
import requests

# Sonnet 4.6 料金(標準): 入力 $3 / 出力 $15 per 1M tokens。この前提で概算。
PRICE_IN, PRICE_OUT = 3.0 / 1_000_000, 15.0 / 1_000_000
USAGE = {"in": 0, "out": 0, "calls": 0}
_KEY = re.sub(r"\s", "", os.environ["ANTHROPIC_API_KEY"])


def measured_anthropic(prompt, system="", model="claude-sonnet-4-6", max_tokens=3000):
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    for attempt in range(5):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                              headers={"x-api-key": _KEY, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json"}, json=body, timeout=180)
            if r.status_code in (429, 500, 502, 503, 529):
                raise requests.exceptions.RequestException(f"retry {r.status_code}")
            r.raise_for_status()
            j = r.json(); u = j.get("usage", {})
            USAGE["in"] += u.get("input_tokens", 0); USAGE["out"] += u.get("output_tokens", 0); USAGE["calls"] += 1
            return "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)
    raise RuntimeError("anthropic失敗")


RL._anthropic = measured_anthropic

GATE = [  # (slug, 社名, 18業界, アーキタイプ表示)
    ("sumitomo-corp", "住友商事", "総合商社", "総合商社"),
    ("keyence", "キーエンス", "電機・精密・重工", "理系メーカー"),
    ("nomura", "野村證券", "銀行・証券・保険", "金融"),
    ("accenture", "アクセンチュア", "コンサル", "コンサル"),
    ("euglena", "ユーグレナ", "その他（外資・新興等）", "少人数SU"),
    ("tokyo-gas", "東京ガス", "インフラ・エネルギー", "インフラ"),
    ("dentsu", "電通", "広告・メディア", "広告"),
    ("fast-retailing", "ファーストリテイリング", "小売・流通", "小売"),
]

_BANNED = RL._BANNED_NUM


def self_check(rec):
    """自己チェック: 氏名3層/人数/AI開示/倍率・出典なき数字ゼロ/人格差。合否+詳細。"""
    fails = []
    personas = rec.get("_personas", {})   # {role_key: (body, name)}
    roster = rec.get("_roster", [])
    n = len(personas)
    # 人数(spec 5〜9・最低4)
    if not (4 <= n <= 9 and n == len(roster)):
        fails.append(f"人数{n}(期待{len(roster)})")
    # 氏名3層: role_key(R*)+役割名(label)+氏名(姓 名)
    labels = {r["role_key"]: r["label"] for r in roster}
    for rk, (body, name) in personas.items():
        if not (rk.startswith("R") and labels.get(rk) and name and " " in name):
            fails.append(f"氏名3層欠落:{rk}/{name}")
    # AI開示
    for rk, (body, name) in personas.items():
        if "AIによる" not in body:
            fails.append(f"AI開示なし:{rk}")
    # 倍率/出典なき数字ゼロ: factpack SoS=0 + body内の倍率パターン0
    sos = RL.source_or_silence_lint(rec.get("factpack", {}))
    if sos:
        fails.append(f"SoS違反:{sos[:2]}")
    for rk, (body, name) in personas.items():
        if _BANNED.search(body):
            fails.append(f"倍率混入body:{rk}")
    # 人格差(labels全ユニーク・body全ユニーク)
    bodies = [b for b, n in personas.values()]
    if len(set(labels.values())) != len(labels):
        fails.append("役割名が重複(人格差不足)")
    if len(set(bodies)) != len(bodies):
        fails.append("system_promptが重複(人格差不足)")
    return fails


def main():
    print("=== Phase2 アーキタイプ・ゲート (8社・v3人数可変・実トークン計測) ===\n")
    results = []
    dump_slug = "accenture"   # 1社ぶん全文ダンプ対象(7人)
    dump_text = None
    t0 = time.time()
    for slug, name, ind18, disp in GATE:
        u0 = dict(USAGE); ts = time.time()
        try:
            rec = H.process(slug, name, force=True, industry=ind18)
        except Exception as e:
            rec = {"status": f"例外:{e}"}
        # processは_personas/_rosterを持たないので再取得のため再ラップ: processが登録済みなら_last参照不可 →
        # processの戻りにpersonas(氏名)とfactpackはある。system_prompt本文は戻りに無いので別途取得。
        di = USAGE["in"] - u0["in"]; do = USAGE["out"] - u0["out"]; dc = USAGE["calls"] - u0["calls"]
        cost = di * PRICE_IN + do * PRICE_OUT
        st = rec.get("status", "?")
        passed = (st == "registered")
        row = {"slug": slug, "name": name, "arch": disp, "n": rec.get("n_roles"),
               "lint": rec.get("lint_errors"), "status": st, "in": di, "out": do, "calls": dc,
               "cost": cost, "sec": round(time.time() - ts, 1), "dropped": rec.get("dropped_cond")}
        # self_check用にpersona本文をD1から取得(registered時)
        selfck = ["未登録=skip"]
        if passed:
            import subprocess
            p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                                "--config", str(REPO / "api" / "wrangler.toml"), "--json", "--command",
                                f"SELECT role,persona_name,system_prompt FROM room_personas WHERE company_slug='{slug}' ORDER BY role"],
                               cwd=str(REPO), capture_output=True, text=True, timeout=60)
            try:
                rows = json.loads(p.stdout[p.stdout.find("["):])[0]["results"]
            except Exception:
                rows = []
            rec["_personas"] = {r["role"]: (r["system_prompt"], r["persona_name"]) for r in rows}
            rec["_roster"] = V3.roles_for18(ind18)
            # dropped反映(role_key詰め直し後の実ロースターに合わせる)
            if rec.get("dropped_cond"):
                rec["_roster"] = [dict(r, role_key=f"R{i+1}") for i, r in
                                  enumerate([x for x in rec["_roster"] if x.get("cond") != "research_only"])]
            selfck = self_check(rec)
            if slug == dump_slug:
                lines = [f"\n{'='*70}\n■ ペルソナ全文ダンプ: {name}({slug}) {disp} {len(rows)}人\n{'='*70}"]
                for r in rows:
                    lb = {x["role_key"]: x["label"] for x in rec["_roster"]}.get(r["role"], "?")
                    lines.append(f"\n--- {r['role']} 【{lb}】 氏名: {r['persona_name']} ---\n{r['system_prompt']}")
                dump_text = "\n".join(lines)
        row["selfcheck"] = selfck
        row["gate_ok"] = passed and not selfck
        results.append(row)
        mark = "✅" if row["gate_ok"] else "❌"
        print(f"{mark} {disp:<8} {slug:<15} {row['n']}人 lint={row['lint']} {st[:20]:<20} "
              f"in={di} out={do} ${cost:.4f} {row['sec']}s selfck={'OK' if not selfck else selfck}")

    if dump_text:
        print(dump_text)

    # 集計・×400概算
    print(f"\n{'='*70}\n=== コスト実測 → ×400概算 ===")
    tot_in, tot_out = USAGE["in"], USAGE["out"]
    tot_cost = tot_in * PRICE_IN + tot_out * PRICE_OUT
    n_co = len(results)
    avg_cost = tot_cost / n_co
    avg_n = sum(r["n"] or 0 for r in results) / n_co
    print(f"  8社実測: in={tot_in:,}tok out={tot_out:,}tok calls={USAGE['calls']} 合計 ${tot_cost:.4f}")
    print(f"  1社平均: ${avg_cost:.4f} (平均{avg_n:.1f}人) / 所要 {round(time.time()-t0)}s")
    print(f"  ★全社概算(×400): ${avg_cost*400:.2f}  (料金前提 Sonnet4.6 $3/M-in・$15/M-out)")
    print(f"  ※既登録6人版377社の再生成分。新規/未登録含め上限は400社。")

    # ゲート判定
    ng = [r for r in results if not r["gate_ok"]]
    print(f"\n{'='*70}\n=== ゲート判定 ===")
    if ng:
        print(f"❌ FAIL {len(ng)}/8 アーキタイプ → Phase3停止(ブラストしない)")
        for r in ng:
            print(f"   - {r['arch']} {r['slug']}: status={r['status']} lint={r['lint']} selfck={r['selfcheck']}")
        return 1
    print(f"✅ 全8アーキタイプ ゲート通過(lint5=0 AND 自己チェックOK AND D1登録) → Phase3継続可")
    (REPO / "tools" / "_room_phase2_result.json").write_text(
        json.dumps({"results": results, "usage": USAGE, "avg_cost": avg_cost, "est_400": avg_cost * 400},
                   ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
