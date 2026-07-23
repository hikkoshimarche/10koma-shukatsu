-- company_news: お気に入り社の公式新着(見出し+日付+URLの中継のみ・本文/要約なし)
CREATE TABLE IF NOT EXISTS company_news (
  company_id   TEXT NOT NULL,
  title        TEXT NOT NULL,
  url          TEXT NOT NULL,
  published_at TEXT,
  fetched_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (company_id, url)   -- URL重複排除
);
-- 巡回: tokyari-pipeline/scripts/crawl_company_news.py (bookmarks有社のみ・週次launchd com.tokyari.companynews 月曜7:30)
