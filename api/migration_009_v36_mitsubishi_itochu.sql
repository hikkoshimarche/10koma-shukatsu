-- ===== Schema 拡張 (v3.6 構造化情報用、初回のみ実行) =====
-- 既に存在する列に対する ALTER TABLE はエラーになるが、INSERT には影響なし。
-- 必要に応じて手動でコメントアウトしてから流すこと。

ALTER TABLE company_panels ADD COLUMN main_copy TEXT;
ALTER TABLE company_panels ADD COLUMN sub_copy TEXT;
ALTER TABLE company_panels ADD COLUMN source_url TEXT;
ALTER TABLE company_panels ADD COLUMN script_json TEXT;
ALTER TABLE company_panels ADD COLUMN visual_hook TEXT;
ALTER TABLE company_panels ADD COLUMN brand_object_json TEXT;

-- ===== mitsubishi-corp (三菱商事株式会社) =====
-- source: output/mitsubishi-corp/scenario.json
-- jsDelivr ref: @7cfd454 (commit-pinned post-push, 2026-06-17)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('mitsubishi-corp', '三菱商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_01.png', 'nana', '[nana] ねぇハルキ、就活で『三菱商事』って聞いたことある?
[haruki] あるけど…日本のビジネスを裏で動かしてる会社、ってイメージしかない。
[nana] それなのよ。実は私たちの生活、全部この会社に触れてる。', 'その会社、知ってる?', '三菱商事 / 8058', NULL, '["[nana] ねぇハルキ、就活で『三菱商事』って聞いたことある?", "[haruki] あるけど…日本のビジネスを裏で動かしてる会社、ってイメージしかない。", "[nana] それなのよ。実は私たちの生活、全部この会社に触れてる。"]', 'H1: 丸の内パークビルディング(本社)の建築サイン(赤いスリーダイヤ+漢字「三菱商事」)', '{"location": "中央の超高層ビル最上部の外壁面(画面上部1/4〜1/3の高さ)", "object_type": "建物の構造の一部として取り付けられた立体的な建築サイン(金属プレート+レリーフ文字)", "brand_form": "赤い金属で成型された立体的なスリーダイヤ(3つのダイヤモンドが互いに組み合わさった三菱の形状)と、その真下に並ぶ漢字「三菱商事」の社名サイン", "attachment": "ビル外壁の石材またはガラスパネルに金属ボルトで物理的に固定され、外壁の質感と一体化。見上げのパースで台形に歪んで見える(下辺が広く上辺が狭まる)。朝の光が金属表面で反射し、外壁に薄い影が落ちる", "scale_note": "実在の丸の内の大企業ビル建築サインと同じ控えめな比率。ビル最上部に小さくおさまるサイズで、巨大化や看板化はしない"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_02.png', 'both', '[both] え、19兆円!?
[haruki] 売上19兆円。純利益8,000億円。
[nana] それ、国家予算の話してる…?', '売上 19兆円 / 純利益 8,000億円', '2025年度通期(連結)', 'IRBANK 8058', '["[both] え、19兆円!?", "[haruki] 売上19兆円。純利益8,000億円。", "[nana] それ、国家予算の話してる…?"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_03.png', 'nana', '[nana] 今晩のおかず、伊藤ハムのソーセージなんだけど。
[haruki] それ三菱商事グループだよ。
[nana] え、じゃあこの成城石井のチーズも?
[haruki] それも。あと明日の朝のローソンのコーヒーもね。', '全部、三菱商事グループ。', NULL, NULL, '["[nana] 今晩のおかず、伊藤ハムのソーセージなんだけど。", "[haruki] それ三菱商事グループだよ。", "[nana] え、じゃあこの成城石井のチーズも?", "[haruki] それも。あと明日の朝のローソンのコーヒーもね。"]', 'H2: ローソン店舗ファサード(青と白の看板、ミルク缶モチーフ)', '{"location": "ダイニングの窓の外、夕暮れの街並みの一角(画面右奥)", "object_type": "コンビニエンスストア店舗のファサード看板", "brand_form": "青と白を基調にした「LAWSON」の店舗看板と、ミルク缶のシンボルマークが筐体に組み込まれた、店舗ファサードの一部としてのサイン", "attachment": "夜の街並みの一店舗として歩道沿いに自然に佇み、店内の蛍光灯の明かりが看板を背後から照らす。街並みのスケールに馴染んだ通常サイズ", "scale_note": "窓越しに小さく見える、控えめなサイズ。画面の主役ではなく、街並みのワンポイントとして馴染ませる"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_04.png', 'haruki', '[haruki] それだけじゃない。スマホの電気も、車のガソリンも、家の鉄も。
[nana] 全部関係あるの?
[haruki] 天然ガス、金属資源、化学品。原料のところを握ってる。
[nana] 触れてない日が、逆にない…', '原料から、押さえている。', NULL, NULL, '["[haruki] それだけじゃない。スマホの電気も、車のガソリンも、家の鉄も。", "[nana] 全部関係あるの?", "[haruki] 天然ガス、金属資源、化学品。原料のところを握ってる。", "[nana] 触れてない日が、逆にない…"]', 'H3: LNGタンカー(三菱商事の天然ガス事業の象徴、夜の港湾を航行)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_05.png', 'nana', '[nana] ところで…ここ、お給料いくらなの?
[haruki] 平均年収、2,033万円。
[nana] にせん…?
[haruki] 平均年齢42歳で、ね。', '2,033万円', '平均年齢 42.4歳 / 2024年度有報', '日経会社情報 8058', '["[nana] ところで…ここ、お給料いくらなの?", "[haruki] 平均年収、2,033万円。", "[nana] にせん…?", "[haruki] 平均年齢42歳で、ね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_06.png', 'nana', '[nana] その年収、何が買えるの?
[haruki] 都心のタワマンも視野。ローンを組めば、ね。
[nana] 同じ国に住んでるのに、見える物件のグレードが違いすぎる…', '見える物件のグレードが違う。', NULL, NULL, '["[nana] その年収、何が買えるの?", "[haruki] 都心のタワマンも視野。ローンを組めば、ね。", "[nana] 同じ国に住んでるのに、見える物件のグレードが違いすぎる…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_07.png', 'nana', '[nana] …でも、入れる気がしない。
[haruki] 採用139人。エントリーは14,512人。
[nana] 100倍超…
[haruki] うん。普通の意気込みじゃ無理。', '100倍超。', '採用 139名 / プレエントリー 14,512人', 'talentsquare 採用集計・リクナビ', '["[nana] …でも、入れる気がしない。", "[haruki] 採用139人。エントリーは14,512人。", "[nana] 100倍超…", "[haruki] うん。普通の意気込みじゃ無理。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_08.png', 'haruki', '[haruki] でもね、139人のうち、女性が50人。文系が108人。
[nana] え、文系で7〜8割?
[haruki] そう。理系の専門知識より『芯』と『共創力』を見てる。
[nana] それなら…私が立てる土俵に、ある。', '土俵は、ある。', NULL, NULL, '["[haruki] でもね、139人のうち、女性が50人。文系が108人。", "[nana] え、文系で7〜8割?", "[haruki] そう。理系の専門知識より『芯』と『共創力』を見てる。", "[nana] それなら…私が立てる土俵に、ある。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_09.png', 'haruki', '[nana] もし入れたら、何ができるの?
[haruki] 例えば3つ。シンガポールでLNGをトレード。
[haruki] ニューヨークで成長企業に投資する事業投資。
[haruki] 東京でローソンの事業経営。
[nana] 3つとも、全然違う未来。', '未来は、3つどころじゃない。', NULL, NULL, '["[nana] もし入れたら、何ができるの?", "[haruki] 例えば3つ。シンガポールでLNGをトレード。", "[haruki] ニューヨークで成長企業に投資する事業投資。", "[haruki] 東京でローソンの事業経営。", "[nana] 3つとも、全然違う未来。"]', 'H6: 三菱商事の海外3拠点(東京・シンガポール・NY)が地図上に光る', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/mitsubishi-corp/panel_10.png', 'both', '[haruki] 三綱領—所期奉公・処事光明・立業貿易。1934年から変わらない指針。
[nana] 139人の枠に、私たちも挑む。
[both] 必要なのは、芯と、共創力。', '139名の枠に、私たちも挑む。', '芯 と 共創力。', NULL, '["[haruki] 三綱領—所期奉公・処事光明・立業貿易。1934年から変わらない指針。", "[nana] 139人の枠に、私たちも挑む。", "[both] 必要なのは、芯と、共創力。"]', 'H5: 三綱領(所期奉公・処事光明・立業貿易)が刻まれた石碑を遊歩道の傍らに配置', NULL);

-- ===== itochu (伊藤忠商事株式会社) =====
-- source: output/itochu-shoji/scenario.json
-- jsDelivr ref: @7cfd454 (commit-pinned post-push, 2026-06-17)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('itochu', '伊藤忠商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_01.png', 'nana', '[nana] ねぇハルキ、就活で『伊藤忠商事』って聞いたことある?
[haruki] あるけど…ファミマの会社、ってイメージしかない。
[nana] それなのよ。実は今着てる服も、元をたどれば伊藤忠の繊維事業からなのよ。', 'その会社、知ってる?', '伊藤忠商事 / 8001', NULL, '["[nana] ねぇハルキ、就活で『伊藤忠商事』って聞いたことある?", "[haruki] あるけど…ファミマの会社、ってイメージしかない。", "[nana] それなのよ。実は今着てる服も、元をたどれば伊藤忠の繊維事業からなのよ。"]', 'H6: 巨大な繊維倉庫(伊藤忠の繊維事業の象徴、反物・布地のロールが整然と並ぶ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_02.png', 'both', '[both] え、純利益8,800億円!?
[haruki] 売上14兆7,000億円。過去最高益。
[nana] 待って、いま家計の話してた気がするんだけど…', '純利益 8,803億円 (過去最高)', '売上 14.7兆円 / 2025年3月期', '公式 決算ハイライト', '["[both] え、純利益8,800億円!?", "[haruki] 売上14兆7,000億円。過去最高益。", "[nana] 待って、いま家計の話してた気がするんだけど…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_03.png', 'nana', '[nana] (スマホをかざして) ピッ。
[haruki] それファミマだろ?伊藤忠の完全子会社。
[nana] え、レジを通るたびに、伊藤忠の売上になってるってこと?
[haruki] そう。あと、棚に並んでる『コンビニウェア』も、伊藤忠の繊維部門が企画したもの。', 'レジを通るたび、伊藤忠グループ。', NULL, NULL, '["[nana] (スマホをかざして) ピッ。", "[haruki] それファミマだろ?伊藤忠の完全子会社。", "[nana] え、レジを通るたびに、伊藤忠の売上になってるってこと?", "[haruki] そう。あと、棚に並んでる『コンビニウェア』も、伊藤忠の繊維部門が企画したもの。"]', 'H2: ファミリーマート店舗(緑と白の店内、ファミマグリーンのレジカウンター上看板)', '{"location": "レジカウンターの真上の壁面と、店外に向かう側のガラスファサード", "object_type": "コンビニエンスストアの店舗看板と店内のサイン", "brand_form": "緑(FAMILY MARTグリーン)と白を基調にした『FamilyMart』のロゴサインが、レジ上の壁面パネルと店外ファサードの両方に設置されている", "attachment": "店舗筐体の一部としてアクリル製の照明付きパネルがビスで取り付けられている。店舗の標準的なサイン", "scale_note": "実在のファミマ店舗と同じ通常サイズ。レジ周りに自然に馴染むスケール"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_04.png', 'haruki', '[haruki] 上から見ると、伊藤忠の事業ってどこにでもある。
[nana] 服、コンビニ、住宅、保険…
[haruki] 食品、機械、エネルギー、金融。商社って『街そのもの』の運営者なんだよ。', '街そのものに、商社がいる。', NULL, NULL, '["[haruki] 上から見ると、伊藤忠の事業ってどこにでもある。", "[nana] 服、コンビニ、住宅、保険…", "[haruki] 食品、機械、エネルギー、金融。商社って『街そのもの』の運営者なんだよ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_05.png', 'nana', '[nana] ねぇ、ここの年収って…
[haruki] 平均1,805万円。
[nana] (スマホがすべり落ちかける) えっ。
[haruki] 平均年齢42歳で、ね。', '1,805万円', '平均年齢 42.2歳 / 2025年3月期有報', '日経会社情報 8001', '["[nana] ねぇ、ここの年収って…", "[haruki] 平均1,805万円。", "[nana] (スマホがすべり落ちかける) えっ。", "[haruki] 平均年齢42歳で、ね。"]', 'H1: 青山の伊藤忠商事東京本社ビル(マホガニー・レッドの石材外装の高層ビル)が背景遠景に控えめに見える', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_06.png', 'nana', '[nana] その年収、何が買えるの?
[haruki] 都心の腕時計から、別荘の頭金まで。
[nana] 同じ時代に生きてるはずなのに、見えてる景色が違いすぎる…', '見えてる景色が違いすぎる。', NULL, NULL, '["[nana] その年収、何が買えるの?", "[haruki] 都心の腕時計から、別荘の頭金まで。", "[nana] 同じ時代に生きてるはずなのに、見えてる景色が違いすぎる…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_07.png', 'nana', '[nana] でも…無理な気がしてきた。
[haruki] 採用 約129人。エントリーは2万8,700人超。
[nana] 200倍超…
[haruki] うん。普通の意気込みじゃ届かない。', '200倍超。', '総合職採用 129名 / プレエントリー 28,751人', 'talentsquare 採用集計 / リクナビ', '["[nana] でも…無理な気がしてきた。", "[haruki] 採用 約129人。エントリーは2万8,700人超。", "[nana] 200倍超…", "[haruki] うん。普通の意気込みじゃ届かない。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_08.png', 'haruki', '[haruki] (OBに) 文系でも、海外で事業を作れるんですか?
[OB先輩] 文系91名、理系38名。むしろ文系の方が多いよ。
[OB先輩] うちは『ひとりの商人、無数の使命』。出自じゃなくて、何を担うかで動く。
[nana] それなら…私が立てる土俵に、ある。', '土俵は、ある。', NULL, NULL, '["[haruki] (OBに) 文系でも、海外で事業を作れるんですか?", "[OB先輩] 文系91名、理系38名。むしろ文系の方が多いよ。", "[OB先輩] うちは『ひとりの商人、無数の使命』。出自じゃなくて、何を担うかで動く。", "[nana] それなら…私が立てる土俵に、ある。"]', 'H7: 伊藤忠商事東京本社の光庭(自然光が降り注ぐ吹き抜けの中庭、植栽と上階回廊)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_09.png', 'haruki', '[nana] もし入れたら、何ができるの?
[haruki] 例えば3つ。東京でファミマの事業経営。
[haruki] ミラノで繊維のグローバルブランドを企画。
[haruki] シンガポールで食料・エネルギーのトレード。
[nana] 3つとも、全然違う未来。', '未来は、3つどころじゃない。', NULL, NULL, '["[nana] もし入れたら、何ができるの?", "[haruki] 例えば3つ。東京でファミマの事業経営。", "[haruki] ミラノで繊維のグローバルブランドを企画。", "[haruki] シンガポールで食料・エネルギーのトレード。", "[nana] 3つとも、全然違う未来。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@7cfd454/public/images/itochu/panel_10.png', 'both', '[haruki] 三方よし — 売り手よし、買い手よし、世間よし。1872年から変わらない、初代伊藤忠兵衛の指針。
[nana] 129人の枠に、私たちも挑む。
[both] 必要なのは、ひとりの商人としての、芯と、使命感。', '129名の枠に、私たちも挑む。', 'ひとりの商人、無数の使命。', NULL, '["[haruki] 三方よし — 売り手よし、買い手よし、世間よし。1872年から変わらない、初代伊藤忠兵衛の指針。", "[nana] 129人の枠に、私たちも挑む。", "[both] 必要なのは、ひとりの商人としての、芯と、使命感。"]', 'H4: 鳥居の傍らに「三方よし」と刻まれた近江商人モチーフの石碑', '{"location": "参道の鳥居の手前、向かって右側の石畳の脇", "object_type": "自然石を加工した石碑(近江商人モチーフ、人の腰の高さ)", "brand_form": "石碑の正面に『三方よし』の3文字が大きく刻まれ、その下に小さく『売り手よし 買い手よし 世間よし』と刻まれている。近江商人の天秤棒モチーフが石の側面に控えめに彫られている", "attachment": "参道の石畳に基礎ごと埋め込まれ、地面と一体化している。長年の風雨で角が少し丸まった自然な質感", "scale_note": "実在の神社の境内にある由来碑と同じ控えめサイズ。人の腰〜胸の高さ。参道の主役は鳥居であり、石碑はあくまで脇役"}');
