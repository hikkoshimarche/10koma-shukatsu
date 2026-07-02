#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase_c_lib.py — Phase C 自動ループの中核ライブラリ(GAS非依存)。

提供:
  - parse_migration_sql / write_migration_sql : api/migration_v4_<slug>.sql ⇄ 構造化
  - sql_to_scenario : lint(scenario_lints_v5_ext)に渡せる {meta,koma} へ変換
  - lint_company    : 台本(SQL)をv5_extでlint → errors/warnings
  - triage_fb       : FBを ①台本バグ ②画像バグ ③感想 に仕分け (Claude)
  - fix_script_koma : 該当コマの台本(dialogue/script_json/overlay)をClaudeで修正
  - backup_file / append_diff_log : 可逆性(バックアップ+差分ログ)

本モジュールは副作用の少ない純粋ロジックに寄せ、デプロイ/GAS I/Oは呼び出し側(phase_c_autoloop.py)に置く。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
API_DIR = REPO / "api"
BACKUP_DIR = REPO / ".backups"
DIFF_LOG = BACKUP_DIR / "phase_c_diff.log"

EXCLUDED_SLUGS = set()  # 除外なし。三井物産も一般化canary下で他社同様のライブ自動対象(2026-06-22解除)

# --- FB懸念の分類 (要判断オスカー vs 要調査Claude) --------------------------
# 方針(2026-06-22): 「要判断(オスカー)」はオスカーの好み/トーン/方向性"判断"だけに限定。
# 「ちゃんと調べて」「根拠は」等の事実確認・調査系はオスカーに戻さず Claude/CC が裏取りして
# 反映まで完結させる(取れなければ据置)。LINEの要判断件数は preference のみ数える。
# 注: 「印象/イメージ」は明確な修正指示にも頻出(例『食品専業の印象→一事業として書いて』)し
# 誤escalateを招くため除外。真に主観的・好みの語のみに限定。
_PREF_PAT = re.compile(
    r"(好み|主観|センス|テイスト|可愛|かわい|かっこ|ダサ|おしゃれ|オシャレ|雰囲気|トーン|"
    r"方向性|テンション|温度感|世界観|刺さ|エモ|なんか変|なんかいや|"
    r"どう思|好き(?!感)|嫌い|の方が好み|の方が好き)", re.I)
_FACT_PAT = re.compile(
    r"(出典|根拠|ソース|エビデンス|裏付け|本当に|事実|データ|統計|調べ|確認して|"
    r"正しい|合って|間違って|何年|いつから|誰が|どこ(の|から)|数字|金額|割合|倍率|"
    r"source|fact|verify|本当\?|ほんと\?)", re.I)


def classify_concern(text: str) -> str | None:
    """FB文を 'preference'(=要判断オスカー) | 'factcheck'(=要調査Claude) | None に分類。

    事実確認が絡む場合は preference より優先(オスカーに戻さず裏取りで完結させるため)。
    """
    t = str(text or "")
    if _FACT_PAT.search(t):
        return "factcheck"
    if _PREF_PAT.search(t):
        return "preference"
    return None


def is_oscar_judgment(text: str) -> bool:
    """真にオスカー判断(好み/トーン/方向性)のみ True。事実確認系は False(=Claude側で処理)。"""
    return classify_concern(text) == "preference"

# --- migration SQL パース --------------------------------------------------
PANEL_RE = re.compile(
    r"INSERT OR REPLACE INTO company_panels\s*\([^)]*\)\s*VALUES\s*\((.*?)\);",
    re.S,
)


def _split_sql_values(blob: str) -> list[str]:
    """SQL VALUES の中身を、'' エスケープと括弧を尊重してトップレベルのカンマで分割。"""
    out, cur, i, n = [], [], 0, len(blob)
    in_str = False
    depth = 0
    while i < n:
        ch = blob[i]
        if in_str:
            if ch == "'":
                if i + 1 < n and blob[i + 1] == "'":
                    cur.append("''"); i += 2; continue
                in_str = False; cur.append(ch); i += 1; continue
            cur.append(ch); i += 1; continue
        if ch == "'":
            in_str = True; cur.append(ch); i += 1; continue
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip()); cur = []; i += 1; continue
        cur.append(ch); i += 1
    if cur:
        out.append("".join(cur).strip())
    return out


def _unq(v: str):
    v = v.strip()
    if v == "NULL":
        return None
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1].replace("''", "'")
    return v


# company_panels の列順(migration_v4 準拠)
PANEL_COLS = ["company_id", "panel_num", "image_url", "character", "dialogue",
              "main_copy", "sub_copy", "source_url", "script_json", "visual_hook",
              "brand_object_json"]


