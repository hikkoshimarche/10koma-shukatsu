#!/usr/bin/env python3
"""EDINET 平均年間給与 一括スイープ(強化版)。2026年3月期有報の平均年間給与を一次取得。
照合強化: NFKC(全角→半角)正規化 + 複数社名源(datasheet/companies.json/shindan) + secCode。
精度ゲート: 「従業員の状況」表と「主要な経営指標等の推移」表の相互照合(±5%一致)のみ採用。
  乖離>25%/片方欠落 → 据置(要人間確認リスト)。走査窓=2026-03〜07(3月期/12月期両対応)。
出力(--dry): output/_salary_sweep_result.json (adopt/hold/exclude/review)。
  python tools/edinet_salary_sweep.py --dry
環境変数 EDINET_API_KEY 必須。
"""
import os, sys, json, re, ssl, time, urllib.request, subprocess, datetime, unicodedata

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TARGETS = os.path.join(OUT, "_salary_sweep_targets.json")
INDEX = os.path.join(OUT, "_edinet_filing_index.json")
RESULT = os.path.join(OUT, "_salary_sweep_result.json")
EXCLUDE = os.path.join(OUT, "_edinet_excluded.json")
KEY = os.environ.get("EDINET_API_KEY", "").strip()
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
DOC_API = "https://api.edinet-fsa.go.jp/api/v2/documents.json?date={d}&type=2&Subscription-Key={k}"
PDF_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{docid}.pdf"


def norm(n):
    n = unicodedata.normalize("NFKC", n or "")
    return re.sub(r"(株式会社|\(株\)|㈱|・|\s|　|グループ$|ホールディングス$|HD$)", "", n).strip()


def build_index():
    if os.path.exists(INDEX):
        return json.load(open(INDEX))
    idx = {}
    start, end = datetime.date(2026, 3, 1), datetime.date(2026, 7, 24)
    d = start; days = 0
    while d <= end:
        if d.weekday() < 5:
            try:
                r = json.load(urllib.request.urlopen(DOC_API.format(d=d.isoformat(), k=KEY), context=CTX, timeout=40))
            except Exception:
                d += datetime.timedelta(days=1); continue
            for x in r.get("results", []):
                if x.get("docTypeCode") != "120":
                    continue
                key = norm(x.get("filerName", ""))
                pe = x.get("periodEnd") or ""
                if not key:
                    continue
                if key not in idx or pe > idx[key]["periodEnd"]:      # 最新periodEnd優先
                    idx[key] = {"docid": x.get("docID"), "periodEnd": pe, "secCode": x.get("secCode"),
                                "edinetCode": x.get("edinetCode"), "filer": x.get("filerName")}
            days += 1
        d += datetime.timedelta(days=1)
    json.dump(idx, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False)
    sys.stderr.write(f"  [idx] 有報{len(idx)}社 ({days}営業日走査)\n")
    return idx


def slug_names(slug):
    """slugの社名候補(datasheet/companies.json/shindan)を返す。"""
    names = []
    for path in (os.path.join(OUT, slug, "datasheet.json"),
                 os.path.join(ROOT, "shindan", "attributes", f"{slug}.json")):
        if os.path.exists(path):
            try:
                nm = json.load(open(path)).get("name")
                if nm:
                    names.append(nm)
            except Exception:
                pass
    global _CJ
    if _CJ is None:
        _CJ = {}
        try:
            for ind, cs in json.load(open(os.path.join(ROOT, "public", "companies.json"))).items():
                for c in cs:
                    _CJ[c["id"]] = c["name"]
        except Exception:
            pass
    if slug in _CJ:
        names.append(_CJ[slug])
    return names


_CJ = None


def match(slug, idx):
    for nm in slug_names(slug):
        k = norm(nm)
        if k in idx:
            return idx[k]
    # 部分一致(正規化名の包含)
    cands = [norm(nm) for nm in slug_names(slug) if len(norm(nm)) >= 4]
    for key, e in idx.items():
        for c in cands:
            if c in key or key in c:
                return e
    return None


