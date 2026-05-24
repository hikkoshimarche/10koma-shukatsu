-- =====================
-- migration_004
-- 1. OBに卒業年度列追加
-- 2. 三菱商事のvideo_urlをクリア（10コマ就活オリジナル動画ができるまで非表示）
-- =====================

-- OBに卒業年度カラム追加
ALTER TABLE obs ADD COLUMN graduation_year INTEGER;

-- 田中 治樹の卒業年度（2025年卒）
UPDATE obs SET graduation_year = 2025 WHERE id = 'tanaka_haruki';

-- 三菱商事のvideo_urlをクリア（10コマ就活オリジナル動画ができるまでCTA非表示）
UPDATE companies SET video_url = NULL WHERE id = 'mitsubishi_corp';

-- 動作確認
SELECT id, name, graduation_year, affiliation, university, line_id FROM obs;
SELECT id, name, video_url FROM companies;