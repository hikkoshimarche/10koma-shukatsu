#!/usr/bin/env python3
"""EDINET 平均年間給与 一括スイープ。2026年3月期有報の平均年間給与を一次取得し年収コマ/診断/datasheetへ反映。
対象: output/_salary_sweep_targets.json の union。Source-or-Silence: 有報(提出会社)の値のみ・年度検証必須。

段: (1)filing index構築(有報docTypeCode=120を提出期間走査・キャッシュ) (2)社名照合でdocID特定
   (3)PDF取得(キー不要)→平均年間給与+対象年度抽出 (4)2026年3月期検証 (5)[本実行のみ]各所更新→lint/canary。

  python tools/edinet_salary_sweep.py --dry               # 取得・検証のみ(更新しない)。取得社数/年度通過数を報告
  python tools/edinet_salary_sweep.py --dry --only <slug>  # 対象限定
  python tools/edinet_salary_sweep.py                       # 本実行(更新)  ※要 --apply 相当は別途配線
環境変数 EDINET_API_KEY 必須(未設定なら中止)。
"""
import os, sys, json, re, ssl, time, urllib.request, subprocess, datetime

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TARGETS = os.path.join(OUT, "_salary_sweep_targets.json")
INDEX = os.path.join(OUT, "_edinet_filing_index.json")
KEY = os.environ.get("EDINET_API_KEY", "").strip()
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
DOC_API = "https://api.edinet-fsa.go.jp/api/v2/documents.json?date={d}&type=2&Subscription-Key={k}"
PDF_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{docid}.pdf"
_SAL_LABEL = re.compile(r"平均年間給与")


def _norm(name):
    n = re.sub(r"(株式会社|\(株\)|㈱|・|\s|　|グループ$)", "", name or "")
    return n.strip()


def build_index(dry_dates=None):
    """有報(120)を提出期間走査してキャッシュ。key=正規化filerName → {docid,periodEnd,secCode,edinetCode,filer}."""
    if os.path.exists(INDEX):
        return json.load(open(INDEX))
    idx = {}
    # 2026年3月期有報の提出ピーク: 2026-06-01〜2026-07-15 の平日
    start = datetime.date(2026, 6, 1); end = datetime.date(2026, 7, 15)
    d = start
    days = 0
    while d <= end:
        if d.weekday() < 5:  # 平日
            url = DOC_API.format(d=d.isoformat(), k=KEY)
            try:
                r = json.load(urllib.request.urlopen(url, context=CTX, timeout=40))
            except Exception as e:
                sys.stderr.write(f"  [idx] {d} ERR {str(e)[:60]}\n"); d += datetime.timedelta(days=1); continue
            for x in r.get("results", []):
                if x.get("docTypeCode") != "120":
                    continue
                pe = x.get("periodEnd") or ""
                key = _norm(x.get("filerName", ""))
                if key and key not in idx:
                    idx[key] = {"docid": x.get("docID"), "periodEnd": pe, "secCode": x.get("secCode"),
                                "edinetCode": x.get("edinetCode"), "filer": x.get("filerName")}
            days += 1
        d += datetime.timedelta(days=1)
    json.dump(idx, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False)
    sys.stderr.write(f"  [idx] 構築完了: 有報{len(idx)}社 ({days}営業日走査)\n")
    return idx


def slug_name(slug):
    dp = os.path.join(OUT, slug, "datasheet.json")
    if os.path.exists(dp):
        try:
            return json.load(open(dp)).get("name", slug)
        except Exception:
            pass
    sh = os.path.join(ROOT, "shindan", "attributes", f"{slug}.json")
    if os.path.exists(sh):
        try:
            return json.load(open(sh)).get("name", slug)
        except Exception:
            pass
    return slug


def match_docid(slug, idx, name2entry):
    nm = _norm(slug_name(slug))
    if nm in name2entry:
        return name2entry[nm]
    # 部分一致(社名がfiler内 or filerが社名内)
    for k, e in name2entry.items():
        if len(nm) >= 4 and (nm in k or k in nm):
            return e
    return None


