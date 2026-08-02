#!/usr/bin/env python3
"""EDINET有価証券報告書(一次情報・bot対策なし)から質的セクションを抽出し rendered_corpus.json へ追記。
対象: bot-wall/fact不足で公式HTMLが取れない上場社。source_url=EDINET直PDF(金融庁・公式一次)。
抽出: 沿革 / 事業の内容 / 従業員の状況 / 経営方針・対処すべき課題 / サステナビリティ / 研究開発。
usage: python build_edinet_corpus.py
"""
import os, re, json, subprocess, time

OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
PY = os.path.expanduser("~/oscar-ai/video-pipeline/venv/bin/python")
PDF = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{}.pdf"
DOCS = {
    "tdk": "S100YD2Y", "daiwa-house": "S100YAZ5", "jal": "S100YFIO",
    "takashimaya": "S100Y4X5", "isetan-mitsukoshi": "S100YD7C",
    "pola-orbis-hd": "S100XSDL", "suntory": "S100XSOR",
}
# (見出し正規表現, 抽出長) — 有報の質的散文セクション
SECTIONS = [
    (r"沿\s*革", 2500),
    (r"事業の内容", 5000),
    (r"従業員の状況", 1800),
    (r"経営方針、経営環境及び対処すべき課題等|経営方針、経営環境及び対処すべき課題", 5000),
    (r"サステナビリティに関する考え方及び取組|サステナビリティに関する考え方", 4000),
    (r"研究開発活動", 3000),
]
asof = time.strftime("%Y-%m-%d")


def extract_text(docid):
    tmp = f"/tmp/edinet_{docid}.pdf"
    if not os.path.exists(tmp) or os.path.getsize(tmp) < 10000:
        subprocess.run(["curl", "-sL", "--max-time", "90", "-A", "Mozilla/5.0",
                        "-o", tmp, PDF.format(docid)], capture_output=True, timeout=100)
    if not os.path.exists(tmp) or os.path.getsize(tmp) < 10000:
        return ""
    r = subprocess.run([PY, "-c",
                        "import fitz,sys;d=fitz.open(sys.argv[1]);print(chr(10).join(p.get_text() for p in d))", tmp],
                       capture_output=True, text=True)
    return r.stdout or ""


def main():
    for slug, docid in DOCS.items():
        text = extract_text(docid)
        if len(text) < 3000:
            print(f"  {slug:18} PDF抽出失敗({len(text)}字)"); continue
        text = re.sub(r"[ \t]+", " ", text)
        cf = os.path.join(OUT, slug, "rendered_corpus.json")
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        cache = json.load(open(cf)) if os.path.exists(cf) else {}
        cache = {u: v for u, v in cache.items() if "Access Denied" not in ((v.get("text") if isinstance(v, dict) else v) or "")[:60]}
        src = PDF.format(docid)
        added = 0
        for pat, ln in SECTIONS:
            m = re.search(pat, text)
            if not m:
                continue
            chunk = text[m.start():m.start() + ln].strip()
            # 数字だらけの表(主要な経営指標)を除外・散文密度チェック
            digits = len(re.findall(r"\d", chunk))
            if len(chunk) > 300 and digits / max(len(chunk), 1) < 0.35:
                label = re.sub(r"\\|\||\s", "", pat)[:12]
                cache[f"{src}#{label}"] = {"text": chunk[:8000], "as_of": asof}
                added += 1
        json.dump(cache, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
        chars = sum(len((v.get("text") if isinstance(v, dict) else v) or "") for v in cache.values())
        print(f"  {slug:18} docid={docid} EDINET節{added}追加 計{len(cache)}頁 {chars}字")


if __name__ == "__main__":
    main()