def fetch_text(docid):
    tmp = f"/tmp/edinet_{docid}.pdf"
    try:
        req = urllib.request.Request(PDF_URL.format(docid=docid), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r, open(tmp, "wb") as f:
            f.write(r.read())
    except Exception:
        return ""
    # 推移表(1-2頁)と従業員の状況表(後方)の両方を確保するため全頁走査(fitzは高速)。
    p = subprocess.run([sys.executable, "-c",
                        "import fitz,sys;d=fitz.open(sys.argv[1]);print(''.join(pg.get_text() for pg in d))", tmp],
                       capture_output=True, text=True)
    try:
        os.remove(tmp)
    except Exception:
        pass
    return p.stdout or ""


def _employee_table(text):
    """従業員の状況表: 提出会社行 [従業員数, 平均年齢, 平均勤続, 平均年間給与]。
    年齢(15-70)・勤続(0-45)らしい2連続の直後の給与レンジ値を採用(小数/整数の両方に対応=emp_missing回収)。"""
    def fnum(x):
        try:
            return float(x.replace(",", ""))
        except ValueError:
            return None
    for m in re.finditer("平均年間給与", text):
        i = m.start()
        ctx = text[max(0, i - 120):i + 500]
        if "平均年齢" not in ctx or not re.search(r"勤続", ctx):
            continue
        unit = 1000 if "千円" in text[i:i + 20] else 1
        toks = re.findall(r"[\d,]+\.\d+|[\d,]+", text[i:i + 500])
        # (a) 小数2連続(年齢.・勤続.)直後
        for k in range(len(toks) - 2):
            if "." in toks[k] and "." in toks[k + 1] and "." not in toks[k + 2]:
                yen = int(toks[k + 2].replace(",", "")) * unit
                if 2_000_000 <= yen <= 80_000_000:
                    return yen
        # (b) 年齢らしい(15-70)・勤続らしい(0-45)の2連続 直後の給与レンジ値(整数年齢の表)
        for k in range(len(toks) - 2):
            a, b, c = fnum(toks[k]), fnum(toks[k + 1]), fnum(toks[k + 2])
            if a and b and c and 15 <= a <= 70 and 0 <= b <= 45 and "." not in toks[k + 2]:
                yen = int(c) * unit
                if 2_000_000 <= yen <= 80_000_000:
                    return yen
    return None


def _trend_table(text):
    """主要な経営指標等の推移: 平均年間給与『行』の数列の最新(最後)値。
    誤取得源を除外(教訓反映): 1人当たり営業利益行/セグメント行/臨時従業員の外書き()/EDINET書類コード(E+数字)/年号(20XX)。"""
    for m in re.finditer("平均年間給与", text):
        i = m.start()
        head = text[i:i + 40]
        if re.search(r"1人当たり|一人当たり|当たり営業利益|セグメント", head):   # 別指標行=除外
            continue
        unit = 1000 if "千円" in text[i:i + 24] else 1
        # ラベル(単位表記込)直後〜次の指標ラベル(長い漢字語)までの区間に限定=行を跨がない
        seg = text[i + 6:i + 140]
        seg = re.split(r"従業員|セグメント|営業利益|[一-龥]{4,}", seg[seg.find(")") + 1:] if ")" in seg[:16] else seg)[0]
        series = []
        for x in re.findall(r"[\d,]{4,}", seg):
            v = x.replace(",", "")
            if re.fullmatch(r"20\d\d", v):        # 年号(2024/2025等)=除外
                continue
            yen = int(v) * unit
            if 2_000_000 <= yen <= 80_000_000:
                series.append(yen)
        if series:
            return series[-1]                     # 最新年度(行内の最後)
    return None


def extract(text):
    """(採否, 値, emp値, trend値, 理由). 相互照合±5%一致のみ採用。乖離>25%/片方欠落は据置。"""
    emp = _employee_table(text)
    tr = _trend_table(text)
    if emp and tr:
        diff = abs(emp - tr) / max(emp, tr)
        if diff <= 0.05:
            return True, emp, emp, tr, "match"
        if diff > 0.25:
            return False, None, emp, tr, f"divergent({diff:.0%})"
        return False, None, emp, tr, f"minor_diff({diff:.0%})"   # 5〜25%も慎重に据置
    if emp and not tr:
        return False, None, emp, None, "trend_missing"
    if tr and not emp:
        return False, None, None, tr, "emp_missing"
    return False, None, None, None, "not_found"


def main():
    if not KEY:
        sys.exit("⛔ EDINET_API_KEY 未設定")
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only"); only = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
    targets = only or json.load(open(TARGETS))["union"]
    sys.stderr.write(f"対象{len(targets)}社 / index構築...\n")
    idx = build_index()
    adopt, hold, exclude, review = [], [], [], []
    for slug in targets:
        e = match(slug, idx)
        if not e:
            exclude.append({"slug": slug, "reason": "no_edinet_filing"}); continue
        pe = e.get("periodEnd") or ""
        if not (pe.startswith("2026") or pe.startswith("2025-12")):
            hold.append({"slug": slug, "reason": f"period={pe}", "docid": e["docid"]}); continue
        text = fetch_text(e["docid"])
        if not text:
            hold.append({"slug": slug, "reason": "pdf_fail", "docid": e["docid"]}); continue
        ok, val, emp, tr, why = extract(text)
        rec = {"slug": slug, "filer": e["filer"], "docid": e["docid"], "periodEnd": pe,
               "emp": emp, "trend": tr, "reason": why}
        if ok:
            rec["yen"] = val; rec["man"] = round(val / 10000)
            adopt.append(rec)
        elif why in ("divergent", "minor_diff") or why.startswith("divergent") or why.startswith("minor_diff"):
            review.append(rec); hold.append({"slug": slug, "reason": why, "docid": e["docid"]})
        else:
            hold.append({"slug": slug, "reason": why, "docid": e["docid"]})
        time.sleep(0.2)
    out = {"targets": len(targets), "adopt": len(adopt), "hold": len(hold), "exclude": len(exclude),
           "review_needed": len(review), "adopt_list": adopt, "review_list": review,
           "hold_reasons": _count([h["reason"].split("(")[0] for h in hold]),
           "exclude_list": [e["slug"] for e in exclude]}
    json.dump(out, open(RESULT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump([e["slug"] for e in exclude], open(EXCLUDE, "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("adopt_list", "review_list", "exclude_list")},
                     ensure_ascii=False, indent=1))


def _count(lst):
    from collections import Counter
    return dict(Counter(lst))


if __name__ == "__main__":
    main()
