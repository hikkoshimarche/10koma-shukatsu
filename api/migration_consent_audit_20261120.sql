-- 同意記録の監査化(2026-11-20・オスカー承認の設計)
-- 1) user_profiles.first_consented_at: 初回同意日時。一度入れたら変えない(API の upsert は COALESCE で既存値を保持)。
--    consented_at は従来どおり「最新の同意日時」。
-- 2) consent_events: 同意イベントの追記専用ログ(UPDATE/DELETE はトリガーで拒否)。
--    event: granted(初回) / regranted(同じ版で再同意・削除後の再登録) / version_changed(別の版へ同意し直し)
--    withdrawn(削除時の撤回記録)は CHECK に枠だけ用意。保持期間とプライバシーポリシー上の扱いを
--    オスカーが確認するまで API からは書かない(実装保留)。
--
-- 【注記】既存12件(2026-11-20 時点)の first_consented_at は、その時点の consented_at で埋めた。
--   本当の初回同意日時は復元できない(従来の upsert が consented_at を毎回上書きしていたため)。
--   同じ注記を consent_events の backfill 行の note にも残す。

ALTER TABLE user_profiles ADD COLUMN first_consented_at TEXT;

UPDATE user_profiles SET first_consented_at = consented_at WHERE first_consented_at IS NULL;

CREATE TABLE IF NOT EXISTS consent_events (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id         TEXT NOT NULL,
  event           TEXT NOT NULL CHECK (event IN ('granted', 'regranted', 'version_changed', 'withdrawn')),
  consent_version TEXT,
  prev_version    TEXT,
  at              TEXT NOT NULL DEFAULT (datetime('now')),
  endpoint        TEXT,
  note            TEXT
);

CREATE INDEX IF NOT EXISTS idx_consent_events_user_at ON consent_events (user_id, at);

CREATE TRIGGER IF NOT EXISTS consent_events_no_update BEFORE UPDATE ON consent_events
BEGIN SELECT RAISE(ABORT, 'consent_events is append-only'); END;

CREATE TRIGGER IF NOT EXISTS consent_events_no_delete BEFORE DELETE ON consent_events
BEGIN SELECT RAISE(ABORT, 'consent_events is append-only'); END;

INSERT INTO consent_events (user_id, event, consent_version, prev_version, at, endpoint, note)
SELECT user_id, 'granted', consent_version, NULL, consented_at, 'migration_20261120',
       'backfill: 2026-11-20 移行時点の consented_at。本当の初回同意日時は復元不可'
FROM user_profiles
WHERE consented_at IS NOT NULL;
