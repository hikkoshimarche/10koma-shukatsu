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

EXCLUDED_SLUGS = {"mitsui-bussan"}  # 三井物産は対象外(安全)

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
        r = requests.post(url, headers=headers, json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
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
              "①台本バグ(文言・数字・誤り・原則違反) ②画像バグ(色/手/服装/レイアウト/文字焼き/絵の誤り) ③感想(好み・主観)。"
              "混在は①②両方に入れる。各項目に対象コマ番号(分かれば)を付す。JSONのみ出力。")


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


def fix_script_koma(slug: str, koma_num: int, instruction: str, rules: str) -> dict:
    """該当コマの台詞/overlayをClaudeで修正し、SQLを書き換える。(変更前/後と backup path)。

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

    backup = backup_file(parsed["path"], f"{slug}_koma{koma_num}")
    new_dialogue = "\n".join(after["script"])
    new_raw = _replace_panel_fields(parsed["raw"], slug, koma_num, after, new_dialogue)
    parsed["path"].write_text(new_raw, encoding="utf-8")
    append_diff_log({"slug": slug, "koma": koma_num, "kind": "script_fix",
                     "before": before, "after": after, "backup": str(backup),
                     "note": new.get("note", instruction[:80])})
    return {"changed": True, "before": before, "after": after, "backup": backup, "note": new.get("note", "")}


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
