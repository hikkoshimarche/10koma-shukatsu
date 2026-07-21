#!/usr/bin/env python3
"""ES・面接対策キット(静的・一回生成)。datasheet保有社を対象。
 ① 志望動機組み立てシート: datasheetの事実を「志望動機の材料」に再構成。
    - 各材料 = datasheetのfact(逐語コピー)+source_url+問いかけ「あなたの経験で繋がるものは？」
    - 構成テンプレ(型紙)+NG例。★完成文の例文は作らない(代筆回避)。
 ② 想定面接質問10問: 事業・人物像から生成、各問に「答えの組み立てヒント」。★模範解答は作らない。
品質ゲート: 事実は全てdatasheet内に実在(逐語)・出典付き・倍率/断定禁止(coverage lint)。
出力: output/<slug>/es_kit.json。--pilot でmdも受け渡しフォルダへ。
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")

# 型紙・NG例は汎用ES指南(会社非依存=coverage対象外)
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

AXIS_FROM_SECTION = {
    "事業内容・セグメント": "事業・強み",
    "社風・求める人物像": "社風・求める人物像",
    "沿革・基本情報": "沿革・基本情報",
}

SYS = (
 "あなたは就活生の自己分析を助けるキャリア支援者です。提供された企業の事実(datasheet由来)だけを使い、"
 "志望動機を『組み立てる材料と問い』、および想定面接質問を用意します。"
 "絶対規則: (1)新しい事実・数値・固有名を足さない(与えられた事実のみ)。(2)完成した志望動機文や面接の模範解答は書かない"
 "(型・問い・ヒントのみ=代筆しない)。(3)『何倍』等の倍率や未確認の断定をしない。(4)出力は日本語。")

USER_TMPL = (
 "企業: {name}\n\n以下は datasheet の事実(idx付き)。これだけを根拠にする。\n{facts}\n\n"
 "出力JSON(厳守):\n"
 "{{\n"
 " \"motivation_prompts\": [{{\"idx\": <上記事実のidx>, \"prompt\": \"この事実に対し就活生が自分の経験と接続するための問いかけ(例:あなたの経験で繋がるものは？を事実に即して具体化)。20-40字。完成文は書かない\"}}],\n"
 " \"interview_questions\": [{{\"idx\": <根拠事実のidx>, \"q\": \"その事実に基づく想定面接質問(1文)\", \"hint\": \"答えの組み立てヒント(型のみ・模範解答や具体回答は書かない・15-40字)\"}}]\n"
 "}}\n"
 "motivation_prompts は事業・社風・人物像・沿革の各事実に1つずつ(最大10)。interview_questions は事業・人物像中心に10問。"
 "idx は必ず上記事実のもの。捏造・模範解答・完成文・倍率は禁止。")


# 志望動機/面接の材料に適さない事実を除外(仕様: 事業/強み/社風/人物像 中心)。
#  - 主要財務(数字の暗記)は材料/設問の基にしない。
#  - 沿革の登記トリビア(本店所在地/資本金/株式数/女性比率等)は弱い設問になるため除外。
_DRY_FACT = re.compile(r"(本店|所在地|資本金|発行済|自己株式|株式数|女性比率|平均年齢|平均勤続|住所|郵便番号)")
_USE_SECTIONS = {"事業内容・セグメント", "社風・求める人物像", "沿革・基本情報"}


def load_facts(ds):
    """datasheet → [{axis, fact, source_url, as_of}]。事業/社風/人物像+沿革(非トリビア)のみ。財務は除外。"""
    out = []
    sec = ds.get("sections", {})
    if not isinstance(sec, dict):
        return out
    for k, items in sec.items():
        if k not in _USE_SECTIONS:
            continue                                  # 主要財務は材料にしない
        axis = AXIS_FROM_SECTION.get(k, k)
        for it in (items or []):
            if not isinstance(it, dict):
                continue
            f = it.get("fact", "").strip()
            if not f or _DRY_FACT.search(f):          # 登記トリビアは除外
                continue
            out.append({"axis": axis, "fact": f, "source_url": it.get("source_url", ""),
                        "as_of": it.get("as_of")})
    return out


RATIO = re.compile(r"[0-9０-９]+(?:\.[0-9]+)?\s*倍")


def coverage_check(kit, facts):
    """全fact/source が datasheet 由来か・倍率が無いかを検査。返り: errors[]"""
    valid_facts = {f["fact"] for f in facts}
    valid_src = {f["source_url"] for f in facts}
    errs = []
    for m in kit["motivation_sheet"]["materials"]:
        if m["fact"] not in valid_facts:
            errs.append(f"motivation fact 非datasheet: {m['fact'][:30]}")
        if m["source_url"] and m["source_url"] not in valid_src:
            errs.append(f"motivation source 非datasheet: {m['source_url'][:40]}")
        if RATIO.search(m.get("prompt", "")):
            errs.append(f"motivation prompt に倍率: {m['prompt'][:30]}")
    for iq in kit["interview_questions"]:
        b = iq.get("based_on", {})
        if b.get("fact") and b["fact"] not in valid_facts:
            errs.append(f"interview based_on 非datasheet: {b['fact'][:30]}")
        if RATIO.search(iq.get("q", "")) or RATIO.search(iq.get("hint", "")):
            errs.append(f"interview に倍率: {iq.get('q','')[:30]}")
    return errs


def build_kit(slug, name, ds):
    facts = load_facts(ds)
    if len(facts) < 3:
        return None, ["datasheet fact <3(材料不足)"]
    fact_lines = "\n".join(f"[{i}] ({f['axis']}) {f['fact']}  <src:{f['source_url']}>"
                           for i, f in enumerate(facts))
    txt = q.openai_chat([{"role": "system", "content": SYS},
                         {"role": "user", "content": USER_TMPL.format(name=name, facts=fact_lines)}],
                        max_tokens=2500)
    data = q._parse_json(txt)
    if not isinstance(data, dict):
        return None, ["LLM出力パース失敗"]
    # 材料組み立て(factは逐語コピー=coverage保証)
    materials = []
    for mp in data.get("motivation_prompts", []):
        i = mp.get("idx")
        if not isinstance(i, int) or not (0 <= i < len(facts)):
            continue
        f = facts[i]
        materials.append({"axis": f["axis"], "fact": f["fact"], "source_url": f["source_url"],
                          "prompt": (mp.get("prompt", "") or "あなたの経験で繋がるものは？").strip()})
    iqs = []
    for iq in data.get("interview_questions", []):
        i = iq.get("idx")
        b = {}
        if isinstance(i, int) and 0 <= i < len(facts):
            b = {"fact": facts[i]["fact"], "source_url": facts[i]["source_url"]}
        if not iq.get("q"):
            continue
        iqs.append({"q": iq["q"].strip(), "based_on": b, "hint": iq.get("hint", "").strip()})
    kit = {"slug": slug, "name": name,
           "motivation_sheet": {"materials": materials,
                                "structure_template": STRUCTURE_TMPL, "ng_examples": NG_EXAMPLES},
           "interview_questions": iqs[:10]}
    errs = coverage_check(kit, facts)
    return kit, errs


def to_md(kit):
    L = [f"# ES・面接対策キット: {kit['name']}", "",
         "> 志望動機の**材料と問い**＋想定面接質問。完成文・模範解答は載せません(自分の言葉で組み立てるため)。", ""]
    L.append("## ① 志望動機 組み立てシート")
    L.append("### 構成テンプレ(型紙)")
    for i, s in enumerate(kit["motivation_sheet"]["structure_template"], 1):
        L.append(f"{i}. {s}")
    L.append("\n### 材料(企業の事実)＋問いかけ")
    ax = None
    for m in kit["motivation_sheet"]["materials"]:
        if m["axis"] != ax:
            ax = m["axis"]; L.append(f"\n**【{ax}】**")
        L.append(f"- 事実: {m['fact']}")
        L.append(f"  - ❓ {m['prompt']}")
        L.append(f"  - 出典: {m['source_url']}")
    L.append("\n### NG例(避ける)")
    for n in kit["motivation_sheet"]["ng_examples"]:
        L.append(f"- {n}")
    L.append("\n## ② 想定面接質問(10問)＋組み立てヒント")
    for i, iq in enumerate(kit["interview_questions"], 1):
        L.append(f"{i}. {iq['q']}")
        if iq.get("hint"):
            L.append(f"   - 💡ヒント(型): {iq['hint']}")
        if iq.get("based_on", {}).get("source_url"):
            L.append(f"   - 根拠: {iq['based_on']['source_url']}")
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pilot = "--pilot" in sys.argv
    results = []
    for slug in args:
        dp = os.path.join(OUT, slug, "datasheet.json")
        if not os.path.exists(dp):
            print(f"SKIP {slug}: datasheet無し", flush=True); continue
        ds = json.load(open(dp))
        name = ds.get("name", slug)
        kit, errs = build_kit(slug, name, ds)
        if kit is None:
            print(f"FAIL {slug}: {errs}", flush=True); results.append((slug, "fail", errs)); continue
        if errs:
            print(f"LINT-NG {slug}: {errs}", flush=True); results.append((slug, "lint_ng", errs)); continue
        json.dump(kit, open(os.path.join(OUT, slug, "es_kit.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        nm = len(kit["motivation_sheet"]["materials"]); ni = len(kit["interview_questions"])
        print(f"OK {slug}: 材料{nm} 面接{ni} lint0", flush=True)
        results.append((slug, "ok", {"materials": nm, "interview": ni}))
        if pilot:
            os.makedirs(os.path.join(HANDOFF, "es_kit_pilot"), exist_ok=True)
            open(os.path.join(HANDOFF, "es_kit_pilot", f"es_kit_{slug}.md"), "w", encoding="utf-8").write(to_md(kit))
    print("\n=== SUMMARY ===")
    for s, st, d in results:
        print(f"  {st:8} {s} {d}")


if __name__ == "__main__":
    main()
