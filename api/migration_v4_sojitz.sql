-- ===== sojitz (双日株式会社) =====
-- source: output/sojitz/scenario_v4.json
-- jsDelivr ref: @673bf31
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('sojitz', '双日株式会社', 'sogo_shosha', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_01.png', 'nana', '[nana] 双日って、2003年生まれなんだって。
[haruki] 2003年? 私たちと…ほぼ同い年?
[nana] うん、私たちが22-23歳の時、双日も22-23歳。
[haruki] え、じゃあ、10年後の双日を作るのは…', '双日2003年生まれ、あなたとほぼ同い年', '双日 / 2768 / 一番新しい総合商社', NULL, '["[nana] 双日って、2003年生まれなんだって。", "[haruki] 2003年? 私たちと…ほぼ同い年?", "[nana] うん、私たちが22-23歳の時、双日も22-23歳。", "[haruki] え、じゃあ、10年後の双日を作るのは…"]', 'H1: 内幸町東急ビル本社', '{"location": "本社ビル上部の外壁", "object_type": "建築サイン (双日 / Sojitz)", "brand_form": "ビル外壁に控えめな『双日 / Sojitz』のサイン", "attachment": "ビル外壁固定", "scale_note": "実在の本社ビル通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_02.png', 'haruki', '[haruki] 純利益1,106億円、売上2.5兆円。23歳の会社で、これは大きい。
[nana] え、23歳でそんなに大きいの?
[haruki] 双日は2003年に日商岩井とニチメンが合併して生まれた。だから23歳でも、中身は両社の100年以上。
[nana] そっか、新しい会社だけど、根は古いんだ…', '純利益1,106億円(23歳)', '売上 約2.5兆円 / 2003年 ニチメン+日商岩井 合併', '公式IR', '["[haruki] 純利益1,106億円、売上2.5兆円。23歳の会社で、これは大きい。", "[nana] え、23歳でそんなに大きいの?", "[haruki] 双日は2003年に日商岩井とニチメンが合併して生まれた。だから23歳でも、中身は両社の100年以上。", "[nana] そっか、新しい会社だけど、根は古いんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_03.png', 'haruki', '[haruki] 双日のベトナム進出は商社No.1の規模。
[nana] え、5大商社よりも?
[haruki] うん、ベトナムだけは別格。製造業の進出を双日が現地で支援、不動産・物流・小売まで一気通貫。
[nana] 日本企業がベトナムに進出するとき、双日を通る、ってこと…', 'ベトナム進出、商社No.1', '製造業・不動産・物流・小売を一気通貫', NULL, '["[haruki] 双日のベトナム進出は商社No.1の規模。", "[nana] え、5大商社よりも?", "[haruki] うん、ベトナムだけは別格。製造業の進出を双日が現地で支援、不動産・物流・小売まで一気通貫。", "[nana] 日本企業がベトナムに進出するとき、双日を通る、ってこと…"]', 'H2: ベトナム・ハノイの街並み (双日オフィス)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_04.png', 'haruki', '[haruki] フィリピン産バナナの輸入シェア、双日は業界トップクラス。
[nana] スーパーで買うバナナの…!?
[haruki] それだけじゃない。車載リチウムイオン電池の電解液で世界シェアトップクラス。EVの中身も双日。
[nana] バナナとEV、全然違うのに、同じ会社で持ってるんだ…', 'バナナとEV、両方トップクラス', 'フィリピン産バナナシェア / 車載LiB電解液', NULL, '["[haruki] フィリピン産バナナの輸入シェア、双日は業界トップクラス。", "[nana] スーパーで買うバナナの…!?", "[haruki] それだけじゃない。車載リチウムイオン電池の電解液で世界シェアトップクラス。EVの中身も双日。", "[nana] バナナとEV、全然違うのに、同じ会社で持ってるんだ…"]', 'H3: フィリピンのバナナ農園', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_05.png', 'nana', '[nana] 双日の年収って、どんな構造になってるの?
[haruki] 有価証券報告書(2025年3月期・単体)によると平均1,274万円、平均年齢42.2歳。
[haruki] 内訳はベース給に、海外駐在手当とベトナム・東南アジアへの赴任手当が乗る仕組み。若手で早く海外に出るほど、その分が積み上がっていく。
[nana] 平均年齢42歳台のベースラインだから、20代で海外に飛び出せば、その構造をまるごと前倒しで使えるってことか。', '平均1,274万円(42.2歳・有報単体2025年3月期)+海外駐在で前倒し積み上げ', 'ベース給 / ベトナム・東南ア駐在手当が加算される構造', '日経会社情報 2768', '["[nana] 双日の年収って、どんな構造になってるの?", "[haruki] 有価証券報告書(2025年3月期・単体)によると平均1,274万円、平均年齢42.2歳。", "[haruki] 内訳はベース給に、海外駐在手当とベトナム・東南アジアへの赴任手当が乗る仕組み。若手で早く海外に出るほど、その分が積み上がっていく。", "[nana] 平均年齢42歳台のベースラインだから、20代で海外に飛び出せば、その構造をまるごと前倒しで使えるってことか。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_06.png', 'nana', '[nana] 働き方はどうですか?
[OB先輩] フレックスとリモートが両方使えるよ。新しい会社だから、制度の導入が早かったの。
[OB先輩] 福利厚生で大きいのは家賃補助と独身寮。内幸町近くの寮があるから、20代の家賃の心配がほぼなくなる。
[haruki] 内幸町・新橋・銀座エリアの家賃負担が浮く分が大きいってことか…', 'フレックス+リモート+独身寮あり', '家賃補助・独身寮で住居コスト ↓', NULL, '["[nana] 働き方はどうですか?", "[OB先輩] フレックスとリモートが両方使えるよ。新しい会社だから、制度の導入が早かったの。", "[OB先輩] 福利厚生で大きいのは家賃補助と独身寮。内幸町近くの寮があるから、20代の家賃の心配がほぼなくなる。", "[haruki] 内幸町・新橋・銀座エリアの家賃負担が浮く分が大きいってことか…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_07.png', 'nana', '[nana] 採用約130名は、5大商社並みですよね。
[OB先輩] うん、規模感は5大商社並み。第一希望そのまま通る人は半分くらい。
[OB先輩] でも双日は若手抜擢で有名。2〜3年でハノイ・ホーチミン駐在は当たり前。航空機事業ならシアトル・トゥールーズ。
[haruki] 5大商社の若手より、双日の若手は1〜2年早く海外に出る、ってことか…', '若手抜擢、2〜3年でハノイ駐在', '第一希望通る人は半分 / 5大商社より1〜2年早く海外', NULL, '["[nana] 採用約130名は、5大商社並みですよね。", "[OB先輩] うん、規模感は5大商社並み。第一希望そのまま通る人は半分くらい。", "[OB先輩] でも双日は若手抜擢で有名。2〜3年でハノイ・ホーチミン駐在は当たり前。航空機事業ならシアトル・トゥールーズ。", "[haruki] 5大商社の若手より、双日の若手は1〜2年早く海外に出る、ってことか…"]', 'H4: 航空機メンテナンス工場', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_08.png', 'nana', '[OB先輩] 双日が見るのは、双日精神。スピード・チャレンジ・誠実さ・チームワーク。
[OB先輩] 一番見てるのは、新しい挑戦を恐れずに、誠実に、チームで動ける人。
[nana] 一番新しい商社だから、新しい挑戦が当たり前、ってこと…
[haruki] スピードと誠実さの両立、ってのが双日らしいんだ。', 'スピード・チャレンジ・誠実・チームワーク', '新しい挑戦を、誠実に', NULL, '["[OB先輩] 双日が見るのは、双日精神。スピード・チャレンジ・誠実さ・チームワーク。", "[OB先輩] 一番見てるのは、新しい挑戦を恐れずに、誠実に、チームで動ける人。", "[nana] 一番新しい商社だから、新しい挑戦が当たり前、ってこと…", "[haruki] スピードと誠実さの両立、ってのが双日らしいんだ。"]', 'H6: 双日の社章', '{"location": "壁面中央", "object_type": "社章 (双日のロゴ)", "brand_form": "金属レリーフの『双日』ロゴ、実在のデザイン", "attachment": "壁面に固定", "scale_note": "実在の社内展示の通常サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。ハノイの工業団地で日本企業の進出を統括。
[haruki] フィリピン・ミンダナオでバナナのサプライチェーンを再設計。
[haruki] 中東〜アジアを結ぶLNG運搬で、エネルギー安全保障の起案。
[nana] 10年後、双日も私も、ひとまわり成長してる。一緒に育っていけるんだ…', '10年後、双日も私も、ひとまわり成長。', 'ハノイ / ミンダナオ / 中東〜アジアLNG', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。ハノイの工業団地で日本企業の進出を統括。", "[haruki] フィリピン・ミンダナオでバナナのサプライチェーンを再設計。", "[haruki] 中東〜アジアを結ぶLNG運搬で、エネルギー安全保障の起案。", "[nana] 10年後、双日も私も、ひとまわり成長してる。一緒に育っていけるんだ…"]', 'H2 ハノイ + H3 バナナ農園 + H5 LNGタンカー', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('sojitz', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@673bf31/public/images/sojitz/panel_10.png', 'both', '[haruki] 売上2.5兆円、純利益1,106億円、採用約130名。
[nana] 双日は23歳、私もまだ22-23歳。
[both] 一番新しい総合商社、23歳。伸びしろも、挑戦の数も、これから。', '伸びしろも、挑戦の数も、これから。', '売上 約2.5兆円 / 純利益 約1,106億円 / 採用 約130名', NULL, '["[haruki] 売上2.5兆円、純利益1,106億円、採用約130名。", "[nana] 双日は23歳、私もまだ22-23歳。", "[both] 一番新しい総合商社、23歳。伸びしろも、挑戦の数も、これから。"]', 'H1: 内幸町東急ビル (朝の光)', NULL);
