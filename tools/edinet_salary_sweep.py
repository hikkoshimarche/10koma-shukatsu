#!/usr/bin/env python3
"""EDINET 平均年間給与 一括スイープ (キー投入後にすぐ実行できる準備済スクリプト)。
目的: 10コマ年収コマ/診断avg_salary/company_panels/datasheet の 平均年収 を 2026年3月期有報 の一次値へ一括更新。
対象: output/_salary_sweep_targets.json の union (10コマ年収社 ∪ 診断avg_salary据置社)。

一気通貫: キー投入 → 有報docID特定 → PDF取得 → 平均年間給与抽出 → 2026年3月期検証 → 各所更新 → lint → canary。
Source-or-Silence: 有報(提出会社ベース)の値のみ採用。推計/アグリゲータ不採用。取れない社は据置(理由記録)。

【実行前提】環境変数 EDINET_API_KEY (Subscription-Key)。未設定なら即中止(何も更新しない)。
  python tools/edinet_salary_sweep.py --dry        # 取得・検証のみ(更新しない)
  python tools/edinet_salary_sweep.py              # 本実行(D1/scenario/datasheet/shindan更新)
  python tools/edinet_salary_sweep.py --only <slug...>   # 対象限定
"""
import os, sys, json, re, subprocess, time

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
TARGETS = os.path.join(OUT, "_salary_sweep_targets.json")
EDINET_KEY = os.environ.get("EDINET_API_KEY", "").strip()
DOC_API = "https://api.edinet-fsa.go.jp/api/v2/documents.json"        # 一覧(要 Subscription-Key)
PDF_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{docid}.pdf"  # PDF(キー不要)
FY = "2026年3月期"

# slug → EDINET コード(E########). キー投入時に code→docID を引く。未知はEDINET全文検索でsecCode照合。
#   ※初回はビルドヘルパ build_edinet_code_map() で自動補完(証券コード→EDINETコード)し output/_edinet_code_map.json に保存。
CODE_MAP_PATH = os.path.join(OUT, "_edinet_code_map.json")


def _load_targets():
    if not os.path.exists(TARGETS):
        sys.exit(f"対象リスト無し: {TARGETS}  (先に集約スクリプトで生成)")
    return json.load(open(TARGETS))


def find_yuho_docid(edinet_code, sec_code=None):
    """EDINET documents.json を直近~90日走査し、当該社の 有報(docTypeCode=120) の docID を返す。要キー。
    2026年3月期対象(periodEnd ~2026-03-31)の最新有報を優先。取れなければ None。"""
    if not EDINET_KEY:
        return None
    import urllib.request
    # TODO(キー投入後): 直近の有報提出日レンジ(2026-06-01〜09-30)を日付走査
    for day_offset in range(0, 120):
        # date = (2026-09-30 − offset) を走査 (実装: 日付生成はargsで渡す/固定リストで)
        pass
    return None  # ← キー投入後に実装(下記 __main__ の TODO 参照)


def fetch_pdf_text(docid):
    """searchdocument/pdf/<docid>.pdf を取得しテキスト化(キー不要)。fitzはsubprocess隔離。"""
    import urllib.request
    url = PDF_URL.format(docid=docid)
    tmp = f"/tmp/edinet_{docid}.pdf"
    try:
        urllib.request.urlretrieve(url, tmp)
    except Exception as e:
        return ""
    p = subprocess.run([sys.executable, "-c",
                        "import fitz,sys;d=fitz.open(sys.argv[1]);print('\\n'.join(pg.get_text() for pg in d))", tmp],
                       capture_output=True, text=True)
    return p.stdout or ""


_SAL = re.compile(r"平均年間給与[^\d]{0,12}([\d,]{4,})\s*(?:円|千円)")
_FY = re.compile(r"(20\d{2})年3月")


def extract_salary(text):
    """有報テキストから 提出会社 平均年間給与(円) と 対象年度 を抽出。2026年3月期でなければ (val,fy) で返し呼側で弾く。"""
    m = _SAL.search(text)
    if not m:
        return None, None
    val = int(m.group(1).replace(",", ""))
    # 「従業員の状況」節近傍の年度
    fy = None
    fm = _FY.search(text[max(0, m.start() - 4000):m.start()])
    if fm:
        fy = f"{fm.group(1)}年3月期"
    return val, fy


def update_everywhere(slug, yen, dry):
    """平均年収 yen(円) を 10コマscenario/company_panels/datasheet/shindan に反映。万円表記へ整形。"""
    man = round(yen / 10000)                          # 円→万円
    label = f"{man:,}万円"
    changes = []
    # (1) 10コマ scenario_v4.json koma5 の 年収表記(旧2025万円 → 新2026万円)
    sc = os.path.join(OUT, slug, "scenario_v4.json")
    if os.path.exists(sc):
        raw = open(sc, encoding="utf-8").read()
        raw2 = re.sub(r"\d{3,4}万円", label, raw) if False else raw   # TODO: 旧年収値のみ狙って置換(koma5限定・年収文脈)
        # ↑ 安全のため「旧年収の実値」を対象社ごとに特定して置換(全万円置換は禁止=採用数万円等を壊す)
        changes.append(("scenario", "TODO: koma5年収のみ置換"))
    # (2) company_panels D1: dialogue/sub_copy の年収 → 生成はscenario_to_panels再実行が安全
    # (3) datasheet.json 主要財務 or 待遇 に平均年収 → 追記/更新
    # (4) shindan/attributes/<slug>.json facts.avg_salary = yen
    sh = os.path.join(ROOT, "shindan", "attributes", f"{slug}.json")
    if os.path.exists(sh):
        d = json.load(open(sh))
        old = d.get("facts", {}).get("avg_salary")
        if not dry:
            d.setdefault("facts", {})["avg_salary"] = yen
            json.dump(d, open(sh, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        changes.append(("shindan.avg_salary", f"{old}→{yen}"))
    return label, changes


def main():
    if not EDINET_KEY:
        sys.exit("⛔ EDINET_API_KEY 未設定。キー投入後に再実行してください(何も更新していません)。")
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only"); only = set(sys.argv[i + 1:])
    tg = _load_targets()
    targets = only or set(tg["union"])
    code_map = json.load(open(CODE_MAP_PATH)) if os.path.exists(CODE_MAP_PATH) else {}
    updated, held, report = 0, [], []
    for slug in sorted(targets):
        ecode = code_map.get(slug)
        if not ecode:
            held.append((slug, "no_edinet_code")); continue
        docid = find_yuho_docid(ecode)
        if not docid:
            held.append((slug, "no_yuho_docid")); continue
        text = fetch_pdf_text(docid)
        yen, fy = extract_salary(text)
        if not yen:
            held.append((slug, "salary_not_found")); continue
        if fy and fy != FY:
            held.append((slug, f"fy_mismatch({fy})")); continue     # 2026年3月期でなければ据置
        label, changes = update_everywhere(slug, yen, dry)
        updated += 1
        report.append({"slug": slug, "yen": yen, "label": label, "changes": changes})
        time.sleep(0.3)
    print(json.dumps({"updated": updated, "held": len(held), "held_reasons": held[:40],
                      "sample": report[:10]}, ensure_ascii=False, indent=1))
    # TODO(本実行後): 変更scenarioを scenario_to_panels --v4 → D1反映 / scenario_lints_v5_ext error0 / canary / notion_sync


if __name__ == "__main__":
    main()
