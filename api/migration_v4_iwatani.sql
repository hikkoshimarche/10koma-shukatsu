-- ===== iwatani (岩谷産業株式会社) =====
-- source: output/iwatani/scenario_v4.json
-- jsDelivr ref: @a183b34
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('iwatani', '岩谷産業株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_01.png', 'nana', '[nana] 朝ごはん、鍋にしてみた。
[haruki] 鍋朝食、いいね。これ、カセットコンロ?
[nana] うん。これって誰が作ってる会社なんだろう?
[haruki] 『カセットフー』、岩谷産業の50年続くロングセラーだよ。日本の家庭の鍋を温めてきた会社。岩谷は自分でこういう製品も作る、商社でありメーカーでもある会社なんだ。', '朝の鍋、誰のコンロ?', '岩谷産業 / 8088 / カセットフー(1969年〜)', NULL, '["[nana] 朝ごはん、鍋にしてみた。", "[haruki] 鍋朝食、いいね。これ、カセットコンロ?", "[nana] うん。これって誰が作ってる会社なんだろう?", "[haruki] 『カセットフー』、岩谷産業の50年続くロングセラーだよ。日本の家庭の鍋を温めてきた会社。岩谷は自分でこういう製品も作る、商社でありメーカーでもある会社なんだ。"]', 'H1: イワタニのカセットコンロ『カセットフー』', '{"location": "カセットコンロ本体上部の中央", "object_type": "ブランドロゴ (Iwatani)", "brand_form": "青いカセットコンロ本体に白文字でブランド名、控えめに", "attachment": "コンロ本体に印刷", "scale_note": "実在のカセットフーの通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_02.png', 'haruki', '[haruki] このカセットボンベも、ぜんぶイワタニだ。
[nana] え、これも?
[haruki] うん、50年以上のロングセラー。鍋もキャンプも、災害備蓄も、ぜんぶイワタニのボンベ。
[nana] 当たり前すぎて気づいてなかったけど、私がカセットコンロを使えるのは岩谷が支えてくれていたからだったんだ…', '鍋・キャンプ・災害備蓄も', 'カセットボンベ / 50年以上', NULL, '["[haruki] このカセットボンベも、ぜんぶイワタニだ。", "[nana] え、これも?", "[haruki] うん、50年以上のロングセラー。鍋もキャンプも、災害備蓄も、ぜんぶイワタニのボンベ。", "[nana] 当たり前すぎて気づいてなかったけど、私がカセットコンロを使えるのは岩谷が支えてくれていたからだったんだ…"]', 'H2: イワタニのカセットボンベ', '{"location": "カセットボンベ本体側面", "object_type": "ブランドロゴ (Iwatani)", "brand_form": "銀色の缶にオレンジ色で『Iwatani』ロゴ、実在のデザイン", "attachment": "缶に印刷", "scale_note": "実在のカセットボンベ通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_03.png', 'nana', '[nana] ねえ、このタンク、見たことある。
[haruki] マルヰガス。日本最大のLPGブランドだよ。約340万世帯が使ってる。
[nana] そんなに。
[haruki] 都市ガスが届かない地域は、ほぼマルヰガス。岩谷が日本の家庭の動脈の半分を担ってるんだ。', 'マルヰガス、約340万世帯', '日本最大のLPGブランド', NULL, '["[nana] ねえ、このタンク、見たことある。", "[haruki] マルヰガス。日本最大のLPGブランドだよ。約340万世帯が使ってる。", "[nana] そんなに。", "[haruki] 都市ガスが届かない地域は、ほぼマルヰガス。岩谷が日本の家庭の動脈の半分を担ってるんだ。"]', 'H3: マルヰガスのLPGボンベ (一軒家の外壁横)', '{"location": "LPGタンクの正面", "object_type": "マルヰマーク (LPGブランド)", "brand_form": "丸の中に『マ』の字、赤と白", "attachment": "タンク正面に印刷", "scale_note": "実在のLPGタンクの通常マーク"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_04.png', 'haruki', '[haruki] あ、水素ステーション。これもイワタニ。
[nana] 水素って、未来のエネルギーだよね。
[haruki] うん。岩谷は国内の水素ステーションのトップシェア。トヨタMIRAIみたいなFCV(燃料電池車)に充填してる。
[nana] カセットコンロからLPG、水素まで、エネルギーを連続でやってる会社…', '未来のエネルギーも、イワタニ', '国内水素ステーションのトップシェア / FCV充填', NULL, '["[haruki] あ、水素ステーション。これもイワタニ。", "[nana] 水素って、未来のエネルギーだよね。", "[haruki] うん。岩谷は国内の水素ステーションのトップシェア。トヨタMIRAIみたいなFCV(燃料電池車)に充填してる。", "[nana] カセットコンロからLPG、水素まで、エネルギーを連続でやってる会社…"]', 'H4: 水素ステーション (トヨタMIRAI充填中)', '{"location": "ステーション上部のサイン", "object_type": "イワタニ水素ステーションのブランドサイン", "brand_form": "ステーション屋根の下に『Iwatani』+ 水素マークのサイン", "attachment": "ステーション構造の一部", "scale_note": "実在の水素ステーション通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_05.png', 'nana', '[nana] 年収ってどうなの?
[haruki] 有価証券報告書(単体)によると平均約820万円(平均年齢42歳)。
[haruki] でも岩谷はエネルギー専業で、LPG・水素・産業ガスの3本柱。業績が動けば年収も動く。
[nana] 会社の規模より、エネルギーの値動きと自分の給料が連動する仕事なんだね。', '平均約820万円(有報単体・平均年齢42歳)+エネルギー価格連動', 'LPG・水素・産業ガス専業ゆえの業績連動型', '公式・有報', '["[nana] 年収ってどうなの?", "[haruki] 有価証券報告書(単体)によると平均約820万円(平均年齢42歳)。", "[haruki] でも岩谷はエネルギー専業で、LPG・水素・産業ガスの3本柱。業績が動けば年収も動く。", "[nana] 会社の規模より、エネルギーの値動きと自分の給料が連動する仕事なんだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_06.png', 'nana', '[nana] 働き方はどうですか?
[OB先輩] フレックス・リモート両方あるよ。エネルギー業界だから、災害時の現場対応はあるけどね。
[OB先輩] 福利厚生は『独身寮』と『社宅』が手厚い。大阪本社なら、堂島近くの寮があるから家賃の心配がほぼなくなる。
[haruki] 関西の若手で大阪市内に住むと家賃の負担が大きいけど、それがほぼ無くなるってことか…', 'フレックス+リモート+独身寮あり', '独身寮(堂島近く)・社宅で家賃ほぼ ↓', NULL, '["[nana] 働き方はどうですか?", "[OB先輩] フレックス・リモート両方あるよ。エネルギー業界だから、災害時の現場対応はあるけどね。", "[OB先輩] 福利厚生は『独身寮』と『社宅』が手厚い。大阪本社なら、堂島近くの寮があるから家賃の心配がほぼなくなる。", "[haruki] 関西の若手で大阪市内に住むと家賃の負担が大きいけど、それがほぼ無くなるってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_07.png', 'nana', '[nana] 採用人数は60〜80名/年なんですね。
[OB先輩] そう。キャリアはLPGの全国営業、水素の研究開発、産業ガスのプラント営業に分岐する。
[OB先輩] 配属の第一希望がそのまま通る人は半分くらい。地方配属(LPG)もある。海外駐在は東南アジア(LPG)や欧州(水素技術)。
[haruki] 5大商社みたいな海外駐在中心じゃなくて、日本の地方にも根を張る働き方もあるんだ…', '60〜80名/年、地方も海外も', 'LPG全国営業 / 水素R&D / 産業ガス', NULL, '["[nana] 採用人数は60〜80名/年なんですね。", "[OB先輩] そう。キャリアはLPGの全国営業、水素の研究開発、産業ガスのプラント営業に分岐する。", "[OB先輩] 配属の第一希望がそのまま通る人は半分くらい。地方配属(LPG)もある。海外駐在は東南アジア(LPG)や欧州(水素技術)。", "[haruki] 5大商社みたいな海外駐在中心じゃなくて、日本の地方にも根を張る働き方もあるんだ…"]', 'H7: 業務用LPG配送車', '{"location": "配送トラックの側面", "object_type": "マルヰマーク+社名", "brand_form": "トラック側面に大きなマルヰマークと『マルヰガス / 岩谷産業』の表示", "attachment": "トラック側面に印刷", "scale_note": "実在の配送車の通常表記"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_08.png', 'nana', '[OB先輩] 岩谷が見るのは、『世のため人のため』を体現できる人。
[OB先輩] 倍率は30〜50倍だけど、見てるのはエネルギーで誰かの生活を支える覚悟があるか。
[nana] カセットコンロからオリンピック聖火まで、ぜんぶ『世のため人のため』なんだ…
[haruki] 派手じゃないけど、誰かの今日を温める仕事、ってことだね。', '見てるのは『世のため人のため』', '倍率より、誰かの今日を温める覚悟', NULL, '["[OB先輩] 岩谷が見るのは、『世のため人のため』を体現できる人。", "[OB先輩] 倍率は30〜50倍だけど、見てるのはエネルギーで誰かの生活を支える覚悟があるか。", "[nana] カセットコンロからオリンピック聖火まで、ぜんぶ『世のため人のため』なんだ…", "[haruki] 派手じゃないけど、誰かの今日を温める仕事、ってことだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。福岡でLPG営業所長として地域のガスを支えてる。
[haruki] デュッセルドルフで欧州の水素技術の合弁事業を立ち上げ。
[haruki] 大阪本社で次世代カセットコンロの企画。50年続く商品の次を考える。
[nana] 朝のコンロから、夜のキャンプまで。私が動かすエネルギー、人の生活と続いてる…', '10年後、たとえばこんな場面', '福岡(LPG) / デュッセルドルフ(水素) / 大阪(企画)', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。福岡でLPG営業所長として地域のガスを支えてる。", "[haruki] デュッセルドルフで欧州の水素技術の合弁事業を立ち上げ。", "[haruki] 大阪本社で次世代カセットコンロの企画。50年続く商品の次を考える。", "[nana] 朝のコンロから、夜のキャンプまで。私が動かすエネルギー、人の生活と続いてる…"]', 'H5: キャンプシーンのカセットコンロ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('iwatani', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@a183b34/public/images/iwatani/panel_10.png', 'both', '[haruki] カセットコンロ国内シェアNo.1、マルヰガス約340万世帯、採用60〜80名。
[nana] 朝のカセットコンロから、オリンピック聖火台まで。岩谷の水素が、世界を照らした。
[both] 朝から夜まで、365日、岩谷と一緒に生きている。', '朝から夜まで、365日、岩谷と。', 'カセットフー1969〜 / マルヰガス約340万世帯 / 東京2020 水素聖火', NULL, '["[haruki] カセットコンロ国内シェアNo.1、マルヰガス約340万世帯、採用60〜80名。", "[nana] 朝のカセットコンロから、オリンピック聖火台まで。岩谷の水素が、世界を照らした。", "[both] 朝から夜まで、365日、岩谷と一緒に生きている。"]', 'H6: 東京2020オリンピック聖火台', NULL);
