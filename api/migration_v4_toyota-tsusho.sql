-- ===== toyota-tsusho (豊田通商株式会社) =====
-- source: output/toyota-tsusho/scenario_v4.json
-- jsDelivr ref: @2fa3409
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('toyota-tsusho', '豊田通商株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_01.png', 'nana', '[nana] アフリカでめちゃくちゃトヨタ車見るの、なんでだろう?
[haruki] あ、確かに…ランクルもハイラックスも、全部トヨタだ。
[nana] トヨタが直接売ってるのかな?
[haruki] それが、違うんだよ。アフリカでトヨタ車を売ってるのは、別の会社。', 'アフリカでトヨタ車だらけ、誰が?', '豊田通商 / 8015', NULL, '["[nana] アフリカでめちゃくちゃトヨタ車見るの、なんでだろう?", "[haruki] あ、確かに…ランクルもハイラックスも、全部トヨタだ。", "[nana] トヨタが直接売ってるのかな?", "[haruki] それが、違うんだよ。アフリカでトヨタ車を売ってるのは、別の会社。"]', 'H4: サバンナを走るトヨタ・ランドクルーザー (アフリカ街角の固有疑問)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_02.png', 'haruki', '[haruki] 売上9兆円。アフリカ事業だけで1兆円突破。
[nana] 1兆円!? 日本企業として初って書いてある…
[haruki] アフリカ54カ国・社員2万3,000人。豊田通商。
[nana] 名前すら聞いたことなかったのに、こんなにデカい…', 'アフリカ1兆円(日本企業初)', '売上 約9兆円 / 54カ国 / 23,000名', '公式 IR・FY2022', '["[haruki] 売上9兆円。アフリカ事業だけで1兆円突破。", "[nana] 1兆円!? 日本企業として初って書いてある…", "[haruki] アフリカ54カ国・社員2万3,000人。豊田通商。", "[nana] 名前すら聞いたことなかったのに、こんなにデカい…"]', 'H3: 港湾のトヨタ車キャリアカー (海外輸出の動脈)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_03.png', 'haruki', '[haruki] CFAO。豊田通商の100%子会社で、アフリカ最大の自動車販売網。
[nana] え、アフリカ54カ国でトヨタ車を売ってるのは…全部この会社?
[haruki] そう。修理工場・部品供給・ローン・保険まで一気通貫。
[nana] 商社って単に売り買いするだけじゃなくて、現地の経済の一部になってるんだ…', 'アフリカ最大の自動車販売網', 'CFAO (100%子会社)', NULL, '["[haruki] CFAO。豊田通商の100%子会社で、アフリカ最大の自動車販売網。", "[nana] え、アフリカ54カ国でトヨタ車を売ってるのは…全部この会社?", "[haruki] そう。修理工場・部品供給・ローン・保険まで一気通貫。", "[nana] 商社って単に売り買いするだけじゃなくて、現地の経済の一部になってるんだ…"]', 'H2: アフリカ街角のトヨタ販売店 CFAO (青空とトヨタ車)', '{"location": "ショールームの建物上部とエントランス上", "object_type": "CFAO の店舗サイン (商社の自社ブランド)", "brand_form": "白地に CFAO のロゴ (青または緑)。建物正面に控えめなサイズで設置。アフリカの空に映える形", "attachment": "ショールーム建物の構造の一部として設置", "scale_note": "実在のCFAO店舗と同じ通常サイズ。巨大化禁止"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_04.png', 'haruki', '[haruki] 売って終わりじゃない。輸出物流もアフター部品も、廃車になったらリサイクルまで。
[nana] 1台のトヨタ車を、海を渡って売って、走らせて、最後は素材に戻すまで?
[haruki] そう。ぜんぶ豊田通商が回してる。
[nana] そっか…『商社って何屋さん?』に、初めて自分の言葉で答えられそう。', '売る前から、廃車のあとまで', '輸出→販売→金融→部品→回収→リサイクル', NULL, '["[haruki] 売って終わりじゃない。輸出物流もアフター部品も、廃車になったらリサイクルまで。", "[nana] 1台のトヨタ車を、海を渡って売って、走らせて、最後は素材に戻すまで?", "[haruki] そう。ぜんぶ豊田通商が回してる。", "[nana] そっか…『商社って何屋さん?』に、初めて自分の言葉で答えられそう。"]', 'H6: トヨタリサイクル工場 (廃車解体ライン)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_05.png', 'nana', '[nana] 平均年収って、結局どんな水準なの?
[haruki] 有価証券報告書(単体・2025年3月期)によると平均1,320万円(平均年齢43.1歳)。でもね、ここからが豊田通商らしい。
[haruki] ベース給に加えて、海外駐在手当・ハードシップ手当が積み上がる仕組み。アフリカ駐在になると手当の比重がぐっと大きくなる。
[nana] 額より構造で見るんだ。どこに赴任するかで年収の中身がまるで変わるってことか。', '平均1,320万円(有報単体・2025年3月期)+駐在手当', '赴任地のハードシップ度合いで手当の比重が変わる仕組み', '日経会社情報 8015 / OpenWork等', '["[nana] 平均年収って、結局どんな水準なの?", "[haruki] 有価証券報告書(単体・2025年3月期)によると平均1,320万円(平均年齢43.1歳)。でもね、ここからが豊田通商らしい。", "[haruki] ベース給に加えて、海外駐在手当・ハードシップ手当が積み上がる仕組み。アフリカ駐在になると手当の比重がぐっと大きくなる。", "[nana] 額より構造で見るんだ。どこに赴任するかで年収の中身がまるで変わるってことか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_06.png', 'haruki', '[haruki] ここが名古屋本社。世界9兆円の動脈を、ここから動かしてる。
[nana] 東京じゃないんだ。名古屋…
[haruki] トヨタグループの『現地現物』が染み込んでる。社員が必ず現場に立つ文化。
[nana] 数字で語らず、現場で語る会社、ってことか。', '名古屋から、世界9兆円を動かす', '現地現物・人間性尊重 (トヨタイズム)', NULL, '["[haruki] ここが名古屋本社。世界9兆円の動脈を、ここから動かしてる。", "[nana] 東京じゃないんだ。名古屋…", "[haruki] トヨタグループの『現地現物』が染み込んでる。社員が必ず現場に立つ文化。", "[nana] 数字で語らず、現場で語る会社、ってことか。"]', 'H1: 豊田通商名古屋本社ビル (名駅前のオフィスビル)', '{"location": "名古屋本社ビル上部の外壁", "object_type": "建築サイン (社名表示)", "brand_form": "ビル上部の外壁に取り付けられた『豊田通商』または『Toyota Tsusho』のレリーフサイン", "attachment": "ビル外壁に金属ボルトで固定された建築サイン", "scale_note": "実在の本社ビルと同じ控えめな比率 (巨大化禁止)"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_07.png', 'nana', '[nana] 配属って、希望どおりに行けるんですか?
[OB先輩] 正直に言うと、第一希望そのまま通る人は半分くらい。アフリカ赴任は普通にある。
[OB先輩] 入社3〜5年で海外駐在に出る人が多い。覚悟は要る。でも、20代で国を任される経験ができる会社、他にそうない。
[haruki] 楽じゃないけど、若いうちにそれだけの裁量があるってことか…', 'アフリカ赴任は『普通にある』', '入社3〜5年で海外駐在 / 20代で国を任される', NULL, '["[nana] 配属って、希望どおりに行けるんですか?", "[OB先輩] 正直に言うと、第一希望そのまま通る人は半分くらい。アフリカ赴任は普通にある。", "[OB先輩] 入社3〜5年で海外駐在に出る人が多い。覚悟は要る。でも、20代で国を任される経験ができる会社、他にそうない。", "[haruki] 楽じゃないけど、若いうちにそれだけの裁量があるってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_08.png', 'nana', '[OB先輩] うちが見るのは、学歴じゃない。『現地・現物』で動けるか。
[OB先輩] アフリカの土埃の中で、現地のスタッフと汗をかいて、トラブルを直せるか。
[nana] (静かに) 学歴じゃない、ってシンプルに言われたの、初めてかも。
[haruki] 数字より、足を動かす人を取る会社、ってことか。', '見てるのは『現地・現物で動けるか』', '学歴じゃない。足を動かせるか', NULL, '["[OB先輩] うちが見るのは、学歴じゃない。『現地・現物』で動けるか。", "[OB先輩] アフリカの土埃の中で、現地のスタッフと汗をかいて、トラブルを直せるか。", "[nana] (静かに) 学歴じゃない、ってシンプルに言われたの、初めてかも。", "[haruki] 数字より、足を動かす人を取る会社、ってことか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来が見える。ケニア・モンバサ港でアフリカ全土の輸入物流を統括。
[haruki] ブラジル・サンパウロで水素ステーションをゼロから立ち上げる。
[haruki] 名古屋本社で世界の販売網に新しい仕組みを作る。
[nana] どれも、私の手で世界の地図が変わってる絵が見える…', '10年後、あなたが見ている景色', 'ケニア / ブラジル / 名古屋 — 3つの具体', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来が見える。ケニア・モンバサ港でアフリカ全土の輸入物流を統括。", "[haruki] ブラジル・サンパウロで水素ステーションをゼロから立ち上げる。", "[haruki] 名古屋本社で世界の販売網に新しい仕組みを作る。", "[nana] どれも、私の手で世界の地図が変わってる絵が見える…"]', 'H5: 水素ステーションとMIRAI (新事業領域の具体例)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('toyota-tsusho', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@2fa3409/public/images/toyota-tsusho/panel_10.png', 'both', '[haruki] アフリカ54カ国、社員2万3,000人。採用 約100人。
[nana] 倍率の話じゃなくて、どの国で、どんな仕事を自分のものにするか、ってことだね。
[both] 名古屋から、世界の地図を変えにいく。', '名古屋から、世界の地図を変えにいく。', 'アフリカ54カ国 / 社員23,000名 / 採用 約100名', NULL, '["[haruki] アフリカ54カ国、社員2万3,000人。採用 約100人。", "[nana] 倍率の話じゃなくて、どの国で、どんな仕事を自分のものにするか、ってことだね。", "[both] 名古屋から、世界の地図を変えにいく。"]', 'H4: サバンナを走るランドクルーザー (アフリカ事業の象徴)', NULL);
