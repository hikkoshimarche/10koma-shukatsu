-- ===== kddi (KDDI株式会社) =====
-- source: output/kddi/scenario_v4.json
-- jsDelivr ref: @bf9c0d0a76a957f957be3cda35bd200ea80237c9
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('kddi', 'KDDI株式会社', 'it_ai_saas', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_01.png', 'nana', '[nana] ねえ、au使ってるよね?
[haruki] うん、povo。同じKDDIだけど。
[nana] KDDIって、auの会社でしょ?
[haruki] それだけじゃない。固定・移動・グローバル通信、3つ全部できるの、国内でKDDIだけなんだ。', '固定・移動・グローバル、3つ全部', 'KDDI / 9433 / 国内唯一の総合通信事業者', NULL, '["[nana] ねえ、au使ってるよね?", "[haruki] うん、povo。同じKDDIだけど。", "[nana] KDDIって、auの会社でしょ?", "[haruki] それだけじゃない。固定・移動・グローバル通信、3つ全部できるの、国内でKDDIだけなんだ。"]', 'H2: au携帯電話端末', '{"location": "ナナの手元のスマホ画面", "object_type": "auロゴ", "brand_form": "スマホ画面上部のau表示、オレンジのブランドカラー", "attachment": "スマホ画面内に表示", "scale_note": "実在のau端末表示と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_02.png', 'haruki', '[haruki] 売上5兆9,180億円、営業利益1兆1,187億円。2025年3月期の数字。
[nana] 1兆円超えの営業利益!?
[haruki] auだけじゃない。光ファイバーのauひかり、国際通信、法人向けネットワーク。固定・移動・グローバル全部やってる。
[nana] 携帯だけの会社じゃなかったんだ…', '売上5.9兆円、営業利益1.1兆円', '2025年3月期 / 固定・移動・グローバル通信', '公式IR 2025年3月期決算', '["[haruki] 売上5兆9,180億円、営業利益1兆1,187億円。2025年3月期の数字。", "[nana] 1兆円超えの営業利益!?", "[haruki] auだけじゃない。光ファイバーのauひかり、国際通信、法人向けネットワーク。固定・移動・グローバル全部やってる。", "[nana] 携帯だけの会社じゃなかったんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_03.png', 'nana', '[nana] スマホの通信って、電波だけだと思ってた。
[haruki] 実は海外との通信の大半は、海底ケーブル。その敷設と保守の専用船を持ってるのがKDDI。
[nana] 船!? 通信会社なのに?
[haruki] KDDIオーシャンリンク。世界の通信を海の底で支える、見えないインフラなんだ。', '海外との通信を支える海底ケーブル', '敷設・保守の専用船を持つKDDI', 'KDDI公式', '["[nana] スマホの通信って、電波だけだと思ってた。", "[haruki] 実は海外との通信の大半は、海底ケーブル。その敷設と保守の専用船を持ってるのがKDDI。", "[nana] 船!? 通信会社なのに?", "[haruki] KDDIオーシャンリンク。世界の通信を海の底で支える、見えないインフラなんだ。"]', NULL, '{"location": "店舗看板", "object_type": "ローソンロゴ", "brand_form": "青地に白文字のLAWSONロゴ、実在の店舗看板", "attachment": "店舗外壁に設置", "scale_note": "実在のローソン看板サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_04.png', 'haruki', '[haruki] KDDIは1984年、第二電電として稲盛和夫さんが創業した。
[nana] 1984年…NTT独占時代に挑戦したんだ。
[haruki] 2000年にDDI・KDD・IDOが合併してKDDI発足。2025年7月、品川TAKANAWA GATEWAY CITYに新本社を移転。
[nana] 40年かけて、通信から生活全体へ広がった会社…', '1984年DDI創業→2025年品川新本社', '稲盛和夫 / 40年で通信から生活全体へ', NULL, '["[haruki] KDDIは1984年、第二電電として稲盛和夫さんが創業した。", "[nana] 1984年…NTT独占時代に挑戦したんだ。", "[haruki] 2000年にDDI・KDD・IDOが合併してKDDI発足。2025年7月、品川TAKANAWA GATEWAY CITYに新本社を移転。", "[nana] 40年かけて、通信から生活全体へ広がった会社…"]', 'H5: TAKANAWA GATEWAY CITY新本社', '{"location": "新本社ビル上部", "object_type": "KDDIロゴ", "brand_form": "ビル外壁のKDDI社名ロゴ、シルバーまたは青系", "attachment": "ビル外壁に固定", "scale_note": "実在の企業ロゴサイズに準拠"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_05.png', 'haruki', '[nana] 年収は?
[haruki] 平均1,018万円、平均年齢42.0歳。
[haruki] 初任給は2026年4月入社で31.3万円から。高い専門性がある人は最大37.3万円。
[nana] 初任給37万円!? 新卒でそんなに…
[haruki] スキルで初任給が変わる仕組み。入社時点から専門性を評価する構造。', '平均1,018万円+初任給最大37.3万円', 'スキルで初任給が変わる / 専門性を評価', '公式IR・採用情報2026', '["[nana] 年収は?", "[haruki] 平均1,018万円、平均年齢42.0歳。", "[haruki] 初任給は2026年4月入社で31.3万円から。高い専門性がある人は最大37.3万円。", "[nana] 初任給37万円!? 新卒でそんなに…", "[haruki] スキルで初任給が変わる仕組み。入社時点から専門性を評価する構造。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_06.png', 'nana', '[OB先輩] 総合職は全国転勤あり。地方の基地局保守、代理店サポート、法人営業…配属は幅広い。
[OB先輩] 東京配属希望が多いけど、実際は地方拠点が多数。インフラを支える現場が仕事の基盤。
[nana] 地方配属、覚悟がいるな…
[haruki] でも平均残業24.9時間、有給取得率83.6%。働き方改革は進んでる。', '全国転勤あり、地方拠点が基盤', '平均残業24.9時間 / 有給取得率83.6%', NULL, '["[OB先輩] 総合職は全国転勤あり。地方の基地局保守、代理店サポート、法人営業…配属は幅広い。", "[OB先輩] 東京配属希望が多いけど、実際は地方拠点が多数。インフラを支える現場が仕事の基盤。", "[nana] 地方配属、覚悟がいるな…", "[haruki] でも平均残業24.9時間、有給取得率83.6%。働き方改革は進んでる。"]', 'H4: auショップ店舗', '{"location": "店舗看板", "object_type": "auショップロゴ", "brand_form": "オレンジ地に白文字のauショップ看板", "attachment": "店舗外壁に設置", "scale_note": "実在のauショップ看板サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_07.png', 'nana', '[OB先輩] KDDIの社是は『心を高める』。稲盛和夫さんの教えで、動機善なりや、私心なかりしか、と自問する。
[OB先輩] 求めるのは『あるべき姿に目を向け、具体的な目標を立ててやり抜く力』『周囲と真摯に向き合い、変革していく力』。
[nana] 心を高める…自分の動機を問い続けるってこと?
[haruki] 倍率じゃなくて、その姿勢が合うかどうか。', '心を高める', '動機善なりや、私心なかりしか / 稲盛和夫の教え', NULL, '["[OB先輩] KDDIの社是は『心を高める』。稲盛和夫さんの教えで、動機善なりや、私心なかりしか、と自問する。", "[OB先輩] 求めるのは『あるべき姿に目を向け、具体的な目標を立ててやり抜く力』『周囲と真摯に向き合い、変革していく力』。", "[nana] 心を高める…自分の動機を問い続けるってこと?", "[haruki] 倍率じゃなくて、その姿勢が合うかどうか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_08.png', 'haruki', '[haruki] KDDIが保有する光海底ケーブル、総延長約120万km。地球約30周分。
[nana] 120万km!? そんなに…
[haruki] アジア・太平洋・米国をつなぐ国際通信網。日本の企業や個人が海外とつながるとき、この光ファイバーを通ってる。
[nana] auだけじゃなくて、世界中の通信を支えてるんだ…', '光海底ケーブル120万km', '地球約30周分 / 国際通信を支えるインフラ', NULL, '["[haruki] KDDIが保有する光海底ケーブル、総延長約120万km。地球約30周分。", "[nana] 120万km!? そんなに…", "[haruki] アジア・太平洋・米国をつなぐ国際通信網。日本の企業や個人が海外とつながるとき、この光ファイバーを通ってる。", "[nana] auだけじゃなくて、世界中の通信を支えてるんだ…"]', 'H3: 光海底ケーブル', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいるんだろう?
[haruki] たとえば、こんな未来。シンガポールで海底ケーブルの新ルート企画。
[haruki] 品川本社で6G技術の開発プロジェクト。
[haruki] 地方都市で、ローソンと自治体をつなぐ地域DX推進。
[nana] 通信で、生活ごと支える。どれも、世界と地域を同時につなぐ仕事…', '10年後、たとえばこんな場面', 'シンガポール / 品川6G開発 / 地方ローソン連携', NULL, '["[nana] もし入れたら、10年後どこにいるんだろう?", "[haruki] たとえば、こんな未来。シンガポールで海底ケーブルの新ルート企画。", "[haruki] 品川本社で6G技術の開発プロジェクト。", "[haruki] 地方都市で、ローソンと自治体をつなぐ地域DX推進。", "[nana] 通信で、生活ごと支える。どれも、世界と地域を同時につなぐ仕事…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kddi', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kddi/panel_10.png', 'both', '[haruki] 売上5.9兆円、営業利益1.1兆円、採用308名。
[nana] 固定・移動・グローバル、3つ全部できるのはKDDIだけ。
[both] 通信で、生活ごと支える。KDDI、おもしろいほうの未来へ。', '通信で、生活ごと支える。', '売上5.9兆円 / 営業利益1.1兆円 / 採用308名', NULL, '["[haruki] 売上5.9兆円、営業利益1.1兆円、採用308名。", "[nana] 固定・移動・グローバル、3つ全部できるのはKDDIだけ。", "[both] 通信で、生活ごと支える。KDDI、おもしろいほうの未来へ。"]', 'H1: KDDIビル（新宿本社）', NULL);

-- ===== fujitsu (富士通株式会社) =====
-- source: output/fujitsu/scenario_v4.json
-- jsDelivr ref: @bf9c0d0a76a957f957be3cda35bd200ea80237c9
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('fujitsu', '富士通株式会社', 'it_ai_saas', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_01.png', 'nana', '[nana] 富士通って、このFMVのPCを作ってる会社だよね?
[haruki] それだけだと思ってた?
[nana] え、違うの?
[haruki] FMVは入口。富士通は、日本のインフラ全部を作ってる会社なんだ。', 'FMVだけじゃない、インフラ企業', '富士通 / 6702 / 89年、ずっと未来を作ってる', NULL, '["[nana] 富士通って、このFMVのPCを作ってる会社だよね?", "[haruki] それだけだと思ってた?", "[nana] え、違うの?", "[haruki] FMVは入口。富士通は、日本のインフラ全部を作ってる会社なんだ。"]', 'H3: FMVノートPC', '{"location": "ノートPC天板中央", "object_type": "FMVロゴ", "brand_form": "天板中央の『FMV』シルバーロゴ、実在の意匠", "attachment": "PC天板に印刷", "scale_note": "実在のFMVノートPCと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_02.png', 'haruki', '[haruki] これが富岳。理化学研究所と富士通が共同開発した、世界最高性能のスーパーコンピュータ。
[nana] 世界最高…!?
[haruki] 新薬開発、気象予測、地震シミュレーション。日本の研究インフラの心臓。
[nana] PCを作る会社が、こんなものまで…', '富岳 — 世界最高性能のスパコン', '理化学研究所と共同開発 / 新薬・気象・地震研究の心臓', NULL, '["[haruki] これが富岳。理化学研究所と富士通が共同開発した、世界最高性能のスーパーコンピュータ。", "[nana] 世界最高…!?", "[haruki] 新薬開発、気象予測、地震シミュレーション。日本の研究インフラの心臓。", "[nana] PCを作る会社が、こんなものまで…"]', 'H2: スーパーコンピュータ富岳', '{"location": "スパコン筐体側面", "object_type": "富士通ロゴプレート", "brand_form": "筐体側面の『FUJITSU』ロゴプレート、赤と白", "attachment": "筐体に取付", "scale_note": "実在の富岳筐体の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_03.png', 'haruki', '[haruki] このアンテナ、富士通が作ってる。
[nana] え、5Gの基地局も?
[haruki] 全国の通信キャリアに提供してる。君のスマホが繋がるのも、富士通のインフラ。
[nana] PCの会社だと思ってたのに、通信の裏側まで…', '5G基地局 — スマホの裏にも富士通', '全国のキャリアに通信インフラを提供', NULL, '["[haruki] このアンテナ、富士通が作ってる。", "[nana] え、5Gの基地局も?", "[haruki] 全国の通信キャリアに提供してる。君のスマホが繋がるのも、富士通のインフラ。", "[nana] PCの会社だと思ってたのに、通信の裏側まで…"]', 'H4: 5G基地局設備', '{"location": "基地局設備の制御ボックス", "object_type": "富士通ロゴプレート", "brand_form": "制御ボックス側面の『FUJITSU』プレート、白地に赤文字", "attachment": "ボックスに取付", "scale_note": "実在の通信設備と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_04.png', 'nana', '[nana] 富士通って、パソコンの会社?
[haruki] それだけじゃない。理化学研究所と共同開発したスーパーコンピュータ『富岳』は、計算速度で世界一になった。
[nana] 世界一!?
[haruki] 日本の計算力の頂点を作るのが富士通。社会を支える計算基盤の会社なんだ。', 'スパコン『富岳』計算速度で世界一', '理研と共同開発／日本の計算力の頂点', '富士通公式', '["[nana] 富士通って、パソコンの会社?", "[haruki] それだけじゃない。理化学研究所と共同開発したスーパーコンピュータ『富岳』は、計算速度で世界一になった。", "[nana] 世界一!?", "[haruki] 日本の計算力の頂点を作るのが富士通。社会を支える計算基盤の会社なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_05.png', 'nana', '[nana] 待遇はどうなの?
[haruki] 平均年収929万円。でも富士通はジョブ型を導入してる。
[nana] ジョブ型?
[haruki] 初任給が年収550万円から最大1000万円。専門性があれば、初年度から高く評価される。年功序列じゃなくて、スキルで稼ぐ構造。', 'ジョブ型 — 初年度から専門性で評価', '平均929万円 / 初任給 年収550万～最大1000万円', '公式IR・2025年3月期', '["[nana] 待遇はどうなの?", "[haruki] 平均年収929万円。でも富士通はジョブ型を導入してる。", "[nana] ジョブ型?", "[haruki] 初任給が年収550万円から最大1000万円。専門性があれば、初年度から高く評価される。年功序列じゃなくて、スキルで稼ぐ構造。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_06.png', 'haruki', '[haruki] 2023年、本社を川崎に移転した。約800名の新卒採用。
[nana] 配属はどうなるの?
[haruki] システムインテグレーション、クラウド、AI、量子技術…配属先は多様。
[haruki] でもジョブ型だから、自分の専門性を明確にして、配属後も自律的に動く必要がある。受け身じゃ厳しい。', '約800名採用 — 配属先は多様', '川崎新本社 / SI・クラウド・AI・量子技術 / ジョブ型で自律必須', NULL, '["[haruki] 2023年、本社を川崎に移転した。約800名の新卒採用。", "[nana] 配属はどうなるの?", "[haruki] システムインテグレーション、クラウド、AI、量子技術…配属先は多様。", "[haruki] でもジョブ型だから、自分の専門性を明確にして、配属後も自律的に動く必要がある。受け身じゃ厳しい。"]', 'H1: 川崎新本社(Kawasaki Tower)', '{"location": "本社タワー上部の外壁", "object_type": "建築サイン (FUJITSU)", "brand_form": "ガラスファサード上部に『FUJITSU』のレリーフサイン、赤と白", "attachment": "タワー外壁に固定", "scale_note": "実在の新本社タワーと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_07.png', 'haruki', '[haruki] 富士通が求めるのは、『挑戦・信頼・共感』。
[nana] 挑戦・信頼・共感?
[haruki] パーパスに共感し、自らのパーパスと重ねて未来を描き、挑戦する人。そして周囲と信頼を構築し、共感を引き出せる人。
[nana] 採用は約800名。でも、この3つの価値観でマッチするかを見てる…', '挑戦・信頼・共感', '採用約800名 / パーパスに共感し挑戦する人', NULL, '["[haruki] 富士通が求めるのは、『挑戦・信頼・共感』。", "[nana] 挑戦・信頼・共感?", "[haruki] パーパスに共感し、自らのパーパスと重ねて未来を描き、挑戦する人。そして周囲と信頼を構築し、共感を引き出せる人。", "[nana] 採用は約800名。でも、この3つの価値観でマッチするかを見てる…"]', 'H6: 富士通ロゴ(FUJITSUレッド・インフィニティマーク)', '{"location": "壁面中央", "object_type": "富士通ロゴ(インフィニティマーク付き)", "brand_form": "『FUJITSU』ロゴ(赤)、j・i上部のインフィニティマークが地球と太陽、無限の可能性を象徴", "attachment": "壁面に固定", "scale_note": "実在のエントランスロゴと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_08.png', 'haruki', '[haruki] 2020年、富士通はパーパスを刷新した。ハードからサービスへ。
[nana] パーパス刷新?
[haruki] 売上3兆5,501億円、営業利益2,650億円。前期比+78%。
[nana] 78%!? 何があったの?
[haruki] PC屋じゃなくて、社会のDXを支える企業へ。89年の歴史で、一番大きな変革期。', '営業利益+78% — 大転換の真っ只中', '売上3.6兆円 / 2020年パーパス刷新 / ハード→サービスへ', '2025年3月期決算', '["[haruki] 2020年、富士通はパーパスを刷新した。ハードからサービスへ。", "[nana] パーパス刷新?", "[haruki] 売上3兆5,501億円、営業利益2,650億円。前期比+78%。", "[nana] 78%!? 何があったの?", "[haruki] PC屋じゃなくて、社会のDXを支える企業へ。89年の歴史で、一番大きな変革期。"]', 'H5: 汐留シティセンター(旧本社)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_09.png', 'haruki', '[nana] もし富士通に入ったら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。富岳の次世代スパコン開発チームでAI研究。
[haruki] 全国の5G基地局をクラウドで統合管理するプロジェクトリーダー。
[haruki] 官公庁のデジタル庁で、自治体DXのシステム設計を主導。
[nana] どれも、社会のインフラを作る仕事…', '10年後、たとえばこんな場面', '富岳次世代開発 / 5Gクラウド統合 / 官公庁DX設計', NULL, '["[nana] もし富士通に入ったら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。富岳の次世代スパコン開発チームでAI研究。", "[haruki] 全国の5G基地局をクラウドで統合管理するプロジェクトリーダー。", "[haruki] 官公庁のデジタル庁で、自治体DXのシステム設計を主導。", "[nana] どれも、社会のインフラを作る仕事…"]', 'H2: スーパーコンピュータ富岳(再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('fujitsu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/fujitsu/panel_10.png', 'both', '[haruki] 売上3兆5,501億円、営業利益2,650億円、採用約800名。
[nana] FMVのPC屋じゃなくて、日本のインフラを作る企業だったんだ。
[both] 89年、ずっと未来を作ってる。富士通、変革の真っ只中。', '89年、ずっと未来を作ってる。', '売上3.6兆円 / 営業利益2,650億円 / 採用約800名', NULL, '["[haruki] 売上3兆5,501億円、営業利益2,650億円、採用約800名。", "[nana] FMVのPC屋じゃなくて、日本のインフラを作る企業だったんだ。", "[both] 89年、ずっと未来を作ってる。富士通、変革の真っ只中。"]', 'H1: 川崎新本社(Kawasaki Tower・朝の光)', NULL);

-- ===== pia (ぴあ株式会社) =====
-- source: output/pia/scenario_v4.json
-- jsDelivr ref: @bf9c0d0a76a957f957be3cda35bd200ea80237c9
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('pia', 'ぴあ株式会社', 'advertising_media', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_01.png', 'nana', '[nana] 先週、ぴあアリーナMMでライブ行ったんだけどさ…
[haruki] うん、どうだった?
[nana] 会場の名前が『ぴあ』で、チケット買ったのも『チケットぴあ』で、運営スタッフのジャケットにも『ぴあ』って書いてあって。
[haruki] 気づいちゃった? ぴあって、会場も流通も全部やってる会社なんだ。', '会場も、チケットも、運営も、ぴあ', 'ぴあ株式会社 / 4337 / 感動のライフライン', NULL, '["[nana] 先週、ぴあアリーナMMでライブ行ったんだけどさ…", "[haruki] うん、どうだった?", "[nana] 会場の名前が『ぴあ』で、チケット買ったのも『チケットぴあ』で、運営スタッフのジャケットにも『ぴあ』って書いてあって。", "[haruki] 気づいちゃった? ぴあって、会場も流通も全部やってる会社なんだ。"]', 'H1: ぴあアリーナMM', '{"location": "アリーナ建物上部の外壁", "object_type": "施設サイン (ぴあアリーナMM)", "brand_form": "ガラスファサード上部に『ぴあアリーナMM』の発光サイン、白色LED", "attachment": "建物外壁に固定", "scale_note": "実在のアリーナ外観サインと同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_02.png', 'haruki', '[haruki] ぴあの本業は『チケット流通』。年間で約5,500万枚を扱ってる。
[nana] 5,500万枚!? そんなに?
[haruki] コンサート、スポーツ、演劇、映画…全部ぴあ経由。1984年の電話予約から、今は専用端末とWebで。
[nana] 私がチケットぴあの端末で発券したチケット、全部ぴあのシステムだったんだ…', '年間約5,500万枚のチケット流通', 'コンサート/スポーツ/演劇/映画 すべて', '企業公式サイト', '["[haruki] ぴあの本業は『チケット流通』。年間で約5,500万枚を扱ってる。", "[nana] 5,500万枚!? そんなに?", "[haruki] コンサート、スポーツ、演劇、映画…全部ぴあ経由。1984年の電話予約から、今は専用端末とWebで。", "[nana] 私がチケットぴあの端末で発券したチケット、全部ぴあのシステムだったんだ…"]', 'H3: チケットぴあ店舗端末', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_03.png', 'haruki', '[haruki] ぴあアリーナMMは、民間企業が単独で建てた日本初の1万人規模音楽専用アリーナ。
[nana] 民間単独で!? 普通は自治体とかと一緒じゃないの?
[haruki] そう。でもぴあは『チケットを売る会社』から『会場を作る会社』に進化した。
[nana] チケットだけじゃ足りなくて、箱ごと作っちゃったんだ…', '民間単独で1万人アリーナを建設', 'ぴあアリーナMM / 国内初の挑戦 / 2020年開業', NULL, '["[haruki] ぴあアリーナMMは、民間企業が単独で建てた日本初の1万人規模音楽専用アリーナ。", "[nana] 民間単独で!? 普通は自治体とかと一緒じゃないの?", "[haruki] そう。でもぴあは『チケットを売る会社』から『会場を作る会社』に進化した。", "[nana] チケットだけじゃ足りなくて、箱ごと作っちゃったんだ…"]', 'H1: ぴあアリーナMM (再使用)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_04.png', 'haruki', '[haruki] ぴあは1972年、創業者の矢内廣が学生起業で始めた。最初は雑誌。
[nana] この表紙、見たことある! お母さんが持ってた…
[haruki] 2011年に休刊したけど、チケット事業が育って、今は会場まで作ってる。50年で3回進化した。
[nana] 雑誌で情報を届けて、チケットで体験を届けて、会場で感動を作る…', '1972年学生起業、50年で3回進化', '雑誌→チケット流通→会場運営 / 創業者 矢内廣 現役', NULL, '["[haruki] ぴあは1972年、創業者の矢内廣が学生起業で始めた。最初は雑誌。", "[nana] この表紙、見たことある! お母さんが持ってた…", "[haruki] 2011年に休刊したけど、チケット事業が育って、今は会場まで作ってる。50年で3回進化した。", "[nana] 雑誌で情報を届けて、チケットで体験を届けて、会場で感動を作る…"]', 'H4: 雑誌『ぴあ』表紙イラスト', '{"location": "壁面中央の額装", "object_type": "雑誌『ぴあ』表紙 (及川正通イラスト)", "brand_form": "1975年9月号からの表紙イラスト、カラフルな人物画、『ぴあ』ロゴ", "attachment": "額縁に入れて壁に掛けられている", "scale_note": "実在の雑誌サイズ (A4変形) の表紙"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_05.png', 'nana', '[nana] 年収は?
[haruki] 平均787万円。初任給は基本給23万4,000円で、部門によっては固定残業手当が10万3,000円つく。
[nana] 固定残業、結構大きいね…
[haruki] イベント業界だから、繁忙期は深夜対応も普通。その分、給与に織り込まれてる構造。
[nana] エンタメの裏側って、こういう働き方なんだ…', '787万円 (平均) + イベント連動型', '初任給 23.4万円 / 固定残業込み構造', '有価証券報告書 2024年3月期', '["[nana] 年収は?", "[haruki] 平均787万円。初任給は基本給23万4,000円で、部門によっては固定残業手当が10万3,000円つく。", "[nana] 固定残業、結構大きいね…", "[haruki] イベント業界だから、繁忙期は深夜対応も普通。その分、給与に織り込まれてる構造。", "[nana] エンタメの裏側って、こういう働き方なんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_06.png', 'nana', '[OB先輩] 配属は希望を聞くけど、チケット・会場・企画の3部署をローテーションで回ることが多い。
[OB先輩] イベント当日は深夜2時まで対応とか、普通にある。翌朝9時出社も。
[nana] それ、結構ハード…
[OB先輩] でも、ライブが終わってお客さんの笑顔を見たとき、『感動のライフライン』を作ってる実感がある。', 'イベント当日は深夜2時まで対応', '3部署ローテ / 繁忙期の厳しさは現実', NULL, '["[OB先輩] 配属は希望を聞くけど、チケット・会場・企画の3部署をローテーションで回ることが多い。", "[OB先輩] イベント当日は深夜2時まで対応とか、普通にある。翌朝9時出社も。", "[nana] それ、結構ハード…", "[OB先輩] でも、ライブが終わってお客さんの笑顔を見たとき、『感動のライフライン』を作ってる実感がある。"]', 'H2: 豊洲PIT', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_07.png', 'nana', '[OB先輩] ぴあが大切にしているのは、『経済性と趣旨性のバランス』。
[nana] 経済性と趣旨性?
[OB先輩] 儲けることと、エンタメの価値を守ること。両方のバランスを取りながら、蛇行前進で進む。
[haruki] 採用も、この理念に共感できる人を見てる。エンタメを本気で『生き生きの酸素』だと思える人。', '経済性と趣旨性のバランス', '蛇行前進 / エンタメを酸素と考える人', NULL, '["[OB先輩] ぴあが大切にしているのは、『経済性と趣旨性のバランス』。", "[nana] 経済性と趣旨性?", "[OB先輩] 儲けることと、エンタメの価値を守ること。両方のバランスを取りながら、蛇行前進で進む。", "[haruki] 採用も、この理念に共感できる人を見てる。エンタメを本気で『生き生きの酸素』だと思える人。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_08.png', 'nana', '[nana] 大阪・関西万博のチケットって…
[haruki] そう、ぴあが受託してる。東京2025世界陸上も。
[nana] 国家級のイベントまで、ぴあが関わってるんだ…
[haruki] チケット流通で培った信頼が、こういう大型案件に繋がってる。', '大阪・関西万博も、世界陸上も、ぴあ', '国家級イベントの信頼 / チケッティング受託', NULL, '["[nana] 大阪・関西万博のチケットって…", "[haruki] そう、ぴあが受託してる。東京2025世界陸上も。", "[nana] 国家級のイベントまで、ぴあが関わってるんだ…", "[haruki] チケット流通で培った信頼が、こういう大型案件に繋がってる。"]', 'H6: 大阪・関西万博チケット販売', '{"location": "チケット販売ブースの上部", "object_type": "ぴあロゴ入りサイン", "brand_form": "『ぴあ』のロゴ、青地に白文字", "attachment": "ブース上部に掲示", "scale_note": "実在の販売ブースサイン相当"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。東京駅直結の八重洲劇場で新プログラムを企画。
[haruki] ぴあアリーナMMで、アーティストと直接交渉して興行を作る。
[haruki] 海外の音楽フェスで、日本のチケット流通モデルを輸出する。
[nana] どれも、感動を作る最前線だ…', '10年後、たとえばこんな場面', '八重洲劇場 / ぴあアリーナMM / 海外フェス', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。東京駅直結の八重洲劇場で新プログラムを企画。", "[haruki] ぴあアリーナMMで、アーティストと直接交渉して興行を作る。", "[haruki] 海外の音楽フェスで、日本のチケット流通モデルを輸出する。", "[nana] どれも、感動を作る最前線だ…"]', 'H7: 東京・八重洲劇場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('pia', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/pia/panel_10.png', 'both', '[haruki] 売上553億円、営業利益43億円、過去最高。採用は例年20人。
[nana] チケットだけじゃなくて、会場も作って、感動を最初から最後まで設計してるんだ。
[both] 感動のライフライン、ここから始まる。ぴあ、50年の進化は続く。', '感動のライフライン、ここから始まる', '売上 553億円 / 営業利益 43億円 / 採用 約20名', NULL, '["[haruki] 売上553億円、営業利益43億円、過去最高。採用は例年20人。", "[nana] チケットだけじゃなくて、会場も作って、感動を最初から最後まで設計してるんだ。", "[both] 感動のライフライン、ここから始まる。ぴあ、50年の進化は続く。"]', 'H1: ぴあアリーナMM (夕暮れ)', NULL);

-- ===== kepco (関西電力株式会社) =====
-- source: output/kepco/scenario_v4.json
-- jsDelivr ref: @bf9c0d0a76a957f957be3cda35bd200ea80237c9
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('kepco', '関西電力株式会社', 'infra_energy', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_01.png', 'haruki', '[haruki] ナナ、停電って何回経験した?
[nana] え、停電? …ほとんどない、かも。
[haruki] 関西で停電がほぼゼロ。それ、誰かが24時間365日守ってるからだよ。
[nana] 関西電力…当たり前すぎて、気づかなかった。', '停電、何回経験した?', '関西電力 / 9503 / あたりまえを守る仕事', NULL, '["[haruki] ナナ、停電って何回経験した?", "[nana] え、停電? …ほとんどない、かも。", "[haruki] 関西で停電がほぼゼロ。それ、誰かが24時間365日守ってるからだよ。", "[nana] 関西電力…当たり前すぎて、気づかなかった。"]', 'H1: 関西電力本社ビル(大阪・中之島)', '{"location": "本社ビル上部", "object_type": "企業ロゴサイン", "brand_form": "ビル上部に『KEPCO』のサイン、控えめに", "attachment": "ビル外壁に固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_02.png', 'haruki', '[haruki] 関西電力、売上高4兆3,371億円。営業利益4,689億円。
[nana] 4兆円!? そんなに…
[haruki] 関西2府4県、約1,300万世帯に電気を届けてる。大阪、京都、兵庫、奈良、滋賀、和歌山。
[nana] 私の家も、学校も、この街ぜんぶ…関電の送電網が支えてたんだ。', '売上4.3兆円、関西2府4県を支える', '約1,300万世帯 / 送電網で暮らしを止めない', '2025年3月期決算', '["[haruki] 関西電力、売上高4兆3,371億円。営業利益4,689億円。", "[nana] 4兆円!? そんなに…", "[haruki] 関西2府4県、約1,300万世帯に電気を届けてる。大阪、京都、兵庫、奈良、滋賀、和歌山。", "[nana] 私の家も、学校も、この街ぜんぶ…関電の送電網が支えてたんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_03.png', 'haruki', '[haruki] これが黒部ダム。1963年、関西電力が7年かけて作った。
[nana] 7年!? この山の中に…
[haruki] 世紀の難工事って呼ばれた。171人が殉職して、関西の電力を支える発電所を完成させた。
[nana] 当たり前の電気の裏に、こんな歴史があったんだ…', '黒部ダム、世紀の難工事', '1963年竣工 / 7年の歳月 / 関西の電力を支える', NULL, '["[haruki] これが黒部ダム。1963年、関西電力が7年かけて作った。", "[nana] 7年!? この山の中に…", "[haruki] 世紀の難工事って呼ばれた。171人が殉職して、関西の電力を支える発電所を完成させた。", "[nana] 当たり前の電気の裏に、こんな歴史があったんだ…"]', 'H2: 黒部川第四発電所(くろよん)', '{"location": "ダム堰堤上部またはPR看板", "object_type": "黒部ダム名称表示", "brand_form": "ダム堰堤または看板に『黒部ダム』の表示、石彫またはプレート", "attachment": "堰堤またはPR施設に固定", "scale_note": "実在の表示サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_04.png', 'haruki', '[haruki] 関西電力は、日本で最初に原子力発電所を開設した会社。美浜、高浜、大飯…
[nana] 福島の事故の後、大変だったよね…
[haruki] 全原発が停止して、火力発電に切り替えて電気を守り続けた。今も再稼働と安全対策の最前線。
[nana] 簡単じゃない…当たり前を守るって、こういうことなんだ。', '原子力と火力、両方で守る', '美浜・高浜・大飯 / 福島後も電気を止めなかった', NULL, '["[haruki] 関西電力は、日本で最初に原子力発電所を開設した会社。美浜、高浜、大飯…", "[nana] 福島の事故の後、大変だったよね…", "[haruki] 全原発が停止して、火力発電に切り替えて電気を守り続けた。今も再稼働と安全対策の最前線。", "[nana] 簡単じゃない…当たり前を守るって、こういうことなんだ。"]', 'H3: 美浜原子力発電所 + H6: 送配電鉄塔', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_05.png', 'nana', '[nana] でも、インフラ企業って年収は…
[haruki] 平均973万円。商社ほど派手じゃないけど、長期で安定して上がる。
[haruki] 2026年度は初任給を26万8,600円に改定した。インフラ職は短期の業績に左右されない報酬構造。
[nana] 派手じゃないけど、ずっと続けられる…それがインフラなんだ。', '973万円(平均)+長期安定報酬', '2026年度初任給26.8万円に改定 / インフラ職の構造', '2025年3月期有報・日経報道', '["[nana] でも、インフラ企業って年収は…", "[haruki] 平均973万円。商社ほど派手じゃないけど、長期で安定して上がる。", "[haruki] 2026年度は初任給を26万8,600円に改定した。インフラ職は短期の業績に左右されない報酬構造。", "[nana] 派手じゃないけど、ずっと続けられる…それがインフラなんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_06.png', 'nana', '[OB先輩] 入社後、発電所か変電所か送配電の現場に配属される人が多い。
[OB先輩] 大阪本社じゃなくて、福井の原発、和歌山の火力、滋賀の変電所…地方勤務は覚悟してほしい。
[OB先輩] 24時間シフトもある。停電対応は深夜でも出動。当たり前を守るのは、現場から。
[nana] (静かに) 本社のデスクじゃなくて、現場で守る仕事なんだ…', '現場配属、24時間シフト', '発電所・変電所・送配電 / 地方勤務は普通', NULL, '["[OB先輩] 入社後、発電所か変電所か送配電の現場に配属される人が多い。", "[OB先輩] 大阪本社じゃなくて、福井の原発、和歌山の火力、滋賀の変電所…地方勤務は覚悟してほしい。", "[OB先輩] 24時間シフトもある。停電対応は深夜でも出動。当たり前を守るのは、現場から。", "[nana] (静かに) 本社のデスクじゃなくて、現場で守る仕事なんだ…"]', 'H6: 送配電鉄塔・変電所', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_07.png', 'nana', '[OB先輩] 関西電力が大事にしてるのは、公正・誠実・共感・挑戦。
[OB先輩] 当たり前を守るには誠実さ、新しい挑戦には共感と公正さが要る。採用では、この4つの価値観に共鳴できるかを見てる。
[nana] (静かに) 倍率じゃなくて、価値観で選ぶ会社なんだ…
[haruki] 当たり前を守り、創る。そのための人を探してる。', '公正・誠実・共感・挑戦', '価値観で選ぶ採用 / あたりまえを守り、創る', NULL, '["[OB先輩] 関西電力が大事にしてるのは、公正・誠実・共感・挑戦。", "[OB先輩] 当たり前を守るには誠実さ、新しい挑戦には共感と公正さが要る。採用では、この4つの価値観に共鳴できるかを見てる。", "[nana] (静かに) 倍率じゃなくて、価値観で選ぶ会社なんだ…", "[haruki] 当たり前を守り、創る。そのための人を探してる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_08.png', 'nana', '[nana] あれ、うちのネット、eo光って…
[haruki] そう、eo光は関西電力のグループ会社オプテージが運営してる。
[nana] 電気だけじゃなくて、ネットもスマホも関電だったの!?
[haruki] 電力・ガス・通信・生活サービス。関西の暮らし全体を支えてる総合エネルギー企業。', '電気も、ネットも、関西電力', 'eo光(オプテージ) / 電力・ガス・通信', NULL, '["[nana] あれ、うちのネット、eo光って…", "[haruki] そう、eo光は関西電力のグループ会社オプテージが運営してる。", "[nana] 電気だけじゃなくて、ネットもスマホも関電だったの!?", "[haruki] 電力・ガス・通信・生活サービス。関西の暮らし全体を支えてる総合エネルギー企業。"]', NULL, '{"location": "ルーター本体", "object_type": "eoロゴ", "brand_form": "ルーター上部に『eo』のロゴ、青と白", "attachment": "機器本体に印刷", "scale_note": "実在のeo光ルーターと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。高浜原発の制御室で安全運転を統括。
[haruki] 大阪本社で再生可能エネルギーの新規事業を企画。
[haruki] 和歌山の変電所で深夜の緊急点検、停電ゼロを守り続ける。
[nana] 派手じゃないけど、誰かの当たり前を守る。それが自分の誇りになる。', '10年後、たとえばこんな場面', '原発制御室 / 再エネ企画 / 深夜点検', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。高浜原発の制御室で安全運転を統括。", "[haruki] 大阪本社で再生可能エネルギーの新規事業を企画。", "[haruki] 和歌山の変電所で深夜の緊急点検、停電ゼロを守り続ける。", "[nana] 派手じゃないけど、誰かの当たり前を守る。それが自分の誇りになる。"]', 'H4: 高浜原子力発電所 + H6: 送配電鉄塔', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('kepco', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/kepco/panel_10.png', 'both', '[haruki] 売上4.3兆円、営業利益4,689億円、採用366名。
[nana] 当たり前すぎて見えなかったけど、誰かが守り続けてる。
[both] あたりまえを、守り続ける。関西電力、1951年から今日まで。', 'あたりまえを、守り続ける。', '売上4.3兆円 / 営業利益4,689億円 / 採用366名', NULL, '["[haruki] 売上4.3兆円、営業利益4,689億円、採用366名。", "[nana] 当たり前すぎて見えなかったけど、誰かが守り続けてる。", "[both] あたりまえを、守り続ける。関西電力、1951年から今日まで。"]', 'H1: 関西電力本社ビル(朝の光)', NULL);

-- ===== line-yahoo (LINEヤフー株式会社) =====
-- source: output/line-yahoo/scenario_v4.json
-- jsDelivr ref: @bf9c0d0a76a957f957be3cda35bd200ea80237c9
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('line-yahoo', 'LINEヤフー株式会社', 'it_ai_saas', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_01.png', 'haruki', '[haruki] このアイコン、今日何回開いた?
[nana] え? LINE? もう…10回以上は開いてるかも。
[haruki] 日本人の9割、9,700万人が毎日開くアプリ。
[nana] それって…LINEヤフーの話?', 'このアイコン、今日何回開いた?', 'LINEヤフー / 4689 / 9,700万人の日常インフラ', NULL, '["[haruki] このアイコン、今日何回開いた?", "[nana] え? LINE? もう…10回以上は開いてるかも。", "[haruki] 日本人の9割、9,700万人が毎日開くアプリ。", "[nana] それって…LINEヤフーの話?"]', 'H2: LINEアプリのグリーンアイコン', '{"location": "ナナの手元のスマホ画面中央", "object_type": "LINEアプリのトーク画面", "brand_form": "緑色の吹き出しアイコンと白いトーク背景、画面上部に『LINE』ロゴ", "attachment": "スマホ画面に表示", "scale_note": "実在のLINEアプリUIと同じ配色・レイアウト"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_02.png', 'haruki', '[haruki] LINE、Yahoo! JAPAN、PayPay、ZOZOTOWN。全部、同じ会社。
[nana] え、全部!? Yahoo!とLINEって別じゃないの?
[haruki] 2023年10月に統合。売上1兆9,174億円、営業利益3,150億円。
[nana] 私の1日、ぜんぶLINEヤフーの中を回ってる…', 'LINE・Yahoo!・PayPay・ZOZOTOWN', '全部、同じ会社 / 売上1.9兆円', NULL, '["[haruki] LINE、Yahoo! JAPAN、PayPay、ZOZOTOWN。全部、同じ会社。", "[nana] え、全部!? Yahoo!とLINEって別じゃないの?", "[haruki] 2023年10月に統合。売上1兆9,174億円、営業利益3,150億円。", "[nana] 私の1日、ぜんぶLINEヤフーの中を回ってる…"]', 'H3: Yahoo! JAPANトップページ', '{"location": "PC画面中央上部", "object_type": "Yahoo! JAPANロゴ", "brand_form": "赤い『Y!』ロゴと『Yahoo! JAPAN』テキスト、白背景", "attachment": "PC画面に表示", "scale_note": "実在のYahoo! JAPANトップページと同じ配色"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_03.png', 'nana', '[nana] 朝起きて最初に開くアプリ、メッセージかも。
[haruki] 連絡アプリは、いまや国民の連絡インフラ。検索もニュースもショッピングも、同じ会社が運営してる。
[nana] 連絡も、ニュースも、買い物も…全部?
[haruki] 毎日使うあのアプリを作ってるのが、LINEヤフーなんだ。', '毎日使う連絡・検索・ニュースの基盤', '連絡アプリ／検索／ニュース／ショッピング', 'LINEヤフー公式', '["[nana] 朝起きて最初に開くアプリ、メッセージかも。", "[haruki] 連絡アプリは、いまや国民の連絡インフラ。検索もニュースもショッピングも、同じ会社が運営してる。", "[nana] 連絡も、ニュースも、買い物も…全部?", "[haruki] 毎日使うあのアプリを作ってるのが、LINEヤフーなんだ。"]', 'H4: PayPayの赤いロゴマーク', '{"location": "レジ端末の画面とナナのスマホ画面", "object_type": "PayPayロゴ", "brand_form": "赤と白の『PayPay』ロゴ、QRコード決済画面", "attachment": "端末画面とスマホ画面に表示", "scale_note": "実在のPayPay決済UIと同じ配色"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_04.png', 'nana', '[nana] あ、ZOZOの配送トラック。この前これで服買った。
[haruki] ZOZOもLINEヤフーのグループ。Yahoo!ショッピング、ヤフオク!も全部。
[nana] え、ファッションECも、オークションも!?
[haruki] メッセンジャー、検索、決済、EC。日本最大級のライフプラットフォーム。', 'ZOZOTOWN・Yahoo!ショッピング・ヤフオク!', '全部LINEヤフー / 日本最大級ライフプラットフォーム', NULL, '["[nana] あ、ZOZOの配送トラック。この前これで服買った。", "[haruki] ZOZOもLINEヤフーのグループ。Yahoo!ショッピング、ヤフオク!も全部。", "[nana] え、ファッションECも、オークションも!?", "[haruki] メッセンジャー、検索、決済、EC。日本最大級のライフプラットフォーム。"]', 'H5: ZOZOTOWNの配送トラック', '{"location": "配送トラックの側面中央", "object_type": "ZOZOTOWNロゴ", "brand_form": "白地に黒文字で『ZOZOTOWN』、ファッションECを象徴するシンプルなタイポグラフィ", "attachment": "トラック側面に印刷", "scale_note": "実在のZOZO配送トラックと同じデザイン"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_05.png', 'nana', '[nana] でも、年収は…?
[haruki] 平均884万円。ただし職種で大きく違う。
[haruki] 学部卒430万円、修士470万円、博士530万円。エンジニア専門職は500〜770万円。
[nana] 専門性で決まる構造なんだ。2027年度入社のエンジニアは初任給650万円以上に引き上げるって…', '平均884万円=職種×専門性', '学部430万〜エンジニア専門職770万 / 2027年度エンジニア初任給650万円〜', '有価証券報告書・公式採用サイト', '["[nana] でも、年収は…?", "[haruki] 平均884万円。ただし職種で大きく違う。", "[haruki] 学部卒430万円、修士470万円、博士530万円。エンジニア専門職は500〜770万円。", "[nana] 専門性で決まる構造なんだ。2027年度入社のエンジニアは初任給650万円以上に引き上げるって…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_06.png', 'haruki', '[haruki] 採用は404名。ビジネス職、エンジニア職、デザイナー職、データ職で分かれる。
[nana] 404名!? それだけ採るの?
[haruki] でも配属は専門性重視。エンジニアは技術スタック、ビジネス職は事業部門で希望が通りやすい。
[nana] 大量採用だけど、職種ごとに明確に分かれてるんだ…', '採用404名、専門性で配属', 'ビジネス・エンジニア・デザイナー・データ職 / 職種別採用', '公式採用サイト2024年度実績', '["[haruki] 採用は404名。ビジネス職、エンジニア職、デザイナー職、データ職で分かれる。", "[nana] 404名!? それだけ採るの?", "[haruki] でも配属は専門性重視。エンジニアは技術スタック、ビジネス職は事業部門で希望が通りやすい。", "[nana] 大量採用だけど、職種ごとに明確に分かれてるんだ…"]', 'H1: 東京ガーデンテラス紀尾井町 紀尾井タワー', '{"location": "タワー上部の外壁", "object_type": "LINEヤフー社名サイン", "brand_form": "ガラスファサード上部に『LINEヤフー』のレリーフサイン、控えめに", "attachment": "タワー外壁に固定", "scale_note": "実在の本社タワーと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_07.png', 'nana', '[OB社員] LINEヤフーが大切にするのは『ユーザーファースト・やりぬく・少数精鋭』の3つ。
[OB社員] 選考で見るのは、圧倒的な当事者意識と、データを基に俯瞰で判断できるか。
[nana] ユーザーファースト…9,700万人の日常を支える責任、ってこと?
[haruki] WOW Our Users!。日常に『！』を届ける。それが理念。', 'ユーザーファースト・やりぬく・少数精鋭', 'WOW Our Users! / 当事者意識×専門性で選ぶ', NULL, '["[OB社員] LINEヤフーが大切にするのは『ユーザーファースト・やりぬく・少数精鋭』の3つ。", "[OB社員] 選考で見るのは、圧倒的な当事者意識と、データを基に俯瞰で判断できるか。", "[nana] ユーザーファースト…9,700万人の日常を支える責任、ってこと?", "[haruki] WOW Our Users!。日常に『！』を届ける。それが理念。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_08.png', 'nana', '[nana] このスタンプ、友達との会話で毎日使ってる。
[haruki] スタンプストアには数万種類。クリエイターが自由に制作・販売できる仕組み。
[nana] コミュニケーションのプラットフォームなんだ…
[haruki] LINE、Yahoo!、PayPay、ZOZOTOWN。全部が日常に『！』を届けるための土台。', 'LINEスタンプ、数万種類の創造', 'クリエイター×ユーザー / コミュニケーションのプラットフォーム', NULL, '["[nana] このスタンプ、友達との会話で毎日使ってる。", "[haruki] スタンプストアには数万種類。クリエイターが自由に制作・販売できる仕組み。", "[nana] コミュニケーションのプラットフォームなんだ…", "[haruki] LINE、Yahoo!、PayPay、ZOZOTOWN。全部が日常に『！』を届けるための土台。"]', 'H7: LINEスタンプストア', '{"location": "ナナの手元のスマホ画面全体", "object_type": "LINEスタンプストア画面", "brand_form": "緑色のヘッダーに『スタンプストア』、多彩なスタンプがグリッド表示", "attachment": "スマホ画面に表示", "scale_note": "実在のLINEスタンプストアUIと同じレイアウト"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どんな仕事してると思う?
[haruki] たとえば、こんな未来。紀尾井タワーでLINEの新機能を9,700万人へリリース。
[haruki] 地方都市の商店街で、PayPay加盟店を増やして地域経済を活性化。
[haruki] Yahoo!ニュース編集室で、AIが最適な記事を届けるアルゴリズムを設計。
[nana] どれも、毎日誰かの『！』になる仕事…', '10年後、たとえばこんな場面', '紀尾井タワー / 地方商店街 / ニュース編集室', NULL, '["[nana] もし入れたら、10年後どんな仕事してると思う?", "[haruki] たとえば、こんな未来。紀尾井タワーでLINEの新機能を9,700万人へリリース。", "[haruki] 地方都市の商店街で、PayPay加盟店を増やして地域経済を活性化。", "[haruki] Yahoo!ニュース編集室で、AIが最適な記事を届けるアルゴリズムを設計。", "[nana] どれも、毎日誰かの『！』になる仕事…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('line-yahoo', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@bf9c0d0a76a957f957be3cda35bd200ea80237c9/public/images/line-yahoo/panel_10.png', 'both', '[nana] 朝起きてから寝るまで、ずっとLINEヤフーと一緒だった。
[haruki] 売上1兆9,174億円、営業利益3,150億円、採用404名。
[both] 日常に！を、毎日9,700万人へ。LINEヤフー、ライフプラットフォームの現在地。', '日常に！を、毎日9,700万人へ。', '売上1.9兆円 / 営業利益3,150億円 / 採用404名', NULL, '["[nana] 朝起きてから寝るまで、ずっとLINEヤフーと一緒だった。", "[haruki] 売上1兆9,174億円、営業利益3,150億円、採用404名。", "[both] 日常に！を、毎日9,700万人へ。LINEヤフー、ライフプラットフォームの現在地。"]', 'H2: LINEアプリのグリーンアイコン(再使用)', '{"location": "ナナの手元のスマホ画面中央", "object_type": "LINEアプリアイコン", "brand_form": "緑色の吹き出しアイコン、画面が柔らかく光る", "attachment": "スマホ画面に表示", "scale_note": "実在のLINEアイコンと同じデザイン"}');

