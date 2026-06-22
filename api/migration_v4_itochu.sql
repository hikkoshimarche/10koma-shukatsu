-- ===== itochu (伊藤忠商事株式会社) =====
-- source: output/itochu-shoji/scenario_v4.json
-- jsDelivr ref: @2630894
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('itochu', '伊藤忠商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_01.png', 'nana', '[nana] これ、ファミマで買ったTシャツ。なんで商社の話で出てくるの?
[haruki] そのTシャツ、誰が企画してるか知ってる?
[nana] え、ファミマが自分で作ってるんじゃないの?
[haruki] 実は、ファミマで売ってる『Convenience Wear』は、伊藤忠の繊維カンパニーが企画してるんだ。', 'コンビニのTシャツ、誰が企画?', '伊藤忠商事 / 8001', NULL, '["[nana] これ、ファミマで買ったTシャツ。なんで商社の話で出てくるの?", "[haruki] そのTシャツ、誰が企画してるか知ってる?", "[nana] え、ファミマが自分で作ってるんじゃないの?", "[haruki] 実は、ファミマで売ってる『Convenience Wear』は、伊藤忠の繊維カンパニーが企画してるんだ。"]', 'H3: Convenience Wear (ファミマ店内のアパレル売り場)', '{"location": "商品棚のヘッダーまたは商品タグ", "object_type": "PB ブランドサイン", "brand_form": "『Convenience Wear』のロゴ (シンプルなセリフ体)、棚ヘッダーに控えめに表示", "attachment": "棚に取り付けられたブランドヘッダー", "scale_note": "実在のファミマ店舗の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_02.png', 'haruki', '[haruki] 2020年、ファミマは伊藤忠の完全子会社化。
[nana] 完全って?
[haruki] 株式100%。上場廃止して、伊藤忠の中に。Convenience Wearはその3年後、繊維カンパニーが企画して売上3年で4倍。
[nana] コンビニで服が売れるって発想、商社が出してたんだ…', 'ファミマは伊藤忠の100%子会社', 'Convenience Wear 3年で売上4倍', '公式 / 日経ビジネス', '["[haruki] 2020年、ファミマは伊藤忠の完全子会社化。", "[nana] 完全って?", "[haruki] 株式100%。上場廃止して、伊藤忠の中に。Convenience Wearはその3年後、繊維カンパニーが企画して売上3年で4倍。", "[nana] コンビニで服が売れるって発想、商社が出してたんだ…"]', 'H2: ファミリーマート店舗ファサード', '{"location": "店舗ファサード上部", "object_type": "店舗サイン (FamilyMart 看板)", "brand_form": "緑と白のFamilyMart 看板、実在のロゴデザイン", "attachment": "店舗外壁に固定された看板", "scale_note": "実在のコンビニ店舗の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_03.png', 'haruki', '[haruki] 1858年、初代伊藤忠兵衛が呉服商として創業。15歳で行商を始めた近江商人。
[nana] 呉服…つまり繊維。Tシャツのご先祖、ってこと?
[haruki] そう。座右の銘:『商売は菩薩の業、売り買い何れをも益し、世の不足をうずめる』。
[nana] 150年前から、商売を『人を益する仕事』って捉えてた…', '1858年、呉服商から始まる', '初代伊藤忠兵衛 / 近江商人 / 商売は菩薩の業', NULL, '["[haruki] 1858年、初代伊藤忠兵衛が呉服商として創業。15歳で行商を始めた近江商人。", "[nana] 呉服…つまり繊維。Tシャツのご先祖、ってこと?", "[haruki] そう。座右の銘:『商売は菩薩の業、売り買い何れをも益し、世の不足をうずめる』。", "[nana] 150年前から、商売を『人を益する仕事』って捉えてた…"]', 'H5: 初代伊藤忠兵衛の銅像 (または座右の銘の書)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_04.png', 'haruki', '[haruki] 伊藤忠の繊維カンパニーは業界リーダー。原料→アパレル→小売まで一気通貫。
[nana] 原料って、綿花とか?
[haruki] そう。綿花を中央アジア・米国・豪州から買い付け、中国・ベトナムで縫製、日本のファミマで売る。
[nana] 1枚のTシャツが、世界5カ国を回って、私の手元に来てるんだ…', '綿花→反物→Tシャツ→ファミマ', '原料〜アパレル〜小売まで一気通貫', NULL, '["[haruki] 伊藤忠の繊維カンパニーは業界リーダー。原料→アパレル→小売まで一気通貫。", "[nana] 原料って、綿花とか?", "[haruki] そう。綿花を中央アジア・米国・豪州から買い付け、中国・ベトナムで縫製、日本のファミマで売る。", "[nana] 1枚のTシャツが、世界5カ国を回って、私の手元に来てるんだ…"]', 'H6: 繊維倉庫の反物・アパレル工場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_05.png', 'nana', '[nana] 伊藤忠の年収って、どんな構造なの?
[haruki] 有価証券報告書(単体)によると平均1,805万円(42.2歳)。でも額より構造が大事。
[haruki] ベース+海外駐在手当+各カンパニーの業績連動。自分の担当事業が伸びれば、賞与に反映する。
[nana] 自分が動かした事業の結果が、年収に返ってくるんだ。', '平均1,805万円(有価証券報告書・単体)+業績連動', 'ベース / 海外駐在手当 / 各事業の業績連動', '日経会社情報 8001 / 有報', '["[nana] 伊藤忠の年収って、どんな構造なの?", "[haruki] 有価証券報告書(単体)によると平均1,805万円(42.2歳)。でも額より構造が大事。", "[haruki] ベース+海外駐在手当+各カンパニーの業績連動。自分の担当事業が伸びれば、賞与に反映する。", "[nana] 自分が動かした事業の結果が、年収に返ってくるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_06.png', 'haruki', '[haruki] 青山本社、1980年竣工。マホガニー・レッドの外装は45年変わってない。
[nana] 街に馴染んでる感じ…
[haruki] 2026年8月、45年使った青山の本社をいったん離れる。そしていずれ、同じ青山に新しい本社を建て替えるんだ。
[nana] 建物も人も、続いて、変わる。', '青山45年、そして次へ', '1980年竣工 / 雁行配置 / マホガニー・レッド', NULL, '["[haruki] 青山本社、1980年竣工。マホガニー・レッドの外装は45年変わってない。", "[nana] 街に馴染んでる感じ…", "[haruki] 2026年8月、45年使った青山の本社をいったん離れる。そしていずれ、同じ青山に新しい本社を建て替えるんだ。", "[nana] 建物も人も、続いて、変わる。"]', 'H1: 北青山の伊藤忠商事東京本社ビル', '{"location": "本社ビル上部の外壁", "object_type": "建築サイン (ITOCHU)", "brand_form": "ビル上部にレリーフ調の『ITOCHU』サイン、控えめに", "attachment": "ビル外壁の建築サインとして固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_07.png', 'nana', '[nana] 配属って、自分が希望した部署に行けるんですか？
[OB先輩] 8カンパニーあって、第一希望そのまま通る人は半分くらい。繊維志望が金属に行くことも普通にある。
[OB先輩] でも、3〜5年で海外駐在に出る人が多い。ファミマの海外展開も、商社マンが現地で立ち上げる。
[haruki] 希望と違う配属でも、別の現場が見える、ってことか…', '8カンパニー、希望通り半分', '繊維志望→金属も普通 / 3〜5年で海外駐在', NULL, '["[nana] 配属って、自分が希望した部署に行けるんですか？", "[OB先輩] 8カンパニーあって、第一希望そのまま通る人は半分くらい。繊維志望が金属に行くことも普通にある。", "[OB先輩] でも、3〜5年で海外駐在に出る人が多い。ファミマの海外展開も、商社マンが現地で立ち上げる。", "[haruki] 希望と違う配属でも、別の現場が見える、ってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_08.png', 'haruki', '[haruki] 2020年4月、全社員参加で理念を改訂。満場一致で『三方よし』に。
[nana] 売り手よし、買い手よし、世間よし…
[haruki] 近江商人150年の『商売は菩薩の業』を、現代の言葉で言い直したもの。
[nana] ファミマも、Convenience Wearも、三方よしの中に入ってるんだ。', '売り手よし、買い手よし、世間よし', '2020年4月改訂 / 全社員参加で満場一致', NULL, '["[haruki] 2020年4月、全社員参加で理念を改訂。満場一致で『三方よし』に。", "[nana] 売り手よし、買い手よし、世間よし…", "[haruki] 近江商人150年の『商売は菩薩の業』を、現代の言葉で言い直したもの。", "[nana] ファミマも、Convenience Wearも、三方よしの中に入ってるんだ。"]', 'H4: 三方よしの額・近江商人の暖簾', '{"location": "壁面中央", "object_type": "理念の額", "brand_form": "『売り手よし / 買い手よし / 世間よし』が縦書きで書かれた書、木製の額装", "attachment": "壁面に固定された額", "scale_note": "実在の社内額の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_09.png', 'nana', '[OB先輩] 伊藤忠が見るのは、『ひとりの商人、無数の使命』。目立つ経験ではなく、ひとりの商人として活躍できるか。
[OB先輩] 一人ひとりが、自分で使命を見つけて動けるか。
[nana] 上から指示される会社じゃないんだ…
[haruki] 150年前の近江商人と、今の私たちが、同じ姿勢で立ってる、ってこと。', 'ひとりの商人、無数の使命', '倍率じゃない、自分で使命を持てる人', NULL, '["[OB先輩] 伊藤忠が見るのは、『ひとりの商人、無数の使命』。目立つ経験ではなく、ひとりの商人として活躍できるか。", "[OB先輩] 一人ひとりが、自分で使命を見つけて動けるか。", "[nana] 上から指示される会社じゃないんだ…", "[haruki] 150年前の近江商人と、今の私たちが、同じ姿勢で立ってる、ってこと。"]', 'H7: 本社の光庭 (吹き抜けの自然光)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('itochu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2630894/public/images/itochu/panel_10.png', 'both', '[haruki] 売上14.7兆円、純利益8,803億円(過去最高)、採用129名。
[nana] 見かけの数字じゃなくて、世界のどんな商売を私が動かすかが大事、ってことだね。
[both] 売り手よし、買い手よし、世間よし — 150年前の近江から、世界へ。', '150年前の近江から、世界へ。', '売上14.7兆円 / 純利益8,803億円(過去最高) / 採用129名', NULL, '["[haruki] 売上14.7兆円、純利益8,803億円(過去最高)、採用129名。", "[nana] 見かけの数字じゃなくて、世界のどんな商売を私が動かすかが大事、ってことだね。", "[both] 売り手よし、買い手よし、世間よし — 150年前の近江から、世界へ。"]', 'H6: 繊維倉庫の反物 (締めの象徴)', NULL);
