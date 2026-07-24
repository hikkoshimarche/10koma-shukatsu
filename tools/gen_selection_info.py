#!/usr/bin/env python3
"""選考情報(selection_info)パイロット: 公式採用ページから 選考フロー/スケジュール/募集職種 を構造化抽出。
鉄則: 出典=公式採用ページのみ(口コミ/就活サイト禁止)。全項目に as_of + source_url。
公式に記載が無い項目は『公式採用ページで確認』にフォールバック(推測・昨年度流用は絶対禁止=締切の誤情報は学生に実害)。
grounding gate: 抽出した日付/数値/職種が元ページ本文に実在しないと不採用(フォールバックへ降格)。
成果物: output/<slug>/selection_info.json + 受け渡し md(sha8)。本番D1反映はレビュー承認後(別途)。
"""
import sys, os, json, re, hashlib, datetime, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")
DISCLAIMER = "※取得日時点の情報です。応募前に必ず公式採用ページで最新情報をご確認ください。"
TODAY = datetime.date(2026, 7, 24)
FRESH_FLOOR = TODAY - datetime.timedelta(days=60)     # 直近有効(取得日から過去60日)
# 新卒採用ページ優先 / 中途・アルバイト等は除外(新卒スコープ限定)
_NEWGRAD_URL = re.compile(r"graduate|shinsotsu|shinsotu|newgrad|new-?grad|fresh|新卒|recruit/?$|saiyo/?$", re.I)
_NONGRAD_URL = re.compile(r"midcareer|mid-career|career(?!s)|carrier|chuto|中途|part|arbeit|baito|アルバイト|"
                          r"kikan|handicap|challenged|障が|高校|highschool", re.I)
_NONGRAD_WORD = re.compile(r"中途|キャリア採用|経験者|アルバイト|パート|高校生|障がい|障害者|第二新卒(?!.*新卒)")
# 採用カテゴリ(職種でない)=誤認防止
_CATEGORY = re.compile(r"^(新卒採用|キャリア採用|中途採用|通年採用|障がい者採用|アルバイト|インターン(シップ)?|"
                       r"採用情報|エントリー|マイページ)$")

SYS = ("あなたは公式採用ページから『新卒採用』の選考情報のみを抽出する担当です。厳守:"
       "(1)提供テキストに明記された事実のみ。書いていない項目は必ず null(推測・前年度流用は禁止=締切の誤りは重大)。"
       "(2)対象は新卒採用のみ。中途/キャリア/アルバイト/高校生/障がい者採用の情報は抽出しない(混在時は除外)。"
       "(3)選考フロー(ES→適性検査→面接回数等の順序)、スケジュール(エントリー開始/締切/説明会等の日付。対象卒年度27卒/28卒が分かれば付与)、"
       "募集職種・コース(技術系/事務系/研究職等。『新卒採用/キャリア採用』などの採用カテゴリ名は職種でないので除外)。"
       "(4)日付・数値・職種名は本文の表記のまま。")
USER = ("会社名: {name}\n公式新卒採用ページ本文(抜粋):\n{body}\n\n"
        "JSON: {{\"senko_flow\":[\"..\"]|null, \"schedule\":[{{\"label\":\"..\",\"date\":\"..\",\"grad_year\":\"27卒|28卒|\"}}]|null, "
        "\"shokushu\":[\"..\"]|null}}  (新卒に該当しない/本文に無いキーは null)")

_DATEISH = re.compile(r"\d{1,4}[年/月.\-]\d{1,2}|\d{1,2}月\d{1,2}日|上旬|中旬|下旬|締切|エントリー|\d+回|\d+次")


def _curl(url):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "12", "-A", "Mozilla/5.0", url], capture_output=True, timeout=15)
        return r.stdout.decode("utf-8", "ignore")
    except Exception:
        return ""


