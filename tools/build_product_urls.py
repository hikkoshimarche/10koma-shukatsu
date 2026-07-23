#!/usr/bin/env python3
"""④ ファクトシート製品URLレジストリ: 各社の主力製品/事業セグメントごとに一次情報URL(+as_of)を記録。
headlessクロール回避の根本解決=factsheet側に製品→公式URLを構造化保持。⑤四半期鮮度リフレッシュの監視URL源。
源: (a)datasheet 事業/財務/沿革 factの検証済公式source_url(fact本文をラベルに), (b)rendered_corpusの解決済(非404)製品/事業ページ。
出力: output/<slug>/product_urls.json = {slug,name,as_of,items:[{label,url,kind,source,as_of}]}
非公式ソース(_NONOFFICIAL)は除外(Source-or-Silence)。引数slug限定(既定=rendered_corpus保有社=pilot)。
"""
import json, os, sys, re, glob, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_es_kit as G   # _NONOFFICIAL 流用(公式判定)
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")

# 404/非該当ページのレンダ本文マーカー(このいずれかを含む解決失敗頁は採らない)
_404 = re.compile(r"見つかりません|ページが削除|Not Found|指定のページ|お探しのページ|存在しません|ページはありません")
# URL末尾セグメントから種別を推定
_KIND = [("ir", re.compile(r"/ir/|/investor|/finance|financial|/library/|kessan|earnings|/stock", re.I)),
         ("product", re.compile(r"/product|/software|/hardware|/goods|/lineup|/service", re.I)),
         ("business", re.compile(r"/business|/segment|/company/|/profile|/about", re.I)),
         ("history", re.compile(r"/history|enkaku|/corporate", re.I))]
_SEC_LABEL = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}


def _kind_of(url):
    for k, rx in _KIND:
        if rx.search(url):
            return k
    return "official"


_QUESTION = re.compile(r"(は誰|は何|どれ|ですか|でしょうか|のはどこ|何年|いくつ|いくら)")


def _clean_label(fact, axis="事業", maxlen=40):
    """factの先頭句(コロン前 or 文頭40字)を製品/事業ラベルに。クイズ設問調の残骸は軸名にフォールバック。"""
    f = re.sub(r"\s+", " ", (fact or "")).strip()
    if _QUESTION.search(f):                     # 「〜は誰/何年」等の設問調残骸はラベルにしない
        return f"{axis}(一次情報)"
    m = re.match(r"^(.{4,40}?)[:：]", f)
    lab = m.group(1) if m else f[:maxlen]
    lab = lab.strip("　 ・-")
    if _QUESTION.search(lab) or len(lab) < 3:
        return f"{axis}(一次情報)"
    return lab


def build_one(slug):
    dp = os.path.join(OUT, slug, "datasheet.json")
    if not os.path.exists(dp):
        return None
    ds = json.load(open(dp))
    name = ds.get("name", slug)
    items, seen = [], set()

    # (a) datasheet fact の公式source_url
    for k, arr in (ds.get("sections", {}) or {}).items():
        axis = _SEC_LABEL.get(k, k)
        for it in (arr or []):
            if not isinstance(it, dict):
                continue
            url = (it.get("source_url") or "").strip()
            fact = it.get("fact") or ""
            if not url or not url.startswith("http"):
                continue
            if G._NONOFFICIAL.search(url):        # 非公式ソースは記録しない(Source-or-Silence)
                continue
            key = url
            if key in seen:
                continue
            seen.add(key)
            items.append({"label": f"{axis}: {_clean_label(fact, axis)}", "url": url,
                          "kind": _kind_of(url), "source": "datasheet", "as_of": it.get("as_of") or ""})

    # (b) rendered_corpus の解決済(非404)製品/事業ページ
    rc = os.path.join(OUT, slug, "rendered_corpus.json")
    if os.path.exists(rc):
        for url, v in (json.load(open(rc)) or {}).items():
            if not url.startswith("http") or url in seen:
                continue
            if G._NONOFFICIAL.search(url):
                continue
            text = v.get("text", "") if isinstance(v, dict) else (v or "")
            if len(text.strip()) < 300 or _404.search(text[:400]):   # 中身が薄い/404頁は不採用
                continue
            seen.add(url)
            items.append({"label": f"製品/事業ページ ({_kind_of(url)})", "url": url,
                          "kind": _kind_of(url), "source": "rendered",
                          "as_of": (v.get("as_of", "") if isinstance(v, dict) else "")})

    as_of = next((x["as_of"] for x in items if x.get("as_of")), "")
    out = {"slug": slug, "name": name, "as_of": as_of, "items": items,
           "counts": {"total": len(items), "datasheet": sum(1 for x in items if x["source"] == "datasheet"),
                      "rendered": sum(1 for x in items if x["source"] == "rendered"),
                      "by_kind": {k: sum(1 for x in items if x["kind"] == k) for k in ("ir", "product", "business", "history", "official")}}}
    json.dump(out, open(os.path.join(OUT, slug, "product_urls.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:  # 既定=rendered_corpus保有(pilot5)
        args = sorted(os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(OUT, "*/rendered_corpus.json")))
    print(f"対象 {len(args)}社", flush=True)
    for s in args:
        r = build_one(s)
        if not r:
            print(f"  SKIP {s}: datasheet無"); continue
        c = r["counts"]
        print(f"  {s:16} URL{c['total']:2} (ds{c['datasheet']}/rendered{c['rendered']}) 種別{ {k:v for k,v in c['by_kind'].items() if v} }", flush=True)


if __name__ == "__main__":
    main()