def fetch_pdf_text(docid):
    tmp = f"/tmp/edinet_{docid}.pdf"
    try:
        req = urllib.request.Request(PDF_URL.format(docid=docid), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp, open(tmp, "wb") as f:
            f.write(resp.read())
    except Exception:
        return ""
    # 従業員の状況表は推移表(1-2頁)より後方。従業員状況表(平均年齢を含む)まで確保するため全頁走査。
    p = subprocess.run([sys.executable, "-c",
                        "import fitz,sys;d=fitz.open(sys.argv[1]);buf=[]\n"
                        "for pg in d:\n"
                        "    tx=pg.get_text();buf.append(tx)\n"
                        "    if '平均年間給与' in tx and '平均年齢' in tx: break\n"
                        "print(''.join(buf))", tmp],
                       capture_output=True, text=True)
    try:
        os.remove(tmp)
    except Exception:
        pass
    return p.stdout or ""


def extract_salary(text):
    """有報「従業員の状況」表: 提出会社行 [従業員数, 平均年齢X.X, 平均勤続Y.Y, 平均年間給与] の並びを利用し、
    『平均年齢・勤続年数(小数2連続)の直後の整数』を平均年間給与として特定(円/千円をラベルで判定)。
    従業員数×1000等の誤認(千円単位で従業員数がレンジに入る問題)を回避。"""
    # (1) 従業員の状況表(平均年齢・平均勤続と同居)を優先: 小数2連続(年齢.・勤続.)の直後の整数=給与
    for m in re.finditer("平均年間給与", text):
        i = m.start()
        ctx = text[max(0, i - 120):i + 500]
        if "平均年齢" not in ctx or not re.search(r"勤続", ctx):
            continue
        unit = 1000 if "千円" in text[i:i + 20] else 1
        toks = re.findall(r"[\d,]+\.\d+|[\d,]+", text[i:i + 500])
        for k in range(len(toks) - 2):
            if "." in toks[k] and "." in toks[k + 1] and "." not in toks[k + 2]:
                yen = int(toks[k + 2].replace(",", "")) * unit
                if 2_000_000 <= yen <= 80_000_000:
                    return yen
    # (2) フォールバック=主要経営指標の推移表: ラベル直後の数列(最新年度=最後の範囲内値)
    i = text.find("平均年間給与")
    if i >= 0:
        unit = 1000 if "千円" in text[i:i + 20] else 1
        series = []
        for x in re.findall(r"[\d,]{4,}", text[i + 6:i + 90]):   # ラベル直後の近接数列のみ
            yen = int(x.replace(",", "")) * unit
            if 2_000_000 <= yen <= 80_000_000:
                series.append(yen)
        if series:
            return series[-1]                                    # 最新年度
    return None


def main():
    if not KEY:
        sys.exit("⛔ EDINET_API_KEY 未設定。中止(何も更新していません)。")
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only"); only = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
    tg = json.load(open(TARGETS))
    targets = only or tg["union"]
    sys.stderr.write(f"対象{len(targets)}社 / filing index構築中...\n")
    idx = build_index()
    name2entry = {k: v for k, v in idx.items()}
    matched, fetched, ypass, results, held = 0, 0, 0, [], []
    for slug in targets:
        e = match_docid(slug, idx, name2entry)
        if not e:
            held.append((slug, "no_docid")); continue
        matched += 1
        # 年度: periodEnd が 2026-03 のものだけ(2026年3月期)
        pe = e.get("periodEnd") or ""
        text = fetch_pdf_text(e["docid"])
        if not text:
            held.append((slug, "pdf_fail")); continue
        yen = extract_salary(text)
        if not yen:
            held.append((slug, "salary_not_found")); continue
        fetched += 1
        is2026 = pe.startswith("2026-03")
        if is2026:
            ypass += 1
        else:
            held.append((slug, f"period={pe}"))
        results.append({"slug": slug, "yen": yen, "man": round(yen / 10000), "periodEnd": pe, "y2026": is2026,
                        "filer": e.get("filer")})
        time.sleep(0.25)
    out = {"targets": len(targets), "matched_docid": matched, "salary_fetched": fetched,
           "year_pass_2026": ypass, "held_reasons_top": held[:30],
           "sample_pass": [r for r in results if r["y2026"]][:15]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if not dry:
        sys.stderr.write("※本実行の更新配線(scenario/company_panels/datasheet/shindan)は未接続。--dryで検証後に配線する。\n")


if __name__ == "__main__":
    main()
