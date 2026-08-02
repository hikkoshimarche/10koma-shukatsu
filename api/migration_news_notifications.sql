-- news_notifications: お気に入り企業ニュースのLINE通知台帳(誰に・どのニュースURLを通知済みか)
-- 目的: 週次通知の重複送信を根絶する冪等キー。timestamp watermark だと部分失敗ユーザーを取りこぼす/
--       後からブックマークした人へ過去分を送ってしまうため、per(user,url)で「通知済み」を記録する。
-- 書き込みは tools/notify_company_news.py が LINE API code==200 を実測できた時のみ(空応答=成功にしない)。
CREATE TABLE IF NOT EXISTS news_notifications (
  line_user_id TEXT NOT NULL,
  company_id   TEXT NOT NULL,
  url          TEXT NOT NULL,
  notified_at  TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (line_user_id, url)   -- 同一ユーザー×同一ニュースURLは一度きり
);
CREATE INDEX IF NOT EXISTS idx_news_notif_user ON news_notifications(line_user_id);
