-- companies に youtube_url 列を追加（既に video_url があるが、明示的に YouTube 用を分けて運用）
-- 既に video_url があるので、それを YouTube URL として使う方針に統一する場合は不要。
-- ここでは新規追加はせず、video_url を YouTube URL として扱うルールに統一する。

-- 三菱商事の video_url を実際の三菱商事公式チャンネル動画URLに更新
UPDATE companies
SET video_url = 'https://www.youtube.com/watch?v=lEQfaUC9PNk'
WHERE id = 'mitsubishi_corp';

-- 動作確認用：updated_at がないので created_at だけ確認
SELECT id, name, video_url FROM companies;