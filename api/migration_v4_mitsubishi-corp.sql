-- ===== mitsubishi-corp (三菱商事株式会社) =====
-- source: output/mitsubishi-corp/scenario_v4.json
-- jsDelivr ref: @29041ca
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('mitsubishi-corp', '三菱商事株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_01.png', 'nana', '[nana] 丸の内って、なんで三菱の建物だらけなんだろ?
[haruki] 丸の内には、三菱地所、三菱UFJ、三菱重工、三菱商事…など、三菱系の会社が集まっているよ。
[nana] みんな『三菱村』って呼んでるらしい。
[haruki] それは三菱が丸の内で150年前から続いてるって知ったら、見方変わるかも。', '丸の内って、なんで三菱村?', '三菱商事 / 8058 / 150年の起点', NULL, '["[nana] 丸の内って、なんで三菱の建物だらけなんだろ?", "[haruki] 丸の内には、三菱地所、三菱UFJ、三菱重工、三菱商事…など、三菱系の会社が集まっているよ。", "[nana] みんな『三菱村』って呼んでるらしい。", "[haruki] それは三菱が丸の内で150年前から続いてるって知ったら、見方変わるかも。"]', 'H1: 丸の内パークビルディング本社 (赤いスリーダイヤサイン)', '{"location": "丸の内パークビルディング本社上部の外壁", "object_type": "建築サイン (社名+三菱マーク)", "brand_form": "赤いスリーダイヤと『三菱商事』の漢字サイン、ビル外壁に控えめなサイズで設置", "attachment": "ビル外壁の建築サインとして固定", "scale_note": "実在の本社ビルと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_02.png', 'haruki', '[haruki] 1870年代、岩崎弥太郎が土佐藩の船を引き継いで始めたのが海運業。
[nana] スリーダイヤって、土佐藩主の家紋と岩崎家の家紋を合わせたんだって。
[haruki] そう。海から始まって、今は10事業グループで売上19兆円。
[nana] 150年で、海運1社が、世界に展開していったってこと…', '1870年代、海運から始まった', '今 売上 約19兆円 / 10事業グループ', NULL, '["[haruki] 1870年代、岩崎弥太郎が土佐藩の船を引き継いで始めたのが海運業。", "[nana] スリーダイヤって、土佐藩主の家紋と岩崎家の家紋を合わせたんだって。", "[haruki] そう。海から始まって、今は10事業グループで売上19兆円。", "[nana] 150年で、海運1社が、世界に展開していったってこと…"]', 'H7: 三菱マーク入りコンテナと港湾', '{"location": "中景のコンテナ複数の側面", "object_type": "三菱マーク (スリーダイヤ)", "brand_form": "赤いスリーダイヤがコンテナ側面に印刷", "attachment": "コンテナの塗装の一部", "scale_note": "実在のコンテナと同じ控えめな比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_03.png', 'nana', '[nana] 三綱領、これって約90年前にできた指針なんだって。
[haruki] 所期奉公・処事光明・立業貿易。事業を通じて社会に奉公する、という意味なんだ。
[nana] 約90年前の言葉が、今の19兆円を動かしてるんだ…
[haruki] 90年前の言葉が今も通じる＝それだけブレない軸がある、ってことだよ。', '1934年から変わらない、指針', '所期奉公 / 処事光明 / 立業貿易', NULL, '["[nana] 三綱領、これって約90年前にできた指針なんだって。", "[haruki] 所期奉公・処事光明・立業貿易。事業を通じて社会に奉公する、という意味なんだ。", "[nana] 約90年前の言葉が、今の19兆円を動かしてるんだ…", "[haruki] 90年前の言葉が今も通じる＝それだけブレない軸がある、ってことだよ。"]', 'H5: 三綱領の額・石碑', '{"location": "ロビー壁面の中央", "object_type": "理念の額 (書道作品の額装)", "brand_form": "『所期奉公 / 処事光明 / 立業貿易』が縦書きで書かれた書、木製の額装", "attachment": "壁面に固定された額", "scale_note": "実在の社内額の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_04.png', 'haruki', '[haruki] 戦後1947年、GHQで139社にバラバラに解体された。
[nana] え、商社が消えたってこと?
[haruki] うん。でも1954年、三菱商事として再結集。
[nana] 一度ゼロになっても戻ってくる組織。今は三菱食品とローソンで日本の食卓を支えてる。', '解体されても、戻ってきた組織', '1947 解体 / 1954 再結集 / 今 三菱食品6,500社×3,000社', NULL, '["[haruki] 戦後1947年、GHQで139社にバラバラに解体された。", "[nana] え、商社が消えたってこと?", "[haruki] うん。でも1954年、三菱商事として再結集。", "[nana] 一度ゼロになっても戻ってくる組織。今は三菱食品とローソンで日本の食卓を支えてる。"]', 'H4: 三菱食品の物流倉庫 (戦後の商社復活の象徴として)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_05.png', 'nana', '[nana] 年収、結局いくらなの?
[haruki] 平均2,033万円。でも、ここは構造で見るところ。
[haruki] ベース+海外駐在手当+資源/LNG事業の業績連動賞与。場所と事業で大きく動く。
[nana] 額だけ見たら見誤る、ってことか。', '2,033万円(平均)+構造で変動', 'ベース / 海外駐在 / 資源・LNG連動賞与', '日経会社情報 8058 / 有報', '["[nana] 年収、結局いくらなの?", "[haruki] 平均2,033万円。でも、ここは構造で見るところ。", "[haruki] ベース+海外駐在手当+資源/LNG事業の業績連動賞与。場所と事業で大きく動く。", "[nana] 額だけ見たら見誤る、ってことか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_06.png', 'haruki', '[haruki] 1969年、アラスカからLNG輸入を始めた。日本企業初。
[nana] LNG?
[haruki] 液化天然ガス。今は世界14のプロジェクトに参画。日本の電力の3割が、これに支えられてる。
[nana] 私の家のガスも電気も、夜中にこのタンカーが運んでるんだ…', '1969年、日本のエネルギーを変えた', '世界14のLNGプロジェクト / 日本の電力の3割を支える', NULL, '["[haruki] 1969年、アラスカからLNG輸入を始めた。日本企業初。", "[nana] LNG?", "[haruki] 液化天然ガス。今は世界14のプロジェクトに参画。日本の電力の3割が、これに支えられてる。", "[nana] 私の家のガスも電気も、夜中にこのタンカーが運んでるんだ…"]', 'H3: LNGタンカー (夜の海上)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_07.png', 'nana', '[nana] 配属って、希望通りに行けるんですか?
[OB先輩] 正直、10事業グループのどこに行くかで仕事が全く違う。第一希望そのまま通る人は半分くらい。
[OB先輩] 入社3〜7年で海外駐在に出る人が多い。資源系はオーストラリア・中東、コンシューマーはアジア。
[haruki] 業界より、自分が何を10年やる覚悟があるかで決まる、ってことか…', '10事業グループのどこに?', '第一希望通る人は半分 / 3〜7年で海外駐在', NULL, '["[nana] 配属って、希望通りに行けるんですか?", "[OB先輩] 正直、10事業グループのどこに行くかで仕事が全く違う。第一希望そのまま通る人は半分くらい。", "[OB先輩] 入社3〜7年で海外駐在に出る人が多い。資源系はオーストラリア・中東、コンシューマーはアジア。", "[haruki] 業界より、自分が何を10年やる覚悟があるかで決まる、ってことか…"]', 'H6: 海外拠点 (NY・シンガポール・ロンドンのオフィスファサード)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_08.png', 'haruki', '[haruki] 2001年子会社化、2017年に連結子会社化。ローソンは三菱商事のもの。
[nana] え、この店舗ぜんぶ?
[haruki] 約14,600店舗。三菱食品が6,500社から仕入れて3,000社に卸す。コンビニ・スーパーの裏方は、ぜんぶ三菱の動脈。
[nana] 私のおにぎりも、三菱商事の中を通ってきたんだ…', 'おにぎり1個も、三菱の動脈の中', 'ローソン約14,600店舗 / 三菱食品6,500社×3,000社', NULL, '["[haruki] 2001年子会社化、2017年に連結子会社化。ローソンは三菱商事のもの。", "[nana] え、この店舗ぜんぶ?", "[haruki] 約14,600店舗。三菱食品が6,500社から仕入れて3,000社に卸す。コンビニ・スーパーの裏方は、ぜんぶ三菱の動脈。", "[nana] 私のおにぎりも、三菱商事の中を通ってきたんだ…"]', 'H2: ローソン店舗ファサード', '{"location": "店舗ファサード上部", "object_type": "店舗サイン (LAWSON 看板)", "brand_form": "ミルク缶モチーフの青と白の LAWSON 看板。実在のロゴデザインそのまま", "attachment": "店舗の外壁に固定された看板", "scale_note": "実在のコンビニ店舗の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_09.png', 'nana', '[OB先輩] 三菱が見るのは、『芯』『共創力』『高い志と誠実性』。学歴や倍率じゃない。
[OB先輩] 自分らしさをもって、ステークホルダーと共に価値を作れるか。
[nana] (静かに) 倍率じゃなくて、芯か…
[haruki] 三綱領の90年前から変わらない、人の見方ってことだ。', '見てるのは『芯・共創力・高い志』', '倍率じゃない、人物像で', NULL, '["[OB先輩] 三菱が見るのは、『芯』『共創力』『高い志と誠実性』。学歴や倍率じゃない。", "[OB先輩] 自分らしさをもって、ステークホルダーと共に価値を作れるか。", "[nana] (静かに) 倍率じゃなくて、芯か…", "[haruki] 三綱領の90年前から変わらない、人の見方ってことだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-corp', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@29041ca/public/images/mitsubishi-corp/panel_10.png', 'both', '[haruki] 売上19兆円、純利益8,000億円、採用139名。
[nana] 倍率の話じゃなくて、150年続いてきた仕事を、次に誰が動かすか、ってことだね。
[both] 所期奉公から、三価値同時実現へ。', '所期奉公から、三価値同時実現へ。', '売上 約19兆円 / 純利益 約8,000億円 / 採用139名', NULL, '["[haruki] 売上19兆円、純利益8,000億円、採用139名。", "[nana] 倍率の話じゃなくて、150年続いてきた仕事を、次に誰が動かすか、ってことだね。", "[both] 所期奉公から、三価値同時実現へ。"]', 'H1: 丸の内パークビル本社 (朝の光)', NULL);
