#!/usr/bin/env python3
# === VENDORED COPY (このrepoがversion管理側=正本) ===
# dev/run元: ~/oscar-ai/tokyari-pipeline/scripts/scenario_lints_v5_ext.py
# 依存: scenario_v4.json は tokyari-pipeline/output/<slug>/（このrepoには無い）
# selftest: tokyari-pipeline側で `python scripts/scenario_lints_v5_ext.py --selftest`
#   ここからは path指定: `python tools/scenario_lints_v5_ext.py <scenario_v4.jsonのpath>`
# 編集時は両コピーを必ず同期。
# -*- coding: utf-8 -*-
"""scenario_lints_v5_ext.py — 📚知見集の未機械化項目を加算式で機械化（既存lints非干渉）。
error=マージ不可 / warning=人間レビュー。CLI: <slug|path> | --selftest"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")
if not os.path.isdir(OUTPUT):
    _fb = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
    OUTPUT = _fb if os.path.isdir(_fb) else OUTPUT
PROTAGONISTS = {"nana", "haruki", "both"}
SHOSHA9 = ["mitsubishi-corp","itochu-shoji","sumitomo-corp","marubeni",
           "kanematsu","shinkokusyoji","iwatani","sojitz","mitsui-bussan"]
RATIO_WHITELIST = {
    "sumitomo-corp",  # 住友: 意図的に「倍率は189倍あるけど見てるのは社風」を残す（承認済）
    "iwatani",        # 岩谷: 暫定許容。原則D違反の可能性→台本修正後にここから外す
}

TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*(.*)$", re.S)
RATIO_RE = re.compile(r"(約)?\d+(\.\d+)?\s*[〜~–-]?\s*(\d+)?\s*倍")
NEG_RE = re.compile(r"倍率(の話)?(じゃ|では|でなく|より)")
SELECTIVITY_CTX = ("倍率","採用","応募","競争","入社","選考","難関","内定","エントリー","志望")
HEADCOUNT_RANGE_RE = re.compile(r"\d+\s*[-〜~–]\s*\d+\s*名")
MD_RE = re.compile(r"(\*\*|__|~~|```|\[[^\]]+\]\([^)]+\)|(?m:^\s*#{1,6}\s))")
TERMINAL_OK = "。．！？!?」』）)…ー〜"
TOKEN_RE = re.compile(r"[一-龯々ァ-ヶーＡ-ＺA-Z]{2,}")
STOP = {"事業","会社","仕事","自分","就活","社員","本当","存在","世界","会話","今日",
        "場所","海外","日本","世の中","みんな","一緒","気持","意味","理由","最初","普通"}

def parse_lines(scenario):
    out = []
    for i, k in enumerate(scenario.get("koma", []), start=1):
        for raw in (k.get("script") or []):
            m = TAG_RE.match(raw or "")
            out.append((i, m.group(1).strip().lower(), m.group(2).strip()) if m
                       else (i, "", (raw or "").strip()))
    return out

def overlay_texts(scenario):
    out = []
    for i, k in enumerate(scenario.get("koma", []), start=1):
        ov = k.get("overlay_text") or {}
        for key in ("main_copy", "sub", "title"):
            if ov.get(key): out.append((i, key, str(ov[key])))
    return out

def _f(lint, sev, koma, detail):
    return {"lint": lint, "severity": sev, "koma": koma, "detail": detail}

def lint_ratio_ban(scenario, company_slug=None):
    res = []
    wl = company_slug in RATIO_WHITELIST
    def check(koma, src, text):
        if "倍率" not in text and not RATIO_RE.search(text): return
        if NEG_RE.search(text): return  # 否定/棄却＝原則D準拠、flagしない
        has_sel = any(c in text for c in SELECTIVITY_CTX)  # 採用選抜の文脈か
        num = RATIO_RE.search(text)
        if num and has_sel:               # 選抜文脈での倍率数値の肯定提示が原則D対象
            sev = "warning" if wl else "error"
            note = "(whitelist:意図的容認)" if wl else "(原則D:倍率数値を出さない)"
            res.append(_f("ratio_ban", sev, koma, f"倍率数値『{num.group(0)}』{src}{note}"))
        elif "倍率" in text:              # 数値なしの倍率肯定言及
            res.append(_f("ratio_ban","warning",koma,f"『倍率』肯定言及{src}(数値なし・要確認)"))
        # num だが非選抜 (売上4倍 / 駐在手当×1.5倍 等) は対象外でスキップ
    for koma, sp, text in parse_lines(scenario): check(koma,"",text)
    for koma, key, text in overlay_texts(scenario): check(koma,f" overlay.{key}",text)
    return res

def lint_raw_markdown(scenario):
    res = []
    for koma, sp, text in parse_lines(scenario):
        if MD_RE.search(text): res.append(_f("raw_markdown","error",koma,f"生Markdown: {text[:30]}"))
    for koma, key, text in overlay_texts(scenario):
        if MD_RE.search(text): res.append(_f("raw_markdown","error",koma,f"生Markdown overlay.{key}: {text[:30]}"))
    return res

def lint_unsourced_headcount(scenario):
    res = []
    for koma, sp, text in parse_lines(scenario):
        for mm in HEADCOUNT_RANGE_RE.finditer(text):
            res.append(_f("unsourced_headcount","warning",koma,
                          f"採用数レンジ『{mm.group(0)}』要出典/無ければぼかす"))
    return res

def lint_word_repeat(scenario):
    meta = scenario.get("meta", {}) or {}
    excl = set(meta.get("whitelisted_generic_terms", []) or [])
    for key in ("company","company_name","name","company_short","industry"):
        if meta.get(key): excl.add(str(meta[key]))
    counts = {}
    for koma, sp, text in parse_lines(scenario):
        for tok in TOKEN_RE.findall(text): counts[tok] = counts.get(tok,0)+1
    res = []
    for tok, c in counts.items():
        if c >= 3 and tok not in STOP and not any((tok in e or e in tok) for e in excl):
            res.append(_f("word_repeat","warning",None,f"同語連発『{tok}』×{c}(1台本2回まで)"))
    return res

def lint_terminal_punctuation(scenario):
    res = []
    for koma, sp, text in parse_lines(scenario):
        if text and text[-1] not in TERMINAL_OK:
            res.append(_f("terminal_punct","warning",koma,f"終端記号なし: …{text[-12:]}"))
    return res

def lint_third_party_dominance(scenario):
    lines = parse_lines(scenario)
    total = len([1 for _, sp, t in lines if t])
    if total == 0: return []
    res = []
    third = [(koma, sp) for koma, sp, t in lines if t and sp and sp not in PROTAGONISTS]
    ratio = len(third)/total
    if ratio > 0.25:
        res.append(_f("third_party_dominance","error",None,f"第三者発話比率{ratio:.0%}(>25%)主役化リスク"))
    elif ratio > 0.21:
        res.append(_f("third_party_dominance","warning",None,f"第三者発話比率{ratio:.0%}(>21%)注意"))
    for koma, sp in third:
        if koma < 6 or koma > 8:
            res.append(_f("third_party_dominance","warning",koma,f"第三者[{sp}]がコマ{koma}(原則6-8)"))
    return res

def run_ext_lints(scenario, company_slug=None):
    findings = (lint_ratio_ban(scenario, company_slug) + lint_raw_markdown(scenario)
                + lint_unsourced_headcount(scenario) + lint_word_repeat(scenario)
                + lint_terminal_punctuation(scenario) + lint_third_party_dominance(scenario))
    e = sum(1 for f in findings if f["severity"]=="error")
    w = sum(1 for f in findings if f["severity"]=="warning")
    return {"slug": company_slug, "findings": findings, "errors": e, "warnings": w}

def slug_of(arg):
    return os.path.basename(os.path.dirname(os.path.abspath(arg))) if os.path.isfile(arg) else arg

def load_scenario(arg):
    p = arg if os.path.isfile(arg) else os.path.join(OUTPUT, arg, "scenario_v4.json")
    with open(p, encoding="utf-8") as fh: return json.load(fh)

def format_report(r):
    out = [f"[{r['slug']}] errors={r['errors']} warnings={r['warnings']}"]
    for f in r["findings"]:
        km = f"koma{f['koma']}" if f["koma"] else "-"
        out.append(f"  {f['severity'].upper():7} {f['lint']:22} {km:7} {f['detail']}")
    return "\n".join(out)

def _fixtures():
    return {
      "ratio_ban":{"meta":{},"koma":[{"script":["[nana] 採用倍率は100倍だって。"]}]},
      "raw_markdown":{"meta":{},"koma":[{"script":["[haruki] これは**重要**だよ。"]}]},
      "unsourced_headcount":{"meta":{},"koma":[{"script":["[nana] 採用は7-15名らしい。"]}]},
      "word_repeat":{"meta":{},"koma":[{"script":["[nana] 動脈の話。"]},
                     {"script":["[haruki] 動脈はね。"]},{"script":["[nana] また動脈。"]}]},
      "terminal_punct":{"meta":{},"koma":[{"script":["[nana] 終端が無い文章だよね"]}]},
      "third_party_dominance":{"meta":{},"koma":[
          {"script":["[senpai] 俺が主役だ。","[senpai] ずっと喋る。"]},
          {"script":["[senpai] まだ喋る。","[nana] 一言。"]}]},
    }

def selftest():
    ok = True
    print("=== 負例フィクスチャ：各lint発火 ===")
    for name, sc in _fixtures().items():
        fired = any(f["lint"]==name for f in run_ext_lints(sc, name)["findings"])
        print(f"  {'OK ' if fired else 'NG '} {name}: {'発火' if fired else '発火せず(NG)'}")
        ok = ok and fired
    print("\n=== 商社9社：error=0 か ===")
    terr = 0
    for slug in SHOSHA9:
        try: r = run_ext_lints(load_scenario(slug), slug)
        except Exception as e: print(f"  NG  {slug}: ERR {e}"); ok=False; continue
        terr += r["errors"]
        print(f"  {'OK ' if r['errors']==0 else 'NG '} {slug}: errors={r['errors']} warnings={r['warnings']}")
        for f in r["findings"]:
            if f["severity"]=="error": print(f"        ERROR {f['lint']} koma{f['koma']} {f['detail']}")
    if terr: ok = False
    print("\n=== 警告内訳（参考・非ブロック）===")
    for slug in SHOSHA9:
        try: r = run_ext_lints(load_scenario(slug), slug)
        except Exception: continue
        ws = {}
        for f in r["findings"]:
            if f["severity"]=="warning": ws[f["lint"]] = ws.get(f["lint"],0)+1
        print(f"  {slug}: " + (", ".join(f"{k}={v}" for k,v in ws.items()) or "なし"))
    print("\n=== SELFTEST:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1

def main(argv):
    if not argv or argv[0]=="--selftest": return selftest()
    r = run_ext_lints(load_scenario(argv[0]), slug_of(argv[0]))
    print(format_report(r)); return 1 if r["errors"] else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
