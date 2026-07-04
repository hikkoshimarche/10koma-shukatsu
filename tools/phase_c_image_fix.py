#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase_c_image_fix.py — Phase C 画像FB自動修正エンジン (既存ツール再利用)。

インターンの画像FBを「拾う→直す指示に翻訳→再生成→ハードQAゲート→本番反映→記録」まで
人手ゼロで回す。ただし上限・QAゲート・一般化canary・可逆・全件ログ・エスカレ退避を必須。

既存再利用:
  - 再生成: tokyari generate_images.py --company X --koma N (内部7観点 vision QA)
  - デプロイ部品: fix_and_deploy.py の copy/commit/push/jsDelivr/D1update/verify 関数
  - 一般化canary/D1: deploy_salary.py (canary_snapshot/diff, d1_query, backup_d1)
  - 翻訳/トリアージ: phase_c_lib._anthropic / triage_fb
新規はオーケストレーション(翻訳・ガード・ハードゲート・ログ)のみ。新パイプラインは作らない。

安全:
  - キルフラグ AUTO_IMAGE_FIX_ENABLED=1 の時のみライブ稼働 (テキスト修正と独立)。既定OFF。
  - 予算: 1日 <$IMG_FIX_DAY_COST_MAX, 1時間 <IMG_FIX_HOUR_KOMA_MAX コマ。
  - コマ別: 同一コマ自動修正 累計 <IMG_FIX_PER_KOMA_MAX。
  - showcase(三井/三菱): 既定=自動修正するがLINEに別行で強調。
  - ハードQAゲート: 新画像 overall_severity!=severe かつ char_match=ok。3回不可→反映せずエスカレ。
  - 実行前D1バックアップ→実行後 一般化canary(対象社以外 全hash不変)→可逆。
  - 上限超過/QA連続失敗→画像自動修正を自動一時停止(state.paused)+LINE。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOKYARI / "scripts"))

import phase_c_lib as L          # noqa: E402  (_anthropic, backup, diff log)
import deploy_salary as D        # noqa: E402  (canary, d1, backup_d1)

STATE_FILE = REPO / "tools" / ".image_fix_state.json"
TOKYARI_PY = str(TOKYARI / ".venv" / "bin" / "python")
PAGES_BASE = "https://10koma-shukatsu.pages.dev"

# 7観点ルーブリック (vision_qa と対応): これらに該当する単一コマの画像問題のみ自動対象
RUBRIC = (
    "char_match(2名の顔/髪/服装が設定画と一致) / text_leak(画像内への文字焼き込み) / "
    "layout(構図・メタテキスト混入) / brand_scale(ブランド物の縮尺・配置) / "
    "retail_fixtures(店舗什器の日本実態) / physical_plausibility(遠近・物理整合) / "
    "props_and_hands(小道具・手指の破綻)")

QA_MAX = 3

# ============================================================================
# 決定的ルーブリック分類 (パイロットで判明: translate_image_fb がメタ枠/白帯/横線/縮尺/複合を
#   「7観点外」としてescalateし画像再生成キューに滞留させていた=画像FBが自走で流れない根治)。
#   下記の型に該当する画像FBは LLM判断を待たず auto(画像再生成経路)へ確定させ、
#   再生成指示に char-ref厳守＋背景フック保持＋コラージュ/文字焼き込み禁止 を必ず注入する。
# ============================================================================
# 全型共通で再生成指示に注入する制約 (パイロットfanuc1/komatsu6の背景すり替え・daikin2のchar逸脱の教訓)。
# ※プロンプトlint(prompt_lints)が .jpg 等のファイル名/メタ参照を弾くため、設定画のファイル名は書かない
#   (char-ref自体は generate_images が chars_reference を常時適用。ここでは見た目のみ規定)。
CHAR_REF_CONSTRAINT = (
    "【キャラ一貫性を厳守】ナナ=淡い青のカーディガン、ハルキ=ダークグリーンのシャツ＋ジャケット、"
    "2名の顔立ちをキャラ設定と同一に保つ。"
    "【背景フック保持】会社を象徴する固有の視覚フック(建物/製品/機械等)はbefore同等の形状・色で保持し、"
    "別物に描き直さない。コラージュ禁止・パネル番号/セリフの文字焼き込み禁止(文字はデータ層)。")

