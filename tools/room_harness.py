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
import room_names as RN  # noqa: E402
import room_industry_roles as RIR  # noqa: E402  (v2互換・map13等)
import room_industry_roles_v3 as RIRV3  # noqa: E402  (v3人数可変ロースター)
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


def scrub_sos_factpack(fp):
    """factpackから倍率・年次別年収ラダーを決定的に除去(Source-or-Silence)。モデル遵守に依存しない関所前掃除。
    - stateable_facts: 倍率/ラダーを含むclaimは丸ごと落とす(出典付きでも数値倍率は語らせない=room方針)。
    - deflection_rules: topic『倍率』は残すが、lineの具体数値は『(非公表)』へ置換。"""
    if not fp:
        return fp
    facts = []
    for f in fp.get("stateable_facts", []):
        c = str(f.get("claim", ""))
        if RL._BANNED_NUM.search(c) or RL._LADDER.search(c):
            continue
        facts.append(f)
    fp["stateable_facts"] = facts
    for d in fp.get("deflection_rules", []):
        for k in ("line", "topic"):
            if d.get(k):
                d[k] = RL._LADDER.sub("年次別年収(非公表)", RL._BANNED_NUM.sub("倍率(非公表)", str(d[k])))
    # dna_envelope からも念のため数値倍率を除去
    fp["dna_envelope"] = [RL._BANNED_NUM.sub("倍率(非公表)", str(x)) for x in fp.get("dna_envelope", [])]
    return fp


def scrub_body_numbers(body):
    """生成body内の倍率・年次年収ラダーの具体数値を決定的に無害化(deflection例として漏れた数値の最終掃除)。"""
    b = RL._BANNED_NUM.sub("倍率(公式非公表)", body)
    b = RL._LADDER.sub("年次別年収(公式非公表)", b)
    return b


def visible_facts(factpack, role):
    out = []
    for f in factpack.get("stateable_facts", []):
        vis = f.get("可視役割") or f.get("visible") or []
        if role in vis or not vis:
            out.append(f)
    return out


def build_persona(slug, company, roledef, factpack, industry="", roster=None):
    """v3 roledef(role_key/label/gist/tone/pseudo_interview/female/ob/cond) から1人格を生成。人数可変。"""
    role = roledef["role_key"]
    label = roledef["label"]; tone = roledef["tone"]; gist = roledef["gist"]
    # 特則: 擬似面接(事業部長)/退職者OB絶対ルール は フラグから金型テキストを注入(role prefix非依存)。
    special = ""
    if roledef.get("pseudo_interview"):
        special = RL.ROLES["R3"].get("special", "")
    elif roledef.get("ob"):
        special = RL.ROLES["R6"].get("special", "")
    # NGルーティング: 他の全人格(v3ロースターのlabel)へ振る先を提示
    others = "・".join(f"{r['role_key']}={r['label']}" for r in (roster or []) if r["role_key"] != role)
    facts = visible_facts(factpack, role)
    facts_txt = "\n".join(f"- {f.get('claim')} (出典:{f.get('出典') or f.get('source')})" for f in facts)
    defl_txt = "\n".join(f"- {d.get('topic')} → {d.get('line')}" for d in factpack.get("deflection_rules", []))
    env_txt = " / ".join(factpack.get("dna_envelope", []))
    sys_p = (
        "あなたはトーキャリ・ルームのAI OB訪問システムプロンプト設計者。金型(三井物産GOLD)と同じ構造・密度で、"
        "1人格のsystem promptを書く。必ず含める: ①最初の発話でAI開示 ②役割の語り口 ③話してよい会社の事実(出典付き・"
        "可視factのみ) ④Source-or-Silence(出典なき数字・倍率・年次年収ラダーは言わない/deflectionで正直に逃げる) "
        "⑤体験はdna_envelope内で・存在しない事業制度は創作しない ⑥NG領域は他人格に振る ⑦意思決定を歪めない+深刻相談は人へ "
        "⑧LINE向け2〜4行で短く。出力はsystem prompt本文のみ(前置き不要)。"
        "【重要】この人格は業界別の役割。実在しない属性(その業界・会社に無い職種や海外駐在等)は付けない(Source-or-Silence)。"
        "【厳守・倍率】採用倍率など倍率の具体的数値(例『56倍』)は本文に一切書かない。deflectionの例示としても数値を出さない。"
        "倍率に触れる場合は『公式非公表なので数値では言えない』とだけ書く。Markdownの表(|区切り)を本文に埋め込まない。")
    name = RN.personal_name(slug, role, female=roledef.get("female"))  # 氏名=決定的生成(女性フラグ対応)。実在社員ではないAIロール表示名。
    prompt = (
        f"会社: {company} / 業界: {industry} / 役割: {role} {label} / 氏名: {name} / 語り口: {tone}\n"
        f"【この役割が主に語ること】{gist}\n"
        f"{('特則: '+special) if special else ''}\n"
        f"【この役割が話してよい事実(出典付き)】\n{facts_txt}\n"
        f"【deflection_rules(公式に無い→正直に逃げる)】\n{defl_txt}\n"
        f"【dna_envelope(体験の封筒)】{env_txt}\n"
        f"【NGルーティング】守備範囲外は他人格({others})へ振る\n\n{RL.GUARDRAILS}\n\n"
        f"上記を金型と同じ構造で1つのsystem promptに統合して書け。役割「{label}」として『主に語ること』に沿う人物像にする。"
        f"最初のAI開示で『私はAIによるOB訪問シミュレーション、{company}の{label}「{name}」です。"
        "実在の特定社員ではなく、公式情報をもとにした人物像です』と名乗ること(実在人物を騙らない)。")
    body = RL._anthropic(prompt, system=sys_p, max_tokens=2000)
    # 設計『共通ガードレールは全人格の必携ブロック』→ verbatim付与(envelope/AI開示/ルーティング/OBを確実に内包)。
    env_line = f"\n【封筒(dna_envelope)】体験を語るのは自由だが範囲内({env_txt})。存在しない事業・制度・固有の機密数字は創作しない。"
    full = body.strip() + "\n\n" + RL.GUARDRAILS + env_line
    full = scrub_body_numbers(full)   # ★最終掃除: deflection例として漏れた倍率数値を決定的に無害化
    return full, name


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


