-- ===== otsuka-hd (大塚ホールディングス株式会社) =====
-- source: output/otsuka-hd/scenario_v4.json
-- jsDelivr ref: @c7f21a626089c77db1a018936465b2cd331a66e8
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('otsuka-hd', '大塚ホールディングス株式会社', 'pharma_healthcare', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_01.png', 'nana', '[nana] 大塚ホールディングス、志望動機が思いつかない…
[haruki] え、今ポカリ飲みながら言ってるよね?
[nana] あ…
[haruki] ポカリもカロリーメイトもオロナミンCも、ぜんぶ大塚だよ。君の1日、大塚で支えられてる。', 'ポカリ飲みながら志望動機に悩む矛盾', '大塚ホールディングス / 4578 / 身近すぎて見えない会社', NULL, '["[nana] 大塚ホールディングス、志望動機が思いつかない…", "[haruki] え、今ポカリ飲みながら言ってるよね?", "[nana] あ…", "[haruki] ポカリもカロリーメイトもオロナミンCも、ぜんぶ大塚だよ。君の1日、大塚で支えられてる。"]', 'H2: ポカリスエットのボトル', '{"location": "テーブル中央", "object_type": "ポカリスエットのペットボトル", "brand_form": "青と白のパッケージ、POCARI SWEATロゴ", "attachment": "テーブルに置かれている", "scale_note": "実在の500mlペットボトルと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_02.png', 'haruki', '[haruki] 大塚HDは2本の柱で成り立ってる。医療関連事業とニュートラシューティカルズ関連事業。
[nana] ニュートラ…?
[haruki] 栄養と医薬の造語。ポカリやカロリーメイトは後者。でも売上の主力は医療用医薬品。
[nana] 薬局で見る飲料は、大塚のほんの一部だったんだ…', '医療とニュートラシューティカルズの二本柱', '32カ国・地域 182社 / 約38,000人', '公式HP', '["[haruki] 大塚HDは2本の柱で成り立ってる。医療関連事業とニュートラシューティカルズ関連事業。", "[nana] ニュートラ…?", "[haruki] 栄養と医薬の造語。ポカリやカロリーメイトは後者。でも売上の主力は医療用医薬品。", "[nana] 薬局で見る飲料は、大塚のほんの一部だったんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_03.png', 'nana', '[nana] これも、これも、大塚なんだ…
[haruki] カロリーメイトは科学的根拠に基づく栄養バランス食品。オロナミンCは『愛情一本。』
[nana] 受験勉強のとき、毎日食べてた。
[haruki] 君を支えてきた会社が、実は志望先だったんだよ。', '受験も、部活も、大塚と一緒だった', 'カロリーメイト / オロナミンC / ポカリスエット', NULL, '["[nana] これも、これも、大塚なんだ…", "[haruki] カロリーメイトは科学的根拠に基づく栄養バランス食品。オロナミンCは『愛情一本。』", "[nana] 受験勉強のとき、毎日食べてた。", "[haruki] 君を支えてきた会社が、実は志望先だったんだよ。"]', 'H4: カロリーメイトの箱 + H3: オロナミンCのガラス瓶', '{"location": "棚中央と右", "object_type": "カロリーメイトの箱とオロナミンCの瓶", "brand_form": "カロリーメイトは茶色の箱にCalorie Mateロゴ、オロナミンCは黄色い小瓶にORONAMIN Cロゴ", "attachment": "棚に陳列", "scale_note": "実在の商品サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_04.png', 'haruki', '[haruki] 大塚グループは1921年、大塚武三郎がここ鳴門で創業した。
[nana] 1921年…105年前!?
[haruki] 最初は注射用蒸留水から始まった。医療の基盤を作る仕事。
[nana] ポカリもカロリーメイトも、この小さな研究室から生まれたんだ…', '1921年、鳴門から105年の道', '大塚武三郎 / 注射用蒸留水 / 発祥の地', NULL, '["[haruki] 大塚グループは1921年、大塚武三郎がここ鳴門で創業した。", "[nana] 1921年…105年前!?", "[haruki] 最初は注射用蒸留水から始まった。医療の基盤を作る仕事。", "[nana] ポカリもカロリーメイトも、この小さな研究室から生まれたんだ…"]', 'H5: 大塚記念館(鳴門)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_05.png', 'nana', '[nana] 平均年収1,000万円って、製薬だとどうなの?
[haruki] 平均年齢46.9歳で1,000万円。中堅製薬の標準より少し上。
[haruki] でも大塚の年収は『105年の研究投資が生む長期リターン』。ポカリもカロリーメイトも、10年20年かけて開発した。
[nana] 短期じゃなくて、長く育てることで報いる構造なんだ…', '1,000万円+105年の研究投資リターン', '平均年齢46.9歳 / 長期開発への報い', '日経会社情報 4578', '["[nana] 平均年収1,000万円って、製薬だとどうなの?", "[haruki] 平均年齢46.9歳で1,000万円。中堅製薬の標準より少し上。", "[haruki] でも大塚の年収は『105年の研究投資が生む長期リターン』。ポカリもカロリーメイトも、10年20年かけて開発した。", "[nana] 短期じゃなくて、長く育てることで報いる構造なんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_06.png', 'nana', '[OB先輩] グループは182社あって、大塚製薬・大鵬薬品・大塚倉庫…配属先は多岐にわたる。
[OB先輩] 第一希望が通るとは限らない。医薬営業・研究開発・工場・物流、どこに配属されても大塚のDNAを背負う。
[OB先輩] 245名採用だけど、グループ全体で育てる。転勤も海外赴任も普通にある。
[nana] 大塚製薬に入りたい、だけじゃ足りないんだ…', '182社、配属先は多岐', '採用245名(2025年度・大塚製薬) / グループ全体で育成', NULL, '["[OB先輩] グループは182社あって、大塚製薬・大鵬薬品・大塚倉庫…配属先は多岐にわたる。", "[OB先輩] 第一希望が通るとは限らない。医薬営業・研究開発・工場・物流、どこに配属されても大塚のDNAを背負う。", "[OB先輩] 245名採用だけど、グループ全体で育てる。転勤も海外赴任も普通にある。", "[nana] 大塚製薬に入りたい、だけじゃ足りないんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_07.png', 'nana', '[OB先輩] 大塚のDNAは3つ。『流汗悟道』『実証』『創造性』。
[OB先輩] 流汗悟道は、汗を流して初めて道が開ける。倍率は高いけど、見てるのは『正解のない世界を進む胸の躍り』。
[nana] 汗を流して…道を悟る。ポカリの開発もそうだったんだ…
[haruki] 失敗を恐れずチャレンジする人。それが大塚の求める人物像。', '流汗悟道・実証・創造性', '正解のない世界を進む / 失敗を恐れない人', NULL, '["[OB先輩] 大塚のDNAは3つ。『流汗悟道』『実証』『創造性』。", "[OB先輩] 流汗悟道は、汗を流して初めて道が開ける。倍率は高いけど、見てるのは『正解のない世界を進む胸の躍り』。", "[nana] 汗を流して…道を悟る。ポカリの開発もそうだったんだ…", "[haruki] 失敗を恐れずチャレンジする人。それが大塚の求める人物像。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_08.png', 'haruki', '[haruki] 1968年、大塚製薬は日本初のプラスチック容器輸液を開発した。
[nana] プラスチック容器?
[haruki] それまでガラス瓶だった点滴を、割れないプラスチックに変えた。医療現場に革命を起こした。
[nana] ポカリだけじゃない。命を支える製品も、大塚が作ってる…', '1968年、日本初プラスチック輸液', '医療現場に革命 / 命を支える製品', NULL, '["[haruki] 1968年、大塚製薬は日本初のプラスチック容器輸液を開発した。", "[nana] プラスチック容器?", "[haruki] それまでガラス瓶だった点滴を、割れないプラスチックに変えた。医療現場に革命を起こした。", "[nana] ポカリだけじゃない。命を支える製品も、大塚が作ってる…"]', 'H6: 輸液バッグ(点滴製剤)', '{"location": "壁のフックに掛かっている", "object_type": "輸液バッグ(点滴製剤)", "brand_form": "透明なプラスチック袋、点滴の管", "attachment": "壁のフックに掛けられている", "scale_note": "実在の輸液バッグと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。研究所でポカリの次世代製品を開発。
[haruki] 東南アジアの病院で、大塚の輸液バッグ導入を支援。
[haruki] 鳴門の記念館で、創業105年を次の世代に語り継ぐイベントを企画。
[nana] 身近な製品から、世界の医療まで。どれも、汗を流して道を拓く仕事。', '10年後、たとえばこんな場面', '研究所 / 東南アジア / 鳴門記念館', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。研究所でポカリの次世代製品を開発。", "[haruki] 東南アジアの病院で、大塚の輸液バッグ導入を支援。", "[haruki] 鳴門の記念館で、創業105年を次の世代に語り継ぐイベントを企画。", "[nana] 身近な製品から、世界の医療まで。どれも、汗を流して道を拓く仕事。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('otsuka-hd', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@c7f21a626089c77db1a018936465b2cd331a66e8/public/images/otsuka-hd/panel_10.png', 'both', '[haruki] 採用245名、平均年収1,000万円、グループ182社。
[nana] 毎日飲んでたポカリが、こんなに深い会社だったなんて。
[both] 汗の数だけ、道がある。大塚ホールディングス、105年の現在地。', '汗の数だけ、道がある。', '採用245名 / 平均年収1,000万円 / グループ182社', NULL, '["[haruki] 採用245名、平均年収1,000万円、グループ182社。", "[nana] 毎日飲んでたポカリが、こんなに深い会社だったなんて。", "[both] 汗の数だけ、道がある。大塚ホールディングス、105年の現在地。"]', 'H1: 品川グランドセントラルタワー + H2: ポカリスエット再登場', '{"location": "ベンチの上", "object_type": "ポカリスエットのペットボトル", "brand_form": "青と白のパッケージ、POCARI SWEATロゴ", "attachment": "ベンチに置かれている", "scale_note": "実在の500mlペットボトルと同じサイズ"}');