# 型ごとの再生成指示テンプレート
IMG_FIX_TEMPLATES = {
    "meta_frame": "画像内に紛れ込んだ四角い空白枠/メタ枠/網掛け領域を除去し、その範囲も本来の情景として自然に描き直す(枠内も背景で埋める)。",
    "white_band": "画像上部/端の白い空白帯・余白を除去し、画面全体を情景で満たす(必要ならズーム/再構図。主要被写体は切らない)。",
    "hline":      "画像を横切る不自然な線/継ぎ目/分断を除去し、空・建物・背景が上下で自然に連続するよう描き直す。",
    "scale":      "人物(ナナ・ハルキ)の大きさを背景に対し自然な比率へ是正(人物は前景・画面高さ約1/3以下目安)。ただし背景の固有フックは形状保持し別物に描き直さない。",
    "hands":      "手指・腕の破綻(本数超過/欠損/不自然な接続)を解消し、肩・肘・手首が自然につながる正しい人体にする。",
    "accuracy":   "指摘の製品/什器/機械の形状を実物に近い正しい見た目へ是正する(出典なき誇張はしない)。",
}

# プライマリ5型(task指定): メタ枠/白帯/横線/縮尺 (+複合=これらや下記auxが2つ以上)
_PRIMARY_PATTERNS = [
    # メタ枠/空白ボックス: 四角/枠/網掛け/ボックス。「白いボックス」「空白のボックス」も枠扱い。
    ("meta_frame", re.compile(r"四角[くいで]?.{0,8}(囲|枠|空白|網掛け|ボックス)|網掛け|メタ枠|囲われた空白|白い?ボックス|空白.{0,3}ボックス")),
    ("hline",      re.compile(r"横線|分断|継ぎ目|(空|建物|背景).{0,8}(分断|途切|裂)")),
    ("scale",      re.compile(r"縮尺|遠近|サイズ比|(サイズ|大きさ|比率).{0,6}(合|不自然|比|調整)|大きすぎ|小さすぎ|巨大")),
    # 白帯/クロップ: 「白い〜」に加え、端/上部の"空白"(枠なし)や余白も拾う。※枠付きは meta_frame が優先(下で調停)。
    ("white_band", re.compile(r"白い.{0,6}(空白|部分|帯|スペース)|白帯|余白|クロップ|(上部|下部|上|端|画像上|画像上部|画像下部).{0,8}(の)?空白|空白.{0,6}(削除|消|残らない|見えない)")),
]
# aux(複合検出・単独でも画像再生成で直る既存7観点系): 手指破綻 / 製品什器の形状相違
_AUX_PATTERNS = [
    ("hands",    re.compile(r"(手|指|腕|足).{0,8}(破綻|不自然|欠け|[0-9０-９]本|複数|多い|削除|つながり)")),
    ("accuracy", re.compile(r"(製品|什器|空調|機器|建機|形状|見た目).{0,12}(実物|実際|異な|近い|正しく|相違|確認)")),
]
_TYPE_ORDER = ["meta_frame", "white_band", "hline", "scale", "hands", "accuracy"]


