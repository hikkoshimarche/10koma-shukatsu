#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corpus増強: 公式ドメインの質的ページ(会社概要/事業/理念/採用/沿革/サステナ)を
quiz_corpus.json / rendered_corpus.json(取得済) から locked v3 corpus へマージ。
不足は公式ドメインの想定パスを追加fetch。財務/IR/PDF/第三者(jiji/tdnet)は除外(Source-or-Silence)。
使い方: python3 augment_corpus.py <slug>   → 追加ページ数/文字数を返す。locked corpusをin-place増強。"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
FIN_URL = re.compile(r"/ir/|/ir$|financial|/library/|settlement|\.pdf|jiji|tdnet|equity\.|kabutan|"
                     r"minkabu|nikkei|/investor|yuho|securities-report|shareholders", re.I)
NONOFFICIAL = re.compile(r"wikipedia|\.ac\.jp|\.edu|prtimes|note\.com|ameblo|hatena|toyokeizai|"
                         r"diamond|president\.jp|newspicks|wantedly|itmedia|reuters|bloomberg", re.I)
QUAL_PATHS = ["/company/", "/company/about/", "/corporate/", "/about/", "/recruit/", "/saiyo/",
              "/company/philosophy/", "/philosophy/", "/company/vision/", "/vision/", "/mission/",
              "/sustainability/", "/csr/", "/company/history/", "/history/", "/business/",
              "/company/business/", "/company/profile/"]


import subprocess
QUAL_LINK_KW = ["company", "about", "corporate", "business", "service", "products", "philosophy",
                "vision", "mission", "idea", "value", "story", "culture", "recruit", "saiyo",
                "people", "sustainability", "csr", "outline", "message", "profile", "group",
                "aboutus", "principle", "brand", "strength", "domain"]


def _discover_qual_urls(dom):
    """公式サイトrootの生HTMLからnavの質的ページURLを発見(固定パスに無いサイト対応)。"""
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0", dom],
                           capture_output=True, timeout=35)
        html = r.stdout.decode("utf-8", "ignore")
    except Exception:
        return []
    host = re.sub(r"https?://", "", dom).split("/")[0]
    urls = []
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        h = m.group(1).split("#")[0].split("?")[0]
        if not any(k in h.lower() for k in QUAL_LINK_KW):
            continue
        full = h if h.startswith("http") else dom.rstrip("/") + "/" + h.lstrip("/")
        if host in full and not FIN_URL.search(full) and not NONOFFICIAL.search(full):
            if full not in urls:
                urls.append(full)
    return urls[:18]


def _official_domain(slug):
    """公式ドメインを推定: quiz_corpus/rendered_corpus の非財務・非第三者URLのホスト最頻。"""
    hosts = {}
    for f in ("quiz_corpus.json", "rendered_corpus.json"):
        p = os.path.join(OUT, slug, f)
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for u in (d.keys() if isinstance(d, dict) else []):
            if FIN_URL.search(u) or NONOFFICIAL.search(u):
                continue
            m = re.match(r"(https?://[^/]+)", u)
            if m:
                hosts[m.group(1)] = hosts.get(m.group(1), 0) + 1
    return max(hosts, key=hosts.get) if hosts else None


def augment(slug, do_fetch=True, seed_domain=None):
    lp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    locked = json.load(open(lp)) if os.path.exists(lp) else {}
    before_n = len(locked)
    added = {}
    # 1) 取得済corpusから公式・質的ページを回収
    for f in ("quiz_corpus.json", "rendered_corpus.json"):
        p = os.path.join(OUT, slug, f)
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for u, t in (d.items() if isinstance(d, dict) else []):
            if u in locked or FIN_URL.search(u) or NONOFFICIAL.search(u):
                continue
            if isinstance(t, str) and len(t) > 300:
                added[u] = t
    # 2) 公式ドメインの想定質的パスを追加fetch(不足補完)。seed_domain指定時はそれを優先。
    dom = seed_domain or _official_domain(slug)
    if do_fetch and dom:
        have = set(locked) | set(added)
        # (2a) 実サイトnavから発見したURL + (2b) 固定パス推測 の両方を試行
        cand = _discover_qual_urls(dom) + [dom.rstrip("/") + p for p in QUAL_PATHS]
        for u in cand:
            if u in have or u in added:
                continue
            try:
                body = q.fetch_url(u)
            except Exception:
                body = ""
            if body and len(body) > 500 and not re.search(r"決算|短信|有価証券報告|404|not found", body[:300], re.I):
                added[u] = body
    # マージ
    locked.update(added)
    json.dump(locked, open(lp, "w"), ensure_ascii=False)
    chars = sum(len(v) for v in added.values())
    return {"slug": slug, "official_domain": dom, "before_pages": before_n,
            "added_pages": len(added), "added_chars": chars, "total_pages": len(locked),
            "added_urls": list(added.keys())}


if __name__ == "__main__":
    for slug in [a for a in sys.argv[1:] if not a.startswith("-")]:
        r = augment(slug)
        print(f"{r['slug']}: 公式={r['official_domain']} 追加{r['added_pages']}ページ/{r['added_chars']}字 "
              f"(locked {r['before_pages']}→{r['total_pages']})")
        for u in r["added_urls"]:
            print("   +", u[:90])
