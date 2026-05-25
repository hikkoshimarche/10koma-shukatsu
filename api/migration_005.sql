-- =====================
-- migration_005: Phase A 11社追加
-- 業界: banking_insurance, retail, food_beverage, transport_logistics,
--       advertising_media, real_estate, consulting, it_ai_saas, specialty_trading
-- 会社: mufg, fast-retailing, suntory, ana, jr-east, dentsu,
--       mitsubishi-estate, mckinsey, google-japan, medipal, openai-japan
-- =====================

-- =====================
-- 業界マスター
-- =====================

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('banking_insurance', '銀行・証券・保険', '金融の中核。メガバンク・証券・保険が就活人気上位を占める。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('retail', '小売・流通', '国内外の消費者に商品を届ける。アパレル・コンビニ・EC等。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('food_beverage', '食品・飲料', '食卓を支える国内基幹産業。グローバル展開も加速中。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('transport_logistics', '航空・運輸・物流', '人とモノを動かすインフラ産業。コロナ後のV字回復期。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('advertising_media', '広告・メディア', 'マーケティング×デジタル×クリエイティブが融合する業界。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('real_estate', '不動産・建設', '都市開発から住宅まで。日本の街づくりを担う。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('consulting', 'コンサル', '企業の経営課題を解決するプロ集団。戦略・IT・会計等。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('it_ai_saas', 'IT・AI・SaaS', 'テクノロジーで世界を変える。外資Big Tech＋国内SaaSが激戦。', 10);

INSERT OR IGNORE INTO industries (id, name, description, panel_count)
VALUES ('specialty_trading', '商社（専門）', '特定分野に特化した専門商社。医薬品・化粧品・食品卸等。', 10);

-- =====================
-- 会社マスター
-- =====================

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'mufg',
  '三菱UFJ銀行',
  'banking_insurance',
  '国内最大の総合金融グループ。2024年度純利益1兆8,629億円で過去最高益。銀行・信託・証券・カード・リースを束ねる。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'fast-retailing',
  'ファーストリテイリング',
  'retail',
  '売上3兆円超の世界的アパレル企業。ユニクロ・GU・セオリー等5ブランド、世界3,595店舗を展開。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'suntory',
  'サントリー',
  'food_beverage',
  '創業1899年。売上3兆4,179億円、海外比率50%のグローバル飲料企業。「やってみなはれ」精神を今に伝える。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'ana',
  'ANAホールディングス',
  'transport_logistics',
  '売上2兆559億円で過去最高益。ANA・Peach・AirJapanの3ブランド体制で空の旅を支える。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'jr-east',
  'JR東日本',
  'transport_logistics',
  '売上約2兆7,000億円。1日1,608万人を運ぶ鉄道インフラ。「勇翔2034」でSuica生活圏・空飛ぶクルマまで構想。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'dentsu',
  '電通',
  'advertising_media',
  '日本最大の広告グループ。世界145以上の国・地域に展開。初任給35.5万円、平均年収1,508万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'mitsubishi-estate',
  '三菱地所',
  'real_estate',
  '大手町・丸の内・有楽町（大丸有）エリアの街の主。TOKYO TORCHで日本一の超高層ビル建設中。平均年収1,348万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'mckinsey',
  'マッキンゼー・アンド・カンパニー',
  'consulting',
  '世界最大手の戦略コンサルファーム。65ヶ国130拠点、社員4万人以上。国内上位30社の約8割に提供。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'google-japan',
  'Google日本',
  'it_ai_saas',
  'Alphabet傘下の日本法人。渋谷ストリームに本社、従業員約2,000名。Gemini AIをはじめ世界中の情報整理を担う。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'medipal',
  'メディパルホールディングス',
  'specialty_trading',
  '医薬品・化粧品・日用品卸で国内トップクラス。売上約3.5兆円。メディセオ×パルタックの二大事業で医療と暮らしを支える。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_01.png'
);

INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url)
VALUES (
  'openai-japan',
  'OpenAI Japan',
  'it_ai_saas',
  '2024年4月設立のアジア初拠点。六本木ヒルズ森タワーに本社。AGIが全人類に利益をもたらすことを確実にするミッション。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_01.png'
);

-- =====================
-- パネル（10コマ台本 + 画像URL）
-- =====================

-- 三菱UFJ銀行
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mufg', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_01.png', 'nana',   '銀行って、お金を預けて貸すだけの会社だよね？'),
  ('mufg', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_02.png', 'haruki', '実はMUFGは銀行・信託・証券・カード・リースを束ねる国内最大の総合金融グループ。2024年度は純利益1兆8,629億円で過去最高益を更新したよ。'),
  ('mufg', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_03.png', 'nana',   '1兆8,629億円って想像つかない…。普通の大企業の純利益って数百億円ってイメージなのに。'),
  ('mufg', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_04.png', 'haruki', '収益の柱は4つ。リテール・法人（国内預金/融資）、コーポレートバンキング（大企業/M&A）、グローバル（海外、特にアジア）、市場（資金運用）。最近は海外比率がぐっと上がってる。'),
  ('mufg', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_05.png', 'nana',   '海外まで広げて、何を目指してるの？'),
  ('mufg', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_06.png', 'haruki', 'MUFGのパーパスは「世界が進むチカラになる。」。お金を動かすことで企業や社会を前に進める、という発想。脱炭素ファイナンスや、東南アジア4ヶ国のデジタル金融にも本気で投資してるよ。'),
  ('mufg', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_07.png', 'nana',   'で、新卒で入ったらどんな感じなの？お給料とか働き方とか…'),
  ('mufg', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_08.png', 'haruki', '2026年度の初任給は学部卒30万円・修士31万円。平均年収は856万円。月平均残業は19.3時間でメガバンクの中では短め。30歳前後で年収1,000万円に届く人も多いよ。'),
  ('mufg', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_09.png', 'nana',   '採用は昔みたいに何百人もとってるの？'),
  ('mufg', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg/panel_10.png', 'both',   '2025年度は新卒640名・中途700名の計画。メガバンクで初めて中途が新卒を上回る。一括採用で育てる時代から、専門性で選ぶ時代へ。好奇心と挑戦を楽しめる人が求められてる。');

-- ファーストリテイリング
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('fast-retailing', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_01.png', 'nana',   'ユニクロって、安くて普通の服を売ってるイメージなんだけど…就活で受けるような会社なの？'),
  ('fast-retailing', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_02.png', 'haruki', 'ファーストリテイリング、実は売上3兆円超えの世界的アパレル企業。日本発で世界に挑む数少ないブランドだよ。'),
  ('fast-retailing', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_03.png', 'nana',   '3兆円…！？ユニクロだけでそんなに？'),
  ('fast-retailing', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_04.png', 'haruki', 'ユニクロだけじゃないんだ。ジーユー、プラステ、セオリー、コントワー・デ・コトニエもグループブランド。世界に3,595店舗、海外比率は5割超え。'),
  ('fast-retailing', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_05.png', 'nana',   'すごい規模だね…。でも、アパレルってどんどん新作出して捨てられる、みたいなイメージもあって。'),
  ('fast-retailing', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_06.png', 'haruki', 'ファストリの理念は「服を変え、常識を変え、世界を変えていく」。流行を追うんじゃなくて、LifeWear（究極の普段着）を作る。長く着られる、誰でも着られる、機能性のある服。ヒートテックやウルトラライトダウンがその答え。'),
  ('fast-retailing', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_07.png', 'nana',   '壮大だね！じゃあ、ここで働くとどうなの？'),
  ('fast-retailing', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_08.png', 'haruki', '2026年3月から、新卒初任給37万円（グローバルリーダー候補）。新人店長で月収41万円・年収730万円。平均年収は1,179万円。アパレル業界では桁違いの待遇だよ。'),
  ('fast-retailing', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_09.png', 'nana',   '年収1,179万円!?どんな人を求めてるの？'),
  ('fast-retailing', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/fast-retailing/panel_10.png', 'both',   '「少数精鋭でグローバル水準の仕事に挑む」——それがファストリの方針。挑戦心と高い目標を持ち、常識を変えにいく人が求められてる。世界一のアパレル企業を、本気で目指す会社だよ。');

-- サントリー
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('suntory', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_01.png', 'nana',   'サントリーって、ウイスキーとビールのイメージしかないんだけど…そんなに大きい会社なの？'),
  ('suntory', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_02.png', 'haruki', 'サントリーホールディングス、売上3兆4,179億円。実は海外売上比率が約50%のグローバル企業なんだよ。'),
  ('suntory', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_03.png', 'nana',   '海外でそんなに売れてるの！？ウイスキー以外に何を売ってるんだろう？'),
  ('suntory', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_04.png', 'haruki', '清涼飲料（伊右衛門、サントリー天然水、BOSS）、ビール（ザ・プレミアム・モルツ）、スピリッツ（ジムビーム、山崎）、健康食品、ワイン…幅広いよ。米州・欧州・アジア・オセアニアで事業展開してる。'),
  ('suntory', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_05.png', 'nana',   'そんなに広げて、何を大事にしてる会社なんだろう？'),
  ('suntory', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_06.png', 'haruki', 'サントリーには3つの言葉がある。「やってみなはれ」（創業者・鳥井信治郎の挑戦精神）、「利益三分主義」（事業活動で得た利益を社会に還元）、「Growing for Good」（成長して善きことを成す）。創業1899年の精神が今も生きてる。'),
  ('suntory', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_07.png', 'nana',   '「やってみなはれ」かっこいい！実際の働き方や待遇は？'),
  ('suntory', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_08.png', 'haruki', '初任給は学部卒27.8万円・修士卒29.48万円。平均年収は1,222万円（平均年齢44.8歳）。月平均残業は19.9時間で食品メーカーの中でも働きやすい方。'),
  ('suntory', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_09.png', 'nana',   '年収1,200万円超え！採用はどんな感じなの？'),
  ('suntory', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/suntory/panel_10.png', 'both',   '2024年度は約200名採用、男女ほぼ半々。「やってみなはれ」を体現する挑戦心ある人、多様な価値観を融合できる人が求められてる。100年以上続く挑戦のDNAを、次の世代に繋ぐ仕事。');

-- ANAホールディングス
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('ana', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_01.png', 'nana',   'ANAって飛行機の会社だよね？コロナで大変だったイメージなんだけど、今はどうなの？'),
  ('ana', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_02.png', 'haruki', '完全に復活したよ。2024年3月期、売上2兆559億円・営業利益2,079億円で過去最高益を達成。インバウンド客の急回復と国際線好調が追い風だね。'),
  ('ana', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_03.png', 'nana',   '過去最高益！？コロナ前より儲かってるってこと？'),
  ('ana', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_04.png', 'haruki', 'そう。しかも今は3つの航空ブランドを使い分けてる。ANA（フルサービス）、Peach（LCC）、2024年2月に始まったAirJapan（中距離LCC）。価格帯と路線を最適に組み合わせてるんだ。'),
  ('ana', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_05.png', 'nana',   '賢いね。でも飛行機って事故が怖いし、安全性ってどう考えてるんだろう？'),
  ('ana', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_06.png', 'haruki', 'ANAの経営理念は「安心と信頼を基礎に、世界をつなぐ心の翼で夢にあふれる未来に貢献します。」。安全運航が全ての土台。ANA''s Way「あんしん、あったか、あかるく元気！」で社員の行動指針も明確にしてる。'),
  ('ana', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_07.png', 'nana',   '心の翼かぁ。働き方はどうなの？航空業界って忙しそう。'),
  ('ana', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_08.png', 'haruki', '意外と働きやすいよ。ホールディングス平均年収730万円、初任給は3年連続で引き上げ中で25万円。月平均残業はなんと8.2時間で、業界トップクラスの短さだよ。'),
  ('ana', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_09.png', 'nana',   '残業8時間！？それは驚き。どんな人を求めてるの？'),
  ('ana', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/ana/panel_10.png', 'both',   '安全と信頼を最優先しつつ、多様性を活かし挑戦できる人。グローバルスタッフ、客室乗務、運航乗務、技術…様々な職種で「世界をつなぐ心の翼」になる仲間を募集中。');

-- JR東日本
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('jr-east', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_01.png', 'nana',   'JR東日本って、鉄道会社だよね？電車を走らせてるだけのイメージなんだけど…就活先として何が魅力なの？'),
  ('jr-east', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_02.png', 'haruki', '鉄道だけじゃないんだよ。売上は約2兆7,000億円、1日の輸送人員は約1,608万人。鉄道に加えて駅ナカ、不動産、ホテル、Suica…多角化されてるんだ。'),
  ('jr-east', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_03.png', 'nana',   '1,608万人!?東京の人口より多いじゃん。'),
  ('jr-east', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_04.png', 'haruki', 'しかも今、新しい経営ビジョン「勇翔 2034」を出してる。2034年度に売上5兆円が目標。鉄道を超えて、Suicaを「生活のデバイス」にした「Suica生活圏」、JRE BANK、空飛ぶクルマまで構想してるよ。'),
  ('jr-east', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_05.png', 'nana',   '鉄道会社が空飛ぶクルマ！？どんな会社を目指してるんだろう？'),
  ('jr-east', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_06.png', 'haruki', '「モビリティ×ソリューション」の二軸経営。鉄道で培った安全とインフラ運営力を活かして、人々の暮らし全体を支える会社へ。経営の最優先は今も「安全」。究極の安全を実現するための投資を続けてるよ。'),
  ('jr-east', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_07.png', 'nana',   'スケールが大きいね…！働き方はどうなの？'),
  ('jr-east', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_08.png', 'haruki', '初任給は2025年4月から約25万円、平均年収は767万円。月平均残業は約15時間で、有給取得日数は年18日。鉄道インフラ会社らしく安定してる。'),
  ('jr-east', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_09.png', 'nana',   '安定しつつ未来も描いてるんだ。採用は？'),
  ('jr-east', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/jr-east/panel_10.png', 'both',   '2025年度は新卒+中途で約500名。総合職、地域総合職、ジョブ型の3枠から選べる。鉄道インフラから生活インフラへ進化させる挑戦に、新しい仲間が必要。「自ら成長して自己実現したい人」が求められてる。');

-- 電通
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('dentsu', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_01.png', 'nana',   '電通って広告会社だよね。テレビCMとかを作ってるイメージなんだけど…就活で人気なの？'),
  ('dentsu', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_02.png', 'haruki', '日本最大の広告グループだよ。グループで世界145以上の国・地域、従業員7.1万人。売上1兆4,109億円。ただ、2024年12月期は海外事業ののれん減損で過去最大の赤字も出してる。'),
  ('dentsu', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_03.png', 'nana',   '赤字なの！？それでも就活先として人気なんだ？'),
  ('dentsu', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_04.png', 'haruki', '国内事業は実は好調で売上8%増。特にインターネット広告が成長エンジン。海外で減損は出たけど、2025年は500億円の構造改革で立て直し、2027年にROE10%台半ばを目指してるよ。'),
  ('dentsu', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_05.png', 'nana',   '課題があっても挑戦してるんだね。電通が大事にしてる価値観って何？'),
  ('dentsu', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_06.png', 'haruki', 'パーパスは「an invitation to the never before.」——誰も見たことのない未来へ。創業1901年、120年以上の歴史を持ちながら、常に新しいクリエイティビティで世の中を動かしてきた会社だよ。'),
  ('dentsu', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_07.png', 'nana',   '120年以上！すごい歴史だね。働き方はどうなの？広告業界って忙しいイメージ。'),
  ('dentsu', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_08.png', 'haruki', '働き方改革が進んで、月平均残業は19.5時間まで削減。22時以降の残業は禁止。初任給は35.5万円、平均年収は1,508万円で業界トップクラス。'),
  ('dentsu', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_09.png', 'nana',   '月19.5時間まで減ってるんだ。採用は？'),
  ('dentsu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/dentsu/panel_10.png', 'both',   '電通本体の新卒採用は約100名の狭き門。クリエイティビティで新しい価値を生み出せる人、デジタルとデータを駆使できる人が求められてる。「誰も見たことのない未来」を一緒に作る挑戦が待ってる。');

-- 三菱地所
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mitsubishi-estate', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_01.png', 'nana',   '三菱地所って、不動産屋さん…マンション売ってる会社のイメージ？'),
  ('mitsubishi-estate', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_02.png', 'haruki', 'スケールが違うんだ。三菱地所が運営してるのは「大手町・丸の内・有楽町」エリア全体。東京駅前のオフィス街、あれ実は三菱地所の街なんだよ。'),
  ('mitsubishi-estate', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_03.png', 'nana',   '街そのもの！？東京駅前があの会社のもの？'),
  ('mitsubishi-estate', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_04.png', 'haruki', '営業収益1兆6,000億円、営業利益約3,800億円。今は「TOKYO TORCH」プロジェクトで、東京駅前に日本一の超高層ビルを建設中。ロジスティクスやデータセンターも拡大してる。'),
  ('mitsubishi-estate', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_05.png', 'nana',   '街を作る…ってどんな思いでやってる会社なんだろう？'),
  ('mitsubishi-estate', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_06.png', 'haruki', '経営理念は「私たちは、街づくりを通じて社会に貢献していきます」。建物を建てるだけじゃなくて、人が集まり、文化が生まれ、経済が回る「街」を作る。100年単位の長期視点が必要な仕事だよ。'),
  ('mitsubishi-estate', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_07.png', 'nana',   '100年単位…重みあるね。働き方や待遇は？'),
  ('mitsubishi-estate', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_08.png', 'haruki', '業界トップクラスの待遇だよ。初任給は2025年から学部30.5万円・修士34万円に大幅引き上げ。平均年収1,348万円、有給取得率69%。勤続5年ごとにリフレッシュ休暇もある。'),
  ('mitsubishi-estate', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_09.png', 'nana',   '年収1,348万円…！採用は狭き門なんだろうな。'),
  ('mitsubishi-estate', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi-estate/panel_10.png', 'both',   '新卒採用は40〜60名/年の超狭き門。街づくりへの強い思いを持ち、長期視点で社会価値を創造できる人が求められてる。100年先まで残る「街」を作る、特別なやりがいがある仕事。');

-- マッキンゼー・アンド・カンパニー
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mckinsey', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_01.png', 'nana',   'マッキンゼーって名前は聞いたことあるけど、何してる会社か実はよく分かってないんだ…'),
  ('mckinsey', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_02.png', 'haruki', '世界最大手の戦略コンサルティングファームだよ。世界65ヶ国・130拠点、社員4万人以上。日本オフィスは1971年に大前研一氏が立ち上げた。'),
  ('mckinsey', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_03.png', 'nana',   '戦略コンサル…具体的に何をしてるの？'),
  ('mckinsey', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_04.png', 'haruki', '大企業の経営課題を解決する仕事。国内上位30社の約8割にサービス提供してる。海外進出、M&A、DX、組織改革…日本企業のグローバル化を支える「黒子」みたいな存在だよ。'),
  ('mckinsey', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_05.png', 'nana',   '大企業の社長たちが頼る相手なんだね。マッキンゼーの強みって？'),
  ('mckinsey', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_06.png', 'haruki', '「One Firm Policy」——世界中のオフィスが一つの組織として並列に連携する。日本にいながらシンガポール、ロンドン、ニューヨークのチームと当たり前に協働する。クライアントには「Obligation to Dissent」（異論を述べる義務）も大切にしてる。'),
  ('mckinsey', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_07.png', 'nana',   '異論を述べる義務！？面白い文化だね。働き方は？'),
  ('mckinsey', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_08.png', 'haruki', '新卒初任給は年収600〜700万円スタート、MBA経験者は1,400万円超え。ただし「Up or Out」（成果次第で昇進 or 退職）が厳格。激務だけど、20代でCxOクラスと議論できる稀有な環境。'),
  ('mckinsey', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_09.png', 'nana',   '年収高いけど厳しい世界だね…どんな人を求めてるの？'),
  ('mckinsey', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mckinsey/panel_10.png', 'both',   '「個性的で意欲的で好奇心旺盛な人材」。高い自律性、問題解決能力、リーダーシップが必須。20代で世界トップ企業の経営者と対峙する経験が積める、唯一無二のキャリア。');

-- Google日本
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('google-japan', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_01.png', 'nana',   'Google日本って、検索エンジンの会社でしょ？でも入社できる人なんているの？'),
  ('google-japan', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_02.png', 'haruki', '入れる人はいる。グーグル合同会社、日本法人で従業員約2,000名。Alphabet全体では18万人。渋谷ストリームに本社があるよ。'),
  ('google-japan', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_03.png', 'nana',   '渋谷にあるんだ。実際にどんな仕事してるの？'),
  ('google-japan', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_04.png', 'haruki', '検索・広告・YouTube・Android・Cloud・Workspace、それに今は生成AI「Gemini」の開発と展開。「世界中の情報を整理し、世界中の人々がアクセスできて使えるようにする」というミッションを、技術と事業で実装してる。'),
  ('google-japan', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_05.png', 'nana',   'ミッションが壮大すぎる…。Googleが大事にしてる価値観って？'),
  ('google-japan', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_06.png', 'haruki', '「Googliness（グーグリネス）」が有名。好奇心、謙虚さ、協調性、複雑性の中で動ける能力。技術力だけじゃなく、人柄も重視される文化。フラットな社風で、新卒でもアイデアを発信できるよ。'),
  ('google-japan', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_07.png', 'nana',   '雰囲気よさそう。給料はどうなの？'),
  ('google-japan', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_08.png', 'haruki', '日本法人の平均年収は約1,120万円（口コミベース）、開発職だと2,151万円という調査も。新卒初任給はジョブレベル次第だけど、ソフトウェアエンジニアなら年収1,000万円超のオファーも珍しくない。ストックオプションでAlphabet株も付与される。'),
  ('google-japan', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_09.png', 'nana',   '1,000万円スタート!?どんな人が採用されるの？'),
  ('google-japan', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/google-japan/panel_10.png', 'both',   '新卒採用は限定的で超狭き門。求められるのは「Googliness」を持ち、技術や事業でユーザーに価値を届けられる人。世界中の人の生活に影響を与えるプロダクトに、若いうちから関われる稀有な環境。');

-- メディパルホールディングス
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('medipal', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_01.png', 'nana',   'メディパルホールディングス…？聞いたことないかも。何をしてる会社なの？'),
  ('medipal', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_02.png', 'haruki', '医薬品と化粧品・日用品の卸売で国内トップクラスの会社。売上は約3.5兆円。病院や薬局に医薬品を届ける「メディセオ」、ドラッグストアに化粧品・日用品を届ける「パルタック」が二大事業だよ。'),
  ('medipal', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_03.png', 'nana',   '3.5兆円!?でも卸って…何が面白いの？'),
  ('medipal', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_04.png', 'haruki', '「流通価値の創造を通じて人々の健康と社会の発展に貢献する」のが経営理念。例えば医薬品。製薬会社が作った薬を、毎日全国の病院・薬局に正確に届けることで医療が成り立ってる。社会インフラの「血管」みたいな存在なんだ。'),
  ('medipal', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_05.png', 'nana',   '社会インフラかぁ…。どんな未来を目指してるの？'),
  ('medipal', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_06.png', 'haruki', '「ありたい姿」は「『医療と健康、美』を広げ、支え、つなぐ 健康応援オーケストラ」。2027年に経常利益1,000億円、ROE9%が目標。最近はアニマル領域（ペット）にも進出して、EC大手シグニ社を子会社化したよ。'),
  ('medipal', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_07.png', 'nana',   '健康応援オーケストラっていい表現。働き方はどうなの？'),
  ('medipal', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_08.png', 'haruki', '平均年収814万円。役職が上がると係長963万円、課長1,260万円、部長1,519万円。安定感のある待遇だよ。初任給は約33万円。'),
  ('medipal', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_09.png', 'nana',   '安定してそう。どんな人を求めてるの？'),
  ('medipal', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/medipal/panel_10.png', 'both',   '大事にしてる価値観は「誠実」「倫理観」「使命感」。創造性に富み、健康と社会への貢献を志す人が求められてる。地味だけど、毎日の医療と暮らしを支える「社会インフラ」の仕事。');

-- OpenAI Japan
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('openai-japan', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_01.png', 'nana',   'OpenAI Japanって、ChatGPTを作ってる会社の日本支社だよね？日本でも採用してるの？'),
  ('openai-japan', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_02.png', 'haruki', '2024年4月に「OpenAI Japan合同会社」が設立されたばかりなんだ。サンフランシスコ、ロンドン、ダブリンに次ぐ世界4拠点目で、アジア初。本社は六本木ヒルズ森タワー。'),
  ('openai-japan', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_03.png', 'nana',   'アジア初！日本がそんなに重要なの？'),
  ('openai-japan', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_04.png', 'haruki', '日本のChatGPTユーザーはすでに200万人以上。OpenAI本社のサム・アルトマンCEOも「日本の政府、企業、研究機関と長期的なパートナーになる」と意気込んでる。日本語特化のGPT-4カスタムモデルも作って、最上位モデル比3倍速で動くんだ。'),
  ('openai-japan', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_05.png', 'nana',   '日本にすごく本気なんだね。社長はどんな人？'),
  ('openai-japan', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_06.png', 'haruki', '元AWSジャパン社長の長崎忠雄氏。AWSで13年間、保守的だった日本企業にクラウドを根付かせた実績がある。OpenAIのミッションは「AGI（汎用人工知能）が全人類に利益をもたらすことを確実にする」。長崎氏の「テクノロジーの民主化」という信念と相性がいい。'),
  ('openai-japan', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_07.png', 'nana',   '壮大なミッション！実際の働く環境は？'),
  ('openai-japan', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_08.png', 'haruki', 'まだ10数名〜数十名のスタートアップフェーズだから、給与・待遇は公開されてない。ただ、米OpenAI本社の水準を考えるとシニア層は数千万円〜億円規模。日本法人もそれに準じた高水準と推測されてるよ。'),
  ('openai-japan', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_09.png', 'nana',   '給与は不明だけど、まさに歴史を作る瞬間にいる感じだね…'),
  ('openai-japan', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/openai-japan/panel_10.png', 'both',   '採用は営業・技術開発・ユーザー支援・政府渉外の各領域。中途中心だけど、AI時代の最前線で「日本でかつてない事例」を作る挑戦。AI技術と社会実装の両面で動ける、好奇心と粘り強さを持つ人が求められてる。');

-- 検証ステータス設定
UPDATE companies SET last_verified_at='2026-05-25', verification_status='verified'
WHERE id IN ('mufg','fast-retailing','suntory','ana','jr-east','dentsu','mitsubishi-estate','mckinsey','google-japan','medipal','openai-japan');

UPDATE industries SET last_verified_at='2026-05-25', verification_status='verified'
WHERE id IN ('banking_insurance','retail','food_beverage','transport_logistics','advertising_media','real_estate','consulting','it_ai_saas','specialty_trading');