def classify_image_bug_cats(detail: str) -> list[str]:
    """画像FB本文 → 該当する画像バグ型のリスト(distinct・優先順)。空=未知型(→LLMへ)。

    2つ以上該当したら呼び出し側で 'compound' 扱い。オーバーレイ文字FBはここに来る前に
    L.is_overlay_text_fb で台本経路へ分岐する(translate_image_fb 冒頭で処理)。
    """
    d = str(detail or "")
    hit = set()
    for name, pat in _PRIMARY_PATTERNS + _AUX_PATTERNS:
        if pat.search(d):
            hit.add(name)
    # 調停: 枠付きの空白は meta_frame が優先(同じ空白を white_band と二重計上して誤compoundにしない)。
    if "meta_frame" in hit and "white_band" in hit:
        hit.discard("white_band")
    return [t for t in _TYPE_ORDER if t in hit]


def build_regen_instruction(detail: str, cats: list[str]) -> str:
    """該当型テンプレートを連結し、共通のchar-ref/背景/禁止制約を必ず注入した再生成指示を作る。"""
    body = " ".join(IMG_FIX_TEMPLATES[c] for c in cats if c in IMG_FIX_TEMPLATES)
    return f"【画像再生成指示】{body} {CHAR_REF_CONSTRAINT}\n(元FB: {str(detail)[:80]})"


# ---------- フラグ/設定 ----------
def _env(k, default):
    v = os.environ.get(k)
    return v if v not in (None, "") else default


def cfg():
    return {
        "enabled": _env("AUTO_IMAGE_FIX_ENABLED", "0") == "1",
        "day_cost_max": float(_env("IMG_FIX_DAY_COST_MAX", "5.0")),
        "hour_koma_max": int(_env("IMG_FIX_HOUR_KOMA_MAX", "10")),
        "per_koma_max": int(_env("IMG_FIX_PER_KOMA_MAX", "2")),
        "showcase": set(s.strip() for s in _env("IMG_FIX_SHOWCASE_SLUGS", "").split(",") if s.strip()),
        "showcase_autofix": _env("IMG_FIX_SHOWCASE_AUTOFIX", "1") == "1",
    }


# ---------- state (予算/回数/一時停止) ----------
def load_state():
    today = time.strftime("%Y-%m-%d")
    st = {"day": today, "day_cost": 0.0, "hour_events": [], "per_koma": {},
          "paused": False, "pause_reason": "", "consecutive_qa_fail": 0}
    if STATE_FILE.exists():
        try:
            st.update(json.load(open(STATE_FILE, encoding="utf-8")))
        except Exception:
            pass
    if st.get("day") != today:                       # 日付替わりで日次リセット
        st.update({"day": today, "day_cost": 0.0, "hour_events": []})
    now = time.time()
    st["hour_events"] = [t for t in st.get("hour_events", []) if now - t < 3600]
    return st


