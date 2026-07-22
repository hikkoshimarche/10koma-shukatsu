#!/usr/bin/env python3
"""datasheet 質的増強: 採用ページ・会社概要・理念corpusから 事業/強み/社風/求める人物像/理念 の
散文factを追加取得し、datasheetの質的セクションを厚く再生成。主要財務は温存。
浄化(否定形/答え捏造drop)＋意味検証(出典本文が主張をその向きで支持するか)を配線=再汚染しない。
出力: output/<slug>/datasheet.json を更新。--pilot でmd も。resumable(既増強はskip)・CP20・$100ガード。
"""
import json, os, sys, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import clean_datasheets as CL
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")
PARALLEL = 3
CP_EVERY = 20
QUAL_KW = ("recruit", "saiyo", "company", "corporate", "about", "philosophy", "vision",
           "mission", "culture", "people", "sustainability", "csr", "profile", "value", "story")
QUAL_PATHS = ["/company/", "/company/about/", "/corporate/", "/about/", "/recruit/", "/saiyo/",
              "/company/philosophy/", "/philosophy/", "/vision/", "/sustainability/", "/company/vision/"]

DSQ_SYS = (
 "あなたは就活生向け企業データシートの編集者です。提供された企業の公式一次情報(採用ページ・会社概要・理念等)の"
 "本文だけを根拠に、質的な事実を『完全な文』で列挙します。"
 "絶対規則: (1)本文に実在する内容のみ(捏造・推測・別社の情報を混ぜない)。(2)『○○: X』の穴埋め形式や"
 "クイズ的な列挙にしない=主語述語のある自然な文。(3)倍率・順位の断定をしない。(4)所在地/資本金/株式数/"
 "従業員数などの登記数値は書かない(質的内容に集中)。各factにsource_url。")
DSQ_USER = (
 "企業: {name}\n以下は公式の質的ページ本文(URL付き)。ここに実在する内容だけで質的factを作る。\n\n{sources}\n\n"
 "出力JSON(厳守): {{\"facts\":[{{\"section\":\"事業内容・セグメント|社風・求める人物像|沿革・基本情報\","
 "\"fact\":\"完全な文\",\"source_url\":\"<上記URL>\"}}]}}\n"
 "各section 3〜6文を目安。事業内容=何をする会社か/強み・特徴。社風・求める人物像=価値観/文化/人材像/理念。"
 "沿革=創業・歴史・転機。数値羅列や登記情報は不要。穴埋め形式禁止。")


def _domains(corpus):
    d = []
    for u in corpus:
        m = re.search(r"(https?://[^/]+)", u)
        if m and m.group(1) not in d:
            d.append(m.group(1))
    return d


def _links(html, base):
    out = []
    for m in re.findall(r'href=["\']([^"\']+)["\']', html or ""):
        u = m
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            u = base + u
        elif not u.startswith("http"):
            continue
        if any(k in u.lower() for k in QUAL_KW) and not u.lower().endswith((".pdf", ".jpg", ".png", ".zip")):
            out.append(u.split("#")[0])
    return out


def gather_prose(slug, name):
    """質的ページ本文を収集(既知URL + パス推測 + 1段リンク展開)。"""
    base_corpus = {}
    cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
    known = json.load(open(cp)) if os.path.exists(cp) else {}
    doms = _domains(known)
    seeds = [u for u in known if any(k in u.lower() for k in QUAL_KW)]           # 既知の質的URL
    for d in doms[:2]:
        seeds += [d + p for p in QUAL_PATHS]                                     # パス推測
    prose, seen, crawl_more = {}, set(), []
    for u in dict.fromkeys(seeds):
        if u in seen or len(prose) >= 8:
            continue
        seen.add(u)
        body = known.get(u) or q.fetch_url(u)
        if body and len(body) > 400 and not re.search(r"決算|短信|有価証券報告", body[:300]):
            prose[u] = body
            crawl_more += _links(q.fetch_url(u) if u not in known else "", doms[0] if doms else "")
    for u in dict.fromkeys(crawl_more):                                          # 1段リンク展開
        if u in seen or len(prose) >= 10:
            continue
        seen.add(u)
        body = q.fetch_url(u)
        if body and len(body) > 400 and not re.search(r"決算|短信", body[:300]):
            prose[u] = body
    return prose


