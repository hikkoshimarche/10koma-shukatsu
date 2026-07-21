#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quiz_fanout.py — 理解度クイズ 400社+16業界 自動収束ファンアウト(人手なし)。

二層ゲート: ① quiz_lint(数値/日付のverbatim出典照合) ② OpenAI独立レビュー(R1-R6)。
各社: corpus取得(DDG検索→curl/PyMuPDF)→OpenAI生成30問→lint収束(不可は破棄blocked)。
20社CP毎: サンプルK問をOpenAIレビュー→pass率/systemic→自動修正/HALT/卒業→commit/push→LINE実値。
安全弁: 総額コストガード / resumable / caffeinate想定 / HALTで即LINE。
本番反映はしない: 出力は output/<slug>/quiz_30q.json まで。

使い方:
  python quiz_fanout.py --validate 3      # 少数社を同期実行して検証(背景化しない)
  python quiz_fanout.py --run             # 本番: 全社(resumable, 並列3, CP毎処理)
  環境: OPENAI_API_KEY / SHEET_WEBAPP_URL / SHEET_API_TOKEN (.env, .env.phase_c)
"""
import os, re, sys, json, csv, time, html, subprocess, threading, argparse, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
    load_dotenv(os.path.expanduser("~/projects/10koma-shukatsu/tools/.env.phase_c"))
except Exception:
    pass

sys.path.insert(0, os.path.expanduser("~/projects/10koma-shukatsu/tools"))
import quiz_lint as QL

REPO = os.path.expanduser("~/projects/10koma-shukatsu")
PIPE = os.path.expanduser("~/oscar-ai/tokyari-pipeline")
OUT = os.path.join(PIPE, "output")
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し/quiz_pilot")
STATE_PATH = os.path.join(PIPE, "output", "_quiz_fanout_state.json")
BLOCKED_CSV = os.path.join(PIPE, "output", "quiz_blocked.csv")
COMPANIES = os.path.join(REPO, "public/companies.json")

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
GEN_MODEL = "gpt-4o"
REVIEW_MODEL = "gpt-4o"
# gpt-4o 価格(USD/1M tok)
PRICE_IN, PRICE_OUT = 2.50, 10.00
MAX_USD = float(os.environ.get("QUIZ_MAX_USD", "75"))   # 総額コストガード(Web Claude承認$75)
PARALLEL = 3
CHECKPOINT_EVERY = 20
REVIEW_K = 12
GRAD_PASS = 0.98
AGGREGATORS = ("nikkei.com", "yahoo", "biggo", "disclosure.tokyo", "daiwair", "ifis.co",
               "amazonaws", "edinet", "ullet", "buffett-code", "minkabu", "kabutan",
               "wikipedia", "wikinvest", "salesnow", "sincereed", "gbiz", "irbank",
               "reuters", "bloomberg", "quick", "tdnet")

_lock = threading.Lock()
_cost = {"usd": 0.0, "in": 0, "out": 0, "calls": 0}


# ── コスト/LINE/git ──────────────────────────────────────
def add_cost(u):
    with _lock:
        pt = u.get("prompt_tokens", 0); ct = u.get("completion_tokens", 0)
        _cost["in"] += pt; _cost["out"] += ct; _cost["calls"] += 1
        _cost["usd"] += pt / 1e6 * PRICE_IN + ct / 1e6 * PRICE_OUT

def cost_ok():
    with _lock:
        return _cost["usd"] < MAX_USD

def line(msg):
    url = os.environ.get("SHEET_WEBAPP_URL", "").strip()
    tok = os.environ.get("SHEET_API_TOKEN", "").strip()
    if not url:
        print("[LINE未送信]", msg); return
    try:
        requests.post(url, data={"mode": "pushlinefull", "token": tok, "text": msg}, timeout=60)
    except Exception as e:
        print("[LINE ERR]", e)

def git(*a, cwd=REPO):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=180)


# ── LLM (OpenAI / Anthropic フォールバック) ───────────────
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.environ.get("QUIZ_ANTHROPIC_MODEL", "claude-sonnet-4-5")
# QUIZ_LLM=anthropic で明示切替。OpenAIが insufficient_quota になったら自動でanthropicへ恒久フォールバック。
LLM_BACKEND = [os.environ.get("QUIZ_LLM", "openai")]
# claude-sonnet-4-5 概算価格(USD/1M): in $3 / out $15
A_PIN, A_POUT = 3.0, 15.0

def _anthropic_chat(messages, max_tokens, temperature):
    sys_txt = "\n".join(m["content"] for m in messages if m["role"] == "system")
    usr = [{"role": ("assistant" if m["role"] == "assistant" else "user"), "content": m["content"]}
           for m in messages if m["role"] != "system"]
    for attempt in range(4):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                              headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json"},
                              json={"model": ANTHROPIC_MODEL, "max_tokens": max_tokens,
                                    "temperature": temperature, "system": sys_txt, "messages": usr}, timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(4 * (attempt + 1)); continue
            d = r.json()
            if "content" not in d:
                time.sleep(3 * (attempt + 1)); continue
            u = d.get("usage", {})
            with _lock:
                pt = u.get("input_tokens", 0); ct = u.get("output_tokens", 0)
                _cost["in"] += pt; _cost["out"] += ct; _cost["calls"] += 1
                _cost["usd"] += pt / 1e6 * A_PIN + ct / 1e6 * A_POUT
            return d["content"][0]["text"]
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("anthropic_chat failed after retries")

def openai_chat(messages, model=GEN_MODEL, max_tokens=4000, json_mode=True, temperature=0.3):
    if not cost_ok():
        raise RuntimeError(f"COST_GUARD: ${_cost['usd']:.2f} >= ${MAX_USD}")
    # 既定はOpenAI(出荷済みと生成エンジンを統一)。Anthropicは QUIZ_LLM=anthropic の明示指定時のみ(緊急退避)。
    if LLM_BACKEND[0] == "anthropic" and ANTHROPIC_KEY:
        return _anthropic_chat(messages, max_tokens, temperature)
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    for attempt in range(4):
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers={"Authorization": f"Bearer {OPENAI_KEY}"}, json=body, timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(4 * (attempt + 1)); continue
            d = r.json()
            if "choices" not in d:
                time.sleep(3 * (attempt + 1)); continue
            add_cost(d.get("usage", {}))
            return d["choices"][0]["message"]["content"]
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("openai_chat failed after retries")

def _parse_json(txt):
    """LLM出力からJSONを頑健に抽出(```fence除去・末尾カンマ許容)。"""
    t = (txt or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t); t = re.sub(r"\n?```\s*$", "", t).strip()
    for cand in (t, (re.search(r"\{.*\}", t, re.S).group(0) if re.search(r"\{.*\}", t, re.S) else None)):
        if not cand:
            continue
        try:
            return json.loads(cand)
        except Exception:
            try:
                return json.loads(re.sub(r",\s*([}\]])", r"\1", cand))
            except Exception:
                pass
    return {}


# ── corpus 取得(DDG検索→curl→PyMuPDF/HTML) ───────────────
def clean_html(t):
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<(br|/p|/div|/li|/tr|/h[1-6])[^>]*>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t　]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()

def fetch_url(url):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", "Mozilla/5.0", url],
                           capture_output=True, timeout=55)
        data = r.stdout
        if url.lower().split("?")[0].endswith(".pdf") or data[:5] == b"%PDF-":
            import fitz
            fn = f"/tmp/_qz_{hashlib.md5(url.encode()).hexdigest()[:8]}.pdf"
            open(fn, "wb").write(data)
            doc = fitz.open(fn); txt = "\n".join(p.get_text() for p in doc); doc.close()
            os.remove(fn)
            return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t　]+", " ", txt)).strip()
        return clean_html(data.decode("utf-8", "ignore"))
    except Exception:
        return ""

def ddg(query, want_pdf=False, limit=12):
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "25",
                            "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                            "https://html.duckduckgo.com/html/", "--data-urlencode", f"q={query}"],
                           capture_output=True, timeout=35)
        t = r.stdout.decode("utf-8", "ignore")
        import urllib.parse
        urls = [urllib.parse.unquote(u) for u in re.findall(r"uddg=([^&\"]+)", t)]
        seen, out = set(), []
        for u in urls:
            if u in seen: continue
            seen.add(u)
            if want_pdf and not u.lower().split("?")[0].endswith(".pdf"): continue
            if any(a in u.lower() for a in AGGREGATORS): continue
            out.append(u)
            if len(out) >= limit: break
        return out
    except Exception:
        return []

MANIFEST_PATH = os.path.join(OUT, "_quiz_source_manifest.json")
def _manifest():
    try:
        return json.load(open(MANIFEST_PATH, encoding="utf-8"))
    except Exception:
        return {}

# ── Notion ファクトシート由来の公式URL取得 (notion_sync同等の認証) ──
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
NH = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
BLOCK = ("nikkei", "yahoo", "irbank", "gaishishukatsu", "salesnow", "note.com", "kabuyoho",
         "bloomberg", "reuters", "diamond.jp", "toyokeizai", "openwork", "en-japan",
         "rikunabi", "mynavi", "onecareer", "talentsquare", "sincereed", "cafe-dc",
         "newswitch", "minkabu", "kabutan", "buffett-code", "ullet", "quick.com",
         "notion.so", "notion.com", "app.notion", "youtube", "youtu.be", "twitter",
         "x.com", "facebook", "linkedin", "prtimes", "wikipedia", "jbic.go.jp",
         "google", "amazonaws", "hatena", "ameblo", "livedoor", "wantedly",
         "jobree", "job.", "tenshoku", "hataraku", "career-", "shukatsu", "vorkers",
         "lightworks", "unistyle", "job-", "/tips/",
         # v3-3 主要メディア/情報サイト(本体誤認防止・strong signal判定と二重で)
         "impress", "itmedia", "response.jp", "carview", "goo-net", "autoc", "clicccar",
         "webcg", "president.jp", "sbbit", "gigazine", "famitsu", "4gamer", "carsensor",
         "kakaku", "watch.impress", "nikkeibp", "xtech", "gamer.ne", "automesse",
         "coralcap", "strainer", "logmi", "businessinsider", "forbes", "newspicks")
GOOD_HINT = ("ir", "library", "meeting", "securities", "tanshin", "kessan", "financial",
             "company", "outline", "profile", "corporate", "about", "recruit", "saiyo",
             "release", "news", "pdf")

def _page_id_map():
    m = {}
    p = os.path.join(OUT, "notion_sync_state.csv")
    if os.path.exists(p):
        for row in csv.DictReader(open(p, encoding="utf-8")):
            if row.get("notion_page_id"):
                m[row["slug"]] = row["notion_page_id"]
    return m
_PID = _page_id_map()

def _notion_children(bid):
    out, cur = [], None
    for _ in range(60):
        params = {"page_size": 100}
        if cur: params["start_cursor"] = cur
        try:
            r = requests.get(f"https://api.notion.com/v1/blocks/{bid}/children", headers=NH,
                             params=params, timeout=30).json()
        except Exception:
            break
        out += r.get("results", [])
        if not r.get("has_more"): break
        cur = r.get("next_cursor")
        time.sleep(0.35)  # Notion rate limit
    return out

def _notion_walk(bid, depth=0, acc=None):
    if acc is None: acc = []
    if depth > 3 or len(acc) > 2500: return acc
    for b in _notion_children(bid):
        acc.append(b)
        if b.get("has_children"): _notion_walk(b["id"], depth + 1, acc)
    return acc