def _html_text(html):
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _deep_dive(seed_urls):
    """採用トップHTMLから 募集要項/選考フロー/新卒 の下層リンクを1-2層辿り本文を追加(新卒優先・中途除外)。"""
    add_text, add_urls = [], []
    for seed in seed_urls[:2]:
        html = _curl(seed)
        if not html:
            continue
        base = re.match(r"(https?://[^/]+)", seed).group(1)
        for m in re.findall(r'href="([^"#]+)"', html):
            lu = m if m.startswith("http") else (base + m if m.startswith("/") else None)
            if not lu or base not in lu:
                continue
            if _NONGRAD_URL.search(lu):
                continue
            if re.search(r"boshu|募集要項|youkou|entry|flow|選考|senko|graduate|shinsotsu|newgrad|guideline|schedule", lu, re.I):
                if lu not in add_urls and len(add_urls) < 3:
                    t = _html_text(_curl(lu))
                    if len(t) > 300:
                        add_text.append(t[:4000]); add_urls.append(lu)
    return add_text, add_urls


def _recruit_text(slug):
    """新卒採用ページ本文(優先)＋深掘り下層。中途/アルバイト等は除外。返: (text, urls, asof, is_newgrad)."""
    seed, asof = [], ""
    for fn in ("rendered_corpus.json", "quiz_corpus_locked_v3.json"):
        f = os.path.join(OUT, slug, fn)
        if not os.path.exists(f):
            continue
        rc = json.load(open(f))
        for u in rc:
            if _NONGRAD_URL.search(u):
                continue
            if re.search(r"recruit|saiyo|採用|shinsotsu|newgrad|entry|senko|選考|fresh|graduate", u, re.I):
                v = rc[u]
                seed.append((u, v.get("text", "") if isinstance(v, dict) else v))
                asof = (v.get("as_of", "") if isinstance(v, dict) else "") or asof
        if seed:
            break
    if not seed:
        return "", [], str(TODAY), False, []
    # 新卒URLを優先順に
    seed.sort(key=lambda x: 0 if _NEWGRAD_URL.search(x[0]) else 1)
    urls = [u for u, _ in seed]
    parts = [t for _, t in seed]
    url_texts = [(u, t) for u, t in seed]
    # 深掘り(募集要項/選考フロー下層)
    dtext, durls = _deep_dive(urls)
    parts += dtext; urls += durls
    url_texts += list(zip(durls, dtext))
    is_newgrad = any(_NEWGRAD_URL.search(u) for u in urls) or bool(re.search(r"新卒|graduate|shinsotsu", " ".join(parts)))
    return " ".join(parts)[:7000], urls, (asof or str(TODAY)), is_newgrad, url_texts


def _grounded(val, body):
    """抽出値内の日付/数値表現が本文に実在するか(1つでも不在なら False=フォールバック降格)。"""
    s = val if isinstance(val, str) else json.dumps(val, ensure_ascii=False)
    for m in _DATEISH.findall(s):
        core = re.sub(r"[年/月.\-日]", "", m)
        if core and core.isdigit() and core not in re.sub(r"[^\d]", "", body):
            return False
    return True


def _schedule_fresh(v, body):
    """date必須・未来 or 直近有効(過去60日以内)のみ採用。date無し/過去年度の告知ログは除外。"""
    out = []
    for it in (v or []):
        if not isinstance(it, dict):
            continue
        dt = str(it.get("date") or "").strip()
        if not dt or dt.lower() == "null":            # date必須(null項目はフォールバック扱い)
            continue
        ym = re.search(r"(20\d\d)\D+(\d{1,2})(?:\D+(\d{1,2}))?", dt)
        keep = True
        if ym:
            y, mo, da = int(ym.group(1)), int(ym.group(2)), int(ym.group(3) or 1)
            try:
                d0 = datetime.date(y, mo, da)
                keep = d0 >= FRESH_FLOOR          # 未来 or 直近60日
            except ValueError:
                keep = y >= TODAY.year
        elif re.search(r"20(19|2[0-4])", dt):     # 明示的に過去年(2024以前)
            keep = False
        if _NONGRAD_WORD.search(str(it.get("label", ""))):
            keep = False
        if keep:
            out.append(it)
    return out


