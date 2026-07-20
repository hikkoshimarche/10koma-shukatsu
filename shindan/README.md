# shindan — トーキャリ 企業・業界診断（データ層＋ロジック）

就活初心者向けの「あなたに合いそう」参考提案。12問の回答→決定論マッチングで**業界おすすめ上位＋企業おすすめ複数**を、根拠付きで返す。**AI課金は生成時のみ（診断の応答は決定論・即時）**。

> ⚠️ 本ディレクトリは**データ層とロジックまで**。本番D1反映・メニュー追加は未実施（オスカー起床後にWeb Claude検分→UI接続→v2でメニュー「ホーム」→「診断」差し替え）。

## 設計思想（2層属性）
| 層 | 用途 | 出典ポリシー |
|---|---|---|
| **① ソフト属性**（転勤度/海外度/安定性/成長性/リモフレ/若手裁量/文理/職種タグ） | マッチング用の内部シグナル | **推定OK**（`estimated:true`）。業界baseline＋ファクトシート記述をhaikuで微調整。null可。MBTI的なラフさで良い |
| **② 表示ファクト**（平均年収/初任給） | 結果画面に**数字で出す** | **出典必須・verbatim照合**。平均年収は**有報grade**（有報/日経年収DB/決算短信）のみ。第三者推定は不採用＝数字を出さず定性文で薦める（Source-or-Silence） |

結果には必ず根拠を添える：①=傾向表現（例「海外展開に積極的な傾向」）、②=数字＋出典URL（区別して保持）。
**結果画面の免責文**：「この診断は公式公開情報と業界傾向に基づく参考提案です。断定・優劣付けではありません。」

## ファイル
| ファイル | 役割 |
|---|---|
| `schema.json` | 属性定義（①②・値の形 {value, evidence, as_of, confidence, estimated}） |
| `industry_baseline.json` | 18業界のソフト属性prior（全社に即カバレッジを与える土台） |
| `extract.py` | 1社ハーネス。②=ルール＋verbatim、①=baseline＋haiku微調整＋trend_note生成 |
| `run_all.py` | 400社ローリング・20社毎CP(commit/push)・resumable・**LINE不使用**・coverage出力 |
| `attributes/<slug>.json` | 各社の属性（マッチングの入力データ） |
| `questions.json` | 12問（各属性対応・『こだわらない』で判定対象外・根拠付き） |
| `matching.py` | `recommend(answers)` → 業界/企業おすすめ＋根拠。決定論・即応答 |
| `test_matching.py` | 10サンプル回答→妥当性検証＋`test_results.md` |
| `coverage_report.md` | 属性×充足社数＋平均年収を数字表示できない社リスト（run_allが生成） |

## マッチング仕様（`matching.recommend(answers)`）
- 入力 `answers = {question_id: option_index}`（複数選択設問は `{id:[idx,...]}`）。
- 会社ごとに「適用重みで正規化したスコア（0-1）」を算出。
  - **欠損属性は減点しない**：その設問の重みを分母から除外＝判定対象外。欠損の多寡で不利にならない。
  - score系=希望値との近さ、tags=重なり、industry=一致ブースト、bunri=一致/文理両方は部分点。
- 出力：`top_industries`（所属企業スコアの平均で集計）＋`top_companies`（根拠付き）＋`disclaimer`。

### 出力例（企業1件）
```json
{"name":"双日","industry":"総合商社","score":0.47,
 "rationale":{"trend":"ベトナムNo.1進出規模・LNG/航空機など成長領域で海外…",
   "matched":["海外志向に合致","成長志向に合致"],
   "facts":{"avg_salary":{"text":"平均年収 約1,200万円","source":"https://…","as_of":"2024年3月期"}}}}
```

## UI接続の想定（オスカー作業）
1. `questions.json` を診断画面のフォームに描画（12問・単一/複数選択）。
2. 回答を `matching.recommend()` 相当に渡す（実装：このロジックをWorker/関数に移植 or `attributes/` をD1/KVへ）。
3. 結果画面：業界トップ＋企業カード（trend＋②数字は出典リンク付き）＋免責文を表示。
4. v2でメニュー「ホーム」→「診断」に差し替え。

## 再生成・更新
- 1社だけ：`python3 extract.py <slug>`／全社：`python3 run_all.py`（resumable）。
- ファクトシート更新後に該当 `attributes/<slug>.json` を消して `run_all.py` で再生成。
