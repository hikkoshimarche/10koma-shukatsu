#!/usr/bin/env python3
"""ES・面接対策キット v2(静的・一回生成)。datasheet保有社対象。
v2差し戻し対応(講談社「主催する賞:ノーベル賞」=否定事実の極性反転混入 の根絶):
 (1) 極性・意味検証層: 材料はdatasheetの散文セクション(事業/社風/沿革)のみ。クイズ選択肢/否定事実形は除外。
     さらに全材料を出典corpus本文に対しLLM意味検証「本文はこの主張をこの向きで支持するか」→不支持drop。
 (2) 想定質問カテゴリwhitelist(事業・強み/社風・人物像/製品/理念のみ)。役員名/従業員数/給与/所在地等は質問化禁止。
     生成後に「面接で自然か」レビュー→不自然drop。
 (3) ヒントは型で統一(同語反復禁止)。
 (4) 登記系を除いた実質材料<5個の社は出荷保留(es_thin.csv)。
 ★完成文/模範解答は作らない(代筆回避)。出力 output/<slug>/es_kit.json。--pilot でmd。--selftest で反転検出テスト。
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")
MIN_MATERIALS = 5

STRUCTURE_TMPL = [
    "結論: なぜこの会社か(1文で言い切る)",
    "原体験: そう思ったきっかけ・自分の経験",
    "接点: 企業の事実(下の材料)と自分の経験・価値観の重なり",
    "入社後: その接点を踏まえ入社後にやりたいこと",
]
NG_EXAMPLES = [
    "どの会社にも言える抽象論(『成長できる』『社会貢献したい』だけ)",
    "待遇・福利厚生・知名度だけを理由にする",
    "事実誤認や『業界No.1』『何倍』等の未確認の断定",
    "企業の受け売りをなぞるだけで自分の経験と接続しない",
    "完成文の丸暗記(自分の言葉になっていない)",
]
# ヒントは型で統一(v2-3: 同語反復禁止・具体回答は書かない)
FIXED_HINT = "型: ①結論(この事実のどこに惹かれたか1文)→②自分の原体験→③その事実と自分の接点、を60秒で話せる順に整理する"

# 材料に使う散文セクションのみ(主要財務は除外)
_USE_SECTIONS = {"事業内容・セグメント", "社風・求める人物像", "沿革・基本情報"}
AXIS_FROM_SECTION = {"事業内容・セグメント": "事業・強み",
                     "社風・求める人物像": "社風・求める人物像",
                     "沿革・基本情報": "沿革・理念"}
# (4)登記系/(1)否定事実形は材料から除外
_DRY_FACT = re.compile(r"(本店|所在地|資本金|発行済|自己株式|株式数|女性比率|平均年齢|平均勤続|住所|郵便番号|"
                       r"代表取締役|代表者|社長|会長|役員|取締役|従業員数|初任給|給与|賞与|年収|年商|IR)")
_NEG_SHAPE = re.compile(r"でないもの|一つでない|ではない(?:もの)?|しないもの|含まない|該当しない|以外(?:のもの)?|"
                        r"やっていない|行っていない|扱っていない|展開していない|主催しない|でない[:：]")
# 財務イベント(決算短信由来)は志望動機/面接の材料に適さない=事業/強み/社風/理念の散文のみ採る
_FIN_EVENT = re.compile(r"(減損|再評価益|評価損|評価益|連結子会社化|持分法|のれん|追加投資|損失|計上|"
                        r"営業利益|純利益|経常利益|税引前|当期利益|セグメント利益|増収|減収|増益|減益|"
                        r"前期比|百万円|億円|兆円|上場している)")
RATIO = re.compile(r"[0-9０-９]+(?:\.[0-9]+)?\s*倍")

VERIFY_SYS = (
 "あなたは厳密な校閲者です。与えられた『出典本文』が『主張』を《その向きで》支持しているかだけを判定します。"
 "本文に無い固有名・数値・関係を述べた主張、向きが逆(否定を肯定に/肯定を否定に)、対象を取り違えた主張は『不支持』。"
 "本文に明示的な根拠がある場合のみ『支持』。推測で補わない。")
VERIFY_USER = (
 "各主張について、その出典本文が主張をその向きで支持するか判定せよ。\n{items}\n\n"
 "出力JSON: {{\"verdicts\":[{{\"idx\":<番号>,\"supported\":true/false,\"reason\":\"本文の該当箇所 or 不支持理由(20字)\"}}]}}")

GEN_SYS = (
 "あなたは就活生の自己分析を助けるキャリア支援者です。与えられた企業の事実(検証済)だけを使い、"
 "志望動機を『組み立てる問い』と、面接で自然に聞かれる想定質問を用意します。"
 "絶対規則: (1)新しい事実・数値・固有名を足さない。(2)完成した志望動機文や模範解答は書かない(問いのみ)。"
 "(3)倍率や未確認の断定をしない。(4)想定質問は『事業・強み/社風・求める人物像/製品/理念』に関わるものだけにし、"
 "役員名・従業員数・給与・初任給・所在地・資本金など登記情報は質問にしない。実際の面接で自然に聞かれる問いだけ。")
GEN_USER = (
 "企業: {name}\n\n以下は検証済の事実(idx付き)。これだけを根拠にする。\n{facts}\n\n"
 "出力JSON(厳守):\n"
 "{{\n"
 " \"motivation_prompts\": [{{\"idx\": <事実idx>, \"prompt\": \"就活生が自分の経験と接続するための問いかけ(20-40字・完成文は書かない)\"}}],\n"
 " \"interview_questions\": [{{\"idx\": <根拠事実idx>, \"q\": \"面接で自然に聞かれる想定質問(事業/社風/人物像/製品/理念のみ・1文)\"}}]\n"
 "}}\n"
 "motivation_prompts は各事実に1つ(最大10)。interview_questions は最大10問。idxは必ず上記のもの。登記系(役員/従業員数/給与/所在地)は質問化しない。")

NAT_SYS = "面接官の視点で、各質問が『実際の面接で自然に聞かれる質問か』を判定する。登記情報(役員名/従業員数/給与/所在地)や不自然な問いはfalse。"
NAT_USER = "各質問の自然さを判定:\n{items}\n\n出力JSON: {{\"verdicts\":[{{\"idx\":<番号>,\"natural\":true/false}}]}}"


def _snippet_for(fact, body, width=320):
    if not body:
        return ""
    b = re.sub(r"\s+", " ", body)
    # 主張中の特徴的トークン(2字以上の漢字/カナ列)で本文位置を探す
    toks = re.findall(r"[一-龥ァ-ヶー]{2,}", fact)
    for t in sorted(set(toks), key=len, reverse=True):
        i = b.find(t)
        if i >= 0:
            s = max(0, i - width // 2)
            return b[s:s + width]
    return b[:width]


def verify_materials(cands, corpus):
    """cands=[{axis,fact,source_url}] を出典本文で意味検証。支持のみ返す。"""
    if not cands:
        return []
    items = []
    for i, c in enumerate(cands):
        body = corpus.get((c.get("source_url") or "").strip(), "")
        items.append(f"[{i}] 主張:「{c['fact']}」\n    出典本文抜粋: {_snippet_for(c['fact'], body)}")
    txt = q.openai_chat([{"role": "system", "content": VERIFY_SYS},
                         {"role": "user", "content": VERIFY_USER.format(items="\n".join(items))}],
                        max_tokens=1500, temperature=0)
    data = q._parse_json(txt)
    sup = {}
    if isinstance(data, dict):
        for v in data.get("verdicts", []):
            if isinstance(v.get("idx"), int):
                sup[v["idx"]] = bool(v.get("supported"))
    return [c for i, c in enumerate(cands) if sup.get(i, False)]


def load_prose_facts(ds):
    out = []
    sec = ds.get("sections", {})
    if not isinstance(sec, dict):
        return out
    for k, items in sec.items():
        if k not in _USE_SECTIONS:
            continue
        axis = AXIS_FROM_SECTION.get(k, k)
        for it in (items or []):
            if not isinstance(it, dict):
                continue
            f = (it.get("fact") or "").strip()
            if not f or _DRY_FACT.search(f) or _NEG_SHAPE.search(f) or _FIN_EVENT.search(f):  # 登記系/否定形/財務イベントを除外
                continue
            out.append({"axis": axis, "fact": f, "source_url": it.get("source_url", "")})
    return out


def coverage_check(kit, verified):
    vf = {m["fact"] for m in verified}
    vs = {m["source_url"] for m in verified}
    errs = []
    for m in kit["motivation_sheet"]["materials"]:
        if m["fact"] not in vf:
            errs.append(f"material 非検証: {m['fact'][:26]}")
        if m["source_url"] and m["source_url"] not in vs:
            errs.append(f"source 非datasheet: {m['source_url'][:36]}")
        if RATIO.search(m.get("prompt", "")):
            errs.append("prompt倍率")
    for iq in kit["interview_questions"]:
        if RATIO.search(iq.get("q", "")):
            errs.append("iq倍率")
    return errs


def build_kit(slug, name, ds, corpus):
    cands = load_prose_facts(ds)
    verified = verify_materials(cands, corpus)                # (1) 意味検証
    if len(verified) < MIN_MATERIALS:                         # (4) 出荷保留
        return None, f"thin:実質材料{len(verified)}<{MIN_MATERIALS}", verified
    fact_lines = "\n".join(f"[{i}] ({m['axis']}) {m['fact']}" for i, m in enumerate(verified))
    txt = q.openai_chat([{"role": "system", "content": GEN_SYS},
                         {"role": "user", "content": GEN_USER.format(name=name, facts=fact_lines)}],
                        max_tokens=2200, temperature=0.3)
    data = q._parse_json(txt)
    if not isinstance(data, dict):
        return None, "parse失敗", verified
    materials = []
    for mp in data.get("motivation_prompts", []):
        i = mp.get("idx")
        if isinstance(i, int) and 0 <= i < len(verified):
            m = verified[i]
            materials.append({"axis": m["axis"], "fact": m["fact"], "source_url": m["source_url"],
                              "prompt": (mp.get("prompt") or "あなたの経験で繋がるものは？").strip()})
    raw_iqs = []
    for iq in data.get("interview_questions", []):
        i = iq.get("idx")
        if iq.get("q") and isinstance(i, int) and 0 <= i < len(verified):
            raw_iqs.append({"q": iq["q"].strip(), "based_on": {"fact": verified[i]["fact"],
                            "source_url": verified[i]["source_url"]}, "hint": FIXED_HINT})
    # (2) 自然さレビュー→不自然drop
    if raw_iqs:
        it = "\n".join(f"[{i}] {x['q']}" for i, x in enumerate(raw_iqs))
        nv = q._parse_json(q.openai_chat([{"role": "system", "content": NAT_SYS},
                          {"role": "user", "content": NAT_USER.format(items=it)}], max_tokens=800, temperature=0))
        ok = {v["idx"] for v in (nv.get("verdicts", []) if isinstance(nv, dict) else []) if v.get("natural")}
        iqs = [x for i, x in enumerate(raw_iqs) if i in ok] if ok else raw_iqs
    else:
        iqs = []
    kit = {"slug": slug, "name": name,
           "motivation_sheet": {"materials": materials, "structure_template": STRUCTURE_TMPL,
                                "ng_examples": NG_EXAMPLES},
           "interview_questions": iqs[:10]}
    errs = coverage_check(kit, verified)
    return kit, ("; ".join(errs) if errs else ""), verified


def to_md(kit):
    L = [f"# ES・面接対策キット: {kit['name']}", "",
         "> 志望動機の**材料と問い**＋想定面接質問。完成文・模範解答は載せません(自分の言葉で組み立てるため)。",
         "> 全材料は出典本文で意味検証済(本文が主張をその向きで支持するもののみ)。", ""]
    L += ["## ① 志望動機 組み立てシート", "### 構成テンプレ(型紙)"]
    for i, s in enumerate(kit["motivation_sheet"]["structure_template"], 1):
        L.append(f"{i}. {s}")
    L.append("\n### 材料(企業の事実)＋問いかけ")
    ax = None
    for m in kit["motivation_sheet"]["materials"]:
        if m["axis"] != ax:
            ax = m["axis"]; L.append(f"\n**【{ax}】**")
        L += [f"- 事実: {m['fact']}", f"  - ❓ {m['prompt']}", f"  - 出典: {m['source_url']}"]
    L.append("\n### NG例(避ける)")
    L += [f"- {n}" for n in kit["motivation_sheet"]["ng_examples"]]
    L.append("\n## ② 想定面接質問＋組み立てヒント")
    for i, iq in enumerate(kit["interview_questions"], 1):
        L.append(f"{i}. {iq['q']}")
        L.append(f"   - 💡{iq['hint']}")
    return "\n".join(L)


def selftest():
    """★ノーベル賞型の反転を意味検証が検出するか。"""
    body = ("講談社主催の賞として「講談社漫画賞」、江戸川乱歩氏を記念した「江戸川乱歩賞」、"
            "野間文芸賞などの「野間賞」があります。出版文化を担う優れた作品を顕彰しています。")
    corpus = {"http://x": body}
    cands = [{"axis": "事業・強み", "fact": "講談社が主催する賞: ノーベル賞", "source_url": "http://x"},   # 反転(不支持であるべき)
             {"axis": "事業・強み", "fact": "講談社は江戸川乱歩賞を主催している", "source_url": "http://x"}]  # 支持
    v = verify_materials(cands, corpus)
    facts = [m["fact"] for m in v]
    ok1 = "講談社が主催する賞: ノーベル賞" not in facts    # 反転はdrop
    ok2 = any("江戸川乱歩賞" in f for f in facts)          # 正は残る
    print(f"[selftest] ノーベル反転drop={ok1} / 正例keep={ok2}")
    print("=== SELFTEST:", "PASS ===" if (ok1 and ok2) else "FAIL ===")
    return ok1 and ok2


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pilot = "--pilot" in sys.argv
    thin_rows, results = [], []
    for slug in args:
        dp = os.path.join(OUT, slug, "datasheet.json")
        cp = os.path.join(OUT, slug, "quiz_corpus_locked_v3.json")
        if not os.path.exists(dp):
            print(f"SKIP {slug}: datasheet無し", flush=True); continue
        ds = json.load(open(dp))
        corpus = json.load(open(cp)) if os.path.exists(cp) else {}
        name = ds.get("name", slug)
        kit, msg, verified = build_kit(slug, name, ds, corpus)
        if kit is None:
            if msg.startswith("thin:"):
                thin_rows.append(f"{slug},{name},{len(verified)}")
                print(f"THIN {slug}: {msg} → es_thin.csv(出荷保留)", flush=True)
                results.append((slug, "thin", msg))
            else:
                print(f"FAIL {slug}: {msg}", flush=True); results.append((slug, "fail", msg))
            continue
        if msg:
            print(f"LINT-NG {slug}: {msg}", flush=True); results.append((slug, "lint_ng", msg)); continue
        json.dump(kit, open(os.path.join(OUT, slug, "es_kit.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        nm, ni = len(kit["motivation_sheet"]["materials"]), len(kit["interview_questions"])
        print(f"OK {slug}: 材料{nm} 面接{ni} (検証済材料{len(verified)})", flush=True)
        results.append((slug, "ok", {"materials": nm, "interview": ni, "verified": len(verified)}))
        if pilot:
            os.makedirs(os.path.join(HANDOFF, "es_kit_pilot"), exist_ok=True)
            open(os.path.join(HANDOFF, "es_kit_pilot", f"es_kit_{slug}.md"), "w", encoding="utf-8").write(to_md(kit))
    if thin_rows:
        with open(os.path.join(OUT, "es_thin.csv"), "a", encoding="utf-8") as f:
            f.write("\n".join(thin_rows) + "\n")
    print("\n=== SUMMARY ===")
    for s, st, d in results:
        print(f"  {st:8} {s} {d}")


if __name__ == "__main__":
    main()
