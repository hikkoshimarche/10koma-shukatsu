-- ===================================================================
-- migration_v4_industry_10koma.sql — 業界研究10コマ(16業界×10) D1反映
-- 生成: tokyari-pipeline/scripts/gen_d1_sql_gyokai.py (scenario_to_panels --v4 lint通過)
-- 【未適用】適用条件: タブCの業界研究ページ実装完了 + Web Claude最終確認後。
-- 書き手はタブE一本(タブCはフロントのみ)。REF を public 画像push後のhashへ差し替えてから適用。
-- ===================================================================

-- (1) v4拡張列: company_panels には既に存在(既存400社で導入済)。未導入環境のみ以下を有効化。
-- ALTER TABLE company_panels ADD COLUMN main_copy TEXT;
-- ALTER TABLE company_panels ADD COLUMN sub_copy TEXT;
-- ALTER TABLE company_panels ADD COLUMN source_url TEXT;
-- ALTER TABLE company_panels ADD COLUMN script_json TEXT;
-- ALTER TABLE company_panels ADD COLUMN visual_hook TEXT;
-- ALTER TABLE company_panels ADD COLUMN brand_object_json TEXT;

-- (2) industries タクソノミー整合: 不足3業界を追加(既存はIGNORE)。
INSERT OR IGNORE INTO industries (id, name, description, panel_count) VALUES ('it_ai_saas_game', 'IT・AI・SaaS・ゲーム', 'ソフトの拡張性で人の行動を動かす。IT・AI・SaaS・ゲームの統合業界。', 10);
INSERT OR IGNORE INTO industries (id, name, description, panel_count) VALUES ('manufacturer_maker', 'メーカー', '見えない基幹技術で生活と社会の土台を作る。自動車・電機・素材・化粧品等のメーカー統合。', 10);
INSERT OR IGNORE INTO industries (id, name, description, panel_count) VALUES ('education_hr', '教育・人材', '学びとはたらく機会で人の可能性を広げる。教育・人材サービス。', 10);
INSERT OR IGNORE INTO industries (id, name, description, panel_count) VALUES ('startup', 'スタートアップ', '新しい一つのアイデアに賭け、少人数で常識を変える新興企業群。', 10);
INSERT OR IGNORE INTO industries (id, name, description, panel_count) VALUES ('deeptech_space_ai', 'ディープテック・宇宙・AI', 'まだ世にない基盤技術をゼロから作る。宇宙輸送・AI基盤モデル・最先端半導体。', 10);

-- (3) 業界16 = companies疑似会社行 + company_panels 160行 (INSERT OR IGNORE / OR REPLACE 冪等)