BACKUP_DIR = ROOT / "output" / "room_backups"


def _q(v):
    return "'" + str(v).replace("'", "''") + "'"


def _backup_existing(slug):
    """反映前にD1の既存room_personas行をローカルJSONへ退避(可逆性の担保)。"""
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", str(WCONF), "--json", "--command",
                        f"SELECT company_slug,role,persona_name,system_prompt,fact_pack_json,status "
                        f"FROM room_personas WHERE company_slug={_q(slug)}"],
                       cwd=str(REPO10), capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return None
    try:
        rows = json.loads(p.stdout[p.stdout.find("["):])[0]["results"]
    except Exception:
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    import time as _t
    (BACKUP_DIR / f"{slug}.json").write_text(
        json.dumps({"ts": _t.strftime("%Y-%m-%d %H:%M"), "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return len(rows)


def register_d1(slug, personas, factpack):
    """N人格(人数可変)をD1 room_personas に登録。可逆(事前backup)・冪等(INSERT OR REPLACE)。
    人数減の孤児対策: 登録keyに無い旧role行はDELETE(insert成功後)。三井は呼び出し側で除外。"""
    _backup_existing(slug)                      # ①可逆: 既存をJSON退避
    new_keys = list(personas.keys())
    for role, (prompt, name) in personas.items():   # ②冪等upsert
        sql = (f"INSERT OR REPLACE INTO room_personas (company_slug,role,persona_name,system_prompt,fact_pack_json,status) "
               f"VALUES ({_q(slug)},{_q(role)},{_q(name)},{_q(prompt)},{_q(json.dumps(factpack,ensure_ascii=False))},'active')")
        p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                            "--config", str(WCONF), "--command", sql], cwd=str(REPO10),
                           capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            return False, p.stderr[:150]
    # ③孤児掃除: 新ロースターに無い旧role(例 6→5で余るR6)を削除。三井は対象外(呼び出しで除外済)。
    keylist = ",".join(_q(k) for k in new_keys)
    dp = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                         "--config", str(WCONF), "--command",
                         f"DELETE FROM room_personas WHERE company_slug={_q(slug)} AND role NOT IN ({keylist})"],
                        cwd=str(REPO10), capture_output=True, text=True, timeout=60)
    if dp.returncode != 0:
        return False, f"orphan cleanup失敗:{dp.stderr[:120]}"
    return True, "ok"


