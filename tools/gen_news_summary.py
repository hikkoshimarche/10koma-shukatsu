#!/usr/bin/env python3
"""company_news のやさしい要約(summary_easy)を生成。中学生でも分かる1〜3文。
品質ゲート(クイズlint同方式・必須): 要約内の数値・固有名詞が元記事本文に実在しないと error(不採用)。
専門用語は用語辞書のやさしい語彙へ寄せる。見出し・公式リンク併記前提の『補助』(置換でない)。
生成はOpenAI・週次バッチのみ。D1へは書かず md 受け渡し(Web Claudeが文体レビュー後に本番反映)。
  python tools/gen_news_summary.py [--limit N] [--apply]   # --apply でD1 UPDATE(既定=md出力のみ)
"""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
HANDOFF = os.path.expanduser("~/Desktop/kindle_受け渡し")

# 専門用語→やさしい言い換え(最小辞書・随時拡張)
GLOSSARY = {
    "連結": "グループ全体の", "営業利益": "本業でのもうけ", "経常利益": "会社全体のもうけ",
    "純利益": "最終的にのこったもうけ", "売上高": "売り上げ", "M&A": "会社の買収や合併",
    "サステナビリティ": "地球や社会にやさしい取り組み", "DX": "デジタル化", "IR": "投資家向けの情報",
    "ESG": "環境・社会・会社運営への配慮", "上方修正": "見通しを良い方へ直すこと",
    "IPO": "株を証券取引所に初めて出すこと", "アライアンス": "会社どうしの協力",
}
SYS = ("あなたは就活生向けニュースを『中学生でも分かる』やさしい日本語に要約する編集者です。"
       "厳守: (1)1〜3文・各文短く (2)元記事本文に無い数値・固有名詞・事実を足さない(推測禁止) "
       "(3)専門用語は避け、やさしい言葉に言い換える (4)見出しの丸写しでなく要点を平易に。")
USER = ("会社名: {name}\n見出し: {title}\n記事本文(抜粋):\n{body}\n\n"
        "上のニュースを中学生にも分かるように1〜3文で要約してください。用語辞書(参考): {glossary}\n"
        "JSON: {{\"summary\":\"...\"}}")

_PROPER = re.compile(r"[一-龥ァ-ヶ][一-龥ァ-ヶA-Za-z0-9・ー]{1,}")
_NUM = re.compile(r"\d[\d,\.]*")
# 一般名詞(固有名詞でない)=照合対象外。真の固有名詞(社名/人名/地名/製品名)のみ検査。
_GENERAL = set(("会社 事業 日本 今年 昨年 今回 発表 予定 イベント ウェブサイト ウエブサイト 専門家 被災者 "
                "勤務地 サービス システム 製品 商品 お客様 お客さま 顧客 取り組み 情報 開催 参加 支援 提供 "
                "実施 開始 詳細 確認 内容 世界 地域 市場 業界 技術 企業 会見 記者 社員 従業員 グループ "
                "ニュース リリース プレス 記事 本文 公式 経営 戦略 未来 社会 環境 価値 品質 安全 挑戦 成長 "
                "投資家 株主 株式 資本 決算 売上 利益 資産 今週 来週 一部 複数 各社 当社 同社 新型 新規 "
                "セミナー ウェビナー フォーラム カンファレンス キャンペーン プロジェクト ソリューション").split())
# 国名の同義正規化(どちらか一方が本文にあればOK)
_COUNTRY = {"米国": "アメリカ", "アメリカ": "米国", "英国": "イギリス", "イギリス": "英国",
            "豪州": "オーストラリア", "オーストラリア": "豪州", "独": "ドイツ, ", "仏": "フランス",
            "中国": "中華人民共和国", "韓国": "大韓民国", "比": "フィリピン", "伊": "イタリア", "西": "スペイン"}
# 要約対象外: 金融商品用語(平易化で不正確)・実質本文なしの定型告知
_SKIP_SUMMARY = re.compile(r"新株予約権|ストックオプション|ストック・?オプション|SO付与|自己株式の取得|"
                           r"譲渡制限付株式|転換社債|新株式発行|第三者割当")


def fetch_body(url):
    try:
        t = q.fetch_url(url)          # PDF/HTML両対応(quiz_fanout)
        return re.sub(r"\s+", " ", t)[:4000] if t else ""
    except Exception:
        return ""


