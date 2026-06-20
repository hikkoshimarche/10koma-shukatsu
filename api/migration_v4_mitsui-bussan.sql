-- ===== mitsui-bussan (三井物産株式会社) =====
-- source: output/mitsui-bussan/scenario_v4.json
-- jsDelivr ref: @99ac495
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('mitsui-bussan', '三井物産株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_01.png', 'nana', '[nana] ハルキ、おはよう。朝6時集合って、本当に商社の朝?
[haruki] うん、OB訪問の1日同行。先輩が『私の1日見てほしい』って。
[nana] 平均年収1,996万円って、どんな1日なんだろ…
[haruki] これから1日で分かる。三井物産の朝、ここから。', '商社で働く人の1日、朝6時から', '三井物産 / 8031 / 1日同行ルポ', NULL, '["[nana] ハルキ、おはよう。朝6時集合って、本当に商社の朝?", "[haruki] うん、OB訪問の1日同行。先輩が『私の1日見てほしい』って。", "[nana] 平均年収1,996万円って、どんな1日なんだろ…", "[haruki] これから1日で分かる。三井物産の朝、ここから。"]', 'H2: 大手町本社ビル (朝の遠景)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_02.png', 'nana', '[nana] ここが大手町本社。デカい…
[haruki] 『おはようございます』が、先輩にも後輩にも同じトーン。
[nana] 自由闊達って、これか…上下関係に縛られない。
[haruki] 140年『人の三井』って呼ばれてきた理由。三菱=組織、住友=結束、三井=人。', '『人の三井』(1876年〜140年)', '自由闊達 / 上下関係に縛られない', NULL, '["[nana] ここが大手町本社。デカい…", "[haruki] 『おはようございます』が、先輩にも後輩にも同じトーン。", "[nana] 自由闊達って、これか…上下関係に縛られない。", "[haruki] 140年『人の三井』って呼ばれてきた理由。三菱=組織、住友=結束、三井=人。"]', 'H2: 大手町本社ビル', '{"location": "本社ビル上部の外壁", "object_type": "建築サイン (三井物産)", "brand_form": "ビル外壁に『三井物産 / MITSUI & CO.』の控えめなサイン", "attachment": "ビル外壁固定", "scale_note": "実在の本社ビル通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_03.png', 'nana', '[nana] これが商社の事業…!?
[haruki] 7事業セグメントの『次世代・機能推進』。神奈川20MW、千葉ハイパースケール。
[nana] 5年で3,000億円超の投資って…AIの時代のインフラを商社が作ってるの?
[haruki] そう。2026年4月にデジタル・電力ソリューション本部新設。データセンター × 電力 × AI を掛け合わせる組織を、ゼロから作る。', 'AIの時代のインフラを商社が', '神奈川20MW / 千葉ハイパースケール / 5年3,000億超投資', NULL, '["[nana] これが商社の事業…!?", "[haruki] 7事業セグメントの『次世代・機能推進』。神奈川20MW、千葉ハイパースケール。", "[nana] 5年で3,000億円超の投資って…AIの時代のインフラを商社が作ってるの?", "[haruki] そう。2026年4月にデジタル・電力ソリューション本部新設。データセンター × 電力 × AI を掛け合わせる組織を、ゼロから作る。"]', 'H5: データセンター (神奈川・千葉のハイパースケール)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_04.png', 'nana', '[nana] あれ、データセンターだけじゃないの?
[haruki] 本業の動脈は今も資源・エネルギー。最大の利益は豪州ローズリッジ鉄鉱石。
[haruki] 投資額8,000億円・年2,500億円のCFを生む計画。LNGはモザンビーク・カタール・米国・豪州。
[nana] 売上14.7兆円のうち、これが屋台骨…新規事業と本業、両方やる商社なんだ。', 'ローズリッジ 投資8,000億円', '売上14.7兆円 / 当期利益9,003億円 / 7事業セグメント', '公式IR・有報', '["[nana] あれ、データセンターだけじゃないの?", "[haruki] 本業の動脈は今も資源・エネルギー。最大の利益は豪州ローズリッジ鉄鉱石。", "[haruki] 投資額8,000億円・年2,500億円のCFを生む計画。LNGはモザンビーク・カタール・米国・豪州。", "[nana] 売上14.7兆円のうち、これが屋台骨…新規事業と本業、両方やる商社なんだ。"]', 'H4: 豪州ローズリッジ鉄鉱石鉱山 + H3: LNGタンカー', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_05.png', 'nana', '[nana] 平均年収1,996万円って、どう積み上がってるの?
[haruki] 平均は42歳の人。若手は1年目450万、3年目750万、5年目で1,000万超え。10年目で約2,000万。
[haruki] さらに海外駐在手当が、先進国×1.5倍、新興国×2.0倍。
[nana] 平均額じゃなくて階段で見るんだ。20代後半で1,000万、海外駐在で倍に…', '1996万円(42歳平均)+階段で上がる', '1年目450万 → 5年目1,000万超 → 10年目2,000万', '人事データブック (出典あり)', '["[nana] 平均年収1,996万円って、どう積み上がってるの?", "[haruki] 平均は42歳の人。若手は1年目450万、3年目750万、5年目で1,000万超え。10年目で約2,000万。", "[haruki] さらに海外駐在手当が、先進国×1.5倍、新興国×2.0倍。", "[nana] 平均額じゃなくて階段で見るんだ。20代後半で1,000万、海外駐在で倍に…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_06.png', 'nana', '[nana] OB先輩、今日はありがとうございます。働き方ってどんな感じですか?
[OB先輩] フレックス・リモートが両方使えるよ。海外取引で夜のオンライン会議は普通にあるけどね。
[OB先輩] 福利厚生で大きいのは、社宅と海外駐在帯同手当。私もシンガポール駐在中は家族の生活もカバーされた。家計の心配なく仕事に集中できたよ。
[haruki] 駐在で家族も連れて行ける、生活と仕事を両立できる仕組みなんですね…', 'フレックス+リモート+海外駐在帯同あり', '社宅・海外駐在帯同手当 / 駐在中は家族の生活もカバー', NULL, '["[nana] OB先輩、今日はありがとうございます。働き方ってどんな感じですか?", "[OB先輩] フレックス・リモートが両方使えるよ。海外取引で夜のオンライン会議は普通にあるけどね。", "[OB先輩] 福利厚生で大きいのは、社宅と海外駐在帯同手当。私もシンガポール駐在中は家族の生活もカバーされた。家計の心配なく仕事に集中できたよ。", "[haruki] 駐在で家族も連れて行ける、生活と仕事を両立できる仕組みなんですね…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_07.png', 'nana', '[nana] 配属って、希望通りに行けるんですか?
[OB先輩] 第一希望そのまま通る人は半分くらい。でも三井物産独特なのは、インターン段階で分野別に分けるから、入社時点で配属がほぼ決まってるの。
[OB先輩] 入社3年で初の海外駐在は普通。私の同期はIHHヘルスケアでアジア最大の病院グループを担当して、今はクアラルンプール駐在。シンガポール、ロンドン、NY、サンパウロ、シドニーも当たり前。
[haruki] インターン選びで人生決まる、ってことか…', 'インターン経由必須、配属はそこで決まる', '3年目で海外駐在 / IHHヘルスケアでアジア最大の病院グループ担当', NULL, '["[nana] 配属って、希望通りに行けるんですか?", "[OB先輩] 第一希望そのまま通る人は半分くらい。でも三井物産独特なのは、インターン段階で分野別に分けるから、入社時点で配属がほぼ決まってるの。", "[OB先輩] 入社3年で初の海外駐在は普通。私の同期はIHHヘルスケアでアジア最大の病院グループを担当して、今はクアラルンプール駐在。シンガポール、ロンドン、NY、サンパウロ、シドニーも当たり前。", "[haruki] インターン選びで人生決まる、ってことか…"]', 'H6: IHHヘルスケア病院 (アジア最大の民間病院)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_08.png', 'haruki', '[haruki] 採用で見られるのって、何ですか?
[OB先輩] 3つ。『自ら考え行動する力』『困難を乗り越えた経験』『周囲を巻き込むリーダーシップ』。学歴・資格・TOEICじゃない。
[OB先輩] ESに『自分史』って、小学校から今までのライフヒストリーを書かせるの。堀社長の座右の銘は『実行と実考』。じっくり考えて、一歩一歩着実に進める。
[nana] (静かに) 私の歩み、ぜんぶ価値があるってこと…', '学歴より『自分史』 + 3つの軸', '自ら考え行動 / 困難を乗り越え / 周囲を巻き込む', NULL, '["[haruki] 採用で見られるのって、何ですか?", "[OB先輩] 3つ。『自ら考え行動する力』『困難を乗り越えた経験』『周囲を巻き込むリーダーシップ』。学歴・資格・TOEICじゃない。", "[OB先輩] ESに『自分史』って、小学校から今までのライフヒストリーを書かせるの。堀社長の座右の銘は『実行と実考』。じっくり考えて、一歩一歩着実に進める。", "[nana] (静かに) 私の歩み、ぜんぶ価値があるってこと…"]', 'H7: 堀健一社長の写真 + 『実行と実考』の書', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_09.png', 'haruki', '[nana] 10年後、私はどこにいるかな…
[haruki] 三井物産だと、たとえばこんな未来。ブラジルで100億円規模の鉄鉱石プロジェクトを動かしてる。
[haruki] 東京でAI×医療の新規事業を立ち上げてる。
[haruki] シンガポールでスタートアップ投資を仕掛けてる。
[nana] え、どれも『自分かも』って思えるのが、ちょっと怖い…', '10年後、どこで何を動かしてる?', 'ブラジル鉄鉱石 / 東京AI×医療 / シンガポール投資', NULL, '["[nana] 10年後、私はどこにいるかな…", "[haruki] 三井物産だと、たとえばこんな未来。ブラジルで100億円規模の鉄鉱石プロジェクトを動かしてる。", "[haruki] 東京でAI×医療の新規事業を立ち上げてる。", "[haruki] シンガポールでスタートアップ投資を仕掛けてる。", "[nana] え、どれも『自分かも』って思えるのが、ちょっと怖い…"]', 'H4 ローズリッジ + H5 データセンター + H6 IHHヘルスケア (3つの未来オーバーレイ)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsui-bussan', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@99ac495/public/images/mitsui-bussan/panel_10.png', 'both', '[nana] ありがとうございました…1日同行、めちゃくちゃ濃かった。
[haruki] 売上14.7兆円、当期利益9,003億円、採用129名。難易度全国4位。
[nana] でも見てるのは倍率じゃなくて、3つの軸と『自分史』。
[both] 人の三井 — あなたで、世界中の未来をつくる。', 'あなたで、世界中の未来をつくる。', '売上14.7兆円 / 当期利益9,003億円 / 採用129名 / 1876年〜', NULL, '["[nana] ありがとうございました…1日同行、めちゃくちゃ濃かった。", "[haruki] 売上14.7兆円、当期利益9,003億円、採用129名。難易度全国4位。", "[nana] でも見てるのは倍率じゃなくて、3つの軸と『自分史』。", "[both] 人の三井 — あなたで、世界中の未来をつくる。"]', 'H1: スリーダイヤ社章 + H2: 大手町本社 朝の光', '{"location": "本社入口のサイン", "object_type": "スリーダイヤ社章 (三井のロゴ)", "brand_form": "本社入口の控えめなスリーダイヤとMITSUI & CO.の表記", "attachment": "本社外壁", "scale_note": "実在のサインの通常サイズ"}');
