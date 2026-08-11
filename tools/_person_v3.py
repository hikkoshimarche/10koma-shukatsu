#!/usr/bin/env python3
"""人名判定v3: 姓+名スペース / 姓のみ(頻出姓) / 4択同形状+役職語 を答えベースで検出。役職語拡張。"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d1 import d1

# 日本人頻出姓(上位~180) — 姓のみ選択肢の検出用
SURNAMES = set("佐藤 鈴木 高橋 田中 伊藤 渡辺 山本 中村 小林 加藤 吉田 山田 佐々木 山口 松本 井上 木村 林 斎藤 清水 山崎 森 池田 橋本 阿部 石川 山下 中島 石井 小川 前田 岡田 長谷川 藤田 後藤 近藤 村上 遠藤 青木 坂本 斉藤 福田 太田 西村 藤井 岡本 金子 藤原 松田 中川 中野 原田 小野 田村 竹内 中山 和田 石田 森田 上田 原 柴田 酒井 工藤 横山 宮崎 宮本 内田 高木 安藤 島田 谷口 大野 高田 丸山 今井 河野 藤本 村田 武田 上野 杉山 増田 小島 小山 大塚 平野 菅原 久保 松井 千葉 岩崎 桜井 木下 野口 松尾 菊地 野村 渡部 新井 堀 大西 市川 小松 中田 岡 五十嵐 小池 福島 篠原 吉川 高山 吉村 菊池 大橋 松岡 小田 飯田 栗原 平田 浅野 松下 田口 和泉 星野 大石 荒木 小出 濱岡 楠見 樋口 光永 出光 稲盛 本田 松嶋 江頭 陣内 牧之瀬 掛川 会田 因幡 京川 江尾 海野 長澤 大里 大沼 髙島 髙川 髙橋 齊藤 齋藤 大髙 有田 及川 小濱 竹谷 芝 葊川 蜷川 穴澤 米本 羽野 粂川 淡路 瀬尾 徳地 梅山 森井 榊原 荒井 笹山 笠井 花木 若林".split())

ROLE = re.compile(r"代表取締役|代表者|社長|副社長|会長|CEO|COO|CFO|CSO|CTO|CIO|CMO|CHRO|取締役|執行役員|上席執行役員|専務|常務|本部長|支店長|部長|創業者|創立者|初代|会頭|頭取|理事長|顧問|担当者|議長|日本代表|カントリーマネージャー|トップ|人物")
ASK = re.compile(r"誰|名前|氏名")
_TERM = re.compile(r"施設|事業|製品|会社|グループ|株式|システム|サービス|部門|センター|機関|制度|方針|計画|戦略|技術|組織|賞|所|店|課|室|本部|ビジョン|理念|価値|文化|精神|主義|尊重|追求|拡大|革新|密着|向上|創造|挑戦|貢献|実現|推進|事務|拠点|工場|美術館|劇場|講師|飲料|ケチャップ|ブック|電子版|学習|チャット|大学|学校|市|県|都|区|銀行|保険|商事|工業|産業|証券|建設|不動産|食品|通信|商会|物流|海運|航空|エネルギー|資源|金属|石油|化学|重工|製薬|自動車|電機|鉄道")


def is_person_ans(o):
    """無条件で人名とみなす(高精度): 漢字/カナ スペース姓名、2字以上の頻出姓のみ。ローマ字は含めない(製品誤検出回避)。"""
    s = str(o).strip()
    if _TERM.search(s):
        return False
    core = re.sub(r"[\s　]", "", s)
    if re.fullmatch(r"[一-龥々〆ヶ㐀-鿿]{1,3}[\s　][一-龥々〆ヶ㐀-鿿]{1,4}", s):
        return True
    if core in SURNAMES and len(core) >= 2:   # 姓のみ(2字以上)
        return True
    return False


def kata_space(o):
    return bool(re.fullmatch(r"[ァ-ヶ]{2,10}[\s　][ァ-ヶ]{2,10}", str(o).strip()))


def roman_name(o):
    return bool(re.fullmatch(r"[A-Z][a-z]{1,14}[\s][A-Z][a-z\.]{1,14}", str(o).strip()))


def kanji_2_4(o):
    s = re.sub(r"[\s　]", "", str(o))
    return bool(re.fullmatch(r"[一-龥々〆ヶ]{2,4}", s)) and not _TERM.search(str(o))


def detect(rows):
    hit = []
    for r in rows:
        try:
            opts = json.loads(r["options"])
        except Exception:
            continue
        if len(opts) != 4:
            continue
        corr = str(opts[r["correct"]]) if r["correct"] < 4 else ""
        q = r["q_text"]
        # リスク型の文脈=役職語 or 「誰」のみ(bare「名前/氏名」は製品の名前は…を拾うので除外)
        ctx = bool(ROLE.search(q) or "誰" in q)
        # (a) 正解が人名(漢字スペース姓名/2字姓のみ) — 無条件
        if is_person_ans(corr):
            hit.append(r); continue
        # (b) 文脈付き: ローマ字名 / カタカナ姓名 / 1字姓 / 4択3+同形漢字
        if ctx:
            if roman_name(corr) or kata_space(corr):
                hit.append(r); continue
            if re.sub(r"[\s　]", "", corr) in SURNAMES:   # 1字姓含む
                hit.append(r); continue
            if sum(kanji_2_4(o) for o in opts) >= 3 and kanji_2_4(corr):
                hit.append(r); continue
    return hit


if __name__ == "__main__":
    rows = d1("SELECT id,set_id,difficulty,q_text,options,correct FROM quiz_questions WHERE set_type='company'")
    hit = detect(rows)
    json.dump([r["id"] for r in hit], open("/tmp/person_v3.json", "w"))
    print(f"人名v3検出= {len(hit)}件 / {len(set(r['set_id'] for r in hit))}社")
    # F実例の確認
    for ex in ["life-corp", "salesforce-japan"]:
        exq = [r for r in hit if r["set_id"] == ex]
        print(f"  {ex}: {len(exq)}件検出", [json.loads(r['options'])[r['correct']] for r in exq[:3]])
    from collections import Counter
    print("Lv別:", dict(Counter(r["difficulty"] for r in hit)))
