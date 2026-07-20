# リッチメニュー v1 登録手順（トーキャリ）

## ✅ 実行済み（①作成・②画像アップまで完了 / ③未実行）
- **richmenu_id = `richmenu-56ee5a0a6f890ba332391012930c7e7e`**（name: tokyari-v1 / 2500×1686 / areas 6）
- 画像アップロード: HTTP 200 済 ／ `GET /richmenu/list` に登録確認済（既存0件→並存OK）
- **残るは③デフォルト適用のみ**（下記1コマンド）。

## 🚀 ③ 公開＝合図後にこの1コマンド（自動でトークン発行→全ユーザーに適用）
```bash
cd ~/projects/10koma-shukatsu && CID=$(grep '^LINE_MESSAGING_CHANNEL_ID=' .env|cut -d= -f2) && CSEC=$(grep '^LINE_MESSAGING_CHANNEL_SECRET=' .env|cut -d= -f2) && TOKEN=$(curl -s -X POST https://api.line.me/v2/oauth/accessToken -d grant_type=client_credentials -d client_id=$CID -d client_secret=$CSEC | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])') && curl -sS -X POST https://api.line.me/v2/bot/user/all/richmenu/richmenu-56ee5a0a6f890ba332391012930c7e7e -H "Authorization: Bearer $TOKEN" -w '\nHTTP %{http_code}\n'
```
（動作確認済＝トークン発行部分はテスト済。HTTP 200 で公開成功。）
（.env のチャネルID/シークレットから短命トークンを都度発行＝メモにシークレットを書かない。HTTP 200 で公開成功。ロールバック＝別メニューidで同コマンド、または `DELETE /v2/bot/user/all/richmenu` で既定解除。）

## ⚠️ 切替タイミング
**まだ切替えない。** クイズの D1 投入（quiz_questions）＋業界10コマ適用の完了 → オスカーの合図後に上記③を実行。
＝メニュー公開の瞬間から全6セルが実データで動く状態にするため。
（①②は実行済み。最後の「③デフォルト適用」だけ合図待ち。）

## 使うファイル（このフォルダ内）
- **richmenu_v1.jpg**（2500×1686 / 401KB）… ★アップロードはこちら（LINE上限1MB以内）
- richmenu_v1.png（2500×1686 / 2.19MB）… 参照用（**1MB超のためLINEには使わない**）
- richmenu_v1_areas.json … タップ領域＋各セルのURI（下表と一致）

## タップ領域＋遷移先（確定routing表と一致・2×3グリッド）
| 位置 | セル | URI |
|---|---|---|
| 左上 | 企業研究 | https://liff.line.me/2010075487-89AJxZnA/industry |
| 中上 | 業界研究 | https://liff.line.me/2010075487-89AJxZnA/gyokai |
| 右上 | 理解度クイズ | https://liff.line.me/2010075487-89AJxZnA/quiz.html |
| 左下 | お気に入り | https://liff.line.me/2010075487-89AJxZnA/bookmarks.html |
| 中下 | 使い方 | https://liff.line.me/2010075487-89AJxZnA/howto.html |
| 右下 | ホーム | https://liff.line.me/2010075487-89AJxZnA/home.html |

> 前提：LIFF `2010075487-89AJxZnA` のエンドポイントURLが `https://10koma-shukatsu.pages.dev/`（ルート）であること。これでパス付きURL（/industry 等）が各ページに解決される。

---

## 方法A：LINE Official Account Manager（GUI・かんたん）
1. https://manager.line.biz/ → 対象アカウント → 「トークルーム管理 > リッチメニュー」→「作成」
2. 表示設定：タイトル `tokyari-v1`／メニューバーのテキスト `メニュー`／表示期間（任意）
3. テンプレート：**大（6分割＝2行×3列）** を選択
4. 背景画像：**richmenu_v1.jpg** をアップロード
5. 各エリアにアクション設定＝タイプ「**リンク**」、URLを上表どおり（A左上→企業研究 … F右下→ホーム）
6. 保存
7. **（合図後）** 一覧で本メニューを「**デフォルト表示**」に設定＝全ユーザー公開

## 方法B：Messaging API（curl・boundsを精密指定）
`$TOKEN` = Messaging APIチャネルアクセストークン（長期）。
```bash
# 1) リッチメニュー作成（areas JSON）→ richMenuId が返る
curl -v -X POST https://api.line.me/v2/bot/richmenu \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @richmenu_v1_areas.json
# → {"richMenuId":"richmenu-xxxxxxxx"}

# 2) 画像アップロード（JPEG）
curl -v -X POST https://api-data.line.me/v2/bot/richmenu/<richMenuId>/content \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: image/jpeg" \
  --data-binary @richmenu_v1.jpg

# 3) 【合図後】全ユーザーのデフォルトに設定＝公開の瞬間
curl -v -X POST https://api.line.me/v2/bot/user/all/richmenu/<richMenuId> \
  -H "Authorization: Bearer $TOKEN"
```
- 差し替え（v2で「ホーム」→「診断」）時：新richMenuを作成→画像/areas設定→手順3で付け替え。旧は削除（DELETE /v2/bot/richmenu/<id>）。

## ロールバック
デフォルトを旧メニューに戻す：手順3を旧 richMenuId で実行、またはGUIで旧メニューをデフォルトに再設定。