def gen_qual_facts(name, prose):
    src = "\n\n".join(f"===== source_url: {u} =====\n{b[:3500]}" for u, b in list(prose.items())[:8])
    txt = q.openai_chat([{"role": "system", "content": DSQ_SYS},
                         {"role": "user", "content": DSQ_USER.format(name=name, sources=src)}],
                        max_tokens=2000, temperature=0.2)
    data = q._parse_json(txt)
    return data.get("facts", []) if isinstance(data, dict) else []


def enrich_one(slug):
    dp = os.path.join(OUT, slug, "datasheet.json")
    if not os.path.exists(dp):
        return {"slug": slug, "status": "no_datasheet"}
    ds = json.load(open(dp))
    name = ds.get("name", slug)
    prose = gather_prose(slug, name)
    if len(prose) < 1:
        return {"slug": slug, "status": "no_prose"}
    facts = gen_qual_facts(name, prose)
    ctext = CL._corpus_text(prose)
    cd = re.sub(r"\D", "", ctext)
    # 浄化(否定形/答え捏造)＋意味検証
    clean = []
    for f in facts:
        txt = (f.get("fact") or "").strip()
        sec = f.get("section", "")
        su = f.get("source_url", "")
        if not txt or sec not in CL.PROSE_SECTIONS:
            continue
        if CL._NEG_SHAPE.search(txt) or not CL._answer_ok(txt, ctext, cd):
            continue
        clean.append({"section": sec, "fact": txt, "source_url": su if su in prose else (list(prose)[0])})
    verds = _verify([c["fact"] for c in clean], prose) if clean else []
    clean = [c for c, ok in zip(clean, verds) if ok]
    if not clean:
        return {"slug": slug, "status": "no_qual_facts", "prose": len(prose)}
    # マージ: 質的3セクションを「既存の生き残り(浄化後) + 新規」で置換。主要財務は温存。
    sec = ds.setdefault("sections", {})
    bysec = {}
    for c in clean:
        bysec.setdefault(c["section"], []).append({"fact": c["fact"], "source_url": c["source_url"]})
    def _nkey(f):
        return re.sub(r"[\s、。「」()（）・,.]", "", f)[:26]   # 句読点/空白無視の重複キー
    added = 0
    for k in CL.PROSE_SECTIONS:
        old = [it for it in sec.get(k, []) if not CL._NEG_SHAPE.search(it.get("fact", ""))
               and CL._answer_ok(it.get("fact", ""), ctext, cd)]
        seen = set()
        merged = []
        for it in old + bysec.get(k, []):              # old→new順で正規化dedup(new内の近重複も除去)
            key = _nkey(it.get("fact", ""))
            if key in seen:
                continue
            seen.add(key)
            merged.append(it)
        added += max(0, len(merged) - len(old))
        sec[k] = merged
    json.dump(ds, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 実質材料(登記系/財務除く散文)数
    subst = sum(1 for k in CL.PROSE_SECTIONS for it in sec.get(k, [])
                if not re.search(r"本店|所在地|資本金|従業員数|女性比率|株式数|代表取締役|社長|役員", it.get("fact", "")))
    return {"slug": slug, "status": "ok", "prose": len(prose), "added": added, "substantive": subst}


def _snip(fact, ctext, width=360):
    for t in sorted(set(re.findall(r"[一-龥ァ-ヶーA-Za-z]{2,}", fact)), key=len, reverse=True):
        i = ctext.find(t)
        if i >= 0:
            s = max(0, i - width // 2)
            return ctext[s:s + width]
    return ""


def _verify(facts, prose):
    if not facts:
        return []
    ctext = CL._corpus_text(prose)
    items = "\n".join(f"[{i}] 主張:「{f}」\n    本文抜粋: {_snip(f, ctext)}"
                      for i, f in enumerate(facts))
    VSYS = ("出典本文が主張をその向きで支持するか判定する校閲者。本文に無い内容・向きが逆・別社の情報は不支持。")
    VUSER = "各主張を判定:\n" + items + "\n出力JSON: {\"verdicts\":[{\"idx\":<番号>,\"supported\":true/false}]}"
    data = q._parse_json(q.openai_chat([{"role": "system", "content": VSYS}, {"role": "user", "content": VUSER}],
                                       max_tokens=1200, temperature=0))
    sup = {v["idx"]: bool(v.get("supported")) for v in (data.get("verdicts", []) if isinstance(data, dict) else [])
           if isinstance(v.get("idx"), int)}
    return [sup.get(i, False) for i in range(len(facts))]


def main():
    import glob
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allslugs = sorted(os.path.basename(os.path.dirname(d)) for d in glob.glob(os.path.join(OUT, "*/datasheet.json"))
                      if not os.path.basename(os.path.dirname(d)).startswith("industry__"))
    stp = os.path.join(OUT, "_enrich_state.json")
    st = json.load(open(stp)) if os.path.exists(stp) else {"done": [], "ok": [], "cost": 0.0, "cp": 0}
    with q._lock:
        q._cost["usd"] = st.get("cost", 0.0)
    targets = args if args else [s for s in allslugs if s not in set(st["done"])]   # resumable
    q.line(f"📝 datasheet質的増強 開始/再開: 対象{len(targets)}社(全{len(allslugs)}・完了{len(st['done'])}) / 並列{PARALLEL}・${q.MAX_USD}ガード")
    results, batch = [], []

    def checkpoint():
        st["cost"] = round(q._cost["usd"], 4)
        st["cp"] += 1
        json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False)
        try:
            q.git("add", "output/*/datasheet.json", "output/_enrich_state.json", cwd=q.PIPE)
            q.git("-c", "user.email=quiz@local", "-c", "user.name=quiz-enrich", "commit", "-q",
                  "-m", f"enrich CP{st['cp']}: 増強{len(st['ok'])}/{len(st['done'])}社 ${st['cost']}", cwd=q.PIPE)
            q.git("push", "-q", "origin", "HEAD", cwd=q.PIPE)
        except Exception as e:
            print("[commit ERR]", e)
        q.line(f"[増強CP{st['cp']}] 完了{len(st['done'])}/{len(allslugs)} 増強OK{len(st['ok'])} ${st['cost']:.2f}")

    stop = None
    it = iter(targets); inflight = {}
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for _ in range(PARALLEL):
            t = next(it, None)
            if t: inflight[ex.submit(enrich_one, t)] = t
        while inflight:
            done, _p = wait(list(inflight), return_when=FIRST_COMPLETED)
            for fu in done:
                inflight.pop(fu, None)
                r = fu.result()
                results.append(r); batch.append(r)
                with q._lock:
                    if r["slug"] not in st["done"]: st["done"].append(r["slug"])
                    if r["status"] == "ok" and r["slug"] not in st["ok"]: st["ok"].append(r["slug"])
                print(f"  {r['status']:12} {r['slug']:16} prose={r.get('prose')} 追加={r.get('added')} 実質={r.get('substantive')} ${q._cost['usd']:.2f}", flush=True)
                if not q.cost_ok(): stop = "cost"
                if len(batch) >= CP_EVERY:
                    checkpoint(); batch = []
                if stop is None:
                    nt = next(it, None)
                    if nt: inflight[ex.submit(enrich_one, nt)] = nt
            if stop: break
    if batch:
        checkpoint()
    json.dump(st, open(stp, "w", encoding="utf-8"), ensure_ascii=False)
    ok = [r for r in results if r["status"] == "ok"]
    q.line(f"[増強 {stop or 'done'}] 今回OK{len(ok)}/{len(results)} 累計増強{len(st['ok'])}/{len(st['done'])} ${q._cost['usd']:.2f}")
    print(f"=== 増強OK {len(ok)}/{len(results)} 累計{len(st['ok'])} ===")


if __name__ == "__main__":
    main()
