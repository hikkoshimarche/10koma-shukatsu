#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_lib.py — トーキャリ・ルーム L4 共通: 6役割マスタ/ガードレール/5lint/Claude。

設計: Notion「Layer 3 会話エンジン設計」/ 金型「三井6人格パック GOLD」準拠。
純Claude API・Mac非依存(クラウドバッチ化可)。
"""
from __future__ import annotations
import json
import os
import re
import time

# ---- 6役割マスタ(Layer1・固定) + NGルーティング ----
ROLES = {
    "R1": {"label": "若手エース", "tone": "カジュアル寄り敬語(『いやー正直』『ぶっちゃけ』)",
           "ng": "女性キャリア・産休育休→R4 / 採用基準・面接評価→R3 / 海外駐在の生活詳細→R5 / 辞めた本音・転職市場→R6 / 中堅の出世観→R2 / 経営戦略→R3"},
    "R2": {"label": "中堅マネージャー", "tone": "論理的(『結論から言うと』)",
           "ng": "女性キャリア→R4 / 採用基準→R3 / 退職本音→R6 / 海外駐在生活詳細→R5"},
    "R3": {"label": "事業部長", "tone": "落ち着いた敬語・含み笑い",
           "ng": "個別人事案件 / 生々しい給与→R2 / 退職本音→R6",
           "special": "擬似面接モード: 学生が『面接して』と言ったら面接官として質問→学生回答→社風(採用3軸)に紐づくFB。点数・倍率・合否確率は出さない。終了で通常復帰。"},
    "R4": {"label": "中堅女性", "tone": "等身大(『私の場合はね』)。模範生にしない・管理職一歩手前",
           "ng": "男性出世競争→R2 / 採用裏話→R3 / 駐在生活詳細→R5"},
    "R5": {"label": "海外駐在経験者", "tone": "海外目線(『向こうではね』)",
           "ng": "国内本社の細部→R2 / 最新若手事情→R1"},
    "R6": {"label": "退職者OB", "tone": "客観(『正直、外から見ると』『振り返ってみると』)",
           "ng": "現職の最新社内事情・未来戦略→R3や現職メンバー",
           "special": "退職者の絶対ルール: ①会社を批判しすぎない(『会社がダメ』でなく『私の人生ではこう判断した』) ②必ず感謝も伝える(得たスキル・人脈・経験の価値) ③学生の意思決定を歪めない(辞めるべき/入るべきを断定しない)"},
}

GUARDRAILS = (
    "【共通ガードレール】\n"
    "1.【AI開示】最初の発話で必ず『私はAIによるOB訪問シミュレーションです』と伝える。隠さない。\n"
    "2.【Source-or-Silence】会社の数字・制度はファクトパックのstateable_factsにある出典付き事実だけを話す。"
    "無いことを聞かれたらdeflection_rulesに従い正直に『公式に出てない』と言い語れる範囲へ誘導。"
    "倍率・検証不能な年収額・口コミの残業時間は絶対に数字で言わない。\n"
    "3.【封筒】自分の体験はdna_envelopeの範囲内で自由に語ってよいが、存在しない事業・制度をでっち上げない。\n"
    "4.【他人格ルーティング】NG領域の質問は他の人格に振る。\n"
    "5.【意思決定を歪めない】学生の人生選択を断定で誘導しない。\n"
    "6.【セーフティ】メンタル不調・ハラスメント等の深刻な相談はAIの限界を認め、大学キャリアセンター等 人の窓口を案内。"
)

# 出典なき数値=禁止(Source-or-Silence)。倍率/年次別年収ラダー/口コミ残業の混入検出。
_BANNED_NUM = re.compile(r"(倍率\s*[0-9]+|[0-9]+\s*倍(?!率))")
_LADDER = re.compile(r"(1年目|3年目|5年目|10年目).{0,8}[0-9,]+\s*万")


def _anthropic(prompt, system="", model="claude-sonnet-4-6", max_tokens=3000):
    key = re.sub(r"\s", "", os.environ["ANTHROPIC_API_KEY"])
    import requests
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    for attempt in range(4):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                              headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json"}, json=body, timeout=120)
            if r.status_code in (429, 500, 502, 503, 529):
                raise requests.exceptions.RequestException(f"retry {r.status_code}")
            r.raise_for_status()
            return "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)
    raise RuntimeError("anthropic失敗")


# ---- 5種 ルームlint(本番ゲート・error=登録ブロック) ----
def source_or_silence_lint(factpack):
    errs = []
    for f in factpack.get("stateable_facts", []):
        if not f.get("出典") and not f.get("source"):
            errs.append(f"出典なしfact: {str(f.get('claim'))[:40]}")
        claim = str(f.get("claim", ""))
        if _BANNED_NUM.search(claim):
            errs.append(f"倍率混入: {claim[:40]}")
        if _LADDER.search(claim):
            errs.append(f"年次年収ラダー混入: {claim[:40]}")
    return errs


def disclosure_lint(prompt):
    # AI開示: 「AI」+(シミュレーション/AIによる) かつ 初回/最初/冒頭 のいずれか の存在で概念充足。
    ai = ("AI" in prompt) and ("シミュレーション" in prompt or "AIによる" in prompt or "AI開示" in prompt or "実在の" in prompt)
    first = any(w in prompt for w in ("最初", "初回", "冒頭", "1通目", "一通目", "はじめに", "初めに"))
    return [] if (ai and first) else ["AI開示文が無い"]


def ng_routing_lint(prompt, role):
    # NGルーティング: 他人格へ振る概念。役割ID(R2等)/『〜さん』/振る/任せる/聞いた方/へ など広く。
    has = any(w in prompt for w in ("振る", "振っ", "→", "さんに", "さんへ", "さんが", "他の人格",
                                    "聞いた方", "に聞い", "任せ", "に相談", "へどうぞ", "得意")) \
        or any(f"R{n}" in prompt for n in range(1, 7))
    return [] if has else ["NGルーティングが無い"]


def envelope_lint(prompt, factpack):
    # 封筒制約: 創作しない/でっち上げない/存在しない事業/封筒/範囲内 等の概念。
    has = any(w in prompt for w in ("封筒", "envelope", "創作しない", "創作せず", "でっち上げ",
                                    "存在しない事業", "存在しない制度", "範囲内", "範囲を超え", "勝手に作"))
    return [] if has else ["envelope制約が無い"]


def r6_safety_lint(prompt, is_ob):
    # 退職者OB(v3では職種別に①②へ分化・role keyのR6prefixに依存しない)= ob=True全員に適用。
    if not is_ob:
        return []
    crit = any(w in prompt for w in ("批判しすぎ", "批判し過ぎ", "会社がダメ", "私の人生では", "決めつけ"))
    grat = ("感謝" in prompt) or ("得たもの" in prompt) or ("価値" in prompt and "経験" in prompt)
    return [] if (crit and grat) else ["OB: 批判しすぎない+感謝 が無い"]


def body_sos_lint(prompt):
    # Source-or-Silence を「生成body」にも適用。factpackが綺麗でも、deflection例として本文に
    # 『採用倍率(56倍)』等が混入する事故(fast-retailing型)を関所で止める。倍率/年次年収ラダーを検出。
    errs = []
    if _BANNED_NUM.search(prompt):
        errs.append("body倍率混入")
    if _LADDER.search(prompt):
        errs.append("body年次年収ラダー混入")
    return errs


def run_room_lints(prompts_by_role, factpack, role_meta=None):
    """全N人格(人数可変) + factpack に5種lint。{role:[errs]} とerror総数を返す。
    role_meta={role_key:{'ob':bool,...}} が渡ればob=Trueにr6_safety適用。
    後方互換: role_meta省略時は role=='R6' をOBとみなす(v2)。
    ※SoSはfactpackとbody両方に適用(body_sos_lint)。"""
    report = {}
    sos = source_or_silence_lint(factpack)
    for role, prompt in prompts_by_role.items():
        is_ob = bool(role_meta[role].get("ob")) if (role_meta and role in role_meta) else (role == "R6")
        e = []
        e += disclosure_lint(prompt)
        e += ng_routing_lint(prompt, role)
        e += envelope_lint(prompt, factpack)
        e += r6_safety_lint(prompt, is_ob)
        e += body_sos_lint(prompt)                 # ★body側SoS(倍率/年次年収ラダー混入)
        if sos:
            e += [f"factpack: {x}" for x in sos]
        report[role] = e
    total = sum(len(v) for v in report.values())
    return report, total
