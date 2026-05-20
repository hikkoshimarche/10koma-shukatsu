-- ユーザー
CREATE TABLE IF NOT EXISTS users (
  line_user_id TEXT PRIMARY KEY,
  display_name TEXT,
  picture_url  TEXT,
  grade        TEXT,
  university   TEXT,
  target_industries TEXT,
  created_at   TEXT DEFAULT (datetime('now')),
  updated_at   TEXT DEFAULT (datetime('now'))
);

-- 業種
CREATE TABLE IF NOT EXISTS industries (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT,
  panel_count INTEGER DEFAULT 10,
  thumbnail_url TEXT,
  created_at  TEXT DEFAULT (datetime('now'))
);

-- 業種の10コマ
CREATE TABLE IF NOT EXISTS industry_panels (
  industry_id TEXT NOT NULL,
  panel_num   INTEGER NOT NULL,
  image_url   TEXT NOT NULL,
  character   TEXT NOT NULL,
  dialogue    TEXT NOT NULL,
  PRIMARY KEY (industry_id, panel_num),
  FOREIGN KEY (industry_id) REFERENCES industries(id)
);

-- 会社
CREATE TABLE IF NOT EXISTS companies (
  id           TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  industry_id  TEXT NOT NULL,
  description  TEXT,
  thumbnail_url TEXT,
  video_url    TEXT,
  created_at   TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (industry_id) REFERENCES industries(id)
);

