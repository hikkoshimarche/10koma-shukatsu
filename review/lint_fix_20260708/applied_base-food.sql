-- ===== base-food (ベースフード株式会社) =====
-- source: output/base-food/scenario_v4.json
-- jsDelivr ref: @def7c6ecaa490837e9a9e266b0321fa4f6ee544c
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('base-food', 'ベースフード株式会社', 'others', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_01.png', 'nana', '[nana] このパン、栄養素が26種類も入ってるの!?
[haruki] それ、ベースフードのBASE BREAD。主食そのものを栄養から作り変えた完全栄養食。
[nana] 完全栄養食って、宇宙食みたいなやつ?
[haruki] いや、普通のパン。1食2袋で、1日に必要な栄養素の3分の1が摂れる。', '主食を栄養から作り変えるBASE BREAD', '完全栄養食 / 1食2袋で1日の栄養の1/3', 'ベースフード公式', '["[nana] このパン、栄養素が26種類も入ってるの!?", "[haruki] それ、ベースフードのBASE BREAD。主食そのものを栄養から作り変えた完全栄養食。", "[nana] 完全栄養食って、宇宙食みたいなやつ?", "[haruki] いや、普通のパン。1食2袋で、1日に必要な栄養素の3分の1が摂れる。"]', 'H1: BASE BREAD（完全栄養パン）', '{"location": "ナナの手元中央", "object_type": "BASE BREADパッケージ（チョコレート味）", "brand_form": "黄色のビタミンカラーと正五角形ロゴ、BASE BREADの文字が明瞭なパッケージ", "attachment": "ナナが手に持つ", "scale_note": "実在の商品パッケージと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_02.png', 'haruki', '[haruki] 全国5万店舗以上で売ってる。配荷率81.3パーセント。
[nana] え、ほぼ全部の店に…
[haruki] 累計販売2億袋突破。売上152億円、2025年2月期に初めて黒字化した。
[nana] 黒字化って、つい最近!? まだ成長してる途中なんだ…', '全国5万店舗、累計2億袋突破', '配荷率81.3% / 売上152億円', '公式IR 2025年2月期', '["[haruki] 全国5万店舗以上で売ってる。配荷率81.3パーセント。", "[nana] え、ほぼ全部の店に…", "[haruki] 累計販売2億袋突破。売上152億円、2025年2月期に初めて黒字化した。", "[nana] 黒字化って、つい最近!? まだ成長してる途中なんだ…"]', 'H6: コンビニ店頭の陳列棚', '{"location": "陳列棚中央", "object_type": "BASE BREADシリーズ（複数フレーバー）", "brand_form": "チョコレート・メープル・シナモン等のフレーバーが並ぶ黄色パッケージ群", "attachment": "棚に陳列", "scale_note": "実在の店頭陳列と同じ配置"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_03.png', 'nana', '[nana] パンだけじゃないんだ。パスタもクッキーも?
[haruki] そう。BASE PASTAは茹で時間1から2分の生パスタ。BASE Cookiesは間食でも栄養補給できる。
[nana] 主食を全部、完全栄養にする…
[haruki] 創業者の橋本舜は元DeNA。2016年に創業して、主食をイノベーションするって決めた。', '主食を全部、完全栄養に', 'BASE BREAD / PASTA / Cookies', NULL, '["[nana] パンだけじゃないんだ。パスタもクッキーも?", "[haruki] そう。BASE PASTAは茹で時間1から2分の生パスタ。BASE Cookiesは間食でも栄養補給できる。", "[nana] 主食を全部、完全栄養にする…", "[haruki] 創業者の橋本舜は元DeNA。2016年に創業して、主食をイノベーションするって決めた。"]', 'H2: BASE PASTA（完全栄養パスタ） / H3: BASE Cookies（完全栄養クッキー）', '{"location": "テーブル中央", "object_type": "BASE PASTAとBASE Cookiesのパッケージ", "brand_form": "BASE PASTAフェットチーネの袋と、BASE Cookiesココア味の袋、どちらも黄色ベース", "attachment": "テーブル上に配置", "scale_note": "実在商品パッケージと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_04.png', 'haruki', '[haruki] 橋本さんは東大卒でDeNAにいたけど、仕事が忙しくて食事が疎かになってた。
[nana] それで完全栄養食を…?
[haruki] うん。正五角形のロゴは栄養バランス、コック帽は美味しさ。栄養と美味しさ、両立させるって決めた。
[nana] ビジネスじゃなくて、自分の課題から始まったんだ…', '栄養と美味しさ、両立させる', '創業者 橋本舜 / 2016年創業 / 元DeNA', NULL, '["[haruki] 橋本さんは東大卒でDeNAにいたけど、仕事が忙しくて食事が疎かになってた。", "[nana] それで完全栄養食を…?", "[haruki] うん。正五角形のロゴは栄養バランス、コック帽は美味しさ。栄養と美味しさ、両立させるって決めた。", "[nana] ビジネスじゃなくて、自分の課題から始まったんだ…"]', 'H4: 完全栄養食のパッケージデザイン（黄色ビタミンカラー・正五角形ロゴ）', '{"location": "壁面中央", "object_type": "ブランドロゴパネル（正五角形+コック帽）", "brand_form": "黄色ビタミンカラーの正五角形（栄養バランス象徴）とコック帽（美味しさ象徴）を組み合わせたロゴ", "attachment": "壁面に固定", "scale_note": "実在のブランドアイデンティティ展示サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_05.png', 'nana', '[nana] 年収はどのくらい?
[haruki] 平均853万円。年俸制で、査定が年2回ある。
[nana] 査定2回!? 半年ごとに評価されるってこと?
[haruki] そう。成長期のフードテック企業だから、成果がすぐ反映される仕組み。大手みたいな安定じゃない。', '平均年収853万円、年俸制', '査定年2回 / 成果がすぐ反映', 'フィスコ株式会社 2025年7月時点', '["[nana] 年収はどのくらい?", "[haruki] 平均853万円。年俸制で、査定が年2回ある。", "[nana] 査定2回!? 半年ごとに評価されるってこと?", "[haruki] そう。成長期のフードテック企業だから、成果がすぐ反映される仕組み。大手みたいな安定じゃない。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_06.png', 'haruki', '[haruki] 従業員128人。少数精鋭で、一人ひとりの裁量が大きい。
[nana] 128人で売上152億円って…一人あたりの負荷、すごそう…
[haruki] 正直、激務。成長期だから、配属も固定じゃなくて事業の優先度で動く。
[nana] 安定を求めるなら、向かない会社なんだ…', '従業員128人、少数精鋭の激務', '一人あたり売上1億円超 / 配属は事業優先', NULL, '["[haruki] 従業員128人。少数精鋭で、一人ひとりの裁量が大きい。", "[nana] 128人で売上152億円って…一人あたりの負荷、すごそう…", "[haruki] 正直、激務。成長期だから、配属も固定じゃなくて事業の優先度で動く。", "[nana] 安定を求めるなら、向かない会社なんだ…"]', 'H5: 座間市の物流拠点（GLP座間2F）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_07.png', 'nana', '[採用担当] ベースフードが見るのは、ミッションへの共感。完全栄養食で健康のあたりまえを変えたいと強く思えるか。
[採用担当] 常識にとらわれず、あらゆる可能性を自ら検討して、ミッションの達成に心を燃やせる人。
[nana] 心を燃やす…強い言葉だ…
[haruki] 数字じゃなくて、情熱で選ぶ会社なんだ。', 'ミッションに心を燃やす人', '常識にとらわれず / 可能性を自ら検討', NULL, '["[採用担当] ベースフードが見るのは、ミッションへの共感。完全栄養食で健康のあたりまえを変えたいと強く思えるか。", "[採用担当] 常識にとらわれず、あらゆる可能性を自ら検討して、ミッションの達成に心を燃やせる人。", "[nana] 心を燃やす…強い言葉だ…", "[haruki] 数字じゃなくて、情熱で選ぶ会社なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_08.png', 'nana', '[nana] あ、あの人もBASE BREAD食べてる…
[haruki] サブスク会員が22.3万人いる。定期購入で毎月届く仕組み。
[nana] 22万人も、毎月買い続けてるんだ…
[haruki] 一度食べたら、栄養バランスの楽さに気づく。それが支持される理由。', 'サブスク会員22.3万人の支持', '定期購入 / 毎月届く完全栄養食', NULL, '["[nana] あ、あの人もBASE BREAD食べてる…", "[haruki] サブスク会員が22.3万人いる。定期購入で毎月届く仕組み。", "[nana] 22万人も、毎月買い続けてるんだ…", "[haruki] 一度食べたら、栄養バランスの楽さに気づく。それが支持される理由。"]', 'H1: BASE BREAD（完全栄養パン）再使用', '{"location": "周囲の学生の手元", "object_type": "BASE BREADパッケージ（複数）", "brand_form": "黄色パッケージ、学生たちが手に持つ", "attachment": "各学生が手に持つ", "scale_note": "実在商品サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。ニューヨークの店頭でBASE BREADを展開する営業。
[haruki] 本社ラボで、次世代の完全栄養スイーツを開発する研究員。
[haruki] 学校給食に完全栄養食を導入する自治体プロジェクトのリーダー。
[nana] どれも、主食を変える仕事。人の健康のあたりまえを、変えてる…', '10年後、たとえばこんな場面', '海外展開 / 新製品開発 / 学校給食導入', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。ニューヨークの店頭でBASE BREADを展開する営業。", "[haruki] 本社ラボで、次世代の完全栄養スイーツを開発する研究員。", "[haruki] 学校給食に完全栄養食を導入する自治体プロジェクトのリーダー。", "[nana] どれも、主食を変える仕事。人の健康のあたりまえを、変えてる…"]', 'H6: コンビニ店頭の陳列棚（再使用）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('base-food', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@def7c6ecaa490837e9a9e266b0321fa4f6ee544c/public/images/base-food/panel_10.png', 'both', '[haruki] 売上152億円、営業利益1.3億円で初黒字、従業員128人。
[nana] 激務だけど、確かに成長してる。主食を変えるって、人生を変えるってことなんだ。
[both] 主食が、人生を支える。ベースフード、健康のあたりまえをつくる会社。', '主食が、人生を支える。', '売上152億円 / 初黒字達成 / 従業員128人', NULL, '["[haruki] 売上152億円、営業利益1.3億円で初黒字、従業員128人。", "[nana] 激務だけど、確かに成長してる。主食を変えるって、人生を変えるってことなんだ。", "[both] 主食が、人生を支える。ベースフード、健康のあたりまえをつくる会社。"]', 'H4: 完全栄養食のパッケージデザイン（黄色ビタミンカラー・正五角形ロゴ）再使用', '{"location": "二人の手元", "object_type": "BASE BREADパッケージ", "brand_form": "黄色ビタミンカラーの正五角形ロゴ入りパッケージ", "attachment": "手に持つ", "scale_note": "実在商品サイズ"}');
