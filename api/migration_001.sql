-- 信頼性カラム追加（Day 4: コンテンツ信頼性ルール）
ALTER TABLE industries ADD COLUMN source_urls TEXT;
ALTER TABLE industries ADD COLUMN last_verified_at TEXT;
ALTER TABLE industries ADD COLUMN next_verify_due TEXT;
ALTER TABLE industries ADD COLUMN verification_status TEXT DEFAULT 'unverified';
ALTER TABLE industries ADD COLUMN factsheet_url TEXT;

ALTER TABLE companies ADD COLUMN source_urls TEXT;
ALTER TABLE companies ADD COLUMN last_verified_at TEXT;
ALTER TABLE companies ADD COLUMN next_verify_due TEXT;
ALTER TABLE companies ADD COLUMN verification_status TEXT DEFAULT 'unverified';
ALTER TABLE companies ADD COLUMN factsheet_url TEXT;