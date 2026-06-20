-- ===== marubeni (丸紅株式会社) =====
-- source: output/marubeni/scenario_v4.json
-- jsDelivr ref: @3486a64
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('marubeni', '丸紅株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_01.png', 'nana', '[nana] 丸紅のリクルートサイト見て。『正・新・和』って3文字、書いてある。
[haruki] あ、それが丸紅の理念だね。
[nana] この3文字で、丸紅でのキャリアの分岐が決まる気がするんだけど、本当?
[haruki] そう、9つの営業グループ、どこに行ってもこの3文字が指針になる。', '3文字で、キャリアの分岐が決まる', '丸紅 / 8002 / 正・新・和', NULL, '["[nana] 丸紅のリクルートサイト見て。『正・新・和』って3文字、書いてある。", "[haruki] あ、それが丸紅の理念だね。", "[nana] この3文字で、丸紅でのキャリアの分岐が決まる気がするんだけど、本当?", "[haruki] そう、9つの営業グループ、どこに行ってもこの3文字が指針になる。"]', 'H5: 緑の丸に紅字の社章', '{"location": "ノートパソコン画面の中央", "object_type": "理念表記 (社の固有3文字)", "brand_form": "『正・新・和』が縦並びで表示されたリクルートサイトの画面、緑と白", "attachment": "ノートパソコン画面の表示", "scale_note": "実在のリクルートサイト画面の通常表示"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_02.png', 'haruki', '[haruki] 純利益4,800億円、売上7兆円。
[nana] 4,800億…
[haruki] 5大商社の中で規模は突出していないけど、得意分野では世界トップクラス。
[nana] その規模で、世界トップ? どこで?', '純利益4,800億円(2025年3月期)', '売上 約7兆円 / 9事業グループ', '公式IR', '["[haruki] 純利益4,800億円、売上7兆円。", "[nana] 4,800億…", "[haruki] 5大商社の中で規模は突出していないけど、得意分野では世界トップクラス。", "[nana] その規模で、世界トップ? どこで?"]', 'H1: 丸紅本社ビル (大手町)', '{"location": "本社ビル上部の外壁", "object_type": "建築サイン (Marubeni)", "brand_form": "ガラスファサード上部に『Marubeni』のサイン、控えめに", "attachment": "ビル外壁の建築サインとして固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_03.png', 'haruki', '[haruki] 1つ目の強み、米国の小麦輸入。日本でシェアNo.1。
[nana] え、丸紅が一番多く運んでるの?
[haruki] そう。朝のパン、お昼のパスタ、夕食のうどん。スーパーで手に取った小麦のほとんどが、元を辿ると丸紅。
[nana] 米国の畑から、私の朝食まで、全部1つの会社が動かしてるんだ…', '米国小麦シェアNo.1', 'パン・麺・おにぎりの裏方', NULL, '["[haruki] 1つ目の強み、米国の小麦輸入。日本でシェアNo.1。", "[nana] え、丸紅が一番多く運んでるの?", "[haruki] そう。朝のパン、お昼のパスタ、夕食のうどん。スーパーで手に取った小麦のほとんどが、元を辿ると丸紅。", "[nana] 米国の畑から、私の朝食まで、全部1つの会社が動かしてるんだ…"]', 'H2: 米国の小麦畑', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_04.png', 'haruki', '[haruki] 2つ目の強み、海外発電。中東・東南アジアの発電所を運営。
[nana] 商社が、発電所を運営?
[haruki] そう。建設して終わりじゃなくて、20〜30年単位で電気を売る。海外電力IPPで世界トップクラス。
[nana] 小麦と発電…全然違う2つの世界を、同じ会社が回してる…', '海外発電IPPで世界トップクラス', '20〜30年で電気を売る事業', NULL, '["[haruki] 2つ目の強み、海外発電。中東・東南アジアの発電所を運営。", "[nana] 商社が、発電所を運営?", "[haruki] そう。建設して終わりじゃなくて、20〜30年単位で電気を売る。海外電力IPPで世界トップクラス。", "[nana] 小麦と発電…全然違う2つの世界を、同じ会社が回してる…"]', 'H3: 海外大規模発電所', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_05.png', 'nana', '[nana] 丸紅の年収って、いくらなの?
[haruki] 平均1,709万円。でも、構造が大事。
[haruki] ベース+海外駐在手当+リスク手当。シカゴ駐在(小麦)とドバイ駐在(発電)で、額が大きく変わる。
[nana] 同じ丸紅でも、駐在地で手当が違うんだ。', '1,709万円(平均)+駐在地で変動', 'シカゴ(小麦) / ドバイ(発電) で手当差', '日経会社情報 8002', '["[nana] 丸紅の年収って、いくらなの?", "[haruki] 平均1,709万円。でも、構造が大事。", "[haruki] ベース+海外駐在手当+リスク手当。シカゴ駐在(小麦)とドバイ駐在(発電)で、額が大きく変わる。", "[nana] 同じ丸紅でも、駐在地で手当が違うんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_06.png', 'haruki', '[haruki] 9つの営業グループ。生活産業、食料、エネルギー・金属、化学、電力、インフラ、航空・船舶、金融・リース、ICT・不動産。
[nana] 9つ…私はどこ?
[haruki] 入った後の配属で決まる。希望は出せるけど、その通りに行くとは限らない。
[nana] でも、どこに行くかで、10年後の私が全然違うってこと…', '9つの営業グループ、どこに?', '生活産業 / 食料 / エネ金属 / 化学 / 電力 / インフラ / 航空船舶 / 金融リース / ICT不動産', NULL, '["[haruki] 9つの営業グループ。生活産業、食料、エネルギー・金属、化学、電力、インフラ、航空・船舶、金融・リース、ICT・不動産。", "[nana] 9つ…私はどこ?", "[haruki] 入った後の配属で決まる。希望は出せるけど、その通りに行くとは限らない。", "[nana] でも、どこに行くかで、10年後の私が全然違うってこと…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_07.png', 'nana', '[nana] 配属って、希望通りに行けるんですか?
[OB先輩] 正直、第一希望そのまま通る人は半分くらい。米国・シカゴ駐在(小麦)は、3〜5年でほぼ普通にある。
[OB先輩] 食料部門と電力部門は、若いうちから海外に出る。希望と違う部門でも、現地で覚悟を決める人が伸びる。
[haruki] 9つのどこに入っても、5年で世界のどこかにいるってことか…', '5年で世界のどこかに', '第一希望通る人は半分 / シカゴ・ドバイ駐在は普通', NULL, '["[nana] 配属って、希望通りに行けるんですか?", "[OB先輩] 正直、第一希望そのまま通る人は半分くらい。米国・シカゴ駐在(小麦)は、3〜5年でほぼ普通にある。", "[OB先輩] 食料部門と電力部門は、若いうちから海外に出る。希望と違う部門でも、現地で覚悟を決める人が伸びる。", "[haruki] 9つのどこに入っても、5年で世界のどこかにいるってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_08.png', 'nana', '[OB先輩] 丸紅が見るのは、『正・新・和』。正しい行動、新しい価値、和をもって事業に取り組むか。
[OB先輩] 応募者は多数だが、この3文字を体現できる人を求めている。
[nana] (静かに) 9つのどこに行っても、その3文字が指針になるんだ…
[haruki] どの部署でも、この3文字が自分のキャリアの方向性を形作る。', '見てるのは『正・新・和』', '倍率じゃない、3文字に合うか', NULL, '["[OB先輩] 丸紅が見るのは、『正・新・和』。正しい行動、新しい価値、和をもって事業に取り組むか。", "[OB先輩] 応募者は多数だが、この3文字を体現できる人を求めている。", "[nana] (静かに) 9つのどこに行っても、その3文字が指針になるんだ…", "[haruki] どの部署でも、この3文字が自分のキャリアの方向性を形作る。"]', 'H5: 緑の丸に紅字の社章 (再使用)', '{"location": "壁面中央", "object_type": "理念の3文字額または掲示", "brand_form": "『正・新・和』が縦書きで書かれた額、緑と白", "attachment": "壁面に固定", "scale_note": "実在の社内掲示の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。シカゴで小麦トレーディングをドル建てで動かしてる。
[haruki] バンコクで太陽光IPPを着工。
[haruki] 大手町本社でNYと電話会議しながら、新本部の設立を起案。
[nana] こんな未来、どれも私が選べる。この3文字を軸にすればいい。', '10年後、たとえばこんな場面', 'シカゴ / バンコク / 大手町(電話会議)', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。シカゴで小麦トレーディングをドル建てで動かしてる。", "[haruki] バンコクで太陽光IPPを着工。", "[haruki] 大手町本社でNYと電話会議しながら、新本部の設立を起案。", "[nana] こんな未来、どれも私が選べる。この3文字を軸にすればいい。"]', 'H4: 食品スーパーのパン棚 + H2 + H3 (3つの未来)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('marubeni', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@3486a64/public/images/marubeni/panel_10.png', 'both', '[haruki] 売上7兆円、純利益4,800億円、採用77名。
[nana] 細かく分岐しているように見えて、理念の3文字が進むべき方向を定めてくれる。
[both] 正しく、新しく、和をもって。丸紅、9つの分岐から、世界へ。', '正しく、新しく、和をもって。', '売上 約7兆円 / 純利益 約4,800億円 / 採用77名', NULL, '["[haruki] 売上7兆円、純利益4,800億円、採用77名。", "[nana] 細かく分岐しているように見えて、理念の3文字が進むべき方向を定めてくれる。", "[both] 正しく、新しく、和をもって。丸紅、9つの分岐から、世界へ。"]', 'H1: 丸紅本社ビル (朝の光)', NULL);
