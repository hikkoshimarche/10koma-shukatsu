-- 業種: 自動車（先に作成）
INSERT OR IGNORE INTO industries (id, name, description, panel_count, thumbnail_url)
VALUES (
  'jidousha',
  '自動車',
  '日本の基幹産業。電動化・自動運転・モビリティサービスへの大変革期。',
  10,
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_01.png'
);

-- 会社: トヨタ自動車
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'toyota_motor',
  'トヨタ自動車',
  'jidousha',
  '世界販売台数1位の自動車メーカー。モビリティカンパニーへの変革を掲げ、HV/EV/水素の全方位電動化、コネクテッド、Woven Cityで未来を創る。',
  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_01.png',
  'https://www.youtube.com/watch?v=PLACEHOLDER_TOYOTA'
);

-- トヨタ自動車の10コマ
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('toyota_motor', 1,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_01.png', 'nana',   'トヨタって車作ってる会社だよね？それだけ？'),
  ('toyota_motor', 2,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_02.png', 'haruki', '売上50.7兆円・連結38.4万人。今は「モビリティカンパニー」を目指してるんだ'),
  ('toyota_motor', 3,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_03.png', 'nana',   'モビリティカンパニーって具体的に何？'),
  ('toyota_motor', 4,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_04.png', 'haruki', '①世界販売1,128万台 ②HV/EV/水素の全方位電動化が柱'),
  ('toyota_motor', 5,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_05.png', 'haruki', '③KINTOなど販売金融＋コネクテッド ④Woven Cityで未来都市実験'),
  ('toyota_motor', 6,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_06.png', 'haruki', '米国関税1.4兆円を吸収しても営業利益3.8兆円。強さの証明だね'),
  ('toyota_motor', 7,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_07.png', 'nana',   '凄い…で、給料とか働き方はどうなの？'),
  ('toyota_motor', 8,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_08.png', 'haruki', '初任給 学部27.5万/修士30万、平均年収982万、男性育休67.4%'),
  ('toyota_motor', 9,  'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_09.png', 'nana',   '選考フローと採用人数は？'),
  ('toyota_motor', 10, 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/toyota/panel_10.png', 'both',   '2024年度1,928名採用。「人間力×実行力」、合言葉は「あなたで加速します」');

-- 検証ステータス更新
UPDATE companies SET last_verified_at='2026-05-25', verification_status='verified' WHERE id='toyota_motor';
UPDATE industries SET last_verified_at='2026-05-25', verification_status='verified' WHERE id='jidousha';
