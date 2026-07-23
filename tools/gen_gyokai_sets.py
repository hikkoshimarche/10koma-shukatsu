#!/usr/bin/env python3
"""承認済みGYOKAI枠の業界クイズを生成。就活の"枠組み"で束ね、枠組み名を明示。
 - 構成社(corpus取得済のみ)のcorpusをmerge → converge_locked(枠組みextra) → ship≥15
 - set_id=industry__<GYOKAIスラグ>(ハッシュ禁止)。output/industry__<slug>/ に保存。
D1投入はしない(別ステップ)。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
import quiz_lint as QL

OUT = q.OUT
SHIP_MIN = q.SHIP_MIN

# GYOKAIスラグ → {name(表示), fw(枠組みテキスト), members(corpus済slug)}
MAP = {
 # 初期5セット(sogo/senmon/finance/consulting/manufacturer)のうち鮮度再生成対象。member=corpus取得済社。
 "manufacturer": {"name": "メーカー(精密・機械)",
   "fw": "精密機器・機械メーカー大手(島津製作所/いすゞ自動車/クボタ)",
   "members": ["shimadzu", "isuzu", "kubota"]},
 "medical-healthcare": {"name": "製薬・ヘルスケア",
   "fw": "内資製薬大手(武田薬品/アステラス/第一三共/中外製薬/エーザイ/塩野義)",
   "members": ["takeda", "astellas", "daiichi-sankyo", "chugai", "eisai", "shionogi"]},
 "infra-energy": {"name": "インフラ・エネルギー",
   "fw": "電力大手(東京電力/中部電力/九州電力)、都市ガス大手(東京ガス/大阪ガス)、石油元売り(ENEOS)、資源開発(INPEX)、プラントエンジ(日揮)",
   "members": ["tepco", "chubu-electric", "kyushu-electric", "chugoku-electric", "j-power",
               "tokyo-gas", "osaka-gas", "saibu-gas", "eneos", "cosmo-energy", "inpex", "japex", "jgc-hd", "chiyoda"]},
 "realestate-construction": {"name": "不動産・建設",
   "fw": "スーパーゼネコン(鹿島建設/清水建設/竹中工務店 ※5社中3社)、大手デベロッパー財閥系御三家(三井不動産/三菱地所/住友不動産)、大手住宅メーカー(積水ハウス)",
   "members": ["kajima", "shimizu", "takenaka", "mitsui-fudosan", "mitsubishi-estate", "sumitomo-fudosan", "sekisui-house", "mori-building"]},
 "transport-logistics": {"name": "航空・運輸・物流",
   "fw": "JR本州3社(JR東日本/JR東海/JR西日本)、大手私鉄(近鉄グループ/阪急阪神)、航空(ANA)、海運大手(日本郵船/川崎汽船)、陸運物流(日本通運/佐川)",
   "members": ["jr-east", "jr-central", "jr-west", "ana-hd", "nyk", "k-line", "nippon-express-hd", "sg-hd", "kintetsu-group-hd", "hankyu-hanshin-hd"]},
 "retail": {"name": "小売・流通",
   "fw": "総合小売2強(セブン&アイ/イオン)、SPAアパレル(ファーストリテイリング)、ドラッグストア大手(ウエルシア/ツルハ)、家電量販(ヤマダ)、ホームセンター(ニトリ/カインズ)",
   "members": ["seven-and-i", "aeon", "fast-retailing", "nitori-hd", "welcia-hd", "tsuruha-hd", "yamada-hd", "cainz", "ppih"]},
 "food-beverage": {"name": "食品・飲料",
   "fw": "総合食品(明治HD/日清食品/山崎製パン/日本ハム/ハウス食品)、乳業大手(森永乳業/雪印メグミルク)、飲料(伊藤園/ヤクルト/キリン)",
   "members": ["meiji-hd", "nissin-hd", "yamazaki-pan", "nipponham", "house-foods", "morinaga-milk", "yukijirushi-megmilk", "itoen", "kirin-hd"]},
 "ad-media": {"name": "広告・メディア",
   "fw": "広告代理店大手(電通/博報堂DY/ADK)、民放キー局(日本テレビ/フジ/テレビ朝日)、大手出版(KADOKAWA/集英社)、エンタメ(オリエンタルランド)",
   "members": ["dentsu", "hakuhodo-dy", "adk-hd", "ntv-hd", "fuji-media-hd", "tv-asahi-hd", "kadokawa", "shueisha", "oriental-land"]},
 "it-ai-saas-game": {"name": "IT・通信・SaaS・ゲーム",
   "fw": "通信3大キャリア(NTT/KDDI/ソフトバンク)、大手SIer(NTTデータ)、メガベンチャー(楽天/サイバーエージェント/LINEヤフー)、大手SaaS(Sansan/freee)、ゲーム大手(任天堂/バンダイナムコ/カプコン)",
   "members": ["ntt", "kddi", "softbank", "ntt-data", "rakuten-group", "cyberagent", "line-yahoo", "sansan", "freee", "nintendo", "bandai-namco", "capcom"]},
 "startup": {"name": "スタートアップ",
   "fw": "上場SaaS・スタートアップ(メルカリ/freee/Sansan/ビジョナル/LayerX/ラクス/カオナビ/kubell)",
   "members": ["mercari", "freee", "sansan", "visional", "layerx", "rakus", "kaonavi", "kubell"]},
 "deeptech-space-ai": {"name": "ディープテック・AI",
   "fw": "AI開発企業(Preferred Networks/Sakana AI/PKSHA Technology/ELYZA/ブレインパッド) ※宇宙(ispace/アストロスケール)は公式財務corpus未取得のため後日追補",
   "members": ["pref-networks", "sakana-ai", "pksha", "elyza", "brainpad"]},
}

EXTRA_TMPL = (
 "これは『{name}』業界の理解度クイズです。就活の枠組みで束ねています: {fw}。\n"
 "・枠組み名(例:スーパーゼネコン/内資製薬大手/JR本州3社など)自体を問う設問を1〜3問含めてよい(業界研究になる)。\n"
 "・各設問は必ず特定1社の一次情報に接地し source_url を持つ(その社の事実)。会社をまたいだ捏造禁止。\n"
 "・『最大/最高/1位』等の順位設問は、枠組み内『全社の数値が揃う指標』(売上収益・利益額・従業員数等)のみ。"
 "EPS等の株数依存指標での社間比較は禁止。順位設問には type:\"rank\" と competitors:[{{name,value,source_url}}] を付す。\n"
 "・数値/日付は各社source本文に実在する表記のまま。誤答も同一source内の実在数値(別項目/別期)。")

targets = sys.argv[1:] if len(sys.argv) > 1 else list(MAP.keys())
results = []
for slug in targets:
    m = MAP[slug]
    islug = "industry__" + slug
    mcorpus = {}
    used = []
    for ms in m["members"]:
        cp = os.path.join(OUT, ms, "quiz_corpus_locked_v3.json")
        if os.path.exists(cp):
            try:
                mcorpus.update(json.load(open(cp)))
                used.append(ms)
            except Exception:
                pass
    if len(used) < 3:
        print(f"SKIP {islug}: corpus社 {len(used)}<3", flush=True)
        results.append({"slug": islug, "status": "skip_corpus", "members": len(used)})
        continue
    extra = EXTRA_TMPL.format(name=m["name"], fw=m["fw"])
    try:
        final, dropped, rate = q.converge_locked(islug, m["name"], mcorpus, target=30, extra=extra)
    except Exception as e:
        print(f"ERR {islug}: {type(e).__name__}:{str(e)[:60]}", flush=True)
        results.append({"slug": islug, "status": "err", "err": str(e)[:80]})
        continue
    rep = QL.run_quiz_lints(final, mcorpus)
    if len(final) < SHIP_MIN:
        print(f"THIN {islug}: n={len(final)} (<{SHIP_MIN}) 保留", flush=True)
        results.append({"slug": islug, "status": "thin", "n": len(final), "pass": rate})
        continue
    os.makedirs(os.path.join(OUT, islug), exist_ok=True)
    json.dump(final, open(os.path.join(OUT, islug, "quiz_30q_locked_v3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(mcorpus, open(os.path.join(OUT, islug, "quiz_corpus_locked_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
    rankn = sum(1 for x in final if x.get("type") == "rank" or x.get("category") == "業界順位")
    print(f"OK {islug}: n={len(final)} lint_err={rep['errors']} rank={rankn} pass={rate} 社={len(used)}", flush=True)
    results.append({"slug": islug, "status": "ok", "n": len(final), "lint": rep["errors"],
                    "rank": rankn, "pass": rate, "members": len(used)})

print("\n=== SUMMARY ===")
print(json.dumps(results, ensure_ascii=False, indent=1))
ok = [r for r in results if r["status"] == "ok"]
print(f"生成OK {len(ok)}/{len(targets)} 枠 / 総問 {sum(r['n'] for r in ok)}")
