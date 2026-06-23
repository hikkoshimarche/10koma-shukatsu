#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""persona_review.py — インターンFB AI人格4体の合成レビュー層(初稿の質を上げる前さばき)。

Notion設計書「🎭 インターンFB AI人格 4体」準拠。新ループ:
  AI初稿 → 4人格が合成レビュー(並走) → AI自己修正(Source-or-Silenceガード) → lint=0 → 人間レビュー面へ。
鉄則:
  1. Source-or-Silenceガード: 仁科・千田の「根拠は?」は捏造で埋めず、factcheck→Claude裏取り経路へ。取れねば据置。
  2. 人間は外さない: 合成レビューは前さばき。既知の再発パターンに高精度で当て、新規性検出は人間に残す。
  3. ホモジナイズ防止: 4人格は別の型(網羅/具体性/ファクト/素の読者)を並走。
  4. 回路維持: 横断指摘は📚知見集(共通の修正案)へ蒸留。
本番ゲート(v5_ext lint/canary/backup)は不変。合成レビューは初稿品質を上げるだけ。
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOK / "scripts"))
import phase_c_lib as L          # noqa: E402  (_anthropic, classify_concern, fix_koma_text, extract_koma)
import scenario_lints_v5_ext as v5  # noqa: E402

ENV = REPO / "tools" / ".env.phase_c"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# 4人格 = レビュープロンプト(lint signature + 口調 + 出力フォーマット)。互いに別の型を並走。
PERSONAS = {
    "小林(徹底校閲)": (
        "あなたはインターン小林史弥＝『徹底校閲者』。パネルごとに全部見る最も網羅的な門番。"
        "次の型(lint signature)だけを高精度で当てる(新規性検出はしない): "
        "①他社比較で自社が下に見える生数字/表現(『トヨタより低い』『商社より低い』『本体より低い』)を削除 "
        "②ネガティブ/見下し表現(『〜屋さんが3兆円?』『規模は小さいけど』の多用) "
        "③ト書き『(静かに)』等の括弧表現 ④読点の誤り(不要読点) "
        "⑤事実・年数の計算ミス(例 1933年→2026年は93年なのに『87年』) "
        "⑥読者が知らない固有名詞の未説明 ⑦画像不良(白い余白/構図不自然/旧字体)。"
        "口調: 【全体】＋【N枚目】で構造化、『〜に修正する』『削除する』と命令形。"),
    "木内(具体性ハンター)": (
        "あなたはインターン木内一希＝『具体性ハンター』。汎用的すぎるを最も嫌う。"
        "次の型だけを当てる: ①入口・説明が汎用的(原則E違反) ②エピソードが弱い "
        "③説明が雑(数字の羅列で具体像が無い) ④キャラ関係性(ハルキが知識を与える主役性)の崩れ "
        "⑤横断ルール化できる指摘。口調: 【Nコマ目】＋具体的な置換セリフを「」で即提示。簡潔・実装可能。"),
    "仁科(ファクト検証)": (
        "あなたはインターン仁科嘉隆＝『ファクト検証者』。数字の根拠と論理整合を突く。"
        "次の型だけを当てる: ①出典不明な数字を問う(『この採用数は本当?根拠が不明』) "
        "②数値の論理矛盾(比率合計が100%超 等) ③意味が伝わらない発言の言い換え "
        "④接続詞・語尾の不自然さ ⑤『(静かに)』削除。"
        "口調: 【Nコマ目】、『根拠が不明』『本当の数字?』と問う。簡潔・論理的。"
        "※捏造で具体化しない。根拠を問うだけ(裏取りは後段)。"),
    "千田(素の読者)": (
        "あなたはインターン千田浩太朗＝『素の読者』。普通の就活生の直感で読んで腑に落ちるか。"
        "次の型だけを当てる: ①意味が通らない箇所 ②不自然な日本語(『〜のほうが自然』) "
        "③根拠を問う(『どこからの情報?根拠ある?』) ④冗長な語句の削除 "
        "⑤助詞の誤り ⑥表記ゆれの統一。口調: 『コマN』表記、口語・短い・直感的。方向性を示す(置換文は必須でない)。"),
}

REVIEW_SYS_TAIL = (
    "\n\n対象は10コマ漫画の台本(各コマ script配列＋overlay)。あなたの型に該当する指摘『だけ』を出す"
    "(該当なしなら空配列)。実在しない問題を創作しない。新規性のある主観評価は人間に残すので出さない。"
    '出力はJSONのみ: {"items":[{"koma":int,"detail":"指摘(あなたの口調で・該当ならば置換案も)"}]}')


def load_koma(slug):
    """scenario_v4.json から {koma_number: {script, overlay_text}} を読む(初稿)。"""
    p = TOK / "output" / slug / "scenario_v4.json"
    sc = json.loads(p.read_text(encoding="utf-8"))
    cur = {}
    for k in sc.get("koma", []):
        cur[k["koma_number"]] = {
            "script": k.get("script") or [],
            "main_copy": (k.get("overlay_text") or {}).get("main_copy", ""),
            "sub_copy": (k.get("overlay_text") or {}).get("sub", ""),
        }
    return sc, cur


def _koma_blob(cur):
    return "\n".join(f"[コマ{n}] script={json.dumps(c['script'],ensure_ascii=False)} "
                     f"main={c['main_copy']} sub={c['sub_copy']}" for n, c in sorted(cur.items()))