-- 会社の10コマ
CREATE TABLE IF NOT EXISTS company_panels (
  company_id  TEXT NOT NULL,
  panel_num   INTEGER NOT NULL,
  image_url   TEXT NOT NULL,
  character   TEXT NOT NULL,
  dialogue    TEXT NOT NULL,
  PRIMARY KEY (company_id, panel_num),
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- いいね
CREATE TABLE IF NOT EXISTS likes (
  line_user_id TEXT NOT NULL,
  content_type TEXT NOT NULL,
  content_id   TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (line_user_id, content_type, content_id)
);

-- ブックマーク
CREATE TABLE IF NOT EXISTS bookmarks (
  line_user_id TEXT NOT NULL,
  company_id   TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (line_user_id, company_id)
);

-- 閲覧ログ
CREATE TABLE IF NOT EXISTS view_logs (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  line_user_id TEXT NOT NULL,
  content_type TEXT NOT NULL,
  content_id   TEXT NOT NULL,
  viewed_at    TEXT DEFAULT (datetime('now'))
);

-- シェアログ
CREATE TABLE IF NOT EXISTS share_logs (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  line_user_id TEXT NOT NULL,
  content_type TEXT NOT NULL,
  content_id   TEXT NOT NULL,
  shared_at    TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(line_user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks(line_user_id);
CREATE INDEX IF NOT EXISTS idx_view_logs_user_time ON view_logs(line_user_id, viewed_at);

-- =====================
-- β版シードデータ
-- =====================

-- 業種: 総合商社
INSERT OR IGNORE INTO industries (id, name, description, panel_count, thumbnail_url)
VALUES (
  'sogo_shosha',
  '総合商社',
  '世界中のビジネスをつなぐ。資源・食料・インフラなど幅広い分野に投資・経営参画する。',
  10,
  'https://assets.example.com/industries/sogo_shosha/thumbnail.jpg'
);

-- 総合商社の10コマ（仮URL・仮セリフ）
INSERT OR IGNORE INTO industry_panels (industry_id, panel_num, image_url, character, dialogue) VALUES
  ('sogo_shosha', 1,  'https://assets.example.com/industries/sogo_shosha/panel_01.jpg', 'nana',   '総合商社ってなんでも扱うって本当？'),
  ('sogo_shosha', 2,  'https://assets.example.com/industries/sogo_shosha/panel_02.jpg', 'haruki', 'そう！資源から食品、インフラまで世界中が舞台だよ'),
  ('sogo_shosha', 3,  'https://assets.example.com/industries/sogo_shosha/panel_03.jpg', 'nana',   'でも最近は「投資会社」化してるって聞いた'),
  ('sogo_shosha', 4,  'https://assets.example.com/industries/sogo_shosha/panel_04.jpg', 'haruki', '正確には「事業投資×経営参画」がモデルなんだ'),
  ('sogo_shosha', 5,  'https://assets.example.com/industries/sogo_shosha/panel_05.jpg', 'both',   '海外駐在率が高いのも特徴のひとつ！'),
  ('sogo_shosha', 6,  'https://assets.example.com/industries/sogo_shosha/panel_06.jpg', 'nana',   '入社後のキャリアはどう決まるの？'),
  ('sogo_shosha', 7,  'https://assets.example.com/industries/sogo_shosha/panel_07.jpg', 'haruki', '最初は営業・トレーディングが多いかな'),
  ('sogo_shosha', 8,  'https://assets.example.com/industries/sogo_shosha/panel_08.jpg', 'nana',   '文系でも理系でも活躍できる？'),
  ('sogo_shosha', 9,  'https://assets.example.com/industries/sogo_shosha/panel_09.jpg', 'haruki', 'もちろん！語学力とタフさが大事だよ'),
  ('sogo_shosha', 10, 'https://assets.example.com/industries/sogo_shosha/panel_10.jpg', 'both',   '気になる会社をチェックしてみよう！');

-- 会社: 三菱商事
INSERT OR IGNORE INTO companies (id, name, industry_id, description, thumbnail_url, video_url)
VALUES (
  'mitsubishi_corp',
  '三菱商事',
  'sogo_shosha',
  '日本最大級の総合商社。エネルギー・金属から食品・流通まで、世界90カ国以上でビジネスを展開。',
  'https://assets.example.com/companies/mitsubishi_corp/thumbnail.jpg',
  'https://www.youtube.com/watch?v=PLACEHOLDER_MC'
);

-- 三菱商事の10コマ（仮URL・仮セリフ）
INSERT OR IGNORE INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
  ('mitsubishi_corp', 1,  'https://assets.example.com/companies/mitsubishi_corp/panel_01.jpg', 'nana',   '三菱商事ってどんな会社？'),
  ('mitsubishi_corp', 2,  'https://assets.example.com/companies/mitsubishi_corp/panel_02.jpg', 'haruki', '売上高が日本トップクラスの総合商社だよ'),
  ('mitsubishi_corp', 3,  'https://assets.example.com/companies/mitsubishi_corp/panel_03.jpg', 'nana',   'どんな事業があるの？'),
  ('mitsubishi_corp', 4,  'https://assets.example.com/companies/mitsubishi_corp/panel_04.jpg', 'haruki', 'LNG・銅・ローソン…業種を超えて関わってる'),
  ('mitsubishi_corp', 5,  'https://assets.example.com/companies/mitsubishi_corp/panel_05.jpg', 'both',   '三菱グループの中核として存在感は抜群！'),
  ('mitsubishi_corp', 6,  'https://assets.example.com/companies/mitsubishi_corp/panel_06.jpg', 'nana',   '新卒採用の規模はどのくらい？'),
  ('mitsubishi_corp', 7,  'https://assets.example.com/companies/mitsubishi_corp/panel_07.jpg', 'haruki', '毎年100〜200名前後、倍率は数百倍とも'),
  ('mitsubishi_corp', 8,  'https://assets.example.com/companies/mitsubishi_corp/panel_08.jpg', 'nana',   '求められる人材像は？'),
  ('mitsubishi_corp', 9,  'https://assets.example.com/companies/mitsubishi_corp/panel_09.jpg', 'haruki', '「自分で考えて動ける」タフな人材が多い印象'),
  ('mitsubishi_corp', 10, 'https://assets.example.com/companies/mitsubishi_corp/panel_10.jpg', 'both',   'まずはインターンで雰囲気を掴もう！');
