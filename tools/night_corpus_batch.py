#!/usr/bin/env python3
"""夜間バッチ第1便: クイズ未対応社のcorpus収集(公式サイト ヘッドレス+PDF)＋製品URLレジストリ全社展開。
収集のみ(生成なし)・本番D1/ページ不変・OpenAI不使用。マナー厳守(同一ホスト逐次1req/秒・キャッシュ)。
checkpoint方式(_night_corpus_state.json)で中断/再開可能。1社失敗で全体停止しない。
段: (1)未対応社の公式ドメイン解決(DDG検索・キャッシュ) (2)render_official_pages で各社クロール
   (3)build_product_urls 全社展開。
"""
import sys, os, re, json, time, subprocess, urllib.parse, datetime

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
PIPE = os.path.expanduser("~/oscar-ai/tokyari-pipeline")
VENV = os.path.join(PIPE, ".venv/bin/python")
DOMAINS = os.path.join(OUT, "_official_domains.json")
STATE = os.path.join(OUT, "_night_corpus_state.json")
NAMES = "/tmp/uncovered_names.json"

AGG = ["wikipedia", "yahoo", "note.com", "kabutan", "minkabu", "nikkei", "prtimes", "facebook",
       "twitter", "x.com", "instagram", "youtube", "linkedin", "indeed", "rikunabi", "mynavi",
       "en-japan", "openwork", "vorkers", "wantedly", "baseconnect", "alarmbox", "houjin",
       "ullet", "buffett-code", "job-", "tenshoku", "doda", "green-japan", "amazon.co.jp/gp"]


def log(m):
    line = f"[{datetime.datetime.now():%H:%M:%S}] {m}"
    print(line, flush=True)


def ddg(query):
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "25", "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                            "https://html.duckduckgo.com/html/", "--data-urlencode", f"q={query}"],
                           capture_output=True, timeout=35)
        t = r.stdout.decode("utf-8", "ignore")
        urls = [urllib.parse.unquote(u) for u in re.findall(r"uddg=([^&\"]+)", t)]
        out = []
        for u in urls:
            if any(a in u.lower() for a in AGG):
                continue
            out.append(u)
        return out
    except Exception:
        return []


def resolve_domain(slug, name):
    for q in (f"{name} 公式サイト 会社概要", f"{name} コーポレートサイト", f"{name} 企業情報"):
        for u in ddg(q):
            m = re.match(r"(https?://[^/]+)", u)
            if not m:
                continue
            host = m.group(1)
            # 企業ドメインらしさ(co.jp/com/.jp/.co 等・検索/辞書系除外)
            if re.search(r"\.(co\.jp|com|jp|co|inc|net|group)(/|$)", host) and not any(a in host.lower() for a in AGG):
                return host
        time.sleep(1)
    return None


def main():
    names = json.load(open(NAMES))
    targets = sorted(names)
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"done": [], "pages": {}, "fail": [], "dom_fail": []}
    domains = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}
    log(f"夜間corpus収集 開始/再開: 対象{len(targets)}社 完了{len(st['done'])}")
    for i, slug in enumerate(targets):
        if slug in st["done"]:
            continue
        name = names[slug]
        try:
            # (1) ドメイン(事前解決済みのみ使用。当環境はDDG検索がブロックされるため未解決社はskip記録)
            if not domains.get(slug):
                st["dom_fail"].append(slug); st["done"].append(slug)
                log(f"  {slug}({name}): ドメイン未解決→skip")
                continue
            # (2) クロール(render_official_pages・venv・別プロセス隔離)
            r = subprocess.run([VENV, "scripts/render_official_pages.py", slug], cwd=PIPE,
                               capture_output=True, text=True, timeout=600)
            cf = os.path.join(OUT, slug, "rendered_corpus.json")
            n = len(json.load(open(cf))) if os.path.exists(cf) else 0
            st["pages"][slug] = n
            if n == 0:
                st["fail"].append(slug)
            st["done"].append(slug)
            log(f"  {slug}({name}) dom={domains.get(slug)} 頁={n}  [{i+1}/{len(targets)}]")
        except Exception as e:
            st["fail"].append(slug); st["done"].append(slug)
            log(f"  {slug}: ERR {str(e)[:60]}")
        if (i + 1) % 5 == 0:
            _save(st, domains)
        time.sleep(1)                      # 社間も間隔
    _save(st, domains)
    okpages = sum(1 for s, n in st["pages"].items() if n > 0)
    log(f"収集完了: 成功{okpages}社 / 頁失敗{len(st['fail'])} / ドメイン失敗{len(st['dom_fail'])} / 総頁{sum(st['pages'].values())}")
    # (3) 製品URLレジストリ 全社展開(datasheet保有 or rendered_corpus保有社)
    log("製品URLレジストリ 全社展開...")
    import glob as _g
    files = _g.glob(OUT + "/*/datasheet.json") + _g.glob(OUT + "/*/rendered_corpus.json")
    allslugs = sorted({os.path.basename(os.path.dirname(f)) for f in files
                       if not os.path.basename(os.path.dirname(f)).startswith("industry")})
    pu = subprocess.run([sys.executable, "tools/build_product_urls.py"] + allslugs, cwd=ROOT,
                        capture_output=True, text=True, timeout=1200)
    open("/tmp/night_product_urls.log", "w").write(pu.stdout + "\n" + pu.stderr)
    log(f"製品URL 完了 (出力: /tmp/night_product_urls.log 末尾参照)")
    log("NIGHT_BATCH_DONE")


def _save(st, domains):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(domains, open(DOMAINS, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