def parse_migration_sql(slug: str) -> dict:
    """api/migration_v4_<slug>.sql → {'path','panels':[{col:val,...}x10],'raw'}"""
    p = API_DIR / f"migration_v4_{slug}.sql"
    raw = p.read_text(encoding="utf-8")
    panels = []
    for m in PANEL_RE.finditer(raw):
        vals = _split_sql_values(m.group(1))
        row = {col: _unq(vals[i]) if i < len(vals) else None for i, col in enumerate(PANEL_COLS)}
        if row.get("panel_num") is not None:
            row["panel_num"] = int(row["panel_num"])
        panels.append(row)
    panels.sort(key=lambda r: r.get("panel_num") or 0)
    return {"path": p, "panels": panels, "raw": raw}


def sql_to_scenario(parsed: dict) -> dict:
    """lint 用に {meta:{slug},koma:[{koma_number,script,overlay_text}]} へ。"""
    koma = []
    for row in parsed["panels"]:
        try:
            script = json.loads(row.get("script_json") or "[]")
        except Exception:
            script = [ln for ln in (row.get("dialogue") or "").split("\n") if ln.strip()]
        koma.append({
            "koma_number": row.get("panel_num"),
            "script": script,
            "overlay_text": {"main_copy": row.get("main_copy") or "",
                             "sub": row.get("sub_copy") or ""},
        })
    return {"meta": {"slug": parsed["panels"][0]["company_id"] if parsed["panels"] else "?"},
            "koma": koma}


def lint_company(slug: str):
    """台本(SQL)を scenario_lints_v5_ext でlint。(errors,warnings,findings)。"""
    import sys
    sys.path.insert(0, str(REPO / "tools"))
    import scenario_lints_v5_ext as v5
    scen = sql_to_scenario(parse_migration_sql(slug))
    r = v5.run_ext_lints(scen, slug)
    return r["errors"], r["warnings"], r["findings"]


# --- 可逆性: backup + diff log --------------------------------------------
def backup_file(path: Path, tag: str) -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"{ts}_{tag}_{path.name}.bak"
    shutil.copy2(path, dst)
    return dst


