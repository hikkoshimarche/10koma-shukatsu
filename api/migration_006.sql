-- Phase B-1: 総合商社7社 + 専門商社2社（9社×10コマ = 90パネル）
-- industries: sogo_shosha / specialty_trading は既に存在するため INSERT OR IGNORE のみ

-- 三井物産
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'mitsui-bussan',
  '三井物産',
  'sogo_shosha',
  '売上14兆6,000億円・グループ5万6,400人。鉄鉱石・LNG・食料・医療・自動車・データセンターまで「地球まるごと」扱う総合商社。平均年収1,996万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mitsui-bussan', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_01.png', 'nana',   '三井物産ってよく聞くけど…結局なにしてる会社なの？'),
  ('mitsui-bussan', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_02.png', 'haruki', '売上、いくらだと思う？／うーん…1兆円とか！？／14兆6,000億円（2025年3月期）。グループで5万6,400人。／え、ケタ間違えてない…！？'),
  ('mitsui-bussan', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_03.png', 'haruki', 'でもさ、商社って遠い世界じゃないんだよ。ナナがコンビニで買うサラダチキン、その鶏肉も、ガソリンの原油も、スマホに入ってる金属も、全部どこかで商社が動かしてる。'),
  ('mitsui-bussan', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_04.png', 'nana',   'え、待って、ぜんぶ！？鉄鉱石・LNG・食料・医療・自動車・データセンターまで、地球まるごと扱ってるってこと？私の生活、知らない間に商社にめっちゃ支えられてた…！'),
  ('mitsui-bussan', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,996万円（2025年3月期、有報）。／せ、せん…きゅうひゃくきゅうじゅうろくまん…！？'),
  ('mitsui-bussan', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_06.png', 'haruki', '新卒1年目の初任給も学部卒34万円、院卒37.5万円（Global総合職・2026年4月予定）。'),
  ('mitsui-bussan', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／確かに難しい。2025年度の採用は142名。倍率は推定50倍超。東洋経済の「入社が難しい企業ランキング」でも4位。／やっぱり…無理ゲーだ…'),
  ('mitsui-bussan', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_08.png', 'haruki', 'でもね、三井物産の採用、実は学歴フィルター明文化されてない。採用大学一覧見ると、全国の国立、地方の私立、海外大学からも内定出てる。重視されるのは「TOEIC」より「自分で動いた経験」。長期インターンや学外活動が刺さる。'),
  ('mitsui-bussan', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？ブラジルで100億円規模の鉄鉱石プロジェクトを動かしてるかもしれない。東京でAI×医療の新規事業を立ち上げてるかもしれない。シンガポールでスタートアップに投資してるかもしれない。三井物産だと、全部「普通にある未来」だよ。'),
  ('mitsui-bussan', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui-bussan/panel_10.png', 'both',   '2025年度は総合職142名採用。求めるのは「自ら考え、行動し、未来をつくる人材」。三井物産は140年前から「人の三井」と呼ばれてきた。一人ひとりの挑戦が、世界を動かす。「世界中の未来をつくる」——次は、ナナの番。');

-- 伊藤忠商事
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'itochu',
  '伊藤忠商事',
  'sogo_shosha',
  '売上14兆7,000億円・純利益8,803億円で過去最高益更新。ファミマを完全子会社化。「川下」戦略を持つ唯一の総合商社。平均年収1,805万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('itochu', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_01.png', 'nana',   'ねえハルキ、伊藤忠商事って…なんか名前は聞くけど、何やってる会社か全然わかんない。'),
  ('itochu', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_02.png', 'haruki', '売上、いくらだと思う？／え、5兆円くらい！？／14兆7,000億円（2025年3月期）。しかも純利益8,803億円で過去最高益更新。／か、過去最高！？'),
  ('itochu', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_03.png', 'haruki', 'でね、伊藤忠ってナナの生活のすぐ近くにある会社なんだよ。ファミマでナナがおにぎり買うとき、そのレジでFamiPay使うとき、全部伊藤忠グループ。'),
  ('itochu', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_04.png', 'nana',   'え、ファミマって伊藤忠なの！？2024年に完全子会社化した。1日1,500万人がファミマで買い物してる。それ全部、伊藤忠が支えてる。私、ほぼ毎日伊藤忠にお金落としてた…！'),
  ('itochu', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_05.png', 'nana',   'ところで…お給料は？／平均年収1,805万円（2025年3月期、有報）。／せ、せん…はっぴゃくまん…！？'),
  ('itochu', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_06.png', 'haruki', '新卒1年目の初任給も学部卒・院卒ともに月36万円（2026年4月入社、総合職）。主要企業で最高水準。しかも朝型勤務で残業も少ない。'),
  ('itochu', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_07.png', 'nana',   'でも…私みたいな普通の学生、入れる気しない…／確かに難しい。倍率は推定188倍超（2025年度）。総合職採用は毎年100名程度。／188倍…宝くじレベルだ…'),
  ('itochu', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_08.png', 'haruki', 'でもね、伊藤忠の採用、実は中途採用比率15%もある。多様なバックグラウンドの人を集めてる。新卒も「学歴」より「商人マインド」重視。長期インターンやビジネスコンテスト経験、起業経験は超強い。文化部出身でも、留学経験なしでも内定取ってる人いる。'),
  ('itochu', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？アジアでファミマの新業態を立ち上げてるかもしれない。東京で食品ベンチャーへの投資を任されてるかもしれない。海外駐在でアパレルブランドを展開してるかもしれない。「川下」が伊藤忠の戦略だから、消費者に近い場所で勝負できるんだ。'),
  ('itochu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/itochu/panel_10.png', 'both',   '2026年度は新卒150名採用。求めるのは「商人マインド」を持つ人。近江商人から続く「三方よし」——売り手よし、買い手よし、世間よし。「ひとりの商人、無数の使命」——伊藤忠は、その一人を待ってる。');

-- 住友商事
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'sumitomo-corp',
  '住友商事',
  'sogo_shosha',
  '売上7兆7,000億円・純利益5,624億円。月平均残業9.9時間で「高年収×ホワイト」。「求める人物像を設けていない」ユニークな採用姿勢。平均年収1,744万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('sumitomo-corp', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_01.png', 'nana',   '住友商事ってよく名前は聞くけど…他の商社と何が違うの？'),
  ('sumitomo-corp', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_02.png', 'haruki', '売上規模、いくらだと思う？／うーん…3兆円とか！？／7兆7,000億円規模、純利益5,624億円（2025年3月期）。グループで約7万9,000人。／え、鉄鋼とかだけじゃないんだ…！？'),
  ('sumitomo-corp', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_03.png', 'haruki', '住友商事ってさ、ナナの生活のすぐ近くにもいるよ。ケーブルテレビの「J:COM」も、SCSKとかのITサービス、街で見るトヨタ販売店、全部住友商事グループ。'),
  ('sumitomo-corp', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_04.png', 'nana',   'え、J:COMとかSCSKも！？住友商事は鉄鋼・自動車・不動産・メディア・金属・デジタルまで全9グループ。ケーブルテレビとITだけで企業価値1兆円超える。私のスマホのWi-Fiも、住友商事がつなげてるんだ…！'),
  ('sumitomo-corp', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,744万円（2025年3月期、有報）。／せ、せん…せんななひゃくよんしゃんまん…！？'),
  ('sumitomo-corp', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_06.png', 'haruki', 'しかも、月平均残業は9.9時間。商社業界で最低水準。スーパーフレックスもテレワークもある。「高年収×ホワイト」で有名。'),
  ('sumitomo-corp', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／確かに難しい。採用倍率は推定189倍（2026年度）。採用人数は毎年100名程度。／やっぱり…189倍は無理じゃん…'),
  ('sumitomo-corp', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_08.png', 'haruki', 'でもね、住友商事は「求める人物像を設けていない」って公式に言ってるんだよ。「多様な個が集まることが競争力」という考え方。中途採用比率も40%と業界最高。それぞれの個性を見てくれる。'),
  ('sumitomo-corp', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？インドでメディア事業を拡大しているかもしれない。東京でAIの新規事業を立ち上げているかもしれない。アフリカでEVインフラをゼロから作ってるかもしれない。9グループもあるから、選び放題だよ。'),
  ('sumitomo-corp', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sumitomo-corp/panel_10.png', 'both',   '2026年度はプロフェッショナル職100名程度を採用。住友商事は「求める人物像を設けていない」。多様な「個」が集まることが、競争力——だからこそ、私みたいな普通の学生にもチャンスがある。「Enriching lives and the world」——豊かさを、たたえる、つくる。');

-- 丸紅
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'marubeni',
  '丸紅',
  'sogo_shosha',
  '創業166年・売上7兆8,000億円・純利益5,030億円。「ギアチェンジ」をテーマに変革中。月平均残業15.8時間、離職率1.3%。平均年収1,709万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('marubeni', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_01.png', 'nana',   'ねえハルキ、丸紅って…「丸紅」って名前は古いけど、何してる会社なの？'),
  ('marubeni', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_02.png', 'haruki', '収益、いくらだと思う？／うーん…2兆円とか？／7兆8,000億円（2025年3月期）。純利益も5,030億円。／え、ケタちゃう…！？'),
  ('marubeni', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_03.png', 'haruki', 'でもさ、丸紅ってナナの生活のすぐ近くにもいるよ。ナナが毎朝飲むコーヒーの豆も、コンビニのカントリーマアムの製造も、スマホの電気も、世界中の食材や電力事業で丸紅が関わってる。'),
  ('marubeni', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_04.png', 'nana',   'カントリーマアムには反応した！あれ作ってるの！？ベトナムで製造工場を拡充したんだ。丸紅は「資源と非資源のバランス」が上手で、食材・電力・航空機リースなんかも広くやってる。私の毎日、丸紅だらけなんだ…！'),
  ('marubeni', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,709万円（2025年3月期、有報）。／せ、せん…、せんなななひゃくまん…！？'),
  ('marubeni', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_06.png', 'haruki', 'しかもさ、丸紅は5大商社の中でも月平均残業が15.8時間と少なめ。離職率は1.3%。学部33万円、院卒36.5万円。賞与含めると入社初年で年収500万円超えるよ。'),
  ('marubeni', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_07.png', 'nana',   'でも、そんな会社…採用は鬼狭き門なんでしょ？／2025年度の採用はたった77名。倍率は推定200倍超。／200倍…超難関だ…私にも無理だよ。'),
  ('marubeni', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_08.png', 'haruki', 'でもね、丸紅のキャリア採用比率は37.9%。弁護士や会計士、トップ企業出身もどんどん入ってきてる。そもそも丸紅は「面白くない会社」を脱却しようとしてて、「ギアチェンジ」がテーマ。多様な人を求めてるよ。'),
  ('marubeni', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？ベトナムで製菓工場を動かしてるかもしれない。米国でAIデータセンター事業をリードしてるかもしれない。豪州でグリーン水素プロジェクトを指揮してるかもしれない。ギアチェンジの会社だから、どの領域も成長のチャンスがある。'),
  ('marubeni', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/marubeni/panel_10.png', 'both',   '1858年、近江商人の伊藤忠兵衛から始まった丸紅。167年経った今も、社是は「正・新・親」。公明正大、進取の気魄、人を思いやる心——「面白くない会社」を脱却、2030年に時価総額10兆円へ。丸紅は、その「個の力」を待ってる。');

-- 豊田通商
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'toyota-tsusho',
  '豊田通商',
  'sogo_shosha',
  '売上10兆3,000億円・連結約7万人。アフリカ全土54ヶ国で事業展開。「WITH AFRICA FOR AFRICA」を掲げるトヨタグループ唯一の総合商社。平均年収1,320万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('toyota-tsusho', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_01.png', 'nana',   'ねえハルキ、豊田通商って…もしかしてトヨタの仕事だけやってる会社？'),
  ('toyota-tsusho', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_02.png', 'haruki', '収益、いくらだと思う？／うーん…3兆円ぐらい？／10兆3,000億円（2025年3月期）。連結で約7万人もいる。／え、ケタ違うわ…！？'),
  ('toyota-tsusho', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_03.png', 'haruki', '何がすごいって、豊田通商はアフリカ全土54ヶ国で事業をやってるんだ。アフリカでトヨタ車走ってるの見たことある？あれ全部、豊田通商が現地に取り扱い店を作って、部品を供給して、メンテナンスしてる。アフリカ事業だけで収益1兆円超。'),
  ('toyota-tsusho', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_04.png', 'nana',   'アフリカにそんなに深く関わってる会社、初めて聞いた…！「WITH AFRICA FOR AFRICA」ってスローガンを掲げてる。アフリカの子どもの医療、電力、教育…生活そのものを支えてる。他の商社と全然違う…！'),
  ('toyota-tsusho', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,320万円（2025年3月期、有報）。／せ、せん…せんせんさんびゃくまん…！？'),
  ('toyota-tsusho', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_06.png', 'haruki', '初任給は28.5万円（グローバル職）。他5大商社より少し控えめだけど、海外駐在になると手当で年収が倍近くになるケースもあるよ。しかも新卒1年目は会社のマンションに月2,000円で住める。'),
  ('toyota-tsusho', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_07.png', 'nana',   'でも、そんな会社…採用めちゃくちゃ難しいんでしょ？／採用倍率は推定100倍前後。難関大出身者も多い。／100倍…やっぱり難しいんだ…'),
  ('toyota-tsusho', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_08.png', 'haruki', 'でもね、豊田通商は名古屋本社だから、関西・中部圏の大学出身者が他商社より多い。名古屋大・南山大・同志社・立命館とかも採用実績ある。「アフリカやトヨタとともに世界を越えて挑戦したい」というマインドの人を採ってる。'),
  ('toyota-tsusho', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？ケニアでトヨタ車の販売事業をやってるかもしれない。ブラジルでリチウムサプライチェーンを動かしてるかもしれない。名古屋で水素ステーション事業をリードしてるかもしれない。トヨタという背中を持ちながら、未開拓の地で事業を作れるのが豊田通商だよ。'),
  ('toyota-tsusho', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota-tsusho/panel_10.png', 'both',   '連結69,517名、アフリカ全土54ヶ国で事業を動かす、トヨタグループ唯一の総合商社。「WITH AFRICA FOR AFRICA」——アフリカで人生する、を本当にやってる会社。名古屋から、世界の未来へ。豊田通商は、その挑戦者を待ってる。');

-- 双日
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'sojitz',
  '双日',
  'sogo_shosha',
  '売上2兆5,097億円。ベトナムでは3本指に入る日系企業。他5大商社が手薄な新興国を得意とする総合商社。採用倍率55倍、平均年収1,274万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('sojitz', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_01.png', 'nana',   'ねえハルキ、「双日」って商社、名前聴いたことあるけど何してる会社なの？'),
  ('sojitz', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_02.png', 'haruki', '収益、いくらだと思う？／うーん…5,000億円とか？／2兆5,097億円（2025年3月期、過去最高水準近い）。グループで約2万4,000人。／えーっ！そんなにあったの…！？'),
  ('sojitz', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_03.png', 'haruki', 'しかもさ、双日って、ナナがそんなに意識してないアジアの国で超存在感出してるんだよ。ベトナム、インド、モンゴル、ナイジェリア…。ベトナムのスーパーやコンビニ、インドの農産物、モンゴルでの資源開発…、全部双日がやってる。'),
  ('sojitz', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_04.png', 'nana',   'え、ベトナムのコンビニも！？双日は「ベトナムでは3本指に入る日系企業」と言われるほど。他5大商社が手をつけてない「スキマ」を独り歩きしてる。ベトナム・ハノイで見たコンビニ、双日のおかげだったのか…！'),
  ('sojitz', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,274万円（2025年3月期、有報）。しかも平均年齢41歳。5大商社より若いのに並ぶ。／う、うそでしょ…！？'),
  ('sojitz', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_06.png', 'haruki', '初任給は学部卒30.5万円、院卒34万円。賞与含めて1年目で年収500〜550万円。新卒1年目から500万超えの7大商社！'),
  ('sojitz', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／確かに難しい。採用は毎年130名規模、倍率55倍。他5大商社よりは関門が低めだよ。／えーっ、倍率「たった」55倍！？'),
  ('sojitz', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_08.png', 'haruki', 'しかも双日は「多様性を競争力に」をガチで掲げている商社だよ。採用実績見ると、東大や京大はもちろん、鳥取大や鹿児島大、全国の大学から採用してる。学歴より「この人としかやりたくない人生」が評価される。'),
  ('sojitz', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？ベトナム・ハノイでスーパー事業を拡大してるかもしれない。インドでサプライチェーンを作っているかもしれない。モンゴルで資源開発プロジェクトを任されているかもしれない。「他社が手をつけていない地域で先駆け」るのが双日だよ。'),
  ('sojitz', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/sojitz/panel_10.png', 'both',   '「普通の学生」だった先輩が、いま世界を動かしてる。次はナナの番かも。まずは説明会、行ってみない？');

-- 兼松
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'kanematsu',
  '兼松',
  'sogo_shosha',
  '売上1兆50億円。電子・デバイスと航空宇宙を主力とする総合商社。採用倍率推定17倍と他商社より狙いやすい。平均年収1,143万円（平均年齢38.2歳）。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('kanematsu', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_01.png', 'nana',   'ねえハルキ、「兼松」って初耳だけど何してる会社？'),
  ('kanematsu', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_02.png', 'haruki', '売上、いくらだと思う？／うーん…2,000億円とか？／1兆50億円（2025年3月期、前期比+6.6%）。純利益274億円。／え、一兆越えてるの！？'),
  ('kanematsu', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_03.png', 'haruki', '兼松の主力は実は「電子・デバイス」だよ。ナナが使ってるスマホやPCの中に入ってる部品、企業のサーバー・ストレージ、データセンターなど、「見えないけど世の中を支えてるテクノロジー」を企業に届けてる。'),
  ('kanematsu', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_04.png', 'nana',   'え、私のiPhoneの中にも入ってる部品が？グループ会社の「兼松エレクトロニクス」は上場してるITサービスのトップ企業。2つ目は航空宇宙。防衛・航空機部品、ロケットパーツ、街で見るレンタカーもやってる。スマホの中とロケットを両方やってる会社、ロマンさえ感じる…！'),
  ('kanematsu', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収1,143万円（2025年3月期、有報）。平均年齢38.2歳。5大商社より3・4歳若い。／えーっ！それ38.2歳で！？'),
  ('kanematsu', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_06.png', 'haruki', 'しかも初任給は学部卒も院卒も29万円。他5大商社とそんなに変わらないじゃない！'),
  ('kanematsu', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／それがね、採用倍率は推定17倍。／17倍って、他の商社と桁が一つ違うよね！／本当だよ。他5大と並ぶと、「ん？ケタ違う？」と思う倍率。'),
  ('kanematsu', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_08.png', 'haruki', 'しかも兼松は「冒険家のように商売しよう」をバリューに掲げている。大手と違うところを見て、狙う。IT、航空宇宙、食料、鉄鋼・プラントと4セグメント。実際、入社者の「オタク」や「スタートアップ詳しい人」も多いよ。'),
  ('kanematsu', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？シリコンバレーでAIスタートアップと提携してるかもしれない。防衛・航空機でロケットの調達でタイに駐在してるかもしれない。食品でブラジルを飛び回ってるかもしれない。「他商社と違う」領域で、縦長志向なら勝負できるよ。'),
  ('kanematsu', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/kanematsu/panel_10.png', 'both',   '「普通の学生」だった先輩が、いま世界を動かしてる。次はナナの番かも。まずは説明会、行ってみない？');

-- 稲畑産業（専門商社）
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'inabata',
  '稲畑産業',
  'specialty_trading',
  '売上8,378億円（2025年3月期、過去最高更新）。住友化学グループの化学品専門商社。スマホ・半導体材料から医薬品まで。アジア12カ国59拠点。平均年収984万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('inabata', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_01.png', 'nana',   'ねえハルキ、「稲畑産業」って、聞いたことないかも…でも気になる名前。'),
  ('inabata', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_02.png', 'haruki', '売上、いくらだと思う？／うーん…1,000億円とか？／8,378億円（2025年3月期、過去最高更新）。営業利益も258億円で過去最高。／え、ほぼ1兆！？知名度低いのに、そんなに大きいの！？'),
  ('inabata', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_03.png', 'haruki', 'ナナのスマホ画面、何でできてると思う？その液晶・有機ELの材料、稲畑産業が大手メーカーに納めてる。半導体関連や電池材料も。目に見えないけど、毎日触ってるテクノロジーの裏方。'),
  ('inabata', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_04.png', 'nana',   'え、私のiPhone画面の中に、稲畑産業が…！？しかも住友化学グループだから、化学業界の超太いパイプを持ってる。海外もアジア12カ国59拠点、社員の62%が海外で働いてる。なんか、ロマンある…！「見えないけど、世界を動かしてる」って感じ…！'),
  ('inabata', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収984万円（2025年3月期、有報）。／……うそでしょ！？大手商社じゃないのに、1,000万円近い！？'),
  ('inabata', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_06.png', 'haruki', '初任給は学部卒26万円、院卒27.4万円。8期連続増配中の超優良企業。'),
  ('inabata', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／採用は年間20〜35名。少数精鋭だから、倍率は高い。けど、5大商社の「189倍」とかとは桁が違う。／そうなんだ…でも、少数だから一人ひとり見られそうで、それはそれで怖い…'),
  ('inabata', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_08.png', 'haruki', 'でもね、稲畑産業は「化学の専門家×グローバル」を志向する人を求めてる。文系でも全然OK。顧客の生産ラインを一緒に作るイメージ。「人と深く付き合える人」「1社のお客さんと10年付き合える誠実さ」が刺さる。関西圏出身は特に有利。'),
  ('inabata', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？バンコクでコンパウンド工場を立ち上げてるかもしれない。韓国で半導体メーカーに材料を納めてるかもしれない。ベトナムで医薬品の新規事業を任されてるかもしれない。少数精鋭だから、20代でも海外赴任は当たり前だよ。'),
  ('inabata', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/inabata/panel_10.png', 'both',   '1890年、パリ留学帰りの稲畑勝太郎が始めた化学品商社。「自利利他・公私一如」——135年、その精神は今も生きてる。目に見えないけど、世界を動かしてる会社って、こういうことか…！');

-- 蝶理（専門商社）
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'chori',
  '蝶理',
  'specialty_trading',
  '1861年創業・大阪本社。繊維と化学品の専門商社。ユニクロ・ナイキ・アディダスの生地を手がける。4期連続過去最高益。平均年収925万円、総合職平均1,147万円。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_01.png',
  NULL
);

INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('chori', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_01.png', 'nana',   'ねえハルキ、「蝶理」って名前聴いたことないよ…蝶？理？'),
  ('chori', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_02.png', 'haruki', '創業何年だと思う？／うーん…、50年とか？／1861年。今年で165年目。京都の西陣で糸商として起こした。明治維新より前だよ。／えーっ！江戸時代からずっと続いてる会社ってこと！？'),
  ('chori', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_03.png', 'haruki', 'しかもさ、ナナのよく知ってるブランドにも関わってるよ。ユニクロ、ナイキ、アディダス、ゴルフアパレルなど。高機能繊維やスポーツウェアの生地をアジアの工場で作って、それを全世界に届けてるのが蝶理。さらに、化粧品や医薬品の原料もやってるよ。'),
  ('chori', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_04.png', 'nana',   'え、ユニクロの服も関わってるんだ！？化粧品も！？繊維事業と化学品事業で売上がほぼ半々。しかもさ、本社は大阪だよ。大阪本社で、ユニクロの裏方として出てるなんて…めっちゃローカルキャリア感ある！'),
  ('chori', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_05.png', 'nana',   'ところで…ぶっちゃけお給料は？／平均年収925万円、総合職だと平均1,147万円。／えーっ！専門商社でもそんなにもらえるの…！'),
  ('chori', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_06.png', 'haruki', 'しかも4期連続過去最高益更新。今期、初めて純利益100億円台に到達したんだ。右肩上がりの高年収。'),
  ('chori', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_07.png', 'nana',   'でも、そんな会社…私なんかが入れるわけ…／採用は毎年15〜25名規模。少数精鋭だから、倍率はやっぱり高い。／そうだよね…もしかして、他の専門商社も同じくらい難しいんだ…'),
  ('chori', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_08.png', 'haruki', 'でもね、蝶理は「川上から川下まで一貫して関わりたい人」を求めてるよ。繊維なら、素材を調達して、工場で布を作るところまで見て、そしてブランドと一緒に服を企画して、最後に販売まで見る、ということ。「商社マン」というより「モノづくりに関わる人」に近い。'),
  ('chori', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_09.png', 'haruki', '入社して10年後、ナナはどんな自分になりたい？ベトナムのスポーツウェア工場を任されてるかもしれない。中国で医薬品原料の新規事業を立ち上げてるかもしれない。イタリアで高級ブランドとコラボの話を進めてるかもしれない。川上から川下まで、本当に世界のどこにでも出ていけるよ。'),
  ('chori', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/chori/panel_10.png', 'both',   '「普通の学生」だった先輩が、いま世界を動かしてる。次はナナの番かも。まずは説明会、行ってみない？');

-- 検証ステータス更新
UPDATE companies SET last_verified_at='2026-05-26', verification_status='verified'
WHERE id IN ('mitsui-bussan','itochu','sumitomo-corp','marubeni','toyota-tsusho','sojitz','kanematsu','inabata','chori');
