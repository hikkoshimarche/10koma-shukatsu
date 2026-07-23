-- クイズ難易度4段階(Lv1入門/Lv2基礎/Lv3応用/Lv4実践)。既存データ無変更の非破壊migration。
-- ★本番D1への適用はパイロット承認後。difficulty未設定(NULL)は当面Lv2相当として扱う。
ALTER TABLE quiz_questions ADD COLUMN difficulty INTEGER;
-- 出題フロー(API仕様案・実装はタブC): set内をdifficulty昇順で提示。Lv毎に正答率80%でnext Lv解放。
--   GET /api/quiz?set_type=&set_id=&level=1..4  (level省略時は解放済み最大まで)
--   進捗: user_quiz_progress を level別集計し、当該levelの正答率>=0.8 で level+1 を解放。
