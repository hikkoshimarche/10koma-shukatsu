-- ===== shinkokusyoji (神鋼商事株式会社) =====
-- source: output/shinkokusyoji/scenario_v4.json
-- jsDelivr ref: @fe2b636
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('shinkokusyoji', '神鋼商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_01.png', 'nana', '[nana] 神鋼商事、有価証券報告書（単体）の平均年収は919万円。
[haruki] でもそれ、なんでその水準が出るか分かる?
[nana] 5大商社じゃないのに、ってこと?
[haruki] 神戸製鋼グループの素材・鉄鋼フローを一手に担う専業商社だから、取扱商材の単価と取引規模が年収の土台になってるんだよ。', '919万円の背景を読む。', '神鋼商事 / 8075 / KOBELCOグループ', NULL, '["[nana] 神鋼商事、有価証券報告書（単体）の平均年収は919万円。", "[haruki] でもそれ、なんでその水準が出るか分かる?", "[nana] 5大商社じゃないのに、ってこと?", "[haruki] 神戸製鋼グループの素材・鉄鋼フローを一手に担う専業商社だから、取扱商材の単価と取引規模が年収の土台になってるんだよ。"]', 'H1: 神戸の港湾エリア、神戸製鋼ビルと神鋼商事本社', '{"location": "工場群の建物外壁", "object_type": "建築サイン (KOBELCO)", "brand_form": "工場上部に『KOBELCO』のサイン、赤と白", "attachment": "工場外壁に固定", "scale_note": "実在の工場サインの通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_02.png', 'haruki', '[haruki] 売上4,500億円、純利益約100億円。確かに5大商社の数十分の1。
[nana] そんな小さいのに、919万円?
[haruki] それは、神鋼商事は神戸製鋼グループの中核商社だから。
[nana] 神戸製鋼の動脈に乗ってる、って言ったやつね…', '売上4,500億円、純利益100億円', '規模より、母体の質', NULL, '["[haruki] 売上4,500億円、純利益約100億円。確かに5大商社の数十分の1。", "[nana] そんな小さいのに、919万円?", "[haruki] それは、神鋼商事は神戸製鋼グループの中核商社だから。", "[nana] 神戸製鋼の動脈に乗ってる、って言ったやつね…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_03.png', 'haruki', '[haruki] これ、神戸製鋼の自動車鋼板コイル。3メートル径。
[nana] 3メートル!?
[haruki] 神戸製鋼が作って、神鋼商事がトヨタや日産に売る。日本車の車体は、ここから始まってる。
[nana] つまり、日本の自動車産業の入り口、ってこと…', '日本車の車体、ここから', '神戸製鋼の鋼板 / 神鋼商事が国内自動車メーカーに販売', NULL, '["[haruki] これ、神戸製鋼の自動車鋼板コイル。3メートル径。", "[nana] 3メートル!?", "[haruki] 神戸製鋼が作って、神鋼商事がトヨタや日産に売る。日本車の車体は、ここから始まってる。", "[nana] つまり、日本の自動車産業の入り口、ってこと…"]', 'H2: 巨大な鉄鋼コイル + H3: 自動車製造ラインの車体', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_04.png', 'haruki', '[haruki] チタンも神鋼商事の主力。神戸製鋼のチタンは、医療用の人工関節や航空機エンジン部品に使われてる。
[nana] え、人工関節!?
[haruki] そう。膝や股関節の人工関節、ジェットエンジンのブレード。神鋼商事が世界の医療メーカーや航空機メーカーに販売。
[nana] 鋼板から人工関節まで、神戸製鋼の素材を世界に届ける役なんだ…', '人工関節と航空エンジンも', '神戸製鋼のチタン / 医療・航空の世界へ', NULL, '["[haruki] チタンも神鋼商事の主力。神戸製鋼のチタンは、医療用の人工関節や航空機エンジン部品に使われてる。", "[nana] え、人工関節!?", "[haruki] そう。膝や股関節の人工関節、ジェットエンジンのブレード。神鋼商事が世界の医療メーカーや航空機メーカーに販売。", "[nana] 鋼板から人工関節まで、神戸製鋼の素材を世界に届ける役なんだ…"]', 'H5: チタン製品 (人工関節・航空エンジン部品)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_05.png', 'nana', '[nana] で、結局919万円はどこから?
[haruki] 高炉で作った素材を、その品質と量で、世界の自動車・医療・航空に売る。神戸製鋼の業績連動で、神鋼商事の社員にも還元される。
[haruki] つまり、平均919万円は『神戸製鋼の素材が世界で売れた量』が源泉。素材の値段が動けば、年収も動く。
[nana] 商社単独じゃなくて、製造の動脈と一緒に動くんだ…', '919万円(平均)+KOBELCO連動', '神戸製鋼の素材販売連動 / 業績次第で変動', '公式・有報', '["[nana] で、結局919万円はどこから?", "[haruki] 高炉で作った素材を、その品質と量で、世界の自動車・医療・航空に売る。神戸製鋼の業績連動で、神鋼商事の社員にも還元される。", "[haruki] つまり、平均919万円は『神戸製鋼の素材が世界で売れた量』が源泉。素材の値段が動けば、年収も動く。", "[nana] 商社単独じゃなくて、製造の動脈と一緒に動くんだ…"]', 'H6: 製鋼所の高炉', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_06.png', 'nana', '[nana] 働き方ってどんな感じですか?
[OB先輩] メーカー系商社だから、5大商社より落ち着いた働き方。フレックスもあるし、東京⇄神戸でリモートも使えるよ。
[OB先輩] 福利厚生で大きいのは、独身寮と社宅。神戸本社なら六甲山近くの独身寮があるから、家賃の心配がない分、手取り感はかなり違う。
[haruki] 5大商社より年収が低くても、住居コスト込みで考えるとそんなに変わらない、ってことか…', 'メーカー系で落ち着いた働き方+リモート可', '独身寮(六甲山近く)・社宅で家賃↓', NULL, '["[nana] 働き方ってどんな感じですか?", "[OB先輩] メーカー系商社だから、5大商社より落ち着いた働き方。フレックスもあるし、東京⇄神戸でリモートも使えるよ。", "[OB先輩] 福利厚生で大きいのは、独身寮と社宅。神戸本社なら六甲山近くの独身寮があるから、家賃の心配がない分、手取り感はかなり違う。", "[haruki] 5大商社より年収が低くても、住居コスト込みで考えるとそんなに変わらない、ってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_07.png', 'nana', '[nana] 配属って、6事業領域(鉄鋼/原料/非鉄/機械/溶接/その他)のどこに行くんですか?
[OB先輩] 少人数採用だから、第一希望でも全員は通らない。鉄鋼が花形だけど、機械(建機・クレーン)に行く人もいる。
[OB先輩] 入社3〜5年で東南アジア・中東駐在は普通。世界の自動車メーカー・建機ユーザーが顧客だから。
[haruki] 6つのどこに行っても、神戸製鋼の素材を世界に売る役、ってことか…', '6事業領域、若手で海外駐在', '少人数採用で配属分岐 / 3〜5年で海外', NULL, '["[nana] 配属って、6事業領域(鉄鋼/原料/非鉄/機械/溶接/その他)のどこに行くんですか?", "[OB先輩] 少人数採用だから、第一希望でも全員は通らない。鉄鋼が花形だけど、機械(建機・クレーン)に行く人もいる。", "[OB先輩] 入社3〜5年で東南アジア・中東駐在は普通。世界の自動車メーカー・建機ユーザーが顧客だから。", "[haruki] 6つのどこに行っても、神戸製鋼の素材を世界に売る役、ってことか…"]', 'H4: KOBELCOクレーン', '{"location": "クレーン本体側面", "object_type": "KOBELCO ロゴ", "brand_form": "青い大型クレーンに白文字の『KOBELCO』ロゴ", "attachment": "クレーン本体に印刷", "scale_note": "実在の建機の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_08.png', 'nana', '[OB先輩] 神戸製鋼は、自動車の薄鋼板ではトヨタの主要サプライヤー。航空のチタンはボーイング・エアバス向け。
[OB先輩] その世界販売を担うのが神鋼商事。1社のグループ商社として、グローバルに動く役。
[nana] 神戸製鋼の物語と、神鋼商事の物語が、ぴったり重なってるんだ。
[haruki] 別の5大商社ならではの『総合』とは違う、神戸製鋼一本での『深さ』、ってことだね。', '神戸製鋼の世界戦略を担う1社', 'トヨタ・ボーイング・エアバスへ', NULL, '["[OB先輩] 神戸製鋼は、自動車の薄鋼板ではトヨタの主要サプライヤー。航空のチタンはボーイング・エアバス向け。", "[OB先輩] その世界販売を担うのが神鋼商事。1社のグループ商社として、グローバルに動く役。", "[nana] 神戸製鋼の物語と、神鋼商事の物語が、ぴったり重なってるんだ。", "[haruki] 別の5大商社ならではの『総合』とは違う、神戸製鋼一本での『深さ』、ってことだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_09.png', 'nana', '[OB先輩] 神鋼商事が見るのは、『Sincerity, Synergy, Speed』。誠実・連携・スピード。
[OB先輩] 神戸製鋼の素材を、世界の顧客に届ける。3つともBtoBの商売の核。
[nana] 派手じゃないけど、根が深い言葉…
[haruki] 製造と商売の両方を理解できる人、ってことだね。', 'Sincerity, Synergy, Speed', '誠実・連携・スピード / BtoB商売の核', NULL, '["[OB先輩] 神鋼商事が見るのは、『Sincerity, Synergy, Speed』。誠実・連携・スピード。", "[OB先輩] 神戸製鋼の素材を、世界の顧客に届ける。3つともBtoBの商売の核。", "[nana] 派手じゃないけど、根が深い言葉…", "[haruki] 製造と商売の両方を理解できる人、ってことだね。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('shinkokusyoji', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@fe2b636/public/images/shinkokusyoji/panel_10.png', 'both', '[haruki] 売上4,500億円、純利益約100億円、採用は少数精鋭。
[nana] 神戸製鋼の素材を世界中の自動車・医療・航空に届ける役を担ってる。
[both] 神戸製鋼の動脈で、世界の機械を動かす。神鋼商事。', '神戸製鋼の動脈で、世界の機械を動かす。', '売上 約4,500億円 / 純利益 約100億円 / 採用は少数精鋭', NULL, '["[haruki] 売上4,500億円、純利益約100億円、採用は少数精鋭。", "[nana] 神戸製鋼の素材を世界中の自動車・医療・航空に届ける役を担ってる。", "[both] 神戸製鋼の動脈で、世界の機械を動かす。神鋼商事。"]', 'H1: 神戸の港湾エリア (朝の光)', NULL);