def gate(summary, body):
    """要約の数値・真の固有名詞が本文に実在するか(国名は同義正規化・一般名詞は対象外)。不実在は error。"""
    errs = []
    bdig = re.sub(r"\D", "", body)
    for n in _NUM.findall(summary):
        digits = re.sub(r"\D", "", n)
        if len(digits) >= 2 and digits not in bdig:
            errs.append(f"数値『{n}』が本文に無い")
    for p in set(_PROPER.findall(summary)):
        if len(p) < 3 or p in _GENERAL:            # 一般名詞は照合しない
            continue
        if p in body:
            continue
        alt = _COUNTRY.get(p)                        # 国名同義(米国↔アメリカ 等)
        if alt and any(a.strip() in body for a in alt.split(",")):
            continue
        errs.append(f"固有名詞『{p}』が本文に無い")
    return errs


def d1(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql], cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    rows = []
    for blk in (json.loads(t[i:]) if i >= 0 else []):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


def main():
    apply = "--apply" in sys.argv
    limit = 999
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    rows = d1("SELECT company_id,title,url,published_at FROM company_news WHERE summary_easy IS NULL ORDER BY published_at DESC")[:limit]
    q.line(f"📰 やさしい要約: 対象{len(rows)}件 (品質ゲート=数値/固有名詞の本文実在)")
    ok, rejected, skipped, results, updates = 0, [], [], [], []
    for r in rows:
        # (b) 金融商品用語(SO/新株予約権等)=平易化で不正確→要約対象外(見出し+リンクのみ)
        if _SKIP_SUMMARY.search(r["title"]):
            skipped.append({"url": r["url"], "title": r["title"][:30], "reason": "金融商品用語(要約なし)"}); continue
        body = fetch_body(r["url"])
        # (a) 本文が実質取得できない告知(PDF直リンクのみ等)=要約対象外(見出し+タグで十分)
        if len(body) < 200 or r["url"].lower().endswith(".pdf"):
            skipped.append({"url": r["url"], "title": r["title"][:30], "reason": "本文実質なし(告知/PDF直)"}); continue
        if _SKIP_SUMMARY.search(body[:500]):
            skipped.append({"url": r["url"], "title": r["title"][:30], "reason": "金融商品用語(本文)"}); continue
        txt = q.openai_chat([{"role": "system", "content": SYS},
                             {"role": "user", "content": USER.format(name=r["company_id"], title=r["title"],
                              body=body[:3000], glossary=json.dumps(GLOSSARY, ensure_ascii=False))}],
                            max_tokens=300, temperature=0.2)
        d = q._parse_json(txt) or {}
        summ = (d.get("summary") or "").strip()
        if not summ:
            rejected.append({"url": r["url"], "reason": "生成失敗"}); continue
        errs = gate(summ, body)
        if errs:
            rejected.append({"url": r["url"], "title": r["title"][:30], "summary": summ, "reason": errs[:2]}); continue
        ok += 1
        results.append({"company_id": r["company_id"], "title": r["title"], "url": r["url"], "summary": summ})
        updates.append((r["company_id"], r["url"], summ))
        if not q.cost_ok():
            break
    # md受け渡し
    L = ["# company_news やさしい要約(初回・文体レビュー用)", "",
         f"品質ゲート(数値/固有名詞の本文実在)通過 {ok}件 / 不採用 {len(rejected)}件。**見出し・公式リンク併記の補助**であり置換でない。", ""]
    for x in results:
        L += [f"## {x['company_id']}: {x['title']}", f"- 公式: {x['url']}", f"- やさしい要約: **{x['summary']}**", ""]
    if rejected:
        L += ["", "## 不採用(ゲート落ち・要確認)", ""]
        for x in rejected[:20]:
            L.append(f"- {x.get('title','')} : {x['reason']} {('→「'+x['summary']+'」') if x.get('summary') else ''}")
    if skipped:
        L += ["", "## 要約対象外(告知/PDF直/金融商品用語=見出し+リンクのみ)", ""]
        for x in skipped[:20]:
            L.append(f"- {x.get('title','')} : {x['reason']}")
    import hashlib
    body_md = "\n".join(L)
    sha8 = hashlib.sha256(body_md.encode()).hexdigest()[:8]
    os.makedirs(HANDOFF, exist_ok=True)
    fn = f"news_やさしい要約_初回__{sha8}.md"
    open(os.path.join(HANDOFF, fn), "w", encoding="utf-8").write(body_md)
    if apply and updates:
        def qq(s): return "'" + str(s).replace("'", "''") + "'"
        sql = "\n".join(f"UPDATE company_news SET summary_easy={qq(s)} WHERE company_id={qq(c)} AND url={qq(u)};" for c, u, s in updates)
        open("/tmp/news_summary_update.sql", "w").write(sql)
    print(json.dumps({"target": len(rows), "ok": ok, "rejected": len(rejected), "skipped_rule": len(skipped),
                      "cost_usd": round(q._cost["usd"], 3), "md": fn, "applied": apply}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
