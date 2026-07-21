# リッチメニュー v2 登録・切替メモ

6セル（2×3）。診断・お守り追加版。**v1と並存で登録済み。デフォルト切替はまだ実行しない**
（＝相性診断・お守りが両方ライブになってから、オスカーの合図で下記1コマンドを実行）。

## 登録済みの実体
- **v2 richMenuId**: `richmenu-6ac18393ce9583a78cc48c8d88715b2a`（name: tokyari-v2）
- v1 richMenuId（現デフォルト・据置）: `richmenu-56ee5a0a6f890ba332391012930c7e7e`（name: tokyari-v1）
- 画像: `assets/richmenu_v2.jpg`（2500×1686 / JPEG q92 / 約496KB）
- タップ領域: `assets/richmenu_v2_areas.json`

## routing表 v2（2×3グリッド）
| セル | 位置 | ラベル | 遷移先URI |
|---|---|---|---|
| 1 | 左上 | 企業研究 | `https://liff.line.me/2010075487-89AJxZnA/industry` |
| 2 | 中上 | 業界研究 | `https://liff.line.me/2010075487-89AJxZnA/gyokai` |
| 3 | 右上 | 相性診断 | `https://liff.line.me/2010075487-89AJxZnA/shindan.html` |
| 4 | 左下 | お気に入り | `https://liff.line.me/2010075487-89AJxZnA/bookmarks.html` |
| 5 | 中下 | 使い方 | `https://liff.line.me/2010075487-89AJxZnA/howto.html` |
| 6 | 右下 | お守り | `https://liff.line.me/2010075487-89AJxZnA/omamori.html` |

※ v1にあった「理解度クイズ」「ホーム」はv2で外した。クイズ＝各ページ内導線＋ホームカードから到達／ホーム＝ロゴタップ→home.htmlで到達。

## 【③ 切替コマンド（オスカー合図後に1回だけ実行）】
トークンは client_credentials で都度発行（既存トークンを無効化しない）。`.env` の
`LINE_MESSAGING_CHANNEL_ID` / `LINE_MESSAGING_CHANNEL_SECRET` を使用。

```bash
set -a; source ~/projects/10koma-shukatsu/.env; set +a
TOK=$(curl -s -X POST https://api.line.me/v2/oauth/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d grant_type=client_credentials \
  -d client_id="$LINE_MESSAGING_CHANNEL_ID" \
  -d client_secret="$LINE_MESSAGING_CHANNEL_SECRET" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# ★これが切替の本体（全ユーザーのデフォルトをv2へ）
curl -s -X POST "https://api.line.me/v2/bot/user/all/richmenu/richmenu-6ac18393ce9583a78cc48c8d88715b2a" \
  -H "Authorization: Bearer $TOK" -w "\nHTTP %{http_code}\n"

# 確認（v2のIDが返ればOK）
curl -s https://api.line.me/v2/bot/user/all/richmenu -H "Authorization: Bearer $TOK"; echo
```

## ロールバック（v1へ戻す）
```bash
curl -s -X POST "https://api.line.me/v2/bot/user/all/richmenu/richmenu-56ee5a0a6f890ba332391012930c7e7e" \
  -H "Authorization: Bearer $TOK" -w "\nHTTP %{http_code}\n"
```

## 実施ログ（今回）
- ① 作成: POST /v2/bot/richmenu → `richmenu-6ac18393ce9583a78cc48c8d88715b2a`
- ② 画像アップ: POST /v2/bot/richmenu/{id}/content (image/jpeg) → HTTP 200
- ③ デフォルト適用: **未実行**（現デフォルトは v1 のまま。合図待ち）