def save_state(st):
    json.dump(st, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ---------- ガード ----------
def guard(slug, koma, st, c):
    """(allowed, reason, showcase) — クレジットを使う前の関所。"""
    showcase = slug in c["showcase"]
    if not c["enabled"]:
        return False, "AUTO_IMAGE_FIX_ENABLED=0 (フラグOFF)", showcase
    if st.get("paused"):
        return False, f"一時停止中: {st.get('pause_reason')}", showcase
    if st["day_cost"] >= c["day_cost_max"]:
        return False, f"日次予算超過 ${st['day_cost']:.2f}>=${c['day_cost_max']}", showcase
    if len(st["hour_events"]) >= c["hour_koma_max"]:
        return False, f"時間レート超過 {len(st['hour_events'])}>={c['hour_koma_max']}コマ/h", showcase
    key = f"{slug}#{koma}"
    if st["per_koma"].get(key, 0) >= c["per_koma_max"]:
        return False, f"コマ別上限 {key} {st['per_koma'][key]}>={c['per_koma_max']}回", showcase
    if showcase and not c["showcase_autofix"]:
        return False, "showcase自動修正OFF設定", showcase
    return True, "ok", showcase


# ---------- 翻訳 (FB→範囲限定の再生成指示 or escalate) ----------
TRANSLATE_SYS = (
    "あなたはトーキャリ10コマ画像の修正ディレクター。インターンの画像FBを、"
    "『その1コマだけ』を直す範囲限定の画像再生成指示に翻訳する。台本(セリフ/構図/コマ割り)は作り直さない。"
    "対象が単一コマ・具体的・再生成で直る画像問題(7観点系: 手指/文字混入/服装色ドリフト/什器/物理整合/ブランド縮尺/キャラ一致)なら action=auto。"
    "曖昧/複数コマ/台本・構図レベル/好み・主観/自信を持って具体化できない場合は action=escalate。"
    "JSONのみ出力。")


def translate_image_fb(company, slug, koma, detail, scenario_excerpt=""):
    """FB→{'action':'auto'|'escalate','instruction':str,'reason':str,('type','cats','route')}。

    優先順:
      0) オーバーレイ文字(sub_copy/main_copy)FB → route=script(画像再生成対象外・台本D1テキスト経路へ)。
      1) 決定的ルーブリック分類(メタ枠/白帯/横線/縮尺/複合 + 手指/製品形状) → escalateせず auto。
         再生成指示に char-ref厳守＋背景フック保持＋コラージュ/文字焼き込み禁止 を必ず注入。
      2) 未知型のみ 従来のLLM翻訳(真に曖昧/主観はescalate)。
    """
    # 0) 三菱型の誤分類再発防止: 画像内テキスト=オーバーレイはGemini再生成でなくD1テキスト修正。
    if L.is_overlay_text_fb(detail):
        return {"action": "escalate", "instruction": "", "route": "script",
                "reason": "overlay文字(main/sub_copy)=台本D1テキスト経路へ(画像再生成対象外)"}

    # 1) 決定的ルーブリック(5型)。該当すれば LLMを待たず auto 確定。
    cats = classify_image_bug_cats(detail)
    if cats:
        btype = "compound" if len(cats) >= 2 else cats[0]
        return {"action": "auto", "instruction": build_regen_instruction(detail, cats),
                "reason": f"ルーブリック型={btype}", "type": btype, "cats": cats}

    # 2) 未知型のみ 従来LLM翻訳(曖昧はescalate)。
    prompt = (
        f"会社: {company} (slug={slug})\n対象コマ: {koma}\n"
        f"画像FB: {detail}\n\n7観点ルーブリック: {RUBRIC}\n"
        f"{('該当コマscene/brand: '+scenario_excerpt) if scenario_excerpt else ''}\n\n"
        '次のJSONで出力: {"action":"auto"|"escalate",'
        '"instruction":"範囲限定の再生成指示(autoのみ・1〜3行・画像のどこをどう直すか具体的に)",'
        '"reason":"判断理由(短く)"}')
    txt = L._anthropic(prompt, system=TRANSLATE_SYS, max_tokens=800)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return {"action": "escalate", "instruction": "", "reason": "翻訳パース失敗", "_raw": txt[:200]}
    try:
        out = json.loads(m.group(0))
        if out.get("action") not in ("auto", "escalate"):
            out["action"] = "escalate"
        if out["action"] == "auto" and not out.get("instruction"):
            out = {"action": "escalate", "instruction": "", "reason": "指示空 → エスカレ"}
        # LLM経路のautoにも共通制約(char-ref/背景/禁止)を注入(型経路と同基準に揃える)。
        if out.get("action") == "auto" and out.get("instruction") and CHAR_REF_CONSTRAINT not in out["instruction"]:
            out["instruction"] = f"{out['instruction']} {CHAR_REF_CONSTRAINT}"
            out.setdefault("type", "llm")
        return out
    except Exception:
        return {"action": "escalate", "instruction": "", "reason": "翻訳JSON不正", "_raw": txt[:200]}


def _scenario_excerpt(tslug, koma):
    p = TOKYARI / "output" / tslug / "scenario.json"
    if not p.exists():
        return ""
    try:
        sc = json.load(open(p, encoding="utf-8"))
        k = next((x for x in sc.get("koma", []) if x.get("koma_number") == koma), None)
        if not k:
            return ""
        return json.dumps({"scene": k.get("scene"), "brand_object": k.get("brand_object")},
                          ensure_ascii=False)[:400]
    except Exception:
        return ""


# ---------- ハードQAゲート ----------
def hard_gate(tslug, koma):
    """直近 qa_report の該当コマ: (pass, severity, char_match, cost)。
    pass = overall_severity!=severe かつ char_match.verdict=='ok'。"""
    qp = TOKYARI / "output" / tslug / "qa_report.json"
    if not qp.exists():
        return False, "no_report", "?", 0.0
    rep = json.load(open(qp, encoding="utf-8"))
    cost = float(rep.get("total_cost_usd", 0.0) or 0.0)
    res = next((x for x in rep.get("results", []) if x.get("koma_number") == koma), None)
    if not res:
        return False, "no_koma", "?", cost
    fq = res.get("final_qa") or {}
    sev = fq.get("overall_severity", "severe")
    cm = (fq.get("char_match") or {}).get("verdict", "concern")
    return (sev != "severe" and cm == "ok"), sev, cm, cost


# ---------- LINE / ログ ----------
def push_line(text):
    url = _env("SHEET_WEBAPP_URL", "").strip()
    token = _env("SHEET_API_TOKEN", "").strip()
    if not url:
        print(f"[LINE未設定]\n{text}"); return
    try:
        import requests
        requests.get(url, params={"mode": "pushline", "token": token, "text": text}, timeout=30)
    except Exception as e:
        print(f"[LINE送信失敗:{e}]\n{text}")


def gas(params):
    url = _env("SHEET_WEBAPP_URL", "").strip()
    params = {**params, "token": _env("SHEET_API_TOKEN", "").strip()}
    try:
        import requests
        return requests.get(url, params=params, timeout=30).json()
    except Exception as e:
        return {"error": str(e)}


def record_knowledge(rule, note, scope="system"):
    """横断ルールを📚共通の修正案(知見集)に蓄積。"""
    gas({"mode": "addcommonfix", "rule": rule, "scope": scope, "note": note})


# ---------- 1件処理 ----------
def run_one(company, slug, koma, detail, dry, st, c):
    """画像FB1件を処理。dry: 翻訳+ガード判定+計画ログのみ(生成しない)。
    返り値 rec(辞書)。state(st)はライブ時のみ副作用更新。"""
    import company_master as cm
    tslug = cm.TOKYARI_SLUG_OVERRIDES_REV.get(slug, slug) if hasattr(cm, "TOKYARI_SLUG_OVERRIDES_REV") \
        else {v: k for k, v in cm.TOKYARI_SLUG_OVERRIDES.items()}.get(slug, slug)
    rec = {"company": company, "slug": slug, "tslug": tslug, "koma": koma,
           "detail": detail, "action": None, "instruction": "", "reason": "",
           "guard": None, "showcase": False, "deployed": False, "escalate": None,
           "qa": None, "cost": 0.0, "commit": None}

    # 1) 翻訳 (auto/escalate) — Claudeのみ(クレジット安価)
    excerpt = _scenario_excerpt(tslug, koma)
    tr = translate_image_fb(company, slug, koma, detail, excerpt)
    rec["action"] = tr["action"]
    rec["instruction"] = tr.get("instruction", "")
    rec["reason"] = tr.get("reason", "")
    if tr["action"] == "escalate":
        rec["escalate"] = f"翻訳でescalate: {tr.get('reason')}"
        return rec

    # 2) ガード (クレジット使用前)
    allowed, reason, showcase = guard(slug, koma, st, c)
    rec["guard"] = reason
    rec["showcase"] = showcase
    if not allowed:
        # フラグOFF以外の関所(予算/レート/コマ上限)はエスカレ。OFFはdry扱い。
        if "OFF" not in reason:
            rec["escalate"] = f"ガード不可: {reason}"
        return rec

    # 3) DRY: ここで生成せず計画だけ返す (クレジット不使用)
    if dry:
        rec["note"] = "DRY: 翻訳・ガード通過。ライブなら再生成→ハードQA→canary→反映へ"
        return rec

    # ===== ライブ実行 (フラグON時のみ到達) =====
    import fix_and_deploy as FAD
    # slug_map拡張 (deploy slug→自身、tokyari override考慮)
    FAD.SLUG_MAP.setdefault(tslug, slug)

    scen = TOKYARI / "output" / tslug / "scenario.json"
    if not scen.exists():
        rec["escalate"] = f"scenario.json無し({tslug}) → 画像修正不可・要台本整備"
        return rec

    # 3-pre) D1バックアップ + canary before
    try:
        D.backup_d1(slug)
    except Exception as e:
        rec["escalate"] = f"D1backup失敗: {e}"; return rec
    canary_before = D.canary_snapshot({slug})

    # 4) fix_instructions追記 → 再生成 → ハードQAゲート (最大3)
    FAD.add_fix_instructions_to_scenario(tslug, koma, [rec["instruction"]])
    gate_ok = False
    for attempt in range(1, QA_MAX + 1):
        FAD.regenerate_panel(tslug, koma)
        gate_ok, sev, cm_v, cost = hard_gate(tslug, koma)
        rec["qa"] = {"attempt": attempt, "severity": sev, "char_match": cm_v}
        rec["cost"] = cost
        st["day_cost"] += cost
        st["hour_events"].append(time.time())
        if gate_ok:
            break
    st["per_koma"][f"{slug}#{koma}"] = st["per_koma"].get(f"{slug}#{koma}", 0) + 1

    if not gate_ok:
        st["consecutive_qa_fail"] = st.get("consecutive_qa_fail", 0) + 1
        rec["escalate"] = f"ハードQA{QA_MAX}回不可(sev={rec['qa']['severity']},char={rec['qa']['char_match']})→反映せず"
        # QA連続失敗で自動一時停止
        if st["consecutive_qa_fail"] >= 3:
            st["paused"] = True; st["pause_reason"] = "QA連続失敗×3"
            push_line("🛑【画像自動修正 一時停止】QA連続失敗×3。AUTO_IMAGE_FIX手動再開要。")
        return rec
    st["consecutive_qa_fail"] = 0

    # 5) デプロイ (copy→push→jsDelivr→D1update) — fix_and_deploy部品再利用
    panel = FAD.copy_panel_to_deploy(tslug, koma)
    sha = FAD.git_commit_push(panel, f"fix(image:{slug}): koma{koma:02d} 自動修正(FB)")
    rec["commit"] = sha
    FAD.wait_jsdelivr(slug, koma, sha)
    FAD.update_d1_panel(slug, koma, sha)

    # 6) 一般化canary (対象社以外 全hash不変) + 検証
    canary_after = D.canary_snapshot({slug})
    drift = D.canary_diff(canary_before, canary_after)
    if drift:
        rec["escalate"] = f"🛑canary異常: 対象外変化 {drift} → 要revert(backup有)"
        push_line(f"🛑【画像自動修正 canary異常】{slug} koma{koma}: 対象外{drift}変化。反映停止・要調査。")
        return rec
    api_ok = FAD.verify_api_url_updated(slug, koma, sha)
    rec["deployed"] = bool(api_ok)

    # 7) ログ/書き戻し
    if api_ok:
        gas({"mode": "setreflected", "company": company})
        L.append_diff_log({"kind": "image_fix", "slug": slug, "koma": koma,
                           "instruction": rec["instruction"], "qa": rec["qa"],
                           "cost": rec["cost"], "commit": sha, "showcase": showcase})
    else:
        rec["escalate"] = "API検証NG(URL未更新)"
    return rec


# ---------- 予算超過の事前チェック(バッチ先頭) ----------
def precheck_budget(st, c):
    if st["day_cost"] >= c["day_cost_max"]:
        return False, f"日次予算到達 ${st['day_cost']:.2f}"
    if len(st["hour_events"]) >= c["hour_koma_max"]:
        return False, f"時間レート到達 {len(st['hour_events'])}/h"
    return True, "ok"


# ---------- selftest (ネットワーク非依存: 決定的分類のみ検証) ----------
def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + name)
        ok = ok and cond

    def has_constraints(instr):
        return ("キャラ一貫性を厳守" in instr and "背景フック保持" in instr
                and "コラージュ禁止" in instr and "文字焼き込み禁止" in instr
                and ".jpg" not in instr)  # プロンプトlint(.jpg)を踏まないこと

    print("[selftest] 5型が escalateせず auto・制約注入される (パイロットで詰まった型)")
    CASES = [
        ("meta_frame", "【1枚目】画像上部にある四角く囲われた空白部分は不要。空白が残らないように修正する。"),
        ("meta_frame", "【1コマ目】画像左上の不自然な白いボックスを削除。"),                # 白いボックス(枠なし語)
        ("white_band", "【6枚目】画像上部に白い空白部分がある。画像を拡大または再生成し、空白を削除する。"),
        ("white_band", "【3枚目】画像上部に空白があるため、画像を拡大または再生成し、空白部分を削除する。"),  # 枠なし"上部の空白"
        ("hline",      "【1枚目】写真上部に不自然な黒い横線が入り、空と建物が分断されている。線を削除する。"),
        ("scale",      "【1枚目】人物・建物・山の遠近感とサイズ比が合っていない。自然な構図に調整する。"),
    ]
    for want, detail in CASES:
        r = translate_image_fb("(t)", "(t)", 1, detail)
        chk(f"{want}: action=auto", r.get("action") == "auto")
        chk(f"{want}: type={want}", r.get("type") == want)
        chk(f"{want}: char-ref/背景/禁止 制約が注入", has_constraints(r.get("instruction", "")))

    print("[selftest] 複合(手指+製品形状)が compound で auto (パイロット daikin/koma2)")
    r = translate_image_fb("(t)", "(t)", 2,
        "画像内のハルキの右腕が2本ある。不要な腕を削除。業務用空調の描写が実物と異なるため実際の製品に近い形状へ。")
    chk("daikin2型: action=auto", r.get("action") == "auto")
    chk("daikin2型: type=compound", r.get("type") == "compound")
    chk("daikin2型: cats=手指+製品形状", set(r.get("cats", [])) == {"hands", "accuracy"})
    chk("daikin2型: 制約注入", has_constraints(r.get("instruction", "")))

    print("[selftest] オーバーレイ文字FBは画像でなく台本(script)経路へ分岐 (三菱型誤分類防止)")
    r = translate_image_fb("(t)", "(t)", 2, "画像内テキスト「今 売上約19億円」の「今」を削除する")
    chk("overlay: route=script", r.get("route") == "script")
    chk("overlay: 画像autoにしない", r.get("action") != "auto")

    print("[selftest] 真に主観/曖昧なFBは型に該当せず(→LLM/escalate据置)")
    for detail in ["右側の画像が簡素で品質感を下げる。より質の高い描写に修正。",
                   "ナナが手前に出すぎており構図が不自然。距離感を調整。"]:
        chk(f"未知型(cats空): {detail[:16]}…", classify_image_bug_cats(detail) == [])

    print("\n=== selftest: " + ("ALL PASS ✅" if ok else "FAIL ❌") + " ===")
    return 0 if ok else 1