def review_one(persona_name, persona_prompt, company, cur):
    """1人格のレビューFBを生成。返り: [{koma,detail,persona}]。"""
    prompt = (f"会社: {company}\n【台本(初稿)】\n{_koma_blob(cur)}\n\n"
              f"{persona_prompt}{REVIEW_SYS_TAIL}")
    txt = L._anthropic(prompt, max_tokens=1500)
    m = re.search(r"\{.*\}", txt, re.S)
    items = []
    if m:
        try:
            for it in json.loads(m.group(0)).get("items", []):
                koma = it.get("koma") or L.extract_koma(it.get("detail", ""))
                items.append({"koma": koma, "detail": it.get("detail", ""), "persona": persona_name})
        except Exception:
            pass
    return items


def self_correct(slug, company, cur, fb_items, rules):
    """4人格FBをAI自己修正。Source-or-Silenceガード: factcheckは裏取り経路へ(捏造しない)。

    返り: {overrides:{koma:after}, applied:[], factcheck_held:[], preference_held:[]}。
    """
    from collections import OrderedDict
    by_koma = OrderedDict()
    factcheck_held, preference_held = [], []
    for it in fb_items:
        koma = it.get("koma")
        detail = it.get("detail", "")
        concern = L.classify_concern(detail)
        if concern == "preference" or not koma:
            preference_held.append(it); continue          # 好み/方向性 → 人間判断に残す
        if concern == "factcheck":
            factcheck_held.append(it)                       # 根拠系 → 据置(裏取りは後段factcheck経路)
            continue
        by_koma.setdefault(koma, []).append(f"[{it['persona']}] {detail}")
    overrides, applied = {}, []
    for koma, details in by_koma.items():
        if koma not in cur:
            continue
        instr = "合成レビュー指摘(全て反映・捏造禁止/出典なき数字禁止):\n" + "\n".join(f"- {d}" for d in details)
        res = L.fix_koma_text(slug, koma, instr, rules, cur[koma])
        if res.get("changed"):
            overrides[koma] = res["after"]
            applied.append({"koma": koma, "before": cur[koma]["script"],
                            "after": res["after"]["script"], "note": res.get("note", "")})
    return {"overrides": overrides, "applied": applied,
            "factcheck_held": factcheck_held, "preference_held": preference_held}


def lint_with_overrides(sc, cur, overrides):
    koma = []
    for n, c in sorted(cur.items()):
        ov = overrides.get(n)
        s = ov["script"] if ov else c["script"]
        mc = ov["main_copy"] if ov else c["main_copy"]
        sub = ov["sub_copy"] if ov else c["sub_copy"]
        koma.append({"koma_number": n, "script": s, "overlay_text": {"main_copy": mc, "sub": sub}})
    return v5.run_ext_lints({"meta": {"slug": sc.get("meta", {}).get("slug", "?")}, "koma": koma}, "?")


CAVEAT_CSV = REPO / "tools" / "data_caveat_list.csv"


def queue_factcheck(slug, company, held):
    """根拠不明な数字の据置を裏取りキュー(data_caveat_list.csv)へ自動投入(冪等)。

    本番に未確認数字が出ない担保。後段で factsheet/公式で裏取り→反映 or ぼかし(原則C/D)。
    """
    import csv
    existing = set()
    if CAVEAT_CSV.exists():
        for r in csv.reader(open(CAVEAT_CSV, encoding="utf-8")):
            if len(r) >= 3:
                existing.add((r[0], r[1], r[2][:40]))
    new_rows = []
    for it in held:
        key = (slug, str(it.get("koma")), it.get("detail", "")[:40])
        if key in existing:
            continue
        new_rows.append([slug, str(it.get("koma")), it.get("detail", "")[:200],
                         it.get("persona", ""), "未裏取り"])
    write_header = not CAVEAT_CSV.exists()
    with open(CAVEAT_CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["slug", "koma", "caveat(根拠不明な数字/事実)", "persona", "status"])
        w.writerows(new_rows)
    return len(new_rows)


def run(slug, company):
    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")
    sc, cur = load_koma(slug)
    print(f"=== 合成レビュー: {company} ({slug}) ===\n")
    # 1) 4人格 並走レビュー
    all_fb = []
    for name, pr in PERSONAS.items():
        items = review_one(name, pr, company, cur)
        all_fb.extend(items)
        print(f"--- {name}: {len(items)}件 ---")
        for it in items:
            print(f"  コマ{it['koma']}: {it['detail'][:90]}")
    # 2) AI自己修正(Source-or-Silenceガード)
    res = self_correct(slug, company, cur, all_fb, rules)
    print(f"\n--- AI自己修正: 反映{len(res['applied'])}コマ / factcheck据置{len(res['factcheck_held'])} / 好み据置{len(res['preference_held'])} ---")
    for a in res["applied"]:
        print(f"  ◆コマ{a['koma']} 修正: {a['note'][:80]}")
        print(f"    前: {json.dumps(a['before'],ensure_ascii=False)[:90]}")
        print(f"    後: {json.dumps(a['after'],ensure_ascii=False)[:90]}")
    # 3) factcheck据置 → 裏取りキュー(data_caveat_list.csv)へ自動投入(本番に未確認数字を出さない担保)
    n_q = queue_factcheck(slug, company, res["factcheck_held"])
    print(f"\n--- 裏取りキュー投入: {n_q}件(新規) → data_caveat_list.csv ---")
    # 4) lint=0 確認
    rep = lint_with_overrides(sc, cur, res["overrides"])
    print(f"--- lint(自己修正後): errors={rep['errors']} warnings={rep['warnings']} {'✅' if rep['errors']==0 else '❌'} ---")
    return {"fb": all_fb, "result": res, "lint": rep, "caveat_queued": n_q}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--company", required=True)
    args = ap.parse_args()
    out = run(args.slug, args.company)
    (REPO / "tools" / "_persona_review_last.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
