# 申し送り（タブB向け）: 動画タブ 視聴リンク+FB 記入モード

GASに認証付きモードを追加・**deploy @56 で新版live確認済み**（実挙動テスト・復元まで実施、本番汚染なし）。
規律は LINE漏洩対応と同一：**認証付きmode・対象タブはallowlist固定（動画2タブのみ）・書込は会社名で行を突合**。

WEBAPP = `SHEET_WEBAPP_URL`（/exec）、`token` = `SHEET_API_TOKEN`（`~/oscar-ai/tokyari-pipeline/.env`）。

---

## モード1: `videotabset` — 視聴リンク+FB を upsert（メイン）

会社名で行を突合し、**視聴リンク=公開URL(col4)** と **FB=FB1(col6)** を記入。既存行はupdate、無ければ `append=1` で追加。

### パラメータ
| param | 必須 | 説明 |
|---|---|---|
| `mode` | ✔ | `videotabset` |
| `token` | ✔ | SHEET_API_TOKEN（未認証は `{error:"unauthorized"}`） |
| `sheet` | ✔ | `企業紹介動画` または `決算書分析動画`（他タブは拒否） |
| `company` | ✔ | 会社名（マスターDB表記で突合。`_findRowByCompany`） |
| `url` | 任意 | 視聴リンク。**paramを付ければ書込／空文字=クリア／省略=そのセル不変** |
| `fb` | 任意 | FBテキスト。urlと同じ挙動（部分更新・再記入OK） |
| `round` | 任意 | FBの記入ラウンド（既定1→FB1=col6。round2→FB2=col10…） |
| `url_col`/`fb_col` | 任意 | 列を明示上書き（既定 url=4, fb=fbCol(round)）。**通常は不要**（実ヘッダ確認済み） |
| `status` | 任意 | ステータス列(col3)も更新する場合 |
| `append` | 任意 | `1`＝会社行が無いとき新規追加（業界は`industry`、書式は`sample`行から継承） |
| `industry`/`sample` | 任意 | append時の業界名／書式継承元の見本行(既定3) |

### 呼び出し例（curl / POST推奨・日本語はurl-encode）
```bash
curl -sL "$WU?mode=videotabset&token=$ST" \
  --data-urlencode "sheet=企業紹介動画" \
  --data-urlencode "company=三菱商事" \
  --data-urlencode "url=https://youtu.be/xxxxx" \
  --data-urlencode "fb=導入部の尺やや長い。冒頭10秒で結論を"
# → {"ok":true,"sheet":"企業紹介動画","company":"三菱商事","row":3,"appended":false,"written":{"url_col":4,"fb_col":6}}
```
FBだけ後から更新（視聴リンクは触らない）:
```bash
curl -sL "$WU?mode=videotabset&token=$ST" --data-urlencode "sheet=決算書分析動画" \
  --data-urlencode "company=トヨタ自動車" --data-urlencode "fb=数字の出典テロップを追加"
```

## モード2: `sheethead` — タブのヘッダ実読（診断）
列様式を確認したいとき。`?mode=sheethead&token=$ST&sheet=企業紹介動画` → `header_rows`(1-2行目)+`sample_row`(3行目)を返す。

---

## 実ヘッダ（両動画タブ共通・確認済み / 400行・45列）
- **col1=業界, col2=会社名, col3=ステータス, col4=公開URL(=視聴リンク)**, col5=担当1, **col6=FB1**, col7=状態1, col8=反映1 …（round毎に4列）… col45=更新
- H1はマージ見出し（対象/🟦進捗(Claude)/🟩公開URL(オスカー)/修正ラウンド/🟦更新）、**H2が実列名**。
- したがって既定（url→col4, fb→col6）でそのまま合致。`url_col`/`fb_col` の上書きは不要。

## 注意
- 対象タブは **企業紹介動画 / 決算書分析動画 のみ**（10コマ/ルーム等は拒否）。
- 会社名はマスターDB表記で突合（表記揺れは `setcompanyname` で是正可）。
- `onEdit` の状態連動はFB列書込では発火しない（状態列を変えないため）。ステータスを動かすなら `status` param か別mode。