# ---------- CLI (dry-run検証) ----------
def _load_env():
    env = REPO / "tools" / ".env.phase_c"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main(argv=None):
    import argparse
    if argv is None and "--selftest" in sys.argv:
        return _selftest()
    _load_env()
    ap = argparse.ArgumentParser(description="画像FB自動修正 (既定dry-run・クレジット不使用)")
    ap.add_argument("--selftest", action="store_true", help="決定的ルーブリック分類の関所テスト")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--live", dest="dry_run", action="store_false",
                    help="ライブ実行 (AUTO_IMAGE_FIX_ENABLED=1 必須・wave/孤児/OK後)")
    ap.add_argument("--companies", help="会社名カンマ区切りで絞る(検証用)")
    ap.add_argument("--limit", type=int, default=2, help="処理FB件数上限(dry検証は1〜2)")
    ap.add_argument("--manual", help="手動FB 'slug|koma|detail' で1件投入(スプシ未使用)")
    args = ap.parse_args(argv)

    c = cfg()
    st = load_state()
    print("=" * 64)
    print(f"=== 画像FB自動修正 [{'DRY-RUN' if args.dry_run else 'LIVE'}] ===")
    print(f"フラグ AUTO_IMAGE_FIX_ENABLED={'ON' if c['enabled'] else 'OFF'} / "
          f"予算 day<${c['day_cost_max']} hour<{c['hour_koma_max']}コマ / コマ別<{c['per_koma_max']}回")
    print(f"state: day_cost=${st['day_cost']:.2f} hour={len(st['hour_events'])}件 "
          f"paused={st['paused']} showcase={sorted(c['showcase'])}")
    print("=" * 64)

    # FB収集
    img_fbs = []  # (company, slug, koma, detail)
    if args.manual:
        slug, koma, detail = args.manual.split("|", 2)
        img_fbs.append(("(manual)", slug, int(koma), detail))
    else:
        import phase_c_autoloop as A
        items = [it for it in A.fetch_attention() if it.get("content") == "10コマ"]
        if args.companies:
            want = {x.strip() for x in args.companies.split(",")}
            items = [it for it in items if it.get("company") in want]
        for it in items:
            company = it.get("company", "")
            slug = A.resolve_slug(company)
            if not slug:
                continue
            tri = L.triage_fb(company, it.get("fb", ""))
            for b in tri.get("image_bugs", []):
                if b.get("koma"):
                    img_fbs.append((company, slug, b["koma"], b.get("detail", "")))
        img_fbs = img_fbs[:args.limit]

    if not img_fbs:
        print("画像FBなし(対象0件)。"); return 0

    results = []
    for company, slug, koma, detail in img_fbs:
        print(f"\n--- {company} ({slug}) koma{koma} ---")
        print(f"  画像FB: {detail[:80]}")
        rec = run_one(company, slug, koma, detail, args.dry_run, st, c)
        results.append(rec)
        print(f"  翻訳判定: action={rec['action']} reason={rec['reason'][:60]}")
        if rec["instruction"]:
            print(f"  再生成指示: {rec['instruction'][:120]}")
        print(f"  ガード: {rec['guard']} showcase={rec['showcase']}")
        if rec["escalate"]:
            print(f"  ⚠ エスカレ: {rec['escalate']}")
        if not args.dry_run:
            print(f"  QA={rec['qa']} cost=${rec['cost']:.3f} deployed={rec['deployed']} commit={rec['commit']}")
        else:
            print(f"  → {rec.get('note','(escalate=生成せず)')}")

    if not args.dry_run:
        save_state(st)

    # サマリ
    auto = [r for r in results if r["action"] == "auto" and not r["escalate"]]
    esc = [r for r in results if r["escalate"]]
    show = [r for r in results if r["showcase"]]
    print("\n" + "=" * 64)
    print(f"集計: {len(results)}件 / 自動経路 {len(auto)} / エスカレ {len(esc)} / showcase {len(show)}")
    if show:
        print("  ★showcase(別行強調):", ", ".join(f"{r['slug']}#{r['koma']}" for r in show))
    out = REPO / "tools" / "_image_fix_last.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"結果: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
