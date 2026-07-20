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

-- =====================================================================
-- 復習モード API（ルールベース・user_quiz_progress 集計）★フロント(quiz.html 復習タブ)が既に呼ぶ形
--   GET /api/quiz/review?user_id=<line_user_id>&mode=<recent|frequent|weak_category>
--        → quiz_questions[] を最大10問返す（options/correct/explanation/source_url 込み）
--   集計ルール（SQL例・いずれも is_correct=0 の誤答起点、正解済みは除外可）:
--     mode=recent:        直近で間違えた問題を新しい順
--        SELECT q.* FROM user_quiz_progress p JOIN quiz_questions q ON q.id=p.question_id
--        WHERE p.line_user_id=? AND p.is_correct=0 ORDER BY p.answered_at DESC LIMIT 10;
--     mode=frequent:      誤答回数の多い順（同一問題を複数回誤答）
--        SELECT q.*, COUNT(*) ng FROM user_quiz_progress p JOIN quiz_questions q ON q.id=p.question_id
--        WHERE p.line_user_id=? AND p.is_correct=0 GROUP BY p.question_id ORDER BY ng DESC, MAX(p.answered_at) DESC LIMIT 10;
--     mode=weak_category: 苦手カテゴリ(誤答率高)を優先し、その category の未正解問題を出題
--        WITH cat AS (SELECT q.category, AVG(p.is_correct) acc FROM user_quiz_progress p
--                     JOIN quiz_questions q ON q.id=p.question_id WHERE p.line_user_id=? GROUP BY q.category)
--        SELECT q.* FROM quiz_questions q JOIN cat ON cat.category=q.category
--        ORDER BY cat.acc ASC, RANDOM() LIMIT 10;
--   ※ user_quiz_progress は既に chosen/is_correct/answered_at/set_type/set_id を保持（上記CREATE）。
--      集計インデックス idx_uqp_user_set で user 単位の絞り込みは高速。
--      category 別集計を多用するなら CREATE INDEX idx_uqp_user_q ON user_quiz_progress(line_user_id, question_id); を追加検討。
-- =====================================================================

-- =====================================================================
-- 【設計メモ・次フェーズ】AI適応出題（寄り添い型）※回答データ蓄積後
--   ・上記ルールベース復習で回答ログ(user_quiz_progress)が貯まってから着手。
--   ・案: ユーザーの誤答パターン(カテゴリ/難易度/出典種別)をLLMに渡し、
--         「次に出すべき1問」または「弱点を突く新設問」を動的生成/選択（Source-or-Silence厳守）。
--   ・出題だけでなく、解説を個別化（"前回ここで間違えたよね" 等の寄り添い文面）。
--   ・DBは現行スキーマで足りる（question_id/category/is_correct の履歴があれば特徴量化可能）。
--     追加するなら user_quiz_progress に response_ms(回答時間) 等の任意列を後付けINSERT。
-- =====================================================================
