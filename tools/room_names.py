#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_names.py — ルーム6人格の「氏名(個人名)」を決定的に生成。

3層: 役割記号(R1-R6) / 役割名(若手エース等=ROLES) / 氏名(個人名=本モジュール)。
氏名は実在の特定社員ではないAIロールの表示名。一般的な日本人名を slug+role の
ハッシュで決定的生成(再syncで不変)。R4=中堅女性のみ女性名。三井物産は金型の6名固定。
AI開示(「実在の特定社員ではありません」)は別途system_prompt側で維持。
"""
import hashlib

# 三井物産=金型GOLD REFERENCEの6名(Notion 3887518001ef817caa63fe602545f72a より)
MITSUI_ROSTER = {
    "R1": "佐藤 健太", "R2": "山田 俊介", "R3": "高橋 誠一郎",
    "R4": "鈴木 美咲", "R5": "田中 浩二", "R6": "渡辺 潤",
}

SURNAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
    "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
    "山崎", "森", "池田", "橋本", "阿部", "石川", "中島", "前田", "藤田", "後藤",
    "岡田", "長谷川", "村上", "近藤", "石井", "坂本", "遠藤", "青木", "藤井", "西村",
]
GIVEN_MALE = [
    "健太", "大輔", "翔", "拓也", "直樹", "雄太", "亮", "誠", "洋平", "達也",
    "和也", "智也", "俊介", "浩二", "誠一郎", "啓介", "雄一", "隆", "学", "剛",
    "裕樹", "康平", "真一", "data省略でない真", "貴之", "英樹", "正樹", "光", "悠斗", "拓海",
]
GIVEN_FEMALE = [
    "美咲", "愛", "さくら", "陽子", "香織", "真由", "彩", "優子", "麻衣", "絵里",
    "奈々", "瞳", "結衣", "沙織", "由美", "恵", "彩香", "千尋", "理恵", "葵",
]
# typo保険: 不正要素を除去
GIVEN_MALE = [g for g in GIVEN_MALE if "省略" not in g]


def personal_name(slug, role, female=None):
    """slug+role で決定的に氏名生成(再syncで不変)。三井は金型固定。
    female: v3は女性フラグ(role名に依存しない)。None時は後方互換で role=='R4' を女性とみなす。"""
    if slug == "mitsui-bussan" and role in MITSUI_ROSTER:
        return MITSUI_ROSTER[role]
    if female is None:
        female = (role == "R4")
    h = hashlib.md5(f"{slug}/{role}".encode("utf-8")).hexdigest()
    s = SURNAMES[int(h[:8], 16) % len(SURNAMES)]
    pool = GIVEN_FEMALE if female else GIVEN_MALE
    g = pool[int(h[8:16], 16) % len(pool)]
    return f"{s} {g}"


if __name__ == "__main__":
    for sl in ["mitsui-bussan", "honda", "sony-group", "kao"]:
        print(sl, {r: personal_name(sl, r) for r in ["R1", "R2", "R3", "R4", "R5", "R6"]})