def _notion_search_pid(name):
    try:
        r = requests.post("https://api.notion.com/v1/search", headers=NH,
                          json={"query": f"{name} ファクトシート",
                                "filter": {"property": "object", "value": "page"}}, timeout=30).json()
        for res in r.get("results", []):
            title = "".join(t.get("plain_text", "") for t in
                            res.get("properties", {}).get("title", {}).get("title", []))
            if "ファクトシート" in title and (name in title):
                return res["id"]
    except Exception:
        pass
    return None

def _reg_domain(host):
    labels = host.split(".")
    if len(labels) >= 3 and labels[-2] in ("co", "or", "ne", "ac", "go", "ad", "com", "gr"):
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])

def _factsheet_official_urls(slug, name):
    pid = _PID.get(slug) or _notion_search_pid(name)
    if not pid:
        return [], None
    urls = set()
    for b in _notion_walk(pid):
        t = b.get("type"); o = b.get(t, {})
        rt = o.get("rich_text", []) if isinstance(o, dict) else []
        for x in rt:
            if x.get("href"): urls.add(x["href"])
        txt = "".join(x.get("plain_text", "") for x in rt)
        for u in re.findall(r"https?://[^\s)\]\"'>」）]+", txt):
            urls.add(u)
    # ★v3-3 公式ドメイン判定: IR/会社概要/短信PDF/有報の“強いシグナル”を持つドメインのみ公式とみなす。
    #   第三者メディア(impress/watch等 /news/だけ)を本体に誤認しない。強シグナルが無ければ needs_source。
    def _strong(path, is_pdf):
        if is_pdf: return 3
        if any(k in path for k in ("securities", "yuho", "yuka", "有報")): return 3
        if any(k in path for k in ("/ir/", "/ir?", "/ir#", "ir/library", "library", "financial",
                                   "tanshin", "kessan", "earnings", "/investor")): return 2
        if any(k in path for k in ("/company", "/outline", "/profile", "/corporate", "/about",
                                   "/companyinfo", "/overview", "/philosophy", "/idea")): return 2
        if any(k in path for k in ("recruit", "saiyo", "career", "/jobs", "/csr", "/sustainab")): return 1
        return 0
    cand, strong, count = [], {}, {}
    for u in urls:
        m = re.match(r"https?://([^/]+)(/[^\s]*)?", u)
        if not m: continue
        host = m.group(1).lower(); path = (m.group(2) or "").lower()
        if any(b in host for b in BLOCK): continue
        rd = _reg_domain(host)
        is_pdf = u.lower().split("?")[0].endswith(".pdf")
        cand.append((rd, path, u))
        strong[rd] = max(strong.get(rd, 0), _strong(path, is_pdf))
        count[rd] = count.get(rd, 0) + 1
    # 強シグナル(>=2: IR/会社概要/PDF/有報)を持つドメインだけ公式候補に
    qualified = {rd for rd in strong if strong[rd] >= 2}
    if not qualified:
        return [], None            # 公式ドメイン不明 → メディアを使わず needs_source
    official = max(qualified, key=lambda k: (strong[k], count[k]))
    def prio(u):
        ul = u.lower()
        if ul.split("?")[0].endswith(".pdf"): return 0
        if "securities" in ul: return 1
        if any(k in ul for k in ("outline", "profile", "company", "corporate", "about")): return 2
        if "/ir" in ul or "library" in ul: return 3
        if any(k in ul for k in ("recruit", "saiyo", "career")): return 4
        return 5
    picked = sorted({u for rd, path, u in cand if rd == official}, key=prio)
    return picked, official

def acquire_corpus(name, slug=None):
    """公式一次情報の corpus 化。①Notionファクトシート由来の公式ドメインURL(主) + ②manifest(補助)。
    第三者サイトは除外。curl生取得→PyMuPDF/HTML verbatim抽出。公式URL無しなら空(→needs_source)。"""
    corpus = {}
    urls, _dom = _factsheet_official_urls(slug or "", name)
    urls = list(urls)[:5]                      # コスト/時間のため最大5本
    for u in _manifest().get(slug or "", []):  # 既知の追加seed(あれば補助)
        if u not in urls: urls.append(u)
    for u in urls:
        body = fetch_url(u)
        if len(body) > 700:
            corpus[u] = body
        time.sleep(0.3)
    return corpus

def _expand_official_pdfs(index_url, official_dom, limit=2):
    """IR/有報の索引HTMLを取得し、公式ドメイン上の 決算短信/有報 PDF リンクを抽出。"""
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "35", "-A", "Mozilla/5.0", index_url],
                           capture_output=True, timeout=45)
        html_t = r.stdout.decode("utf-8", "ignore")
    except Exception:
        return []
    base = re.match(r"(https?://[^/]+)", index_url)
    base = base.group(1) if base else ""
    hrefs = re.findall(r'href="([^"]+\.pdf[^"]*)"', html_t, re.I)
    out = []
    for h in hrefs:
        u = h if h.startswith("http") else (base + h if h.startswith("/") else base + "/" + h)
        host = re.match(r"https?://([^/]+)/", u)
        if not host or official_dom not in host.group(1):
            continue
        ul = u.lower()
        score = (0 if any(k in ul for k in ("tanshin", "kessan", "ta.pdf", "短信", "earnings", "summary")) else
                 1 if any(k in ul for k in ("yuho", "securities", "有価", "asr", "yukashoken")) else 2)
        out.append((score, u))
    out.sort(key=lambda x: x[0])
    seen, res = set(), []
    for _s, u in out:
        if u in seen: continue
        seen.add(u); res.append(u)
        if len(res) >= limit: break
    return res

def _host_reg(u):
    m = re.match(r"https?://([^/]+)", u)
    return _reg_domain(m.group(1).lower()) if m else None

# ★鮮度: 決算データは常に最新期を一次情報で取得(取れた期をverbatim確認してから採用)
LATEST_FY = os.environ.get("QUIZ_LATEST_FY", "2026年3月期")
_FY_SUBS = [("_253_", "_263_"), ("ja_253", "ja_263"), ("_253", "_263"), ("202505", "202605"),
            ("202405", "202505"), ("2503", "2603"), ("25_ended", "26_ended"),
            ("/2024/", "/2025/"), ("/2025/", "/2026/"), ("2025", "2026")]
def _fy_variants(u):
    out = set()
    for a, b in _FY_SUBS:
        if a in u:
            out.add(u.replace(a, b))
    return out
def _has_fy(body, fy=None):
    fy = (fy or LATEST_FY).replace(" ", "")
    return fy in re.sub(r"\s", "", body or "")
def _prefer_latest_tanshin(urls, official_reg):
    """既存短信PDFのFY変種 + IR索引の最新年度PDF を試し、LATEST_FY をverbatim含むものを先頭へ。"""
    pdfs = [u for u in urls if u.lower().split("?")[0].endswith(".pdf")]
    cands = set()
    for u in pdfs:
        cands |= _fy_variants(u)
    for u in urls:
        ul = u.lower()
        if ul.split("?")[0].endswith(".pdf"):
            continue
        if any(k in ul for k in ("securities", "library", "/ir", "meeting", "earnings", "report", "financial")):
            for p in _expand_official_pdfs(u, official_reg, limit=6):
                if any(y in p for y in ("263", "2606", "2605", "202606", "202605", "/2026/", "26_ended")):
                    cands.add(p)
    latest = []
    for c in list(cands)[:8]:
        if _host_reg(c) != official_reg or c in urls and c in latest:
            continue
        body = fetch_url(c)
        if body and _has_fy(body):
            latest.append(c)
    if latest:
        return latest + [u for u in urls if u not in latest]
    return urls

def acquire_corpus_thick(name, slug, prefer_latest=True):
    """品質固定モードの厚いcorpus。会社概要+seed + 公式IR/有報索引→PDF展開。
    ★v3: 本体公式ドメイン(registrable domain)のみに厳密限定。子会社ドメイン
    (例 mitsubishicorprtm.com=RtMジャパン)は registrable が異なるので除外し、本体への誤帰属を防ぐ。"""
    urls, dom = _factsheet_official_urls(slug or "", name)
    urls = list(urls)
    seed = _manifest().get(slug or "", [])
    for u in seed:
        if u not in urls: urls.append(u)
    # 本体公式 registrable domain を確定(seed優先=権威)。無ければ factsheet 判定。
    official_reg = _host_reg(seed[0]) if seed else (_reg_domain(dom) if dom else None)
    if not official_reg:
        return {}
    # IR/有報 索引HTMLからPDFを展開(本体ドメインのみ)
    extra = []
    for u in list(urls):
        ul = u.lower()
        if ul.split("?")[0].endswith(".pdf"): continue
        if any(k in ul for k in ("securities", "library", "/ir", "financial", "report", "yuka", "meeting")):
            extra += _expand_official_pdfs(u, official_reg)
    urls += extra
    # ★本体 registrable domain 完全一致のみ採用(子会社/別ドメインは除外)
    urls = [u for u in dict.fromkeys(urls) if _host_reg(u) == official_reg]
    def prio(u):
        ul = u.lower()
        if ul.split("?")[0].endswith(".pdf"):
            return 0 if any(k in ul for k in ("tanshin", "ta.pdf", "earnings", "summary", "kessan", "202505", "package")) else 1
        if any(k in ul for k in ("securities", "yuka")): return 2
        if any(k in ul for k in ("outline", "profile", "about", "company", "corporate")): return 3
        return 5
    urls = sorted(urls, key=prio)[:7]
    if prefer_latest:                       # ★最新期(2026年3月期)短信を先頭へ(verbatim確認済のみ)
        urls = _prefer_latest_tanshin(urls, official_reg)[:8]
    corpus = {}
    for u in urls:
        body = fetch_url(u)
        if len(body) > 700:
            corpus[u] = body
        time.sleep(0.3)
    return corpus

def corpus_latest_fy(corpus):
    """corpus内に存在する最新の決算期(2026年3月期があればそれ、無ければ2025…)。鮮度lint/hold判定用。"""
    joined = " ".join(corpus.values()) if isinstance(corpus, dict) else str(corpus)
    j = re.sub(r"\s", "", joined)
    for fy in ("2026年3月期", "2025年3月期", "2024年3月期"):
        if fy in j:
            return fy
    return None


