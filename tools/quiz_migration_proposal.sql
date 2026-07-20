-- =====================================================================
-- クイズ D1 スキーマ提案（★まだ適用しない）
-- 適用手順: クイズ全社データ確定後に「backup → migration → canary」で一括。
--   1. npx wrangler d1 execute 10koma-shukatsu-db --remote --config api/wrangler.toml \
--        --json --command "SELECT ..." > .backups/pre_quiz_YYYYMMDD.json   (バックアップ)
--   2. このファイルを --file で適用（下記CREATE）
--   3. 1社だけ投入して /quiz.html?company=<slug> で canary 確認 → 全社投入
-- データ源: ~/oscar-ai/tokyari-pipeline/output/<slug>/quiz_30q.json（会社別）,
--           output/industry__<hash>/quiz_30q.json（業界別）
-- 各設問: {category,q_text,options[4],correct(0-3),explanation,source_url,as_of}
-- =====================================================================

CREATE TABLE IF NOT EXISTS quiz_questions (
  id           TEXT PRIMARY KEY,      -- 例: sap-japan_01
  set_type     TEXT NOT NULL,         -- 'company' | 'industry'
  set_id       TEXT NOT NULL,         -- company_id または 業界識別子
  category     TEXT,                  -- 例: 会社概要 / 財務数値 / 沿革
  q_text       TEXT NOT NULL,
  options      TEXT NOT NULL,         -- JSON配列(4要素) 例: ["AAA","AA","A","BBB"]
  correct      INTEGER NOT NULL,      -- 0-3
  explanation  TEXT,
  source_url   TEXT,                  -- 出典URL（Source-or-Silence）
  as_of        TEXT,                  -- 例: 2025年3月期
  ord          INTEGER,               -- 表示順
  created_at   TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_quiz_set ON quiz_questions(set_type, set_id, ord);

CREATE TABLE IF NOT EXISTS user_quiz_progress (
  line_user_id TEXT NOT NULL,
  question_id  TEXT NOT NULL,
  set_type     TEXT NOT NULL,
  set_id       TEXT NOT NULL,
  chosen       INTEGER,               -- 0-3（ユーザーの回答）
  is_correct   INTEGER NOT NULL,      -- 0/1
  answered_at  TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (line_user_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_uqp_user_set ON user_quiz_progress(line_user_id, set_type, set_id);

-- =====================================================================
-- 併せて実装が必要な API（api/src/index.ts・quiz.html が既に呼ぶ形）:
--   GET  /api/quiz?set_type=<company|industry>&set_id=<id>
--        → quiz_questions を ord 順で返す（[]配列）
--   POST /api/quiz/answer  {line_user_id, question_id, chosen, is_correct}
--        → user_quiz_progress を upsert（INSERT OR REPLACE）
--   (任意) GET /api/quiz/sets?line_user_id=<id>
--        → 利用可能セット一覧＋進捗（正答率）
-- =====================================================================