def _factpack_has_research(factpack):
    """cond=research_only 判定(Source-or-Silence): factpackに研究/R&D/研究所の記述があるか。"""
    blob = json.dumps(factpack, ensure_ascii=False)
    return any(k in blob for k in ("研究", "R&D", "ＲＤ", "研究所", "開発職", "技術研究", "創薬"))


def process(slug, company, force=False, industry=""):
    rec = {"slug": slug, "company": company, "industry": industry}
    if slug == "mitsui-bussan":
        rec["status"] = "skip(三井GOLD=不可侵)"; return rec        # showcase保護(二重の安全弁)
    roster = RIRV3.roles_for_company(slug, industry)   # ★slug対応(「その他」外資大手の誤バケツ防止)
    if not roster:
        rec["status"] = f"skip(未知アーキタイプ:{industry})"; return rec
    # cond=research_only: 研究記述の無い会社では落とす(Source-or-Silence=実在しない職種を作らない)。factpack取得後に判定。
    dropped = []
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
    factpack = scrub_sos_factpack(factpack)   # ★関所前掃除: 倍率/年次年収ラダーを決定的に除去(SoS)
    if any(r.get("cond") == "research_only" for r in roster) and not _factpack_has_research(factpack):
        dropped = [r["role_key"] for r in roster if r.get("cond") == "research_only"]
        roster = [r for r in roster if r.get("cond") != "research_only"]
        roster = [dict(r, role_key=f"R{i+1}") for i, r in enumerate(roster)]  # role_key詰め直し
    rec["archetype"] = RIRV3.archetype_for(slug, industry); rec["n_roles"] = len(roster)
    if dropped:
        rec["dropped_cond"] = dropped
    personas = {r["role_key"]: build_persona(slug, company, r, factpack, industry, roster) for r in roster}
    prompts = {r: p for r, (p, n) in personas.items()}
    role_meta = {r["role_key"]: r for r in roster}
    report, total = RL.run_room_lints(prompts, factpack, role_meta=role_meta)
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
    ap.add_argument("--industry13", help="v2 13分類でフィルタ(旧・互換)")
    ap.add_argument("--industry", help="v3アーキタイプでフィルタ(例 メーカー/総合商社)。段階展開用。--all と併用")
    args = ap.parse_args()
    cj = json.loads(COMPANIES_JSON.read_text(encoding="utf-8"))
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}  # slug→18業界(role定義の引き先)
    done = load_state()

    if args.all:
        targets = [(s, id2name.get(s, s)) for s in id2name if (ROOT / "output" / s / "factsheet.md").exists()]
        targets = [(s, n) for s, n in targets if s != "mitsui-bussan"]  # 三井GOLD=不可侵(showcase)
        if args.industry:   # v3段階展開: 指定アーキタイプの社のみ(slug対応)
            targets = [(s, n) for s, n in targets if RIRV3.archetype_for(s, id2ind.get(s, "")) == args.industry]
        elif args.industry13:  # 旧v2フィルタ(互換)
            targets = [(s, n) for s, n in targets if RIR.map13(id2ind.get(s, "")) == args.industry13]
    else:
        targets = [(args.slug, args.name or id2name.get(args.slug, args.slug))]

    reg = 0
    for slug, company in targets:
        if not args.force and done.get(slug) == "registered-v3":  # v3済のみskip(v2 'registered'は再処理=アップグレード)
            continue
        try:
            rec = process(slug, company, args.force, industry=id2ind.get(slug, ""))
        except Exception as e:
            rec = {"slug": slug, "status": f"例外:{e}"}
        st = rec.get("status", "?")
        if st == "registered":
            reg += 1
            save_state(slug, "registered-v3")
            print(f"  {slug:18} ✅ registered({rec.get('n_roles')}人 {rec.get('archetype')}) 人格={rec.get('personas')}")
        else:
            save_state(slug, st)
            print(f"  {slug:18} ⚠ {st} {rec.get('lint_detail') or ''}")
        if args.slug:
            (ROOT / "output" / "_room_last.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n=== room登録: {reg}/{len(targets)}社 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
