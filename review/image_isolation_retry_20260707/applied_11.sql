-- ===== aeon (イオン株式会社) =====
-- source: output/aeon/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('aeon', 'イオン株式会社', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_01.png', 'nana', '[nana] 毎月20日のあの黄色い看板、覚えてる?
[haruki] お客さま感謝デー、5%オフのやつ。
[nana] 小学生の頃、母に連れられて来たなあ…
[haruki] その看板の裏側に、10兆円企業と300社超のグループがある。', '毎月20日の黄色い看板、覚えてる?', 'イオン / 8267 / 10兆円の身近な原点', NULL, '["[nana] 毎月20日のあの黄色い看板、覚えてる?", "[haruki] お客さま感謝デー、5%オフのやつ。", "[nana] 小学生の頃、母に連れられて来たなあ…", "[haruki] その看板の裏側に、10兆円企業と300社超のグループがある。"]', 'H5: お客さま感謝デー看板', '{"location": "店内エントランス上部", "object_type": "お客さま感謝デー看板", "brand_form": "黄色地に赤文字で『毎月20日・30日 お客さま感謝デー 5%OFF』の大型横断幕", "attachment": "天井から吊り下げ", "scale_note": "実在店舗の通常サイズ、横幅3〜4m"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_02.png', 'haruki', '[haruki] 営業収益10兆1,348億円。日本最大級の流通グループだよ。
[nana] 10兆円!? スーパーだけじゃないの?
[haruki] イオンは純粋持株会社。小売・金融・ディベロッパー・サービス、グループ300社超を束ねてる。
[nana] 週末に来てたモール、そんな巨大な仕組みの一部だったんだ…', '営業収益10兆1,348億円', 'グループ300社超 / 従業員約62万人', '2025年2月期決算', '["[haruki] 営業収益10兆1,348億円。日本最大級の流通グループだよ。", "[nana] 10兆円!? スーパーだけじゃないの?", "[haruki] イオンは純粋持株会社。小売・金融・ディベロッパー・サービス、グループ300社超を束ねてる。", "[nana] 週末に来てたモール、そんな巨大な仕組みの一部だったんだ…"]', 'H2: イオンモール外観', '{"location": "建物上部ファサード", "object_type": "イオンモールロゴ", "brand_form": "建物正面上部に『AEON MALL』の大型文字サイン、白地に青", "attachment": "建物外壁に固定", "scale_note": "実在モールの通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_03.png', 'nana', '[nana] このトップバリュって、イオンが作ってるの?
[haruki] そう、プライベートブランド。企画・開発・品質管理まで自社でやってる。
[nana] いつも何気なく買ってたけど、メーカーじゃなくて流通が作ってたんだ…
[haruki] メーカー機能も持つ。それがイオンの強み。', 'トップバリュ、イオンの自社開発', 'PB商品 / 企画・品質管理まで一貫', NULL, '["[nana] このトップバリュって、イオンが作ってるの?", "[haruki] そう、プライベートブランド。企画・開発・品質管理まで自社でやってる。", "[nana] いつも何気なく買ってたけど、メーカーじゃなくて流通が作ってたんだ…", "[haruki] メーカー機能も持つ。それがイオンの強み。"]', 'H3: トップバリュ商品パッケージ', '{"location": "中央の商品パッケージ", "object_type": "トップバリュロゴ", "brand_form": "青と白を基調としたシンプルなデザイン、『TOPVALU』ロゴ", "attachment": "商品パッケージに印刷", "scale_note": "実在商品の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_04.png', 'nana', '[nana] WAON、便利だよね。これもイオン?
[haruki] そう。電子マネーWAON、イオン銀行、イオンカード。金融事業も大きい。
[nana] 買い物して、決済して、銀行も使って…全部イオンの中だった。
[haruki] 小売だけじゃない。生活インフラ全体を設計してる会社。', 'WAON・イオン銀行・イオンカード', '金融事業もグループ / 生活インフラを一貫設計', NULL, '["[nana] WAON、便利だよね。これもイオン?", "[haruki] そう。電子マネーWAON、イオン銀行、イオンカード。金融事業も大きい。", "[nana] 買い物して、決済して、銀行も使って…全部イオンの中だった。", "[haruki] 小売だけじゃない。生活インフラ全体を設計してる会社。"]', 'H4: WAON電子マネー端末', '{"location": "レジカウンター上", "object_type": "WAON端末", "brand_form": "ピンク色の犬のキャラクター付き、『WAON』ロゴの電子マネー決済端末", "attachment": "レジカウンターに設置", "scale_note": "実在端末の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_05.png', 'nana', '[nana] 平均年収947万円って、どういう構造?
[haruki] これは純粋持株会社イオン株式会社の数字。平均年齢49.1歳、管理職中心。
[haruki] 実際の採用はグループ各社。イオンリテールやイオンモールは初任給も給与体系も別。
[nana] 持株会社だから、947万円は現場の初任給じゃないんだ…', '947万円=持株会社管理職の平均', '採用はグループ各社 / 初任給は子会社ごと', '2025年2月期・平均年齢49.1歳', '["[nana] 平均年収947万円って、どういう構造?", "[haruki] これは純粋持株会社イオン株式会社の数字。平均年齢49.1歳、管理職中心。", "[haruki] 実際の採用はグループ各社。イオンリテールやイオンモールは初任給も給与体系も別。", "[nana] 持株会社だから、947万円は現場の初任給じゃないんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_06.png', 'haruki', '[haruki] イオン株式会社は純粋持株会社で、直接の新卒採用はほぼない。
[haruki] グループ各社が個別採用して、数年後に持株会社へ出向、っていうキャリアが多い。
[nana] じゃあ最初は、イオンリテールやイオンモールに配属されるんだ?
[haruki] そう。現場で経験を積んで、グループ全体を見る立場に上がっていく。', '持株会社への出向は数年後', '最初はグループ各社 / 現場経験が前提', NULL, '["[haruki] イオン株式会社は純粋持株会社で、直接の新卒採用はほぼない。", "[haruki] グループ各社が個別採用して、数年後に持株会社へ出向、っていうキャリアが多い。", "[nana] じゃあ最初は、イオンリテールやイオンモールに配属されるんだ?", "[haruki] そう。現場で経験を積んで、グループ全体を見る立場に上がっていく。"]', 'H1: イオンタワー本社', '{"location": "タワー上部外壁", "object_type": "イオンロゴサイン", "brand_form": "『AEON』のロゴ、青地に白文字、控えめな位置", "attachment": "ビル外壁に固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_07.png', 'nana', '[OB社員] イオンの理念は『お客さまを原点に平和を追求し、人間を尊重し、地域社会に貢献する』。
[OB社員] 求めるのは、自ら課題を発見し、周囲を巻き込んで解決できる人。自立心が全て。
[nana] (静かに) お客さまを原点に、か…
[haruki] 倍率じゃなくて、理念に共感できるか。それがイオンの入口。', 'お客さまを原点に、自立心を問う', '理念共感 / 課題発見力 / 周囲を巻き込む力', NULL, '["[OB社員] イオンの理念は『お客さまを原点に平和を追求し、人間を尊重し、地域社会に貢献する』。", "[OB社員] 求めるのは、自ら課題を発見し、周囲を巻き込んで解決できる人。自立心が全て。", "[nana] (静かに) お客さまを原点に、か…", "[haruki] 倍率じゃなくて、理念に共感できるか。それがイオンの入口。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_08.png', 'haruki', '[haruki] 1758年、三重県四日市で岡田惣左衛門が呉服太物商を始めた。
[nana] 江戸時代!? 260年以上前…
[haruki] 家訓は『大黒柱に車をつけよ』。時代に合わせて変わり続けろ、という意味。
[nana] 呉服屋が、今の10兆円流通グループになったんだ…', '1758年、岡田屋呉服店から', '家訓『大黒柱に車をつけよ』/ 260年の変革', NULL, '["[haruki] 1758年、三重県四日市で岡田惣左衛門が呉服太物商を始めた。", "[nana] 江戸時代!? 260年以上前…", "[haruki] 家訓は『大黒柱に車をつけよ』。時代に合わせて変わり続けろ、という意味。", "[nana] 呉服屋が、今の10兆円流通グループになったんだ…"]', 'H6: 岡田屋呉服店の歴史的写真', '{"location": "壁面中央", "object_type": "岡田屋呉服店の歴史的写真", "brand_form": "セピア色の古写真、江戸時代の街道沿いの小さな呉服商", "attachment": "額装して壁に掛ける", "scale_note": "A3サイズ程度の額"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_09.png', 'haruki', '[nana] もしイオングループに入ったら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。ベトナムの新規モール開発で地域ニーズをリサーチ。
[haruki] トップバリュの新商品開発で、メーカーと品質基準を詰める会議。
[haruki] 地元の祭りとコラボして、地域の絆を深めるイベントを企画。
[nana] どれも、お客さまを原点に、地域を創ってる。', '10年後、たとえばこんな場面', 'ベトナム / 商品開発 / 地域イベント企画', NULL, '["[nana] もしイオングループに入ったら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。ベトナムの新規モール開発で地域ニーズをリサーチ。", "[haruki] トップバリュの新商品開発で、メーカーと品質基準を詰める会議。", "[haruki] 地元の祭りとコラボして、地域の絆を深めるイベントを企画。", "[nana] どれも、お客さまを原点に、地域を創ってる。"]', 'H2: イオンモール外観 (再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('aeon', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/aeon/panel_10.png', 'both', '[haruki] 営業収益10兆1,348億円、グループ300社超、採用301名以上。
[nana] 毎月20日の黄色い看板、その裏側にこんな世界があったんだ。
[both] 1758年から、あなたの隣へ。イオン、お客さまを原点に。', '1758年から、あなたの隣へ。', '営業収益10兆1,348億円 / グループ300社超 / 採用301名以上', NULL, '["[haruki] 営業収益10兆1,348億円、グループ300社超、採用301名以上。", "[nana] 毎月20日の黄色い看板、その裏側にこんな世界があったんだ。", "[both] 1758年から、あなたの隣へ。イオン、お客さまを原点に。"]', 'H5: お客さま感謝デー看板 (朝の光)', '{"location": "店内エントランス上部", "object_type": "お客さま感謝デー看板", "brand_form": "黄色地に赤文字で『毎月20日・30日 お客さま感謝デー』", "attachment": "天井から吊り下げ", "scale_note": "実在店舗の通常サイズ"}');

-- ===== cosmos-pharma (株式会社コスモス薬品) =====
-- source: output/cosmos-pharma/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('cosmos-pharma', '株式会社コスモス薬品', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_01.png', 'haruki', '[haruki] コスモス薬品、売上高1兆113億円。
[nana] 1兆円!? ドラッグストアでそんなに?
[haruki] しかもM&A一切なし。自社出店だけで達成した異例のケース。
[nana] 買収なしで1兆円って、どうやって…', 'M&Aなしで1兆円', 'コスモス薬品 / 3349 / 自社出店のみ', NULL, '["[haruki] コスモス薬品、売上高1兆113億円。", "[nana] 1兆円!? ドラッグストアでそんなに?", "[haruki] しかもM&A一切なし。自社出店だけで達成した異例のケース。", "[nana] 買収なしで1兆円って、どうやって…"]', 'H2: 郊外型2000㎡メガストア', '{"location": "店舗正面上部", "object_type": "店舗看板（ドラッグストアコスモス）", "brand_form": "オレンジと白のコスモス薬品ロゴ看板、横に長い大型サイン", "attachment": "店舗外壁に固定", "scale_note": "実在店舗と同じ大型看板"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_02.png', 'haruki', '[haruki] 2025年5月期、新規出店120店。1年で120店だよ。
[nana] 120店!? 3日に1店ペース…
[haruki] 全国1,609店舗。九州から始めて、関東・中部・関西まで広がってる。
[nana] このスピードで、どうやって品質保つの…', '年間120店出店', '全国1,609店舗 / 3日に1店ペース', '公式IR 2025年5月期', '["[haruki] 2025年5月期、新規出店120店。1年で120店だよ。", "[nana] 120店!? 3日に1店ペース…", "[haruki] 全国1,609店舗。九州から始めて、関東・中部・関西まで広がってる。", "[nana] このスピードで、どうやって品質保つの…"]', 'H6: 店内陳列フォーマット', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_03.png', 'nana', '[nana] でもこんな田舎に、こんな大きい店…
[haruki] それがコスモスの戦略。人口8000人の小商圏に2000㎡の大型店を出す。
[nana] 8000人!? 普通は出店しないエリアじゃ…
[haruki] 競合が来ない場所で圧倒的シェアを取る。だから年間120店出せる。', '人口8000人に2000㎡メガストア', '小商圏・大型店・独占シェア戦略', NULL, '["[nana] でもこんな田舎に、こんな大きい店…", "[haruki] それがコスモスの戦略。人口8000人の小商圏に2000㎡の大型店を出す。", "[nana] 8000人!? 普通は出店しないエリアじゃ…", "[haruki] 競合が来ない場所で圧倒的シェアを取る。だから年間120店出せる。"]', 'H2: 郊外型2000㎡メガストア', '{"location": "店舗正面上部", "object_type": "店舗看板（ドラッグストアコスモス）", "brand_form": "オレンジと白のロゴ看板", "attachment": "店舗外壁に固定", "scale_note": "実在店舗と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_04.png', 'nana', '[nana] あれ、ポイントカードないの?
[haruki] コスモスはポイント還元を廃止してる。その分、毎日低価格。EDLP戦略。
[nana] ポイント貯めるより、毎日安い方がいい…
[haruki] 一般食品61%、医薬品14%、化粧品9%。日常全部を毎日安く。', 'ポイント廃止、毎日低価格', 'EDLP戦略 / 一般食品61%', '公式IR・Yahoo!ファイナンス', '["[nana] あれ、ポイントカードないの?", "[haruki] コスモスはポイント還元を廃止してる。その分、毎日低価格。EDLP戦略。", "[nana] ポイント貯めるより、毎日安い方がいい…", "[haruki] 一般食品61%、医薬品14%、化粧品9%。日常全部を毎日安く。"]', 'H3: EDLP価格タグ', '{"location": "商品棚の価格表示部分", "object_type": "EDLP価格タグ", "brand_form": "オレンジ色の統一価格表示タグ、毎日低価格の文字", "attachment": "商品棚に取り付け", "scale_note": "実店舗と同じ小型タグ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_05.png', 'nana', '[nana] 平均年収488.7万円。小売にしては…
[haruki] 平均年齢31.1歳、平均勤続6.8年。若い組織。
[haruki] コスモスは利益を価格に還元する。年収より、顧客に返す構造。
[nana] EDLP戦略って、社員の給与にも表れてるんだ…', '488.7万円 = 顧客還元構造', '平均年齢31.1歳 / 平均勤続6.8年', '日経会社情報 3349', '["[nana] 平均年収488.7万円。小売にしては…", "[haruki] 平均年齢31.1歳、平均勤続6.8年。若い組織。", "[haruki] コスモスは利益を価格に還元する。年収より、顧客に返す構造。", "[nana] EDLP戦略って、社員の給与にも表れてるんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_06.png', 'nana', '[OB先輩] 総合職は店舗配属からスタート。年間120店出店だから、転勤は頻繁。
[OB先輩] 登録販売者の資格を取って、医薬品の相談対応もする。
[OB先輩] 九州・中国・四国・関西・中部・関東、全国が対象エリア。家族との時間は工夫が必要。
[nana] 出店ペースが速いから、異動も速い…', '年間120店出店 = 転勤頻繁', '店舗配属スタート / 登録販売者資格 / 全国転勤', NULL, '["[OB先輩] 総合職は店舗配属からスタート。年間120店出店だから、転勤は頻繁。", "[OB先輩] 登録販売者の資格を取って、医薬品の相談対応もする。", "[OB先輩] 九州・中国・四国・関西・中部・関東、全国が対象エリア。家族との時間は工夫が必要。", "[nana] 出店ペースが速いから、異動も速い…"]', 'H4: 登録販売者スタッフ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_07.png', 'nana', '[OB先輩] コスモスの採用基準は、まじめで一生懸命かどうか。それだけ。
[OB先輩] 社是は『純情』。人の役に立ちたい、喜んでもらいたいという想いを見る。
[nana] 数字じゃなくて、人を見てるんだ…
[haruki] EDLP戦略も、120店出店も、全部『まじめで一生懸命』から始まってる。', 'まじめで一生懸命、純情', '採用基準 / 社是 / 人の役に立ちたい想い', NULL, '["[OB先輩] コスモスの採用基準は、まじめで一生懸命かどうか。それだけ。", "[OB先輩] 社是は『純情』。人の役に立ちたい、喜んでもらいたいという想いを見る。", "[nana] 数字じゃなくて、人を見てるんだ…", "[haruki] EDLP戦略も、120店出店も、全部『まじめで一生懸命』から始まってる。"]', 'H1: JR博多駅東NSビルS館本社', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_08.png', 'nana', '[nana] 年間120店、どうやって商品を届けてるの?
[haruki] 広川町に自社所有の物流センター。2006年開設。
[haruki] M&Aなしで1兆円達成できたのは、自社物流を徹底してるから。
[nana] 出店も、物流も、価格も、全部自分たちで…', '自社物流で年間120店を支える', '広川町物流センター / 2006年開設 / 自社所有', NULL, '["[nana] 年間120店、どうやって商品を届けてるの?", "[haruki] 広川町に自社所有の物流センター。2006年開設。", "[haruki] M&Aなしで1兆円達成できたのは、自社物流を徹底してるから。", "[nana] 出店も、物流も、価格も、全部自分たちで…"]', 'H5: 広川町物流センター', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいるかな…
[haruki] たとえば、こんな未来。関東エリアで年間30店の新規出店を統括。
[haruki] 広川町物流センターで、全国1,800店への配送最適化を設計。
[haruki] 本社で、人口6000人の超小商圏への出店戦略を立案。
[nana] 毎日低価格を、毎日出店で届け続ける。', '10年後、たとえばこんな場面', '関東エリア統括 / 物流最適化 / 超小商圏戦略', NULL, '["[nana] もし入れたら、10年後どこにいるかな…", "[haruki] たとえば、こんな未来。関東エリアで年間30店の新規出店を統括。", "[haruki] 広川町物流センターで、全国1,800店への配送最適化を設計。", "[haruki] 本社で、人口6000人の超小商圏への出店戦略を立案。", "[nana] 毎日低価格を、毎日出店で届け続ける。"]', 'H2: 郊外型2000㎡メガストア', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('cosmos-pharma', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/cosmos-pharma/panel_10.png', 'both', '[haruki] 売上1兆113億円、営業利益404億円、店舗1,609。
[nana] M&Aなし、自社出店のみ。まじめで一生懸命、純情。
[both] 毎日低価格、毎日出店。コスモス薬品、1兆円の誠実。', '毎日低価格、毎日出店。', '売上1兆113億円 / 営業利益404億円 / 店舗1,609', NULL, '["[haruki] 売上1兆113億円、営業利益404億円、店舗1,609。", "[nana] M&Aなし、自社出店のみ。まじめで一生懸命、純情。", "[both] 毎日低価格、毎日出店。コスモス薬品、1兆円の誠実。"]', 'H2: 郊外型2000㎡メガストア', '{"location": "店舗正面上部", "object_type": "店舗看板（ドラッグストアコスモス）", "brand_form": "オレンジと白のロゴ看板、夕日に照らされる", "attachment": "店舗外壁に固定", "scale_note": "実在店舗と同じサイズ"}');

-- ===== daito-kentaku (大東建託株式会社) =====
-- source: output/daito-kentaku/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('daito-kentaku', '大東建託株式会社', 'real_estate', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_01.png', 'nana', '[nana] いい部屋ネット、知ってる。賃貸の仲介でしょ?
[haruki] そう。でもこの看板の裏、売上1兆9,847億円。
[nana] え、1.9兆円!? 仲介だけで?
[haruki] 仲介だけじゃない。ここから、もっと大きい話が始まる。', 'いい部屋ネット、売上1.9兆円', '大東建託 / 1878 / 身近な看板の裏側', NULL, '["[nana] いい部屋ネット、知ってる。賃貸の仲介でしょ?", "[haruki] そう。でもこの看板の裏、売上1兆9,847億円。", "[nana] え、1.9兆円!? 仲介だけで?", "[haruki] 仲介だけじゃない。ここから、もっと大きい話が始まる。"]', 'H2: いい部屋ネット店舗', '{"location": "店舗上部の看板", "object_type": "いい部屋ネットロゴ看板", "brand_form": "青地に白文字で『いい部屋ネット』のロゴ看板、LED照明付き", "attachment": "店舗ファサード上部に固定", "scale_note": "実在の店舗看板と同じ横に長い比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_02.png', 'haruki', '[haruki] 大東建託の本業は、『賃貸経営受託』。
[nana] 賃貸経営…受託?
[haruki] 土地オーナーに『アパート建てませんか』って提案して、建築を請け負う。
[haruki] さらに、完成したアパートを35年間一括で借り上げる。オーナーは空室リスクゼロ。', '35年一括借上、空室リスクゼロ', '賃貸経営受託システム / サブリース業界トップ', NULL, '["[haruki] 大東建託の本業は、『賃貸経営受託』。", "[nana] 賃貸経営…受託?", "[haruki] 土地オーナーに『アパート建てませんか』って提案して、建築を請け負う。", "[haruki] さらに、完成したアパートを35年間一括で借り上げる。オーナーは空室リスクゼロ。"]', 'H3: 一括借上アパート外観', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_03.png', 'nana', '[nana] 35年借り上げって、すごいリスクじゃない?
[haruki] だから管理戸数126万戸超。業界トップ。
[nana] 126万戸!?
[haruki] 全国47都道府県に展開。建てて、借り上げて、管理して、仲介する。全部を一貫でやるから強い。', '管理戸数126万戸超、業界トップ', '建築→借上→管理→仲介、一貫提供', '公式IR・Wikipedia', '["[nana] 35年借り上げって、すごいリスクじゃない?", "[haruki] だから管理戸数126万戸超。業界トップ。", "[nana] 126万戸!?", "[haruki] 全国47都道府県に展開。建てて、借り上げて、管理して、仲介する。全部を一貫でやるから強い。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_04.png', 'nana', '[nana] あれ、ソフトバンクホークスの帽子に…
[haruki] 大東建託、メインスポンサー。サッカー日本代表のサポーティングカンパニーでもある。
[nana] スポーツ広告、けっこう派手にやってるんだ。
[haruki] あと、ZEH基準の賃貸住宅も日本初。2025年3月で累計12万戸超。環境配慮も最前線。', 'ホークス・日本代表スポンサー', 'ZEH賃貸12万戸超 / 環境配慮も最前線', NULL, '["[nana] あれ、ソフトバンクホークスの帽子に…", "[haruki] 大東建託、メインスポンサー。サッカー日本代表のサポーティングカンパニーでもある。", "[nana] スポーツ広告、けっこう派手にやってるんだ。", "[haruki] あと、ZEH基準の賃貸住宅も日本初。2025年3月で累計12万戸超。環境配慮も最前線。"]', 'H5: 福岡ソフトバンクホークスユニフォーム', '{"location": "選手の帽子側面", "object_type": "大東建託ワッペン", "brand_form": "帽子側面の大東建託ロゴワッペン、白地に青文字", "attachment": "帽子に縫い付け", "scale_note": "実在のユニフォームワッペンと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_05.png', 'nana', '[nana] 年収はどうなの?
[haruki] 平均837万円。これ、基本給+成果給+ストックオプション。
[nana] ストックオプション…株?
[haruki] そう。業績連動で、頑張った分がストレートに返ってくる仕組み。実力主義。', '837万円=成果給+SO', '基本給+成果給+ストックオプション / 実力主義', '有価証券報告書2024年3月期', '["[nana] 年収はどうなの?", "[haruki] 平均837万円。これ、基本給+成果給+ストックオプション。", "[nana] ストックオプション…株?", "[haruki] そう。業績連動で、頑張った分がストレートに返ってくる仕組み。実力主義。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_06.png', 'nana', '[OB社員] 新卒の8割は建築営業に配属される。土地オーナーへの提案営業。
[OB社員] 転勤は当然ある。全国47都道府県に支店があるから。
[nana] 営業、厳しそう…
[OB社員] 厳しい。でも成果が出れば、20代で年収1,000万円超も普通。頑張る人を全力で応援する社風。', '新卒8割が建築営業、転勤あり', '成果主義 / 20代で1,000万超も / 頑張る人を応援', NULL, '["[OB社員] 新卒の8割は建築営業に配属される。土地オーナーへの提案営業。", "[OB社員] 転勤は当然ある。全国47都道府県に支店があるから。", "[nana] 営業、厳しそう…", "[OB社員] 厳しい。でも成果が出れば、20代で年収1,000万円超も普通。頑張る人を全力で応援する社風。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_07.png', 'nana', '[OB社員] 大東建託が求めるのは、『成長意欲を持ち、自らが挑戦の一歩を踏み出す人』。
[OB社員] 倍率は高いけど、見てるのは数字じゃなくて、挑戦する姿勢。
[nana] 挑戦の一歩…
[haruki] グループパーパスは『託すをつなぎ、未来をひらく』。オーナーも入居者も、託してもらえる人になる仕事。', '成長意欲・挑戦の一歩', '倍率より姿勢 / 託すをつなぎ、未来をひらく', NULL, '["[OB社員] 大東建託が求めるのは、『成長意欲を持ち、自らが挑戦の一歩を踏み出す人』。", "[OB社員] 倍率は高いけど、見てるのは数字じゃなくて、挑戦する姿勢。", "[nana] 挑戦の一歩…", "[haruki] グループパーパスは『託すをつなぎ、未来をひらく』。オーナーも入居者も、託してもらえる人になる仕事。"]', NULL, '{"location": "壁面中央", "object_type": "グループパーパスパネル", "brand_form": "『託すをつなぎ、未来をひらく。』のパネル、白地に黒文字、シンプルなデザイン", "attachment": "壁面に固定", "scale_note": "実在のエントランス展示と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_08.png', 'haruki', '[haruki] 創業者は多田勝美さん。1974年、名古屋市千種区で大東産業を設立。
[nana] 1974年…50年前。
[haruki] 三重県出身、36年間オーナー経営を続けて、今の126万戸の基盤を作った。
[nana] 一人の挑戦が、1.9兆円の会社になったんだ…', '1974年名古屋、多田勝美の挑戦', '36年間オーナー経営 / 126万戸の基盤', NULL, '["[haruki] 創業者は多田勝美さん。1974年、名古屋市千種区で大東産業を設立。", "[nana] 1974年…50年前。", "[haruki] 三重県出身、36年間オーナー経営を続けて、今の126万戸の基盤を作った。", "[nana] 一人の挑戦が、1.9兆円の会社になったんだ…"]', 'H6: 創業者・多田勝美氏', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。地方都市で土地オーナーと35年契約を結ぶ営業。
[haruki] 東京本社でZEH賃貸の次世代モデルを企画する建築企画。
[haruki] 全国126万戸の管理システムを統括する管理本部。
[nana] どれも、誰かの『託す』を支える仕事。', '10年後、たとえばこんな場面', '営業 / 建築企画 / 管理本部', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。地方都市で土地オーナーと35年契約を結ぶ営業。", "[haruki] 東京本社でZEH賃貸の次世代モデルを企画する建築企画。", "[haruki] 全国126万戸の管理システムを統括する管理本部。", "[nana] どれも、誰かの『託す』を支える仕事。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('daito-kentaku', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/daito-kentaku/panel_10.png', 'both', '[haruki] 売上1.9兆円、純利益990億円、管理戸数126万戸超。
[nana] いい部屋ネットの看板の裏、こんなに大きかったんだ。
[both] 託すをつなぎ、未来をひらく。大東建託、挑戦の現在地。', '託すをつなぎ、未来をひらく。', '売上1.9兆円 / 純利益990億円 / 管理戸数126万戸超', NULL, '["[haruki] 売上1.9兆円、純利益990億円、管理戸数126万戸超。", "[nana] いい部屋ネットの看板の裏、こんなに大きかったんだ。", "[both] 託すをつなぎ、未来をひらく。大東建託、挑戦の現在地。"]', 'H1: 品川イーストワンタワー本社', NULL);

-- ===== dcm-hd (DCMホールディングス株式会社) =====
-- source: output/dcm-hd/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('dcm-hd', 'DCMホールディングス株式会社', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_01.png', 'nana', '[nana] DCMって、カーマもダイキもホーマックも全部これになったんだよね?
[haruki] そう。2022年9月に全国の店名を統一した。
[nana] 統一って、簡単じゃないよね…
[haruki] 3社が1つになって16年。DCMは統合で生まれた会社なんだ。', 'カーマもダイキもホーマックも、全部DCM', 'DCMホールディングス / 3050 / 統合で生まれた小売', NULL, '["[nana] DCMって、カーマもダイキもホーマックも全部これになったんだよね?", "[haruki] そう。2022年9月に全国の店名を統一した。", "[nana] 統一って、簡単じゃないよね…", "[haruki] 3社が1つになって16年。DCMは統合で生まれた会社なんだ。"]', 'H2: DCM統一ロゴマーク', '{"location": "店舗正面上部", "object_type": "DCM統一ロゴ看板", "brand_form": "茶色基調に青のアクセント、2022年9月導入のDCMロゴ、横に長い看板", "attachment": "店舗ファサード上部に固定", "scale_note": "実在のDCM店舗と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_02.png', 'haruki', '[haruki] 全国37都道府県に843店舗。売上5,446億円。
[nana] 843店舗!? そんなに…
[haruki] 営業利益332億円。ホームセンター業界で国内最大級の規模。
[nana] 統一したロゴの裏に、これだけの店舗があったんだ…', '全国843店舗、売上5,446億円', '37都道府県 / 営業利益332億円', '2025年2月期決算', '["[haruki] 全国37都道府県に843店舗。売上5,446億円。", "[nana] 843店舗!? そんなに…", "[haruki] 営業利益332億円。ホームセンター業界で国内最大級の規模。", "[nana] 統一したロゴの裏に、これだけの店舗があったんだ…"]', 'H4: 全国843店舗のDCM店舗網', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_03.png', 'haruki', '[haruki] 2006年、カーマ・ダイキ・ホーマックの3社が共同株式移転で統合してDCMホールディングスが誕生。
[nana] 19年前…
[haruki] 2021年に5社統合、2024年にケーヨーを吸収合併、2025年9月にエンチョーも完全子会社化。
[nana] 統合を続けて843店舗まで成長したんだ…', '2006年3社統合→2025年エンチョー統合', 'カーマ / ダイキ / ホーマック / ケーヨー / エンチョー', NULL, '["[haruki] 2006年、カーマ・ダイキ・ホーマックの3社が共同株式移転で統合してDCMホールディングスが誕生。", "[nana] 19年前…", "[haruki] 2021年に5社統合、2024年にケーヨーを吸収合併、2025年9月にエンチョーも完全子会社化。", "[nana] 統合を続けて843店舗まで成長したんだ…"]', 'H6: カーマ・ダイキ・ホーマック統合の歴史', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_04.png', 'nana', '[nana] この塗料も工具も、全部DCMブランドなんだ…
[haruki] 自社開発のプライベートブランド。壁紙、接着剤、ガーデニング用品、家電まで幅広く展開してる。
[nana] 実家のDIY、このブランドで揃えたかも…
[haruki] 843店舗で同じ品質を届ける。統合したからこそできる規模。', 'DCMブランド、生活の中に', '壁紙 / 塗料 / 工具 / ガーデニング / 自社PB', NULL, '["[nana] この塗料も工具も、全部DCMブランドなんだ…", "[haruki] 自社開発のプライベートブランド。壁紙、接着剤、ガーデニング用品、家電まで幅広く展開してる。", "[nana] 実家のDIY、このブランドで揃えたかも…", "[haruki] 843店舗で同じ品質を届ける。統合したからこそできる規模。"]', 'H3: DCMブランド商品群', '{"location": "商品パッケージ中央", "object_type": "DCMブランドロゴ", "brand_form": "塗料缶やパッケージに印刷されたDCMロゴ、茶色基調", "attachment": "商品パッケージに印刷", "scale_note": "実在のDCMブランド商品と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_05.png', 'nana', '[nana] 小売って、年収低いイメージあるけど…
[haruki] DCMは平均721万円。小売業界の中では高水準。
[haruki] 初任給は大卒エリアフリー社員で24万4千円。店舗運営の現場から本部まで、キャリアで上がる仕組み。
[nana] 小売だけど、843店舗の規模があるから構造が違うんだ…', '721万円、小売の中で高水準', '初任給24.4万円 / 店舗→本部キャリア', '有価証券報告書', '["[nana] 小売って、年収低いイメージあるけど…", "[haruki] DCMは平均721万円。小売業界の中では高水準。", "[haruki] 初任給は大卒エリアフリー社員で24万4千円。店舗運営の現場から本部まで、キャリアで上がる仕組み。", "[nana] 小売だけど、843店舗の規模があるから構造が違うんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_06.png', 'nana', '[店舗社員] 新卒はほぼ全員、店舗配属からスタート。エリアフリー社員なら全国転勤、エリア・地域社員なら限定勤務。
[店舗社員] 売場づくり、発注、在庫管理、接客まで全部やる。防災用品も季節で需要が変わるから、現場の判断が重要。
[nana] 店舗で全部学んで、本部に上がるんだ…
[haruki] 843店舗の現場を知ってるからこそ、本部で戦略が立てられる。', '新卒はほぼ全員、店舗配属から', 'エリアフリー / エリア・地域社員 / 現場→本部', NULL, '["[店舗社員] 新卒はほぼ全員、店舗配属からスタート。エリアフリー社員なら全国転勤、エリア・地域社員なら限定勤務。", "[店舗社員] 売場づくり、発注、在庫管理、接客まで全部やる。防災用品も季節で需要が変わるから、現場の判断が重要。", "[nana] 店舗で全部学んで、本部に上がるんだ…", "[haruki] 843店舗の現場を知ってるからこそ、本部で戦略が立てられる。"]', 'H5: 防災・DIY売場風景', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_07.png', 'nana', '[OB社員] DCMの社是は、社会のための奉仕、お客さまのための創造、地域のための団結。
[OB社員] 求めるのは、誰かに喜んでもらえる仕事にマインドを持てる人、ホスピタリティを持って行動できる人。
[nana] 誰かに喜んでもらえる仕事…
[haruki] 843店舗、全国37都道府県。地域の暮らしを支える、それがDCMの哲学。', '奉仕・創造・団結', '誰かに喜んでもらえる仕事 / ホスピタリティ / 地域の暮らし', NULL, '["[OB社員] DCMの社是は、社会のための奉仕、お客さまのための創造、地域のための団結。", "[OB社員] 求めるのは、誰かに喜んでもらえる仕事にマインドを持てる人、ホスピタリティを持って行動できる人。", "[nana] 誰かに喜んでもらえる仕事…", "[haruki] 843店舗、全国37都道府県。地域の暮らしを支える、それがDCMの哲学。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_08.png', 'haruki', '[haruki] DCMの強みは、M&Aで拡大し続けること。
[nana] ケーヨーもエンチョーも、統合で仲間にしてるんだよね。
[haruki] そう。2025年9月にエンチョーを完全子会社化。静岡の地盤を取り込んで、さらに広がる。
[nana] 統合するたびに、地域のくらしが繋がっていくんだ…', 'M&Aで拡大し続ける戦略', 'ケーヨー吸収合併 / 2025年9月エンチョー完全子会社化', NULL, '["[haruki] DCMの強みは、M&Aで拡大し続けること。", "[nana] ケーヨーもエンチョーも、統合で仲間にしてるんだよね。", "[haruki] そう。2025年9月にエンチョーを完全子会社化。静岡の地盤を取り込んで、さらに広がる。", "[nana] 統合するたびに、地域のくらしが繋がっていくんだ…"]', 'H1: 大森ベルポートE館本社ビル', '{"location": "本社ビル上部", "object_type": "ビルサイン", "brand_form": "DCMホールディングス のビルサイン、控えめに", "attachment": "ビル外壁に固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。静岡のDCMエンチョーで新統合店舗の立ち上げ。
[haruki] 本社の商品開発室で、次のDCMブランド商品を企画。
[haruki] 北海道のDCMで、地域に根ざした防災売場づくり。
[nana] 統合で生まれた843店舗、それぞれの地域で、新しいくらしをつくる仕事。', '10年後、たとえばこんな場面', '静岡 / 本社 / 北海道 / 地域のくらしをつくる', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。静岡のDCMエンチョーで新統合店舗の立ち上げ。", "[haruki] 本社の商品開発室で、次のDCMブランド商品を企画。", "[haruki] 北海道のDCMで、地域に根ざした防災売場づくり。", "[nana] 統合で生まれた843店舗、それぞれの地域で、新しいくらしをつくる仕事。"]', 'H4: 全国843店舗のDCM店舗網 (再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('dcm-hd', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/dcm-hd/panel_10.png', 'both', '[haruki] 全国843店舗、売上5,446億円、採用114名。
[nana] カーマもダイキもホーマックも、1つになって生まれた会社。
[both] 統合で生まれる、新しいくらし。DCMホールディングス、地域と共に成長する小売。', '統合で生まれる、新しいくらし', '売上5,446億円 / 843店舗 / 採用114名', NULL, '["[haruki] 全国843店舗、売上5,446億円、採用114名。", "[nana] カーマもダイキもホーマックも、1つになって生まれた会社。", "[both] 統合で生まれる、新しいくらし。DCMホールディングス、地域と共に成長する小売。"]', 'H2: DCM統一ロゴマーク (朝の光)', '{"location": "店舗正面上部", "object_type": "DCM統一ロゴ看板", "brand_form": "茶色基調に青のアクセント、朝日に照らされて輝く", "attachment": "店舗ファサード上部に固定", "scale_note": "実在のDCM店舗と同じ比率"}');

-- ===== kobayashi-pharma (小林製薬株式会社) =====
-- source: output/kobayashi-pharma/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('kobayashi-pharma', '小林製薬株式会社', 'consumer_goods', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_01.png', 'nana', '[nana] トイレの青い水、あれ小林製薬だって知ってた?
[haruki] え、知らなかった。
[nana] ブルーレットって商品。1969年発売で、日本初の水洗トイレ用芳香洗浄剤。
[haruki] 毎日見てるのに、メーカー意識したことなかった…', 'トイレの青い水、小林製薬だった', 'ブルーレット / 1969年発売 / 日本初の水洗トイレ用芳香洗浄剤', NULL, '["[nana] トイレの青い水、あれ小林製薬だって知ってた?", "[haruki] え、知らなかった。", "[nana] ブルーレットって商品。1969年発売で、日本初の水洗トイレ用芳香洗浄剤。", "[haruki] 毎日見てるのに、メーカー意識したことなかった…"]', 'H2: ブルーレット（青い水）', '{"location": "トイレタンク上部", "object_type": "ブルーレット本体", "brand_form": "青い容器に『ブルーレット』のロゴ、実在の製品形状", "attachment": "タンク内に設置", "scale_note": "実在のブルーレットと同じサイズ（約10cm四方）"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_02.png', 'haruki', '[haruki] 熱さまシートも小林製薬。
[nana] え、これも!?
[haruki] しかも海外でも展開されてる主力商品。OTC医薬品って、医師の処方なしで買える市販薬のこと。
[nana] トイレと発熱、全然違う困りごとなのに、両方カタチにしてる…', '熱さまシートも小林製薬', 'OTC医薬品 / 海外展開 / 主力商品', '公式サイト・ファクトシート', '["[haruki] 熱さまシートも小林製薬。", "[nana] え、これも!?", "[haruki] しかも海外でも展開されてる主力商品。OTC医薬品って、医師の処方なしで買える市販薬のこと。", "[nana] トイレと発熱、全然違う困りごとなのに、両方カタチにしてる…"]', 'H4: 熱さまシート', '{"location": "ベッド枕元", "object_type": "熱さまシートのパッケージ", "brand_form": "青と白のパッケージに『熱さまシート』のロゴ、実在の製品デザイン", "attachment": "ベッド上に置かれている", "scale_note": "実在の熱さまシートパッケージと同じサイズ（約15cm×10cm）"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_03.png', 'nana', '[nana] アンメルツヨコヨコ…このネーミング!
[haruki] 背中に届く横向き塗布部を持つから『ヨコヨコ』。困りごとを商品名にまでしてる。
[nana] ブルーレット、熱さまシート、アンメルツ…全部、誰かの困りごとから生まれてる。
[haruki] それが小林製薬の核心。『あったらいいな』をカタチにする会社。', '困りごとを、商品名にまで', 'アンメルツヨコヨコ / 横向き塗布部 / ユニークなネーミング', NULL, '["[nana] アンメルツヨコヨコ…このネーミング!", "[haruki] 背中に届く横向き塗布部を持つから『ヨコヨコ』。困りごとを商品名にまでしてる。", "[nana] ブルーレット、熱さまシート、アンメルツ…全部、誰かの困りごとから生まれてる。", "[haruki] それが小林製薬の核心。『あったらいいな』をカタチにする会社。"]', 'H5: アンメルツヨコヨコ', '{"location": "棚中央", "object_type": "アンメルツヨコヨコのパッケージ", "brand_form": "緑とオレンジの容器に『アンメルツヨコヨコ』のロゴ、ヨコ型塗布部が特徴", "attachment": "棚に陳列", "scale_note": "実在のアンメルツヨコヨコと同じサイズ（約12cm）"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_04.png', 'haruki', '[haruki] 小林製薬、売上1,656億円。国内シェアNo.1のブランドが43品もある。
[nana] 43品も!?
[haruki] サワデー、サラサーティ、トイレその後に、桐灰カイロ…全部ニッチトップ戦略。
[nana] 大きな市場を取るんじゃなくて、小さな困りごとで1番を取る。', '国内シェアNo.1が43品', '売上1,656億円 / ニッチトップ戦略', '2024年12月期決算・公式サイト', '["[haruki] 小林製薬、売上1,656億円。国内シェアNo.1のブランドが43品もある。", "[nana] 43品も!?", "[haruki] サワデー、サラサーティ、トイレその後に、桐灰カイロ…全部ニッチトップ戦略。", "[nana] 大きな市場を取るんじゃなくて、小さな困りごとで1番を取る。"]', 'H3: 『あったらいいな』ロゴ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_05.png', 'nana', '[nana] でも平均年収757万円って、花王とかP&Gより低くない?
[haruki] そう、大手日用品メーカーよりは低い。でも小林製薬は営業利益率15.0%。
[haruki] ニッチトップ戦略だから、広告費を抑えて利益率を高く保てる。年収はその構造の中にある。
[nana] 派手じゃないけど、利益率が高いから長く安定して働ける…', '757万円+営業利益率15.0%', 'ニッチトップ戦略 / 広告費を抑えて利益率を高める', '2024年12月期決算・有報', '["[nana] でも平均年収757万円って、花王とかP&Gより低くない?", "[haruki] そう、大手日用品メーカーよりは低い。でも小林製薬は営業利益率15.0%。", "[haruki] ニッチトップ戦略だから、広告費を抑えて利益率を高く保てる。年収はその構造の中にある。", "[nana] 派手じゃないけど、利益率が高いから長く安定して働ける…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_06.png', 'haruki', '[OB先輩] 配属は営業・研究・製造に分かれる。希望通りいく人もいれば、そうでない人もいる。
[OB先輩] でも小林製薬は若手から『あったらいいな』の提案を吸い上げる文化がある。
[OB先輩] 入社3年目で新商品の企画提案を通した先輩もいる。配属先より、何を提案するかが大事。
[haruki] 困りごとを見つける力が、配属先より評価される会社なんだ…', '配属先より、何を提案するか', '営業・研究・製造 / 若手から『あったらいいな』を吸い上げる', NULL, '["[OB先輩] 配属は営業・研究・製造に分かれる。希望通りいく人もいれば、そうでない人もいる。", "[OB先輩] でも小林製薬は若手から『あったらいいな』の提案を吸い上げる文化がある。", "[OB先輩] 入社3年目で新商品の企画提案を通した先輩もいる。配属先より、何を提案するかが大事。", "[haruki] 困りごとを見つける力が、配属先より評価される会社なんだ…"]', 'H6: 仙台小林製薬工場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_07.png', 'nana', '[OB先輩] 小林製薬が見るのは『ごんたの10か条』。特に4つ。主体性、チャレンジ精神、関係構築力、やり遂げる力。
[OB先輩] 採用は競争が激しいけど、本当に見てるのは、困りごとを見つけて提案できる人かどうか。
[nana] (静かに) 困りごとを見つける力…それが全ての始まりなんだ。
[haruki] あったらいいなを、自分で見つけられる人。', 'ごんたの10か条 / 4つの要件', '主体性・チャレンジ・関係構築・やり遂げる力', NULL, '["[OB先輩] 小林製薬が見るのは『ごんたの10か条』。特に4つ。主体性、チャレンジ精神、関係構築力、やり遂げる力。", "[OB先輩] 採用は競争が激しいけど、本当に見てるのは、困りごとを見つけて提案できる人かどうか。", "[nana] (静かに) 困りごとを見つける力…それが全ての始まりなんだ。", "[haruki] あったらいいなを、自分で見つけられる人。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_08.png', 'nana', '[nana] サワデーも小林製薬だったんだ…
[haruki] そう、芳香剤のトップブランド。サラサーティもそう。おりものシートの固有名詞になってる。
[nana] トイレ、発熱、肩こり、芳香、生理…全部、誰も大きく語らない困りごと。
[haruki] でも毎日ある。それをカタチにし続けてる。', '誰も大きく語らない困りごとを', 'サワデー / サラサーティ / トイレその後に / 桐灰カイロ', NULL, '["[nana] サワデーも小林製薬だったんだ…", "[haruki] そう、芳香剤のトップブランド。サラサーティもそう。おりものシートの固有名詞になってる。", "[nana] トイレ、発熱、肩こり、芳香、生理…全部、誰も大きく語らない困りごと。", "[haruki] でも毎日ある。それをカタチにし続けてる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。ドラッグストアで顧客の声を拾い、新商品を企画する営業。
[haruki] 研究所で、誰も気づかなかった困りごとをカタチにする研究員。
[haruki] 仙台工場で、43品のニッチトップを支える品質管理担当。
[nana] どれも、誰かの困りごとに向き合ってる。', '10年後、たとえばこんな場面', 'ドラッグストア / 研究所 / 仙台工場', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。ドラッグストアで顧客の声を拾い、新商品を企画する営業。", "[haruki] 研究所で、誰も気づかなかった困りごとをカタチにする研究員。", "[haruki] 仙台工場で、43品のニッチトップを支える品質管理担当。", "[nana] どれも、誰かの困りごとに向き合ってる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kobayashi-pharma', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/kobayashi-pharma/panel_10.png', 'both', '[haruki] 売上1,656億円、営業利益率15.0%、採用55名。
[nana] 困りごとをカタチにする土俵、ここにある。
[both] あったらいいなをカタチにする。小林製薬、困りごとの先にある未来。', '困りごとをカタチにする土俵', '売上1,656億円 / 営業利益率15.0% / 採用55名', NULL, '["[haruki] 売上1,656億円、営業利益率15.0%、採用55名。", "[nana] 困りごとをカタチにする土俵、ここにある。", "[both] あったらいいなをカタチにする。小林製薬、困りごとの先にある未来。"]', 'H1: KDX小林道修町ビル本社', NULL);

-- ===== sap-japan (SAPジャパン株式会社) =====
-- source: output/sap-japan/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('sap-japan', 'SAPジャパン株式会社', 'others', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_01.png', 'nana', '[nana] ねえ、このアプリ便利すぎない? レシート撮るだけで経費精算終わるんだけど。
[haruki] ああ、それ『SAP Concur』だね。
[nana] サップ? コンカー?
[haruki] 世界9,300万人が使ってる経費管理システム。でもそれ、SAPっていう会社のほんの一部なんだよ。', 'スマホで撮るだけ、経費精算', 'SAP Concur / 9,300万ユーザー / これが入口', NULL, '["[nana] ねえ、このアプリ便利すぎない? レシート撮るだけで経費精算終わるんだけど。", "[haruki] ああ、それ『SAP Concur』だね。", "[nana] サップ? コンカー?", "[haruki] 世界9,300万人が使ってる経費管理システム。でもそれ、SAPっていう会社のほんの一部なんだよ。"]', 'H3: スマホで領収書撮影（Concur）', '{"location": "ナナの手元のスマホ画面", "object_type": "Concur アプリ画面", "brand_form": "スマホ画面に領収書画像とConcurロゴ（青と白のシンプルな意匠）", "attachment": "スマホディスプレイ内に表示", "scale_note": "実在のConcurアプリUIと同等サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_02.png', 'haruki', '[haruki] SAPは世界最大級のERPソフトウェア企業。従業員10万5,000人、130カ国に拠点がある。
[nana] 10万人!? そんなに大きいの?
[haruki] ERPっていうのは、企業の経理・人事・在庫・生産をぜんぶ一元管理するシステム。
[nana] つまり、会社の基幹システムぜんぶってこと…?', '世界最大級ERPベンダー', '従業員10万5,000人 / 130カ国 / 企業の基幹システムすべて', NULL, '["[haruki] SAPは世界最大級のERPソフトウェア企業。従業員10万5,000人、130カ国に拠点がある。", "[nana] 10万人!? そんなに大きいの?", "[haruki] ERPっていうのは、企業の経理・人事・在庫・生産をぜんぶ一元管理するシステム。", "[nana] つまり、会社の基幹システムぜんぶってこと…?"]', 'H4: グローバル100拠点超の世界地図', '{"location": "タブレット画面中央", "object_type": "世界地図上のSAP拠点マップ", "brand_form": "世界地図に130カ国の拠点が光る点として表示、SAPロゴ（青）が画面隅", "attachment": "タブレット画面内に表示", "scale_note": "タブレット画面全体を使用"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_03.png', 'haruki', '[haruki] SAPの主力製品が『S/4 HANA』。第4世代のERP。
[nana] 第4世代?
[haruki] インメモリデータベースで、リアルタイムに企業の全データを処理できる。経理も在庫も人事も、すべてが瞬時に見える。
[nana] 企業のデジタル変革って、ここから始まるんだ…', 'S/4 HANA、第4世代ERP', 'インメモリDB / リアルタイム全データ処理 / デジタル変革の起点', NULL, '["[haruki] SAPの主力製品が『S/4 HANA』。第4世代のERP。", "[nana] 第4世代?", "[haruki] インメモリデータベースで、リアルタイムに企業の全データを処理できる。経理も在庫も人事も、すべてが瞬時に見える。", "[nana] 企業のデジタル変革って、ここから始まるんだ…"]', 'H2: SAP S/4 HANA', '{"location": "壁面ディスプレイ中央", "object_type": "S/4 HANA ダッシュボード画面", "brand_form": "リアルタイムデータが流れるダッシュボード、S/4 HANAロゴ（青と白）", "attachment": "ディスプレイ内に表示", "scale_note": "実在の企業ダッシュボードUIと同等"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_04.png', 'haruki', '[haruki] SAPは1972年、ドイツIBMを辞めた5人の技術者が起業した。
[nana] IBM辞めて起業…
[haruki] リーダーがハッソ・プラットナー。スタンフォード大学のd.schoolに39億円を投じて、デザイン思考を世界に広めた人。
[nana] 技術者が、デザイン思考…? すごい組み合わせ。', '1972年、IBM技術者5人の起業', 'ハッソ・プラットナー / d.school創設 / デザイン思考の伝道者', NULL, '["[haruki] SAPは1972年、ドイツIBMを辞めた5人の技術者が起業した。", "[nana] IBM辞めて起業…", "[haruki] リーダーがハッソ・プラットナー。スタンフォード大学のd.schoolに39億円を投じて、デザイン思考を世界に広めた人。", "[nana] 技術者が、デザイン思考…? すごい組み合わせ。"]', 'H5: 創業者ハッソ・プラットナー', '{"location": "壁面展示中央", "object_type": "創業者写真とd.school写真", "brand_form": "ハッソ・プラットナーの肖像写真、隣にスタンフォードd.school建物写真", "attachment": "壁面にフレーム展示", "scale_note": "実在のオフィス展示サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_05.png', 'nana', '[nana] 外資だから年収高いんでしょ?
[haruki] 平均1,117万円。でも仕組みが独特。
[haruki] 学部卒は年収約400万円のジョブグレード2からスタート。グローバル統一基準で、実力次第でグレードが上がる。
[nana] 日本企業みたいな年功序列じゃなくて、グローバル共通の階段を登るってこと…', '1,117万円、ジョブグレード型', '学部卒約400万円スタート / グローバル統一基準 / 実力で登る階段', 'OpenWork 2025', '["[nana] 外資だから年収高いんでしょ?", "[haruki] 平均1,117万円。でも仕組みが独特。", "[haruki] 学部卒は年収約400万円のジョブグレード2からスタート。グローバル統一基準で、実力次第でグレードが上がる。", "[nana] 日本企業みたいな年功序列じゃなくて、グローバル共通の階段を登るってこと…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_06.png', 'nana', '[OB先輩] 入社時までにTOEIC800点以上が推奨。というか、ほぼ必須。
[OB先輩] 業務はほぼ英語。グローバルチームとの会議、ドキュメント、すべて英語ベース。
[nana] 毎日英語…
[OB先輩] 配属は営業・コンサル・エンジニアに分かれるけど、どれも顧客と直接向き合う。130カ国どこにでも飛ぶ覚悟が要る。', 'TOEIC800点、ほぼ必須', '業務は英語ベース / 130カ国どこでも / 顧客と直接向き合う', NULL, '["[OB先輩] 入社時までにTOEIC800点以上が推奨。というか、ほぼ必須。", "[OB先輩] 業務はほぼ英語。グローバルチームとの会議、ドキュメント、すべて英語ベース。", "[nana] 毎日英語…", "[OB先輩] 配属は営業・コンサル・エンジニアに分かれるけど、どれも顧客と直接向き合う。130カ国どこにでも飛ぶ覚悟が要る。"]', 'H4: グローバル100拠点超の世界地図（再使用）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_07.png', 'nana', '[OB先輩] SAPが求めるのは、Vision 2032の行動原則に共感できる人。
[OB先輩] 『Be Borderless』壁を超えたオープンな思考。『Take Smart Risks』リスクを恐れない挑戦。
[nana] 倍率は高いって聞いたけど…
[OB先輩] 数字より大事なのは、グローバルな環境で主体的に動けるか。それだけ。', 'Be Borderless / Take Smart Risks', 'Vision 2032行動原則 / 倍率より社風 / 主体性とオープン思考', NULL, '["[OB先輩] SAPが求めるのは、Vision 2032の行動原則に共感できる人。", "[OB先輩] 『Be Borderless』壁を超えたオープンな思考。『Take Smart Risks』リスクを恐れない挑戦。", "[nana] 倍率は高いって聞いたけど…", "[OB先輩] 数字より大事なのは、グローバルな環境で主体的に動けるか。それだけ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_08.png', 'haruki', '[haruki] 2024年、SAPジャパンの売上成長率は前年比20%増。グローバル平均の2倍。
[nana] 日本だけ、そんなに伸びてるの?
[haruki] 2025年から本格展開するAIアシスタント『Joule』が鍵。130以上の生成AIユースケースを組み込んで、業務プロセスを自律実行する。
[nana] AIが、経理も在庫も人事も、ぜんぶ回すってこと…?', '日本売上、前年比20%増', 'グローバルの2倍成長 / AIアシスタントJoule / 130以上の生成AIユースケース', NULL, '["[haruki] 2024年、SAPジャパンの売上成長率は前年比20%増。グローバル平均の2倍。", "[nana] 日本だけ、そんなに伸びてるの?", "[haruki] 2025年から本格展開するAIアシスタント『Joule』が鍵。130以上の生成AIユースケースを組み込んで、業務プロセスを自律実行する。", "[nana] AIが、経理も在庫も人事も、ぜんぶ回すってこと…?"]', 'H6: AI搭載ビジネスアシスタント Joule', '{"location": "モニター中央", "object_type": "Joule AIアシスタント画面", "brand_form": "AIアシスタントJouleのインターフェース、青と白のデザイン、SAPロゴ", "attachment": "モニター内に表示", "scale_note": "実在のJoule UIと同等"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。ニューヨーク本社で、グローバル製品戦略を立案。
[haruki] 東京のクライアント工場で、S/4 HANA導入プロジェクトをリード。
[haruki] スタンフォードd.schoolで、デザイン思考を学び直して次世代UIを設計。
[nana] 技術と、デザインと、ビジネス。ぜんぶ繋がってる…', '10年後、たとえばこんな場面', 'ニューヨーク / 東京工場 / スタンフォードd.school', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。ニューヨーク本社で、グローバル製品戦略を立案。", "[haruki] 東京のクライアント工場で、S/4 HANA導入プロジェクトをリード。", "[haruki] スタンフォードd.schoolで、デザイン思考を学び直して次世代UIを設計。", "[nana] 技術と、デザインと、ビジネス。ぜんぶ繋がってる…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sap-japan', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/sap-japan/panel_10.png', 'both', '[haruki] 従業員10万5,000人、130カ国、採用約20名。
[nana] スマホで領収書を撮るだけ。その先に、こんな世界が広がってたんだ。
[both] 世界の叡智と革新性で、より良い明日を創る。SAPジャパン、1972年からの挑戦。', '世界の叡智と革新性で、より良い明日を創る', '従業員10万5,000人 / 130カ国 / 採用約20名', NULL, '["[haruki] 従業員10万5,000人、130カ国、採用約20名。", "[nana] スマホで領収書を撮るだけ。その先に、こんな世界が広がってたんだ。", "[both] 世界の叡智と革新性で、より良い明日を創る。SAPジャパン、1972年からの挑戦。"]', 'H1: 大手町三井物産ビル本社', NULL);

-- ===== septeni-hd (株式会社セプテーニ・ホールディングス) =====
-- source: output/septeni-hd/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('septeni-hd', '株式会社セプテーニ・ホールディングス', 'advertising_media', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_01.png', 'nana', '[nana] このマンガアプリ、GANMA!って知ってる? 全話無料で読めるんだけど。
[haruki] 知ってる。1,700万DL突破してるやつでしょ。
[nana] えっ、そんなに? でもこれ、広告会社が作ってるって知ってた?
[haruki] セプテーニ・ホールディングス。マンガも広告も、両方やってる会社だよ。', 'そのマンガアプリ、広告会社が作ってる', 'セプテーニ・ホールディングス / 4293 / GANMA! 1,700万DL', NULL, '["[nana] このマンガアプリ、GANMA!って知ってる? 全話無料で読めるんだけど。", "[haruki] 知ってる。1,700万DL突破してるやつでしょ。", "[nana] えっ、そんなに? でもこれ、広告会社が作ってるって知ってた?", "[haruki] セプテーニ・ホールディングス。マンガも広告も、両方やってる会社だよ。"]', 'H2: GANMA!アプリアイコン', '{"location": "ナナのスマホ画面中央", "object_type": "GANMA!アプリアイコン", "brand_form": "GANMAの赤いロゴマーク、アプリアイコンの意匠そのまま", "attachment": "スマホ画面に表示", "scale_note": "実在のアプリアイコンサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_02.png', 'haruki', '[haruki] セプテーニの本業は、デジタル広告の運用支援。
[nana] インスタとかYouTubeで見る広告?
[haruki] そう。Google、Yahoo!、Facebook、Instagram、TikTok…日常で目にする広告の配信・運用を企業に代わってやる。
[nana] 毎日見てる広告、セプテーニが回してるかもしれないってこと…?', '毎日見る広告、セプテーニが回してる', 'Google / Yahoo! / Facebook / Instagram / TikTok', NULL, '["[haruki] セプテーニの本業は、デジタル広告の運用支援。", "[nana] インスタとかYouTubeで見る広告?", "[haruki] そう。Google、Yahoo!、Facebook、Instagram、TikTok…日常で目にする広告の配信・運用を企業に代わってやる。", "[nana] 毎日見てる広告、セプテーニが回してるかもしれないってこと…?"]', 'H4: デジタル広告運用画面', '{"location": "ノートPC画面中央", "object_type": "デジタル広告運用ダッシュボード", "brand_form": "Google・Facebook・Instagram・Yahoo!のロゴアイコンが並ぶ広告管理画面の抽象イメージ", "attachment": "PC画面に表示", "scale_note": "実在の広告運用ツールの通常表示サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_03.png', 'nana', '[nana] でも、なんで広告会社がマンガアプリ?
[haruki] それが、セプテーニの戦略。広告運用だけじゃなくて、自分でメディアも持つ。
[haruki] GANMA!は310作品以上のオリジナルマンガを無料配信してる。累計1,700万DL。
[nana] 広告で稼ぎながら、自分でもコンテンツを作ってる…二刀流なんだ。', '広告運用+自社IP、二刀流', 'GANMA! 310作品以上 / 1,700万DL突破', NULL, '["[nana] でも、なんで広告会社がマンガアプリ?", "[haruki] それが、セプテーニの戦略。広告運用だけじゃなくて、自分でメディアも持つ。", "[haruki] GANMA!は310作品以上のオリジナルマンガを無料配信してる。累計1,700万DL。", "[nana] 広告で稼ぎながら、自分でもコンテンツを作ってる…二刀流なんだ。"]', 'H2: GANMA!アプリアイコン (再使用)', '{"location": "ナナのスマホ画面", "object_type": "GANMA!作品一覧画面", "brand_form": "GANMAのロゴとマンガ作品サムネイルが並ぶ一覧画面", "attachment": "スマホ画面に表示", "scale_note": "実在のアプリ画面サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_04.png', 'haruki', '[haruki] セプテーニは1990年創業、36年目。本社は新宿グランドタワーの30階。
[nana] 36年…意外と歴史ある。
[haruki] 2025年12月期の収益303億円、営業利益42億円。前期比で営業利益+35%成長。
[nana] 広告もマンガも伸びてる…静かに強い会社なんだ。', '1990年創業、36年目の成長企業', '収益303億円 / 営業利益42億円 (前期比+35%)', '2025年12月期決算', '["[haruki] セプテーニは1990年創業、36年目。本社は新宿グランドタワーの30階。", "[nana] 36年…意外と歴史ある。", "[haruki] 2025年12月期の収益303億円、営業利益42億円。前期比で営業利益+35%成長。", "[nana] 広告もマンガも伸びてる…静かに強い会社なんだ。"]', 'H1: 住友不動産新宿グランドタワー', '{"location": "タワー上部の外壁", "object_type": "建築サイン (Septeni Holdings)", "brand_form": "ガラスファサード上部に『Septeni Holdings』のサイン、控えめに", "attachment": "タワー外壁30階付近に固定", "scale_note": "実在の本社表示と同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_05.png', 'nana', '[nana] 年収は?
[haruki] 平均664.8万円。東証スタンダード上場の堅実な水準。
[haruki] でも初任給は月給365,000円。これ、時間外手当92,655円と深夜手当16,480円を含んだ額。
[nana] え、残業代込みで提示してるんだ…リアルだね。', '初任給365,000円=残業代込み', '平均年収664.8万円 / 東証スタンダード上場', '有報・採用ページ', '["[nana] 年収は?", "[haruki] 平均664.8万円。東証スタンダード上場の堅実な水準。", "[haruki] でも初任給は月給365,000円。これ、時間外手当92,655円と深夜手当16,480円を含んだ額。", "[nana] え、残業代込みで提示してるんだ…リアルだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_06.png', 'nana', '[OB先輩] セプテーニの選考は独特で、志望動機や自己PRの準備は不要です。
[OB先輩] HaKaSe診断という適性検査で、個性・環境・行動の3軸を測定して、入社後の活躍傾向を算出します。
[OB先輩] 2009年から7,000人以上のデータを蓄積して、配属にも活用しています。
[nana] 志望動機いらないって…データで人を見るんだ。', '志望動機不要、HaKaSe診断で配属', '個性・環境・行動の3軸 / 2009年から7,000人のデータ蓄積', NULL, '["[OB先輩] セプテーニの選考は独特で、志望動機や自己PRの準備は不要です。", "[OB先輩] HaKaSe診断という適性検査で、個性・環境・行動の3軸を測定して、入社後の活躍傾向を算出します。", "[OB先輩] 2009年から7,000人以上のデータを蓄積して、配属にも活用しています。", "[nana] 志望動機いらないって…データで人を見るんだ。"]', 'H3: HaKaSe診断ツール画面', '{"location": "ノートPC画面中央", "object_type": "HaKaSe診断ツール画面", "brand_form": "適性検査の結果グラフと数値、抽象的なダッシュボード", "attachment": "PC画面に表示", "scale_note": "実在の診断ツール画面サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_07.png', 'haruki', '[haruki] セプテーニの社是は『ひねらんかい』。関西弁で『知恵を出そう、工夫しよう』って意味。
[nana] ひねらんかい…! 関西弁の社是って、珍しい。
[haruki] 創業者の七村守さんがリクルート出身で、1990年に立ち上げた。
[nana] 志望動機より個性を見る選考も、『ひねらんかい』の精神なのかも。', 'ひねらんかい (知恵を出そう)', '創業1990年 / 創業者 七村守 (リクルート出身)', NULL, '["[haruki] セプテーニの社是は『ひねらんかい』。関西弁で『知恵を出そう、工夫しよう』って意味。", "[nana] ひねらんかい…! 関西弁の社是って、珍しい。", "[haruki] 創業者の七村守さんがリクルート出身で、1990年に立ち上げた。", "[nana] 志望動機より個性を見る選考も、『ひねらんかい』の精神なのかも。"]', 'H5: ひねらんかいロゴ', '{"location": "壁面中央", "object_type": "ひねらんかいロゴサイン", "brand_form": "関西弁の『ひねらんかい』をデザイン化したロゴ、金属プレートまたは木彫", "attachment": "壁面に固定", "scale_note": "実在の社内展示の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_08.png', 'haruki', '[haruki] 2022年1月、セプテーニは電通グループの連結子会社になった。
[nana] 電通の傘下に…!?
[haruki] 独立性は保ちつつ、電通との協業案件が前期比+40%成長してる。
[nana] 広告の巨人と組んで、さらに広がってるんだ…', '2022年、電通グループ連結子会社化', '協業案件 前期比+40%成長', NULL, '["[haruki] 2022年1月、セプテーニは電通グループの連結子会社になった。", "[nana] 電通の傘下に…!?", "[haruki] 独立性は保ちつつ、電通との協業案件が前期比+40%成長してる。", "[nana] 広告の巨人と組んで、さらに広がってるんだ…"]', 'H6: 電通グループロゴとの並列', '{"location": "スクリーン中央", "object_type": "電通グループロゴとセプテーニロゴの並列表示", "brand_form": "電通の赤いロゴとセプテーニの青いロゴが並ぶプレゼン資料", "attachment": "スクリーンに投影", "scale_note": "実在のプレゼン資料サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。新宿本社で大手クライアントのデジタル広告戦略を統括。
[haruki] GANMA!編集部でオリジナルマンガのヒット作を企画。
[haruki] 電通との協業プロジェクトで、新しいメディアビジネスを立ち上げる。
[nana] 広告も、コンテンツも、両方を『ひねる』仕事…面白そう。', '10年後、たとえばこんな場面', '新宿本社 / GANMA!編集部 / 電通協業PJ', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。新宿本社で大手クライアントのデジタル広告戦略を統括。", "[haruki] GANMA!編集部でオリジナルマンガのヒット作を企画。", "[haruki] 電通との協業プロジェクトで、新しいメディアビジネスを立ち上げる。", "[nana] 広告も、コンテンツも、両方を『ひねる』仕事…面白そう。"]', 'H4: デジタル広告運用画面 (再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('septeni-hd', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/septeni-hd/panel_10.png', 'both', '[haruki] 収益303億円、営業利益42億円、GANMA!1,700万DL。
[nana] 広告会社だと思ってたけど、マンガも、データも、全部『ひねって』る。
[both] ひねって、広げて、元気にする。セプテーニ・ホールディングス、36年目の知恵。', 'ひねって、広げて、元気にする。', '収益303億円 / GANMA! 1,700万DL / 電通G連結子会社', NULL, '["[haruki] 収益303億円、営業利益42億円、GANMA!1,700万DL。", "[nana] 広告会社だと思ってたけど、マンガも、データも、全部『ひねって』る。", "[both] ひねって、広げて、元気にする。セプテーニ・ホールディングス、36年目の知恵。"]', 'H1: 住友不動産新宿グランドタワー (夜景)', NULL);

-- ===== tsuruha-hd (株式会社ツルハホールディングス) =====
-- source: output/tsuruha-hd/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('tsuruha-hd', '株式会社ツルハホールディングス', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_01.png', 'haruki', '[haruki] これ、1929年、北海道旭川の9坪薬局。
[nana] 9坪って…今のコンビニより狭い!?
[haruki] この薬局が、2026年に売上1兆4,505億円になった。
[nana] え、1兆円!? どうやって…', '9坪薬局が1兆4,505億円になった', 'ツルハホールディングス / 3391 / 1929年旭川創業', NULL, '["[haruki] これ、1929年、北海道旭川の9坪薬局。", "[nana] 9坪って…今のコンビニより狭い!?", "[haruki] この薬局が、2026年に売上1兆4,505億円になった。", "[nana] え、1兆円!? どうやって…"]', 'H3: 創業の地・旭川『鶴羽薬師堂』', '{"location": "薬局上部の看板", "object_type": "創業時の看板", "brand_form": "背の高い縦型看板に『鶴羽薬師堂』の文字、昭和初期の意匠", "attachment": "薬局建物に固定", "scale_note": "当時の実在写真の通り、建物の2倍の高さ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_02.png', 'haruki', '[haruki] 今はツルハ、くすりの福太郎、レデイ薬局を傘下に、2,600店舗超。
[nana] 2,600店舗!?
[haruki] グループ従業員11,554名。売上8,456億円。
[nana] 9坪から、ここまで…どうやって大きくなったの?', '2,600店舗超、11,554名', '売上8,456億円 (2025年2月期) / グループ店舗を統括', '有価証券報告書・公式IR', '["[haruki] 今はツルハ、くすりの福太郎、レデイ薬局を傘下に、2,600店舗超。", "[nana] 2,600店舗!?", "[haruki] グループ従業員11,554名。売上8,456億円。", "[nana] 9坪から、ここまで…どうやって大きくなったの?"]', 'H1: 札幌本社ビル（元町店）', '{"location": "1階店舗入口上部", "object_type": "ツルハドラッグ看板", "brand_form": "ツルハドラッグのロゴ看板、青と白の企業カラー", "attachment": "店舗ファサードに固定", "scale_note": "実在の店舗看板と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_03.png', 'haruki', '[haruki] ツルハの売上構成は、医薬品24%、化粧品14%、日用雑貨26%、食品26%。
[nana] あ、私が普段買ってるシャンプーも、お菓子も、全部ここで揃う…
[haruki] ドラッグストアって『薬』だけじゃない。生活インフラ。
[nana] だから2,600店舗も必要なんだ。', '医薬品24%、食品26%、日用品26%', 'ドラッグストア = 生活インフラ', NULL, '["[haruki] ツルハの売上構成は、医薬品24%、化粧品14%、日用雑貨26%、食品26%。", "[nana] あ、私が普段買ってるシャンプーも、お菓子も、全部ここで揃う…", "[haruki] ドラッグストアって『薬』だけじゃない。生活インフラ。", "[nana] だから2,600店舗も必要なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_04.png', 'haruki', '[haruki] 2025年12月、ウエルシアホールディングスと経営統合。
[nana] ウエルシアって、あの大手ドラッグストア…
[haruki] 統合後の2026年2月期売上は1兆4,505億円、純利益426億円。
[nana] 1兆円超えて、業界トップになる…9坪から、ここまで!', '1兆4,505億円、業界トップへ', '2026年1月 ウエルシア統合 / イオングループ連結子会社化', '公式IR・決算短信', '["[haruki] 2025年12月、ウエルシアホールディングスと経営統合。", "[nana] ウエルシアって、あの大手ドラッグストア…", "[haruki] 統合後の2026年2月期売上は1兆4,505億円、純利益426億円。", "[nana] 1兆円超えて、業界トップになる…9坪から、ここまで!"]', 'H5: ウエルシアとの経営統合ロゴ', '{"location": "スクリーン中央", "object_type": "統合ロゴ", "brand_form": "ツルハとウエルシアの統合ロゴ、2026年1月イオン連結子会社化", "attachment": "スクリーンに投影", "scale_note": "スクリーンの1/4程度"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_05.png', 'nana', '[nana] でも、小売だし、年収は…?
[haruki] 平均604万円。確かに商社や金融より低い。
[haruki] でも構造はこう。店舗スタッフ → 店長 → スーパーバイザー → MD・本部。長期で積み上げる。
[nana] 店舗からキャリアが始まって、10年後にはエリアや商品を統括する側になれる…', '604万円 = 店舗からの積み上げ', '店舗 → 店長 → SV → MD・本部 / 長期キャリアパス', '日経会社情報 3391', '["[nana] でも、小売だし、年収は…?", "[haruki] 平均604万円。確かに商社や金融より低い。", "[haruki] でも構造はこう。店舗スタッフ → 店長 → スーパーバイザー → MD・本部。長期で積み上げる。", "[nana] 店舗からキャリアが始まって、10年後にはエリアや商品を統括する側になれる…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_06.png', 'nana', '[OB先輩] 新卒はほぼ全員、店舗配属からスタート。調剤・MD・店長候補の3コース。
[OB先輩] 最初の3年は発注、在庫管理、接客、調剤補助…全部やる。
[nana] 店舗で、全部…?
[OB先輩] そう。2,600店舗を支えるのは、この現場を知ってる人だけ。本部に行くのは、その後。', '新卒ほぼ全員、店舗配属から', '調剤・MD・店長候補の3コース / 最初3年は現場', NULL, '["[OB先輩] 新卒はほぼ全員、店舗配属からスタート。調剤・MD・店長候補の3コース。", "[OB先輩] 最初の3年は発注、在庫管理、接客、調剤補助…全部やる。", "[nana] 店舗で、全部…?", "[OB先輩] そう。2,600店舗を支えるのは、この現場を知ってる人だけ。本部に行くのは、その後。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_07.png', 'nana', '[OB先輩] ツルハが求めるのは、この3つのモットーを体現できる人。
[OB先輩] お客様第一、しんせつ第一、信用第一。
[nana] 地域のお客さんと、長く信頼関係を築ける人…
[haruki] 派手なスキルじゃなくて、誠実さ。それが95年続いた理由なんだ。', 'お客様第一・しんせつ第一・信用第一', '地域との信頼関係を築くコミュニケーション能力', NULL, '["[OB先輩] ツルハが求めるのは、この3つのモットーを体現できる人。", "[OB先輩] お客様第一、しんせつ第一、信用第一。", "[nana] 地域のお客さんと、長く信頼関係を築ける人…", "[haruki] 派手なスキルじゃなくて、誠実さ。それが95年続いた理由なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_08.png', 'nana', '[nana] あれ、ツルハポイントと楽天ポイント、両方つくの?
[haruki] そう、ツルハは楽天ポイントと併用できる。どっちもポイントが貯まる。
[nana] 私、毎週ここで買い物してるから、知らないうちにポイント貯まってた…
[haruki] 生活の中に溶け込んでる。それがツルハの強さ。', '楽天ポイント併用、どちらも貯まる', '生活インフラとしてのドラッグストア', NULL, '["[nana] あれ、ツルハポイントと楽天ポイント、両方つくの?", "[haruki] そう、ツルハは楽天ポイントと併用できる。どっちもポイントが貯まる。", "[nana] 私、毎週ここで買い物してるから、知らないうちにポイント貯まってた…", "[haruki] 生活の中に溶け込んでる。それがツルハの強さ。"]', 'H4: ツルハポイントカード', '{"location": "ナナの手元", "object_type": "ツルハポイントカード", "brand_form": "ツルハポイントカード、青と白のデザイン", "attachment": "ナナが手に持つ", "scale_note": "実在のカードと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。札幌の店舗で店長として地域のお客様と信頼関係を築く。
[haruki] 東京本社でMDとして、2,600店舗の商品構成を企画する。
[haruki] シンガポールの海外店舗で、アジア展開の最前線に立つ。
[nana] 9坪から1兆円。次は、私たちが2兆円を作る番かも。', '10年後、たとえばこんな場面', '札幌店長 / 東京MD / シンガポール海外店舗', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。札幌の店舗で店長として地域のお客様と信頼関係を築く。", "[haruki] 東京本社でMDとして、2,600店舗の商品構成を企画する。", "[haruki] シンガポールの海外店舗で、アジア展開の最前線に立つ。", "[nana] 9坪から1兆円。次は、私たちが2兆円を作る番かも。"]', 'H6: タイ・ベトナム海外1号店', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tsuruha-hd', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/tsuruha-hd/panel_10.png', 'both', '[haruki] 売上1兆4,505億円、2,600店舗超、従業員11,554名。
[nana] 9坪から95年、成長は止まらない。
[both] 9坪から1兆円、次は2兆円へ。ツルハホールディングス、成長の現在地。', '9坪から1兆円、次は2兆円へ。', '売上1兆4,505億円 / 2,600店舗超 / 従業員11,554名', NULL, '["[haruki] 売上1兆4,505億円、2,600店舗超、従業員11,554名。", "[nana] 9坪から95年、成長は止まらない。", "[both] 9坪から1兆円、次は2兆円へ。ツルハホールディングス、成長の現在地。"]', 'H3: 創業の地・旭川『鶴羽薬師堂』(回想) + H1: 札幌本社ビル(現在)', NULL);

-- ===== usj (合同会社ユー・エス・ジェイ（USJ）) =====
-- source: output/usj/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('usj', '合同会社ユー・エス・ジェイ（USJ）', 'advertising_media', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_01.png', 'nana', '[nana] USJって、要は遊園地でしょ? アルバイトの延長みたいな…
[haruki] え、遊園地?
[nana] だって、パークで働くってそういうことじゃないの?
[haruki] それ、エンターテイメント企業を見誤ってるかも。', '遊園地じゃなくて、エンターテイメント企業', '合同会社ユー・エス・ジェイ（USJ） / 非上場', NULL, '["[nana] USJって、要は遊園地でしょ? アルバイトの延長みたいな…", "[haruki] え、遊園地?", "[nana] だって、パークで働くってそういうことじゃないの?", "[haruki] それ、エンターテイメント企業を見誤ってるかも。"]', 'H2: ユニバーサル・スタジオ・ジャパン地球儀ロゴ', '{"location": "画面中央背景", "object_type": "巨大回転地球儀ロゴ", "brand_form": "USJのシンボル、青い地球に白い大陸、回転台座付き", "attachment": "専用台座に固定", "scale_note": "実在の入口地球儀と同じ巨大サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_02.png', 'haruki', '[haruki] 従業員15,724名。社員3,657名、アルバイト12,067名。年間来場者は推定1500万人超。
[nana] え、そんなに…?
[haruki] 2017年の9カ月で売上1413億円、営業利益256億円。遊園地じゃなくて、エンターテイメント産業の巨人。
[nana] 数字だけ見たら、普通に大企業じゃん…', '従業員15,724名、売上1413億円', '年間推定1500万人超が来場する巨大ビジネス', '公式IR・有報', '["[haruki] 従業員15,724名。社員3,657名、アルバイト12,067名。年間来場者は推定1500万人超。", "[nana] え、そんなに…?", "[haruki] 2017年の9カ月で売上1413億円、営業利益256億円。遊園地じゃなくて、エンターテイメント産業の巨人。", "[nana] 数字だけ見たら、普通に大企業じゃん…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_03.png', 'nana', '[nana] このホグワーツ城、ワーナーがつくったんだと思ってた…
[haruki] 企画・運営はぜんぶUSJ。ワーナーからIPライセンスを取って、自社でエリア設計。
[nana] え、じゃあマリオも…?
[haruki] スーパー・ニンテンドー・ワールドも、任天堂とUSJの共同開発。IPを体験に変換する企画力が本業。', 'IPを体験に変換する企画力', 'ハリポタ / マリオ / ミニオン ぜんぶUSJの自社企画', NULL, '["[nana] このホグワーツ城、ワーナーがつくったんだと思ってた…", "[haruki] 企画・運営はぜんぶUSJ。ワーナーからIPライセンスを取って、自社でエリア設計。", "[nana] え、じゃあマリオも…?", "[haruki] スーパー・ニンテンドー・ワールドも、任天堂とUSJの共同開発。IPを体験に変換する企画力が本業。"]', 'H3: ホグワーツ城', '{"location": "画面中央背景", "object_type": "ホグワーツ城", "brand_form": "ハリー・ポッター・エリアの象徴的な城、石造り風の外観", "attachment": "エリア内に建設された建造物", "scale_note": "実在のホグワーツ城と同じ巨大スケール"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_04.png', 'haruki', '[haruki] 2001年開業から25年、ハリポタ・ミニオン・マリオと、大型エリアを次々投資。
[nana] それ、数百億円規模でしょ…?
[haruki] そう。2026年3月で25周年。投資→集客→利益→再投資のサイクルを回し続けてる。
[nana] 遊園地じゃなくて、エンターテイメントの長期戦略企業なんだ…', '2001年開業から25年、投資サイクル', 'ハリポタ / ミニオン / マリオ 数百億円規模の連続投資', NULL, '["[haruki] 2001年開業から25年、ハリポタ・ミニオン・マリオと、大型エリアを次々投資。", "[nana] それ、数百億円規模でしょ…?", "[haruki] そう。2026年3月で25周年。投資→集客→利益→再投資のサイクルを回し続けてる。", "[nana] 遊園地じゃなくて、エンターテイメントの長期戦略企業なんだ…"]', 'H4: スーパー・ニンテンドー・ワールド', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_05.png', 'nana', '[nana] でも、平均年収455万円って、そんなに高くないよね?
[haruki] OpenWorkの集計値で455万円。ただし2026年3月に正社員平均6.5%の昇給を実施。
[haruki] USJのスローガンは『No Limit!』。成果を出せば、限界なく評価される仕組み。
[nana] 固定給じゃなくて、自分次第で伸びる構造…', '455万円+昇給6.5%、No Limit!', '成果を出せば限界なく評価される仕組み', 'OpenWork / 公式IR', '["[nana] でも、平均年収455万円って、そんなに高くないよね?", "[haruki] OpenWorkの集計値で455万円。ただし2026年3月に正社員平均6.5%の昇給を実施。", "[haruki] USJのスローガンは『No Limit!』。成果を出せば、限界なく評価される仕組み。", "[nana] 固定給じゃなくて、自分次第で伸びる構造…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_06.png', 'haruki', '[先輩社員] 配属は12部門あって、希望通りいく人ばかりじゃない。パーク運営・企画・マーケ・施設管理…
[先輩社員] シフト制で土日祝は基本出勤。ゲストが来る時間が勝負だから、カレンダー通りじゃない。
[先輩社員] でも、自分のアイデアが数万人のゲストに届く瞬間は、ほかの仕事じゃ味わえない。
[haruki] 働き方はハードだけど、やりがいの規模が桁違い…', '12部門、シフト制、土日祝出勤', '希望通りいかない配属もある / 数万人に届くやりがい', NULL, '["[先輩社員] 配属は12部門あって、希望通りいく人ばかりじゃない。パーク運営・企画・マーケ・施設管理…", "[先輩社員] シフト制で土日祝は基本出勤。ゲストが来る時間が勝負だから、カレンダー通りじゃない。", "[先輩社員] でも、自分のアイデアが数万人のゲストに届く瞬間は、ほかの仕事じゃ味わえない。", "[haruki] 働き方はハードだけど、やりがいの規模が桁違い…"]', 'H6: パーククルー制服', '{"location": "先輩社員の身体", "object_type": "パーククルー制服", "brand_form": "カラフルな職種別ユニフォーム、エンターテイナー精神を体現", "attachment": "先輩社員が着用", "scale_note": "実在の制服デザイン"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_07.png', 'nana', '[採用担当] USJが求めるのは、『自分は何をすべきか』『自分には何ができるか』を、自ら考え、自ら探し、自ら行動する人。
[採用担当] 採用人数は2025年度127名。決して少なくないけど、受け身の人は残らない。
[nana] 自ら動く、って言葉、重いな…
[haruki] 『No Limit!』は、限界を自分で決めない人のためのスローガンなんだ。', '自ら考え、自ら探し、自ら行動する', '2025年度採用127名 / 受け身の人は残らない文化', NULL, '["[採用担当] USJが求めるのは、『自分は何をすべきか』『自分には何ができるか』を、自ら考え、自ら探し、自ら行動する人。", "[採用担当] 採用人数は2025年度127名。決して少なくないけど、受け身の人は残らない。", "[nana] 自ら動く、って言葉、重いな…", "[haruki] 『No Limit!』は、限界を自分で決めない人のためのスローガンなんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_08.png', 'nana', '[nana] このミニオンエリアも、USJの企画…
[haruki] そう。ちなみに女性管理職比率28%、役員に占める女性割合36%。エンターテイメント業界でトップクラス。
[nana] 女性が活躍してる現場なんだ…
[haruki] ゲストの半分以上は女性。だから社内も女性の視点が不可欠なんだ。', '女性管理職28%、役員36%', 'ゲストの半分以上が女性 / 女性の視点が不可欠', NULL, '["[nana] このミニオンエリアも、USJの企画…", "[haruki] そう。ちなみに女性管理職比率28%、役員に占める女性割合36%。エンターテイメント業界でトップクラス。", "[nana] 女性が活躍してる現場なんだ…", "[haruki] ゲストの半分以上は女性。だから社内も女性の視点が不可欠なんだ。"]', 'H5: ミニオン・パーク', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。新エリア開発の企画リーダーとして、次のIPを選定。
[haruki] マーケティング部門で、年間1500万人の来場データを解析して施策を立案。
[haruki] 海外パークとの提携交渉で、USJの企画力を輸出する。
[nana] どれも、数万人から数百万人に届く仕事…', '10年後、たとえばこんな場面', '新エリア企画 / データ解析 / 海外提携交渉', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。新エリア開発の企画リーダーとして、次のIPを選定。", "[haruki] マーケティング部門で、年間1500万人の来場データを解析して施策を立案。", "[haruki] 海外パークとの提携交渉で、USJの企画力を輸出する。", "[nana] どれも、数万人から数百万人に届く仕事…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('usj', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/usj/panel_10.png', 'both', '[haruki] 従業員15,724名、2025年度採用127名、平均年収455万円+昇給6.5%。
[nana] 遊園地じゃなくて、エンターテイメント企業だったんだ。
[both] 限界のない創造力で、数百万人に届ける。合同会社ユー・エス・ジェイ、No Limit!の現在地。', '限界のない創造力で、数百万人に届ける', '従業員15,724名 / 2025年度採用127名 / 平均年収455万円', NULL, '["[haruki] 従業員15,724名、2025年度採用127名、平均年収455万円+昇給6.5%。", "[nana] 遊園地じゃなくて、エンターテイメント企業だったんだ。", "[both] 限界のない創造力で、数百万人に届ける。合同会社ユー・エス・ジェイ、No Limit!の現在地。"]', 'H1: 本社ビル（パーク内）', NULL);

-- ===== welcia-hd (ウエルシアホールディングス株式会社) =====
-- source: output/welcia-hd/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('welcia-hd', 'ウエルシアホールディングス株式会社', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_01.png', 'nana', '[nana] この店、いつも来てるけど…
[haruki] ウエルシア、売上1兆2,850億円だよ。
[nana] え、1兆円!? この近所の店が?
[haruki] 全国3,013店舗。毎日通ってる店、実は日本トップクラスのドラッグストアチェーンなんだ。', '毎日の店、売上1兆2,850億円', 'ウエルシアHD / 3141 / 全国3,013店舗', NULL, '["[nana] この店、いつも来てるけど…", "[haruki] ウエルシア、売上1兆2,850億円だよ。", "[nana] え、1兆円!? この近所の店が?", "[haruki] 全国3,013店舗。毎日通ってる店、実は日本トップクラスのドラッグストアチェーンなんだ。"]', 'H2: 調剤併設型ドラッグストア店舗', '{"location": "店舗ファサード上部", "object_type": "ウエルシア店舗ロゴ看板", "brand_form": "Welciaロゴ、青と白の配色、バックライト付き", "attachment": "店舗外壁に固定", "scale_note": "実在店舗の標準サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_02.png', 'haruki', '[haruki] ウエルシアの強みは、調剤併設店舗が2,282店舗あること。
[nana] 調剤併設って、処方箋を受け付けてる店?
[haruki] そう。併設率77.3%。ほぼ8割の店舗に薬剤師がいて、処方箋を受け付けられる。
[nana] 病院帰りに薬もらって、日用品も買える。だから毎日ここに来てたんだ…', '調剤併設2,282店舗、併設率77.3%', '処方箋受付 + 日用品 = 専門総合店舗', '2025年2月期決算短信', '["[haruki] ウエルシアの強みは、調剤併設店舗が2,282店舗あること。", "[nana] 調剤併設って、処方箋を受け付けてる店?", "[haruki] そう。併設率77.3%。ほぼ8割の店舗に薬剤師がいて、処方箋を受け付けられる。", "[nana] 病院帰りに薬もらって、日用品も買える。だから毎日ここに来てたんだ…"]', 'H2: 調剤併設型ドラッグストア店舗', '{"location": "処方箋受付カウンター上部", "object_type": "処方箋受付サイン", "brand_form": "「処方箋受付」の青いサイン、Welciaロゴ入り", "attachment": "カウンター上部に吊り下げ", "scale_note": "実在店舗の標準サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_03.png', 'nana', '[nana] あれ、深夜なのに開いてる…
[haruki] ウエルシアは24時間営業店舗も多い。しかも深夜でも薬剤師が常駐してる店がある。
[nana] 深夜に薬剤師さんがいるの!?
[haruki] 急な発熱や体調不良でも、深夜に健康相談できる。地域の医療インフラになってるんだ。', '深夜でも薬剤師常駐、健康相談可能', '24時間営業店舗 / 地域の医療インフラ', NULL, '["[nana] あれ、深夜なのに開いてる…", "[haruki] ウエルシアは24時間営業店舗も多い。しかも深夜でも薬剤師が常駐してる店がある。", "[nana] 深夜に薬剤師さんがいるの!?", "[haruki] 急な発熱や体調不良でも、深夜に健康相談できる。地域の医療インフラになってるんだ。"]', 'H6: 深夜・24時間営業店舗', '{"location": "店舗入口上部", "object_type": "24時間営業サイン", "brand_form": "「24時間営業」の光る看板、Welciaロゴ", "attachment": "店舗外壁に固定", "scale_note": "実在店舗の標準サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_04.png', 'nana', '[nana] この商品、からだWelciaって…自社ブランド?
[haruki] プライベートブランドで390品目。健康とエコをテーマにした商品が多い。
[nana] あ、外に移動販売車が…
[haruki] うえん号。買い物が難しい地域に巡回してる。2024年グッドデザイン賞を取った。', 'PB390品目 + 移動販売うえん号', 'からだWelcia / くらしWelcia / 2024年グッドデザイン賞', NULL, '["[nana] この商品、からだWelciaって…自社ブランド?", "[haruki] プライベートブランドで390品目。健康とエコをテーマにした商品が多い。", "[nana] あ、外に移動販売車が…", "[haruki] うえん号。買い物が難しい地域に巡回してる。2024年グッドデザイン賞を取った。"]', 'H5: プライベートブランド商品 + H4: 移動販売車うえん号', '{"location": "商品パッケージ中央", "object_type": "からだWelciaロゴ", "brand_form": "「からだWelcia」の緑と白のパッケージロゴ", "attachment": "商品パッケージに印刷", "scale_note": "実在商品の標準サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_05.png', 'nana', '[nana] 年収はどれくらい?
[haruki] ホールディングスの平均年収は799万円。ただしこれは持株会社の平均。
[haruki] 薬剤師の初任給は平均35.5万円前後。調剤業務と小売業務の両方を担うから、専門性が評価される。
[nana] 持株会社と現場で構造が違うんだ。薬剤師は専門職として高い水準…', '平均年収799万円(HD) / 薬剤師初任給35.5万円', '持株会社と現場の構造 / 専門性を評価', '年収データ2024年度', '["[nana] 年収はどれくらい?", "[haruki] ホールディングスの平均年収は799万円。ただしこれは持株会社の平均。", "[haruki] 薬剤師の初任給は平均35.5万円前後。調剤業務と小売業務の両方を担うから、専門性が評価される。", "[nana] 持株会社と現場で構造が違うんだ。薬剤師は専門職として高い水準…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_06.png', 'nana', '[OB先輩] 新卒は基本、店舗配属からスタート。調剤業務と小売業務の両方を覚える。
[OB先輩] 薬剤師は調剤がメインだけど、棚卸しや発注も担当することがある。
[nana] 医療と小売、両方やるんですね…
[OB先輩] ウエルシアは地域密着だから、転勤は基本エリア内。でも店舗ごとに客層も処方箋も違う。毎日が学び。', '店舗配属から、調剤と小売の両方', '地域密着転勤 / 店舗ごとに異なる学び', NULL, '["[OB先輩] 新卒は基本、店舗配属からスタート。調剤業務と小売業務の両方を覚える。", "[OB先輩] 薬剤師は調剤がメインだけど、棚卸しや発注も担当することがある。", "[nana] 医療と小売、両方やるんですね…", "[OB先輩] ウエルシアは地域密着だから、転勤は基本エリア内。でも店舗ごとに客層も処方箋も違う。毎日が学び。"]', 'H2: 調剤併設型ドラッグストア店舗', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_07.png', 'nana', '[採用担当] ウエルシアの理念は『お客様の豊かな社会生活と健康な暮らしを提供する』。
[採用担当] ビジョンは『生活のプラットフォームになる』。処方箋も日用品も健康相談も、ぜんぶここで完結する街角を目指してる。
[nana] 地域の健康を、街角から支える…
[haruki] 倍率は公表されてないけど、求めるのは地域に根を張る覚悟がある人、ってことか。', '生活のプラットフォームになる', '地域の健康を街角から / 専門総合店舗の実現', NULL, '["[採用担当] ウエルシアの理念は『お客様の豊かな社会生活と健康な暮らしを提供する』。", "[採用担当] ビジョンは『生活のプラットフォームになる』。処方箋も日用品も健康相談も、ぜんぶここで完結する街角を目指してる。", "[nana] 地域の健康を、街角から支える…", "[haruki] 倍率は公表されてないけど、求めるのは地域に根を張る覚悟がある人、ってことか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_08.png', 'nana', '[nana] あれ、店舗の中にカフェが…
[haruki] ウエルカフェ。地域協働コミュニティスペース。2024年グッドデザイン賞を取ってる。
[nana] 健康相談イベントとか、地域の人が集まる場所になってるんだ…
[haruki] 買い物だけじゃない。地域の居場所を作ってる。', 'ウエルカフェ、地域の居場所', 'コミュニティスペース / 2024年グッドデザイン賞', NULL, '["[nana] あれ、店舗の中にカフェが…", "[haruki] ウエルカフェ。地域協働コミュニティスペース。2024年グッドデザイン賞を取ってる。", "[nana] 健康相談イベントとか、地域の人が集まる場所になってるんだ…", "[haruki] 買い物だけじゃない。地域の居場所を作ってる。"]', 'H3: ウエルカフェ', '{"location": "カフェ入口上部", "object_type": "ウエルカフェサイン", "brand_form": "「Welcafe」のロゴサイン、木製風", "attachment": "入口上部に吊り下げ", "scale_note": "実在店舗の標準サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_09.png', 'haruki', '[nana] もし入社できたら、10年後どこにいるんだろう…
[haruki] たとえば、こんな未来。調剤カウンターで、患者さんの服薬指導をしてる薬剤師。
[haruki] ウエルカフェで、地域の健康セミナーを企画するエリアマネージャー。
[haruki] 移動販売車うえん号で、買い物が難しい高齢者に笑顔を届ける職員。
[nana] どれも、地域に根を張る仕事だ…', '10年後、たとえばこんな場面', '調剤カウンター / ウエルカフェ / うえん号', NULL, '["[nana] もし入社できたら、10年後どこにいるんだろう…", "[haruki] たとえば、こんな未来。調剤カウンターで、患者さんの服薬指導をしてる薬剤師。", "[haruki] ウエルカフェで、地域の健康セミナーを企画するエリアマネージャー。", "[haruki] 移動販売車うえん号で、買い物が難しい高齢者に笑顔を届ける職員。", "[nana] どれも、地域に根を張る仕事だ…"]', 'H2: 調剤併設型ドラッグストア店舗 + H3: ウエルカフェ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('welcia-hd', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/welcia-hd/panel_10.png', 'both', '[haruki] 売上1兆2,850億円、調剤併設2,282店舗、採用897人。
[nana] 毎日通ってた店が、地域の健康インフラだったんだ。
[both] 毎日の健康を、街角から。ウエルシアホールディングス、生活のプラットフォーム。', '毎日の健康を、街角から。', '売上 約1兆2,850億円 / 調剤併設2,282店舗 / 採用897人', NULL, '["[haruki] 売上1兆2,850億円、調剤併設2,282店舗、採用897人。", "[nana] 毎日通ってた店が、地域の健康インフラだったんだ。", "[both] 毎日の健康を、街角から。ウエルシアホールディングス、生活のプラットフォーム。"]', 'H2: 調剤併設型ドラッグストア店舗', '{"location": "店舗ファサード上部", "object_type": "ウエルシア店舗ロゴ看板", "brand_form": "Welciaロゴ、青と白の配色、バックライト付き", "attachment": "店舗外壁に固定", "scale_note": "実在店舗の標準サイズ"}');

-- ===== workman (株式会社ワークマン) =====
-- source: output/workman/scenario_v4.json
-- jsDelivr ref: @40a0a39efab9f226c5026db3ec4fa2dec7aa0afa
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('workman', '株式会社ワークマン', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_01.png', 'nana', '[nana] ワークマンって、作業服の店でしょ? 就活先としては…
[haruki] え、それ10年前の常識かも。
[nana] え? 作業服じゃないの?
[haruki] 今は違う。銀座に旗艦店があって、女性客が7割の店舗もある。', '作業服の店でしょ? それ10年前の常識かも', 'ワークマン / 7564 / 高機能×低価格の革命', NULL, '["[nana] ワークマンって、作業服の店でしょ? 就活先としては…", "[haruki] え、それ10年前の常識かも。", "[nana] え? 作業服じゃないの?", "[haruki] 今は違う。銀座に旗艦店があって、女性客が7割の店舗もある。"]', 'H3: オレンジ×黒のロゴと店舗', '{"location": "店舗上部の看板", "object_type": "ワークマンロゴ看板", "brand_form": "オレンジ地に黒文字で『WORKMAN』、やる気ワクワクのキャッチコピー", "attachment": "店舗外壁に固定", "scale_note": "実在の店舗看板と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_02.png', 'haruki', '[haruki] 営業総収入1,326億円。全国1,011店舗、全47都道府県に出店完了。
[nana] え、そんなに!? 作業服の店が?
[haruki] フランチャイズ展開で急成長。でも本当にすごいのは、10期連続増収増益を『しない経営』で実現したこと。
[nana] しない経営…? 何をしないの?', '営業総収入1,326億円、1,011店舗', '全47都道府県に出店完了 / 10期連続増収増益', '公式IR・有報', '["[haruki] 営業総収入1,326億円。全国1,011店舗、全47都道府県に出店完了。", "[nana] え、そんなに!? 作業服の店が?", "[haruki] フランチャイズ展開で急成長。でも本当にすごいのは、10期連続増収増益を『しない経営』で実現したこと。", "[nana] しない経営…? 何をしないの?"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_03.png', 'nana', '[nana] え、これがワークマン!? 銀座に…
[haruki] Workman Colors、機能性ベーシックウェア専門店。女性客が7割の店舗もある。
[nana] 作業服のイメージ、まったくない…
[haruki] WORKMAN Plus、ワークマン女子、Workman Colors。3つの業態で客層を広げてる。', '銀座に旗艦店、女性客7割の店舗も', 'WORKMAN Plus / ワークマン女子 / Workman Colors', NULL, '["[nana] え、これがワークマン!? 銀座に…", "[haruki] Workman Colors、機能性ベーシックウェア専門店。女性客が7割の店舗もある。", "[nana] 作業服のイメージ、まったくない…", "[haruki] WORKMAN Plus、ワークマン女子、Workman Colors。3つの業態で客層を広げてる。"]', 'H4: 銀座エグジットメルサ Workman Colors 旗艦店', '{"location": "店舗入口上部", "object_type": "Workman Colors ロゴ", "brand_form": "シンプルなサンセリフ書体で『Workman Colors』、都市型のデザイン", "attachment": "店舗外壁に固定", "scale_note": "実在の旗艦店と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_04.png', 'nana', '[nana] 2,900円で防水防寒スーツ!? これ本当にプロ仕様なの?
[haruki] 原価率65%。一般的アパレルの2倍以上。品質を落とさず、流通コストを削ってる。
[haruki] PB比率はチェーン全店売上の約6割。商品企画から製造まで全部自社で。
[nana] 高機能×低価格って、こうやって実現してたんだ…', '原価率65%、PB比率6割', '2,900円イージス防水防寒スーツ / 高機能×低価格の秘密', '公式IR・メディア取材', '["[nana] 2,900円で防水防寒スーツ!? これ本当にプロ仕様なの?", "[haruki] 原価率65%。一般的アパレルの2倍以上。品質を落とさず、流通コストを削ってる。", "[haruki] PB比率はチェーン全店売上の約6割。商品企画から製造まで全部自社で。", "[nana] 高機能×低価格って、こうやって実現してたんだ…"]', 'H7: 2,900円イージス防水防寒スーツ', '{"location": "商品タグ中央", "object_type": "価格タグ", "brand_form": "2,900円の価格表示、高機能×低価格のコピー", "attachment": "商品に吊り下げ", "scale_note": "実在の店舗タグと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_05.png', 'nana', '[nana] でも年収は…そんなに高くないよね?
[haruki] 平均756.8万円。初任給は月給26.1万円。
[haruki] でも、ワークマンの理念は『エブリデー・ロープライス』。価格を抑えるために、あらゆるコストを削る。
[nana] 年収も、その構造の一部なんだ…低価格を実現するための。', '756.8万円 (平均) + エブリデー・ロープライス', '初任給 月給26.1万円 / 低価格実現のための構造', '日経会社情報 7564', '["[nana] でも年収は…そんなに高くないよね?", "[haruki] 平均756.8万円。初任給は月給26.1万円。", "[haruki] でも、ワークマンの理念は『エブリデー・ロープライス』。価格を抑えるために、あらゆるコストを削る。", "[nana] 年収も、その構造の一部なんだ…低価格を実現するための。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_06.png', 'haruki', '[OB先輩] ワークマンの働き方は『しない経営』。残業しない、ノルマ設けない、頑張らない。
[OB先輩] 18時には全員帰る。データ分析はExcelで完結。一括発注ボタンを押すだけで仕入れ完了。
[OB先輩] ストレスフリーだけど、数字やデータに強くないと厳しい。全員がExcel使いこなす前提。
[haruki] 頑張らないで10期連続増収増益…逆にすごい。', 'しない経営 / 残業しない / ノルマ設けない', '18時退社 / Excel経営 / 数字に強い人材', NULL, '["[OB先輩] ワークマンの働き方は『しない経営』。残業しない、ノルマ設けない、頑張らない。", "[OB先輩] 18時には全員帰る。データ分析はExcelで完結。一括発注ボタンを押すだけで仕入れ完了。", "[OB先輩] ストレスフリーだけど、数字やデータに強くないと厳しい。全員がExcel使いこなす前提。", "[haruki] 頑張らないで10期連続増収増益…逆にすごい。"]', 'H6: しない経営の象徴的シーン', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_07.png', 'nana', '[OB先輩] ワークマンが見るのは、『親切心』。社員採用条件の第1がこれ。
[OB先輩] 新しいことを学び成長したい、数字やデータに強い、協調性や親切心を生かした経験。
[nana] (静かに) 親切心が第1って、初めて聞いた…
[haruki] 低価格を実現するには、社員同士の協力が不可欠。親切心が経営の核なんだ。', '社員採用条件の第1は親切心', '数字に強い / 協調性 / 成長意欲', NULL, '["[OB先輩] ワークマンが見るのは、『親切心』。社員採用条件の第1がこれ。", "[OB先輩] 新しいことを学び成長したい、数字やデータに強い、協調性や親切心を生かした経験。", "[nana] (静かに) 親切心が第1って、初めて聞いた…", "[haruki] 低価格を実現するには、社員同士の協力が不可欠。親切心が経営の核なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_08.png', 'nana', '[nana] これ、全部Excelで…? データ分析から発注まで?
[haruki] そう。ワークマンの『エクセル経営』。全社員がデータ分析できる前提。
[nana] ITシステムじゃなくて、Excelで1,011店舗を管理してるの!?
[haruki] 一括発注ボタンを押すだけで仕入れ完了。シンプルだけど、数字に強くないと務まらない。', 'エクセル経営 / 全社員がデータ分析', '1,011店舗を一括発注 / シンプルでも数字に強い', NULL, '["[nana] これ、全部Excelで…? データ分析から発注まで?", "[haruki] そう。ワークマンの『エクセル経営』。全社員がデータ分析できる前提。", "[nana] ITシステムじゃなくて、Excelで1,011店舗を管理してるの!?", "[haruki] 一括発注ボタンを押すだけで仕入れ完了。シンプルだけど、数字に強くないと務まらない。"]', 'H5: エクセル経営のデータ分析風景', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。銀座で新業態の店舗開発を企画。
[haruki] 伊勢崎本社でExcelを駆使した全店データ分析。
[haruki] 海外の新規出店候補地で、高機能×低価格を世界に広げる。
[nana] しない経営だけど、やることは深く広い。どれも、長く残る仕事。', '10年後、たとえばこんな場面', '銀座 / 伊勢崎本社 / 海外出店候補地', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。銀座で新業態の店舗開発を企画。", "[haruki] 伊勢崎本社でExcelを駆使した全店データ分析。", "[haruki] 海外の新規出店候補地で、高機能×低価格を世界に広げる。", "[nana] しない経営だけど、やることは深く広い。どれも、長く残る仕事。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('workman', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@40a0a39efab9f226c5026db3ec4fa2dec7aa0afa/public/images/workman/panel_10.png', 'both', '[haruki] 営業総収入1,326億円、1,011店舗、採用約30名。
[nana] しない経営で、10期連続増収増益。親切心が第1の会社。
[both] しない経営で、10期連続増収増益。ワークマン、高機能×低価格の革命。', 'しない経営で、10期連続増収増益。', '営業総収入 1,326億円 / 1,011店舗 / 採用 約30名', NULL, '["[haruki] 営業総収入1,326億円、1,011店舗、採用約30名。", "[nana] しない経営で、10期連続増収増益。親切心が第1の会社。", "[both] しない経営で、10期連続増収増益。ワークマン、高機能×低価格の革命。"]', 'H1: 群馬県伊勢崎市の関東信越本部ビル (朝の光)', NULL);

