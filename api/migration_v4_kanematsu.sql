-- ===== kanematsu (兼松株式会社) =====
-- source: output/kanematsu/scenario_v4.json
-- jsDelivr ref: @36be84b
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('kanematsu', '兼松株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_01.png', 'nana', '[nana] 商社って5大商社しか聞いたことない…
[haruki] 三菱・三井・伊藤忠・住友・丸紅、ね。
[nana] うん。それ以外って、どうなってるの?
[haruki] そこに、もう一段先がある。第7商社=兼松。1889年から続いてる。', '5大商社しか知らない? 一段先へ', '兼松 / 8020 / 1889年〜', NULL, '["[nana] 商社って5大商社しか聞いたことない…", "[haruki] 三菱・三井・伊藤忠・住友・丸紅、ね。", "[nana] うん。それ以外って、どうなってるの?", "[haruki] そこに、もう一段先がある。第7商社=兼松。1889年から続いてる。"]', 'H1: 兼松本社 シーバンスN館 (芝浦の運河沿い)', '{"location": "シーバンスN館の外壁上部", "object_type": "建築サイン (Kanematsu)", "brand_form": "ビル外壁に控えめな『Kanematsu』サイン", "attachment": "ビル外壁固定", "scale_note": "実在の本社ビル通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_02.png', 'haruki', '[haruki] ある5大商社Aは売上19兆円。兼松は7,700億円。約25分の1。
[nana] そんなに違うの…
[haruki] でも純利益で見ると、兼松の利益率は5大商社と遜色ない。
[nana] 規模で戦わずに、利益率で戦ってるってこと?', '規模じゃ戦わない、選択', '売上 約7,700億円 / 純利益 約200億円 / 利益率で勝負', '公式IR', '["[haruki] ある5大商社Aは売上19兆円。兼松は7,700億円。約25分の1。", "[nana] そんなに違うの…", "[haruki] でも純利益で見ると、兼松の利益率は5大商社と遜色ない。", "[nana] 規模で戦わずに、利益率で戦ってるってこと?"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_03.png', 'haruki', '[haruki] 電子・デバイスが兼松の主力。スマホの半導体部品、ぜんぶ兼松経由で動いてる。
[nana] え、私のスマホの中も?
[haruki] ある商社Bが資源で戦うとしたら、兼松は半導体トレード。電子の方が利益率が高い。
[nana] 規模じゃなくて、勝てる場所を選んでるんだ…', 'スマホの中、兼松経由', '電子・デバイスが主力 / 半導体トレード', NULL, '["[haruki] 電子・デバイスが兼松の主力。スマホの半導体部品、ぜんぶ兼松経由で動いてる。", "[nana] え、私のスマホの中も?", "[haruki] ある商社Bが資源で戦うとしたら、兼松は半導体トレード。電子の方が利益率が高い。", "[nana] 規模じゃなくて、勝てる場所を選んでるんだ…"]', 'H3: 半導体ウェハの輸送ケース', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_04.png', 'haruki', '[haruki] 食料も主力。ブラジル・コロンビアからコーヒー豆を年間数万トン輸入。
[nana] え、私が毎朝飲むコーヒー、もしかして…
[haruki] そう、カフェチェーンの豆はかなり兼松経由。インスタント麺の小麦原料もそう。
[nana] 表に出ないだけで、朝の食卓は兼松だらけだったんだ…', '朝のコーヒー、麺、ぜんぶ兼松', 'ブラジル・コロンビアからの豆 / 食料原料', NULL, '["[haruki] 食料も主力。ブラジル・コロンビアからコーヒー豆を年間数万トン輸入。", "[nana] え、私が毎朝飲むコーヒー、もしかして…", "[haruki] そう、カフェチェーンの豆はかなり兼松経由。インスタント麺の小麦原料もそう。", "[nana] 表に出ないだけで、朝の食卓は兼松だらけだったんだ…"]', 'H2: コーヒー麻袋を積んだ倉庫 (+ H6 インスタント麺)', '{"location": "麻袋の側面", "object_type": "麻袋のスタンプ (KANEMATSU)", "brand_form": "麻袋に黒インクのスタンプで『KANEMATSU』と『COFFEE』の文字", "attachment": "麻袋にスタンプ印刷", "scale_note": "実在のコーヒー麻袋の通常表記"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_05.png', 'nana', '[nana] 兼松の年収は?
[haruki] 平均1,143万円。ある商社Aの2,033万円と比べると低い。
[haruki] でも社員数が少ない分、1人あたりの裁量と利益貢献が大きい。手当も電子・食料の業績連動。
[nana] 大きい商社の半分弱、でも一人あたりの責任は同じくらい大きい、ってことか…', '1,143万円(平均)+少人数で裁量', 'ベース / 電子・食料連動', '日経会社情報 8020', '["[nana] 兼松の年収は?", "[haruki] 平均1,143万円。ある商社Aの2,033万円と比べると低い。", "[haruki] でも社員数が少ない分、1人あたりの裁量と利益貢献が大きい。手当も電子・食料の業績連動。", "[nana] 大きい商社の半分弱、でも一人あたりの責任は同じくらい大きい、ってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_06.png', 'nana', '[nana] 働き方ってどんな感じですか?
[OB先輩] 電子事業は繁忙期が長いけど、フレックスとリモートが両方使えるよ。
[OB先輩] 福利厚生で大きいのは、独身寮と家賃補助。芝浦の社員寮があるから、20代の家賃の心配がほぼなくなる。
[haruki] 給料の額より、住居コストが浮く分が大きいってことか…', 'フレックス+リモート可+独身寮あり', '独身寮・家賃補助で住居コスト ↓', NULL, '["[nana] 働き方ってどんな感じですか?", "[OB先輩] 電子事業は繁忙期が長いけど、フレックスとリモートが両方使えるよ。", "[OB先輩] 福利厚生で大きいのは、独身寮と家賃補助。芝浦の社員寮があるから、20代の家賃の心配がほぼなくなる。", "[haruki] 給料の額より、住居コストが浮く分が大きいってことか…"]', 'H1: 兼松本社 シーバンスN館 (再使用・運河の夜景)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_07.png', 'nana', '[nana] 採用が7-15名って、すごく少ないですよね。
[OB先輩] うん、内定はめちゃくちゃ難しい。でも入ってからは、若手から大きく任される。
[OB先輩] 入社2〜3年で海外駐在は当たり前。電子なら台湾・韓国、食料ならブラジル、航空ならアメリカ。
[haruki] 少人数で機動的、ってのが規模の代わりの戦力なんだ…', '7-15名/年、入社2〜3年で海外', '少人数で機動的 / 電子=台韓、食料=ブラジル、航空=米', NULL, '["[nana] 採用が7-15名って、すごく少ないですよね。", "[OB先輩] うん、内定はめちゃくちゃ難しい。でも入ってからは、若手から大きく任される。", "[OB先輩] 入社2〜3年で海外駐在は当たり前。電子なら台湾・韓国、食料ならブラジル、航空ならアメリカ。", "[haruki] 少人数で機動的、ってのが規模の代わりの戦力なんだ…"]', 'H4: 航空機の主翼部品', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_08.png', 'haruki', '[haruki] 1889年、創業者 兼松房治郎が豪州との貿易から始めた。
[nana] 明治22年!? 130年以上前…
[haruki] 兼松房治郎の遺した言葉:『直道は近道なり』。誠実が最大の近道。
[nana] 130年、規模で勝負しない選択を続けてきたんだ。', '1889年、規模より質を選んだ', '兼松房治郎 / 直道は近道なり', NULL, '["[haruki] 1889年、創業者 兼松房治郎が豪州との貿易から始めた。", "[nana] 明治22年!? 130年以上前…", "[haruki] 兼松房治郎の遺した言葉:『直道は近道なり』。誠実が最大の近道。", "[nana] 130年、規模で勝負しない選択を続けてきたんだ。"]', 'H5: 明治の暖簾 (『兼』の社章)', '{"location": "壁面中央の暖簾", "object_type": "創業時の暖簾 (社章)", "brand_form": "藍色の和風暖簾、白抜きで『兼』の文字", "attachment": "壁面に固定された展示", "scale_note": "実在の社章展示の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_09.png', 'nana', '[OB先輩] 兼松が見るのは、『直道は近道なり』を体現できる人。
[OB先輩] 倍率は確かに高い。でも一番見てるのは、規模を追わず、質で勝負できる人。
[nana] (静かに) 派手じゃなくていい、ってこと…
[haruki] 大手商社の若手と同じ量の仕事をやる覚悟があるか、ってことだね。', '見てるのは『質で戦える人』', '倍率じゃなく、直道は近道なり', NULL, '["[OB先輩] 兼松が見るのは、『直道は近道なり』を体現できる人。", "[OB先輩] 倍率は確かに高い。でも一番見てるのは、規模を追わず、質で勝負できる人。", "[nana] (静かに) 派手じゃなくていい、ってこと…", "[haruki] 大手商社の若手と同じ量の仕事をやる覚悟があるか、ってことだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kanematsu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@36be84b/public/images/kanematsu/panel_10.png', 'both', '[haruki] 売上7,700億円、純利益約200億円、採用7-15名。
[nana] 5大商社の競争に参加せず、自分の戦い方を130年続けてる。
[both] **5大商社じゃない。だから、戦い方が違う。**', '5大商社じゃない。だから、戦い方が違う。', '売上 約7,700億円 / 純利益 約200億円 / 採用7-15名', NULL, '["[haruki] 売上7,700億円、純利益約200億円、採用7-15名。", "[nana] 5大商社の競争に参加せず、自分の戦い方を130年続けてる。", "[both] **5大商社じゃない。だから、戦い方が違う。**"]', 'H1: 兼松本社シーバンスN館 (朝の光)', NULL);