-- ===== industry_10koma__sogo-shosha (総合商社) =====
-- source: output/industry_10koma__sogo-shosha/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__sogo-shosha', '総合商社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_01.png', 'nana', '[nana] このおにぎり、ふつうにローソンで買うやつだよね。
[haruki] うん。でもこのローソン、三菱商事のグループ会社なんだ。
[nana] え、商社ってエネルギーとか鉄とかの会社じゃないの?
[haruki] それも本当。でも実は、資源からこのおにぎりまで、ぜんぶ動かしてる。', 'このおにぎりも、商社が動かしてる', '総合商社 / 資源から生活まで', NULL, '["[nana] このおにぎり、ふつうにローソンで買うやつだよね。", "[haruki] うん。でもこのローソン、三菱商事のグループ会社なんだ。", "[nana] え、商社ってエネルギーとか鉄とかの会社じゃないの?", "[haruki] それも本当。でも実は、資源からこのおにぎりまで、ぜんぶ動かしてる。"]', 'H_コンビニ店内(架空・無地看板・実ロゴなし)', '{"location": "店舗入口上部", "object_type": "架空のコンビニ看板", "brand_form": "無地または架空マークのコンビニ看板(実在チェーンのロゴ・商標・文字は一切描かない)", "attachment": "店舗外壁", "scale_note": "実在の店舗と同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_02.png', 'haruki', '[haruki] 天然ガスを運ぶこの船も、商社の仕事。
[haruki] 三菱はローソン、伊藤忠はファミマ、住友はメルカリにも出資してる。
[nana] エネルギーの船と、コンビニと、フリマアプリが、同じ会社の中にあるの?
[haruki] そう。扱う領域が広いから『総合』商社なんだ。', '資源も、コンビニも、アプリも', 'だから『総合』商社', '各社公式・事業紹介', '["[haruki] 天然ガスを運ぶこの船も、商社の仕事。", "[haruki] 三菱はローソン、伊藤忠はファミマ、住友はメルカリにも出資してる。", "[nana] エネルギーの船と、コンビニと、フリマアプリが、同じ会社の中にあるの?", "[haruki] そう。扱う領域が広いから『総合』商社なんだ。"]', 'H_LNGタンカー(天然ガス事業)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_03.png', 'haruki', '[haruki] 稼ぎ方は二つ。物を売り買いするトレーディングと、会社ごと持つ事業投資。
[nana] 事業投資って、株を持つってこと?
[haruki] うん。三菱の純利益は八千億円、伊藤忠は過去最高の八千八百億円。多くが投資先から生まれてる。
[nana] 自分で売るだけじゃなくて、育てて分け前をもらう仕組みなんだ。', 'トレーディング＋事業投資の二本柱', '純利益は三菱 約8,005億円 / 伊藤忠 約8,803億円', '各社2025年3月期・通期決算', '["[haruki] 稼ぎ方は二つ。物を売り買いするトレーディングと、会社ごと持つ事業投資。", "[nana] 事業投資って、株を持つってこと?", "[haruki] うん。三菱の純利益は八千億円、伊藤忠は過去最高の八千八百億円。多くが投資先から生まれてる。", "[nana] 自分で売るだけじゃなくて、育てて分け前をもらう仕組みなんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_04.png', 'haruki', '[haruki] 三菱食品は仕入先が約六千五百社、届け先が約三千社ある食品卸。
[nana] スーパーやコンビニに並ぶ前の、見えない通り道なんだ。
[haruki] 伊藤忠は綿花からアパレルまで繊維を一気通貫で扱う。服の裏側にもいる。
[nana] 毎日のごはんも服も、気づかないうちに通ってきてるんだね。', '毎日の食卓と服の、見えない通り道', '三菱食品 仕入約6,500社・販売約3,000社', '三菱商事 公式・事業紹介', '["[haruki] 三菱食品は仕入先が約六千五百社、届け先が約三千社ある食品卸。", "[nana] スーパーやコンビニに並ぶ前の、見えない通り道なんだ。", "[haruki] 伊藤忠は綿花からアパレルまで繊維を一気通貫で扱う。服の裏側にもいる。", "[nana] 毎日のごはんも服も、気づかないうちに通ってきてるんだね。"]', 'H_三菱食品の物流倉庫', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_05.png', 'nana', '[nana] 商社って給料が高いイメージだけど、なんでそんなに出せるの?
[haruki] 平均年収は三菱で約二千万円、伊藤忠で約千八百万円。有報の数字だよ。
[haruki] 高いのは、事業投資のリターンと、海外駐在の手当が土台にあるから。
[nana] 額そのものより、稼ぎの仕組みが給料に返ってきてるんだ。', '高年収は、事業投資と駐在の構造から', '平均年収 三菱 約2,033万円 / 伊藤忠 約1,805万円', '各社 有価証券報告書(2025年3月期)', '["[nana] 商社って給料が高いイメージだけど、なんでそんなに出せるの?", "[haruki] 平均年収は三菱で約二千万円、伊藤忠で約千八百万円。有報の数字だよ。", "[haruki] 高いのは、事業投資のリターンと、海外駐在の手当が土台にあるから。", "[nana] 額そのものより、稼ぎの仕組みが給料に返ってきてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_06.png', 'haruki', '[haruki] 事業領域が十くらいに分かれてて、第一希望どおりに配属される人ばかりじゃない。
[nana] 入ってみないと、どの分野になるか分からないんだ。
[haruki] しかも入社して数年で、海外駐在に出ることも普通にある。
[nana] 場所も分野も動く。腰を据えて動ける人に向いてるんだね。', '配属は広く、数年で海外駐在も', '第一希望どおりとは限らない働き方', NULL, '["[haruki] 事業領域が十くらいに分かれてて、第一希望どおりに配属される人ばかりじゃない。", "[nana] 入ってみないと、どの分野になるか分からないんだ。", "[haruki] しかも入社して数年で、海外駐在に出ることも普通にある。", "[nana] 場所も分野も動く。腰を据えて動ける人に向いてるんだね。"]', 'H_海外拠点オフィス(駐在)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_07.png', 'nana', '[nana] これだけ人気だと、採用はやっぱり狭き門なんでしょ?
[haruki] 狭き門だけど、各社が見てるのは点数より哲学なんだ。
[haruki] 三菱は所期奉公、伊藤忠は三方よし、住友は不趨浮利。社会と長く付き合う姿勢を問う。
[nana] どんな人か、どんな志か。会社の価値観と合うかを見てるんだ。', '選ぶ基準は、点数より哲学', '所期奉公 / 三方よし / 不趨浮利', NULL, '["[nana] これだけ人気だと、採用はやっぱり狭き門なんでしょ?", "[haruki] 狭き門だけど、各社が見てるのは点数より哲学なんだ。", "[haruki] 三菱は所期奉公、伊藤忠は三方よし、住友は不趨浮利。社会と長く付き合う姿勢を問う。", "[nana] どんな人か、どんな志か。会社の価値観と合うかを見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_08.png', 'nana', '[nana] コンビニで服まで買えるの、便利だなって思ってた。
[haruki] その衣料は伊藤忠が企画したブランドで、数年で売上が大きく伸びた。
[nana] 資源の船から、この靴下まで。ほんとに幅が広い。
[haruki] 生活のあちこちに、気づかれないまま入り込んでる。それが商社の強みだよ。', '資源の船から、この靴下まで', 'コンビニ衣料も商社の企画', '伊藤忠 繊維カンパニー 事例', '["[nana] コンビニで服まで買えるの、便利だなって思ってた。", "[haruki] その衣料は伊藤忠が企画したブランドで、数年で売上が大きく伸びた。", "[nana] 資源の船から、この靴下まで。ほんとに幅が広い。", "[haruki] 生活のあちこちに、気づかれないまま入り込んでる。それが商社の強みだよ。"]', 'H_コンビニウェア売り場(伊藤忠)', '{"location": "棚の商品タグ", "object_type": "コンビニ衣料PB", "brand_form": "無地のグレー基調アパレル、シンプルなタグ", "attachment": "商品に付属", "scale_note": "実在の売り場と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば中東で、天然ガスの取引を現地でまとめている。
[haruki] あるいはアジアで、コンビニの出店網を広げる企画をしている。
[nana] 資源も、生活も、自分の手で動かせるんだ。どれも大きく残る仕事だね。', '10年後、たとえばこんな場面', '中東のガス取引 / アジアの店舗網 / 国内の再エネ', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば中東で、天然ガスの取引を現地でまとめている。", "[haruki] あるいはアジアで、コンビニの出店網を広げる企画をしている。", "[nana] 資源も、生活も、自分の手で動かせるんだ。どれも大きく残る仕事だね。"]', 'H_LNGタンカー(天然ガス事業)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__sogo-shosha', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__sogo-shosha/panel_10.png', 'both', '[haruki] 資源から生活まで、売って、育てて、分け前をもらう。それが商社の稼ぎ方。
[nana] 見えないところで、こんなに世界を動かしてたんだ。
[both] 資源から、コンビニまで。動かしているのは、総合商社。', '資源から、コンビニまで。', 'トレーディング＋事業投資で世界を動かす業界', NULL, '["[haruki] 資源から生活まで、売って、育てて、分け前をもらう。それが商社の稼ぎ方。", "[nana] 見えないところで、こんなに世界を動かしてたんだ。", "[both] 資源から、コンビニまで。動かしているのは、総合商社。"]', 'H_丸の内の商社本社ビル群', NULL);

-- ===== industry_10koma__senmon-shosha (専門商社) =====
-- source: output/industry_10koma__senmon-shosha/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__senmon-shosha', '専門商社', 'specialty_trading', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_01.png', 'nana', '[nana] この棚、朝にはもう全部そろってるよね。誰が並べてるんだろう。
[haruki] 店員さんもだけど、その手前に専門商社の一日があるんだ。
[nana] 専門商社? 総合商社とは違うの?
[haruki] うん。分野をしぼって、メーカーと店をつなぐ黒子。今日の一日を追ってみよう。', 'この棚の裏に、専門商社の一日がある', '専門商社 / 分野をしぼる黒子', NULL, '["[nana] この棚、朝にはもう全部そろってるよね。誰が並べてるんだろう。", "[haruki] 店員さんもだけど、その手前に専門商社の一日があるんだ。", "[nana] 専門商社? 総合商社とは違うの?", "[haruki] うん。分野をしぼって、メーカーと店をつなぐ黒子。今日の一日を追ってみよう。"]', 'H_ドラッグストア・薬局の棚', '{"location": "陳列棚の全体", "object_type": "商品陳列棚", "brand_form": "整然と補充された日用品と医薬品の棚", "attachment": "店舗の棚", "scale_note": "実在の売り場と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_02.png', 'haruki', '[haruki] 一日は夜明け前から始まる。物流センターで、注文どおりに商品が仕分けられていく。
[nana] みんなが寝てる時間に、もう動いてるんだ。
[haruki] メディパルは、全国で約十万軒もの医療機関に薬を届けてる。
[nana] 薬が切れないのは、この早朝の仕事のおかげなんだ。', '夜明け前、物流センターから一日が始まる', 'メディパル 全国約10万軒の医療機関へ', 'メディパル 公式・会社情報', '["[haruki] 一日は夜明け前から始まる。物流センターで、注文どおりに商品が仕分けられていく。", "[nana] みんなが寝てる時間に、もう動いてるんだ。", "[haruki] メディパルは、全国で約十万軒もの医療機関に薬を届けてる。", "[nana] 薬が切れないのは、この早朝の仕事のおかげなんだ。"]', 'H_医薬品の高機能物流センター(メディパル)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_03.png', 'nana', '[nana] 総合商社が何でも扱うなら、専門商社は何が違うの?
[haruki] 分野を一つに絞って、そこで誰より深くつなぐ。国分は食品で、一万社のメーカーを束ねてる。
[haruki] 扱う商品は六十万点。どれを、いつ、どこに届けるかを毎日さばいてる。
[nana] 広く浅くじゃなくて、狭く深く。それが専門商社なんだ。', '分野を絞って、誰より深くつなぐ', '国分 食品メーカー約10,000社・約60万商品', '国分グループ 公式・会社情報', '["[nana] 総合商社が何でも扱うなら、専門商社は何が違うの?", "[haruki] 分野を一つに絞って、そこで誰より深くつなぐ。国分は食品で、一万社のメーカーを束ねてる。", "[haruki] 扱う商品は六十万点。どれを、いつ、どこに届けるかを毎日さばいてる。", "[nana] 広く浅くじゃなくて、狭く深く。それが専門商社なんだ。"]', 'H_食品物流とK&K缶詰(国分)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_04.png', 'haruki', '[haruki] 昼は営業や専門職が、病院や店を回る。欠品はないか、新しい商品はどうか。
[nana] ただ運ぶだけじゃなくて、現場と話すんだ。
[haruki] 医薬品では、専門の資格を持った担当者が正しい情報を医療機関に届ける。
[nana] 見えないところで、こまやかな気配りが積み重なってるんだね。', '昼は現場を回り、欠品と情報を調整', '医薬品は専門資格を持つ担当者が情報を届ける', '各社 公式・事業紹介', '["[haruki] 昼は営業や専門職が、病院や店を回る。欠品はないか、新しい商品はどうか。", "[nana] ただ運ぶだけじゃなくて、現場と話すんだ。", "[haruki] 医薬品では、専門の資格を持った担当者が正しい情報を医療機関に届ける。", "[nana] 見えないところで、こまやかな気配りが積み重なってるんだね。"]', 'H_MR・営業の訪問', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_05.png', 'nana', '[nana] 黒子の仕事だと、お給料は控えめなのかな。
[haruki] 上場してるスズケンは有報で平均約七百三十万円。国分は非上場、メディパルは持株会社で、現場の額は出典が定まらないんだ。
[haruki] だから額より、分野の専門性と、切らさない仕事の安定が土台、と見るのが正確だよ。
[nana] 目立たないけど、確かな専門性で長く積み上げる構造なんだ。', '専門性と安定が、年収の土台', 'スズケン約728万(有報) ※国分は非上場・メディパルはHDで現場額は出典不定', 'スズケン(9987) 有価証券報告書(2024年度)', '["[nana] 黒子の仕事だと、お給料は控えめなのかな。", "[haruki] 上場してるスズケンは有報で平均約七百三十万円。国分は非上場、メディパルは持株会社で、現場の額は出典が定まらないんだ。", "[haruki] だから額より、分野の専門性と、切らさない仕事の安定が土台、と見るのが正確だよ。", "[nana] 目立たないけど、確かな専門性で長く積み上げる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_06.png', 'haruki', '[haruki] 働き方は、ルート営業や提案の営業、物流、専門職に分かれる。
[nana] 同じ会社でも、担う役割がいろいろあるんだ。
[haruki] 全国を動く総合職と、地域を決めて働くエリア職がある会社も多い。
[nana] 自分の暮らす場所を選びながら、専門を深める道もあるんだね。', '営業・物流・専門職、エリアで働く道も', '全国型とエリア型という選択', NULL, '["[haruki] 働き方は、ルート営業や提案の営業、物流、専門職に分かれる。", "[nana] 同じ会社でも、担う役割がいろいろあるんだ。", "[haruki] 全国を動く総合職と、地域を決めて働くエリア職がある会社も多い。", "[nana] 自分の暮らす場所を選びながら、専門を深める道もあるんだね。"]', 'H_エリアの営業車・拠点', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_07.png', 'nana', '[nana] 安定してる分、採用の基準はどんなところを見るの?
[haruki] 点数より、人としての信用。国分は社是そのものが信用という言葉なんだ。
[haruki] スズケンは世のため人のため、メディパルは本質を見極め周囲を巻き込める人を大事にする。
[nana] 毎日を切らさない仕事だから、まず信頼できる人柄を見てるんだ。', '見るのは、点数より人の信用', '社是『信用』 / 世のため人のため / 本質を見極める', NULL, '["[nana] 安定してる分、採用の基準はどんなところを見るの?", "[haruki] 点数より、人としての信用。国分は社是そのものが信用という言葉なんだ。", "[haruki] スズケンは世のため人のため、メディパルは本質を見極め周囲を巻き込める人を大事にする。", "[nana] 毎日を切らさない仕事だから、まず信頼できる人柄を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_08.png', 'nana', '[nana] 夜にはまた、棚がきれいにそろってる。
[haruki] 一日の終わりに、明日の分がもう整ってる。切らさないことを、ずっと守ってきた。
[haruki] 国分は創業から三百年以上、信用を守り続けてる。それが専門商社の底力なんだ。
[nana] 当たり前に商品がある毎日は、こんなに長く守られてきたんだ。', '切らさないを、何百年も守り続ける', '国分 創業から300年以上、信用を守る', '国分グループ 公式・沿革', '["[nana] 夜にはまた、棚がきれいにそろってる。", "[haruki] 一日の終わりに、明日の分がもう整ってる。切らさないことを、ずっと守ってきた。", "[haruki] 国分は創業から三百年以上、信用を守り続けてる。それが専門商社の底力なんだ。", "[nana] 当たり前に商品がある毎日は、こんなに長く守られてきたんだ。"]', 'H_夜に整った店の棚', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば分野のプロとして、仕入れの舵を任されている。あるいは新しい物流を設計している。
[haruki] あるいは海外から、まだ日本にない商品を見つけて運んでいる。
[nana] 黒子だけど、毎日を止めない中心にいるんだ。', '10年後、たとえばこんな姿', '分野の仕入れを任される / 新しい物流の設計 / 海外調達', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば分野のプロとして、仕入れの舵を任されている。あるいは新しい物流を設計している。", "[haruki] あるいは海外から、まだ日本にない商品を見つけて運んでいる。", "[nana] 黒子だけど、毎日を止めない中心にいるんだ。"]', 'H_医薬品の高機能物流センター(メディパル)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__senmon-shosha', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__senmon-shosha/panel_10.png', 'both', '[haruki] 分野を絞って深くつなぎ、毎日を切らさない。それが専門商社の一日。
[nana] 当たり前に棚がそろう毎日は、見えない専門家たちが作ってたんだ。
[both] 毎日を、切らさない。それが、専門商社。', '毎日を、切らさない。', '分野を絞りメーカーと現場をつなぐ業界', NULL, '["[haruki] 分野を絞って深くつなぎ、毎日を切らさない。それが専門商社の一日。", "[nana] 当たり前に棚がそろう毎日は、見えない専門家たちが作ってたんだ。", "[both] 毎日を、切らさない。それが、専門商社。"]', 'H_ドラッグストア・薬局の棚', NULL);

-- ===== industry_10koma__finance (銀行・証券・保険) =====
-- source: output/industry_10koma__finance/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__finance', '銀行・証券・保険', 'banking_insurance', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_01.png', 'nana', '[nana] この前、新NISAの口座をつくったんだ。ちょっと大人になった気分。
[haruki] いいね。その一歩に、銀行と証券と保険が全部関わってるって知ってた?
[nana] え、口座をつくっただけだよ?
[haruki] そのお金が動くと、経済が回る。金融って、その仕組みそのものなんだ。', 'その一歩に、金融の全部が関わってる', '銀行・証券・保険 / お金を動かす業界', NULL, '["[nana] この前、新NISAの口座をつくったんだ。ちょっと大人になった気分。", "[haruki] いいね。その一歩に、銀行と証券と保険が全部関わってるって知ってた?", "[nana] え、口座をつくっただけだよ?", "[haruki] そのお金が動くと、経済が回る。金融って、その仕組みそのものなんだ。"]', 'H_ATM・店舗ネットワーク(メガバンク)', '{"location": "店舗入口のATMコーナー", "object_type": "銀行ATM", "brand_form": "整然と並ぶ現金自動預け払い機", "attachment": "床置き・壁付け", "scale_note": "実在のATMコーナーと同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_02.png', 'haruki', '[haruki] 金融には三つの顔がある。銀行はお金を貸す、証券は市場でつなぐ、保険はリスクを守る。
[nana] 貸す、つなぐ、守る。役割が分かれてるんだ。
[haruki] 三菱UFJ銀行は国内最大手、野村證券は預かる資産が百五十兆円を超える。
[nana] スケールが大きすぎて、想像が追いつかない。', '貸す・つなぐ・守る、三つの顔', '銀行=貸す / 証券=つなぐ / 保険=守る', '各社 公式・会社概要', '["[haruki] 金融には三つの顔がある。銀行はお金を貸す、証券は市場でつなぐ、保険はリスクを守る。", "[nana] 貸す、つなぐ、守る。役割が分かれてるんだ。", "[haruki] 三菱UFJ銀行は国内最大手、野村證券は預かる資産が百五十兆円を超える。", "[nana] スケールが大きすぎて、想像が追いつかない。"]', 'H_丸の内・大手町の金融ビル群', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_03.png', 'haruki', '[haruki] 銀行は集めた預金を企業に貸して、事業を大きくする後押しをする。
[nana] 私の預けたお金が、どこかの会社の挑戦を支えてるってこと?
[haruki] そう。三菱UFJの純利益は一年で一兆八千億円を超える。それだけ大きな流れを回してる。
[nana] お金が動くたびに、経済も人も育っていくんだ。', '預けたお金が、誰かの挑戦を育てる', '三菱UFJ 純利益 約1兆8,629億円', 'MUFG 2025年3月期・連結', '["[haruki] 銀行は集めた預金を企業に貸して、事業を大きくする後押しをする。", "[nana] 私の預けたお金が、どこかの会社の挑戦を支えてるってこと?", "[haruki] そう。三菱UFJの純利益は一年で一兆八千億円を超える。それだけ大きな流れを回してる。", "[nana] お金が動くたびに、経済も人も育っていくんだ。"]', 'H_証券トレーディングフロア(野村)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_04.png', 'haruki', '[haruki] 野村は戦後、百貨店に投資の相談所を置いて、資産形成を一般の人に広げた歴史がある。
[nana] 昔から、ふつうの人のお金と向き合ってきたんだ。
[haruki] 保険もそう。東京海上は日本で最初の保険会社で、いざという時の備えを支える。
[nana] 就職、住宅、年金…人生の節目のたびに、金融がそばにいるんだね。', '人生の節目のたびに、金融がいる', '野村=資産形成の民主化 / 東京海上=日本初の保険会社', '各社 公式・沿革', '["[haruki] 野村は戦後、百貨店に投資の相談所を置いて、資産形成を一般の人に広げた歴史がある。", "[nana] 昔から、ふつうの人のお金と向き合ってきたんだ。", "[haruki] 保険もそう。東京海上は日本で最初の保険会社で、いざという時の備えを支える。", "[nana] 就職、住宅、年金…人生の節目のたびに、金融がそばにいるんだね。"]', 'H_投資信託の相談窓口', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_05.png', 'nana', '[nana] 金融って安定してそうだけど、お給料はどうなの?
[haruki] メガバンクの平均は約八百五十万円、証券は約千二百万円、損保は約九百万円。有報の数字だよ。
[haruki] 額そのものより、役割と専門性を積むほど伸びる。運用や引受の専門職はまた別の伸び方をする。
[nana] 一律じゃなくて、何を極めるかで道が分かれる構造なんだ。', '役割と専門性を積むほど伸びる', '平均年収 メガバンク約856万 / 証券約1,224万 / 損保約904万', '各社 有価証券報告書等(2025年3月期)', '["[nana] 金融って安定してそうだけど、お給料はどうなの?", "[haruki] メガバンクの平均は約八百五十万円、証券は約千二百万円、損保は約九百万円。有報の数字だよ。", "[haruki] 額そのものより、役割と専門性を積むほど伸びる。運用や引受の専門職はまた別の伸び方をする。", "[nana] 一律じゃなくて、何を極めるかで道が分かれる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_06.png', 'haruki', '[haruki] 配属で道が分かれる。法人営業、個人のリテール、運用やアクチュアリの専門職。
[nana] 同じ会社でも、やることが全然ちがうんだ。
[haruki] 転勤のある総合職も、地域を決めて働く道もある。自分の暮らし方も選べる。
[nana] どこで何を積むか。入り口の選び方が大事なんだね。', '配属で道が分かれる。暮らし方も選べる', '法人 / リテール / 専門職 / 地域限定という選択', NULL, '["[haruki] 配属で道が分かれる。法人営業、個人のリテール、運用やアクチュアリの専門職。", "[nana] 同じ会社でも、やることが全然ちがうんだ。", "[haruki] 転勤のある総合職も、地域を決めて働く道もある。自分の暮らし方も選べる。", "[nana] どこで何を積むか。入り口の選び方が大事なんだね。"]', 'H_銀行の支店・窓口', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_07.png', 'nana', '[nana] 大人気の業界だと、採用はやっぱり厳しいんでしょ?
[haruki] 厳しいけど、見られるのは指示待ちじゃなく、自ら考えて動き、やり抜けるか。
[haruki] 野村は自律、三菱UFJは挑戦、東京海上は世のため人のためという志。人柄と姿勢を問う。
[nana] お金を扱うからこそ、誠実さと主体性を見てるんだ。', '見るのは、自ら考え動きやり抜く姿勢', '自律 / 挑戦 / 世のため人のため', NULL, '["[nana] 大人気の業界だと、採用はやっぱり厳しいんでしょ?", "[haruki] 厳しいけど、見られるのは指示待ちじゃなく、自ら考えて動き、やり抜けるか。", "[haruki] 野村は自律、三菱UFJは挑戦、東京海上は世のため人のためという志。人柄と姿勢を問う。", "[nana] お金を扱うからこそ、誠実さと主体性を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_08.png', 'haruki', '[haruki] 金融は女性が長く働きやすい業界の一つで、産休や育休の後も戻って伸びる人が多い。
[nana] 一度離れても、キャリアを続けられるんだ。
[haruki] 中途で入る人も多くて、いろんな経歴が混じる。若手が数字と信頼を積んで育つ器なんだ。
[nana] 安定してるだけじゃなくて、ちゃんと成長できる場所なんだね。', '若手も、長く成長できる器', '産休育休後の復帰・多様な経歴が混じる職場', '各社 公式・人事情報', '["[haruki] 金融は女性が長く働きやすい業界の一つで、産休や育休の後も戻って伸びる人が多い。", "[nana] 一度離れても、キャリアを続けられるんだ。", "[haruki] 中途で入る人も多くて、いろんな経歴が混じる。若手が数字と信頼を積んで育つ器なんだ。", "[nana] 安定してるだけじゃなくて、ちゃんと成長できる場所なんだね。"]', 'H_金融の研修・オフィス(女性総合職の成長)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば大企業のメインバンク担当として、会社の成長を資金で支えている。
[haruki] あるいは運用のプロとして、多くの人の資産を預かって動かしている。
[nana] お金を通じて、人や会社の成長に立ち会えるんだ。いい十年後だね。', '10年後、たとえばこんな姿', '企業のメインバンク担当 / 運用のプロ / 海外拠点', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば大企業のメインバンク担当として、会社の成長を資金で支えている。", "[haruki] あるいは運用のプロとして、多くの人の資産を預かって動かしている。", "[nana] お金を通じて、人や会社の成長に立ち会えるんだ。いい十年後だね。"]', 'H_丸の内・大手町の金融ビル群', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__finance', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__finance/panel_10.png', 'both', '[haruki] お金を、貸して、つないで、守る。金融はその全部で経済と人の成長を支える。
[nana] 口座をつくった小さな一歩の先に、こんな大きな流れがあったんだ。
[both] お金を動かし、人と会社の成長を支える。それが、金融。', 'お金を動かし、成長を支える。', '貸す・つなぐ・守るで経済を回す業界', NULL, '["[haruki] お金を、貸して、つないで、守る。金融はその全部で経済と人の成長を支える。", "[nana] 口座をつくった小さな一歩の先に、こんな大きな流れがあったんだ。", "[both] お金を動かし、人と会社の成長を支える。それが、金融。"]', 'H_ATM・店舗ネットワーク(メガバンク)', NULL);

-- ===== industry_10koma__consulting (コンサル) =====
-- source: output/industry_10koma__consulting/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__consulting', 'コンサル', 'consulting', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_01.png', 'nana', '[nana] この棚、コンサル出身の人が書いた本ばっかりだね。
[haruki] うん。マッキンゼーを冠した本だけで、日本語で三百冊近くあると言われてる。
[nana] でも、コンサルって普段どんな仕事してるのか、正直よく分からない。
[haruki] じゃあ、この棚から入ってみよう。実は身近なところに接点があるんだ。', 'この本棚、ぜんぶコンサル発', 'コンサル / 見えにくいけど身近', NULL, '["[nana] この棚、コンサル出身の人が書いた本ばっかりだね。", "[haruki] うん。マッキンゼーを冠した本だけで、日本語で三百冊近くあると言われてる。", "[nana] でも、コンサルって普段どんな仕事してるのか、正直よく分からない。", "[haruki] じゃあ、この棚から入ってみよう。実は身近なところに接点があるんだ。"]', 'H_書店のビジネス書コーナー(マッキンゼー本)', '{"location": "棚差しの本の背表紙", "object_type": "ビジネス書", "brand_form": "経営・思考法の書籍が並ぶ棚、抽象的な背表紙", "attachment": "書棚に配架", "scale_note": "実在の書店棚と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_02.png', 'haruki', '[haruki] この四象限のマトリクス、経営の授業で習わなかった?
[nana] 習った。事業をこの図で仕分けするやつだよね。
[haruki] あれはBCGが考えた枠組み。7Sもマッキンゼー発。世界の経営の共通言語になってる。
[nana] 気づかないうちに、コンサルの考え方を使って学んでたんだ。', '授業で習うあの図も、コンサル発', 'BCGの成長・シェアマトリクス / マッキンゼー7S', '各社 公式・沿革', '["[haruki] この四象限のマトリクス、経営の授業で習わなかった?", "[nana] 習った。事業をこの図で仕分けするやつだよね。", "[haruki] あれはBCGが考えた枠組み。7Sもマッキンゼー発。世界の経営の共通言語になってる。", "[nana] 気づかないうちに、コンサルの考え方を使って学んでたんだ。"]', 'H_フレームワーク図(BCGマトリクス・7S)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_03.png', 'nana', '[nana] じゃあ、コンサルは何で稼いでるの?
[haruki] 企業が自分たちだけでは解けない、一番難しい課題を、外から解いて対価をもらう。
[haruki] 戦略を描くだけの会社もあれば、実行や運用まで一緒にやる会社もある。
[nana] 答えのない問いに、外から答えを出すのが仕事なんだ。', '企業の最難関の課題を、外から解く', '戦略の立案から、実行・運用まで', NULL, '["[nana] じゃあ、コンサルは何で稼いでるの?", "[haruki] 企業が自分たちだけでは解けない、一番難しい課題を、外から解いて対価をもらう。", "[haruki] 戦略を描くだけの会社もあれば、実行や運用まで一緒にやる会社もある。", "[nana] 答えのない問いに、外から答えを出すのが仕事なんだ。"]', 'H_プロジェクトルームのホワイトボード', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_04.png', 'haruki', '[haruki] 大阪・関西万博のICT計画も、アクセンチュアが受け持った仕事だよ。
[nana] あんな大きなイベントの裏側にもいるんだ。
[haruki] BCGは百貨店のデジタル戦略、マッキンゼーは国内トップ企業の多くを支えてる。
[nana] 表には名前が出ないけど、社会のいろんな決め事に関わってるんだね。', '万博も、百貨店の変革も、裏側にいる', '表に名は出ないが社会の決め事を支える', '各社 公式・事例', '["[haruki] 大阪・関西万博のICT計画も、アクセンチュアが受け持った仕事だよ。", "[nana] あんな大きなイベントの裏側にもいるんだ。", "[haruki] BCGは百貨店のデジタル戦略、マッキンゼーは国内トップ企業の多くを支えてる。", "[nana] 表には名前が出ないけど、社会のいろんな決め事に関わってるんだね。"]', 'H_赤坂の総合コンサル本社ビル(アクセンチュア)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_05.png', 'nana', '[nana] コンサルも給料が高いって聞くけど、なんで若手から高いの?
[haruki] 高い水準だと言われるけど、外資系は非上場で有報がなくて、確かな平均額は公表されてないんだ。
[haruki] 額そのものより、課題を解いた付加価値をそのまま対価にする仕事、というのが本質だよ。
[nana] 年次で上がるより、生んだ価値がそのまま返ってくる構造なんだ。', '若手から高いのは、付加価値を売るから', '付加価値を対価にする / 外資系は非上場で平均額は非公表', 'Source-or-Silence: 有報のない非上場のため額は非提示', '["[nana] コンサルも給料が高いって聞くけど、なんで若手から高いの?", "[haruki] 高い水準だと言われるけど、外資系は非上場で有報がなくて、確かな平均額は公表されてないんだ。", "[haruki] 額そのものより、課題を解いた付加価値をそのまま対価にする仕事、というのが本質だよ。", "[nana] 年次で上がるより、生んだ価値がそのまま返ってくる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_06.png', 'haruki', '[haruki] プロジェクトごとに、担当する業界も課題も毎回変わる。
[nana] 同じ仕事の繰り返しじゃないんだ。刺激はありそう。
[haruki] その分、密度は高い。数年で事業会社や起業へ卒業していく人も多い。
[nana] 短くても濃く成長して、次へ進む。そういう働き方なんだね。', '毎回、業界も課題も変わる高密度', '卒業・転職が前提のキャリア', NULL, '["[haruki] プロジェクトごとに、担当する業界も課題も毎回変わる。", "[nana] 同じ仕事の繰り返しじゃないんだ。刺激はありそう。", "[haruki] その分、密度は高い。数年で事業会社や起業へ卒業していく人も多い。", "[nana] 短くても濃く成長して、次へ進む。そういう働き方なんだね。"]', 'H_夜のプロジェクトルーム', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_07.png', 'nana', '[nana] 人気の業界だし、採用はかなり狭き門なんでしょ?
[haruki] 狭き門だけど、見られるのは学歴の点数より、その場で考え抜けるか。
[haruki] ケース面接で、答えのない問いに筋道を立てられるか。本質を深く洞察できるかを問う。
[nana] 覚えた知識じゃなくて、目の前で考える力を見てるんだ。', '見るのは、その場で考え抜けるか', 'ケース面接 / 本質を洞察する力・成長力', NULL, '["[nana] 人気の業界だし、採用はかなり狭き門なんでしょ?", "[haruki] 狭き門だけど、見られるのは学歴の点数より、その場で考え抜けるか。", "[haruki] ケース面接で、答えのない問いに筋道を立てられるか。本質を深く洞察できるかを問う。", "[nana] 覚えた知識じゃなくて、目の前で考える力を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_08.png', 'nana', '[nana] 考えるのが仕事なら、資料を作って終わりじゃないの?
[haruki] 今はそこから先が広い。BCGはエンジニアを数千人規模で集めて、実装まで一緒にやる。
[nana] 戦略を描くだけじゃなくて、動くところまで面倒を見るんだ。
[haruki] 考える力と作る力を、一つの集団に束ねられる。それが今のコンサルの強みだよ。', '考える力と、作る力を一つに', '戦略から実装まで束ねる(BCG X 等)', '各社 公式・組織紹介', '["[nana] 考えるのが仕事なら、資料を作って終わりじゃないの?", "[haruki] 今はそこから先が広い。BCGはエンジニアを数千人規模で集めて、実装まで一緒にやる。", "[nana] 戦略を描くだけじゃなくて、動くところまで面倒を見るんだ。", "[haruki] 考える力と作る力を、一つの集団に束ねられる。それが今のコンサルの強みだよ。"]', 'H_デジタルラボ(BCG X)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどこにいると思う?
[haruki] たとえば事業会社の経営企画で、会社の舵を内側から取っている。
[haruki] あるいは自分で起業している。コンサル出身の経営者はとても多い。
[nana] 解く力を持って、どこへでも動ける。そういう十年後なんだね。', '10年後、たとえばこんな進路', '事業会社の経営 / 起業 / コンサルのパートナー', NULL, '["[nana] もし入れたら、十年後はどこにいると思う?", "[haruki] たとえば事業会社の経営企画で、会社の舵を内側から取っている。", "[haruki] あるいは自分で起業している。コンサル出身の経営者はとても多い。", "[nana] 解く力を持って、どこへでも動ける。そういう十年後なんだね。"]', 'H_フレームワーク図(BCGマトリクス・7S)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__consulting', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__consulting/panel_10.png', 'both', '[haruki] 企業が自分では解けない問いを、外から一緒に解く。それがコンサルの仕事。
[nana] 見えないところで、こんなに世の中の決め事に関わってたんだ。
[both] 答えのない問いに、外から答えを出す。それが、コンサル。', '答えのない問いに、外から答えを。', '最難関の課題を解いて対価を得る業界', NULL, '["[haruki] 企業が自分では解けない問いを、外から一緒に解く。それがコンサルの仕事。", "[nana] 見えないところで、こんなに世の中の決め事に関わってたんだ。", "[both] 答えのない問いに、外から答えを出す。それが、コンサル。"]', 'H_書店のビジネス書コーナー(マッキンゼー本)', NULL);

-- ===== industry_10koma__ad-media (広告・メディア) =====
-- source: output/industry_10koma__ad-media/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__ad-media', '広告・メディア', 'advertising_media', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_01.png', 'nana', '[nana] こういう広告を見てると、たまに、こんな未来だったらいいなって思うことある。
[haruki] その、まだない未来を人々の心に描いて、実現まで動かすのが広告メディアなんだ。
[nana] 広告って、モノを売るだけじゃないの?
[haruki] うん。ありたい未来から逆算して考えると、この業界の正体が見えるよ。', 'まだない未来を、人々の心に描く', '広告・メディア / 未来から逆算する仕事', NULL, '["[nana] こういう広告を見てると、たまに、こんな未来だったらいいなって思うことある。", "[haruki] その、まだない未来を人々の心に描いて、実現まで動かすのが広告メディアなんだ。", "[nana] 広告って、モノを売るだけじゃないの?", "[haruki] うん。ありたい未来から逆算して考えると、この業界の正体が見えるよ。"]', 'H_街頭の大型ビジョン・CM', '{"location": "ビルの壁面", "object_type": "大型ビジョン", "brand_form": "交差点の大型LEDビジョン、抽象的な映像", "attachment": "ビル外壁に設置", "scale_note": "実在の街頭ビジョンと同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_02.png', 'haruki', '[haruki] 未来を動かすには、まず人の心をつかむアイデアがいる。
[haruki] 電通は東京の大きな国際大会の開閉会式を演出して、日本の姿を世界に届けた。
[nana] あの大舞台の演出も、広告会社の仕事だったんだ。
[nana] アイデア一つで、世界中の人の心が動くってすごいね。', '未来を動かすのは、人の心をつかむアイデア', '電通=国際大会の開閉会式を演出', '電通 公式・実績', '["[haruki] 未来を動かすには、まず人の心をつかむアイデアがいる。", "[haruki] 電通は東京の大きな国際大会の開閉会式を演出して、日本の姿を世界に届けた。", "[nana] あの大舞台の演出も、広告会社の仕事だったんだ。", "[nana] アイデア一つで、世界中の人の心が動くってすごいね。"]', 'H_大型イベントの演出(電通の五輪演出)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_03.png', 'nana', '[nana] それで、どうやって稼いでるの?
[haruki] 企業や社会のメッセージを、生活者の心に届けて、行動を動かす。その対価を広告主からもらう。
[haruki] テレビCMも、イベントも、ネットの広告も、全部そのための道具なんだ。
[nana] 人の気持ちを動かすことが、そのまま仕事になるんだ。', '心と行動を動かして、対価を得る', 'CM・イベント・デジタルは届けるための道具', NULL, '["[nana] それで、どうやって稼いでるの?", "[haruki] 企業や社会のメッセージを、生活者の心に届けて、行動を動かす。その対価を広告主からもらう。", "[haruki] テレビCMも、イベントも、ネットの広告も、全部そのための道具なんだ。", "[nana] 人の気持ちを動かすことが、そのまま仕事になるんだ。"]', 'H_CM制作の現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_04.png', 'haruki', '[haruki] 人を動かすには、まず人を深く知ること。博報堂は生活総合研究所で暮らしを研究してきた。
[nana] どんな未来を望んでるか、先に理解するんだ。
[haruki] その生活者発想から、世界一の広告賞を二度も受けたアイデアが生まれた。
[nana] 人を知る力が、心に届くアイデアの源なんだね。', '人を深く知ることが、アイデアの源', '博報堂=生活者発想 / 世界的な広告賞を受賞', '博報堂DY 公式・沿革', '["[haruki] 人を動かすには、まず人を深く知ること。博報堂は生活総合研究所で暮らしを研究してきた。", "[nana] どんな未来を望んでるか、先に理解するんだ。", "[haruki] その生活者発想から、世界一の広告賞を二度も受けたアイデアが生まれた。", "[nana] 人を知る力が、心に届くアイデアの源なんだね。"]', 'H_生活総合研究所とカンヌのトロフィー(博報堂)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_05.png', 'nana', '[nana] 華やかそうだけど、お給料はどうなの?
[haruki] 電通は平均約千六百万円、博報堂は約千九十万円だよ。
[haruki] 高いのは、心を動かすアイデアと、それを本当に形にする実現力に価値があるから。
[nana] 思いつくだけじゃなく、実現まで持っていく力にお金がつくんだ。', '高いのは、アイデアと実現力の付加価値', '平均年収 電通約1,596万 / 博報堂約1,092万', '各社 有価証券報告書等(2025年3月・12月期)', '["[nana] 華やかそうだけど、お給料はどうなの?", "[haruki] 電通は平均約千六百万円、博報堂は約千九十万円だよ。", "[haruki] 高いのは、心を動かすアイデアと、それを本当に形にする実現力に価値があるから。", "[nana] 思いつくだけじゃなく、実現まで持っていく力にお金がつくんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_06.png', 'haruki', '[haruki] 仕事は、クリエイティブ、プランナー、営業、デジタルと分かれてる。
[nana] 華やかに見えて、大変そうな気もする。
[haruki] 締切と向き合う高い稼働もあるし、最後は一人ひとりの個性の勝負になる。
[nana] 楽じゃないけど、自分の色で勝負できる仕事なんだね。', '締切と高稼働、最後は個性の勝負', 'クリエイティブ / プランナー / 営業 / デジタル', NULL, '["[haruki] 仕事は、クリエイティブ、プランナー、営業、デジタルと分かれてる。", "[nana] 華やかに見えて、大変そうな気もする。", "[haruki] 締切と向き合う高い稼働もあるし、最後は一人ひとりの個性の勝負になる。", "[nana] 楽じゃないけど、自分の色で勝負できる仕事なんだね。"]', 'H_深夜の制作スタジオ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_07.png', 'nana', '[nana] 人気の業界だし、採用はやっぱり狭き門なんでしょ?
[haruki] 狭き門だけど、見られるのは肩書きより、他にないアイデアと、それを形にする力。
[haruki] 電通はアイデアと実現力、そして好奇心。博報堂は個性がぶつかって生まれるものを大事にする。
[nana] 覚えた正解じゃなくて、その人らしい発想を見てるんだ。', '見るのは、他にないアイデアと実現する力', 'アイデア×実現力・好奇心 / 生活者発想', NULL, '["[nana] 人気の業界だし、採用はやっぱり狭き門なんでしょ?", "[haruki] 狭き門だけど、見られるのは肩書きより、他にないアイデアと、それを形にする力。", "[haruki] 電通はアイデアと実現力、そして好奇心。博報堂は個性がぶつかって生まれるものを大事にする。", "[nana] 覚えた正解じゃなくて、その人らしい発想を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_08.png', 'nana', '[nana] この業界の、一番の強みって何なの?
[haruki] まだ世の中にない未来を、アイデアで形にして、たくさんの人に広められること。
[haruki] 電通も博報堂も、百年以上前からずっと、その力で時代の空気を作ってきた。
[nana] 目に見えない未来を、目に見える形にして届けるんだ。', 'まだない未来を、形にして広める', '百年以上、時代の空気をつくってきた', '各社 公式・沿革', '["[nana] この業界の、一番の強みって何なの?", "[haruki] まだ世の中にない未来を、アイデアで形にして、たくさんの人に広められること。", "[haruki] 電通も博報堂も、百年以上前からずっと、その力で時代の空気を作ってきた。", "[nana] 目に見えない未来を、目に見える形にして届けるんだ。"]', 'H_創業の歴史(電通1901・博報堂1895)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば世界に届くキャンペーンを作っている。あるいは新しいメディアを立ち上げている。
[haruki] あるいは、社会を動かす大きなイベントを仕切っている。
[nana] 自分のアイデアが、時代の空気を作るんだ。わくわくするね。', '10年後、たとえばこんな到達点', '世界に届くキャンペーン / 新しいメディア / 社会を動かすイベント', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば世界に届くキャンペーンを作っている。あるいは新しいメディアを立ち上げている。", "[haruki] あるいは、社会を動かす大きなイベントを仕切っている。", "[nana] 自分のアイデアが、時代の空気を作るんだ。わくわくするね。"]', 'H_大型イベントの演出(電通の五輪演出)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__ad-media', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__ad-media/panel_10.png', 'both', '[haruki] ありたい未来から逆算して、アイデアで形にして、みんなの心に届ける。それが広告メディア。
[nana] モノを売るだけじゃなくて、未来そのものを作ってたんだ。
[both] まだない未来を、みんなの心に。それが、広告・メディア。', 'まだない未来を、みんなの心に。', '心を動かして未来を実現する業界', NULL, '["[haruki] ありたい未来から逆算して、アイデアで形にして、みんなの心に届ける。それが広告メディア。", "[nana] モノを売るだけじゃなくて、未来そのものを作ってたんだ。", "[both] まだない未来を、みんなの心に。それが、広告・メディア。"]', 'H_街頭の大型ビジョン・CM', NULL);

-- ===== industry_10koma__infra-energy (インフラ・エネルギー) =====
-- source: output/industry_10koma__infra-energy/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__infra-energy', 'インフラ・エネルギー', 'infra_energy', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_01.png', 'nana', '[nana] 電気とガスって、当たり前すぎて、業界としては退屈じゃない?
[haruki] その当たり前を、一秒も止めないこと。実はいちばん難しい仕事なんだ。
[nana] 止めないだけなら、地味な安定産業でしょ?
[haruki] それがね、今この業界は、大きく変わってる最中なんだ。順番に解いていこう。', '当たり前を止めないのが、いちばん難しい', 'インフラ・エネルギー / 安定と変革の業界', NULL, '["[nana] 電気とガスって、当たり前すぎて、業界としては退屈じゃない?", "[haruki] その当たり前を、一秒も止めないこと。実はいちばん難しい仕事なんだ。", "[nana] 止めないだけなら、地味な安定産業でしょ?", "[haruki] それがね、今この業界は、大きく変わってる最中なんだ。順番に解いていこう。"]', 'H_都市ガスの青い炎(東京ガス)', '{"location": "コンロの中央", "object_type": "ガスの炎", "brand_form": "都市ガスの青いリング状の炎", "attachment": "コンロのバーナー", "scale_note": "実在のコンロの炎と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_02.png', 'haruki', '[haruki] エネルギーは、作って、運んで、届ける。この三つで社会の土台になってる。
[nana] 発電して、送って、家に届く。その全部が仕事なんだ。
[haruki] 東京電力は関東の広い地域に電気を送り、ENEOSは全国に約一万三千のスタンドを持つ。
[nana] 見えてる炎の裏に、こんなに大きな仕組みがあったんだ。', '作って、運んで、届ける巨大インフラ', '東京電力=関東広域 / ENEOS=全国約13,000のスタンド', '各社 公式・会社概要', '["[haruki] エネルギーは、作って、運んで、届ける。この三つで社会の土台になってる。", "[nana] 発電して、送って、家に届く。その全部が仕事なんだ。", "[haruki] 東京電力は関東の広い地域に電気を送り、ENEOSは全国に約一万三千のスタンドを持つ。", "[nana] 見えてる炎の裏に、こんなに大きな仕組みがあったんだ。"]', 'H_送電鉄塔と送電線(東京電力)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_03.png', 'nana', '[nana] でも、やってることは昔から変わらないんでしょ?
[haruki] そこが誤解。ENEOSは国内で初めて水素のスタンドを開いて、太陽光にも広げてる。
[haruki] 東京電力は全国に百六十カ所以上の水力を持ち、再エネの土台も厚い。
[nana] 石油や電気の会社が、脱炭素の最前線に立ってるんだ。', '古い産業が、脱炭素の最前線に', 'ENEOS=国内初の水素ステーション / 東京電力=水力160カ所以上', '各社 公式・事業紹介', '["[nana] でも、やってることは昔から変わらないんでしょ?", "[haruki] そこが誤解。ENEOSは国内で初めて水素のスタンドを開いて、太陽光にも広げてる。", "[haruki] 東京電力は全国に百六十カ所以上の水力を持ち、再エネの土台も厚い。", "[nana] 石油や電気の会社が、脱炭素の最前線に立ってるんだ。"]', 'H_水素ステーション・メガソーラー(ENEOS)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_04.png', 'haruki', '[haruki] さっきの青い炎は、東京ガスが海外から運んだ天然ガスが元になってる。
[nana] あの炎、海を越えてきたんだ。
[haruki] 東京ガスは、渋沢栄一が明治時代に始めた会社で、今も都市の暮らしを支えてる。
[nana] 百年以上前の仕事が、今日の私のコンロにつながってるんだね。', '海を越えた天然ガスが、青い炎になる', '東京ガス=渋沢栄一が創業 / LNGを海外から供給', '東京ガス 公式・沿革', '["[haruki] さっきの青い炎は、東京ガスが海外から運んだ天然ガスが元になってる。", "[nana] あの炎、海を越えてきたんだ。", "[haruki] 東京ガスは、渋沢栄一が明治時代に始めた会社で、今も都市の暮らしを支えてる。", "[nana] 百年以上前の仕事が、今日の私のコンロにつながってるんだね。"]', 'H_LNG基地とタンカー(東京ガス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_05.png', 'nana', '[nana] 安定してる分、お給料は控えめなの?
[haruki] ENEOSは平均約千七十万円、東京電力は約八百六十万円、東京ガスは約七百六十万円だよ。
[haruki] 派手じゃないけど、社会を止めない責任と長く働ける安定が、そのまま年収の土台になってる。
[nana] 目立たないけど、揺るがない。そういう構造なんだ。', '派手じゃないが揺るがない、安定の構造', '平均年収 ENEOS約1,069万 / 東京電力約860万 / 東京ガス約765万', '各社 有価証券報告書等(2025年3月期)', '["[nana] 安定してる分、お給料は控えめなの?", "[haruki] ENEOSは平均約千七十万円、東京電力は約八百六十万円、東京ガスは約七百六十万円だよ。", "[haruki] 派手じゃないけど、社会を止めない責任と長く働ける安定が、そのまま年収の土台になってる。", "[nana] 目立たないけど、揺るがない。そういう構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_06.png', 'haruki', '[haruki] 働き方は大きく二つ。設備や保安、系統を担う技術系と、事業を回す事務系。
[nana] 理系と文系で、役割が分かれるんだ。
[haruki] 地域に根ざす仕事だから転勤もあるけど、その分、長く働き続ける人が多い。
[nana] 腰を据えて、地域と一緒に生きていく働き方なんだね。', '技術系と事務系、地域に根ざす働き方', '設備・保安・系統 / 転勤あり・長く働ける', NULL, '["[haruki] 働き方は大きく二つ。設備や保安、系統を担う技術系と、事業を回す事務系。", "[nana] 理系と文系で、役割が分かれるんだ。", "[haruki] 地域に根ざす仕事だから転勤もあるけど、その分、長く働き続ける人が多い。", "[nana] 腰を据えて、地域と一緒に生きていく働き方なんだね。"]', 'H_発電所・供給現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_07.png', 'nana', '[nana] 人気で安定してる業界だし、採用は厳しいんでしょ?
[haruki] 厳しいけど、見られるのは点数より、自ら考えて挑み続けられるか。
[haruki] 東京電力は自律心と情熱と多様性、ENEOSは挑戦と向上心、東京ガスは挑み続ける姿勢を問う。
[nana] 安定を守るだけじゃなく、変化に挑める人を求めてるんだ。', '見るのは、自ら挑み続けられるか', '自律心・情熱・多様性 / 挑戦・向上心', NULL, '["[nana] 人気で安定してる業界だし、採用は厳しいんでしょ?", "[haruki] 厳しいけど、見られるのは点数より、自ら考えて挑み続けられるか。", "[haruki] 東京電力は自律心と情熱と多様性、ENEOSは挑戦と向上心、東京ガスは挑み続ける姿勢を問う。", "[nana] 安定を守るだけじゃなく、変化に挑める人を求めてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_08.png', 'nana', '[nana] 結局、この業界の一番の強みって何なの?
[haruki] 生活を一秒も止めない安定と、脱炭素という次の百年への挑戦が、同じ会社の中にあること。
[haruki] EVの充電網も、再エネも、この業界が広げてる。守りながら、変えていくんだ。
[nana] 揺るがない土台の上で、未来を作る。それが強さなんだね。', '止めない安定と、次の百年への挑戦', 'EV充電網・再エネを広げる', '各社 公式・事業紹介', '["[nana] 結局、この業界の一番の強みって何なの?", "[haruki] 生活を一秒も止めない安定と、脱炭素という次の百年への挑戦が、同じ会社の中にあること。", "[haruki] EVの充電網も、再エネも、この業界が広げてる。守りながら、変えていくんだ。", "[nana] 揺るがない土台の上で、未来を作る。それが強さなんだね。"]', 'H_EV充電ステーション', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば再エネの発電所を動かしている。あるいは水素の新しい事業を立ち上げている。
[haruki] あるいは街全体のエネルギーの使い方を設計している。
[nana] 毎日の当たり前を守りながら、未来のエネルギーを作るんだ。', '10年後、たとえばこんな現場', '再エネ発電所の運営 / 水素の新事業 / 街のエネルギー設計', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば再エネの発電所を動かしている。あるいは水素の新しい事業を立ち上げている。", "[haruki] あるいは街全体のエネルギーの使い方を設計している。", "[nana] 毎日の当たり前を守りながら、未来のエネルギーを作るんだ。"]', 'H_水素ステーション・メガソーラー(ENEOS)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__infra-energy', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__infra-energy/panel_10.png', 'both', '[haruki] 当たり前を止めない。そのうえで、脱炭素という次の百年をつくる。それがこの業界。
[nana] 退屈な安定産業だと思ってたのは、変化に気づいてなかっただけだった。
[both] 当たり前を止めない。そして、次の百年をつくる。それが、インフラ・エネルギー。', '当たり前を止めず、次の百年をつくる。', '安定と変革が同居するエネルギー業界', NULL, '["[haruki] 当たり前を止めない。そのうえで、脱炭素という次の百年をつくる。それがこの業界。", "[nana] 退屈な安定産業だと思ってたのは、変化に気づいてなかっただけだった。", "[both] 当たり前を止めない。そして、次の百年をつくる。それが、インフラ・エネルギー。"]', 'H_都市ガスの青い炎(東京ガス)', NULL);

-- ===== industry_10koma__realestate-construction (不動産・建設) =====
-- source: output/industry_10koma__realestate-construction/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__realestate-construction', '不動産・建設', 'real_estate', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_01.png', 'nana', '[nana] この東京駅、レトロできれいだよね。
[haruki] これ、百年前の姿を建設会社がまるごと蘇らせたんだ。復原って言うんだよ。
[nana] 新しく建てるんじゃなくて、昔の姿を戻したの?
[haruki] うん。不動産と建設は、時間そのものを扱う業界なんだ。起源からたどってみよう。', '百年前の駅を、まるごと蘇らせた', '不動産・建設 / 時間を扱う業界', NULL, '["[nana] この東京駅、レトロできれいだよね。", "[haruki] これ、百年前の姿を建設会社がまるごと蘇らせたんだ。復原って言うんだよ。", "[nana] 新しく建てるんじゃなくて、昔の姿を戻したの?", "[haruki] うん。不動産と建設は、時間そのものを扱う業界なんだ。起源からたどってみよう。"]', 'H_東京駅丸の内駅舎(鹿島が復原)', '{"location": "駅舎全体", "object_type": "歴史的建造物", "brand_form": "赤レンガ造りの丸の内駅舎、ドーム屋根", "attachment": "駅舎そのもの", "scale_note": "実在の駅舎と同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_02.png', 'haruki', '[haruki] 三井不動産は、日本で初めての超高層ビルを一九六八年に建てた。
[nana] そんな昔から、高いビルがあったんだ。
[haruki] 三菱地所は明治の頃から丸の内を任され、この街を百年以上かけて育ててきた。
[nana] 私が歩いてる街そのものが、この業界の歴史なんだ。', '街の起点を、百年かけてつくってきた', '三井=日本初の超高層(1968) / 三菱地所=丸の内を明治から', '各社 公式・沿革', '["[haruki] 三井不動産は、日本で初めての超高層ビルを一九六八年に建てた。", "[nana] そんな昔から、高いビルがあったんだ。", "[haruki] 三菱地所は明治の頃から丸の内を任され、この街を百年以上かけて育ててきた。", "[nana] 私が歩いてる街そのものが、この業界の歴史なんだ。"]', 'H_霞が関ビル・丸ビル(日本の超高層の起源)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_03.png', 'nana', '[nana] 不動産と建設って、どう違うの?
[haruki] 不動産は街を企画して作り育てる側、建設は実際に建物を建てる側。二役なんだ。
[haruki] 三井や三菱地所が街を描き、鹿島のようなゼネコンが形にする。
[nana] 絵を描く人と、建てる人。二つがそろって街になるんだ。', '街を描く不動産、建物を建てる建設', 'デベロッパーとゼネコンの二役', NULL, '["[nana] 不動産と建設って、どう違うの?", "[haruki] 不動産は街を企画して作り育てる側、建設は実際に建物を建てる側。二役なんだ。", "[haruki] 三井や三菱地所が街を描き、鹿島のようなゼネコンが形にする。", "[nana] 絵を描く人と、建てる人。二つがそろって街になるんだ。"]', 'H_再開発の建設現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_04.png', 'haruki', '[haruki] 休みに行くショッピングモールや、待ち合わせに使う複合ビルも、この業界が作った街だよ。
[nana] ららぽーとも、ミッドタウンも?
[haruki] そう。三井が長い時間をかけて企画して、運営まで手がけてる。
[nana] 毎日なにげなく使う場所が、誰かの何年もの仕事だったんだ。', '毎日行く場所も、誰かの何年もの仕事', '商業施設・複合ビルの企画から運営まで', '三井不動産 公式・事業紹介', '["[haruki] 休みに行くショッピングモールや、待ち合わせに使う複合ビルも、この業界が作った街だよ。", "[nana] ららぽーとも、ミッドタウンも?", "[haruki] そう。三井が長い時間をかけて企画して、運営まで手がけてる。", "[nana] 毎日なにげなく使う場所が、誰かの何年もの仕事だったんだ。"]', 'H_ららぽーと・東京ミッドタウン(三井)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_05.png', 'nana', '[nana] 大きな建物を扱うと、お給料も大きいの?
[haruki] 三井不動産は平均約千七百五十万円、三菱地所は約千三百五十万円、鹿島は約千百八十万円だよ。
[haruki] 高いのは、土地と時間と、一つ数百億円規模の大型案件が価値になるから。
[nana] 額そのものより、動かす資産と時間の大きさが返ってくる構造なんだ。', '土地と時間、大型案件が価値になる構造', '平均年収 三井約1,756万 / 三菱地所約1,348万 / 鹿島約1,185万', '各社 有価証券報告書等(2025年3月期)', '["[nana] 大きな建物を扱うと、お給料も大きいの?", "[haruki] 三井不動産は平均約千七百五十万円、三菱地所は約千三百五十万円、鹿島は約千百八十万円だよ。", "[haruki] 高いのは、土地と時間と、一つ数百億円規模の大型案件が価値になるから。", "[nana] 額そのものより、動かす資産と時間の大きさが返ってくる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_06.png', 'haruki', '[haruki] 不動産は総合職で、用地の仕入れや企画、運営を担う。
[nana] 建設のほうは理系が多いって聞くけど。
[haruki] うん。ゼネコンは施工管理や構造設計といった理系の職種が中核で、現場は全国にある。
[nana] 文系も理系も、それぞれの入り口から街づくりに関われるんだね。', '不動産は総合職、建設は理系職が中核', '用地・企画・運営 / 施工管理・構造設計・全国の現場', NULL, '["[haruki] 不動産は総合職で、用地の仕入れや企画、運営を担う。", "[nana] 建設のほうは理系が多いって聞くけど。", "[haruki] うん。ゼネコンは施工管理や構造設計といった理系の職種が中核で、現場は全国にある。", "[nana] 文系も理系も、それぞれの入り口から街づくりに関われるんだね。"]', 'H_ゼネコンの施工現場(理系)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_07.png', 'nana', '[nana] 人気だし、採用はやっぱり狭き門なんでしょ?
[haruki] 狭き門だけど、見られるのは点数より、その人となり。
[haruki] 三井は人となりを大切にし、三菱地所は志を持ってまちづくりに挑む人、鹿島は責任感と意欲を見る。
[nana] 長く残るものを作るから、まず人としての芯を見てるんだ。', '見るのは、点数より人となりと志', '人となり / まちづくりへの志 / 責任感・意欲', NULL, '["[nana] 人気だし、採用はやっぱり狭き門なんでしょ?", "[haruki] 狭き門だけど、見られるのは点数より、その人となり。", "[haruki] 三井は人となりを大切にし、三菱地所は志を持ってまちづくりに挑む人、鹿島は責任感と意欲を見る。", "[nana] 長く残るものを作るから、まず人としての芯を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_08.png', 'nana', '[nana] 昔の建物を守るだけじゃなくて、新しいものも作るんだよね?
[haruki] そう。三菱地所は今、日本一の高さの超高層ビルを建ててる。
[haruki] 鹿島は百年をつくる会社を掲げてる。過去を受け継ぎながら、次の百年を作るんだ。
[nana] 残ってきたものの上に、これから残るものを積んでいくんだね。', '過去を受け継ぎ、次の百年をつくる', '日本一の超高層を建設中 / 100年をつくる会社', '各社 公式・事業紹介', '["[nana] 昔の建物を守るだけじゃなくて、新しいものも作るんだよね?", "[haruki] そう。三菱地所は今、日本一の高さの超高層ビルを建ててる。", "[haruki] 鹿島は百年をつくる会社を掲げてる。過去を受け継ぎながら、次の百年を作るんだ。", "[nana] 残ってきたものの上に、これから残るものを積んでいくんだね。"]', 'H_日本一の超高層ビル建設(三菱地所Torch Tower)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば新しい街の再開発を仕切っている。あるいは超高層の建設現場を任されている。
[haruki] あるいは、次の時代のまちづくりを設計している。
[nana] 自分の名前が、街に残るんだ。すごく大きな仕事だね。', '10年後、たとえばこんな現場', '街の再開発 / 超高層の建設 / 次世代のまちづくり設計', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば新しい街の再開発を仕切っている。あるいは超高層の建設現場を任されている。", "[haruki] あるいは、次の時代のまちづくりを設計している。", "[nana] 自分の名前が、街に残るんだ。すごく大きな仕事だね。"]', 'H_再開発の建設現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__realestate-construction', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__realestate-construction/panel_10.png', 'both', '[haruki] 街を描き、建物を建て、百年前を受け継いで、次の百年をつくる。それがこの業界。
[nana] 私が歩く街のぜんぶに、誰かの長い時間が積もってたんだ。
[both] 百年前を受け継ぎ、次の百年をつくる。それが、不動産・建設。', '次の百年を、つくる。', '街を作り育て、建物を建てる業界', NULL, '["[haruki] 街を描き、建物を建て、百年前を受け継いで、次の百年をつくる。それがこの業界。", "[nana] 私が歩く街のぜんぶに、誰かの長い時間が積もってたんだ。", "[both] 百年前を受け継ぎ、次の百年をつくる。それが、不動産・建設。"]', 'H_東京駅丸の内駅舎(鹿島が復原)', NULL);

-- ===== industry_10koma__retail (小売・流通) =====
-- source: output/industry_10koma__retail/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__retail', '小売・流通', 'retail', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_01.png', 'nana', '[nana] このインナー、あったかいのに安いよね。
[haruki] それ、ユニクロが企画から生産までぜんぶ自分でやって作ってるんだ。
[nana] え、お店って、仕入れて売るだけじゃないの?
[haruki] そこが小売の面白いところ。毎日使う一番身近な業界を、のぞいてみよう。', 'この服、自分で企画から作ってる', '小売・流通 / 一番身近な業界', NULL, '["[nana] このインナー、あったかいのに安いよね。", "[haruki] それ、ユニクロが企画から生産までぜんぶ自分でやって作ってるんだ。", "[nana] え、お店って、仕入れて売るだけじゃないの?", "[haruki] そこが小売の面白いところ。毎日使う一番身近な業界を、のぞいてみよう。"]', 'H_機能服とアパレル店(ユニクロ)', '{"location": "陳列棚の商品", "object_type": "機能性インナー", "brand_form": "たたまれた機能性インナー、シンプルなパッケージ", "attachment": "棚に陳列", "scale_note": "実在の売り場と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_02.png', 'haruki', '[haruki] 小売は生活のいちばん近くにいる。イオンは一年の営業収益が十兆円を超える。
[nana] 十兆円!? スーパーの集まりなのに?
[haruki] グループで働く人は六十万人以上。日本でも指折りの巨大な産業なんだ。
[nana] 毎日使ってるのに、規模を全然知らなかった。', '生活のいちばん近くに、10兆円の産業', 'イオン 営業収益 約10兆円 / グループ約62万人', 'イオン 2025年2月期・会社情報', '["[haruki] 小売は生活のいちばん近くにいる。イオンは一年の営業収益が十兆円を超える。", "[nana] 十兆円!? スーパーの集まりなのに?", "[haruki] グループで働く人は六十万人以上。日本でも指折りの巨大な産業なんだ。", "[nana] 毎日使ってるのに、規模を全然知らなかった。"]', 'H_大型ショッピングモール(イオン)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_03.png', 'nana', '[nana] 仕入れて売るのと、自分で作るのは、何が違うの?
[haruki] 稼ぎ方が二つあるんだ。いろんなメーカーから仕入れて売る流通と、自分で作って売るSPA。
[haruki] ユニクロはSPAだから、機能の高い服を、いい品質で安く届けられる。
[nana] 作るところから握ると、値段も品質も自分で決められるんだ。', '仕入れて売る流通と、作って売るSPA', 'SPA=企画・生産・販売を一貫', 'ファーストリテイリング 公式・事業紹介', '["[nana] 仕入れて売るのと、自分で作るのは、何が違うの?", "[haruki] 稼ぎ方が二つあるんだ。いろんなメーカーから仕入れて売る流通と、自分で作って売るSPA。", "[haruki] ユニクロはSPAだから、機能の高い服を、いい品質で安く届けられる。", "[nana] 作るところから握ると、値段も品質も自分で決められるんだ。"]', 'H_SPAの企画・生産現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_04.png', 'haruki', '[haruki] このスーパーの自社ブランドも、電子マネーも、コンビニも、実は同じイオングループ。
[nana] 買い物のあちこちが、ひとつの会社の中なんだ。
[haruki] 自分たちで企画したブランドを持つと、暮らしをまるごと支えられる。
[nana] 気づかないうちに、一日の買い物が同じグループを回ってた。', '毎日の買い物が、同じグループの中', '自社ブランド・電子マネー・コンビニまで', 'イオン 公式・事業紹介', '["[haruki] このスーパーの自社ブランドも、電子マネーも、コンビニも、実は同じイオングループ。", "[nana] 買い物のあちこちが、ひとつの会社の中なんだ。", "[haruki] 自分たちで企画したブランドを持つと、暮らしをまるごと支えられる。", "[nana] 気づかないうちに、一日の買い物が同じグループを回ってた。"]', 'H_プライベートブランドの棚(トップバリュ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_05.png', 'nana', '[nana] 身近な業界だけど、お給料はどうなの?
[haruki] ファーストリテイリングは平均約千二百五十万円、イオンは約九百五十万円だよ。
[haruki] 高いところは、作って売る仕組みと世界規模の販売という付加価値が返ってきてる。
[nana] 身近さと、仕組みの大きさは、別の話なんだ。', '規模と仕組みの付加価値が、年収の土台', '平均年収 ファーストリテイリング約1,251万 / イオン約947万', '各社 有価証券報告書等(2025年期)', '["[nana] 身近な業界だけど、お給料はどうなの?", "[haruki] ファーストリテイリングは平均約千二百五十万円、イオンは約九百五十万円だよ。", "[haruki] 高いところは、作って売る仕組みと世界規模の販売という付加価値が返ってきてる。", "[nana] 身近さと、仕組みの大きさは、別の話なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_06.png', 'haruki', '[haruki] 仕事は、店長、バイヤー、商品計画、ECと広い。多くはまず店舗の現場から始まる。
[nana] いきなり本部じゃなくて、お店からなんだ。
[haruki] 全国に店があるから転勤もあるし、土日に働くことも多い。
[nana] お客さんの近くで学んで、そこから道が広がるんだね。', '多くは店舗の現場から始まる', '店長・バイヤー・商品計画・EC / 転勤・土日勤務も', NULL, '["[haruki] 仕事は、店長、バイヤー、商品計画、ECと広い。多くはまず店舗の現場から始まる。", "[nana] いきなり本部じゃなくて、お店からなんだ。", "[haruki] 全国に店があるから転勤もあるし、土日に働くことも多い。", "[nana] お客さんの近くで学んで、そこから道が広がるんだね。"]', 'H_店舗の売り場の現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_07.png', 'nana', '[nana] 大きな会社だと、採用の基準はどんなところを見るの?
[haruki] 点数より、自分で課題を見つけて動けるか。イオンは自立心とお客様視点、そして誠実さを見る。
[haruki] ファーストリテイリングは、世界に通用する実力と、商売の原理原則を大事にする。
[nana] お客さんの近くで、自分から動ける人を求めてるんだ。', '見るのは、自分で動けるお客様視点', '自立心・お客様視点・誠実 / 実力と原理原則', NULL, '["[nana] 大きな会社だと、採用の基準はどんなところを見るの?", "[haruki] 点数より、自分で課題を見つけて動けるか。イオンは自立心とお客様視点、そして誠実さを見る。", "[haruki] ファーストリテイリングは、世界に通用する実力と、商売の原理原則を大事にする。", "[nana] お客さんの近くで、自分から動ける人を求めてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_08.png', 'nana', '[nana] 日本の小売って、国内だけの話じゃないんだ。
[haruki] ユニクロは世界に二千四百を超える店を持ってる。作る力を握ったから世界へ出られた。
[nana] 身近な服が、世界中で同じように売れてるんだ。
[haruki] 生活を支える力を、日本から世界へ広げられる。それが小売流通の強みだよ。', '作る力で、日本から世界へ広がる', 'ユニクロ 世界2,400超の店', 'ファーストリテイリング 公式・会社情報', '["[nana] 日本の小売って、国内だけの話じゃないんだ。", "[haruki] ユニクロは世界に二千四百を超える店を持ってる。作る力を握ったから世界へ出られた。", "[nana] 身近な服が、世界中で同じように売れてるんだ。", "[haruki] 生活を支える力を、日本から世界へ広げられる。それが小売流通の強みだよ。"]', 'H_世界の旗艦店', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば店を任される店長になっている。あるいは世界に売る商品のバイヤーをしている。
[haruki] あるいは、ネットの新しい買い物のかたちを作っている。
[nana] お客さんの毎日を、自分の手で良くできるんだ。', '10年後、たとえばこんな姿', '店を任される店長 / 世界に売るバイヤー / ECの新しい買い物', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば店を任される店長になっている。あるいは世界に売る商品のバイヤーをしている。", "[haruki] あるいは、ネットの新しい買い物のかたちを作っている。", "[nana] お客さんの毎日を、自分の手で良くできるんだ。"]', 'H_大型ショッピングモール(イオン)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__retail', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__retail/panel_10.png', 'both', '[haruki] 仕入れて売り、時には自分で作って売る。小売流通は、いちばん近くで暮らしを支える。
[nana] 毎日の買い物の裏に、こんな大きな仕組みがあったんだ。
[both] 作って、届けて、暮らしを支える。それが、小売・流通。', '作って、届けて、暮らしを支える。', '仕入れて売る／作って売るで生活を支える業界', NULL, '["[haruki] 仕入れて売り、時には自分で作って売る。小売流通は、いちばん近くで暮らしを支える。", "[nana] 毎日の買い物の裏に、こんな大きな仕組みがあったんだ。", "[both] 作って、届けて、暮らしを支える。それが、小売・流通。"]', 'H_機能服とアパレル店(ユニクロ)', NULL);

-- ===== industry_10koma__food-beverage (食品・飲料) =====
-- source: output/industry_10koma__food-beverage/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__food-beverage', '食品・飲料', 'food_beverage', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_01.png', 'nana', '[nana] 食品メーカーって、安定してるけど、業界としては地味じゃない?
[haruki] 地味?
[nana] うん。毎日のごはんは作ってるけど、なんだか華がない気がして。
[haruki] そのギョーザを作る味の素、実はスマホの中にもいるって言ったら驚く?', '食品メーカーって、地味?', '食品・飲料 / 安定だけじゃない武器', NULL, '["[nana] 食品メーカーって、安定してるけど、業界としては地味じゃない?", "[haruki] 地味?", "[nana] うん。毎日のごはんは作ってるけど、なんだか華がない気がして。", "[haruki] そのギョーザを作る味の素、実はスマホの中にもいるって言ったら驚く?"]', 'H_ほんだし・冷凍ギョーザ等の食品(味の素)', '{"location": "調理台の上", "object_type": "冷凍食品・だしのパック", "brand_form": "家庭用の冷凍ギョーザ袋と顆粒だしのパック", "attachment": "調理台に置く", "scale_note": "実在の商品と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_02.png', 'haruki', '[haruki] 味の素はうま味のアミノ酸研究から、半導体の絶縁材料を生み出した。
[haruki] その材料は、世界のパソコンやスマホの心臓で高いシェアを持ってる。
[nana] だしの会社が、半導体を支えてるの?
[haruki] うん。台所の技術が、最先端の電子部品につながってるんだ。', 'だしの技術が、半導体を支える', '味の素 アミノサイエンス→半導体絶縁材料で高シェア', '味の素 公式・事業紹介', '["[haruki] 味の素はうま味のアミノ酸研究から、半導体の絶縁材料を生み出した。", "[haruki] その材料は、世界のパソコンやスマホの心臓で高いシェアを持ってる。", "[nana] だしの会社が、半導体を支えてるの?", "[haruki] うん。台所の技術が、最先端の電子部品につながってるんだ。"]', 'H_半導体材料と研究開発(味の素アミノサイエンス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_03.png', 'nana', '[nana] でも普段は、やっぱり調味料の会社でしょ?
[haruki] その調味料が、毎日の食卓の味を科学で支えてる。だしも中華の素もスープも。
[nana] 言われてみれば、この棚のほとんど、名前を知ってる。
[haruki] 当たり前の一皿の裏に、何十年もの研究が積み重なってるんだ。', '毎日の一皿の裏に、何十年もの研究', 'だし / 合わせ調味料 / スープ', '味の素 公式・製品情報', '["[nana] でも普段は、やっぱり調味料の会社でしょ?", "[haruki] その調味料が、毎日の食卓の味を科学で支えてる。だしも中華の素もスープも。", "[nana] 言われてみれば、この棚のほとんど、名前を知ってる。", "[haruki] 当たり前の一皿の裏に、何十年もの研究が積み重なってるんだ。"]', 'H_スーパーの調味料棚', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_04.png', 'haruki', '[haruki] サントリーは山崎というウイスキーを、何十年もかけて世界一の評価まで育てた。
[nana] 何十年も? そんなに待つの?
[haruki] 食品と飲料は、ブランドが時間で強くなる。だから、やってみなはれで挑む。
[nana] すぐに結果が出なくても、長く育てる。それも一つの戦い方なんだ。', 'ブランドは、時間をかけて強くなる', '山崎を世界的評価へ / やってみなはれ', 'サントリー 公式・沿革', '["[haruki] サントリーは山崎というウイスキーを、何十年もかけて世界一の評価まで育てた。", "[nana] 何十年も? そんなに待つの?", "[haruki] 食品と飲料は、ブランドが時間で強くなる。だから、やってみなはれで挑む。", "[nana] すぐに結果が出なくても、長く育てる。それも一つの戦い方なんだ。"]', 'H_山崎蒸溜所(サントリー)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_05.png', 'nana', '[nana] でも安定してる分、お給料はほどほどなんじゃないの?
[haruki] 味の素は有報で平均約千万円、明治も約九百万円。サントリーは非上場で有報がないから額は伏せるね。
[haruki] 安定してるのに高いのは、研究とブランドという長く効く付加価値があるから。
[nana] 目立たないけど、中身は分厚いんだ。', '安定なのに高いのは、研究とブランドの厚み', '平均年収 味の素約1,037万 / 明治約910万(有報) ※サントリーHDは非上場で非提示', '味の素(2802)・明治HD(2269) 有価証券報告書(2025年3月期)', '["[nana] でも安定してる分、お給料はほどほどなんじゃないの?", "[haruki] 味の素は有報で平均約千万円、明治も約九百万円。サントリーは非上場で有報がないから額は伏せるね。", "[haruki] 安定してるのに高いのは、研究とブランドという長く効く付加価値があるから。", "[nana] 目立たないけど、中身は分厚いんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_06.png', 'haruki', '[haruki] 最初は営業配属が多くて、全国のどこかの地方に行くこともある。
[nana] いきなり地方勤務もあるんだ。
[haruki] 商品開発やマーケ、研究に進む道もある。理系なら研究や品質もある。
[nana] 入り口は営業でも、そこから道が広がるんだね。', '最初は営業配属、地方勤務も', '商品開発 / マーケ / 研究・品質へ広がる', NULL, '["[haruki] 最初は営業配属が多くて、全国のどこかの地方に行くこともある。", "[nana] いきなり地方勤務もあるんだ。", "[haruki] 商品開発やマーケ、研究に進む道もある。理系なら研究や品質もある。", "[nana] 入り口は営業でも、そこから道が広がるんだね。"]', 'H_地方の営業・工場現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_07.png', 'nana', '[nana] これだけ人気だと、採用はやっぱり厳しいんでしょ?
[haruki] 厳しいけど、味の素は求める人物像を敢えて決めず、多様な人を人財の雑木林と呼ぶ。
[haruki] サントリーはやってみなはれ、明治は情熱とやる気。挑む姿勢と個性を見てる。
[nana] 型にはめず、その人らしさで挑めるかを見てるんだ。', '見るのは、その人らしさと挑む姿勢', '人財の雑木林 / やってみなはれ / 情熱とやる気', NULL, '["[nana] これだけ人気だと、採用はやっぱり厳しいんでしょ?", "[haruki] 厳しいけど、味の素は求める人物像を敢えて決めず、多様な人を人財の雑木林と呼ぶ。", "[haruki] サントリーはやってみなはれ、明治は情熱とやる気。挑む姿勢と個性を見てる。", "[nana] 型にはめず、その人らしさで挑めるかを見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_08.png', 'nana', '[nana] このヨーグルトもチョコもプロテインも、ぜんぶ明治なんだ。
[haruki] 明治は食品と製薬の両輪で、食と健康を一緒に扱う。だから栄養にも強い。
[nana] おいしいだけじゃなくて、健康まで設計してるんだ。
[haruki] 毎日の当たり前を、味と健康の両面から支える。それが食品飲料の強みだよ。', 'おいしさと、健康を同時に設計', '明治=食品と製薬の両輪 / 健康にアイデアを', '明治 公式・事業紹介', '["[nana] このヨーグルトもチョコもプロテインも、ぜんぶ明治なんだ。", "[haruki] 明治は食品と製薬の両輪で、食と健康を一緒に扱う。だから栄養にも強い。", "[nana] おいしいだけじゃなくて、健康まで設計してるんだ。", "[haruki] 毎日の当たり前を、味と健康の両面から支える。それが食品飲料の強みだよ。"]', 'H_明治の乳製品・菓子・プロテイン', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば新しい味を生む研究をしている。あるいは海外で日本のブランドを育てている。
[haruki] あるいは食と健康をつなぐ新しい事業を立ち上げている。
[nana] 毎日の食卓の、その先を作るんだ。地味どころじゃないね。', '10年後、たとえばこんな場面', '新しい味の研究 / 海外でブランド育成 / 食と健康の新事業', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば新しい味を生む研究をしている。あるいは海外で日本のブランドを育てている。", "[haruki] あるいは食と健康をつなぐ新しい事業を立ち上げている。", "[nana] 毎日の食卓の、その先を作るんだ。地味どころじゃないね。"]', 'H_半導体材料と研究開発(味の素アミノサイエンス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__food-beverage', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__food-beverage/panel_10.png', 'both', '[haruki] 毎日の味を科学で支え、ブランドを長く育て、健康まで設計する。それが食品飲料。
[nana] 地味だと思ってたのは、奥深さに気づいてなかっただけだった。
[both] 地味じゃない、毎日の最先端。それが、食品・飲料。', '地味じゃない、毎日の最先端。', '研究とブランドで食卓を支える業界', NULL, '["[haruki] 毎日の味を科学で支え、ブランドを長く育て、健康まで設計する。それが食品飲料。", "[nana] 地味だと思ってたのは、奥深さに気づいてなかっただけだった。", "[both] 地味じゃない、毎日の最先端。それが、食品・飲料。"]', 'H_スーパーの調味料棚', NULL);

-- ===== industry_10koma__medical-healthcare (医療・ヘルスケア) =====
-- source: output/industry_10koma__medical-healthcare/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__medical-healthcare', '医療・ヘルスケア', 'pharma_healthcare', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_01.png', 'nana', '[nana] 体調を崩したとき、いつもお世話になるこの薬。
[haruki] その一錠の裏に、十年以上かけて誰かの体を守る研究があるんだ。
[nana] たった一錠に、そんなに時間が?
[haruki] うん。医療ヘルスケアは、人の命と健康そのものを支える業界だよ。', 'この一錠の裏に、10年以上の研究', '医療・ヘルスケア / 命と健康を支える業界', NULL, '["[nana] 体調を崩したとき、いつもお世話になるこの薬。", "[haruki] その一錠の裏に、十年以上かけて誰かの体を守る研究があるんだ。", "[nana] たった一錠に、そんなに時間が?", "[haruki] うん。医療ヘルスケアは、人の命と健康そのものを支える業界だよ。"]', 'H_家庭の常備薬(武田のアリナミン等)', '{"location": "棚の上", "object_type": "常備薬", "brand_form": "家庭の常備薬の箱、シンプルなパッケージ", "attachment": "棚に置く", "scale_note": "実在の薬箱と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_02.png', 'haruki', '[haruki] 武田薬品は、二百四十年以上続く日本最大の製薬会社。売上は四兆円を超える。
[nana] 薬の会社が、そんなに大きいんだ。
[haruki] 作った薬は、世界中の患者さんに届く。命に関わるから、責任もとても大きい。
[nana] 誰かの命を守ることが、そのまま仕事なんだ。', '命を守る仕事が、4兆円規模に', '武田=243年続く日本最大の製薬会社', '武田薬品 公式・会社情報', '["[haruki] 武田薬品は、二百四十年以上続く日本最大の製薬会社。売上は四兆円を超える。", "[nana] 薬の会社が、そんなに大きいんだ。", "[haruki] 作った薬は、世界中の患者さんに届く。命に関わるから、責任もとても大きい。", "[nana] 誰かの命を守ることが、そのまま仕事なんだ。"]', 'H_製薬のグローバル本社と研究(武田)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_03.png', 'nana', '[nana] どうやって稼いでるの?
[haruki] 効く薬を生むこと。一つの新薬に十年以上と、巨額の研究費をかける。
[haruki] アステラスの前立腺がんの薬は、世界中の患者さんの支えになってる。
[nana] 一つの薬が、世界の誰かの毎日を救ってるんだ。', '効く薬を生むことが、事業の核心', '一つの新薬に10年以上 / 世界の患者を支える', 'アステラス 公式・製品情報', '["[nana] どうやって稼いでるの?", "[haruki] 効く薬を生むこと。一つの新薬に十年以上と、巨額の研究費をかける。", "[haruki] アステラスの前立腺がんの薬は、世界中の患者さんの支えになってる。", "[nana] 一つの薬が、世界の誰かの毎日を救ってるんだ。"]', 'H_創薬の研究センター(アステラスつくば)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_04.png', 'haruki', '[haruki] 薬だけじゃない。エムスリーは医師三十万人をネットでつないでる。
[nana] お医者さんをつなぐと、何がいいの?
[haruki] 正しい情報が早く届いて、無駄な医療の費用も減る。医療そのものを良くしてるんだ。
[nana] 薬も、仕組みも、どっちも人の健康を支えてるんだね。', '薬だけでなく、医療そのものを良くする', 'エムスリー=医師30万人をつなぎ医療を効率化', 'エムスリー 公式・会社情報', '["[haruki] 薬だけじゃない。エムスリーは医師三十万人をネットでつないでる。", "[nana] お医者さんをつなぐと、何がいいの?", "[haruki] 正しい情報が早く届いて、無駄な医療の費用も減る。医療そのものを良くしてるんだ。", "[nana] 薬も、仕組みも、どっちも人の健康を支えてるんだね。"]', 'H_医療ポータルと電子カルテ(エムスリー)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_05.png', 'nana', '[nana] 命を扱う仕事だと、お給料はどうなの?
[haruki] 武田は平均約千百万円、アステラスは約千五十万円、エムスリーは約九百三十万円だよ。
[haruki] 高いのは、長い研究開発と、世界に届けるグローバルの力が価値になってるから。
[nana] 額そのものより、生み出す薬と世界への広がりが返ってくる構造なんだ。', '研究開発と世界展開の付加価値', '平均年収 武田約1,104万 / アステラス約1,046万 / エムスリー約931万', '各社 有価証券報告書等(2025年3月期)', '["[nana] 命を扱う仕事だと、お給料はどうなの?", "[haruki] 武田は平均約千百万円、アステラスは約千五十万円、エムスリーは約九百三十万円だよ。", "[haruki] 高いのは、長い研究開発と、世界に届けるグローバルの力が価値になってるから。", "[nana] 額そのものより、生み出す薬と世界への広がりが返ってくる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_06.png', 'haruki', '[haruki] 職種は広い。薬を生む研究、医療機関に情報を届けるMRの営業、開発、医療のIT。
[nana] 理系じゃないと難しい?
[haruki] 研究は理系中心だけど、営業や企画では文系も活躍する。海外との仕事も多い。
[nana] いろんな入り口から、人の健康に関われるんだね。', '研究・MR・開発・医療IT、海外との仕事も', '研究は理系中心 / 営業・企画は文系も活躍', NULL, '["[haruki] 職種は広い。薬を生む研究、医療機関に情報を届けるMRの営業、開発、医療のIT。", "[nana] 理系じゃないと難しい?", "[haruki] 研究は理系中心だけど、営業や企画では文系も活躍する。海外との仕事も多い。", "[nana] いろんな入り口から、人の健康に関われるんだね。"]', 'H_MR・研究の現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_07.png', 'nana', '[nana] 人気だし、採用は厳しいんでしょ?
[haruki] 厳しいけど、見られるのは点数より、誠実さと、患者さんのためという気持ち。
[haruki] 武田は誠実を軸に患者のため、アステラスは信頼関係を築いて課題を解ける人を大事にする。
[nana] 命を扱う仕事だから、まず人としての誠実さを見てるんだ。', '見るのは、誠実さと患者のための気持ち', '誠実・患者のため / 信頼関係を築き課題を解く', NULL, '["[nana] 人気だし、採用は厳しいんでしょ?", "[haruki] 厳しいけど、見られるのは点数より、誠実さと、患者さんのためという気持ち。", "[haruki] 武田は誠実を軸に患者のため、アステラスは信頼関係を築いて課題を解ける人を大事にする。", "[nana] 命を扱う仕事だから、まず人としての誠実さを見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_08.png', 'nana', '[nana] この業界の一番の強みって何なの?
[haruki] 一つの薬、一つの仕組みが、国境を越えて世界中の命を救えること。
[haruki] 武田はデング熱のワクチンなど、世界に必要な薬づくりにも挑んでる。
[nana] 目の前の一人から、世界の何百万人まで。届く広さがすごいんだ。', '一つの薬が、世界中の命を救う', '世界に必要なワクチン・薬づくりに挑む', '各社 公式・事業紹介', '["[nana] この業界の一番の強みって何なの?", "[haruki] 一つの薬、一つの仕組みが、国境を越えて世界中の命を救えること。", "[haruki] 武田はデング熱のワクチンなど、世界に必要な薬づくりにも挑んでる。", "[nana] 目の前の一人から、世界の何百万人まで。届く広さがすごいんだ。"]', 'H_ワクチンと世界の患者', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば新しい薬を生む研究をしている。あるいは世界に薬を届けている。
[haruki] あるいは、医療の仕組みをITで変えている。どれも、誰かの命と健康を支える仕事だよ。
[nana] 自分の仕事が、誰かの明日を守るんだ。', '10年後、たとえばこんな現場', '新薬の研究 / 世界に薬を届ける / 医療をITで変える', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば新しい薬を生む研究をしている。あるいは世界に薬を届けている。", "[haruki] あるいは、医療の仕組みをITで変えている。どれも、誰かの命と健康を支える仕事だよ。", "[nana] 自分の仕事が、誰かの明日を守るんだ。"]', 'H_創薬の研究センター(アステラスつくば)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__medical-healthcare', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__medical-healthcare/panel_10.png', 'both', '[haruki] 効く薬を生み、医療を良くして、人の命と健康を守り、延ばす。それが医療ヘルスケア。
[nana] 何気ない一錠の裏に、こんなに大きな意義があったんだ。
[both] 命と健康を、守り、延ばす。それが、医療・ヘルスケア。', '命と健康を、守り、延ばす。', '創薬と医療の仕組みで命を支える業界', NULL, '["[haruki] 効く薬を生み、医療を良くして、人の命と健康を守り、延ばす。それが医療ヘルスケア。", "[nana] 何気ない一錠の裏に、こんなに大きな意義があったんだ。", "[both] 命と健康を、守り、延ばす。それが、医療・ヘルスケア。"]', 'H_家庭の常備薬(武田のアリナミン等)', NULL);

-- ===== industry_10koma__transport-logistics (航空・運輸・物流) =====
-- source: output/industry_10koma__transport-logistics/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__transport-logistics', '航空・運輸・物流', 'transport_logistics', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_01.png', 'nana', '[nana] 毎朝のこれ、当たり前すぎて、考えたこともなかった。
[haruki] そのICカード、使ってる人は八千万人を超えてる。運輸物流の入口なんだよ。
[nana] 改札をタッチしただけで、業界の入口なの?
[haruki] うん。人とモノを運ぶこの業界、一番身近な接点からたどってみよう。', '毎朝のこのタッチ、使う人は8,000万人超', '航空・運輸・物流 / 一番身近な接点', NULL, '["[nana] 毎朝のこれ、当たり前すぎて、考えたこともなかった。", "[haruki] そのICカード、使ってる人は八千万人を超えてる。運輸物流の入口なんだよ。", "[nana] 改札をタッチしただけで、業界の入口なの?", "[haruki] うん。人とモノを運ぶこの業界、一番身近な接点からたどってみよう。"]', 'H_Suicaのタッチと改札(JR東日本)', '{"location": "改札機の読み取り部", "object_type": "ICカード改札", "brand_form": "ICカードをかざす自動改札機", "attachment": "改札に設置", "scale_note": "実在の改札と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_02.png', 'haruki', '[haruki] JR東日本は、一日におよそ千六百万人を運んでる。
[nana] 一日で、それだけの人が動いてるんだ。
[haruki] 駅の中のお店もホテルも、実は同じ会社。運ぶだけじゃなく、街も作ってる。
[nana] 毎日の移動の裏に、こんなに大きな仕事があったんだ。', '1日に、およそ1,600万人を運ぶ', 'JR東日本 / 駅の店もホテルも同じ会社', 'JR東日本 公式・会社情報', '["[haruki] JR東日本は、一日におよそ千六百万人を運んでる。", "[nana] 一日で、それだけの人が動いてるんだ。", "[haruki] 駅の中のお店もホテルも、実は同じ会社。運ぶだけじゃなく、街も作ってる。", "[nana] 毎日の移動の裏に、こんなに大きな仕事があったんだ。"]', 'H_新幹線はやぶさと駅(JR東日本)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_03.png', 'nana', '[nana] 鉄道のほかにも、いろいろあるんだよね?
[haruki] うん。人とモノを運ぶのがこの業界。鉄道、航空、海運の三つが柱なんだ。
[haruki] どれか一つでも止まると、生活も経済も止まってしまう。
[nana] 動いて当たり前の毎日を、支えてる仕事なんだ。', '人とモノを運んで、社会を動かす', '鉄道・航空・海運の三つの柱', NULL, '["[nana] 鉄道のほかにも、いろいろあるんだよね?", "[haruki] うん。人とモノを運ぶのがこの業界。鉄道、航空、海運の三つが柱なんだ。", "[haruki] どれか一つでも止まると、生活も経済も止まってしまう。", "[nana] 動いて当たり前の毎日を、支えてる仕事なんだ。"]', 'H_空港とコンテナヤード', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_04.png', 'haruki', '[haruki] 旅行で乗る飛行機はANAが日本最大の翼。海の向こうから届く荷物や車は、日本郵船が運んでる。
[nana] 私の旅も、通販で届く荷物も、この業界の中なんだ。
[haruki] 日本郵船は明治時代からずっと、世界の海でモノを運び続けてきた。
[nana] 空も海も、気づかないところでつながってたんだね。', '旅も、海を渡る荷物も、この業界の中', 'ANA=日本最大の翼 / 日本郵船=世界の海運', '各社 公式・会社情報', '["[haruki] 旅行で乗る飛行機はANAが日本最大の翼。海の向こうから届く荷物や車は、日本郵船が運んでる。", "[nana] 私の旅も、通販で届く荷物も、この業界の中なんだ。", "[haruki] 日本郵船は明治時代からずっと、世界の海でモノを運び続けてきた。", "[nana] 空も海も、気づかないところでつながってたんだね。"]', 'H_ANAの787旅客機とコンテナ船', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_05.png', 'nana', '[nana] 運ぶ仕事って、お給料はどうなんだろう。
[haruki] 日本郵船は平均約千四百万円、JR東日本は約七百七十万円、ANAは約七百三十万円だよ。
[haruki] 海運が高いのは、運ぶ規模が大きく、世界の市況で大きく動くから。専門性も要る。
[nana] 何を、どれだけ運ぶか。その規模と専門性が返ってくる構造なんだ。', '運ぶ規模と専門性が、年収の土台', '平均年収 日本郵船約1,435万 / JR東約767万 / ANA約730万', '各社 有価証券報告書等(2025年3月期)', '["[nana] 運ぶ仕事って、お給料はどうなんだろう。", "[haruki] 日本郵船は平均約千四百万円、JR東日本は約七百七十万円、ANAは約七百三十万円だよ。", "[haruki] 海運が高いのは、運ぶ規模が大きく、世界の市況で大きく動くから。専門性も要る。", "[nana] 何を、どれだけ運ぶか。その規模と専門性が返ってくる構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_06.png', 'haruki', '[haruki] 働き方は分野で違う。鉄道は現場から、航空は客室や地上、整備、総合職に分かれる。
[nana] 海運はどうなの?
[haruki] 陸で支える職と、船に乗る海上職がある。シフトや、地域をまたぐ勤務もある。
[nana] 現場を知って、運ぶを支える。いろんな入り口があるんだね。', '分野ごとに現場がある働き方', '鉄道の現場 / 航空の客室・地上・整備 / 海運の陸上職と海上職', NULL, '["[haruki] 働き方は分野で違う。鉄道は現場から、航空は客室や地上、整備、総合職に分かれる。", "[nana] 海運はどうなの?", "[haruki] 陸で支える職と、船に乗る海上職がある。シフトや、地域をまたぐ勤務もある。", "[nana] 現場を知って、運ぶを支える。いろんな入り口があるんだね。"]', 'H_運行・整備・物流の現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_07.png', 'nana', '[nana] 人気だし、採用の基準はどんなところを見るの?
[haruki] 点数より、姿勢を見る。JRは高い目標に挑み続けられるか。
[haruki] ANAは安全とお客様視点とチームの心、日本郵船は軸を持った幅広い人を大事にする。
[nana] 安全に運ぶ責任があるから、人柄とチームの力を見てるんだ。', '見るのは、挑む姿勢と安全・チームの心', '挑み続ける / 安全・お客様視点・チーム / 軸のあるジェネラリスト', NULL, '["[nana] 人気だし、採用の基準はどんなところを見るの?", "[haruki] 点数より、姿勢を見る。JRは高い目標に挑み続けられるか。", "[haruki] ANAは安全とお客様視点とチームの心、日本郵船は軸を持った幅広い人を大事にする。", "[nana] 安全に運ぶ責任があるから、人柄とチームの力を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_08.png', 'nana', '[nana] この業界の強みって、規模の大きさだけ?
[haruki] それだけじゃない。運ぶを止めないという誇りが、長い歴史で受け継がれてる。
[haruki] 日本郵船の船のマークは、坂本龍馬の海援隊の旗に由来してるんだ。
[nana] 幕末から今まで、運ぶ誇りがずっと続いてきたんだね。', '運ぶを止めない誇りが、歴史で受け継がれる', '日本郵船の船のマークは海援隊の旗に由来', '日本郵船 公式・沿革', '["[nana] この業界の強みって、規模の大きさだけ?", "[haruki] それだけじゃない。運ぶを止めないという誇りが、長い歴史で受け継がれてる。", "[haruki] 日本郵船の船のマークは、坂本龍馬の海援隊の旗に由来してるんだ。", "[nana] 幕末から今まで、運ぶ誇りがずっと続いてきたんだね。"]', 'H_港湾の船体と無地の煙突(運ぶ誇り)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば新しい駅や路線を作っている。あるいは世界の空をつなぐ運航を支えている。
[haruki] あるいは、海の物流を動かして世界にモノを届けている。
[nana] 人とモノの動きを、自分の手で支えるんだ。頼もしいね。', '10年後、たとえばこんな現場', '新しい駅や路線 / 世界の空をつなぐ / 海の物流を動かす', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば新しい駅や路線を作っている。あるいは世界の空をつなぐ運航を支えている。", "[haruki] あるいは、海の物流を動かして世界にモノを届けている。", "[nana] 人とモノの動きを、自分の手で支えるんだ。頼もしいね。"]', 'H_空港とコンテナヤード', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__transport-logistics', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__transport-logistics/panel_10.png', 'both', '[haruki] 人を運び、モノを運び、その動きを一秒も止めない。それが運輸物流。
[nana] 毎朝のタッチの先に、こんなに大きな仕事が続いてたんだ。
[both] 人とモノを、止めずに運ぶ。それが、航空・運輸・物流。', '人とモノを、止めずに運ぶ。', '鉄道・航空・海運で社会の動きを支える業界', NULL, '["[haruki] 人を運び、モノを運び、その動きを一秒も止めない。それが運輸物流。", "[nana] 毎朝のタッチの先に、こんなに大きな仕事が続いてたんだ。", "[both] 人とモノを、止めずに運ぶ。それが、航空・運輸・物流。"]', 'H_Suicaのタッチと改札(JR東日本)', NULL);

-- ===== industry_10koma__it-ai-saas-game (IT・AI・SaaS・ゲーム) =====
-- source: output/industry_10koma__it-ai-saas-game/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__it-ai-saas-game', 'IT・AI・SaaS・ゲーム', 'it_ai_saas_game', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_01.png', 'nana', '[nana] はい、スマホでピッと。これで支払い完了。
[haruki] その一瞬の裏で、月に十億件くらいを処理する決済システムが動いてる。
[nana] 十億件!? 私のこの一回も、その中の一つなの?
[haruki] そう。NTTデータのCAFISがずっと支えてる。数字で見ると、業界のすごさが分かるよ。', 'そのタッチ、裏で月に10億件', 'IT・AI・SaaS・ゲーム / 数字で動く業界', NULL, '["[nana] はい、スマホでピッと。これで支払い完了。", "[haruki] その一瞬の裏で、月に十億件くらいを処理する決済システムが動いてる。", "[nana] 十億件!? 私のこの一回も、その中の一つなの?", "[haruki] そう。NTTデータのCAFISがずっと支えてる。数字で見ると、業界のすごさが分かるよ。"]', 'H_レジのスマホ決済端末(NTTデータCAFIS)', '{"location": "レジ横の決済端末", "object_type": "決済端末", "brand_form": "カードやスマホをかざす決済端末", "attachment": "レジに設置", "scale_note": "実在の端末と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_02.png', 'haruki', '[haruki] フリマアプリのメルカリは、月に二千三百万人が使ってる。
[nana] それって、日本人の何人に一人って世界だよね。
[haruki] 出品された品は累計で三十億品を超える。全部、スマホひとつで動いてる。
[nana] 手のひらの中に、そんな大きな市場があったんだ。', 'スマホひとつに、月2,300万人の市場', 'メルカリ 累計出品30億品超', 'メルカリ 公式・会社情報', '["[haruki] フリマアプリのメルカリは、月に二千三百万人が使ってる。", "[nana] それって、日本人の何人に一人って世界だよね。", "[haruki] 出品された品は累計で三十億品を超える。全部、スマホひとつで動いてる。", "[nana] 手のひらの中に、そんな大きな市場があったんだ。"]', 'H_フリマアプリと発送段ボール(メルカリ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_03.png', 'nana', '[nana] でも、目に見えないのに、どうやって稼いでるの?
[haruki] ソフトウェアで人の行動を動かすんだ。決済も、売り買いも、遊びも。
[haruki] NTTデータの売上は四兆円を超える。目に見えない仕組みが、これだけの規模になる。
[nana] 形はないのに、世界を動かしてるんだ。', 'ソフトで、人の行動を動かして稼ぐ', 'NTTデータ 売上 約4兆6,387億円', 'NTTデータ 2025年3月期・決算', '["[nana] でも、目に見えないのに、どうやって稼いでるの?", "[haruki] ソフトウェアで人の行動を動かすんだ。決済も、売り買いも、遊びも。", "[haruki] NTTデータの売上は四兆円を超える。目に見えない仕組みが、これだけの規模になる。", "[nana] 形はないのに、世界を動かしてるんだ。"]', 'H_データセンター内部', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_04.png', 'haruki', '[haruki] 任天堂のゲーム機は、世界で一億台を超えて売れてる。
[nana] 世界で一億台! 私の家にもあるやつだ。
[haruki] しかも任天堂は、もともと花札を作っていた会社なんだ。百年以上前からね。
[nana] 花札から始まって、今は世界中を遊ばせてるんだ。すごい変わりようだね。', '花札の会社が、世界を1億台で遊ばせる', '任天堂 ゲーム機 世界累計1億台超', '任天堂 公式・沿革', '["[haruki] 任天堂のゲーム機は、世界で一億台を超えて売れてる。", "[nana] 世界で一億台! 私の家にもあるやつだ。", "[haruki] しかも任天堂は、もともと花札を作っていた会社なんだ。百年以上前からね。", "[nana] 花札から始まって、今は世界中を遊ばせてるんだ。すごい変わりようだね。"]', 'H_ゲーム機とキャラクター(任天堂)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_05.png', 'nana', '[nana] 勢いのある業界だけど、お給料はどうなの?
[haruki] NTTデータは平均約九百二十万円、メルカリは約千百八十万円、任天堂は約九百七十万円だよ。
[haruki] メルカリは平均年齢が三十代半ば。若くても高いのは、市場が大きく付加価値も大きいから。
[nana] 年次じゃなくて、生んだ価値の大きさで決まるんだ。', '若くても高いのは、市場と付加価値の大きさ', '平均年収 NTTデータ約923万 / メルカリ約1,176万 / 任天堂約967万', '各社 有価証券報告書等(2025時点)', '["[nana] 勢いのある業界だけど、お給料はどうなの?", "[haruki] NTTデータは平均約九百二十万円、メルカリは約千百八十万円、任天堂は約九百七十万円だよ。", "[haruki] メルカリは平均年齢が三十代半ば。若くても高いのは、市場が大きく付加価値も大きいから。", "[nana] 年次じゃなくて、生んだ価値の大きさで決まるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_06.png', 'haruki', '[haruki] メルカリは社員の八割超が中途入社で、経歴もいろいろ。実力で評価される世界だよ。
[nana] 新卒じゃなくても、途中から入る人が多いんだ。
[haruki] リモートで柔軟に働ける会社もあれば、大規模開発やゲーム作りは長丁場になることもある。
[nana] 自由もあるけど、作り切る覚悟もいる。そういう働き方なんだね。', '実力主義・柔軟な働き方、その分の覚悟も', '中途比率が高い職場 / 大規模開発は長丁場', NULL, '["[haruki] メルカリは社員の八割超が中途入社で、経歴もいろいろ。実力で評価される世界だよ。", "[nana] 新卒じゃなくても、途中から入る人が多いんだ。", "[haruki] リモートで柔軟に働ける会社もあれば、大規模開発やゲーム作りは長丁場になることもある。", "[nana] 自由もあるけど、作り切る覚悟もいる。そういう働き方なんだね。"]', 'H_開発オフィス', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_07.png', 'nana', '[nana] 人気の業界だし、採用はやっぱり狭き門なんでしょ?
[haruki] 狭き門だけど、見られるのは肩書きより、大胆に挑めるか。
[haruki] メルカリは大胆にやろう、NTTデータは自ら動く力、任天堂は独創性と誠実さを大事にする。
[nana] 自分の頭で考えて、大胆に作れる人を求めてるんだ。', '見るのは、肩書きより大胆に挑めるか', '大胆にやろう / 自ら動く力 / 独創性と誠実さ', NULL, '["[nana] 人気の業界だし、採用はやっぱり狭き門なんでしょ?", "[haruki] 狭き門だけど、見られるのは肩書きより、大胆に挑めるか。", "[haruki] メルカリは大胆にやろう、NTTデータは自ら動く力、任天堂は独創性と誠実さを大事にする。", "[nana] 自分の頭で考えて、大胆に作れる人を求めてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_08.png', 'nana', '[nana] どうして、そんなに大きな数字になるの?
[haruki] ソフトは、一度作れば世界中に一瞬で広がる。工場を建て増す必要がない。
[haruki] 決済もフリマもゲームも、一つの仕組みが何千万、何億の人に届く。
[nana] 小さく作って、大きく広げられる。それがこの業界の強みなんだ。', '一度作れば、世界へ一瞬で広がる', 'ソフトウェアの拡張性が桁違いの数字を生む', NULL, '["[nana] どうして、そんなに大きな数字になるの?", "[haruki] ソフトは、一度作れば世界中に一瞬で広がる。工場を建て増す必要がない。", "[haruki] 決済もフリマもゲームも、一つの仕組みが何千万、何億の人に届く。", "[nana] 小さく作って、大きく広げられる。それがこの業界の強みなんだ。"]', 'H_決済・銀行ネットワークのイメージ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば社会を支える大きなシステムを設計している。あるいは世界に向けたサービスを企画している。
[haruki] あるいは新しいゲームを作って、世界中の人を笑顔にしている。
[nana] 自分の作ったものが、何千万人に届くんだ。わくわくするね。', '10年後、たとえばこんな現場', '社会インフラの設計 / 世界向けサービス / 新しいゲーム開発', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば社会を支える大きなシステムを設計している。あるいは世界に向けたサービスを企画している。", "[haruki] あるいは新しいゲームを作って、世界中の人を笑顔にしている。", "[nana] 自分の作ったものが、何千万人に届くんだ。わくわくするね。"]', 'H_データセンター内部', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__it-ai-saas-game', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__it-ai-saas-game/panel_10.png', 'both', '[haruki] 決済も売買も遊びも、ソフトで動かして、世界へ広げる。だから数字が桁違いになる。
[nana] 目に見えないのに、こんなに世界を動かしてたんだ。
[both] 数字で、世界を動かす。それが、デジタルの業界。', '数字で、世界を動かす。', 'ソフトの拡張性で人の行動を動かす業界', NULL, '["[haruki] 決済も売買も遊びも、ソフトで動かして、世界へ広げる。だから数字が桁違いになる。", "[nana] 目に見えないのに、こんなに世界を動かしてたんだ。", "[both] 数字で、世界を動かす。それが、デジタルの業界。"]', 'H_レジのスマホ決済端末(NTTデータCAFIS)', NULL);

-- ===== industry_10koma__manufacturer (メーカー) =====
-- source: output/industry_10koma__manufacturer/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__manufacturer', 'メーカー', 'manufacturer_maker', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_01.png', 'nana', '[nana] スマホの裏、よく見ると小さな刻印が並んでるんだね。
[haruki] その極小の印字、多くはキーエンスのレーザ機器で刻まれてる。
[nana] メーカーって、車とか家電を作る会社でしょ?
[haruki] それもだけど、この見えない一点にもいる。生活の根っこを技術で支えてるんだ。', 'この小さな刻印も、メーカーの仕事', 'メーカー / 生活の根っこを支える技術', NULL, '["[nana] スマホの裏、よく見ると小さな刻印が並んでるんだね。", "[haruki] その極小の印字、多くはキーエンスのレーザ機器で刻まれてる。", "[nana] メーカーって、車とか家電を作る会社でしょ?", "[haruki] それもだけど、この見えない一点にもいる。生活の根っこを技術で支えてるんだ。"]', 'H_スマホ裏の極小刻印(キーエンスのレーザマーカ)', '{"location": "スマホ裏面の下部", "object_type": "レーザ刻印", "brand_form": "極小のトレーサビリティ刻印(具体的な文字は描かない)", "attachment": "スマホ筐体に刻印", "scale_note": "実在の刻印と同じ極小サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_02.png', 'haruki', '[haruki] この工場の眼になっているセンサも、キーエンスは世界で約四十万社に届けてる。
[nana] 工場の裏側に、そんなに広がってるんだ。
[haruki] エレベーターや新幹線は日立、車はトヨタ。見えないところで生活が回ってる。
[nana] 使ってるのに気づかない。それがメーカーの当たり前なんだね。', '工場の眼も、エレベーターも、車も', 'キーエンス 世界約40万社に技術を提供', 'キーエンス 公式・事業紹介', '["[haruki] この工場の眼になっているセンサも、キーエンスは世界で約四十万社に届けてる。", "[nana] 工場の裏側に、そんなに広がってるんだ。", "[haruki] エレベーターや新幹線は日立、車はトヨタ。見えないところで生活が回ってる。", "[nana] 使ってるのに気づかない。それがメーカーの当たり前なんだね。"]', 'H_工場の生産ラインとFAセンサ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_03.png', 'haruki', '[haruki] メーカーは物を作って売るだけじゃない。社会の土台そのものを技術で作ってる。
[nana] 土台って、道路とか電気みたいな?
[haruki] 近いね。トヨタは売上が四十八兆円、日立は約十兆円。日本の産業を根っこで支える規模だよ。
[nana] 一つの製品の先に、社会全体があるんだ。', '作って売るだけでなく、社会の土台を作る', 'トヨタ 売上 約48兆円 / 日立 約9.8兆円', '各社 2025年3月期・決算', '["[haruki] メーカーは物を作って売るだけじゃない。社会の土台そのものを技術で作ってる。", "[nana] 土台って、道路とか電気みたいな?", "[haruki] 近いね。トヨタは売上が四十八兆円、日立は約十兆円。日本の産業を根っこで支える規模だよ。", "[nana] 一つの製品の先に、社会全体があるんだ。"]', 'H_自動車の組立ライン(トヨタ元町工場)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_04.png', 'haruki', '[haruki] この新幹線を安全に走らせる運行管理の仕組みも、日立が世界で最初に作った。
[nana] 時間どおりに来る当たり前が、技術で支えられてるんだ。
[haruki] トヨタは世界で最初の量産ハイブリッド車で、環境の課題にも挑んできた。
[nana] 便利も、安全も、環境も。メーカーの技術が社会の課題を解いてるんだね。', '便利も、安全も、環境も、技術で解く', '日立=世界初の列車運行管理 / トヨタ=世界初の量産HV', '各社 公式・沿革', '["[haruki] この新幹線を安全に走らせる運行管理の仕組みも、日立が世界で最初に作った。", "[nana] 時間どおりに来る当たり前が、技術で支えられてるんだ。", "[haruki] トヨタは世界で最初の量産ハイブリッド車で、環境の課題にも挑んできた。", "[nana] 便利も、安全も、環境も。メーカーの技術が社会の課題を解いてるんだね。"]', 'H_新幹線と運行管理システム(日立)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_05.png', 'nana', '[nana] メーカーのお給料って、会社でだいぶ差があるって本当?
[haruki] うん。キーエンスの平均は約二千万円、トヨタは約九百八十万円、日立は約九百六十万円。
[haruki] 高いところは、少ない人数で大きな付加価値を生む生産性の高さが年収に返ってる。
[nana] 額の差そのものより、どれだけ価値を生む仕組みかで決まるんだ。', '高年収は、付加価値と生産性の構造', '平均年収 キーエンス約2,039万 / トヨタ約983万 / 日立約961万', '各社 有価証券報告書等(2025年3月期)', '["[nana] メーカーのお給料って、会社でだいぶ差があるって本当?", "[haruki] うん。キーエンスの平均は約二千万円、トヨタは約九百八十万円、日立は約九百六十万円。", "[haruki] 高いところは、少ない人数で大きな付加価値を生む生産性の高さが年収に返ってる。", "[nana] 額の差そのものより、どれだけ価値を生む仕組みかで決まるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_06.png', 'haruki', '[haruki] 理系は専攻を活かして、開発や生産技術、研究に進む道がある。
[nana] 文系はメーカーだと何をするの?
[haruki] 営業や企画、知財など事業を回す役割。勤務地が地方の工場や研究所になることも多い。
[nana] 職種でも場所でも道が分かれる。自分の軸で選ぶ業界なんだね。', '理系は開発・生産技術・研究、文系は事業を回す', '工場・研究所勤務で地方配属も', NULL, '["[haruki] 理系は専攻を活かして、開発や生産技術、研究に進む道がある。", "[nana] 文系はメーカーだと何をするの?", "[haruki] 営業や企画、知財など事業を回す役割。勤務地が地方の工場や研究所になることも多い。", "[nana] 職種でも場所でも道が分かれる。自分の軸で選ぶ業界なんだね。"]', 'H_研究所・開発現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_07.png', 'nana', '[nana] 有名なメーカーばかりだと、採用はやっぱり難しいよね?
[haruki] 難しいけど、見られるのは肩書きより人の芯。トヨタは人間力と実行力を大事にする。
[haruki] キーエンスは準備より等身大の自分で来てほしいと言う。日立は社会課題へ挑む気持ちを問う。
[nana] 飾らずに、何を作りたいかという意志を見てるんだ。', '見るのは、肩書きより人の芯と意志', '人間力と実行力 / 等身大 / 社会課題への挑戦', NULL, '["[nana] 有名なメーカーばかりだと、採用はやっぱり難しいよね?", "[haruki] 難しいけど、見られるのは肩書きより人の芯。トヨタは人間力と実行力を大事にする。", "[haruki] キーエンスは準備より等身大の自分で来てほしいと言う。日立は社会課題へ挑む気持ちを問う。", "[nana] 飾らずに、何を作りたいかという意志を見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_08.png', 'haruki', '[haruki] 日立はこの塔で、世界最速クラスのエレベーターを試してきた。
[nana] 目立たないけど、世界の記録を作る技術がここにあるんだ。
[haruki] 日本のメーカーは、こうした見えない基幹技術で世界の当たり前を支えてる。
[nana] 派手じゃなくても、なくてはならない。それが本当の強さなんだね。', '見えない基幹技術で、世界の当たり前を支える', '世界最速クラスのエレベーターを試す研究塔', '日立 公式・技術紹介', '["[haruki] 日立はこの塔で、世界最速クラスのエレベーターを試してきた。", "[nana] 目立たないけど、世界の記録を作る技術がここにあるんだ。", "[haruki] 日本のメーカーは、こうした見えない基幹技術で世界の当たり前を支えてる。", "[nana] 派手じゃなくても、なくてはならない。それが本当の強さなんだね。"]', 'H_エレベーター研究塔(日立G1TOWER)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな現場にいると思う?
[haruki] たとえば次の世代の電動車を開発している。あるいは海外の工場に技術を提案している。
[haruki] あるいは街のインフラを設計している。どれも生活を根っこから作る仕事だよ。
[nana] 自分の手が、誰かの毎日の当たり前になるんだ。', '10年後、たとえばこんな現場', '次世代車の開発 / 海外工場への技術提案 / インフラ設計', NULL, '["[nana] もし入れたら、十年後はどんな現場にいると思う?", "[haruki] たとえば次の世代の電動車を開発している。あるいは海外の工場に技術を提案している。", "[haruki] あるいは街のインフラを設計している。どれも生活を根っこから作る仕事だよ。", "[nana] 自分の手が、誰かの毎日の当たり前になるんだ。"]', 'H_研究所・開発現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__manufacturer', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__manufacturer/panel_10.png', 'both', '[haruki] 見えない一点から、社会の土台まで。メーカーは技術で生活の根っこを支える。
[nana] 当たり前の毎日は、こんなに多くの技術でできてたんだ。
[both] 生活の根っこを、技術で支える。それが、メーカー。', '生活の根っこを、技術で支える。', '見えない基幹技術で社会の土台を作る業界', NULL, '["[haruki] 見えない一点から、社会の土台まで。メーカーは技術で生活の根っこを支える。", "[nana] 当たり前の毎日は、こんなに多くの技術でできてたんだ。", "[both] 生活の根っこを、技術で支える。それが、メーカー。"]', 'H_工場の生産ラインとFAセンサ', NULL);

-- ===== industry_10koma__education-hr (教育・人材) =====
-- source: output/industry_10koma__education-hr/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__education-hr', '教育・人材', 'education_hr', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_01.png', 'nana', '[nana] 教育とか人材って、いい仕事だと思うけど、地味で儲からなそう。
[haruki] 儲からなそう?
[nana] うん。人の役に立つけど、ビジネスとしては小さそうっていうか。
[haruki] その就活サイトを作ってる会社、売上が三兆円を超えるって言ったら驚く?', '教育・人材って、地味で儲からなそう?', '教育・人材 / いい仕事の、意外な武器', NULL, '["[nana] 教育とか人材って、いい仕事だと思うけど、地味で儲からなそう。", "[haruki] 儲からなそう?", "[nana] うん。人の役に立つけど、ビジネスとしては小さそうっていうか。", "[haruki] その就活サイトを作ってる会社、売上が三兆円を超えるって言ったら驚く?"]', 'H_就活サイトと不動産サイトのキャラ(リクルート)', '{"location": "スマホの画面", "object_type": "情報サービスの画面", "brand_form": "就活・情報サービスの抽象的なアプリ画面", "attachment": "スマホの画面表示", "scale_note": "実在のスマホと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_02.png', 'haruki', '[haruki] リクルートは、世界最大の求人サービスを持ってる。営業利益は五千億円近い。
[nana] え、そんなに大きいの?
[haruki] 就活のリクナビも、住まいのサイトも、旅行の予約も、ぜんぶ同じ会社。
[nana] 人の役に立つことが、こんな大きなビジネスになるんだ。', '世界最大の求人、営業利益は5,000億円近く', 'リクルート 売上 約3.6兆円', 'リクルート 2025年3月期・決算', '["[haruki] リクルートは、世界最大の求人サービスを持ってる。営業利益は五千億円近い。", "[nana] え、そんなに大きいの?", "[haruki] 就活のリクナビも、住まいのサイトも、旅行の予約も、ぜんぶ同じ会社。", "[nana] 人の役に立つことが、こんな大きなビジネスになるんだ。"]', 'H_世界最大の求人サービス(リクルートIndeed)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_03.png', 'nana', '[nana] でも教育のほうは、そんなに大きくないでしょ?
[haruki] ベネッセの通信教育やキャラクターで育った人は多い。学びを生涯支えるのも同じ業界だよ。
[nana] 言われてみれば、私も小さい頃やってた。
[haruki] 子どもの学びから、大人のはたらくまで。人の一生に寄り添う業界なんだ。', '子どもの学びから、大人のはたらくまで', 'ベネッセ=生涯の学びを支える', 'ベネッセ 公式・事業紹介', '["[nana] でも教育のほうは、そんなに大きくないでしょ?", "[haruki] ベネッセの通信教育やキャラクターで育った人は多い。学びを生涯支えるのも同じ業界だよ。", "[nana] 言われてみれば、私も小さい頃やってた。", "[haruki] 子どもの学びから、大人のはたらくまで。人の一生に寄り添う業界なんだ。"]', 'H_進研ゼミとしまじろう(ベネッセ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_04.png', 'haruki', '[haruki] 人材は、はたらくをつなぐ仕事。パーソルは人と仕事の出会いを作ってる。
[nana] 転職や派遣のサービスだよね。
[haruki] うん。誰かに合う仕事を見つけて、その人の可能性を広げる。はたらいて笑おう、が合言葉なんだ。
[nana] 人の人生の、大事な分かれ道に立ち会うんだ。', '人と仕事を出会わせ、可能性を広げる', 'パーソル=はたらくをつなぐ / はたらいて、笑おう。', 'パーソル 公式・事業紹介', '["[haruki] 人材は、はたらくをつなぐ仕事。パーソルは人と仕事の出会いを作ってる。", "[nana] 転職や派遣のサービスだよね。", "[haruki] うん。誰かに合う仕事を見つけて、その人の可能性を広げる。はたらいて笑おう、が合言葉なんだ。", "[nana] 人の人生の、大事な分かれ道に立ち会うんだ。"]', 'H_人材サービスの面談(パーソルdoda)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_05.png', 'nana', '[nana] 人の役に立つ仕事で、そんなにお給料が出せるものなの?
[haruki] リクルートは平均約千百四十万円、ベネッセは約九百四十万円、パーソルは約八百二十万円だよ。
[haruki] 高いのは、人の可能性を広げる価値と、多くの人が使うサービスの規模があるから。
[nana] 人の役に立つことと、儲かることは、両立するんだ。', '人の可能性の価値と、サービスの規模', '平均年収 リクルート約1,145万 / ベネッセ約941万 / パーソル約819万', '各社 有価証券報告書等(2023-2025)', '["[nana] 人の役に立つ仕事で、そんなにお給料が出せるものなの?", "[haruki] リクルートは平均約千百四十万円、ベネッセは約九百四十万円、パーソルは約八百二十万円だよ。", "[haruki] 高いのは、人の可能性を広げる価値と、多くの人が使うサービスの規模があるから。", "[nana] 人の役に立つことと、儲かることは、両立するんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_06.png', 'haruki', '[haruki] 仕事は、営業やキャリアの相談役、企画、教材の開発、エンジニアと幅広い。
[nana] 人と向き合う仕事が多そう。
[haruki] うん。一人ひとりの悩みに向き合うから責任は重いけど、その分、裁量も大きい。
[nana] 人の役に立つ実感が、いちばん近い仕事なんだね。', '人と向き合う、責任も裁量も大きい仕事', '営業・キャリア相談・企画・開発・エンジニア', NULL, '["[haruki] 仕事は、営業やキャリアの相談役、企画、教材の開発、エンジニアと幅広い。", "[nana] 人と向き合う仕事が多そう。", "[haruki] うん。一人ひとりの悩みに向き合うから責任は重いけど、その分、裁量も大きい。", "[nana] 人の役に立つ実感が、いちばん近い仕事なんだね。"]', 'H_キャリア相談・面談の現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_07.png', 'nana', '[nana] 人気だと、採用はやっぱり厳しいんでしょ?
[haruki] 厳しいけど、見られるのは点数より、自分ごととして動けるか。
[haruki] リクルートは自ら機会を創る当事者意識、ベネッセはバイタリティと本気さ、パーソルは主体性を見る。
[nana] 人の人生に関わるから、自分から動ける人を求めてるんだ。', '見るのは、自分ごととして動けるか', '当事者意識 / バイタリティと本気さ / 主体性', NULL, '["[nana] 人気だと、採用はやっぱり厳しいんでしょ?", "[haruki] 厳しいけど、見られるのは点数より、自分ごととして動けるか。", "[haruki] リクルートは自ら機会を創る当事者意識、ベネッセはバイタリティと本気さ、パーソルは主体性を見る。", "[nana] 人の人生に関わるから、自分から動ける人を求めてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_08.png', 'nana', '[nana] 教育も人材も、結局は同じことをしてるんだね。
[haruki] そう。学びと、はたらく機会。人生の節目のたびに寄り添って、可能性を広げる。
[nana] 進学も、就職も、転職も、ぜんぶこの業界が支えてるんだ。
[haruki] 人が一歩を踏み出す瞬間に立ち会える。それが最大の強みだよ。', '人生の節目に寄り添い、可能性を広げる', '進学・就職・転職、一歩を踏み出す瞬間に', '各社 公式・理念', '["[nana] 教育も人材も、結局は同じことをしてるんだね。", "[haruki] そう。学びと、はたらく機会。人生の節目のたびに寄り添って、可能性を広げる。", "[nana] 進学も、就職も、転職も、ぜんぶこの業界が支えてるんだ。", "[haruki] 人が一歩を踏み出す瞬間に立ち会える。それが最大の強みだよ。"]', 'H_学びと就活の場面', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば新しい学びのサービスを作っている。あるいは人と仕事をつなぐ新事業を立ち上げている。
[haruki] あるいは、誰かの就職や転職を支えて、その人の人生を変えている。
[nana] 人の可能性を広げる仕事。地味どころか、一生に関わるんだ。', '10年後、たとえばこんな姿', '新しい学びのサービス / 人と仕事をつなぐ新事業 / 就職を支える', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば新しい学びのサービスを作っている。あるいは人と仕事をつなぐ新事業を立ち上げている。", "[haruki] あるいは、誰かの就職や転職を支えて、その人の人生を変えている。", "[nana] 人の可能性を広げる仕事。地味どころか、一生に関わるんだ。"]', 'H_世界最大の求人サービス(リクルートIndeed)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__education-hr', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__education-hr/panel_10.png', 'both', '[haruki] 学びを届け、はたらく機会をつなぎ、人の可能性を広げる。それが教育人材。
[nana] 地味で儲からないと思ってたのは、この業界の大きさを知らなかっただけだった。
[both] 人の可能性を、広げる。地味どころか、一生に関わる仕事。それが、教育・人材。', '人の可能性を、広げる。', '学びとはたらく機会で人生を支える業界', NULL, '["[haruki] 学びを届け、はたらく機会をつなぎ、人の可能性を広げる。それが教育人材。", "[nana] 地味で儲からないと思ってたのは、この業界の大きさを知らなかっただけだった。", "[both] 人の可能性を、広げる。地味どころか、一生に関わる仕事。それが、教育・人材。"]', 'H_進研ゼミとしまじろう(ベネッセ)', NULL);

-- ===== industry_10koma__startup (スタートアップ) =====
-- source: output/industry_10koma__startup/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__startup', 'スタートアップ', 'startup', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_01.png', 'nana', '[nana] この完全栄養のパン、よく買うんだよね。
[haruki] それを作ってる会社、百人ちょっとで、累計二億袋も売ったんだ。
[nana] 百人で二億袋!? そんな小さな会社が?
[haruki] それがスタートアップ。少人数で、桁違いの数字を生むんだ。', '100人ちょっとで、累計2億袋', 'スタートアップ / 少人数で桁違い', NULL, '["[nana] この完全栄養のパン、よく買うんだよね。", "[haruki] それを作ってる会社、百人ちょっとで、累計二億袋も売ったんだ。", "[nana] 百人で二億袋!? そんな小さな会社が?", "[haruki] それがスタートアップ。少人数で、桁違いの数字を生むんだ。"]', 'H_完全栄養食のパン(ベースフード)', '{"location": "棚の商品", "object_type": "完全栄養食のパン", "brand_form": "黄色を基調にした完全栄養食のパンのパッケージ", "attachment": "棚に陳列", "scale_note": "実在の商品と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_02.png', 'haruki', '[haruki] 暗号資産のbitFlyerは、百五十人ほどで、預かる資産が一兆円を超えてる。
[nana] 百五十人で、一兆円!?
[haruki] 大きな会社じゃなくても、これだけの規模を動かせる。
[nana] 人数と、生み出す数字が、全然つり合ってない。', '150人ほどで、預かる資産1兆円超', 'bitFlyer=暗号資産取引所', 'bitFlyer 公式・事業報告(2024年12月末)', '["[haruki] 暗号資産のbitFlyerは、百五十人ほどで、預かる資産が一兆円を超えてる。", "[nana] 百五十人で、一兆円!?", "[haruki] 大きな会社じゃなくても、これだけの規模を動かせる。", "[nana] 人数と、生み出す数字が、全然つり合ってない。"]', 'H_暗号資産取引所のアプリ(bitFlyer)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_03.png', 'nana', '[nana] どうして少人数で、そんな数字が出せるの?
[haruki] 新しい一つのアイデアに、全部を賭けるからだよ。ミドリムシ、完全栄養食、暗号資産。
[haruki] ユーグレナは、ミドリムシを世界で初めて大量に育てることに成功した。
[nana] 誰もやってないことに集中して、市場そのものを作るんだ。', '一つのアイデアに全部を賭け、市場を作る', 'ユーグレナ=ミドリムシの量産に世界で初成功', 'ユーグレナ 公式・沿革', '["[nana] どうして少人数で、そんな数字が出せるの?", "[haruki] 新しい一つのアイデアに、全部を賭けるからだよ。ミドリムシ、完全栄養食、暗号資産。", "[haruki] ユーグレナは、ミドリムシを世界で初めて大量に育てることに成功した。", "[nana] 誰もやってないことに集中して、市場そのものを作るんだ。"]', 'H_ミドリムシの培養プール(ユーグレナ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_04.png', 'haruki', '[haruki] そのミドリムシから、飲み物やサプリだけじゃなく、バイオ燃料まで作った。
[nana] 微生物が、飛行機の燃料になるの?
[haruki] うん。実際に、その燃料で飛行機を飛ばすことにも成功してる。
[nana] 小さな会社の一つの発想が、こんなに広がるんだ。', '微生物から、飛行機の燃料まで', 'ユーグレナ=バイオ燃料での飛行に成功', 'ユーグレナ 公式・実績', '["[haruki] そのミドリムシから、飲み物やサプリだけじゃなく、バイオ燃料まで作った。", "[nana] 微生物が、飛行機の燃料になるの?", "[haruki] うん。実際に、その燃料で飛行機を飛ばすことにも成功してる。", "[nana] 小さな会社の一つの発想が、こんなに広がるんだ。"]', 'H_バイオ燃料と飛行機(ユーグレナ・サステオ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_05.png', 'nana', '[nana] 小さい会社だと、お給料は低いのかな。
[haruki] 上場してるユーグレナは有報で平均約七百万円。ベースフードやbitFlyerは平均額の出典が有報に定まらないから伏せるね。
[haruki] 少人数で大きな価値を生む仕事だけど、まだ赤字で挑戦している段階の会社もある。そこは正直に。
[nana] 今の安定より、生む価値と将来にかける構造なんだ。', '少人数で生む価値が、年収に返る', 'ユーグレナ約697万(有報) ※ベースフード・bitFlyerは平均額の出典が定まらず非提示', 'ユーグレナ(2931) 有価証券報告書', '["[nana] 小さい会社だと、お給料は低いのかな。", "[haruki] 上場してるユーグレナは有報で平均約七百万円。ベースフードやbitFlyerは平均額の出典が有報に定まらないから伏せるね。", "[haruki] 少人数で大きな価値を生む仕事だけど、まだ赤字で挑戦している段階の会社もある。そこは正直に。", "[nana] 今の安定より、生む価値と将来にかける構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_06.png', 'haruki', '[haruki] 少人数だから、一人が幅広い仕事を担う。若くても大きな役割を持てる。
[nana] やりがいはありそう。
[haruki] その分、変化がとても速くて、安定という意味では不確かさもある。
[nana] 大きな裁量と、不安定さが、セットなんだね。', '一人が幅広く担い、裁量は大きい', '変化が速く、不安定さもある', NULL, '["[haruki] 少人数だから、一人が幅広い仕事を担う。若くても大きな役割を持てる。", "[nana] やりがいはありそう。", "[haruki] その分、変化がとても速くて、安定という意味では不確かさもある。", "[nana] 大きな裁量と、不安定さが、セットなんだね。"]', 'H_少人数のオフィス', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_07.png', 'nana', '[nana] 少人数だと、採用で見るところも違いそう。
[haruki] うん。肩書きより、挑戦したい気持ちと、常識にとらわれない発想。
[haruki] ユーグレナはチャレンジ精神、ベースフードは常識を超える発想、bitFlyerは熱意とスピードを見る。
[nana] まだない道を、自分で作れる人を求めてるんだ。', '見るのは、挑戦と常識を超える発想', 'チャレンジ精神 / 常識にとらわれない / 熱意とスピード', NULL, '["[nana] 少人数だと、採用で見るところも違いそう。", "[haruki] うん。肩書きより、挑戦したい気持ちと、常識にとらわれない発想。", "[haruki] ユーグレナはチャレンジ精神、ベースフードは常識を超える発想、bitFlyerは熱意とスピードを見る。", "[nana] まだない道を、自分で作れる人を求めてるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_08.png', 'nana', '[nana] スタートアップの一番の武器って、何なの?
[haruki] 少人数でも、一つのアイデアで、世の中の常識を変えられること。
[haruki] 完全栄養の主食も、暗号資産も、数年前は当たり前じゃなかった。それを普通にした。
[nana] 小さなチームが、みんなの当たり前を作り替えるんだ。', '少人数でも、世の中の常識を変える', '数年前は当たり前でなかったものを、普通にする', NULL, '["[nana] スタートアップの一番の武器って、何なの?", "[haruki] 少人数でも、一つのアイデアで、世の中の常識を変えられること。", "[haruki] 完全栄養の主食も、暗号資産も、数年前は当たり前じゃなかった。それを普通にした。", "[nana] 小さなチームが、みんなの当たり前を作り替えるんだ。"]', 'H_成長を示す数字のイメージ', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば自分の担当事業を大きく育てている。あるいは新しい市場を作っている。
[haruki] あるいは、次の当たり前になるものを生み出している。
[nana] 小さく始めて、世の中を変えるんだ。ぞくぞくするね。', '10年後、たとえばこんな到達点', '担当事業を育てる / 新しい市場を作る / 次の常識を生む', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば自分の担当事業を大きく育てている。あるいは新しい市場を作っている。", "[haruki] あるいは、次の当たり前になるものを生み出している。", "[nana] 小さく始めて、世の中を変えるんだ。ぞくぞくするね。"]', 'H_暗号資産取引所のアプリ(bitFlyer)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__startup', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__startup/panel_10.png', 'both', '[haruki] 新しいアイデアに全部を賭けて、少人数で常識を変える。だから数字が桁違いになる。
[nana] 小さなチームが、こんなに世の中を動かしてたんだ。
[both] 少人数で、常識を変える。小さなチームの、大きな数字。それが、スタートアップ。', '少人数で、常識を変える。', '一つのアイデアに賭けて市場を作る業界', NULL, '["[haruki] 新しいアイデアに全部を賭けて、少人数で常識を変える。だから数字が桁違いになる。", "[nana] 小さなチームが、こんなに世の中を動かしてたんだ。", "[both] 少人数で、常識を変える。小さなチームの、大きな数字。それが、スタートアップ。"]', 'H_完全栄養食のパン(ベースフード)', NULL);

-- ===== industry_10koma__deeptech-space-ai (ディープテック・宇宙・AI) =====
-- source: output/industry_10koma__deeptech-space-ai/scenario_v4.json
-- jsDelivr ref: @2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('industry_10koma__deeptech-space-ai', 'ディープテック・宇宙・AI', 'deeptech_space_ai', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_01.png', 'nana', '[nana] このAIが作った浮世絵、すごくない?最近AIって本当に進んだよね。
[haruki] それを作った日本のAI会社、生まれてまだ数年なんだ。
[nana] そんな新しい会社が、こんなものを?
[haruki] うん。まだ小さいけど、これから世界を変える技術。この業界、一緒に育つ場所なんだ。', 'このAI、生まれてまだ数年の会社', 'ディープテック・宇宙・AI / これから伸びる業界', NULL, '["[nana] このAIが作った浮世絵、すごくない?最近AIって本当に進んだよね。", "[haruki] それを作った日本のAI会社、生まれてまだ数年なんだ。", "[nana] そんな新しい会社が、こんなものを?", "[haruki] うん。まだ小さいけど、これから世界を変える技術。この業界、一緒に育つ場所なんだ。"]', 'H_AIが生成した浮世絵(Sakana AI)', '{"location": "スマホの画面", "object_type": "AI生成画像", "brand_form": "浮世絵風のAI生成画像、抽象的な和のモチーフ", "attachment": "スマホの画面表示", "scale_note": "実在のスマホと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_02.png', 'haruki', '[haruki] ディープテックは、まだ世の中にない基盤技術をゼロから作る業界。
[nana] ゼロからだと、時間がかかりそう。
[haruki] でもさっきのAI会社は、生まれて約一年で企業価値が四千億円まで伸びた。国内で最速だよ。
[nana] 小さく始めて、一気に大きくなれるんだ。', '生まれて約1年で、企業価値4,000億円', '国内最速でユニコーンへ', '各社 公表・報道(2025年時点)', '["[haruki] ディープテックは、まだ世の中にない基盤技術をゼロから作る業界。", "[nana] ゼロからだと、時間がかかりそう。", "[haruki] でもさっきのAI会社は、生まれて約一年で企業価値が四千億円まで伸びた。国内で最速だよ。", "[nana] 小さく始めて、一気に大きくなれるんだ。"]', 'H_麻布台ヒルズのAI企業オフィス(Sakana AI)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_03.png', 'nana', '[nana] 稼ぎ方は、ふつうの会社と何が違うの?
[haruki] 誰も持っていない技術を、自分たちが持つこと。それがそのまま強さになる。
[haruki] ラピダスは国をあげて、世界最先端の二ナノメートルの半導体づくりに挑んでる。
[nana] 誰もできてないことに、正面から挑むんだ。', '誰も持たない技術を、自分たちが持つ', 'ラピダス=国産で最先端2nm半導体に挑戦', 'ラピダス 公式・事業紹介', '["[nana] 稼ぎ方は、ふつうの会社と何が違うの?", "[haruki] 誰も持っていない技術を、自分たちが持つこと。それがそのまま強さになる。", "[haruki] ラピダスは国をあげて、世界最先端の二ナノメートルの半導体づくりに挑んでる。", "[nana] 誰もできてないことに、正面から挑むんだ。"]', 'H_最先端半導体工場とEUV露光装置(ラピダス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_04.png', 'haruki', '[haruki] ispaceは、月に着陸船を送る会社。まだ着陸には成功しきってない。
[nana] 失敗もあったんだ。
[haruki] うん。でも、その一回ごとに技術を伸ばして、次の挑戦へ進んでる。
[nana] うまくいかなくても、前に進み続ける。それも成長なんだね。', '失敗を糧に、挑戦を続けて伸びる', 'ispace=月へ着陸船を送る挑戦', 'ispace 公式・ミッション情報', '["[haruki] ispaceは、月に着陸船を送る会社。まだ着陸には成功しきってない。", "[nana] 失敗もあったんだ。", "[haruki] うん。でも、その一回ごとに技術を伸ばして、次の挑戦へ進んでる。", "[nana] うまくいかなくても、前に進み続ける。それも成長なんだね。"]', 'H_月着陸船と管制室(ispace)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_05.png', 'nana', '[nana] まだ小さい会社だと、お給料は低いのかな。
[haruki] 上場してるispaceは有報で平均約九百八十万円。ラピダスやAI企業は非上場で、確かな平均額は出てないんだ。
[haruki] 若くても専門性で高い場合もある。ただ、まだ赤字で挑戦している段階の会社が多い。そこは正直に。
[nana] 今の額だけじゃなく、専門性と将来にかける構造なんだ。', '専門性で高い場合も、将来にかける構造', 'ispace約978万(有報) ※ラピダス・AI企業は非上場で平均額は非公表', 'ispace(9348) 有価証券報告書(2025年度)', '["[nana] まだ小さい会社だと、お給料は低いのかな。", "[haruki] 上場してるispaceは有報で平均約九百八十万円。ラピダスやAI企業は非上場で、確かな平均額は出てないんだ。", "[haruki] 若くても専門性で高い場合もある。ただ、まだ赤字で挑戦している段階の会社が多い。そこは正直に。", "[nana] 今の額だけじゃなく、専門性と将来にかける構造なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_06.png', 'haruki', '[haruki] 少人数で、中途で入る人が中心。一人ひとりの裁量がとても大きい。
[nana] 若くても、大きな仕事を任されるんだ。
[haruki] その分、組織はまだ固まってなくて、変化も速い。安定より挑戦を選ぶ場所だよ。
[nana] 自由と不確かさが、セットなんだね。', '少人数で裁量大、変化も速い挑戦の場', '中途中心 / 組織はまだ固まっていない', NULL, '["[haruki] 少人数で、中途で入る人が中心。一人ひとりの裁量がとても大きい。", "[nana] 若くても、大きな仕事を任されるんだ。", "[haruki] その分、組織はまだ固まってなくて、変化も速い。安定より挑戦を選ぶ場所だよ。", "[nana] 自由と不確かさが、セットなんだね。"]', 'H_少人数のラボ・開発現場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_07.png', 'nana', '[nana] 最先端すぎて、採用のハードルも高そう。
[haruki] 高いけど、見られるのは肩書きより、限界を押し広げたいという情熱。
[haruki] ラピダスはぶれない信念と探求心、ispaceは答えのない状況に立ち向かう力を大事にする。
[nana] 前人未踏に挑める気持ちを見てるんだ。', '見るのは、限界を押し広げる情熱', '限界を押し広げる情熱 / ぶれない信念・探求心', NULL, '["[nana] 最先端すぎて、採用のハードルも高そう。", "[haruki] 高いけど、見られるのは肩書きより、限界を押し広げたいという情熱。", "[haruki] ラピダスはぶれない信念と探求心、ispaceは答えのない状況に立ち向かう力を大事にする。", "[nana] 前人未踏に挑める気持ちを見てるんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_08.png', 'nana', '[nana] 小さい会社に、そんなに力があるものなの?
[haruki] あるよ。日本発のAIが世界最速で伸び、国産の最先端半導体が試作で動いた。
[haruki] 少人数でも、一人の一手が会社を、そして世界を動かす。
[nana] 大きな組織じゃなくても、世界を変えられるんだ。', '少人数でも、一手が世界を動かす', '国産の最先端半導体が試作で動作', '各社 公式・技術発表', '["[nana] 小さい会社に、そんなに力があるものなの?", "[haruki] あるよ。日本発のAIが世界最速で伸び、国産の最先端半導体が試作で動いた。", "[haruki] 少人数でも、一人の一手が会社を、そして世界を動かす。", "[nana] 大きな組織じゃなくても、世界を変えられるんだ。"]', 'H_2nm試作ウェーハ(ラピダス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_09.png', 'nana', '[nana] もし入れたら、十年後はどんな仕事をしてると思う?
[haruki] たとえば月面の開発に関わっている。あるいは世界に使われるAIを作っている。
[haruki] あるいは、最先端の半導体を量産している。どれも、まだ誰も見ていない景色だよ。
[nana] 自分の手で、世界の最前線を切り開くんだ。', '10年後、たとえばこんな最前線', '月面の開発 / 世界に使われるAI / 最先端半導体の量産', NULL, '["[nana] もし入れたら、十年後はどんな仕事をしてると思う?", "[haruki] たとえば月面の開発に関わっている。あるいは世界に使われるAIを作っている。", "[haruki] あるいは、最先端の半導体を量産している。どれも、まだ誰も見ていない景色だよ。", "[nana] 自分の手で、世界の最前線を切り開くんだ。"]', 'H_月着陸船と管制室(ispace)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('industry_10koma__deeptech-space-ai', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2a982ddcc49a9c4d3a7a54a885300c5e2a9f3232/public/images/industry_10koma__deeptech-space-ai/panel_10.png', 'both', '[haruki] まだ世の中にない技術を、ゼロから作って、世界を変える。それがこの業界。
[nana] 小さくても、これから伸びる。自分も一緒に伸びられるんだ。
[both] まだない技術を、ゼロからつくる。自分も、最前線で伸びる。それが、ディープテック・宇宙・AI。', 'まだない技術を、ゼロからつくる。', '基盤技術で世界を変える成長業界', NULL, '["[haruki] まだ世の中にない技術を、ゼロから作って、世界を変える。それがこの業界。", "[nana] 小さくても、これから伸びる。自分も一緒に伸びられるんだ。", "[both] まだない技術を、ゼロからつくる。自分も、最前線で伸びる。それが、ディープテック・宇宙・AI。"]', 'H_麻布台ヒルズのAI企業オフィス(Sakana AI)', NULL);

