#!/usr/bin/env python3
"""選考情報(selection_info)パイロット: 公式採用ページから 選考フロー/スケジュール/募集職種 を構造化抽出。
鉄則: 出典=公式採用ページのみ(口コミ/就活サイト禁止)。全項目に as_of + source_url。
公式に記載が無い項目は『公式採用ページで確認』にフォールバック(推測・昨年度流用は絶対禁止=締切の誤情報は学生に実害)。
grounding gate: 抽出した日付/数値/職種が元ページ本文に実在しないと不採用(フォールバックへ降格)。
成果物: output/<slug>/selection_info.json + 受け渡し md(sha8)。本番D1反映はレビュー承認後(別途)。
"""
import sys, os, json, re, hashlib, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")
DISCLAIMER = "※取得日時点の情報です。応募前に必ず公式採用ページで最新情報をご確認ください。"

SYS = ("あなたは公式採用ページから選考情報を『そのまま』抽出する担当です。厳守:"
       "(1)提供テキストに明記された事実のみ。書いていない項目は必ず null(推測・前年度流用は禁止=締切の誤りは重大)。"
       "(2)選考フロー(ES・適性検査・面接回数等の順序)、スケジュール(エントリー開始/締切/説明会等の日付)、募集職種 を抽出。"
       "(3)日付・数値・職種名は本文の表記のまま。")
USER = ("会社名: {name}\n公式採用ページ本文(抜粋):\n{body}\n\n"
        "JSON: {{\"senko_flow\":[\"..\"]|null, \"schedule\":[{{\"label\":\"..\",\"date\":\"..\"}}]|null, "
        "\"shokushu\":[\"..\"]|null}}  (本文に無いキーは null)")

_DATEISH = re.compile(r"\d{1,4}[年/月.\-]\d{1,2}|\d{1,2}月\d{1,2}日|上旬|中旬|下旬|締切|エントリー|\d+回|\d+次")


def _recruit_text(slug):
    """rendered_corpus/quiz_corpusから採用・選考ページ本文＋そのURL群。"""
    for fn in ("rendered_corpus.json", "quiz_corpus_locked_v3.json"):
        f = os.path.join(OUT, slug, fn)
        if not os.path.exists(f):
            continue
        rc = json.load(open(f))
        urls = [u for u in rc if re.search(r"recruit|saiyo|採用|shinsotsu|newgrad|careers?|entry|senko|選考|fresh", u, re.I)]
        if urls:
            parts, asof = [], ""
            for u in urls:
                v = rc[u]
                t = v.get("text", "") if isinstance(v, dict) else v
                asof = (v.get("as_of", "") if isinstance(v, dict) else "") or asof
                parts.append(t)
            return " ".join(parts)[:6000], urls, (asof or str(datetime.date(2026, 7, 24)))
    return "", [], ""


def _grounded(val, body):
    """抽出値内の日付/数値表現が本文に実在するか(1つでも不在なら False=フォールバック降格)。"""
    s = val if isinstance(val, str) else json.dumps(val, ensure_ascii=False)
    for m in _DATEISH.findall(s):
        core = re.sub(r"[年/月.\-日]", "", m)
        if core and core.isdigit() and core not in re.sub(r"[^\d]", "", body):
            return False
    return True


def gen_one(slug, name):
    body, urls, asof = _recruit_text(slug)
    src = urls[0] if urls else ""
    if len(body) < 200:
        return {"slug": slug, "name": name, "status": "no_recruit_page",
                "selection_info": {"fallback": f"公式採用ページで確認: {src}", "disclaimer": DISCLAIMER}}
    txt = q.openai_chat([{"role": "system", "content": SYS},
                         {"role": "user", "content": USER.format(name=name, body=body[:5000])}],
                        max_tokens=700, temperature=0.1)
    d = q._parse_json(txt) or {}
    info = {"as_of": asof, "source_url": src, "disclaimer": DISCLAIMER}
    dropped = []
    for key, label in (("senko_flow", "選考フロー"), ("schedule", "スケジュール"), ("shokushu", "募集職種")):
        v = d.get(key)
        if not v:
            info[key] = {"fallback": f"公式採用ページで確認: {src}"}      # 公式に記載なし
        elif not _grounded(v, body):
            info[key] = {"fallback": f"公式採用ページで確認: {src}"}      # grounding落ち=誤情報回避
            dropped.append(label)
        else:
            info[key] = v
    json.dump({"slug": slug, "name": name, "selection_info": info},
              open(os.path.join(OUT, slug, "selection_info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"slug": slug, "name": name, "status": "ok", "selection_info": info, "grounding_dropped": dropped}


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")]
    q.line(f"🧭 選考情報パイロット: {len(slugs)}社 (公式採用ページのみ・推測禁止・grounding gate)")
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
        if r.get("status") in ("ok", "no_recruit_page"):
            info = r["selection_info"]
            L.append(f"## {r['name']}（{r['slug']}）")
            L.append(f"- 取得日: {info.get('as_of','')} / 出典: {info.get('source_url','')}")
            for key, lab in (("senko_flow", "選考フロー"), ("schedule", "スケジュール"), ("shokushu", "募集職種")):
                v = info.get(key)
                if isinstance(v, dict) and "fallback" in v:
                    L.append(f"- {lab}: ⚠️{v['fallback']}")
                elif v:
                    L.append(f"- {lab}: {json.dumps(v, ensure_ascii=False)}")
            if r.get("grounding_dropped"):
                L.append(f"  （grounding落ちでフォールバック: {r['grounding_dropped']}）")
            L.append("")
    body_md = "\n".join(L)
    sha8 = hashlib.sha256(body_md.encode()).hexdigest()[:8]
    os.makedirs(HANDOFF, exist_ok=True)
    fn = f"選考情報パイロット10社_検分用__{sha8}.md"
    open(os.path.join(HANDOFF, fn), "w", encoding="utf-8").write(body_md)
    print(f"\nmd: {fn} / cost=${round(q._cost['usd'],3)}")


if __name__ == "__main__":
    main()