def _evidence(values, url_texts):
    """抽出値の識別トークンが『どのURLの本文のどこ』にあるかを特定し、前後数行(verbatim)＋その具体URLを返す。監査用恒久証拠。"""
    pieces = []
    for v in (values or []):
        toks = [str(v.get("label", "")), str(v.get("date", ""))] if isinstance(v, dict) else [str(v)]
        for tok in toks:
            for pc in re.split(r"[（）()・/、\s]", tok):
                pc = pc.strip()
                if len(pc) >= 2:
                    pieces.append(pc)
    pieces = list(dict.fromkeys(pieces))
    best_cov, best_seg, best_url = 0, "", ""
    for url, text in (url_texts or []):
        # 各トークン位置を集め、±180字窓で最多トークンを覆う箇所を採用(被覆度重視=関係箇所を掴む)
        positions = sorted(text.find(pc) for pc in pieces if text.find(pc) >= 0)
        for anchor in positions:
            win = text[anchor:anchor + 260]
            cov = sum(1 for pc in pieces if pc in win)
            if cov > best_cov:
                best_cov, best_seg, best_url = cov, text[max(0, anchor - 40):anchor + 260], url
    return {"excerpt": re.sub(r"\s+", " ", best_seg).strip()[:320], "source_url": best_url, "token_coverage": best_cov}


def _norm_job(x):
    return re.sub(r"([^（）\s]+)＝([^（）\s]+)", r"\1（\2）", x.strip())   # 編集＝記者→編集（記者）


def _clean_shokushu(v):
    return [_norm_job(x) for x in (v or []) if isinstance(x, str) and not _CATEGORY.match(x.strip()) and not _NONGRAD_WORD.search(x)]


