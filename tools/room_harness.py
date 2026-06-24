#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_harness.py — 1社=factpack抽出→6人格生成→5lint→D1 room_personas登録(冪等)。

純Claude API・Mac非依存。冪等(room_sync_state.csv・登録済slugスキップ)。
本番ゲート: 5lint error=0 でなければ登録ブロック。Source-or-Silence厳守(出典なき数値は捏造しない)。
使い方: room_harness.py --slug mitsui-bussan [--name 三井物産] [--force]
        room_harness.py --all   (factsheetがある全社・冪等)
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import room_lib as RL  # noqa: E402
import company_master as _cm  # noqa: E402
try:
    from dotenv import load_dotenv as _ld; _ld(ROOT / ".env")
except Exception:
    pass

REPO10 = Path(os.environ.get("REPO10") or "/Users/oscardodds/projects/10koma-shukatsu")
WCONF = Path(os.environ.get("WRANGLER_CONFIG") or (REPO10 / "api" / "wrangler.toml"))
if not WCONF.exists():
    WCONF = ROOT / "data" / "wrangler.toml"
STATE = ROOT / "output" / "room_sync_state.csv"
COMPANIES_JSON = Path(os.environ.get("COMPANIES_JSON") or str(REPO10 / "public" / "companies.json"))
if not COMPANIES_JSON.exists():
    COMPANIES_JSON = ROOT / "data" / "companies.json"

EXTRACT_SYS = (
    "あなたはトーキャリ・ルームのファクトパック抽出器。会社のファクトシートから、AI OBが発話してよい"
    "『出典付きの事実』だけを構造化する。Source-or-Silence厳守: 出典の無い数字・倍率・年次別年収ラダー・"
    "口コミ残業時間は絶対に入れない(無いものは入れない=黙る)。会社名は正式名称。JSONのみ出力。")


def _parse_json_lenient(txt):
    """```フェンス除去 → {...}抽出 → loads → 末尾修復 の順で寛容にパース。失敗時None。"""
    if not txt:
        return None
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt.strip(), flags=re.M)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    raw = m.group(0)
    try:
        return json.loads(raw)
    except Exception:
        pass
    # 末尾切れ: 最後の完全な } まで切り詰め
    for cut in range(len(raw) - 1, 0, -1):
        if raw[cut] == "}":
            try:
                return json.loads(raw[:cut + 1])
            except Exception:
                continue
    return None


def extract_factpack(slug, company, factsheet):
    # 真因: Claudeが文字列値内に半角"を生で入れJSON破損する事が確率的に起きる(途中切れではない)。
    # 対策: ①半角"禁止のプロンプト硬化 ②最大3回リトライ(指数バックオフ) ③最後にClaude自身でJSON修復。捏造はしない。
    import time
    prompt = (
        f"会社: {company}\n【ファクトシート】\n{factsheet[:12000]}\n\n"
        "次のJSONで出力:\n"
        '{"company":"正式名称",'
        '"stateable_facts":[{"claim":"出典付きで言える事実","出典":"出典名","可視役割":["R1".."R6"のうち話せる役割]}],'
        '"deflection_rules":[{"topic":"倍率/年次年収額/残業数値/配属確約 等","line":"正直に出典なしと言い語れる範囲へ誘導する返し"}],'
        '"dna_envelope":["体験を語る封筒(事業範囲・社風)。この外は創作しない"]}\n'
        "出典が無い数字・倍率は stateable_facts に入れない。deflection_rulesで正直に逃げる形にする。\n"
        "【厳守】有効なJSONのみ出力。文字列値の中で半角ダブルクォート(\")は絶対に使わない"
        "(引用は『』を使う)。改行は文字列値の外でのみ。```で囲まない。")
    last_raw = None
    tries = 5  # 確率的にJSON破損するため複数回(単発成功率↑)。不運な全滅を防ぐ。
    for attempt in range(tries):
        txt = RL._anthropic(prompt, system=EXTRACT_SYS, max_tokens=8000)
        last_raw = txt
        fp = _parse_json_lenient(txt)
        if fp:
            return fp
        if attempt < tries - 1:
            time.sleep(min(2 ** attempt, 8))  # 指数バックオフ(上限8s)
    # 最終手段: Claude自身に「値は変えずに有効なJSONへ修復」させる(捏造でなく構文修復)
    try:
        fix = RL._anthropic(
            "次は無効なJSONです。内容(値)は一切変えず、半角\"のエスケープ等で構文だけ有効なJSONに直して、"
            "JSONのみ返してください(```で囲まない):\n\n" + (last_raw or "")[:14000],
            system="あなたはJSON構文修復器。値の意味は変えず、有効なJSONのみ返す。", max_tokens=8000)
        return _parse_json_lenient(fix)
    except Exception:
        return None


def visible_facts(factpack, role):
    out = []
    for f in factpack.get("stateable_facts", []):
        vis = f.get("可視役割") or f.get("visible") or []
        if role in vis or not vis:
            out.append(f)
    return out