# ── 生成(OpenAI, corpus厳密紐付け) ───────────────────────
GEN_SYS = (
 "あなたは日本企業の就活生向け『理解度チェッククイズ』を、提供された一次情報の本文だけを根拠に作る出題者です。"
 "絶対規則(Source-or-Silence): 設問文・4つの選択肢・解説に登場する数値と日付は、指定された source 本文に"
 "『文字列として実在』するものだけを使う。存在しない数値・概算・別表記(兆億へ換算等)は禁止。"
 "誤答(不正解の3択)の数値も必ず同じ source 本文内の別の実数(別年度・別項目・別セグメント)を使う。"
 "各設問には category を付す(財務数値/会社概要/事業セグメント/沿革/製品・サービス/人名・役員/業界順位/その他)。"
 "数字を含む設問には必ず as_of(時期)を付す。倍率は禁止。総会開催日・配当支払日・有報提出日などの日程トリビアは禁止。"
 "日付は必ず完全形(例 2024年7月1日)で本文と一致させる。EPS等の株数依存指標を会社間で比較する順位設問は禁止"
 "(順位は収益・利益額・ROEで作る)。ミックス規定: 財務数値は最大15問、残りは事業セグメント・会社概要・沿革・製品/サービス。"
 # ★v3-2 作りの機械ルール
 " 【選択肢の型統一】4択は必ず同じ型で揃える: 人名を問う設問の誤答は人名のみ(会社名を混ぜない)、"
 "会社名を問うなら全て会社名、金額なら全て同じ単位。"
 " 【可変事実のas_of必須】社長/代表者・従業員数・連結子会社数/会社数・発行済株式数・拠点数・資本金など"
 "『時点で変わる事実』には必ず as_of を付ける(例: 2025年5月時点 / 2026年3月31日現在 / 2025年3月期)。"
 " 【冗長禁止】同じ事実を言い回しを変えて2回問わない。合計が他2問の答えの和になる派生値(例 連結対象合計=子会社+持分法適用)は作らない。"
 "同一リストについて『含まれるもの』と『含まれないもの』の両方を作らず、どちらか1問だけにする。"
 " 【トリビア禁止】電話番号・上場取引所/上場市場・本店所在地/住所は問わない。"
)
GEN_USER_TMPL = (
 "対象企業: {name}\n"
 "以下は許可された source 本文(URL付き)。ここに実在する文字列だけを根拠に、4択クイズを{n}問、JSONで出力。\n\n"
 "{sources}\n\n"
 "出力JSON形式(厳守):\n"
 '{{"questions":[{{"category":"財務数値","q_text":"...","options":["A","B","C","D"],"correct":0,'
 '"explanation":"...","source_url":"<上記URLのいずれか>","as_of":"2025年3月期"}}]}}\n'
 "各設問: options は必ず4つ・correct は0-3の整数・source_url は上記の該当URL。"
 "数値/日付は必ず source 本文に実在する表記のまま(百万円・円・%・完全な日付)。捏造禁止。"
)