def gen_one(slug, name):
    body, urls, asof, is_newgrad, url_texts = _recruit_text(slug)
    src = next((u for u in urls if _NEWGRAD_URL.search(u)), urls[0] if urls else "")
    fb = {"fallback": f"公式採用ページで確認: {src}"} if src else {"fallback": "公式採用ページで確認"}
    # 新卒ページに到達できない(中途のみ)/本文薄い → 表示は採用リンク1本のみ(空カード禁止)
    if len(body) < 200 or not is_newgrad:
        return {"slug": slug, "name": name, "status": "link_only",
                "selection_info": {"as_of": asof, "source_url": src, "link_only": True, "disclaimer": DISCLAIMER, "freshness_days": 45},
                "reason": "新卒ページ未到達/本文薄" }
    txt = q.openai_chat([{"role": "system", "content": SYS},
                         {"role": "user", "content": USER.format(name=name, body=body[:5500])}],
                        max_tokens=800, temperature=0.1)
    d = q._parse_json(txt) or {}
    info = {"as_of": asof, "source_url": src, "disclaimer": DISCLAIMER, "freshness_days": 45}
    dropped, fbcount = [], 0
    # 選考フロー(evidence必須=本文抜粋+具体URLを保存・監査用)
    v = d.get("senko_flow")
    ev = _evidence(v, url_texts) if v else {"excerpt": "", "source_url": ""}
    if v and _grounded(v, body) and ev.get("token_coverage",0) >= 2:       # 抜粋が取れないもの=証拠なし→フォールバック
        info["senko_flow"] = v
        info["senko_flow_evidence"] = ev
    else:
        info["senko_flow"] = fb; fbcount += 1
        if v: dropped.append("選考フロー")
    # スケジュール(鮮度フィルタ + evidence必須)
    sv = _schedule_fresh(d.get("schedule"), body)
    ev2 = _evidence(sv, url_texts) if sv else {"excerpt": "", "source_url": ""}
    if sv and _grounded(sv, body) and ev2.get("token_coverage",0) >= 1:
        info["schedule"] = sv
        info["schedule_evidence"] = ev2
    else:
        info["schedule"] = fb; fbcount += 1
        if d.get("schedule"): dropped.append("スケジュール(古い/非新卒)")
    # 募集職種(カテゴリ誤認除去)
    kv = _clean_shokushu(d.get("shokushu"))
    if kv and _grounded(kv, body):
        info["shokushu"] = kv
    else:
        info["shokushu"] = fb; fbcount += 1
        if d.get("shokushu"): dropped.append("職種(カテゴリ誤認)")
    # 表示価値ガード: 3項目すべてフォールバック → 採用リンク1本のみ(空カード禁止)
    status = "link_only" if fbcount == 3 else "ok"
    if status == "link_only":
        info = {"as_of": asof, "source_url": src, "link_only": True, "disclaimer": DISCLAIMER, "freshness_days": 45}
    json.dump({"slug": slug, "name": name, "selection_info": info},
              open(os.path.join(OUT, slug, "selection_info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"slug": slug, "name": name, "status": status, "selection_info": info, "grounding_dropped": dropped}


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if "--from" in sys.argv:                          # スラグlist(JSON)から
        slugs = json.load(open(sys.argv[sys.argv.index("--from") + 1]))
    if "--all" in sys.argv:                          # ドメイン解決済み(corpus保有)全社
        import glob
        slugs = sorted({os.path.basename(os.path.dirname(f)) for f in
                        glob.glob(OUT + "/*/rendered_corpus.json") + glob.glob(OUT + "/*/quiz_corpus_locked_v3.json")
                        if not os.path.basename(os.path.dirname(f)).startswith("industry")})
    if not force:                                     # resumable: 生成済はskip
        slugs = [s for s in slugs if not os.path.exists(os.path.join(OUT, s, "selection_info.json"))]
    q.line(f"🧭 選考情報 展開: {len(slugs)}社 (公式採用ページのみ・新卒限定・推測禁止・grounding gate)")
    names = json.load(open("/tmp/uncovered_names.json")) if os.path.exists("/tmp/uncovered_names.json") else {}
    # companies.jsonの名前も
    try:
        cj = json.load(open("/Users/oscardodds/projects/10koma-shukatsu/public/companies.json"))
        for _i, cs in cj.items():
            for c in cs:
                names.setdefault(c["id"], c["name"])
    except Exception:
        pass
    out = []
    for s in slugs:
        try:
            r = gen_one(s, names.get(s, s))
        except Exception as e:
            r = {"slug": s, "status": "error", "err": str(e)[:80]}
        out.append(r)
        print(f"  {s:16} {r['status']} 落ち={r.get('grounding_dropped', [])}", flush=True)
    # md
    L = ["# 選考情報 パイロット10社（Web Claude検分用）", "",
         "**出典=公式採用ページのみ**（口コミ/就活サイト禁止）。全項目 as_of+出典URL。公式に記載無しは『公式で確認→リンク』にフォールバック（**推測・昨年度流用は禁止**）。", "",
         f"**{DISCLAIMER}**", ""]
    for r in out:
        info = r.get("selection_info", {})
        L.append(f"## {r.get('name',r['slug'])}（{r['slug']}）")
        L.append(f"- 取得日: {info.get('as_of','')} / 出典: {info.get('source_url','')}")
        if r.get("status") == "link_only" or info.get("link_only"):
            L.append(f"- 選考情報ブロック: **非表示（空カード禁止）** → 「採用情報→公式リンク」1本のみ表示。理由: {r.get('reason','3項目すべて公式確認へフォールバック')}")
        else:
            for key, lab in (("senko_flow", "選考フロー"), ("schedule", "スケジュール"), ("shokushu", "募集職種")):
                v = info.get(key)
                if isinstance(v, dict) and "fallback" in v:
                    L.append(f"- {lab}: ⚠️{v['fallback']}")
                elif v:
                    L.append(f"- {lab}: {json.dumps(v, ensure_ascii=False)}")
            if r.get("grounding_dropped"):
                L.append(f"  （フォールバック降格: {r['grounding_dropped']}）")
        L.append("")
    body_md = "\n".join(L)
    sha8 = hashlib.sha256(body_md.encode()).hexdigest()[:8]
    os.makedirs(HANDOFF, exist_ok=True)
    fn = f"選考情報パイロット10社_検分用__{sha8}.md"
    open(os.path.join(HANDOFF, fn), "w", encoding="utf-8").write(body_md)
    print(f"\nmd: {fn} / cost=${round(q._cost['usd'],3)}")


if __name__ == "__main__":
    main()