def build_persona(slug, company, role, factpack):
    rdef = RL.ROLES[role]
    facts = visible_facts(factpack, role)
    facts_txt = "\n".join(f"- {f.get('claim')} (出典:{f.get('出典') or f.get('source')})" for f in facts)
    defl_txt = "\n".join(f"- {d.get('topic')} → {d.get('line')}" for d in factpack.get("deflection_rules", []))
    env_txt = " / ".join(factpack.get("dna_envelope", []))
    special = rdef.get("special", "")
    sys_p = (
        "あなたはトーキャリ・ルームのAI OB訪問システムプロンプト設計者。金型(三井物産GOLD)と同じ構造・密度で、"
        "1人格のsystem promptを書く。必ず含める: ①最初の発話でAI開示 ②役割の語り口 ③話してよい会社の事実(出典付き・"
        "可視factのみ) ④Source-or-Silence(出典なき数字・倍率・年次年収ラダーは言わない/deflectionで正直に逃げる) "
        "⑤体験はdna_envelope内で・存在しない事業制度は創作しない ⑥NG領域は他人格に振る ⑦意思決定を歪めない+深刻相談は人へ "
        "⑧LINE向け2〜4行で短く。出力はsystem prompt本文のみ(前置き不要)。")
    prompt = (
        f"会社: {company} / 役割: {role} {rdef['label']} / 語り口: {rdef['tone']}\n"
        f"{('特則: '+special) if special else ''}\n"
        f"【この役割が話してよい事実(出典付き)】\n{facts_txt}\n"
        f"【deflection_rules(公式に無い→正直に逃げる)】\n{defl_txt}\n"
        f"【dna_envelope(体験の封筒)】{env_txt}\n"
        f"【NGルーティング】{rdef['ng']}\n\n{RL.GUARDRAILS}\n\n"
        "上記を金型と同じ構造で1つのsystem promptに統合して書け。")
    body = RL._anthropic(prompt, system=sys_p, max_tokens=2000)
    # 設計『共通ガードレールは全6人格の必携ブロック』→ verbatim付与(envelope/AI開示/ルーティング/R6を確実に内包)。
    env_line = f"\n【封筒(dna_envelope)】体験を語るのは自由だが範囲内({env_txt})。存在しない事業・制度・固有の機密数字は創作しない。"
    full = body.strip() + "\n\n" + RL.GUARDRAILS + env_line
    name = _extract_name(body, role)
    return full, name


def _extract_name(prompt_body, role):
    # L4設計上、人格は「実在の人物ではありません」と明示するAIロール=実在氏名を持たない。
    # 旧実装は本文の最初の「」(=セリフ例)を誤って氏名に拾い汚染していた。役割ラベルを正とする。
    return RL.ROLES[role]["label"]


def load_state():
    done = {}
    if STATE.exists():
        for r in csv.reader(open(STATE, encoding="utf-8")):
            if len(r) >= 2:
                done[r[0]] = r[1]
    return done


def save_state(slug, status):
    new = not STATE.exists()
    with open(STATE, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["slug", "status", "ts"])
        import time as _t
        w.writerow([slug, status, _t.strftime("%Y-%m-%d %H:%M")])


def register_d1(slug, personas, factpack):
    """6人格をD1 room_personas に INSERT OR REPLACE。"""
    def q(v):
        return "'" + str(v).replace("'", "''") + "'"
    for role, (prompt, name) in personas.items():
        sql = (f"INSERT OR REPLACE INTO room_personas (company_slug,role,persona_name,system_prompt,fact_pack_json,status) "
               f"VALUES ({q(slug)},{q(role)},{q(name)},{q(prompt)},{q(json.dumps(factpack,ensure_ascii=False))},'active')")
        p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                            "--config", str(WCONF), "--command", sql], cwd=str(REPO10),
                           capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            return False, p.stderr[:150]
    return True, "ok"


def process(slug, company, force=False):
    rec = {"slug": slug, "company": company}
    _rev = {v: k for k, v in getattr(_cm, "TOKYARI_SLUG_OVERRIDES", {}).items()}
    tslug = _rev.get(slug, slug)
    fs = ROOT / "output" / tslug / "factsheet.md"
    if not fs.exists():
        fs = ROOT / "output" / slug / "factsheet.md"
    if not fs.exists():
        rec["status"] = "skip(factsheet無)"; return rec
    factpack = extract_factpack(slug, company, fs.read_text(encoding="utf-8"))
    if not factpack:
        rec["status"] = "skip(factpack抽出失敗)"; return rec
    personas = {role: build_persona(slug, company, role, factpack) for role in RL.ROLES}
    prompts = {r: p for r, (p, n) in personas.items()}
    report, total = RL.run_room_lints(prompts, factpack)
    rec["lint_errors"] = total
    rec["lint_detail"] = {r: e for r, e in report.items() if e}
    if total > 0:
        rec["status"] = f"lint error {total}→登録ブロック"; return rec
    ok, msg = register_d1(slug, personas, factpack)
    rec["status"] = "registered" if ok else f"D1失敗:{msg}"
    rec["personas"] = {r: n for r, (p, n) in personas.items()}
    rec["factpack"] = factpack
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--name")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    cj = json.loads(COMPANIES_JSON.read_text(encoding="utf-8"))
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    done = load_state()

    if args.all:
        targets = [(s, id2name.get(s, s)) for s in id2name if (ROOT / "output" / s / "factsheet.md").exists()]
    else:
        targets = [(args.slug, args.name or id2name.get(args.slug, args.slug))]

    reg = 0
    for slug, company in targets:
        if not args.force and done.get(slug) == "registered":
            continue
        try:
            rec = process(slug, company, args.force)
        except Exception as e:
            rec = {"slug": slug, "status": f"例外:{e}"}
        st = rec.get("status", "?")
        if st == "registered":
            reg += 1
            save_state(slug, "registered")
            print(f"  {slug:18} ✅ registered 人格={rec.get('personas')}")
        else:
            save_state(slug, st)
            print(f"  {slug:18} ⚠ {st} {rec.get('lint_detail') or ''}")
        if args.slug:
            (ROOT / "output" / "_room_last.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n=== room登録: {reg}/{len(targets)}社 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