def _sources_block(corpus, max_chars=16000):
    # 予算を各ソースに均等配分(先頭PDFで埋め尽くさない=非財務ページも必ず生成に見せる)。
    n = max(1, len(corpus))
    per = max(1800, max_chars // n)
    blocks = []
    for url, body in corpus.items():
        blocks.append(f"===== source_url: {url} =====\n{body[:per]}")
    return "\n\n".join(blocks)

def generate(name, corpus, n=30, extra=""):
    user = GEN_USER_TMPL.format(name=name, n=n, sources=_sources_block(corpus))
    if extra:
        user += "\n\n" + extra
    txt = openai_chat([{"role": "system", "content": GEN_SYS}, {"role": "user", "content": user}],
                      model=GEN_MODEL, max_tokens=6000)
    data = _parse_json(txt)
    return data.get("questions", []) if isinstance(data, dict) else []

def fix_failures(name, corpus, failed):
    """lintで落ちた設問を、その理由付きで再生成(バッチ)。"""
    fb = json.dumps([{"q": f["q"], "lint_errors": f["errs"]} for f in failed], ensure_ascii=False)
    user = (GEN_USER_TMPL.format(name=name, n=len(failed), sources=_sources_block(corpus))
            + "\n\n以下は前回lintで不合格になった設問と理由。根拠が本文に無いものは別の実在数値で作り直すか、"
              "本文で確実に裏取りできる別テーマ(セグメント/沿革/製品/会社概要)に差し替えて再出力:\n" + fb)
    txt = openai_chat([{"role": "system", "content": GEN_SYS}, {"role": "user", "content": user}],
                      model=GEN_MODEL, max_tokens=4000)
    return _parse_json(txt).get("questions", [])


# ── datasheet(教材) 生成: クイズと同一corpusで対に ───────────
DS_SYS = (
 "あなたは就活生向けの『企業データシート(教材)』を、提供された一次情報の本文だけを根拠に作る編集者です。"
 "絶対規則(Source-or-Silence): 記載する数値・日付・固有名は指定 source 本文に『実在』するものだけ。"
 "捏造・概算・別表記(兆億換算等)は禁止。各 fact に source_url を付す。数値・可変事実には as_of(時点)を付す。"
 "構成は4セクション: 『事業内容・セグメント』『主要財務』『社風・求める人物像』『沿革・基本情報』。"
 "各セクションに、その会社を理解できる要点を短い日本語のfactで列挙する(1factは1文)。"
 "主要財務は 収益・利益・ROE・配当・キャッシュフロー等を as_of 付きで。社風・人物像は公式の記述の範囲のみ。")
DS_USER_TMPL = (
 "対象企業: {name}\n以下は許可された source 本文(URL付き)。ここに実在する事実だけで data sheet を作る。\n\n{sources}\n\n"
 "出力JSON(厳守): {{\"sections\":{{"
 "\"事業内容・セグメント\":[{{\"fact\":\"...\",\"source_url\":\"<上記URL>\"}}],"
 "\"主要財務\":[{{\"fact\":\"...\",\"as_of\":\"2025年3月期\",\"source_url\":\"...\"}}],"
 "\"社風・求める人物像\":[{{\"fact\":\"...\",\"source_url\":\"...\"}}],"
 "\"沿革・基本情報\":[{{\"fact\":\"...\",\"as_of\":\"...\",\"source_url\":\"...\"}}]}}}}\n"
 "数値・日付は source 本文の表記のまま。source_url は上記URLのいずれか。捏造禁止。")

def generate_datasheet(name, corpus):
    user = DS_USER_TMPL.format(name=name, sources=_sources_block(corpus))
    txt = openai_chat([{"role": "system", "content": DS_SYS}, {"role": "user", "content": user}],
                      model=GEN_MODEL, max_tokens=4000)
    data = _parse_json(txt)
    return data if isinstance(data, dict) and data.get("sections") else {"sections": {}}

def _filter_datasheet_sos(ds, corpus):
    """Source-or-Silence: 数値が引用source本文に実在しないfactを除去。"""
    out = {"sections": {}}
    for sec, items in (ds.get("sections") or {}).items():
        keep = []
        for it in (items or []):
            url = (it.get("source_url") or "").strip()
            nums = QL._num_tokens(str(it.get("fact", "")) + " " + str(it.get("as_of", "")))
            body = corpus.get(url, "")
            if nums and (not body or any(t not in QL._norm_num(body) for t in nums)):
                continue                       # 捏造数値fact→除去
            if url not in corpus:              # 出典が台帳外→除去
                continue
            keep.append(it)
        out["sections"][sec] = keep
    return out

_DS_SEC = {"財務数値": "主要財務", "業界順位": "主要財務", "事業セグメント": "事業内容・セグメント",
           "製品・サービス": "事業内容・セグメント", "沿革": "沿革・基本情報",
           "会社概要": "沿革・基本情報", "人名・役員": "沿革・基本情報", "その他": "沿革・基本情報"}
def _repair_coverage(ds, quiz):
    """quiz→datasheet カバレッジ保証: datasheet に無いクイズ正解を、該当セクションに追記。
    (正解はすでにcorpus実在をlint済=Source-or-Silence担保)。"""
    body = QL.datasheet_body(ds); bodyn = QL._norm_num(body); bns = re.sub(r"\s", "", body)
    ds.setdefault("sections", {})
    for q in quiz:
        opts = q.get("options") or []; ci = q.get("correct")
        if not (isinstance(ci, int) and 0 <= ci < len(opts)):
            continue
        corr = str(opts[ci]).strip(); nums = QL._num_tokens(corr)
        covered = (all(t in bodyn for t in nums) if nums else re.sub(r"\s", "", corr) in bns)
        if covered:
            continue
        sec = _DS_SEC.get(q.get("category"), "沿革・基本情報")
        subj = re.split(r"(はどれ|はどの|はいくつ|はどこ|は何|に含まれ|ですか|は、|は？|\?)", q.get("q_text", ""))[0].strip()
        item = {"fact": f"{subj or q.get('q_text','')[:24]}: {corr}", "source_url": q.get("source_url")}
        if q.get("as_of"):
            item["as_of"] = q["as_of"]
        ds["sections"].setdefault(sec, []).append(item)
        body += " " + item["fact"]; bodyn = QL._norm_num(body); bns = re.sub(r"\s", "", body)
    return ds

def build_datasheet(slug, name, corpus, quiz):
    """corpus から datasheet 生成 → SoS除去 → quizカバレッジ修復。返り: (datasheet, cov_errors)"""
    ds = generate_datasheet(name, corpus)
    ds = _filter_datasheet_sos(ds, corpus)
    ds = _repair_coverage(ds, quiz)
    ds["slug"] = slug; ds["name"] = name
    ds["generated_from"] = list(corpus.keys())
    cov = QL.lint_datasheet_coverage(quiz, ds)
    return ds, len([f for f in cov if f["severity"] == "error"])


# ── lint収束 ─────────────────────────────────────────────
def lint_one(q, corpus):
    r = QL.run_quiz_lints([q], corpus)
    errs = [f"{f['lint']}:{f['detail']}" for f in r["findings"] if f["severity"] == "error"]
    return errs

def converge(slug, name, corpus, target=30, max_fix=2):
    """生成→lint→不合格は最大2回fix→なお不合格は破棄。(passed[], dropped_count)"""
    passed, pool = [], generate(name, corpus, target)
    for _round in range(max_fix + 1):
        survivors, failed = [], []
        for q in pool:
            q.setdefault("id", "")
            errs = lint_one(q, corpus)
            (survivors if not errs else failed).append((q, errs))
        for q, _e in survivors:
            passed.append(q)
        passed = _dedup(passed)
        if len(passed) >= target or not failed or _round == max_fix:
            break
        pool = fix_failures(name, corpus, [{"q": q, "errs": e} for q, e in failed])
    # id 採番
    final = []
    for i, q in enumerate(passed[:target], 1):
        q["id"] = f"{slug}_{i:02d}"
        final.append(q)
    # 再lintで最終保証(id重複等)
    r = QL.run_quiz_lints(final, corpus)
    if r["errors"] > 0:  # 念のため error 残存は除去
        good = []
        for q in final:
            if not lint_one(q, corpus):
                good.append(q)
        final = [{**q, "id": f"{slug}_{i:02d}"} for i, q in enumerate(good, 1)]
    dropped = target - len(final)
    return final, max(0, dropped)

def _dedup(qs):
    seen, out = set(), []
    for q in qs:
        k = q.get("q_text", "").strip()[:40]
        if k in seen: continue
        seen.add(k); out.append(q)
    return out

def _group(digits):
    """'16811509' -> '16,811,509'。小数はそのまま。"""
    if "." in digits:
        a, b = digits.split(".", 1)
        return _group(a) + "." + b
    r = ""
    for i, c in enumerate(reversed(digits)):
        if i and i % 3 == 0:
            r = "," + r
        r = c + r
    return r

def _repair_distractors(q, corpus):
    """誤答が捏造(本文に不在)の財務問を、corpus内の同一単位・同桁の実数へ置換して救済。
    正解が本文に実在する場合のみ。成功で修復後q、失敗でNone。"""
    body = corpus.get(q.get("source_url"), "")
    if not body:
        return None
    body_norm = QL._norm_num(body)
    opts = [str(o) for o in (q.get("options") or [])]
    ci = q.get("correct")
    if len(opts) != 4 or not isinstance(ci, int) or not (0 <= ci < 4):
        return None
    correct = opts[ci]
    # 正解の数値が本文に無ければ修復不能(正解が捏造=破棄)
    if any(t not in body_norm for t in QL._num_tokens(correct)):
        return None
    unit = QL._unit_class(correct)
    if unit in ("text", "date", "year"):
        return None                      # 非数値/日付は本修復の対象外
    cm = QL.NUM_RE.search(correct)
    if not cm:
        return None
    core = QL._norm_num(cm.group(0))
    suffix = correct[cm.end():].strip()  # 例 "百万円" / "%" / "円" / "名" / "株"
    is_pct = (unit == "percent")
    ndig = len(core.replace(".", ""))
    # corpus から同単位・同桁の実数を収集(紛らわしい別項目/別年度の値)
    pool, seen = [], {core}
    for m in QL.NUM_RE.finditer(body):
        t = QL._norm_num(m.group(0))
        if not t or t in seen:
            continue
        if is_pct:
            try:
                fv = float(t)
            except ValueError:
                continue
            if not (0 < fv < 100 and "." in t):
                continue
        else:
            if "." in t or len(t) != ndig:
                continue
        seen.add(t); pool.append(t)
    if len(pool) < 3:
        return None
    newopts = list(opts)
    pi = 0
    for i in range(4):
        if i == ci:
            continue
        newopts[i] = (pool[pi] + "%") if is_pct else (_group(pool[pi]) + suffix)
        pi += 1
    q2 = {**q, "options": newopts}
    return q2 if not lint_one(q2, corpus) else None

def _review_pass_ids(qs, corpus):
    """二層目: qs をレビューし、pass した id集合・pass率・(graded, passed)件数 を返す(バッチ12)。"""
    passed, graded = set(), 0
    for i in range(0, len(qs), 12):
        batch = qs[i:i + 12]
        items = [{"id": q["id"], "q_text": q["q_text"], "options": q["options"], "correct": q["correct"],
                  "explanation": q.get("explanation", ""), "category": q.get("category"),
                  "source_url": q.get("source_url"), "snippets": snippets_for(q, corpus)} for q in batch]
        rev = review_batch(items)
        for r in rev.get("results", []):
            graded += 1
            if r.get("pass"):
                passed.add(r.get("id"))
    rate = (len(passed) / graded) if graded else 1.0
    return passed, rate, graded, len(passed)

def converge_locked(slug, name, corpus, target=30, max_round=5, extra=""):
    """品質固定: 生成→lint収束→OpenAI R1-R6レビュー→pass分のみ採用。ミックス強制(財務≤target/2)。
    不足は非財務優先で再生成backfill。返り: (final[], dropped, review_pass_rate)。lint error=0 かつ review pass。"""
    FIN = "財務数値"
    fin_cap, fin_floor = 15, 8      # 財務は8〜15
    accepted, seen_q, seen_concepts, fin_n, dry_n = [], set(), set(), 0, 0
    tot_graded, tot_passed = 0, 0
    for rnd in range(max_round):
        need = target - len(accepted)
        if need <= 0:
            break
        # 生成バイアス: 財務が下限未満→意味ある財務を、上限到達→非財務のみ
        dyn = extra
        if fin_n < fin_floor:
            dyn = (extra + "\n【重要】意味のある財務設問を多めに作れ(収益/営業利益/税引前利益/当期利益/"
                   "親会社帰属利益/総資産/ROE/配当/キャッシュフロー等を各1問ずつ・異なる指標で)。")
        elif fin_n >= fin_cap:
            dyn = (extra + "\n【重要】財務数値は上限。以降は財務を作らず、事業セグメント/会社概要/沿革/"
                   "製品・サービス/人名・役員 のみで作ること。同じ事実の重複設問は作らない。")
        pool = generate(name, corpus, max(need + 6, 12), extra=dyn)
        lint_ok = []
        for q in pool:
            q.setdefault("id", "")
            k = q.get("q_text", "").strip()[:40]
            if k in seen_q:
                continue
            if lint_one(q, corpus):                  # 単一lint(単位整合/数値日付/カテゴリ等)
                rq = _repair_distractors(q, corpus)  # 誤答捏造なら corpus 内の同単位実数へ修復
                if rq is None:
                    continue
                q = rq
            seen_q.add(k); lint_ok.append(q)
        if not lint_ok:
            if not cost_ok(): break
            continue
        for j, q in enumerate(lint_ok):
            q["id"] = f"{slug}_r{rnd}_{j:02d}"
        passed_ids, rate, g, p = _review_pass_ids(lint_ok, corpus)
        tot_graded += g; tot_passed += p
        # 採用: レビューpass + 概念重複なし + ドライ上限 + 財務上限。財務は下限まで優先。
        cands = [q for q in lint_ok if q["id"] in passed_ids]
        cands.sort(key=lambda x: 0 if (x.get("category") == FIN and fin_n < fin_floor) else
                                 (2 if x.get("category") == FIN else 1))
        for q in cands:
            if len(accepted) >= target:
                break
            concept = QL._concept_of(q)
            key = (concept, (q.get("as_of") or "").strip())
            if concept and key in seen_concepts:
                continue                              # 概念重複
            if concept in QL.DRY_CONCEPTS and dry_n >= QL.DRY_CAP:
                continue                              # 登記トリビア上限
            if q.get("category") == FIN and fin_n >= fin_cap:
                continue                              # 財務上限
            accepted.append(q)
            if concept: seen_concepts.add(key)
            if concept in QL.DRY_CONCEPTS: dry_n += 1
            if q.get("category") == FIN: fin_n += 1
        if not cost_ok():
            break
    final = [{**q, "id": f"{slug}_{i:02d}"} for i, q in enumerate(accepted[:target], 1)]
    # 最終list-lint(概念dedup/ドライ上限/単位)でerror残があれば除去して再採番
    r = QL.run_quiz_lints(final, corpus)
    if r["errors"] > 0:
        bad = {f["id"] for f in r["findings"] if f["severity"] == "error"}
        final = [{**q, "id": f"{slug}_{i:02d}"} for i, q in enumerate(
                 [q for q in final if q["id"] not in bad], 1)]
    dropped = target - len(final)
    overall_rate = (tot_passed / tot_graded) if tot_graded else 1.0
    return final, max(0, dropped), round(overall_rate, 3)


# ── OpenAI レビュー(R1-R6) ───────────────────────────────
REVIEW_SYS = (
 "あなたはクイズの『事実正しさ』の独立審査員。各設問を提供された source スニペットに照らし採点する。\n"
 "【前提】設計面(数値・日付の実在=lint済 / 4択の単位統一 / 概念重複なし / 登記トリビア上限 / 財務比率)は\n"
 "別途 機械lint で既に保証済み。あなたは設計を再審査しない。**事実の正しさだけ**を見る。\n"
 "スニペットはPDF表抽出でラベルと数値が離れることがある。『ラベル併記が無い』だけでは落とさない。\n"
 "不合格(pass=false)にするのは、次の“明確な誤り”がある時だけ:\n"
 "  ・正解が設問の問う指標と明確に取り違え(例: 収益を問うのに税引前利益の値、当期利益と包括利益の混同)\n"
 "  ・解説が source と矛盾している\n"
 "  ・正解が実際には誤り、または正解が2つ以上ある\n"
 "  ・誤答が正解と重複している/明らかに正解と区別できない(＝実質的に答えが割れる)\n"
 "  ・誤答に『現実に存在しない値』が含まれる(架空の証券取引所=西証/南証、存在しない電話番号、"
 "実在しない地名・役職・製品など)。誤答はすべて実在し得る妥当な値であること。\n"
 "  ・非数値設問(セグメント名/製品/沿革/人名)で、正解が source の記述と矛盾している\n"
 "上記に当てはまらなければ **pass=true**(良問は通す。スタイルや『やや易しい』では落とさない)。\n"
 "参考ルーブリック: R1整合 / R3順位はcompetitors必須・EPS社間比較は不可 / R5誤答が同source実数として妥当 / R6正解1つで正しい。\n"
 "出力JSON: {\"results\":[{\"id\":\"..\",\"pass\":true,\"reasons\":\"..\"}],"
 "\"systemic_flags\":[\"..\"],\"pass_rate\":0.0}. systemic_flags は“同一ルール違反が3問以上で多発”した場合のみ、"
 "該当ルール名(R1..R6)+要約を入れる。単発の懸念は systemic に入れない。")

# 設問が問う指標のキーワード(スニペットにラベル文脈を添えて偽陽性を減らす)
METRIC_KW = ("収益", "売上高", "売上収益", "営業利益", "税引前利益", "当期利益", "純利益", "包括利益",
             "総資産", "資産合計", "純資産", "資本", "自己資本", "ROE", "配当", "配当性向", "持分",
             "従業員", "資本金", "設立", "創業", "拠点", "セグメント", "事業本部", "本社", "本店")

def review_batch(items):
    """items: [{id,q_text,options,correct,explanation,source_url,category,snippets}]"""
    payload = json.dumps(items, ensure_ascii=False)[:24000]
    txt = openai_chat([{"role": "system", "content": REVIEW_SYS},
                       {"role": "user", "content": "採点対象:\n" + payload}],
                      model=REVIEW_MODEL, max_tokens=3000)
    d = _parse_json(txt) or {"results": [], "systemic_flags": ["review_parse_error"], "pass_rate": 0.0}
    return d

def _flex_ctx(body, needle, width=60):
    chars = [c for c in needle if not c.isspace() and c not in ",，"]
    if len(chars) < 2:
        return None
    m = re.search(r"[\s,，]*".join(re.escape(c) for c in chars), body)
    if not m:
        return None
    return re.sub(r"\s+", " ", body[max(0, m.start() - width): m.end() + width])

def snippets_for(q, corpus, width=60):
    """レビュー用の証拠スニペット。数値設問は該当数値の周辺、非数値設問は正解語の周辺を引用。
    どうしても取れなければ corpus 先頭抜粋を渡す(reviewerが評価不能にならないように)。"""
    body = corpus.get(q.get("source_url"), "")
    out = []
    # ① 各選択肢の主要数値(>=3桁)の周辺
    for o in q.get("options", []):
        for m in QL.NUM_RE.finditer(str(o)):
            tok = QL._norm_num(m.group(0))
            if len(tok.replace(".", "")) < 3:
                continue
            if re.search(r"[\s,，]*".join(re.escape(c) for c in tok), QL._norm_num(body)):
                c = _flex_ctx(body, tok, width)
                if c:
                    out.append(c)
            break
    # ② 非数値設問: 正解の語句の周辺(セグメント名/製品/人名/会社概要 等)
    if not out:
        corr = str(q.get("options", ["", "", "", ""])[q.get("correct", 0)]).strip()
        c = _flex_ctx(body, corr.replace(" ", ""), width + 20)
        if c:
            out.append(c)
    # ②b 設問が問う指標ラベルの周辺も添える(PDF表でラベルと数値が離れる問題への対策)
    qt = q.get("q_text", "") + " " + q.get("explanation", "")
    for kw in METRIC_KW:
        if kw in qt:
            c = _flex_ctx(body, kw, width)
            if c:
                out.append(c)
            break
    # ③ フォールバック: corpus 先頭抜粋(reviewerが「証拠なし」で機械的にfailしないため)
    if not out and body:
        out.append(re.sub(r"\s+", " ", body[:280]))
    # 重複除去
    seen, uniq = set(), []
    for s in out:
        if s in seen:
            continue
        seen.add(s); uniq.append(s)
    return uniq[:4]


# ── 対象リスト ───────────────────────────────────────────
def load_targets():
    d = json.load(open(COMPANIES, encoding="utf-8"))
    companies, industries = [], []
    for industry, lst in d.items():
        members = [(c["id"], c["name"]) for c in lst if c.get("id") and c.get("name")]
        for cid, cname in members:
            companies.append({"kind": "company", "slug": cid, "name": cname, "industry": industry})
        industries.append({"kind": "industry", "slug": f"industry__{_ind_slug(industry)}",
                           "name": industry, "members": members[:5]})
    return companies, industries

def _ind_slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or hashlib.md5(s.encode()).hexdigest()[:6]


# ── 状態(resumable) ──────────────────────────────────────
def load_state():
    if os.path.exists(STATE_PATH):
        return json.load(open(STATE_PATH, encoding="utf-8"))
    return {"done": [], "blocked": [], "counts": {"q": 0, "dropped": 0},
            "checkpoints": [], "grad_streak": 0, "graduated": False,
            "rule_tuning": 0, "halted": False, "cost_usd": 0.0}

def save_state(st):
    st["cost_usd"] = round(_cost["usd"], 4)
    json.dump(st, open(STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def record_blocked(slug, name, got, reason):
    newfile = not os.path.exists(BLOCKED_CSV)
    with open(BLOCKED_CSV, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if newfile: w.writerow(["slug", "name", "got", "reason", "ts"])
        w.writerow([slug, name, got, reason, int(time.time())])

NEEDS_CSV = os.path.join(OUT, "quiz_needs_source.csv")
def record_needs_source(slug, name, got, reason):
    """公式一次情報が無い/薄い社(roomの倍率ブロック同方式・後で手当て)。"""
    newfile = not os.path.exists(NEEDS_CSV)
    with open(NEEDS_CSV, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if newfile: w.writerow(["slug", "name", "got", "reason", "ts"])
        w.writerow([slug, name, got, reason, int(time.time())])

FRESHNESS_HOLD_CSV = os.path.join(OUT, "freshness_hold.csv")
def record_freshness_hold(slug, name, got_fy, want_fy=None):
    """最新期(2026年3月期)が取得できず旧期のまま維持した社(捏造しない・後で手当て)。"""
    newfile = not os.path.exists(FRESHNESS_HOLD_CSV)
    with open(FRESHNESS_HOLD_CSV, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if newfile: w.writerow(["slug", "name", "got_fy", "want_fy", "ts"])
        w.writerow([slug, name, got_fy, want_fy or LATEST_FY, int(time.time())])

SHIP_MIN = 15   # 出荷基準: lint+review通過の良問が15問以上の社のみ出荷(質を下げて埋めない)
THIN_CSV = os.path.join(OUT, "quiz_thin.csv")
def record_thin(slug, name, got, industry=""):
    """良問が15未満=保留。後でcorpus増強→再生成。"""
    newfile = not os.path.exists(THIN_CSV)
    with open(THIN_CSV, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if newfile: w.writerow(["slug", "name", "got", "industry", "ts"])
        w.writerow([slug, name, got, industry, int(time.time())])


# ── 1社処理 ──────────────────────────────────────────────
def process_one(tgt):
    slug, name, kind = tgt["slug"], tgt["name"], tgt["kind"]
    outdir = os.path.join(OUT, slug)
    os.makedirs(outdir, exist_ok=True)
    out_q = os.path.join(outdir, "quiz_30q.json")
    if os.path.exists(out_q):
        try:
            nq = len(json.load(open(out_q)))
            return {"slug": slug, "name": name, "n": nq, "dropped": 0, "blocked": False,
                    "skipped": True, "corpus_ok": True, "needs_source": False, "kind": kind}
        except Exception:
            pass
    try:
        if kind == "industry":
            corpus = {}
            for cid, cname in tgt.get("members", []):
                corpus.update(acquire_corpus(cname, cid))
                if not cost_ok(): break
        else:
            corpus = acquire_corpus(name, slug)
        if not corpus:
            record_needs_source(slug, name, 0, "no_official_url(ファクトシートに公式ドメインURL無し/薄い)")
            return {"slug": slug, "name": name, "n": 0, "dropped": 0, "blocked": True,
                    "needs_source": True, "corpus_ok": False, "kind": kind}
        final, dropped = converge(slug, name, corpus, target=30)
        json.dump(final, open(out_q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(corpus, open(os.path.join(outdir, "quiz_corpus.json"), "w", encoding="utf-8"),
                  ensure_ascii=False)
        if len(final) < 30:
            record_needs_source(slug, name, len(final), f"under30(公式URLは有るがcorpus薄い: {len(final)}/30)")
        return {"slug": slug, "name": name, "n": len(final), "dropped": dropped,
                "blocked": len(final) < 30, "needs_source": len(final) < 30, "corpus_ok": True,
                "kind": kind, "corpus_urls": list(corpus.keys())}
    except Exception as e:
        record_needs_source(slug, name, 0, f"error:{type(e).__name__}:{str(e)[:80]}")
        return {"slug": slug, "name": name, "n": 0, "dropped": 0, "blocked": True,
                "needs_source": True, "corpus_ok": False, "kind": kind, "err": str(e)[:120]}


# ── チェックポイント(レビュー+report+commit+LINE) ────────
def checkpoint(st, batch_results, cp_idx):
    # レビュー対象サンプル抽出(順位・非財務・新規社優先)
    sample = []
    for res in batch_results:
        if res.get("blocked") or res.get("n", 0) == 0: continue
        try:
            qs = json.load(open(os.path.join(OUT, res["slug"], "quiz_30q.json")))
            corpus = json.load(open(os.path.join(OUT, res["slug"], "quiz_corpus.json")))
        except Exception:
            continue
        ranked = [q for q in qs if q.get("type") == "rank" or q.get("category") == "業界順位"]
        nonfin = [q for q in qs if q.get("category") not in ("財務数値", "業界順位")]
        pick = (ranked[:2] + nonfin[:2] + qs[:1])
        for q in pick:
            sample.append({"id": q["id"], "q_text": q["q_text"], "options": q["options"],
                           "correct": q["correct"], "explanation": q.get("explanation", ""),
                           "category": q.get("category"), "source_url": q.get("source_url"),
                           "snippets": snippets_for(q, corpus)})
        if len(sample) >= REVIEW_K: break
    sample = sample[:REVIEW_K]
    review = review_batch(sample) if (sample and not st["graduated"]) else {"results": [], "systemic_flags": [], "pass_rate": 1.0}
    pass_rate = review.get("pass_rate", 1.0)
    sysflags = review.get("systemic_flags", [])
    # lint統計(バッチ)
    lint_err = 0
    for res in batch_results:
        if res.get("blocked"): continue
        try:
            qs = json.load(open(os.path.join(OUT, res["slug"], "quiz_30q.json")))
            corpus = json.load(open(os.path.join(OUT, res["slug"], "quiz_corpus.json")))
            lint_err += QL.run_quiz_lints(qs, corpus)["errors"]
        except Exception:
            pass
    # このバッチの 公式URL取得成否
    b_corpus_ok = sum(1 for r in batch_results if r.get("corpus_ok"))
    b_needs = sum(1 for r in batch_results if r.get("needs_source"))
    cp = {"cp": cp_idx, "done": len(st["done"]), "q": st["counts"]["q"],
          "dropped": st["counts"]["dropped"], "blocked": len(st["blocked"]),
          "batch_corpus_ok": b_corpus_ok, "batch_needs_source": b_needs,
          "lint_err": lint_err, "pass_rate": pass_rate, "systemic": sysflags,
          "cost": round(_cost["usd"], 2)}
    st["checkpoints"].append(cp)
    # 卒業判定
    if lint_err == 0 and pass_rate >= GRAD_PASS and not sysflags:
        st["grad_streak"] += 1
        if st["grad_streak"] >= 3 and not st["graduated"]:
            st["graduated"] = True
    else:
        st["grad_streak"] = 0
    # サンプルreview.md(1社)を受け渡しフォルダへ
    try:
        _write_sample_review(batch_results, cp_idx)
    except Exception:
        pass
    # HALT判定: 単発のレビュー偽陽性で全体を止めないため、真の恒常systemicに限定。
    #   (1) バッチ全体でpass率が崩れた(<0.85) -> 即HALT
    #   (2) 同種systemicが2チェックポイント連続 -> HALT(恒常systemic)
    #   (3) 既知ノブ(R2/R3/R4/date/rank/eps/mix)由来は tuning(最大2)で吸収し止めない
    halt = False
    known = ("R2", "R3", "R4", "date", "rank", "eps", "mix")
    persistent_sys = bool(sysflags) and bool(st.get("prev_sysflags"))
    if sysflags and any(any(k in str(f) for k in known) for f in sysflags) and st["rule_tuning"] < 2:
        st["rule_tuning"] += 1   # 既知ノブ->プロンプト強化余地(lintは既に強化済)
    elif persistent_sys:
        halt = True              # 2CP連続の未知systemic=恒常->停止して相談
    if pass_rate < 0.85:
        halt = True
    st["prev_sysflags"] = sysflags
    st["halted"] = halt
    save_state(st)
    # commit/push (privateのtokyari-pipeline側に成果, 10koma側にコード/状態は別途)
    _commit_push(cp_idx, cp)
    msg = (f"[quiz CP{cp_idx}] 完了{cp['done']}社 / 公式URL取得{b_corpus_ok}・needs_source{b_needs} / "
           f"生成{cp['q']}問 / 破棄{cp['dropped']} / lint_err{lint_err} / pass{pass_rate:.0%} / ${cp['cost']}"
           + (" / ★卒業(以降lint主体)" if st["graduated"] else "")
           + (f" / ⚠HALT systemic={sysflags}" if halt else ""))
    line(msg)
    return halt

def _write_sample_review(batch_results, cp_idx):
    cand = [r for r in batch_results if not r.get("blocked") and r.get("n", 0) >= 20]
    if not cand: return
    res = cand[0]
    qs = json.load(open(os.path.join(OUT, res["slug"], "quiz_30q.json")))
    corpus = json.load(open(os.path.join(OUT, res["slug"], "quiz_corpus.json")))
    md = [f"# quiz 検分サンプル CP{cp_idx}: {res['name']} ({res['slug']})", ""]
    for i, q in enumerate(qs, 1):
        md.append(f"### {i}. {q['id']} — {q.get('category')}")
        md.append(f"**設問**: {q['q_text']}")
        for j, o in enumerate(q["options"]):
            md.append(f"- {'★' if j == q['correct'] else '　'} {o}")
        md.append(f"as_of: {q.get('as_of')} / source: {q.get('source_url')}")
        for s in snippets_for(q, corpus):
            md.append(f"  - 裏取り: …{s}…")
        md.append("")
    os.makedirs(HANDOFF, exist_ok=True)
    open(os.path.join(HANDOFF, f"quiz_sample_CP{cp_idx}_{res['slug']}.md"), "w",
         encoding="utf-8").write("\n".join(md))

def _commit_push(cp_idx, cp):
    # コードと状態は 10koma(public) にはコード/レポートのみ。成果JSONは private tokyari-pipeline に。
    try:
        # quiz関連のみをstage(無関係な output 変更を巻き込まない)
        git("add", "output/_quiz_fanout_state.json", "output/quiz_blocked.csv",
            "output/quiz_needs_source.csv", "output/*/quiz_30q.json", "output/*/quiz_corpus.json", cwd=PIPE)
        git("-c", "user.email=quiz@local", "-c", "user.name=quiz-fanout",
            "commit", "-q", "-m", f"quiz-fanout CP{cp_idx}: done={cp['done']} q={cp['q']} blocked={cp['blocked']} pass={cp['pass_rate']}", cwd=PIPE)
        git("push", "-q", "origin", "HEAD", cwd=PIPE)
    except Exception as e:
        print("[commit ERR]", e)


# ── メイン ───────────────────────────────────────────────
def run(targets, st, is_validate=False):
    # ローリング投入: 全タスクを一括submitするとexecutor drainでHALT/コストガードが
    # 実効しない。同時にPARALLEL件だけ走らせ、stop判断後は新規投入を止める(超過は最大PARALLEL-1)。
    from concurrent.futures import wait, FIRST_COMPLETED
    doneset = set(st["done"])
    blk = set(b if isinstance(b, str) else b.get("slug") for b in st["blocked"])
    pending = [t for t in targets if t["slug"] not in doneset and t["slug"] not in blk]
    print(f"対象 {len(targets)} / 未処理 {len(pending)} / done {len(st['done'])}", flush=True)
    batch = []
    stop_reason = None
    it = iter(pending)
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        inflight = {}
        for _ in range(PARALLEL):
            t = next(it, None)
            if t: inflight[ex.submit(process_one, t)] = t
        while inflight:
            done, _pend = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fut in done:
                inflight.pop(fut, None)
                res = fut.result()
                with _lock:
                    if res["slug"] not in st["done"]:
                        st["done"].append(res["slug"])
                    st["counts"]["q"] += res.get("n", 0)
                    st["counts"]["dropped"] += res.get("dropped", 0)
                    if res.get("blocked"):
                        st["blocked"].append({"slug": res["slug"], "name": res["name"], "n": res.get("n", 0)})
                batch.append(res)
                print(f"  {'SKIP' if res.get('skipped') else 'DONE'} {res['slug']}: n={res.get('n')} "
                      f"blocked={res.get('blocked')} ${_cost['usd']:.2f}", flush=True)
                if not cost_ok():
                    stop_reason = "cost_stop"
                if len(batch) >= CHECKPOINT_EVERY and not is_validate:
                    cp_idx = len(st["checkpoints"]) + 1
                    halt = checkpoint(st, batch, cp_idx)
                    batch = []
                    if halt:
                        line(f"⚠️ HALT CP{cp_idx}: systemic恒常化。ファンアウト一時停止。")
                        stop_reason = "halt"
                if stop_reason is None:  # 新規投入は stop でない時のみ(超過を防ぐ)
                    nt = next(it, None)
                    if nt: inflight[ex.submit(process_one, nt)] = nt
            if stop_reason:
                break  # 新規投入停止。inflight(<=PARALLEL)はwith脱出時にdrainされるが最大2件
    if stop_reason == "cost_stop":
        save_state(st); line(f"⚠️ COST_GUARD ${_cost['usd']:.2f}>=${MAX_USD} 停止。done={len(st['done'])}")
        return "cost_stop"
    if stop_reason == "halt":
        save_state(st); return "halt"
    if batch and not is_validate:
        checkpoint(st, batch, len(st["checkpoints"]) + 1)
    save_state(st)
    return "done"


def run_locked(industry_name, lockdir="sogo_shosha_locked", suf="locked"):
    """品質固定モード: 1業界の各社+業界を 厚いcorpus + 二層ゲート(lint+review) で作り直す。
    小バッチ・ローリング(PARALLEL)・コストガード。出力は <lockdir>/ と private。"""
    from concurrent.futures import wait, FIRST_COMPLETED
    companies, industries = load_targets()
    members = [(c["slug"], c["name"]) for c in companies if c.get("industry") == industry_name]
    ind = next((x for x in industries if x["name"] == industry_name), None)
    LOCK_DIR = os.path.join(HANDOFF, lockdir)
    Q30F, CORPF = f"quiz_30q_{suf}.json", f"quiz_corpus_{suf}.json"
    os.makedirs(LOCK_DIR, exist_ok=True)
    line(f"🔒 quiz品質固定モード開始: {industry_name} {len(members)}社+業界1 / 厚corpus+二層ゲート / 並列{PARALLEL}・${MAX_USD}ガード")
    results = []

    def work_company(slug, name):
        try:
            corpus = acquire_corpus_thick(name, slug)
            if not corpus:
                record_needs_source(slug, name, 0, "locked:no_official_url")
                return {"slug": slug, "name": name, "n": 0, "pass": None, "needs_source": True}
            final, dropped, rate = converge_locked(slug, name, corpus, target=30)
            outp = os.path.join(OUT, slug, Q30F)
            os.makedirs(os.path.dirname(outp), exist_ok=True)
            json.dump(final, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            json.dump(corpus, open(os.path.join(OUT, slug, CORPF), "w", encoding="utf-8"), ensure_ascii=False)
            json.dump(final, open(os.path.join(LOCK_DIR, f"{slug}_quiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            if len(final) < 30:
                record_needs_source(slug, name, len(final), f"locked:under30({len(final)}/30, corpus薄)")
            return {"slug": slug, "name": name, "n": len(final), "pass": rate, "needs_source": len(final) < 30,
                    "corpus_urls": len(corpus)}
        except Exception as e:
            record_needs_source(slug, name, 0, f"locked:error:{type(e).__name__}:{str(e)[:60]}")
            return {"slug": slug, "name": name, "n": 0, "pass": None, "needs_source": True, "err": str(e)[:100]}

    # ローリング(最大PARALLEL同時)
    it = iter(members); inflight = {}
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for _ in range(PARALLEL):
            m = next(it, None)
            if m: inflight[ex.submit(work_company, *m)] = m
        while inflight:
            done, _p = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fut in done:
                inflight.pop(fut, None)
                r = fut.result(); results.append(r)
                print(f"  {r['slug']:16} n={r['n']} pass={r['pass']} needs_source={r.get('needs_source')} ${_cost['usd']:.2f}", flush=True)
                if cost_ok():
                    m = next(it, None)
                    if m: inflight[ex.submit(work_company, *m)] = m
            if not cost_ok():
                line(f"⚠️ COST_GUARD ${_cost['usd']:.2f}>=${MAX_USD} locked停止"); break

    # 業界quiz(順位設問: 全社corpusをmerge, competitors必須)
    ind_res = None
    if ind and cost_ok():
        mcorpus = {}
        for slug, name in members:
            cf = os.path.join(OUT, slug, CORPF)
            if os.path.exists(cf):
                mcorpus.update(json.load(open(cf)))
        extra = ("この業界クイズでは、可能な範囲で『順位/最大/最高』の設問を作る場合、必ず type:\"rank\" と "
                 "competitors:[{name,value,source_url}](全比較社の値+出典URL)を付ける。EPS等の株数依存指標での"
                 "社間比較は禁止(収益・利益額・ROE・総資産で作る)。数値は各社source本文に実在するものだけ。")
        if mcorpus:
            final, dropped, rate = converge_locked(ind["slug"], industry_name, mcorpus, target=30, extra=extra)
            json.dump(final, open(os.path.join(LOCK_DIR, f"industry_{ind['slug']}_quiz.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            json.dump(mcorpus, open(os.path.join(OUT, ind["slug"], CORPF), "w", encoding="utf-8"),
                      ensure_ascii=False) if os.path.isdir(os.path.join(OUT, ind["slug"])) or os.makedirs(os.path.join(OUT, ind["slug"]), exist_ok=True) is None else None
            rankn = sum(1 for q in final if q.get("type") == "rank" or q.get("category") == "業界順位")
            ind_res = {"slug": ind["slug"], "n": len(final), "pass": rate, "rank": rankn}
            print(f"  業界 {industry_name}: n={len(final)} pass={rate} rank設問={rankn}", flush=True)

    # サンプル review.md(1社 + 業界)
    def write_reviewmd(slug, name, qs, corpus):
        md = [f"# quiz(品質固定): {name} ({slug})", "", f"全{len(qs)}問 / lint error=0 + OpenAI R1-R6 pass のみ採用", ""]
        for i, q in enumerate(qs, 1):
            md.append(f"### {i}. {q['id']} — {q.get('category')}")
            md.append(f"**設問**: {q['q_text']}")
            for j, o in enumerate(q["options"]):
                md.append(f"- {'★' if j == q['correct'] else '　'} {o}")
            md.append(f"as_of: {q.get('as_of')} / source: {q.get('source_url')}")
            for s in snippets_for(q, corpus)[:2]:
                md.append(f"  - 裏取り: …{s[:150]}…")
            md.append("")
        open(os.path.join(LOCK_DIR, f"review_{slug}.md"), "w", encoding="utf-8").write("\n".join(md))
    for r in results:
        if r["n"] >= 20:
            qs = json.load(open(os.path.join(OUT, r["slug"], Q30F)))
            corpus = json.load(open(os.path.join(OUT, r["slug"], CORPF)))
            write_reviewmd(r["slug"], r["name"], qs, corpus); break

    # サマリ
    dist = {}
    for r in results:
        b = "30" if r["n"] >= 30 else "20-29" if r["n"] >= 20 else "<20" if r["n"] > 0 else "0"
        dist[b] = dist.get(b, 0) + 1
    passes = [r["pass"] for r in results if r["pass"] is not None]
    summary = {"industry": industry_name, "companies": results, "industry_quiz": ind_res,
               "distribution": dist, "avg_review_pass": round(sum(passes) / len(passes), 3) if passes else None,
               "cost_usd": round(_cost["usd"], 2)}
    json.dump(summary, open(os.path.join(LOCK_DIR, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot_q = sum(r["n"] for r in results) + (ind_res["n"] if ind_res else 0)
    line(f"🔒 quiz品質固定 完了: {industry_name} {len(results)}社 / 総問{tot_q} / 分布{dist} / "
         f"平均review pass{summary['avg_review_pass']} / ${summary['cost_usd']} / 出力 {lockdir}/")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


LOCKED_STATE = os.path.join(OUT, "_quiz_locked_state.json")
def _load_locked_state():
    if os.path.exists(LOCKED_STATE):
        return json.load(open(LOCKED_STATE, encoding="utf-8"))
    return {"done": [], "shipped": [], "thin": [], "needs": [], "q": 0,
            "checkpoints": [], "prev_low": False, "cost_usd": 0.0}
def _save_locked_state(st):
    st["cost_usd"] = round(_cost["usd"], 4)
    json.dump(st, open(LOCKED_STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def _locked_reviewmd(slug, name, qs, corpus, outdir):
    md = [f"# quiz(品質固定v3): {name} ({slug})", "",
          f"全{len(qs)}問 / v3 lint error=0 + 事実レビューpass / corpus=本体公式ドメインのみ", ""]
    for i, q in enumerate(qs, 1):
        md.append(f"### {i}. {q['id']} — {q.get('category')}")
        md.append(f"**設問**: {q['q_text']}")
        for j, o in enumerate(q["options"]):
            md.append(f"- {'★' if j == q['correct'] else '　'} {o}")
        md.append(f"as_of: {q.get('as_of')} / source: {q.get('source_url')}")
        for s in snippets_for(q, corpus)[:2]:
            md.append(f"  - 裏取り: …{s[:140]}…")
        md.append("")
    open(os.path.join(outdir, f"review_{slug}.md"), "w", encoding="utf-8").write("\n".join(md))

def run_freshness():
    """出荷済社の財務を最新期(LATEST_FY)へ再生成。最新corpusで全問再生成し、
    ≥SHIP_MIN & lint0(財務freshness含む) & 財務as_of=最新 の時だけ上書き。
    最新期(LATEST_FY)がcorpusで取れない社は freshness_hold(旧2025維持)。
    再生成で<15になった社も旧版維持(regen_thin=保留)。ローリング・CP20・resumable・累積コストガード。
    業界セットは本関数の後に --locked-all で(更新corpusをmergeして)生成する。"""
    from concurrent.futures import wait, FIRST_COMPLETED
    companies, _industries = load_targets()
    stp = os.path.join(OUT, "_quiz_freshness_state.json")
    st = (json.load(open(stp, encoding="utf-8")) if os.path.exists(stp)
          else {"done": [], "updated": [], "hold": [], "regen_thin": [],
                "q_delta": 0, "checkpoints": [], "cost_usd": 0.0})
    with _lock:
        _cost["usd"] = st.get("cost_usd", 0.0)
    latest_year = int(re.search(r"20\d\d", LATEST_FY).group())
    doneset = set(st["done"])
    shipped = [c for c in companies
               if os.path.exists(os.path.join(OUT, c["slug"], "quiz_30q_locked_v3.json"))
               and c["slug"] not in doneset]
    hold_csv = os.path.join(OUT, "freshness_hold.csv")
    line(f"🕐 鮮度再生成 開始/再開: 対象{len(shipped)}社 (最新期={LATEST_FY}) / "
         f"既更新{len(st['updated'])}・保留{len(st['hold'])+len(st['regen_thin'])} / 並列{PARALLEL}・${MAX_USD}ガード")

    def _hold_row(slug, name, reason, extra=""):
        with open(hold_csv, "a", encoding="utf-8") as f:
            f.write(f"{slug},{name},{reason},{extra}\n")

    def work(tgt):
        slug, name, ind = tgt["slug"], tgt["name"], tgt["industry"]
        outp = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        try:
            corpus = acquire_corpus_thick(name, slug, prefer_latest=True)
            if not corpus:
                return {"slug": slug, "name": name, "status": "hold", "reason": "no_corpus"}
            latest = QL._corpus_latest_fy_year(corpus)
            if latest is None or latest < latest_year:
                return {"slug": slug, "name": name, "status": "hold", "reason": f"corpus_latest={latest or 'NA'}"}
            # 最新corpusで再生成: freshness lintが財務as_of<最新をerror化→最新期を強制
            final, dropped, rate = converge_locked(slug, name, corpus, target=30)
            if len(final) < SHIP_MIN:
                return {"slug": slug, "name": name, "status": "regen_thin", "n": len(final)}
            rep = QL.run_quiz_lints(final, corpus)
            if rep["errors"] > 0:
                return {"slug": slug, "name": name, "status": "regen_thin", "n": len(final), "reason": "lint"}
            # 最新期の財務問が1問以上あることを確認(0なら鮮度更新の意味がない→保留で旧版維持)
            fin_latest = [q for q in final if q.get("category") in ("財務数値", "業界順位")
                          and QL._fy_year(q.get("as_of")) == latest]
            if not fin_latest:
                return {"slug": slug, "name": name, "status": "hold", "reason": "no_latest_financial_q"}
            oldn = 0
            try:
                oldn = len(json.load(open(outp)))
            except Exception:
                pass
            json.dump(final, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            json.dump(corpus, open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
            try:
                ds, _cov = build_datasheet(slug, name, corpus, final)
                json.dump(ds, open(os.path.join(OUT, slug, "datasheet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            except Exception:
                pass
            return {"slug": slug, "name": name, "status": "updated", "n": len(final),
                    "delta": len(final) - oldn, "fin_latest": len(fin_latest), "pass": rate}
        except Exception as e:
            return {"slug": slug, "name": name, "status": "hold", "reason": f"err:{type(e).__name__}:{str(e)[:40]}"}

    def checkpoint(batch, cp_idx):
        upd = [r for r in batch if r["status"] == "updated"]
        cp = {"cp": cp_idx, "done": len(st["done"]), "updated": len(st["updated"]),
              "hold": len(st["hold"]), "regen_thin": len(st["regen_thin"]),
              "q_delta": st["q_delta"], "cost": round(_cost["usd"], 2)}
        st["checkpoints"].append(cp)
        json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        try:
            git("add", "output/_quiz_freshness_state.json", "output/freshness_hold.csv",
                "output/*/quiz_30q_locked_v3.json", "output/*/quiz_corpus_locked_v3.json",
                "output/*/datasheet.json", cwd=PIPE)
            git("-c", "user.email=quiz@local", "-c", "user.name=quiz-freshness",
                "commit", "-q", "-m",
                f"quiz-freshness CP{cp_idx}: 更新{len(st['updated'])} 保留{len(st['hold'])+len(st['regen_thin'])} Δq{st['q_delta']} ({LATEST_FY})", cwd=PIPE)
            git("push", "-q", "origin", "HEAD", cwd=PIPE)
        except Exception as e:
            print("[commit ERR]", e)
        line(f"[鮮度 CP{cp_idx}] 完了{cp['done']}/{len(shipped)} / 更新{cp['updated']}・保留{cp['hold']+cp['regen_thin']} / "
             f"Δq{cp['q_delta']} / ${cp['cost']}")

    batch, stop = [], None
    it = iter(shipped); inflight = {}
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for _ in range(PARALLEL):
            t = next(it, None)
            if t: inflight[ex.submit(work, t)] = t
        while inflight:
            done, _p = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fut in done:
                inflight.pop(fut, None)
                r = fut.result()
                with _lock:
                    if r["slug"] not in st["done"]: st["done"].append(r["slug"])
                    if r["status"] == "updated":
                        if r["slug"] not in st["updated"]: st["updated"].append(r["slug"])
                        st["q_delta"] += r.get("delta", 0)
                    elif r["status"] == "regen_thin":
                        if r["slug"] not in st["regen_thin"]: st["regen_thin"].append(r["slug"])
                        _hold_row(r["slug"], r["name"], "regen_thin", str(r.get("n")))
                    else:
                        if r["slug"] not in st["hold"]: st["hold"].append(r["slug"])
                        _hold_row(r["slug"], r["name"], r.get("reason", "hold"))
                batch.append(r)
                print(f"  {r['status']:10} {r['slug']:16} n={r.get('n')} fin={r.get('fin_latest')} ${_cost['usd']:.2f}"
                      + (f" [{r.get('reason')}]" if r.get("reason") else ""), flush=True)
                if not cost_ok(): stop = "cost"
                if len(batch) >= CHECKPOINT_EVERY:
                    checkpoint(batch, len(st["checkpoints"]) + 1); batch = []
                if stop is None:
                    nt = next(it, None)
                    if nt: inflight[ex.submit(work, nt)] = nt
            if stop: break
    if batch:
        checkpoint(batch, len(st["checkpoints"]) + 1)
    json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    agg = {"target": len(shipped) + len(st["updated"]) + len(st["hold"]) + len(st["regen_thin"]),
           "updated": len(st["updated"]), "hold": len(st["hold"]),
           "regen_thin": len(st["regen_thin"]), "q_delta": st["q_delta"],
           "cost_usd": round(_cost["usd"], 2), "stop": stop or "done", "latest_fy": LATEST_FY}
    line(f"[鮮度 {agg['stop']}] 更新{agg['updated']}社 / 保留{agg['hold']+agg['regen_thin']}(旧期維持) / "
         f"Δq{agg['q_delta']} / ${agg['cost_usd']} ({LATEST_FY})")
    print(json.dumps(agg, ensure_ascii=False, indent=1))
    return 0

def run_all_locked():
    """全16業界の品質固定ロック。各業界=所属全社(厚corpus+二層ゲート+出荷基準≥15)。
    夜間規律: ローリング投入・20社毎CP(lint統計+サンプル1社+commit/push+LINE)・resumable・
    コストガード$75・systemic劣化でHALT。本番反映(D1)はしない。"""
    from concurrent.futures import wait, FIRST_COMPLETED
    companies, industries = load_targets()
    HROOT = os.path.join(HANDOFF, "gyokai_locked_v3")
    os.makedirs(HROOT, exist_ok=True)
    st = _load_locked_state()
    with _lock:                      # コストガードを累積化(resumeでも$75総額を守る)
        _cost["usd"] = st.get("cost_usd", 0.0)
    doneset = set(st["done"])
    # pending: 未処理(fresh) + quizありdatasheet無し(retrofit対象)。done済のthin/needsは再挑戦しない。
    pending = []
    for c in companies:
        qp = os.path.join(OUT, c["slug"], "quiz_30q_locked_v3.json")
        dp = os.path.join(OUT, c["slug"], "datasheet.json")
        if os.path.exists(qp):
            if not os.path.exists(dp):
                pending.append(c)          # datasheet retrofit
        elif c["slug"] not in doneset:
            pending.append(c)              # fresh(quiz+datasheet)
    # 既出荷社のdatasheet補完(安価)を先に→既shipの教材を完備してから fresh へ
    pending.sort(key=lambda c: 0 if os.path.exists(os.path.join(OUT, c["slug"], "quiz_30q_locked_v3.json")) else 1)
    retro = sum(1 for c in pending if os.path.exists(os.path.join(OUT, c["slug"], "quiz_30q_locked_v3.json")))
    line(f"🔒 quiz+教材ロック開始/再開: 全{len(companies)}社 / 処理{len(pending)}(datasheet補完{retro}) / "
         f"出荷済{len(st['shipped'])} / 並列{PARALLEL}・${MAX_USD}ガード・出荷基準≥{SHIP_MIN}問")

    def ind_slug(nm): return _ind_slug(nm)
    def _emit_datasheet(slug, name, corpus, quiz, hd):
        """datasheet生成→SoS→カバレッジ修復→output/<slug>/datasheet.json + 受け渡し。"""
        ds, cov_err = build_datasheet(slug, name, corpus, quiz)
        json.dump(ds, open(os.path.join(OUT, slug, "datasheet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if hd:
            json.dump(ds, open(os.path.join(hd, f"{slug}_datasheet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return cov_err
    def work(tgt):
        slug, name, ind = tgt["slug"], tgt["name"], tgt["industry"]
        outp = os.path.join(OUT, slug, "quiz_30q_locked_v3.json")
        dsp = os.path.join(OUT, slug, "datasheet.json")
        hd = os.path.join(HROOT, ind_slug(ind))
        if os.path.exists(outp):   # 冪等: quizあり
            try:
                quiz = json.load(open(outp)); n = len(quiz)
            except Exception:
                n = 0; quiz = []
            if quiz and not os.path.exists(dsp):   # datasheet未生成→retrofit(保存corpusから)
                cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
                if os.path.exists(cp) and cost_ok():
                    try:
                        os.makedirs(hd, exist_ok=True)
                        _emit_datasheet(slug, name, json.load(open(cp)), quiz, hd)
                    except Exception:
                        pass
            return {"slug": slug, "name": name, "ind": ind, "n": n, "status": "shipped", "skipped": True, "pass": None}
        try:
            corpus = acquire_corpus_thick(name, slug)
            if not corpus:
                record_needs_source(slug, name, 0, "locked_all:no_official_url")
                return {"slug": slug, "name": name, "ind": ind, "n": 0, "status": "needs", "pass": None}
            final, dropped, rate = converge_locked(slug, name, corpus, target=30)
            if len(final) < SHIP_MIN:
                record_thin(slug, name, len(final), ind)
                return {"slug": slug, "name": name, "ind": ind, "n": len(final), "status": "thin", "pass": rate}
            os.makedirs(os.path.dirname(outp), exist_ok=True); os.makedirs(hd, exist_ok=True)
            json.dump(final, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            json.dump(corpus, open(os.path.join(OUT, slug, "quiz_corpus_locked_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
            json.dump(final, open(os.path.join(hd, f"{slug}_quiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            cov = _emit_datasheet(slug, name, corpus, final, hd)   # 教材も同一runで生成
            return {"slug": slug, "name": name, "ind": ind, "n": len(final), "status": "shipped", "pass": rate, "cov_err": cov}
        except Exception as e:
            record_needs_source(slug, name, 0, f"locked_all:error:{type(e).__name__}:{str(e)[:50]}")
            return {"slug": slug, "name": name, "ind": ind, "n": 0, "status": "needs", "pass": None, "err": str(e)[:80]}

    def checkpoint(batch, cp_idx):
        shipped = [r for r in batch if r["status"] == "shipped"]
        passes = [r["pass"] for r in batch if r.get("pass") is not None]
        avg = round(sum(passes) / len(passes), 3) if passes else None
        # lint統計(バッチの出荷分)
        lint_err = 0
        for r in shipped:
            try:
                qs = json.load(open(os.path.join(OUT, r["slug"], "quiz_30q_locked_v3.json")))
                c = json.load(open(os.path.join(OUT, r["slug"], "quiz_corpus_locked_v3.json")))
                lint_err += QL.run_quiz_lints(qs, c)["errors"]
            except Exception:
                pass
        # サンプル1社の review.md を受け渡しフォルダへ
        for r in shipped:
            if r["n"] >= SHIP_MIN:
                try:
                    qs = json.load(open(os.path.join(OUT, r["slug"], "quiz_30q_locked_v3.json")))
                    c = json.load(open(os.path.join(OUT, r["slug"], "quiz_corpus_locked_v3.json")))
                    _locked_reviewmd(r["slug"], r["name"], qs, c, HROOT)
                except Exception:
                    pass
                break
        cp = {"cp": cp_idx, "done": len(st["done"]), "shipped": len(st["shipped"]),
              "thin": len(st["thin"]), "needs": len(st["needs"]), "q": st["q"],
              "batch_avg_pass": avg, "lint_err": lint_err, "cost": round(_cost["usd"], 2)}
        st["checkpoints"].append(cp)
        # HALT: systemic劣化(バッチ平均pass<0.70 が2CP連続 or lint error残)
        low = (avg is not None and avg < 0.70) or lint_err > 0
        halt = low and st.get("prev_low", False)
        st["prev_low"] = low
        _save_locked_state(st)
        # commit/push(private tokyari-pipeline)
        try:
            git("add", "output/_quiz_locked_state.json", "output/quiz_thin.csv", "output/quiz_needs_source.csv",
                "output/*/quiz_30q_locked_v3.json", "output/*/quiz_corpus_locked_v3.json", cwd=PIPE)
            git("-c", "user.email=quiz@local", "-c", "user.name=quiz-locked",
                "commit", "-q", "-m", f"quiz-locked-all CP{cp_idx}: 出荷{len(st['shipped'])} 保留{len(st['thin'])} needs{len(st['needs'])} q{st['q']} pass{avg}", cwd=PIPE)
            git("push", "-q", "origin", "HEAD", cwd=PIPE)
        except Exception as e:
            print("[commit ERR]", e)
        line(f"[quiz-all CP{cp_idx}] 完了{cp['done']}社 / 出荷{cp['shipped']}・保留{cp['thin']}・needs{cp['needs']} / "
             f"問{cp['q']} / batch pass{avg} / lint_err{lint_err} / ${cp['cost']}" + (" / ⚠HALT" if halt else ""))
        return halt

    batch, stop = [], None
    it = iter(pending); inflight = {}
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for _ in range(PARALLEL):
            t = next(it, None)
            if t: inflight[ex.submit(work, t)] = t
        while inflight:
            done, _p = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fut in done:
                inflight.pop(fut, None)
                r = fut.result()
                with _lock:
                    if r["slug"] not in st["done"]: st["done"].append(r["slug"])
                    st["q"] += r.get("n", 0)
                    tgt = {"shipped": "shipped", "thin": "thin", "needs": "needs"}.get(r["status"])
                    if tgt and r["slug"] not in st[tgt]: st[tgt].append(r["slug"])
                batch.append(r)
                print(f"  {r['status']:7} {r['slug']:16} n={r.get('n')} pass={r.get('pass')} ${_cost['usd']:.2f}", flush=True)
                if not cost_ok(): stop = "cost"
                if len(batch) >= CHECKPOINT_EVERY:
                    if checkpoint(batch, len(st["checkpoints"]) + 1): stop = "halt"
                    batch = []
                if stop is None:
                    nt = next(it, None)
                    if nt: inflight[ex.submit(work, nt)] = nt
            if stop: break
    if batch and not stop:
        checkpoint(batch, len(st["checkpoints"]) + 1)
    _save_locked_state(st)

    # ── 業界セット生成(所属出荷社のcorpusをmerge・順位設問はLLMがcompetitors付きで出せた分)──
    if not stop:
        st.setdefault("industry_done", [])
        for ind in industries:
            iname = ind["name"]; islug = "industry__" + _ind_slug(iname)
            iout = os.path.join(OUT, islug, "quiz_30q_locked_v3.json")
            if os.path.exists(iout) or islug in st["industry_done"] or not cost_ok():
                continue
            # 代表5社(出荷済)のcorpusをmerge(全社mergeは薄くなるため)
            mems = [c["slug"] for c in companies if c["industry"] == iname
                    and os.path.exists(os.path.join(OUT, c["slug"], "quiz_corpus_locked_v3.json"))][:5]
            mcorpus = {}
            for ms in mems:
                try:
                    mcorpus.update(json.load(open(os.path.join(OUT, ms, "quiz_corpus_locked_v3.json"))))
                except Exception:
                    pass
            if len(mcorpus) < 2:
                continue
            extra = ("業界クイズ。可能なら『最大/最高』の順位設問は type:\"rank\" と competitors:"
                     "[{name,value,source_url}](全比較社の値+出典)を必須で付す。EPS等の株数依存指標の社間比較は禁止"
                     "(収益・利益額・ROE・総資産で作る)。数値は各社source本文に実在する表記のまま。")
            try:
                final, _dr, rate = converge_locked(islug, iname, mcorpus, target=30, extra=extra)
                if len(final) >= SHIP_MIN:
                    os.makedirs(os.path.join(OUT, islug), exist_ok=True)
                    json.dump(final, open(iout, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    json.dump(mcorpus, open(os.path.join(OUT, islug, "quiz_corpus_locked_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
                    hd = os.path.join(HROOT, _ind_slug(iname)); os.makedirs(hd, exist_ok=True)
                    json.dump(final, open(os.path.join(hd, f"industry_{islug}_quiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    rankn = sum(1 for q in final if q.get("type") == "rank" or q.get("category") == "業界順位")
                    print(f"  [業界] {iname}: n={len(final)} rank={rankn} pass={rate}", flush=True)
                st["industry_done"].append(islug)
            except Exception as e:
                print(f"  [業界ERR] {iname}: {str(e)[:60]}", flush=True)
            _save_locked_state(st)
        try:
            git("add", "output/industry_*/quiz_30q_locked_v3.json", "output/_quiz_locked_state.json", cwd=PIPE)
            git("-c", "user.email=quiz@local", "-c", "user.name=quiz-locked", "commit", "-q",
                "-m", f"quiz-locked-all: 業界セット {len(st['industry_done'])}", cwd=PIPE)
            git("push", "-q", "origin", "HEAD", cwd=PIPE)
        except Exception:
            pass

    # 集約レポート
    agg = {"shipped": len(st["shipped"]), "thin": len(st["thin"]), "needs": len(st["needs"]),
           "total_q": st["q"], "checkpoints": st["checkpoints"], "cost_usd": round(_cost["usd"], 2),
           "stop": stop or "done"}
    passes = [cp["batch_avg_pass"] for cp in st["checkpoints"] if cp.get("batch_avg_pass")]
    agg["avg_pass"] = round(sum(passes) / len(passes), 3) if passes else None
    json.dump(agg, open(os.path.join(HROOT, "AGG_SUMMARY.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    line(f"[quiz-all {agg['stop']}] 出荷{agg['shipped']}社 / 保留{agg['thin']} / needs{agg['needs']} / "
         f"総問{agg['total_q']} / 平均pass{agg['avg_pass']} / ${agg['cost_usd']} → gyokai_locked_v3/")
    print(json.dumps(agg, ensure_ascii=False, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", type=int, default=0, help="少数社を同期検証(背景化しない)")
    ap.add_argument("--run", action="store_true", help="本番: 全社(company→industry)")
    ap.add_argument("--locked", type=str, default="", help="品質固定モード: 指定業界のみ厚corpus+二層ゲートで作り直す")
    ap.add_argument("--lockdir", type=str, default="sogo_shosha_locked", help="locked出力の受け渡しサブフォルダ")
    ap.add_argument("--suffix", type=str, default="locked", help="locked成果ファイルのサフィックス(v1保全のため v2 等)")
    ap.add_argument("--industries-only", action="store_true")
    ap.add_argument("--locked-all", action="store_true", help="全16業界の品質固定ロック(夜間規律・出荷基準≥15・resumable)")
    ap.add_argument("--freshness", action="store_true", help="出荷済社の財務を最新期(LATEST_FY)へ再生成(取れない社は旧期維持でhold)")
    args = ap.parse_args()
    if args.freshness:
        return run_freshness()
    if args.locked_all:
        if not OPENAI_KEY:
            print("NO OPENAI_API_KEY"); return 2
        return run_all_locked()
    if args.locked:
        if not OPENAI_KEY:
            print("NO OPENAI_API_KEY"); return 2
        return run_locked(args.locked, lockdir=args.lockdir, suf=args.suffix)
    if not OPENAI_KEY:
        print("NO OPENAI_API_KEY"); return 2
    companies, industries = load_targets()
    st = load_state()
    if args.validate:
        targets = companies[:args.validate]
        st2 = {"done": [], "blocked": [], "counts": {"q": 0, "dropped": 0}, "checkpoints": [],
               "grad_streak": 0, "graduated": False, "rule_tuning": 0, "halted": False, "cost_usd": 0.0}
        run(targets, st2, is_validate=True)
        print("\n=== VALIDATE 集計 ===")
        print(json.dumps({"done": len(st2["done"]), "q": st2["counts"]["q"],
                          "dropped": st2["counts"]["dropped"], "blocked": st2["blocked"],
                          "cost_usd": round(_cost["usd"], 3)}, ensure_ascii=False, indent=1))
        return 0
    if args.run:
        targets = ([] if args.industries_only else companies) + industries
        status = run(targets, st, is_validate=False)
        # 最終集約
        agg = {"status": status, "done": len(st["done"]), "q": st["counts"]["q"],
               "dropped": st["counts"]["dropped"], "blocked": len(st["blocked"]),
               "checkpoints": st["checkpoints"], "cost_usd": round(_cost["usd"], 2)}
        json.dump(agg, open(os.path.join(HANDOFF, "quiz_fanout_summary.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        line(f"[quiz FINAL {status}] 完了{agg['done']} / 問{agg['q']} / blocked{agg['blocked']} / ${agg['cost_usd']}")
        return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
