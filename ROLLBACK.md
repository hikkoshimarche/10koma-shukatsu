# ROLLBACK / LAUNCH SAFETY 手順書（8/1 ローンチ用）

> 目的: 障害時に**直前の正常状態へ1コマンドで戻す**／ローンチ前バックアップ／Phase C キルスイッチ。
> ※このファイルは公開リポジトリに置くため、鍵・トークン・アカウントID・PII・費用/人員情報は一切書かない。

## 0. 現在の正常版（LAUNCH BASELINE）
- **正常 commit hash: `8a45b99e`**（main・2026-07-27。会社サマリーカード/LP改行根治/OGP/計測/LIFF UX修正まで反映済の安定版）
- ロールバック先候補（さらに手前）: `e26a06a7`（OGP前）/ `226b5dbd`（LIFF UX後・計測前）
- デプロイ機構: main への push で **API Worker（GitHub Actions: deploy-api.yml）** と **Cloudflare Pages（Git連携・public/）** が自動反映。

---

## 1. ロールバック（LP / LIFF アプリ）

### A. コード（最優先・確実）: 直前の正常commitへ戻して push
```bash
cd ~/projects/10koma-shukatsu
git checkout main && git pull
git revert --no-edit <戻したいcommit>..HEAD    # 例: 直近1件なら git revert --no-edit HEAD
git push origin main                            # → Pages と API が自動で正常版へ再デプロイ
```
不可逆に一気に戻す場合（履歴を巻き戻す・慎重に）:
```bash
git reset --hard 8a45b99e && git push --force-with-lease origin main
```

### B. デプロイ単位で即時ロールバック（コードは触らず、配信だけ戻す）
- **Cloudflare Pages**: ダッシュボード → Workers & Pages → `10koma-shukatsu` → Deployments → 直前の正常デプロイの「⋯」→ **Rollback to this deployment**（数秒で切替・最速）。
- **API Worker**: `cd api && npx wrangler rollback`（直前バージョンへ）。または該当commitを checkout して `npx wrangler deploy`。

### C. ドメイン系（talkcareer.jp）が不調のとき
- 直近の事例＝`functions/_middleware.js` がリライトループを誘発。**該当があれば削除して push**（現在は無し）。
- ゾーンの Redirect Rule（`/`→`/lp/`）は Cloudflare ダッシュボード → talkcareer.jp → Rules で ON/OFF 可能。

---

## 2. ローンチ前バックアップ（8/1 開始前に取得）

### D1（本番DB `10koma-shukatsu-db`）
```bash
cd ~/projects/10koma-shukatsu/api
mkdir -p ~/Desktop/tokyari_backup_$(date +%Y%m%d)
npx wrangler d1 export 10koma-shukatsu-db --remote \
  --output ~/Desktop/tokyari_backup_$(date +%Y%m%d)/d1_full.sql          # スキーマ+データ全体
npx wrangler d1 export 10koma-shukatsu-db --remote --no-data \
  --output ~/Desktop/tokyari_backup_$(date +%Y%m%d)/d1_schema.sql        # スキーマのみ(復元検証用)
```
復元（緊急時）: 新DBを作り `npx wrangler d1 execute <db> --remote --file d1_full.sql`（本番へ直接流す場合は要人手確認）。

### 画像
- 10コマ/ブランド画像は **`public/images/` に git 管理**＝**gitがバックアップ**（`8a45b99e` に固定）。個別退避が要るなら:
```bash
cp -R ~/projects/10koma-shukatsu/public/images ~/Desktop/tokyari_backup_$(date +%Y%m%d)/images
```
- TTSキャッシュ等の R2 バケットは配信の一時物のため対象外（消えても再生成可）。

### スプレッドシート（ユーザープロフィール同期先 等）
- Google スプレッドシートは **ファイル → コピーを作成**、または **ファイル → 変更履歴 → 版を作成**（日付名）で当日版を固定。日次同期は全件洗い替え=冪等なので、コピー1部で十分。

---

## 3. Phase C 自走ループ（`com.tokyari.phasec`）— ローンチ当日の扱い

### 何をするジョブか / 当日走ると何が変わるか
- Mac の launchd 毎時ジョブ。画像フィードバックの自動修正ループ（GAS/clasp・画像はMac依存）。**本番 `company_panels` の画像URL更新や commit/push を伴いうる**。
- つまり **ローンチ当日に走ると、意図しないタイミングで本番の画像/データが変わる**可能性がある（レビュー中の状態が上書きされうる）。

### 推奨
- **ローンチ当日は停止して状態を凍結**（安定版 `8a45b99e` を固定表示させる）。落ち着いてから再開。

### キルスイッチ / 再開
```bash
# 停止（当日の凍結）
launchctl bootout gui/$(id -u)/com.tokyari.phasec
# 稼働状態の確認（一覧に出なければ停止済）
launchctl list | grep com.tokyari.phasec
# 再開（ローンチ後）
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.tokyari.phasec.plist
```
- 同様に一時停止しておくと安全な自走系（当日）: `com.tokyari.companynews` / `com.tokyari.selection-refresh` / `com.tokyari.quarterly-refresh`（いずれも本番データを書き換えうる）。
- 継続で問題ない: `com.tokyari.healthcheck`（検知のみ・無変更）/ `com.tokyari.userprofilesync`・`com.tokyari.sheetsync`（読み取り/スプシ書き込みのみ・本番配信に無影響）。

---

## 4. 障害時の切り分け早見表
| 症状 | まず見る | 対処 |
|---|---|---|
| LP/アプリが壊れた（直近pushの後） | 直近commit | §1-A で revert→push、急ぐなら §1-B Pages Rollback |
| API(/api/*)が5xx | `npx wrangler tail`（api/） | §1-B `wrangler rollback` |
| talkcareer.jp が表示不能/ループ | `functions/` の有無・Redirect Rule | §1-C |
| データがおかしい | §2 のバックアップ | D1復元（要人手確認） |
| 勝手に本番が変わる | §3 の自走ジョブ | §3 キルスイッチで停止 |