def append_diff_log(entry: dict) -> None:
    BACKUP_DIR.mkdir(exist_ok=True)
    entry = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), **entry}
    with open(DIFF_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# --- Claude 呼び出し -------------------------------------------------------
def _anthropic(prompt: str, system: str = "", model: str = "claude-sonnet-4-6", max_tokens: int = 2000) -> str:
    key = re.sub(r"\s", "", os.environ["ANTHROPIC_API_KEY"])
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    # macOS(Python3.14)の素urllibはCA不足でSSL失敗するため requests/certifi を優先
    try:
        import requests
        last = None
        for attempt in range(4):  # ネットワーク瞬断/過負荷に指数バックオフ
            try:
                r = requests.post(url, headers=headers, json=body, timeout=120)
                if r.status_code in (429, 500, 502, 503, 529):
                    raise requests.exceptions.RequestException(f"retryable {r.status_code}")
                r.raise_for_status()
                data = r.json()
                last = None
                break
            except requests.exceptions.RequestException as ex:
                last = ex
                time.sleep(2 ** attempt)
        if last is not None:
            raise last
    except ImportError:
        import ssl
        ctx = None
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            data = json.loads(resp.read().decode())
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


TRIAGE_SYS = ("あなたはトーキャリ10コマのFBトリアージ担当。ユーザーFBを3カテゴリに仕分ける。"
              "①台本バグ(文言・数字・誤り・原則違反・**具体的な書き換え方向を含む指摘**) "
              "②画像バグ(色/手/服装/レイアウト/文字焼き/絵の誤り) ③感想(好み・主観のみ)。"
              "重要: 『〜のほうがいい』『言い回しが不自然』『分かりにくい』『リライトして』等、"
              "**直す方向が読み取れるものは必ず①台本バグに入れる**(③感想に入れない)。"
              "③感想は『action不能な純粋な好み・印象』だけに限定。混在は①②両方に入れる。"
              "各項目に対象コマ番号(分かれば)を付す。JSONのみ出力。")


def extract_koma(text: str):
    """FB文からコマ番号を抽出(コマN / N枚目 / 【Nコマ目】等)。無ければNone。"""
    t = str(text or "")
    for pat in (r"(?:コマ|こま|panel)\s*0*(\d+)", r"【\s*0*(\d+)\s*(?:コマ|枚)",
                r"0*(\d+)\s*(?:枚目|コマ目)"):
        m = re.search(pat, t)
        if m:
            return int(m.group(1))
    return None


# v3.6以降の10コマは、画像上の main_copy/sub_copy を **フロント側HTMLオーバーレイ** で描画する
# (PNGには文字を焼き込まない: public/company.html .panel-overlay)。よって「画像内テキスト/文字」を
# 直す系のFBは Gemini再生成ではなく D1 の main_copy/sub_copy(=台本テキスト)修正で直る。
# 描画バグ(手/指/腕/構図/色/服/空白/線 等)はここでは False にして従来どおり画像キューへ回す。
_OVERLAY_TEXT_PAT = re.compile(
    r"(テキスト|文字).{0,20}(削除|消して|消す|除|変更|修正|直|に変|加え|追加|統一|表記)"
    r"|画像内.{0,6}(テキスト|文字)"
    r"|オーバーレイ"
    r"|「[^」]{1,40}」.{0,8}(削除|消して|消す|変更|修正)")
_DRAW_BUG_PAT = re.compile(
    r"(手|指|腕|足|構図|レイアウト|色|服|ジャケット|上着|空白|余白|線|背景|描画|"
    r"縮尺|視線|位置|人物|大きさ|遠近|吹き出し|画面|スマホ|スマートフォン|耳|髪|顔|表情|"
    r"棚|コップ|瓶|ビール|再生成|拡大)")


def is_overlay_text_fb(detail: str) -> bool:
    """FBが『オーバーレイ文字(main_copy/sub_copy)の編集で直る』ものか。

    True  = 画像内テキスト/文字の削除・変更系 → 台本テキスト修正経路へ(画像再生成不要)。
    False = 手/構図/色 等の描画バグ、または非該当 → 従来の画像再生成キューへ。
    描画バグ語が含まれる場合は文字語があっても False(絵の修正が主目的とみなす)。
    """
    d = str(detail or "")
    if _DRAW_BUG_PAT.search(d):
        return False
    return bool(_OVERLAY_TEXT_PAT.search(d))


def fix_koma_text(slug: str, koma_num: int, instruction: str, rules: str, current: dict) -> dict:
    """D1ライブ基準でコマ台本を修正(ファイル非依存)。current={script,main_copy,sub_copy}。

    api/migration_v4_<slug>.sql の有無に依存せず、呼び出し側がD1から読んだ現行台本を渡す。
    戻り値: {changed, before, after:{script,main_copy,sub_copy,note}, note}。
    """
    cur_script = current.get("script") or []
    prompt = (f"【ルール】\n{rules}\n\n【会社】{slug} koマ{koma_num}\n"
              f"【現行script(JSON配列)】{json.dumps(cur_script, ensure_ascii=False)}\n"
              f"【現行main_copy】{current.get('main_copy')}\n【現行sub_copy】{current.get('sub_copy')}\n\n"
              f"【修正指示(FB由来)】{instruction}\n\n"
              "ルール厳守・最小限の修正。話者タグ([nana]/[haruki]/[OB先輩]等)は維持。"
              "生Markdown禁止/倍率数値禁止/出典なき数字禁止。修正不要なら現行のまま返す。"
              '出力はJSONのみ: {"script":[...], "main_copy":"...", "sub_copy":"...", "note":"何を直したか"}')
    txt = _anthropic(prompt, max_tokens=1500)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return {"changed": False, "note": "JSON抽出失敗", "before": current, "after": current}
    try:
        new = json.loads(m.group(0))
    except Exception as e:
        return {"changed": False, "note": f"JSON不正:{e}", "before": current, "after": current}
    after = {"script": new.get("script", cur_script),
             "main_copy": new.get("main_copy", current.get("main_copy")),
             "sub_copy": new.get("sub_copy", current.get("sub_copy")),
             "note": new.get("note", "")}
    changed = (after["script"] != cur_script
               or after["main_copy"] != current.get("main_copy")
               or after["sub_copy"] != current.get("sub_copy"))
    return {"changed": changed, "before": current, "after": after, "note": after["note"]}


def triage_fb(company: str, fb: str) -> dict:
    """FB → {'script_bugs':[{koma,detail}],'image_bugs':[{koma,detail}],'opinions':[str]}"""
    prompt = (f"会社: {company}\nFB:\n{fb}\n\n"
              '次のJSONで出力: {"script_bugs":[{"koma":int|null,"detail":str}],'
              '"image_bugs":[{"koma":int|null,"detail":str}],"opinions":[str]}')
    txt = _anthropic(prompt, system=TRIAGE_SYS, max_tokens=1500)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return {"script_bugs": [], "image_bugs": [], "opinions": [], "_raw": txt}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"script_bugs": [], "image_bugs": [], "opinions": [], "_raw": txt}


