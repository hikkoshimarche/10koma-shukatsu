# リッチメニュー v3 登録メモ（お気に入り→マイページ 差し替え版）

**登録・デフォルト適用まで実施済み（2026-07-23）**。v2は削除せず温存（ロールバック用）。

## 実体
- **v3 richMenuId**: `richmenu-983e09164f894845ddb63f7ef953f52b`（name: tokyari-v3）＝**現在のデフォルト**
- v2（旧デフォルト・温存）: `richmenu-6ac18393ce9583a78cc48c8d88715b2a`
- v1（温存）: `richmenu-56ee5a0a6f890ba332391012930c7e7e`
- 画像: `assets/richmenu_v3.jpg`（2500×1686 / JPEG q92 / 約417KB）／タップ領域: `assets/richmenu_v3_areas.json`

## routing（2×3・座標はv2と完全同一。左下のみ変更）
| 位置 | ラベル | 遷移先 |
|---|---|---|
| 左上 | 企業研究 | /industry |
| 中上 | 業界研究 | /gyokai |
| 右上 | 相性診断 | /shindan.html |
| **左下** | **マイページ** | **/mypage.html**（v2はお気に入り→bookmarks.html。v3で直リンク化） |
| 中下 | 使い方 | /howto.html |
| 右下 | お守り | /omamori.html |

## ロールバック（v2へ戻す1コマンド）
```bash
set -a; source ~/projects/10koma-shukatsu/.env; set +a
TOK=$(curl -s -X POST https://api.line.me/v2/oauth/accessToken -H "Content-Type: application/x-www-form-urlencoded" -d grant_type=client_credentials -d client_id="$LINE_MESSAGING_CHANNEL_ID" -d client_secret="$LINE_MESSAGING_CHANNEL_SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X POST "https://api.line.me/v2/bot/user/all/richmenu/richmenu-6ac18393ce9583a78cc48c8d88715b2a" -H "Authorization: Bearer $TOK" -w "\nHTTP %{http_code}\n"
```
※ v1・v2・孤立ページ(bookmarks転送/company-list/hub/obs/videos)の削除は後日一括判断。
