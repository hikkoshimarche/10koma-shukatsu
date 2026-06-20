# 10koma-shukatsu / トーキャリ 開発ガイド

このリポジトリ（Cloudflare Pages + Workers + D1 = `10koma-shukatsu-db`）と、台本ソース（`~/oscar-ai/tokyari-pipeline/output/<slug>/scenario_v4.json`）を扱う際の恒久ルール。

## 【必須】台本のNotion保存（Definition of Done）
台本を新規作成・変更・本番デプロイしたら、その作業は「Notionファクトシートへの台本同期」まで終えて初めて"完了"とする。ローカル(scenario_v4.json / D1)だけで終えない。未同期で作業を閉じない。
- 同期は非破壊の notion_sync.py を使う：既存版は削除せず見出しを「⚠️旧版(...)」にrename、新版を「## 自動生成版 <日付> <版>（最新の正）✅」として末尾に追記。
- ID限定：登録済み page_id のみ更新。pages.create は禁止（新規ページを作らない）。slugにpage_idが無ければ skip＋報告。
- 別社上書き防止：書き込み前にタイトルが「🌐 {社名} ファクトシート」であることを fetch で確認。不一致なら skip＋報告。
- SYNC_DATE は実際の作業日・版（例: 2026-06-20 v4.1）に更新する。
- 本番デプロイ手順の最後に必ず「scenario_v4.json同期 ＋ Notion台本同期」を含める。どちらか欠けたら未完了。