def fix_script_koma(slug: str, koma_num: int, instruction: str, rules: str, dry: bool = False) -> dict:
    """該当コマの台詞/overlayをClaudeで修正。dry=Trueなら書込まず提案のみ返す。

    戻り値: {'changed':bool,'before':{...},'after':{...},'backup':Path|None,'note':str}
    """
    parsed = parse_migration_sql(slug)
    target = next((r for r in parsed["panels"] if r["panel_num"] == koma_num), None)
    if target is None:
        return {"changed": False, "note": f"koma{koma_num}が無い"}
    try:
        script = json.loads(target.get("script_json") or "[]")
    except Exception:
        script = []
    before = {"script": script, "main_copy": target.get("main_copy"), "sub_copy": target.get("sub_copy")}
    prompt = (f"【ルール】\n{rules}\n\n【会社】{slug} koma{koma_num}\n"
              f"【現行script(JSON配列)】{json.dumps(script, ensure_ascii=False)}\n"
              f"【現行main_copy】{target.get('main_copy')}\n【現行sub_copy】{target.get('sub_copy')}\n\n"
              f"【修正指示(FB由来のバグ)】{instruction}\n\n"
              "ルールを厳守し最小限の修正。生Markdown禁止/倍率数値禁止/出典なき数字禁止。"
              '出力はJSONのみ: {"script":[...], "main_copy":"...", "sub_copy":"...", "note":"何を直したか"}')
    txt = _anthropic(prompt, max_tokens=1500)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return {"changed": False, "note": "Claude応答からJSON抽出失敗", "before": before}
    new = json.loads(m.group(0))
    after = {"script": new.get("script", script),
             "main_copy": new.get("main_copy", target.get("main_copy")),
             "sub_copy": new.get("sub_copy", target.get("sub_copy"))}
    if after == before:
        return {"changed": False, "note": "変更なし(反映済)", "before": before, "after": after}
    if dry:
        return {"changed": True, "before": before, "after": after, "backup": None,
                "note": new.get("note", ""), "dry": True}

    backup = backup_file(parsed["path"], f"{slug}_koma{koma_num}")
    new_dialogue = "\n".join(after["script"])
    new_raw = _replace_panel_fields(parsed["raw"], slug, koma_num, after, new_dialogue)
    parsed["path"].write_text(new_raw, encoding="utf-8")
    append_diff_log({"slug": slug, "koma": koma_num, "kind": "script_fix",
                     "before": before, "after": after, "backup": str(backup),
                     "note": new.get("note", instruction[:80])})
    return {"changed": True, "before": before, "after": after, "backup": backup, "note": new.get("note", "")}


def lint_with_overrides(slug: str, overrides: dict):
    """台本に koma別 override({koma:{'script','main_copy','sub_copy'}})を当てた状態でlint。

    overrides を反映した仮想 scenario を作って scenario_lints_v5_ext にかける(ファイルは触らない)。
    戻り値: (errors, warnings, findings)
    """
    import sys
    sys.path.insert(0, str(REPO / "tools"))
    import scenario_lints_v5_ext as v5
    parsed = parse_migration_sql(slug)
    scen = sql_to_scenario(parsed)
    for k in scen["koma"]:
        ov = overrides.get(k["koma_number"])
        if ov:
            if "script" in ov:
                k["script"] = ov["script"]
            k["overlay_text"] = {"main_copy": ov.get("main_copy", k["overlay_text"]["main_copy"]),
                                 "sub": ov.get("sub_copy", k["overlay_text"]["sub"])}
    r = v5.run_ext_lints(scen, slug)
    return r["errors"], r["warnings"], r["findings"]


def _sqlq(v) -> str:
    if v is None:
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def _replace_panel_fields(raw: str, slug: str, koma_num: int, after: dict, new_dialogue: str) -> str:
    """指定パネルのINSERT行で dialogue/main_copy/sub_copy/script_json を差し替える。"""
    def repl(m):
        seg = m.group(0)
        vals = _split_sql_values(m.group(1))
        if len(vals) < len(PANEL_COLS):
            return seg
        if int(_unq(vals[1])) != koma_num:
            return seg
        vals[4] = _sqlq(new_dialogue)                                   # dialogue
        vals[5] = _sqlq(after["main_copy"])                            # main_copy
        vals[6] = _sqlq(after["sub_copy"])                             # sub_copy
        vals[8] = _sqlq(json.dumps(after["script"], ensure_ascii=False))  # script_json
        head = seg[:seg.index("VALUES")]
        return f"{head}VALUES ({', '.join(vals)});"
    return PANEL_RE.sub(repl, raw)
