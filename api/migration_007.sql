-- Phase B-2: 銀行・証券・保険業界 第1陣 8社×10コマ = 80パネル
-- industry: banking_insurance は既存

-- 三井住友銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'smbc-bank',
  '三井住友銀行',
  'banking_insurance',
  '純利益1兆1,779億円（邦銀2社目の1兆円超え）。Olive・三井住友カード・SMBC日興証券を擁するSMFGの中核銀行。初任給30万円、平均年収892万円、残業15.6h/月。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('smbc-bank', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_01.png', 'nana',   '三井住友銀行って、要は普通の銀行でしょ？'),
  ('smbc-bank', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_02.png', 'haruki', '実はね、2025年3月期で純利益1兆1,779億円。邦銀グループで2社目、初めて1兆円を超えた銀行なんだ。'),
  ('smbc-bank', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_03.png', 'nana',   'えっ、コンビニATMで使ってるあのSMBCが…1兆円！？'),
  ('smbc-bank', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_04.png', 'haruki', 'そうそう。普段使ってる三井住友カード、Olive、SMBC日興証券、SMBCコンシューマーファイナンス。全部このグループ。気づかないだけで、毎日触ってる金融インフラなんだよ。'),
  ('smbc-bank', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_05.png', 'nana',   'うわ…そんなとこに入ったら、お給料どうなるの？'),
  ('smbc-bank', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_06.png', 'haruki', '2026年度から初任給30万円に大幅アップ。平均年収は892万円。月の残業は15.6時間で、メガバンクの中でも最短水準。'),
  ('smbc-bank', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_07.png', 'nana',   'でも倍率…プレエントリー2万4千人で採用500人って、48倍じゃん。私なんかじゃ無理かも。'),
  ('smbc-bank', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_08.png', 'haruki', '実は採用コースが「法人営業」「海外」「デジタル」「ウェルスマネジメント」と細かく分かれてるんだ。求めるのは「プロフェッショナル・チームワーク・挑戦」の3つ。学歴より、自分の言葉で「なぜSMBCか」を語れるかが評価される。20代から海外駐在も全然ある。'),
  ('smbc-bank', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_09.png', 'nana',   '20代で…海外駐在！？'),
  ('smbc-bank', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smbc-bank/panel_10.png', 'haruki', '「すべては現場から」——それがSMBCの方針。プロフェッショナルとして、チームの中で、失敗を恐れず挑戦する人が求められてる。「世界をつなぐ、日本発のトラステッド・パートナー」を、本気で目指す銀行だよ。');

-- みずほフィナンシャルグループ
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'mizuho-fg',
  'みずほフィナンシャルグループ',
  'banking_insurance',
  '純利益8,854億円（過去最高）。邦銀唯一、銀行・信託・証券をワンチームで動かす。グループ5社合同採用・3つの型×16コース。初任給学部26万円、平均年収823万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mizuho-fg', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_01.png', 'nana',   'みずほって、銀行と証券と信託がばらばらあるグループ？'),
  ('mizuho-fg', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_02.png', 'haruki', 'それが違うんだよ。みずほは邦銀で唯一、銀行・信託・証券をワンチームで動かしてる会社。2025年3月期は純利益8,854億円、過去最高益だよ。'),
  ('mizuho-fg', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_03.png', 'nana',   'えっ、そんなグループとして動いてるの？'),
  ('mizuho-fg', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_04.png', 'haruki', '送金アプリ、クレジットカード、退職年金、メルカリやアスクルとも取引してる。銀行・信託・証券・R&Tを一体で動かす、邦銀唯一のワンチーム体制なんだよ。'),
  ('mizuho-fg', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_05.png', 'nana',   'うっ…そんなとこに、もし入ったら？'),
  ('mizuho-fg', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_06.png', 'haruki', '初任給は学部26万円・修士28万円・博士30万円。銀行単体の平均年収は823万円、持株会社だと1,117万円。40歳で年収1,000万円超えは現実的だよ。'),
  ('mizuho-fg', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_07.png', 'nana',   'でも倍率…グループ一括で300人採用って、倍率70倍じゃん。私の話、聞いてもらえるのかな…'),
  ('mizuho-fg', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_08.png', 'haruki', '実はみずほ、コースが「3つの型×16コース」と選択肢がめちゃくちゃ多いんだ。「オープン型」だと幅広く評価されるし、「オーダーメイド型」だと自分でキャリアを設計できる。しかもグループ間の人事異動が活発で、「銀行と証券を両方経験する」そんなキャリアも普通にあるよ。'),
  ('mizuho-fg', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_09.png', 'nana',   '銀行と証券両方…？'),
  ('mizuho-fg', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mizuho-fg/panel_10.png', 'haruki', '「警鐘となる」「見送らず踏み込む」「より遡って跟ずく」——みずほが求めているのは、この3つができる人。3メガで唯一、銀行・信託・証券をワンチームで動かす会社だから、「ともに挑む。ともに実る。」というパーパスが本気で実現できる。');

-- りそな銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'resona',
  'りそな銀行',
  'banking_insurance',
  '純利益2,133億円（7期ぶり2,000億超え）。2003年「よみがえり」からV字回復。オムニチャネル型金融で「リテールNo.1」を目指す。12コース採用、初任給28万円、平均年収727万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('resona', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_01.png', 'nana',   'りそな銀行って、関西の銀行？それとも首都圏？'),
  ('resona', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_02.png', 'haruki', '両方だよ。2003年、「よみがえり」という全国を揺るがした金融危機を生き延び、今やメガバンクを除いて国内最大級のリテール金融グループ。2025年3月期は純利益2,133億円、7期ぶり2,000億超えだよ。'),
  ('resona', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_03.png', 'nana',   '7期ぶりって…もしかしてりそなって復活した会社？'),
  ('resona', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_04.png', 'haruki', 'そうなんだ。公的資金を受けた銀行が、いまやスマホアプリだけで住宅ローン・信託・保険・取引を全部できる「オムニチャネル型金融」を業界で一番進めてる。うちの親世代も、住宅ローンも、りそな使ってる人結構多いよ。'),
  ('resona', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_05.png', 'nana',   '住宅ローンもりそな？そんなとこに入ったら、お給料どうなるの？'),
  ('resona', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_06.png', 'haruki', '初任給は28万円（2027年募集・ソリューションコース）、平均年収は727万円。勤続年数16.9年と、長く勤められる銀行だよ。'),
  ('resona', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_07.png', 'nana',   'でもメガバンクと違って、りそなって複雑そう…私、そんな金融、できるかな。'),
  ('resona', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_08.png', 'haruki', 'それが違うんだよ。りそなは採用を12コースに分けてて、「ソリューションコース」「専門コース」「カスタマーサービスコース」など自分のタイプを選べる。複数コース間を動ける柔軟さもあるんだ。'),
  ('resona', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_09.png', 'nana',   '12コース…？それなら、どんな未来があるの？'),
  ('resona', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/resona/panel_10.png', 'haruki', '三メガとトラストを除いてリテールNo.1を目指す中期経営計画を動かしている。「金融＋で、未来をプラスに。」——金融に何かをプラスする人、りそなが採ってるのは「銀行の枠を超えた発想」と「幅広いつながり」を作れる人。');

-- 三井住友信託銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'smtb',
  '三井住友信託銀行',
  'banking_insurance',
  '受託資産（AUF）140兆円・純利益2,576億円（前期比×3.3、過去最高）。創業100年。「Trust Bank, Investment Bank, More than Banking」。初任給26.8万円、平均年収752万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('smtb', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_01.png', 'nana',   '信託銀行って、普通の銀行と何が違うの？'),
  ('smtb', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_02.png', 'haruki', '信託銀行は、資産を「預かる」だけじゃない、「代を越えて預かる」銀行。三井住友信託はその業界首位。預かり資産（AUF）は140兆円、純利益は2025年3月期で2,576億円、前期比3.3倍の過去最高。'),
  ('smtb', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_03.png', 'nana',   '140兆円を預かる…？そんな会社、どこで接点あるの？'),
  ('smtb', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_04.png', 'haruki', 'SNSやネットでよく見かけるよ。退職金の運用、企業年金、インデックスファンド（日興アセットマネジメント、今のアモーヴア）、遺言信託、不動産信託…シニア世代の「子に家を残したい」という願いも、ここが動いてる。'),
  ('smtb', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_05.png', 'nana',   'そんなところに入ったら、お給料どうなるの？'),
  ('smtb', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_06.png', 'haruki', '初任給は26万8,000円、平均年収は752万円。中長期の育成重視だから、仕事のやりがいも、同期との関係も上質だと評判。'),
  ('smtb', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_07.png', 'nana',   '1万人エントリーして400人採用って…トップ名門だけじゃないんだよね。'),
  ('smtb', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_08.png', 'haruki', '信託は「人間関係・長期信任」をもともと評価してて、求める人物像は「信託の受託者精神を持ち、長期視点で考える人」。「現場で動く強さ」「複雑な課題をやり抜く粘り強さ」が学歴より重要。'),
  ('smtb', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_09.png', 'nana',   '長期視点で考える人…それ、ちょっと私にも当てはまるかも。'),
  ('smtb', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/smtb/panel_10.png', 'nana',   '100年という時間軸を手にして、「未来を花開かせる」仕事——三井住友信託はそういう会社。「Trust Bank, Investment Bank, More than Banking」。2030年、ここで私はなにを花開かせていたいだろう？');

-- 三菱UFJ信託銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'mufg-trust',
  '三菱UFJ信託銀行',
  'banking_insurance',
  'MUFGグループ中核。信託銀行業界トップクラス。平均年収951万円（全銀行でも最高水準）。初任給学部30万円・修士33万円。「人をつなぐ。未来をつなぐ。」',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mufg-trust', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_01.png', 'nana',   '三菱UFJ信託銀行って、三菱UFJ銀行と別の会社なの？'),
  ('mufg-trust', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_02.png', 'haruki', 'そうなんだよ。三菱UFJ銀行の姉妹会社、位置づけとしてはMUFGグループの中核会社の一つだよ。そして信託銀行として業界トップクラス、平均年収は951万円で全銀行でも最高水準。'),
  ('mufg-trust', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_03.png', 'nana',   '951万円…？うちの実家の貯金も、もしかしてここに預けてるの？'),
  ('mufg-trust', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_04.png', 'haruki', 'さぁ、貯金は銀行だろうね。でも、もしお父さんが会社員なら、退職金の運用や企業年金は三菱UFJ信託が入ってる可能性高いよ。住宅ローン、遺産、不動産——「世代を越えた資産」を託されてる会社。家族の見えない部分でしっかり動いてる会社なんだよ。'),
  ('mufg-trust', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_05.png', 'nana',   'うわー…そんなとこに入ったら、お給料どうなるの？'),
  ('mufg-trust', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_06.png', 'haruki', '初任給は学部30万円・修士33万円。平均年収は951万円。メガバンクを超えて業界首位クラス。信託銀行としては業界トップだよ。'),
  ('mufg-trust', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_07.png', 'nana',   '三菱UFJ信託って、採用はトップ名門が多いよという評判だよね…。私、信託について詳しいわけじゃないし、ちょっと不安。'),
  ('mufg-trust', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_08.png', 'haruki', 'ちょっと待って。もしナナが、「もらったものにはていねいにお返しする人」「サークルの同期と先輩の間をつなぐような仕事をしたことがある」なら、この会社の「人をつなぐ」仕事は、ナナに向いてる。金融知識は入ってからでも間に合うよ。'),
  ('mufg-trust', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_09.png', 'nana',   '「人をつなぐ」仕事。それ、本当に私にできるのかな…？個人のお客さんと長く付き合う自分の姿が、今見えた気がした。'),
  ('mufg-trust', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mufg-trust/panel_10.png', 'both',   '1927年、三菱信託として創業してもう100年近く、この会社は「人をつなぐ。未来をつなぐ。」をコーポレートメッセージにしてきた。個人と個人を、人と社会を、現在と未来をつなぐ仕事。MUFGの「世界が進むチカラになる。」というパーパスの中、信託銀行として人の人生に長期で伴走していく。');

-- ゆうちょ銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'yucho',
  'ゆうちょ銀行',
  'banking_insurance',
  '貯金残高192兆円（個人貯金日本最大級）・純利益4,001億円。全国約2万拠点の郵便局ネットワーク。「ゆうちょして、ひろがる。」初任給25.5万円、平均年収716万円、平均勤続21年。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('yucho', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_01.png', 'nana',   'ゆうちょ銀行って、郵便局と同じ会社？'),
  ('yucho', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_02.png', 'haruki', '同じグループだけど、ゆうちょ銀行としては上場独立した会社だよ。貯金残高は192兆円、日本全国の個人貯金の単独トップ。純利益も4,001億円だよ。'),
  ('yucho', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_03.png', 'nana',   '貯金192兆円って…うちのおばあちゃんも、もしかしてゆうちょ？'),
  ('yucho', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_04.png', 'haruki', '高い確率でそうかも。全国約2万拠点という圧倒的なネットワーク。郵便局のそばにあるATMも、スマホの「ゆうちょ通帳アプリ」も、ゆうちょPayも、全部ここ。コンビニATMサービスもゆうちょ連携だよ。'),
  ('yucho', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_05.png', 'nana',   'そんなところに入ったら、お給料どうなるの？'),
  ('yucho', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_06.png', 'haruki', '初任給は25万5,000円、平均年収は716万円。メガバンクよりは低めだけど、平均勤続21年という長期雇用。生涯賃金で見るとメガとそん色ないよ。'),
  ('yucho', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_07.png', 'nana',   'メガより低いのに、一生勤められるんだよね…それはそれで不安、仕事物足りなそう。'),
  ('yucho', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_08.png', 'haruki', 'それが違うんだよ。「2026年以降の次世代デジタルサービス」「Σビジネス」「グリーン投資」……ゆうちょは今、「信頼を深め、金融革新に挑戦」する5年間の中だよ。「郵便局銀行」というイメージの裏で、世界最大級の機関投資家として動いてる一面もある。'),
  ('yucho', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_09.png', 'nana',   '郵便局銀行、という裏をもう一度中身を見てみたら、もしかして仕事、面白いかもしれないね。'),
  ('yucho', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/yucho/panel_10.png', 'haruki', '「ゆうちょして、ひろがる。」それがゆうちょ銀行のスローガン。経営理念は「お客さまから最も信頼される、もっとも身近で、もっとも便利な銀行」。2026年度からは次期中期経営計画も始まる。金融革新と地域・社会の未来を能動的につくる人財を採ってる。');

-- 千葉銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'chibagin',
  '千葉銀行',
  'banking_insurance',
  '純利益720億円（地銀トップクラス）。2030年目標1,000億円・NY/ロンドン/香港/上海に海外拠点。第16次中計「エンゲージメントバンクグループ〜フェーズ2〜」。平均年収795万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('chibagin', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_01.png', 'nana',   '千葉銀行ってさ、地銀って印象あるけど、ちょっと地味じゃない？'),
  ('chibagin', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_02.png', 'haruki', '地味って言ったかい？じゃあ数字見てみよ。純利益720億円、地銀のトップクラス。2030年度には1,000億円を目指してる。ニューヨーク・ロンドン・香港・上海に海外拠点もあるからね。地銀の枠を完全に飛び越えてる。'),
  ('chibagin', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_03.png', 'nana',   'えっ、地銀なのに海外拠点まで？地味どころか、めっちゃアクティブじゃん…！'),
  ('chibagin', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_04.png', 'haruki', 'そりゃ千葉県は成田空港もあれば、ディズニーもあるし、京葉工業地帯も房総半島の農業もある。多様性の塊。お父さんの会社の取引銀行も、おばあちゃんが孫のために積み立てた定期も、お母さんの住宅ローンも、千葉県内なら千葉銀行で繋がってる可能性が一番高い。'),
  ('chibagin', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_05.png', 'nana',   'そんなところに入ったら、お給料はどうなるの？'),
  ('chibagin', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_06.png', 'haruki', '初任給は26万円、平均年収は795万円（平均年齢38.5歳）。地銀の中では断トツのトップクラスだよ。一部のメガバンクを超えてる。'),
  ('chibagin', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_07.png', 'nana',   'でもさ、銀行って金利環境とか厳しそうじゃない？私、入ったあと「あれ、就職先間違えたかな」ってなるの嫌だな…。'),
  ('chibagin', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_08.png', 'haruki', '大丈夫、よく見てみて。千葉銀行が新しく出した第16次中期経営計画は「エンゲージメントバンクグループ〜フェーズ2〜」。「人×AIで生産性向上、地域まるごとDX・GX・WX」って戦略を打ち出してる。利上げ局面で追い風になってる業界の中で、ROE目標8%、純利益1,000億円を明確に掲げてる、攻めの地銀だよ。'),
  ('chibagin', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_09.png', 'nana',   '攻めの地銀、エンゲージメントバンク…なんだか、地元と一緒に走るって感じ、いいかも。私、千葉のあのお祭りも、海も、結構好きだったな。'),
  ('chibagin', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chibagin/panel_10.png', 'nana',   '千葉銀行のパーパスは「一人ひとりの思いを、もっと実現できる地域社会にする」。人材育成方針は「共に走り続ける人に。」。地元のお客さま一人ひとり、一社一社と「深いつながり」を築きながら、自分も地域社会も一緒に成長していく。私、ここで誰かと一緒に走ってみたいかも。');

-- 横浜銀行
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'hamagin',
  '横浜銀行',
  'banking_insurance',
  '1920年創業・地銀日本最大級。神奈川県内602拠点。2025年10月「横浜フィナンシャルグループ」に社名変更。2028年純利益1,200億円超を目標。平均年収771万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('hamagin', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_01.png', 'nana',   '横浜銀行って、三菱UFJとかと並んでよく名前を見るけど、やっぱり地銀なの？'),
  ('hamagin', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_02.png', 'haruki', '地銀だよ。だけどね、地銀としては日本最大級だよ。1920年創業、関東大震災からの復興を支えるために誕生した「横浜興信銀行」がルーツ。今年10月、持株会社を「横浜フィナンシャルグループ」に改名したばかり。「神奈川回帰」を掲げてるグループだよ。'),
  ('hamagin', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_03.png', 'nana',   '105年前の震災からの復興…？そんな背景で生まれた銀行、「地域にとってなくてはならない」って、なんか自然に言えそう。'),
  ('hamagin', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_04.png', 'haruki', 'そりゃそうだよ。誕生のその背景が「地域にとってなくてはならない存在」という経営理念そのものになってるんだ。神奈川県に602の拠点があって、県内の中小企業のメインバンクになってる。もしナナが神奈川県出身なら、うちの親も、街のお店も、現金も、もしかして横浜銀行かもしれないよ。'),
  ('hamagin', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_05.png', 'nana',   'そんなところに入ったら、お給料どうなるの？'),
  ('hamagin', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_06.png', 'haruki', '初任給は26万5,000円、平均年収は771万円。地銀トップクラス。不動産、企業年金、中小企業貸し出しと、様々な分野でやりがいある仕事があるよ。'),
  ('hamagin', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_07.png', 'nana',   'でもさ、横浜銀行って「銘柄だけど退屈そう」とか言われてる人もいるんだよね…。そういうの、私、不安だなぁ。'),
  ('hamagin', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_08.png', 'haruki', 'それが違うんだよ。中計「Growth / Empowerment / Sustainability」を掲げて、「金利のある世界」に合わせて、低金利時代にやってた店舗統廃合を転換して「店舗を核に中小企業貸し出しを強化」する「店舗回帰」路線に振り込んだばかりだよ。地域に人を返し、面と面での長期伴走に重きを置いてる。'),
  ('hamagin', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_09.png', 'nana',   '人間関係を仕事の中心に置く、適度な規模の地銀。そういう働き方を一度体験してみたい、かもしれない。'),
  ('hamagin', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/hamagin/panel_10.png', 'both',   '1920年、関東大震災からの復興を支えるために生まれた「横浜興信銀行」。それから105年、この銀行は「お客さまに信頼され、地域にとってなくてはならない金融グループ」であり続けてきた。いま「地域に根ざし、ともに歩むソリューション・カンパニー」を目指して、スタートアップ、中小企業、シニア世代と並走する人財を採り続けているよ。');

-- 検証ステータス更新
UPDATE companies SET last_verified_at='2026-05-27', verification_status='verified'
WHERE id IN ('smbc-bank','mizuho-fg','resona','smtb','mufg-trust','yucho','chibagin','hamagin');
