-- ===== ricoh (株式会社リコー) =====
-- source: output/ricoh/scenario_v4.json
-- jsDelivr ref: @e3c10f7026a087999fe3ac064f643e55eb101adf
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('ricoh', '株式会社リコー', 'electronics_precision', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_01.png', 'nana', '[nana] リコーって、コピー機の会社でしょ?
[haruki] それが、世界初のワンショット360度カメラを作ったのもリコー。RICOH THETA。
[nana] 360度! あの全天球の写真?
[haruki] VR/ARのインプットデバイスで市場を切り拓いた。複合機の会社が、見える世界そのものを変えてる。', '世界初のワンショット360度カメラ THETA', '全天球撮影 / VR・ARのインプットデバイス', 'リコー公式', '["[nana] リコーって、コピー機の会社でしょ?", "[haruki] それが、世界初のワンショット360度カメラを作ったのもリコー。RICOH THETA。", "[nana] 360度! あの全天球の写真?", "[haruki] VR/ARのインプットデバイスで市場を切り拓いた。複合機の会社が、見える世界そのものを変えてる。"]', 'H4: 複合機(オフィス向け)', '{"location": "複合機本体の前面パネル", "object_type": "RICOHロゴ", "brand_form": "複合機の操作パネル上部に『RICOH』の青いロゴ、実在の意匠", "attachment": "機器本体に印刷", "scale_note": "実在のオフィス複合機と同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_02.png', 'haruki', '[haruki] 売上2兆3,503億円。複合機、プリンター、FAXの複合機事業が主力。
[nana] 2兆円!? コピー機だけで?
[haruki] 『販売のリコー』って呼ばれるほど、販売網が広くて厚い。役所も大学も企業も、全部リコーの複合機。
[nana] 毎日使ってるのに、意識したことなかった…', '売上2兆3,503億円『販売のリコー』', '複合機・プリンター・FAX / 広く厚い販売網', '2024年3月期連結決算', '["[haruki] 売上2兆3,503億円。複合機、プリンター、FAXの複合機事業が主力。", "[nana] 2兆円!? コピー機だけで?", "[haruki] 『販売のリコー』って呼ばれるほど、販売網が広くて厚い。役所も大学も企業も、全部リコーの複合機。", "[nana] 毎日使ってるのに、意識したことなかった…"]', 'H4: 複合機(オフィス向け)', '{"location": "最も手前の複合機前面", "object_type": "RICOHロゴ", "brand_form": "複合機のパネル上部に青い『RICOH』ロゴ", "attachment": "機器本体に印刷", "scale_note": "実在のオフィス複合機サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_03.png', 'haruki', '[haruki] これ、RICOH THETA。世界初のワンシャッターで360度全天球撮影できるカメラ。
[nana] え、これリコーなの!? SNSでよく見るやつ…
[haruki] 2013年発売。VR不動産の内覧とか、観光地の記録とか、用途が広がってる。
[nana] 複合機だけじゃなくて、カメラも光学技術も持ってるんだ。', 'THETA、世界初360度カメラ', '2013年発売 / SNS・VR不動産で活躍', NULL, '["[haruki] これ、RICOH THETA。世界初のワンシャッターで360度全天球撮影できるカメラ。", "[nana] え、これリコーなの!? SNSでよく見るやつ…", "[haruki] 2013年発売。VR不動産の内覧とか、観光地の記録とか、用途が広がってる。", "[nana] 複合機だけじゃなくて、カメラも光学技術も持ってるんだ。"]', 'H3: RICOH THETA(360度カメラ)', '{"location": "テーブル中央、ナナの手の中", "object_type": "RICOH THETAロゴ", "brand_form": "超小型の円筒形360度カメラ本体に『RICOH THETA』の刻印、青と黒のツートン", "attachment": "カメラ本体に印刷", "scale_note": "実在のTHETAと同じ手のひらサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_04.png', 'haruki', '[haruki] 1936年、理研感光紙株式会社として創業。87年前。
[nana] 87年…昭和の初めから?
[haruki] この三愛ドリームセンターは1963年開業、銀座のランドマーク。2023年解体が始まって、2027年に新ビルが建つ。
[nana] 60年のビルを壊して、また新しく建てる。変革を続けてるんだ…', '1936年創業、87年の変革', '三愛ドリームセンター 1963〜2027 / 銀座のランドマーク', NULL, '["[haruki] 1936年、理研感光紙株式会社として創業。87年前。", "[nana] 87年…昭和の初めから?", "[haruki] この三愛ドリームセンターは1963年開業、銀座のランドマーク。2023年解体が始まって、2027年に新ビルが建つ。", "[nana] 60年のビルを壊して、また新しく建てる。変革を続けてるんだ…"]', 'H2: 三愛ドリームセンター(銀座4丁目交差点)', '{"location": "ビル上部の外壁", "object_type": "三愛ドリームセンター建築サイン", "brand_form": "円筒形総ガラスビルの上部に『SAN-AI DREAM CENTER』のサイン、控えめに", "attachment": "ビル外壁に固定", "scale_note": "実在の建築サインと同じ比率"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_05.png', 'nana', '[nana] 平均年収は?
[haruki] 860万円。平均年齢45.4歳。初任給は学士卒で28万5千円。
[nana] メーカーの中では?
[haruki] 平均的だけど、リコーの年収は『三愛精神』に支えられてる。人を愛し、国を愛し、勤めを愛す。長く勤めることで報いる構造。', '860万円＋三愛精神', '平均年齢45.4歳 / 初任給28万5千円(学士) / 長期勤続報酬', '2025年3月期', '["[nana] 平均年収は?", "[haruki] 860万円。平均年齢45.4歳。初任給は学士卒で28万5千円。", "[nana] メーカーの中では?", "[haruki] 平均的だけど、リコーの年収は『三愛精神』に支えられてる。人を愛し、国を愛し、勤めを愛す。長く勤めることで報いる構造。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_06.png', 'haruki', '[OB先輩] 採用は年間93名前後。営業職と技術職で半々くらい。
[OB先輩] 配属は営業なら全国の支社・営業所、技術なら開発拠点や工場。転勤は普通にある。
[OB先輩] 2018年に本社を創業の地・馬込に戻した。『原点回帰』を大事にする会社。
[haruki] 原点に戻りながら、変革を続ける。それがリコーの働き方なんだ。', '採用93名、全国転勤あり', '営業職・技術職 / 2018年本社を創業地・馬込に回帰', NULL, '["[OB先輩] 採用は年間93名前後。営業職と技術職で半々くらい。", "[OB先輩] 配属は営業なら全国の支社・営業所、技術なら開発拠点や工場。転勤は普通にある。", "[OB先輩] 2018年に本社を創業の地・馬込に戻した。『原点回帰』を大事にする会社。", "[haruki] 原点に戻りながら、変革を続ける。それがリコーの働き方なんだ。"]', 'H1: 本社事業所(大田区中馬込)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_07.png', 'nana', '[OB先輩] リコーが見るのは、三愛精神に共鳴できるか。人を愛し、国を愛し、勤めを愛す。
[OB先輩] 創業者・市村清が1946年に提唱した。77年前の言葉が、今も採用基準の中心。
[nana] (静かに) 人を愛し、国を愛し、勤めを愛す…
[haruki] 倍率じゃなくて、この精神に共鳴できるかが問われる。', '三愛精神『人を愛し国を愛し勤めを愛す』', '創業者・市村清 1946年提唱 / 77年続く採用基準', NULL, '["[OB先輩] リコーが見るのは、三愛精神に共鳴できるか。人を愛し、国を愛し、勤めを愛す。", "[OB先輩] 創業者・市村清が1946年に提唱した。77年前の言葉が、今も採用基準の中心。", "[nana] (静かに) 人を愛し、国を愛し、勤めを愛す…", "[haruki] 倍率じゃなくて、この精神に共鳴できるかが問われる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_08.png', 'nana', '[nana] ここ、RING CUBEっていうの? 写真がいっぱい…
[haruki] 2008年開設の写真文化発信拠点。三愛ドリームセンターの中にある。
[haruki] リコーは光学技術の会社だから、写真文化を支える活動もしてる。
[nana] 複合機とカメラと、写真文化。全部つながってるんだ。', 'RING CUBE、写真文化の発信拠点', '2008年開設 / 銀座・三愛ドリームセンター内', NULL, '["[nana] ここ、RING CUBEっていうの? 写真がいっぱい…", "[haruki] 2008年開設の写真文化発信拠点。三愛ドリームセンターの中にある。", "[haruki] リコーは光学技術の会社だから、写真文化を支える活動もしてる。", "[nana] 複合機とカメラと、写真文化。全部つながってるんだ。"]', 'H6: RING CUBE(銀座フォトギャラリー)', '{"location": "ギャラリー入口の壁面", "object_type": "RING CUBEロゴ", "brand_form": "壁面に『RING CUBE』のサイン、控えめなフォント", "attachment": "壁面に固定", "scale_note": "実在のギャラリーサインと同じサイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。全国の営業所で、企業の働き方改革を複合機で支える。
[haruki] 開発拠点で、次世代THETAの光学設計を担当。
[haruki] 銀座の新ビルで、RING CUBEの新しい写真文化企画を立ち上げる。
[nana] どれも、人を愛し、勤めを愛する仕事。', '10年後、たとえばこんな場面', '営業所 / 開発拠点 / 銀座新ビル', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。全国の営業所で、企業の働き方改革を複合機で支える。", "[haruki] 開発拠点で、次世代THETAの光学設計を担当。", "[haruki] 銀座の新ビルで、RING CUBEの新しい写真文化企画を立ち上げる。", "[nana] どれも、人を愛し、勤めを愛する仕事。"]', 'H5: リコピー101(歴史的製品)', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('ricoh', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/ricoh/panel_10.png', 'both', '[haruki] 売上2兆3,503億円、採用93名、平均年収860万円。
[nana] 1936年から87年、ずっと変革を続けてきた会社。
[both] 想像を、変革に。リコー、imagine. change.', '想像を、変革に。', '売上2兆3,503億円 / 採用93名 / 平均年収860万円', NULL, '["[haruki] 売上2兆3,503億円、採用93名、平均年収860万円。", "[nana] 1936年から87年、ずっと変革を続けてきた会社。", "[both] 想像を、変革に。リコー、imagine. change."]', 'H1: 本社事業所(大田区中馬込)', NULL);

-- ===== mitsubishi-shokuhin (三菱食品株式会社) =====
-- source: output/mitsubishi-shokuhin/scenario_v4.json
-- jsDelivr ref: @e3c10f7026a087999fe3ac064f643e55eb101adf
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('mitsubishi-shokuhin', '三菱食品株式会社', 'specialty_trading', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_01.png', 'nana', '[nana] ハリボー、好きなんだよね。このクマのグミ。
[haruki] それ、三菱食品が輸入してるの。全国の店頭の棚に並ぶお菓子や飲料を、陰で支える食品卸首位の会社。
[nana] 食品卸…?
[haruki] ハリボーもティムタムも、この会社が全国に届けてる。見えない食のインフラなんだ。', '店頭の棚を支える食品卸首位', '三菱食品 / 全国物流網 / 見えない食のインフラ', '三菱食品公式', '["[nana] ハリボー、好きなんだよね。このクマのグミ。", "[haruki] それ、三菱食品が輸入してるの。全国の店頭の棚に並ぶお菓子や飲料を、陰で支える食品卸首位の会社。", "[nana] 食品卸…?", "[haruki] ハリボーもティムタムも、この会社が全国に届けてる。見えない食のインフラなんだ。"]', 'H2: ハリボーグミ', '{"location": "ナナの手元中央", "object_type": "ハリボー ゴールドベア パッケージ", "brand_form": "クマ型グミのイラストと『HARIBO』ロゴ入り袋、実在の意匠", "attachment": "ナナの手で持たれている", "scale_note": "実在のハリボー商品袋と同サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_02.png', 'haruki', '[haruki] 三菱食品は売上2兆1,208億円。食品卸で業界首位。
[nana] 2兆円!? そんな大きい会社なのに、名前聞いたことなかった…
[haruki] 普通の人は知らない。でも、仕入先6,500社の商品を全国の小売に届けてる。
[nana] 6,500社… それ、スーパーやコンビニの棚ほぼ全部ってこと?', '売上2兆1,208億円、食品卸首位', '仕入先6,500社 / 業界トップ', '2025年3月期決算', '["[haruki] 三菱食品は売上2兆1,208億円。食品卸で業界首位。", "[nana] 2兆円!? そんな大きい会社なのに、名前聞いたことなかった…", "[haruki] 普通の人は知らない。でも、仕入先6,500社の商品を全国の小売に届けてる。", "[nana] 6,500社… それ、スーパーやコンビニの棚ほぼ全部ってこと?"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_03.png', 'nana', '[nana] ティムタムも三菱食品なんだ…
[haruki] そう。それだけじゃない。ローソン、イオン、イトーヨーカドーの配送も三菱食品が担ってる。
[nana] え、じゃあ私がさっきローソンで買ったこれも?
[haruki] その袋の中の商品、かなりの確率で三菱食品が運んだもの。', 'ティムタムもローソンも', 'イオン / イトーヨーカドー / 全国小売へ配送', NULL, '["[nana] ティムタムも三菱食品なんだ…", "[haruki] そう。それだけじゃない。ローソン、イオン、イトーヨーカドーの配送も三菱食品が担ってる。", "[nana] え、じゃあ私がさっきローソンで買ったこれも?", "[haruki] その袋の中の商品、かなりの確率で三菱食品が運んだもの。"]', 'H3: ティムタムビスケット', '{"location": "棚中央の商品パッケージ", "object_type": "ティムタム パッケージ", "brand_form": "『Tim Tam』ロゴ入りチョコビスケット箱、実在の意匠", "attachment": "棚に陳列", "scale_note": "実在のティムタム商品と同サイズ"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_04.png', 'haruki', '[haruki] 全国に物流拠点を持ってて、特に中国地方の酒類流通では圧倒的。
[nana] すごい… これ全部、毎日動いてるの?
[haruki] そう。食のライフライン。スーパーの棚が空にならないのは、この物流があるから。
[nana] 私、商社って海外ビジネスのイメージだったけど、国内のこれも商社なんだ…', '全国物流、食のライフライン', '中国地方酒類流通で突出 / 毎日の棚を支える', NULL, '["[haruki] 全国に物流拠点を持ってて、特に中国地方の酒類流通では圧倒的。", "[nana] すごい… これ全部、毎日動いてるの?", "[haruki] そう。食のライフライン。スーパーの棚が空にならないのは、この物流があるから。", "[nana] 私、商社って海外ビジネスのイメージだったけど、国内のこれも商社なんだ…"]', 'H4: 全国物流ネットワーク', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_05.png', 'nana', '[nana] 年収はどのくらいなの?
[haruki] 平均730万円。食品卸のトップ企業としては堅実な水準。
[nana] 2兆円の会社にしては、そこまで高くない…?
[haruki] 食品流通は薄利多売。でも平均勤続19.4年、離職率1.7%。安定した報酬で、長く働ける構造になってる。', '平均730万円+長期安定', '平均勤続19.4年 / 離職率1.7% / 食品流通インフラへの対価', '2025年3月期', '["[nana] 年収はどのくらいなの?", "[haruki] 平均730万円。食品卸のトップ企業としては堅実な水準。", "[nana] 2兆円の会社にしては、そこまで高くない…?", "[haruki] 食品流通は薄利多売。でも平均勤続19.4年、離職率1.7%。安定した報酬で、長く働ける構造になってる。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_06.png', 'nana', '[OB先輩] 総合職は全国転勤が前提。地方の物流拠点配属も普通にある。
[OB先輩] 入社3年目で九州の拠点、5年目で東北、みたいなキャリアも珍しくない。
[nana] 地方配属… 覚悟がいるな。
[OB先輩] でも食のライフラインを支える実感は、現場でしか得られない。月残業14.6時間で、生活は守られてる。', '全国転勤、地方拠点配属あり', '入社3〜5年で地方拠点 / 月残業14.6時間', NULL, '["[OB先輩] 総合職は全国転勤が前提。地方の物流拠点配属も普通にある。", "[OB先輩] 入社3年目で九州の拠点、5年目で東北、みたいなキャリアも珍しくない。", "[nana] 地方配属… 覚悟がいるな。", "[OB先輩] でも食のライフラインを支える実感は、現場でしか得られない。月残業14.6時間で、生活は守られてる。"]', 'H6: コンビニ・量販店への配送', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_07.png', 'nana', '[OB先輩] 三菱食品の根っこは三綱領。『所期奉公』社会への奉仕、『処事光明』公明正大、『立業貿易』貿易で立業。
[OB先輩] 求める人物像は『チャレンジする自律したプロ人財』。食の環境変化に柔軟に対応できる人。
[nana] 倍率は高い?
[OB先輩] 競争は厳しいけど、見てるのは倍率じゃなくて、食のライフラインを支える覚悟と柔軟性。', '所期奉公、チャレンジする自律', '三綱領 / 求める人物像 / 食の環境変化への柔軟性', NULL, '["[OB先輩] 三菱食品の根っこは三綱領。『所期奉公』社会への奉仕、『処事光明』公明正大、『立業貿易』貿易で立業。", "[OB先輩] 求める人物像は『チャレンジする自律したプロ人財』。食の環境変化に柔軟に対応できる人。", "[nana] 倍率は高い?", "[OB先輩] 競争は厳しいけど、見てるのは倍率じゃなくて、食のライフラインを支える覚悟と柔軟性。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_08.png', 'haruki', '[haruki] 三菱食品は2011年に菱食、明治屋商事、サンエス、フードサービスネットワークの4社が統合して生まれた。
[nana] 4社が一つに… それで2兆円規模になったんだ。
[haruki] 統合で全国ネットワークが完成した。単独じゃできなかった規模の物流が実現してる。
[nana] 歴史が浅いんじゃなくて、戦略的に作られた会社なんだ…', '2011年、4社統合で首位へ', '菱食 / 明治屋商事 / サンエス / FSN', NULL, '["[haruki] 三菱食品は2011年に菱食、明治屋商事、サンエス、フードサービスネットワークの4社が統合して生まれた。", "[nana] 4社が一つに… それで2兆円規模になったんだ。", "[haruki] 統合で全国ネットワークが完成した。単独じゃできなかった規模の物流が実現してる。", "[nana] 歴史が浅いんじゃなくて、戦略的に作られた会社なんだ…"]', 'H5: 2011年経営統合の歴史', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。九州の拠点で全国配送網の効率化プロジェクト。
[haruki] 本社で海外の新ブランド導入交渉、次のハリボーを探す。
[haruki] 全国の小売チェーン本部で、食のトレンド提案。
[nana] 地味じゃない。毎日の食卓を、裏側から支える仕事。', '10年後、たとえばこんな場面', '九州拠点 / 本社ブランド導入 / 全国小売提案', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。九州の拠点で全国配送網の効率化プロジェクト。", "[haruki] 本社で海外の新ブランド導入交渉、次のハリボーを探す。", "[haruki] 全国の小売チェーン本部で、食のトレンド提案。", "[nana] 地味じゃない。毎日の食卓を、裏側から支える仕事。"]', 'H1: 文京ガーデンゲートタワー本社', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('mitsubishi-shokuhin', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/mitsubishi-shokuhin/panel_10.png', 'both', '[haruki] 売上2兆1,208億円、仕入先6,500社、採用113名。
[nana] ハリボーもティムタムもローソンも、ぜんぶ三菱食品だった。
[both] 毎日の食卓、三菱食品がつないでる。食品卸首位、ここにある。', '毎日の食卓、三菱食品がつないでる', '売上2兆1,208億円 / 仕入先6,500社 / 採用113名', NULL, '["[haruki] 売上2兆1,208億円、仕入先6,500社、採用113名。", "[nana] ハリボーもティムタムもローソンも、ぜんぶ三菱食品だった。", "[both] 毎日の食卓、三菱食品がつないでる。食品卸首位、ここにある。"]', 'H1: 文京ガーデンゲートタワー本社(朝の光)', NULL);

-- ===== tis (TIS株式会社) =====
-- source: output/tis/scenario_v4.json
-- jsDelivr ref: @e3c10f7026a087999fe3ac064f643e55eb101adf
-- version: v4 (案B/ぼかし済)

INSERT OR IGNORE INTO companies (id, name, industry_id, thumbnail_url) VALUES ('tis', 'TIS株式会社', 'it_ai_saas', 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_01.png');

-- 10 panels (panel_num 1-10) — 既存5列 + v3.6 拡張列
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 1, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_01.png', 'haruki', '[haruki] ナナ、今日何回カード使った?
[nana] え? 自販機と昼ごはんと…3回かな。
[haruki] その3回、ぜんぶTISのシステムが支えてる。クレジットカードの基幹システムで国内トップクラス。
[nana] TIS? 聞いたことない…カードの裏側にいるの?', '今日何回カード使った?', 'TIS / カード決済の基幹システム / 国内トップクラス', 'TIS公式', '["[haruki] ナナ、今日何回カード使った?", "[nana] え? 自販機と昼ごはんと…3回かな。", "[haruki] その3回、ぜんぶTISのシステムが支えてる。クレジットカードの基幹システムで国内トップクラス。", "[nana] TIS? 聞いたことない…カードの裏側にいるの?"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 2, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_02.png', 'haruki', '[haruki] 国内のクレジットカード基幹システム、シェア約50%がTIS。
[nana] 半分!?
[haruki] デビットカードは約80%。JCBもTISのシステムで動いてる。
[nana] 私が使ってるカード、ほとんどTISが支えてるってこと…', 'クレジットカード基幹 約50%', 'デビットカード 約80% / JCB等 / 国内最大手', 'Wikipedia・公式サイト', '["[haruki] 国内のクレジットカード基幹システム、シェア約50%がTIS。", "[nana] 半分!?", "[haruki] デビットカードは約80%。JCBもTISのシステムで動いてる。", "[nana] 私が使ってるカード、ほとんどTISが支えてるってこと…"]', 'H6: クレジットカード基幹システム（業界シェア50%）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 3, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_03.png', 'haruki', '[haruki] これ、PAYCIERGE。TISの次世代決済プラットフォーム。
[nana] ペイシェルジュ?
[haruki] クレジット・デビット・プリペイド・スマホ決済を一つのシステムで動かす。
[nana] カード1枚の裏に、こんな技術が…', 'PAYCIERGE ペイシェルジュ', '次世代決済プラットフォーム / カード発行から決済まで一気通貫', NULL, '["[haruki] これ、PAYCIERGE。TISの次世代決済プラットフォーム。", "[nana] ペイシェルジュ?", "[haruki] クレジット・デビット・プリペイド・スマホ決済を一つのシステムで動かす。", "[nana] カード1枚の裏に、こんな技術が…"]', 'H3: PAYCIERGE 決済プラットフォーム', '{"location": "モニター中央", "object_type": "PAYCIERGEロゴ", "brand_form": "『PAYCIERGE』のロゴ、青系のグラデーション (実在の意匠に基づく)", "attachment": "モニター画面に表示", "scale_note": "モニター画面の1/4程度"}');
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 4, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_04.png', 'haruki', '[haruki] TISは1971年、三和銀行のシステム子会社として始まった。
[nana] 1971年!? 50年以上前…
[haruki] 金融システムを50年間、止めずに動かし続けてる。心斎橋gDCは2009年開業のミッションクリティカル拠点。
[nana] 50年間、止めない技術…それがカードの裏にあるんだ。', '1971年創業、50年以上止めない', '三和銀行の子会社 → 独立系SI最大手 / 心斎橋gDC', NULL, '["[haruki] TISは1971年、三和銀行のシステム子会社として始まった。", "[nana] 1971年!? 50年以上前…", "[haruki] 金融システムを50年間、止めずに動かし続けてる。心斎橋gDCは2009年開業のミッションクリティカル拠点。", "[nana] 50年間、止めない技術…それがカードの裏にあるんだ。"]', 'H4: 心斎橋gDC（次世代型データセンター）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 5, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_05.png', 'nana', '[nana] 年収はどうなの?
[haruki] 平均807万円。独立系SIerとしては高い方。
[haruki] TISの強みは、金融システムの継続性。50年間止めない技術に、企業が対価を払い続ける。
[nana] 一発の案件じゃなくて、長く守り続けることで報酬が積み上がるんだ…', '807万円(平均)+継続性の対価', '独立系SI / 金融システム50年の信頼', '有報 2025年3月期', '["[nana] 年収はどうなの?", "[haruki] 平均807万円。独立系SIerとしては高い方。", "[haruki] TISの強みは、金融システムの継続性。50年間止めない技術に、企業が対価を払い続ける。", "[nana] 一発の案件じゃなくて、長く守り続けることで報酬が積み上がるんだ…"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 6, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_06.png', 'nana', '[OB先輩] 配属は金融・製造・流通・公共の4本部に分かれる。希望通る人は6割くらい。
[OB先輩] 金融に配属されると、最初の3年は基幹システムの保守が多い。夜間バッチの監視も普通にある。
[nana] 夜間…
[OB先輩] でも、止めちゃいけないシステムを守る経験は、どこでも通用する。3年後、上流工程に上がれる。', '希望配属6割、最初3年は保守', '金融基幹システム / 夜間バッチ監視あり / 3年後上流へ', NULL, '["[OB先輩] 配属は金融・製造・流通・公共の4本部に分かれる。希望通る人は6割くらい。", "[OB先輩] 金融に配属されると、最初の3年は基幹システムの保守が多い。夜間バッチの監視も普通にある。", "[nana] 夜間…", "[OB先輩] でも、止めちゃいけないシステムを守る経験は、どこでも通用する。3年後、上流工程に上がれる。"]', 'H2: 豊洲ベイサイドクロスタワー', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 7, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_07.png', 'nana', '[OB先輩] TISが大切にしてるのは、オネスト、オープン、パイオニアリング。
[OB先輩] 採用は278名。規模は大きいけど、見てるのは『正直に課題に向き合えるか』『周囲を巻き込めるか』。
[nana] (静かに) 正直、オープン、開拓…
[haruki] 裏側を支える仕事だからこそ、正直さが一番大事なんだ。', 'オネスト・オープン・パイオニアリング', '採用 278名 / 正直に課題に向き合う人', NULL, '["[OB先輩] TISが大切にしてるのは、オネスト、オープン、パイオニアリング。", "[OB先輩] 採用は278名。規模は大きいけど、見てるのは『正直に課題に向き合えるか』『周囲を巻き込めるか』。", "[nana] (静かに) 正直、オープン、開拓…", "[haruki] 裏側を支える仕事だからこそ、正直さが一番大事なんだ。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 8, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_08.png', 'nana', '[nana] 自販機も、カフェも、駅の改札も…
[haruki] ぜんぶカード決済の裏でTISが動いてる。
[nana] 私の1日、TISのシステムに支えられてる…
[haruki] 見えないけど、確実にある。それがインフラの仕事。', '見えないけど、確実にある', '店舗 / カフェ / 駅 / 全部TIS', NULL, '["[nana] 自販機も、カフェも、駅の改札も…", "[haruki] ぜんぶカード決済の裏でTISが動いてる。", "[nana] 私の1日、TISのシステムに支えられてる…", "[haruki] 見えないけど、確実にある。それがインフラの仕事。"]', NULL, NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 9, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_09.png', 'haruki', '[nana] もし入れたら、10年後どこにいると思う?
[haruki] たとえば、こんな未来。心斎橋gDCで次世代決済システムのアーキテクト。
[haruki] 豊洲オフィスでPAYCIERGEの海外展開を企画。
[haruki] アジアの金融機関で、TISの基幹システムを導入提案。
[nana] 見えないけど、止めちゃいけない。それを守り続ける仕事。', '10年後、たとえばこんな場面', '心斎橋gDC / 豊洲 / アジア金融機関', NULL, '["[nana] もし入れたら、10年後どこにいると思う?", "[haruki] たとえば、こんな未来。心斎橋gDCで次世代決済システムのアーキテクト。", "[haruki] 豊洲オフィスでPAYCIERGEの海外展開を企画。", "[haruki] アジアの金融機関で、TISの基幹システムを導入提案。", "[nana] 見えないけど、止めちゃいけない。それを守り続ける仕事。"]', 'H4: 心斎橋gDC（次世代型データセンター）', NULL);
INSERT OR REPLACE INTO company_panels (company_id, panel_num, image_url, character, dialogue, main_copy, sub_copy, source_url, script_json, visual_hook, brand_object_json) VALUES ('tis', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@e3c10f7026a087999fe3ac064f643e55eb101adf/public/images/tis/panel_10.png', 'both', '[haruki] 売上5,716億円、営業利益690億円、採用278名。
[nana] カード決済の裏側、ぜんぶTISだった。
[both] 見えないインフラ、動かす誇り。TIS、50年の現在地。', '見えないインフラ、動かす誇り。', '売上 約5,716億円 / 営業利益 約690億円 / 採用 278名', NULL, '["[haruki] 売上5,716億円、営業利益690億円、採用278名。", "[nana] カード決済の裏側、ぜんぶTISだった。", "[both] 見えないインフラ、動かす誇り。TIS、50年の現在地。"]', 'H1: 住友不動産新宿グランドタワー（本社）', NULL);

