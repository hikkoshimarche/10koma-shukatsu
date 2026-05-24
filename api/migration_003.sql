-- =====================
-- migration_003: 動画機能・OB機能用テーブル
-- =====================

-- 設定（パスワードなど可変値）
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- OB・内定者
CREATE TABLE IF NOT EXISTS obs (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  affiliation   TEXT NOT NULL,        -- 内定先 or 所属（例：野村證券）
  university    TEXT NOT NULL,        -- 卒業大学
  line_id       TEXT NOT NULL,        -- LINE ID
  industry_id   TEXT,                 -- 紐付け業界（任意）
  display_order INTEGER DEFAULT 100,
  created_at    TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (industry_id) REFERENCES industries(id)
);

CREATE INDEX IF NOT EXISTS idx_obs_industry ON obs(industry_id);

-- 動画（企業の video_url は既存。業界別動画は今後追加するため別テーブル）
CREATE TABLE IF NOT EXISTS industry_videos (
  industry_id   TEXT NOT NULL,
  video_url     TEXT NOT NULL,
  title         TEXT NOT NULL,
  display_order INTEGER DEFAULT 100,
  PRIMARY KEY (industry_id, video_url),
  FOREIGN KEY (industry_id) REFERENCES industries(id)
);

-- =====================
-- 初期データ
-- =====================

-- パスワード設定
INSERT OR REPLACE INTO settings (key, value, updated_at)
VALUES ('ob_password', 'osd2026', datetime('now'));

-- OB初期データ（田中 治樹）
INSERT OR IGNORE INTO obs (id, name, affiliation, university, line_id, industry_id, display_order)
VALUES (
  'tanaka_haruki',
  '田中 治樹',
  '野村證券',
  '明治大学',
  'tanaka_haruki',
  NULL,
  10
);

-- 動作確認
SELECT * FROM settings;
SELECT * FROM obs;