#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shindan/extract.py — 1社分の属性抽出ハーネス。

二層:
  ① ソフト属性(マッチング用)= 業界baseline prior + ファクトシート記述でLLM微調整。estimated:true。null可。
  ② 表示ファクト(結果画面に数字で出す)= 出典必須・verbatim照合。無ければnull(定性文で薦める)。
     - avg_salary: 有報grade(有報/日経nkd/公式IR)のみ採用。第三者推定は不採用(Source-or-Silence)。
       data_caveat_list.csv(verdict=verified)を最優先。
     - starting_salary: 公式初任給。ファクトシート待遇欄からverbatim抽出。

使い方: python3 extract.py <company_id>     # 単体
        from extract import extract_company # ハーネス
"""
import os, re, json, sys, csv, requests
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
PIPE = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline"))
OUT  = PIPE / "output"
load_dotenv(os.path.expanduser("~/oscar-ai/morning-briefing/.env"))
ANT_KEY = re.sub(r"\s", "", os.environ.get("ANTHROPIC_API_KEY", ""))
MODEL = "claude-haiku-4-5-20251001"

BASELINE = json.load(open(ROOT / "industry_baseline.json"))["baselines"]
# companies.json id → output dir 別名(episode-slug差異)
DIR_ALIAS = {"itochu": "itochu-shoji"}

# 有報grade判定: これらを出典に含むもののみ avg_salary をファクト採用
# 有報grade: 日経の年収DB(nikkei.com)は有報 単体平均年収ベース→採用。公式IR/有報/決算短信も採用。
YUHO_MARKERS = ["有価証券報告書", "有報", "nikkei.com", "/salary/?scode", "yuho", "投資家情報", "決算短信", "ir/library"]
# 第三者推定(不採用の目印。avg_salaryは上のYUHO_MARKERSに合致しない限り不採用)
THIRD_PARTY_HINT = ["talentsquare", "openwork", "en-hyouban", "doda", "type.jp", "vorkers", "生涯年収", "転職会議", "renew-career", "unlockly"]


def _dir_for(cid):
    d = DIR_ALIAS.get(cid, cid)
    return OUT / d


def load_company(cid):
    d = _dir_for(cid)
    fs = (d / "factsheet.md")
    factsheet = fs.read_text(encoding="utf-8") if fs.exists() else ""
    corpus = ""
    qc = d / "quiz_corpus.json"
    if qc.exists():
        try:
            data = json.load(open(qc))
            if isinstance(data, dict):
                corpus = "\n".join(str(v) for v in data.values())
            else:
                corpus = str(data)
        except Exception:
            corpus = ""
    return factsheet, corpus


def load_caveats():
    rows = []
    for p in [PIPE / "output" / "data_caveat_list.csv", ROOT.parent / "tools" / "data_caveat_list.csv"]:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            break
    return rows


def _norm_digits(s):
    """数値照合用: 数字だけ連結(約/カンマ/空白/全角を無視)。"""
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    return re.sub(r"[^0-9]", "", s)


def verbatim_ok(figure, *texts):
    """figure中の主要数字列が、いずれかのtext中に(カンマ等無視で)出現するか。"""
    fig = _norm_digits(figure)
    if len(fig) < 3:  # 短すぎる数値は照合対象外(誤検出防止)→ 不採用扱い
        return False
    for t in texts:
        if fig and fig in _norm_digits(t):
            return True
    return False


def _extract_line(factsheet, label):
    """ファクトシートの '- **<label>**: 値 [出典](url)' 行を拾う。"""
    for line in factsheet.splitlines():
        if label in line and "**" in line:
            return line
    return ""


def _source_url(line):
    m = re.search(r"\[出典\]\((https?://[^)]+)\)", line)
    return m.group(1) if m else ""


def extract_avg_salary(name, caveats, factsheet, corpus):
    """② 平均年収(万円): 有報gradeのみ。caveat verified最優先→factsheet(有報出典)。無ければNone。"""
    # 会社名の核(株式会社等/括弧内コード除去)
    core = re.sub(r"(株式会社|ホールディングス|グループ|\(.*?\)|（.*?）)", "", name).strip()
    # 1) data_caveat_list: subject_entityに社名core & verified & 有報系
    for r in caveats:
        subj = r.get("subject_entity", "")
        if core and core[:3] in subj and r.get("verdict", "").startswith("verified"):
            fig = r.get("figure", "")
            man = _norm_digits(fig)
            if man and ("万" in fig):
                val = int(_norm_digits(fig.split("万")[0]))
                return {"value": val, "unit": "万円",
                        "evidence": {"source_url": r.get("primary_source", ""),
                                     "quote": f"{subj} {r.get('claim','')} {fig}（{r.get('source_type','')}）"},
                        "as_of": r.get("fiscal_year", ""), "confidence": "high", "estimated": False}
    # 2) factsheet 平均年収行: 出典が有報grade のときのみ採用
    line = _extract_line(factsheet, "平均年収")
    if line:
        url = _source_url(line)
        blob = (line + " " + url).lower()
        is_yuho = any(m.lower() in blob for m in YUHO_MARKERS)
        is_third = any(m.lower() in blob for m in THIRD_PARTY_HINT)
        m = re.search(r"([0-9,]+)\s*万円", line.replace("，", ","))
        if m and is_yuho and not is_third:
            val = int(m.group(1).replace(",", ""))
            fig = m.group(0)
            if verbatim_ok(fig, factsheet, corpus):
                return {"value": val, "unit": "万円",
                        "evidence": {"source_url": url, "quote": line.strip("- ").strip()},
                        "as_of": "", "confidence": "medium", "estimated": False}
    return None  # Source-or-Silence: 有報grade出典が無ければ数字を出さない


def extract_starting_salary(factsheet, corpus):
    """② 初任給(月給・円): 公式初任給。ファクトシート待遇欄からverbatim抽出。無ければNone。"""
    line = _extract_line(factsheet, "初任給")
    if not line:
        return None
    url = _source_url(line)
    # 学部卒 月給 XXX,XXX円 を優先(無ければ最初の n,nnn円)
    m = re.search(r"(?:学部卒|大卒|学部)[^0-9]{0,8}([0-9]{2,3},[0-9]{3})\s*円", line)
    if not m:
        m = re.search(r"([0-9]{2,3},[0-9]{3})\s*円", line)
    if not m:
        return None
    fig = m.group(1) + "円"
    if not verbatim_ok(fig, factsheet, corpus):
        return None
    val = int(m.group(1).replace(",", ""))
    blob = (line + " " + url).lower()
    is_third = any(t in blob for t in THIRD_PARTY_HINT)
    return {"value": val, "unit": "円/月",
            "evidence": {"source_url": url, "quote": line.strip("- ").strip()},
            "as_of": "", "confidence": "medium" if is_third else "high", "estimated": False}


SOFT_KEYS = ["tenkin_do", "kaigai_do", "stability", "growth", "remote_flex", "young_discretion"]


def _clamp5(x, default):
    try:
        v = int(round(float(x)))
        return min(5, max(1, v))
    except Exception:
        return default


def soft_attributes(cid, name, industry, factsheet):
    """① baseline priorをLLMで微調整。失敗時はbaselineそのまま(coverage維持)。"""
    base = BASELINE.get(industry, {"tenkin_do": 3, "kaigai_do": 3, "stability": 3, "growth": 3,
                                   "remote_flex": 3, "young_discretion": 3, "bunri": "文理両方",
                                   "job_tags": [], "confidence": "low"})
    conf = base.get("confidence", "medium")
    result = {k: {"value": base.get(k, 3), "estimated": True, "confidence": conf, "evidence": None} for k in SOFT_KEYS}
    result["bunri"] = {"value": base.get("bunri", "文理両方"), "estimated": True, "confidence": conf, "evidence": None}
    result["job_tags"] = {"value": base.get("job_tags", []), "estimated": True, "confidence": conf, "evidence": None}
    trend = ""
    if not ANT_KEY or not factsheet:
        return result, trend
    sys_p = ("あなたは就活診断のための企業属性アナリスト。業界baseline priorを出発点に、ファクトシートの記述から"
             "ソフト属性(1-5)を推定調整する。これはMBTI的な参考提案の内部シグナルでラフでよい。断定不能はbaseline維持。"
             "海外拠点/駐在の記述→kaigai_do、全国拠点/転勤→tenkin_do、成長率/新規事業→growth、老舗/安定/インフラ→stability、"
             "リモート/フレックス制度→remote_flex、若手抜擢/裁量→young_discretion に反映。JSONのみ出力。")
    usr_p = json.dumps({
        "company": name, "industry": industry, "baseline": {k: base.get(k) for k in SOFT_KEYS + ["bunri", "job_tags"]},
        "factsheet_excerpt": factsheet[:4000],
        "output_schema": {**{k: "1-5 int" for k in SOFT_KEYS},
                          "bunri": "文系寄り|理系寄り|文理両方", "job_tags": "list(職種タグ最大4)",
                          "trend_note": "20-40字の傾向表現(結果画面の根拠用。例:海外拠点が多く海外志向に合う傾向)"}
    }, ensure_ascii=False)
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
                          headers={"x-api-key": ANT_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                          json={"model": MODEL, "max_tokens": 500, "system": sys_p,
                                "messages": [{"role": "user", "content": usr_p}]}, timeout=60)
        if r.status_code != 200:
            return result, trend
        txt = "".join(b.get("text", "") for b in r.json().get("content", []))
        j = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
        for k in SOFT_KEYS:
            result[k]["value"] = _clamp5(j.get(k), base.get(k, 3))
            result[k]["confidence"] = "medium"
        if j.get("bunri") in ("文系寄り", "理系寄り", "文理両方"):
            result["bunri"]["value"] = j["bunri"]; result["bunri"]["confidence"] = "medium"
        if isinstance(j.get("job_tags"), list) and j["job_tags"]:
            result["job_tags"]["value"] = j["job_tags"][:4]; result["job_tags"]["confidence"] = "medium"
        trend = str(j.get("trend_note", ""))[:60]
    except Exception:
        pass
    return result, trend


_TREND_PHRASE = {
    "kaigai_do": "海外展開に積極的な傾向", "tenkin_do": "全国・海外に拠点が広がる傾向",
    "stability": "安定・成熟した基盤の傾向", "growth": "成長・拡大局面の傾向",
    "remote_flex": "柔軟な働き方が比較的整う傾向", "young_discretion": "若手から裁量を持ちやすい傾向",
}


def _fallback_trend(soft, industry):
    """LLM未取得時の傾向文。スコア上位2軸から生成(結果画面の根拠用)。"""
    scored = sorted(((soft[k]["value"], k) for k in SOFT_KEYS if isinstance(soft[k]["value"], int)),
                    reverse=True)
    tops = [_TREND_PHRASE[k] for v, k in scored[:2] if v >= 4]
    if tops:
        return f"{industry}。" + "・".join(tops) + "。"
    return f"{industry}の一般的な傾向にもとづく提案です。"


def extract_company(cid, name, industry):
    factsheet, corpus = load_company(cid)
    caveats = load_caveats()
    lint = {"errors": [], "notes": []}
    if not factsheet:
        lint["errors"].append("no_factsheet")
    avg = extract_avg_salary(name, caveats, factsheet, corpus)
    start = extract_starting_salary(factsheet, corpus)
    if avg is None:
        lint["notes"].append("avg_salary: 有報grade出典なし→null(定性提案)")
    if start is None:
        lint["notes"].append("starting_salary: 抽出/照合不可→null")
    soft, trend = soft_attributes(cid, name, industry, factsheet)
    if not trend:
        trend = _fallback_trend(soft, industry)
    return {
        "slug": cid, "name": name, "industry": industry,
        "soft": soft,
        "facts": {"avg_salary": avg, "starting_salary": start,
                  "industry": {"value": industry, "estimated": False}},
        "trend_note": trend,
        "disclaimer": "公式公開情報と業界傾向に基づく参考提案です。",
        "lint": lint,
    }


if __name__ == "__main__":
    cid = sys.argv[1]
    comp = json.load(open(PIPE / "data" / "companies.json"))
    name, ind = None, None
    for i2, lst in comp.items():
        for c in lst:
            if c["id"] == cid:
                name, ind = c["name"], i2
    if not name:
        print("unknown id", cid); sys.exit(1)
    print(json.dumps(extract_company(cid, name, ind), ensure_ascii=False, indent=2))
