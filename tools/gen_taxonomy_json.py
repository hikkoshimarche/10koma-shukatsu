#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ph1: 正準タクソノミー public/taxonomy.json を生成。
構造(大15/中55/安定ascii-slug/横断タグ/中55→業界研究16ブリッジ)のみ。個社割当は持たない(CSVに分離)。
業界研究ハブは現行16を維持し、chu(中分類)→gyokai16 で橋渡し(将来揃えたくなったら揃えられる構造)。"""
import json

OUT = "/Users/oscardodds/projects/10koma-shukatsu/public/taxonomy.json"

# 業界研究ハブ(現行16・不変) — hyphen slug は gyokai.html / quiz.html と一致
GYOKAI16 = [
    ("sogo-shosha","総合商社"), ("senmon-shosha","専門商社"), ("finance","銀行・証券・保険"),
    ("it-ai-saas-game","IT・AI・SaaS・ゲーム"), ("consulting","コンサル"), ("manufacturer","メーカー"),
    ("ad-media","広告・メディア"), ("infra-energy","インフラ・エネルギー"),
    ("realestate-construction","不動産・建設"), ("retail","小売・流通"), ("food-beverage","食品・飲料"),
    ("medical-healthcare","医療・ヘルスケア"), ("transport-logistics","航空・運輸・物流"),
    ("education-hr","教育・人材"), ("startup","スタートアップ"), ("deeptech-space-ai","ディープテック・宇宙・AI"),
]

# 横断タグ(業界軸と直交する企業属性)
TAGS = [
    {"id":"foreign","label":"外資系","desc":"日本法人・外資系企業。業界とは直交する属性(タグ)として保持し、業界からも属性からも到達可能にする。"},
    {"id":"startup","label":"スタートアップ・新興","desc":"新興・成長企業。大分類ではなくタグで表現(大分類=事業領域 / タグ=企業属性 の役割分離)。"},
]

# 大分類(slug,name) -> [ (中分類slug, 中分類name, 対応する業界研究16slug) ]
STRUCT = [
 ("shosha","商社",[
    ("sogo-shosha","総合商社","sogo-shosha"),
    ("senmon-shosha-food-pharma","専門商社（食品・医薬）","senmon-shosha"),
    ("senmon-shosha-industrial","専門商社（エレキ・鉄鋼・化学・機械）","senmon-shosha"),
 ]),
 ("finance","金融",[
    ("bank","銀行","finance"),
    ("securities","証券・投資","finance"),
    ("insurance","生保・損保","finance"),
    ("lease-credit","リース・クレジット・その他金融","finance"),
 ]),
 ("automotive","自動車・輸送機器",[
    ("automaker","自動車（完成車）","manufacturer"),
    ("auto-parts","自動車部品","manufacturer"),
 ]),
 ("electronics-machinery","電機・機械・重工",[
    ("electronics-general","総合電機・重電","manufacturer"),
    ("electronic-components","電子部品・デバイス","manufacturer"),
    ("semiconductor","半導体・半導体製造装置","manufacturer"),
    ("precision-optics","精密・光学・計測機器","manufacturer"),
    ("heavy-machinery","重工・産業機械・プラント","manufacturer"),
 ]),
 ("materials-chemical","素材・化学",[
    ("steel-metal","鉄鋼・非鉄・金属","manufacturer"),
    ("chemical-materials","化学・繊維・ゴム・ガラス","manufacturer"),
 ]),
 ("consumer-healthcare","消費財・ヘルスケアメーカー",[
    ("food-beverage","食品・飲料","food-beverage"),
    ("toiletry","日用品・トイレタリー","manufacturer"),
    ("cosmetics","化粧品・美容","manufacturer"),
    ("pharma","医薬品・製薬","medical-healthcare"),
    ("medical-device-healthtech","医療機器・ヘルステック","medical-healthcare"),
 ]),
 ("it-telecom-internet","IT・通信・インターネット",[
    ("telecom-carrier","通信キャリア","it-ai-saas-game"),
    ("sier-itservice","SIer・ITサービス","it-ai-saas-game"),
    ("internet-web","インターネット・Webサービス","it-ai-saas-game"),
    ("saas","SaaS・業務ソフト","it-ai-saas-game"),
    ("ai-data","AI・データ・先端テック","it-ai-saas-game"),
 ]),
 ("consulting","コンサル・シンクタンク",[
    ("strategy-consulting","戦略コンサル","consulting"),
    ("general-it-consulting","総合・ITコンサル","consulting"),
    ("think-tank","シンクタンク・リサーチ","consulting"),
 ]),
 ("infra-energy","インフラ・エネルギー",[
    ("electric-power","電力","infra-energy"),
    ("renewable-energy","再生可能エネルギー","infra-energy"),
    ("gas","ガス","infra-energy"),
    ("oil-resources","石油・資源・鉱業","infra-energy"),
    ("plant-water","プラントエンジ・水環境","infra-energy"),
 ]),
 ("construction-realestate","建設・不動産",[
    ("real-estate-developer","不動産・デベロッパー","realestate-construction"),
    ("housing","ハウスメーカー","realestate-construction"),
    ("general-contractor","ゼネコン・建設","realestate-construction"),
    ("facility-electrical","設備・電気工事","realestate-construction"),
 ]),
 ("transport-logistics","運輸・物流",[
    ("railway","鉄道","transport-logistics"),
    ("airline","航空","transport-logistics"),
    ("shipping","海運","transport-logistics"),
    ("logistics","陸運・物流","transport-logistics"),
 ]),
 ("retail","小売・流通",[
    ("general-retail","総合小売（GMS・スーパー・CVS）","retail"),
    ("department-store","百貨店","retail"),
    ("specialty-apparel-ec","専門店・アパレル・EC","retail"),
    ("electronics-retail-hc","家電量販・ホームセンター","retail"),
    ("drugstore","ドラッグストア","retail"),
 ]),
 ("media-entertainment","マスコミ・広告・エンタメ",[
    ("advertising-agency","広告代理店","ad-media"),
    ("broadcasting","テレビ・放送","ad-media"),
    ("publishing","新聞・出版","ad-media"),
    ("entertainment","音楽・映画・エンタメ施設","ad-media"),
    ("game","ゲーム","it-ai-saas-game"),   # 業界研究16では ゲーム は it-ai-saas-game 側(directory大分類とは独立=ブリッジの意義)
 ]),
 ("education-hr","教育・人材",[
    ("hr-staffing","人材サービス","education-hr"),
    ("education","教育","education-hr"),
 ]),
 ("deeptech-space","ディープテック・宇宙",[
    ("space-deeptech","宇宙・ディープテック","deeptech-space-ai"),
    ("biotech-newmaterial","バイオ・新素材","startup"),
 ]),
]

dai = []
for dslug, dname, chus in STRUCT:
    dai.append({
        "slug": dslug, "name": dname,
        "chubunrui": [{"slug": cs, "name": cn, "gyokai16": g} for cs, cn, g in chus],
    })

doc = {
    "version": "1.0",
    "generated": "2026-08-03",
    "note": "唯一の正準タクソノミー(構造のみ)。個社割当は tools/taxonomy_companies.csv に分離。"
            "業界研究ハブ(業界10コマ160枚+業界クイズ)は現行16を維持し、中分類→gyokai16 で橋渡し。"
            "将来ディレクトリと業界研究を揃えたくなったら gyokai16 を差し替えるだけで揃う構造。",
    "counts": {"daibunrui": len(dai), "chubunrui": sum(len(d["chubunrui"]) for d in dai)},
    "tags": TAGS,
    "gyokai16": [{"slug": s, "name": n} for s, n in GYOKAI16],
    "daibunrui": dai,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")

# 自己検証
chu_slugs = [c["slug"] for d in dai for c in d["chubunrui"]]
g16 = {s for s, _ in GYOKAI16}
assert len(chu_slugs) == len(set(chu_slugs)), "中分類slug重複"
dai_slugs = [d["slug"] for d in dai]
assert len(dai_slugs) == len(set(dai_slugs)), "大分類slug重複"
bad = [c["slug"] for d in dai for c in d["chubunrui"] if c["gyokai16"] not in g16]
assert not bad, f"未知gyokai16参照: {bad}"
covered = {c["gyokai16"] for d in dai for c in d["chubunrui"]}
missing16 = g16 - covered
print(f"OK: 大分類 {len(dai)} / 中分類 {len(chu_slugs)} / gyokai16被覆 {len(covered)}/16")
if missing16:
    print("  ⚠ どの中分類からも参照されないgyokai16:", missing16)
print("wrote", OUT)
