-- ===== sumitomo-corp (住友商事株式会社) =====
-- source: output/sumitomo-corp/scenario_v4.json
-- jsDelivr ref: @9e93cbf
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('sumitomo-corp', '住友商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_01.png', 'nana', '[nana] 住友商事って、5大商社で一番地味じゃない?
[haruki] え、地味?
[nana] うん、三菱・三井・伊藤忠と並べると、印象が薄い…
[haruki] それ、もしかして400年続いた理由かもしれない。', '5大商社で一番地味?', '住友商事 / 8053 / 派手じゃない武器', NULL, '["[nana] 住友商事って、5大商社で一番地味じゃない?", "[haruki] え、地味?", "[nana] うん、三菱・三井・伊藤忠と並べると、印象が薄い…", "[haruki] それ、もしかして400年続いた理由かもしれない。"]', 'H1: 大手町プレイス イーストタワー本社', '{"location": "本社タワー上部の外壁", "object_type": "建築サイン (Sumitomo Corporation)", "brand_form": "ガラスファサード上部に『Sumitomo Corporation』のレリーフサイン、控えめに", "attachment": "タワー外壁に固定", "scale_note": "実在の本社タワーと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_02.png', 'haruki', '[haruki] 純利益5,618億円。売上7兆円。地味どころか、総合商社の中でも堅実なポジション。
[nana] え、そんなに?
[haruki] でも住友は自分から積極的に発信しない会社。だから規模のわりに印象が薄く感じる。
[nana] 数字は出てるのに、自分から語らないんだ…', '純利益5,618億円、地味じゃない', '売上 約7兆円 / 5大商社の堅実派', '公式IR・有報', '["[haruki] 純利益5,618億円。売上7兆円。地味どころか、総合商社の中でも堅実なポジション。", "[nana] え、そんなに?", "[haruki] でも住友は自分から積極的に発信しない会社。だから規模のわりに印象が薄く感じる。", "[nana] 数字は出てるのに、自分から語らないんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_03.png', 'nana', '[nana] あれ、J:COMって…
[haruki] そう、住友商事のグループ会社。ジュピターテレコム。
[nana] 実家のリモコン、ずっと住友商事がかかわっていたの!?
[haruki] それだけじゃない。SCSKもメルカリも、住友が出資してる。地味だけど、生活の中にいる。', 'J:COMもSCSKもメルカリも', 'ぜんぶ住友商事のグループ', NULL, '["[nana] あれ、J:COMって…", "[haruki] そう、住友商事のグループ会社。ジュピターテレコム。", "[nana] 実家のリモコン、ずっと住友商事がかかわっていたの!?", "[haruki] それだけじゃない。SCSKもメルカリも、住友が出資してる。地味だけど、生活の中にいる。"]', 'H2: J:COMのテレビ&リモコン', '{"location": "テレビ画面横またはリモコンの中央", "object_type": "J:COMロゴ", "brand_form": "リモコン中央のJ:COMロゴ、青と白", "attachment": "リモコン本体に印刷", "scale_note": "実在のJ:COMリモコンと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_04.png', 'haruki', '[haruki] 住友家は1691年、別子銅山の経営から始まった。
[nana] 1691年!? 300年以上前…
[haruki] 江戸時代から400年続いてる商家。井桁マークは住友家の家紋。
[nana] 4世紀続いた家が、今のJ:COMやメルカリに繋がってるんだ…', '1691年、別子銅山から400年', '住友家 / 井桁マーク / 江戸から続く商家', NULL, '["[haruki] 住友家は1691年、別子銅山の経営から始まった。", "[nana] 1691年!? 300年以上前…", "[haruki] 江戸時代から400年続いてる商家。井桁マークは住友家の家紋。", "[nana] 4世紀続いた家が、今のJ:COMやメルカリに繋がってるんだ…"]', 'H5: 井桁マーク (住友家の家紋)', '{"location": "壁面中央", "object_type": "井桁マーク (社の家紋・歴史展示)", "brand_form": "井桁(井)を象った住友家の家紋、金属レリーフまたは石彫", "attachment": "壁面に固定", "scale_note": "実在の社内展示の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_05.png', 'nana', '[nana] 5大商社のなかで、年収水準は高くないって聞いたけど。
[haruki] 有価証券報告書(2025年3月期・単体)によると平均年収は1,744万円。住友の理念は『無理せず急がず、不趨浮利』——浮利は追わない。
[haruki] 目先の派手な数字より、長期で積み上げる報酬設計を選んでいる、ってこと。
[nana] 一時の利益じゃなくて、続けることでリターンが育つ仕組みなんだ。', '有報単体1,744万円＋長期で報いる設計', '不趨浮利 / 無理せず急がず', '日経会社情報 8053', '["[nana] 5大商社のなかで、年収水準は高くないって聞いたけど。", "[haruki] 有価証券報告書(2025年3月期・単体)によると平均年収は1,744万円。住友の理念は『無理せず急がず、不趨浮利』——浮利は追わない。", "[haruki] 目先の派手な数字より、長期で積み上げる報酬設計を選んでいる、ってこと。", "[nana] 一時の利益じゃなくて、続けることでリターンが育つ仕組みなんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_06.png', 'haruki', '[OB先輩] 9事業部門あって、第一希望そのまま通る人は半分くらい。
[OB先輩] でも住友は『不趨浮利』。短期の派手な異動はしない。10年単位で人を育てる。
[OB先輩] 入社5〜7年でアフリカ・中東の発電所赴任は普通にある。長期駐在を厭わない人に向く。
[haruki] 短期で結果を出す商社じゃなくて、長く根を張る商社、ってことか…', '10年単位で人を育てる', '第一希望通る人は半分 / 5〜7年で中東・アフリカ駐在', NULL, '["[OB先輩] 9事業部門あって、第一希望そのまま通る人は半分くらい。", "[OB先輩] でも住友は『不趨浮利』。短期の派手な異動はしない。10年単位で人を育てる。", "[OB先輩] 入社5〜7年でアフリカ・中東の発電所赴任は普通にある。長期駐在を厭わない人に向く。", "[haruki] 短期で結果を出す商社じゃなくて、長く根を張る商社、ってことか…"]', 'H6: 海外発電プラント', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_07.png', 'nana', '[OB先輩] 住友が見るのは、『自利利他公私一如』。自分の利と他人の利が一つに見えるか。
[OB先輩] 倍率は189倍あるけど、本当に見てるのは、人と社風が合うか。
[nana] 自利と利他が一つ、って言葉、初めて聞いた…
[haruki] 派手じゃない、長く強い。それは社風から始まってる。', '自利利他公私一如', '倍率より社風 / 自利と利他を一つに見られる人', NULL, '["[OB先輩] 住友が見るのは、『自利利他公私一如』。自分の利と他人の利が一つに見えるか。", "[OB先輩] 倍率は189倍あるけど、本当に見てるのは、人と社風が合うか。", "[nana] 自利と利他が一つ、って言葉、初めて聞いた…", "[haruki] 派手じゃない、長く強い。それは社風から始まってる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_08.png', 'nana', '[nana] このスナックも…ヤマザキビスケットって、住友の子会社なの?
[haruki] そう。TBSも関連会社。テレビと、お菓子と、リモコンと、SCSKと…
[nana] 気づいたら朝から晩まで、住友の事業に触れながら生きてた…
[haruki] 派手じゃないけど、毎日の中にいる。それが住友の強さ。', '毎日の中に、住友がいる', 'ヤマザキビスケット / TBS / J:COM / SCSK / メルカリ', NULL, '["[nana] このスナックも…ヤマザキビスケットって、住友の子会社なの?", "[haruki] そう。TBSも関連会社。テレビと、お菓子と、リモコンと、SCSKと…", "[nana] 気づいたら朝から晩まで、住友の事業に触れながら生きてた…", "[haruki] 派手じゃないけど、毎日の中にいる。それが住友の強さ。"]', 'H3: ヤマザキビスケット商品 (+ H4: TBS赤坂)', '{"location": "中央の商品パッケージ", "object_type": "ヤマザキロゴ", "brand_form": "『Yamazaki』の商品パッケージロゴ、実在の意匠", "attachment": "商品パッケージに印刷", "scale_note": "実在の商品と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_09.png', 'haruki', '[nana] もし入れたら、10年後はどこにいるのかな?
[haruki] たとえば、こんな未来。ドバイの発電所で電力PPA交渉。
[haruki] 大手町本社でJ:COMのアジア展開を企画。
[haruki] 愛媛の別子銅山跡で、400年の発祥地のリニューアル事業。
[nana] 派手じゃないけど深い。どれも長く残る仕事だね。', '10年後、たとえばこんな場面', 'ドバイ / 大手町 / 別子銅山跡(愛媛)', NULL, '["[nana] もし入れたら、10年後はどこにいるのかな?", "[haruki] たとえば、こんな未来。ドバイの発電所で電力PPA交渉。", "[haruki] 大手町本社でJ:COMのアジア展開を企画。", "[haruki] 愛媛の別子銅山跡で、400年の発祥地のリニューアル事業。", "[nana] 派手じゃないけど深い。どれも長く残る仕事だね。"]', 'H6: 海外発電プラント (再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sumitomo-corp', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@9e93cbf/public/images/sumitomo-corp/panel_10.png', 'both', '[haruki] 売上7兆円、純利益5,618億円、採用約100名。
[nana] 派手じゃないのは、戦略だったんだ。
[both] 派手じゃない、長く強い。住友商事、400年の現在地。', '派手じゃない、長く強い。', '売上 約7兆円 / 純利益 約5,618億円 / 採用 約100名', NULL, '["[haruki] 売上7兆円、純利益5,618億円、採用約100名。", "[nana] 派手じゃないのは、戦略だったんだ。", "[both] 派手じゃない、長く強い。住友商事、400年の現在地。"]', 'H1: 大手町プレイス本社 (朝の光)', NULL);
