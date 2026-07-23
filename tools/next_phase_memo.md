# 次フェーズ 設計メモ（実装はまだ）

## 1. 企業ページ「公式採用ページへ」リンク
- **狙い**: 募集情報ニーズに、鮮度管理ゼロで応える（自社で求人を持たず、公式採用ページへ送客）。
- **データ源（新規収集不要・流用）**: 各社の**ファクトシート / クイズcorpus**に既に含まれる**公式採用URL**を流用。
  - quiz_fanout の source_url / manifest（`output/<slug>/_quiz_source_manifest.json` 等）や factsheet の公式URL群から「採用/careers/recruit」を含むURLを抽出 → `companies.recruit_url`(新列) or 別表へ。
  - ★収集はデータ側（タブD/該当pipeline）。フロント(company.html)は列があれば「公式採用ページへ ↗」ボタンを出すだけ（liff.openWindow external）。無ければ非表示（空ボタン禁止）。
- **鮮度**: 公式ページへ送るだけなので募集内容の更新はトーキャリ側で不要。URLの生死だけ時々チェック。
- **実装メモ**: company.html 企業モードの CTA 群（動画/クイズ）の並びに追加。industry モードには出さない。

## 2. お役立ち情報・書籍 → ホーム⑥「お知らせ枠」
- home.html の `#notice`（現在は中身が無いので**非表示**）に、**編集コンテンツ**として後日掲載。
  - 例: 就活お役立ち記事、おすすめ書籍（アフィリエイト可）、季節の告知。
- **データ源**: D1に軽量な `notices`(id,title,body,url,starts_at,ends_at,ord) を作るか、静的JSON(`public/notices.json`)を編集運用。中身ゼロなら枠自体を出さない（空セル禁止の原則を維持）。
- 実装時: home.html main() で notices を取得 → 0件なら `#notice` 非表示のまま。

## 3. AI適応出題（寄り添い型）※quiz_migration_proposal.sql にも記載
- ルールベース復習(実装済)で `user_quiz_progress` が貯まってから。誤答パターンをLLMで特徴量化し次の1問を動的選択/生成（Source-or-Silence厳守）＋個別化解説。

## 【恒久ルール】お守り名言の追記はSource-or-Silence（2026-07-21起票）
- `public/omamori_quotes.json` の名言は**確定8件**（イチロー/ジョーダン/松下/稲盛/ジョブズ/ヘレンケラー/マザーテレサ/清沢哲夫）。
- 一次資料未特定のため**不採用**：本田宗一郎「99%の失敗…」・王貞治「努力は必ず報われる…」（言葉は流通するが本人の著書/会見録の該当箇所を特定できず）。
- **追記は一次資料（本人の著書/会見録/公式スピーチの該当箇所）で裏取りできたもののみ**。ネット拡散系・出典不明・パラフレーズ（例: エジソン「1万通り」＝原文 several thousand things that won't work）は入れない。誤帰属注意（例: マンデラ「倒れるたび起き上がる」＝Goldsmith由来）。
- 配信比率はオリジナル7:名言3（`omamori.html` の `QUOTE_RATIO=0.3`・オリジナル/名言を別プールで抽選・各プール重複なし→再シャッフル）。名言を増やしても比率は自動維持。

## 【恒久ルール】決算データは常に最新期(2026-07-21起票)
- クイズ・データシートの財務は**常に最新の決算期を一次情報で取得**する。IR library indexで年度を確認し、
  PDF本文に「<最新>年3月期」が verbatim 実在することを確認してから採用（別表記/概算/推定は不可＝Source-or-Silence）。
- corpus取得は**最新期優先**（`acquire_corpus_thick` の `_prefer_latest_tanshin`：短信URLのFY変種推定＋IR索引再クロール＋verbatim確認）。
  未公表・取得不能の社のみ旧期を維持し `freshness_hold.csv` に記録（捏造で埋めない）。
- 鮮度lint（`lint_financial_freshness`/`lint_datasheet_freshness`）: 財務as_ofが corpus最新期より古い→error。最新期が取れない社はfireせず現状維持。
- **決算シーズン(毎年5〜6月)に全社定期リフレッシュ**: `QUIZ_LATEST_FY` を当年の「YYYY年3月期」に更新→ `--locked-all`(財務再生成)＋D1 UPDATE。

## [キュー] education-hr 業界セット (2026-07-21起票)
- 保留承認済み。構成社(パーソル/パソナ/ベネッセ/学研/ナガセ東進 等)が全て needs_source=corpus未取得。
- TODO: 各社IR公式URL(有報/短信/会社概要)を手動シード → acquire_corpus_thick で corpus 取得 → gen_gyokai_sets.py の MAP に education-hr を追加(members=取得できた上場社) → 生成 → D1投入(industry__education-hr)。
- リクルートHDは corpus 済だが it-ai-saas-game に分類。単独では枠にならない。

## [キュー] deeptech-space-ai 宇宙追補 (2026-07-21起票)
- 現状 AI開発5社(pref-networks/sakana-ai/pksha/elyza/brainpad)のみで生成。
- ispace: 公式library(ispace-inc.com)は広報PDFのみ・決算短信リンク無し。自動取得は第三者サイト(kitaishihon.com)を掴む=無効。
- astroscale(186A): 公式IR(astroscale.com/ja/ir/)に xj-storage.jp(TDnet)開示PDF有るが、取得できたのは通知/議決権行使書で「年3月期」決算短信の形でない(3月決算か要確認)。
- TODO: 両社の正しい決算短信PDF(TDnet/xj-storage)を手動シード → corpus取得 → deeptech-space-ai の members に追加して再生成(AI+宇宙の完全枠)。

## [キュー] build_datasheet の根本修正(再汚染防止) 2026-07-22
- 汚染の出所は build_datasheet が corpus からdatasheetを作る際、クイズ的な否定事実/distractorを事実化していたこと(例「主催する賞:ノーベル賞」「小田急の事業:製造業」)。
- clean_datasheets.py で既存266を浄化済み(130社226fact除去・D1反映済)だが、**build_datasheet自体は未修正**=run_freshnessや新規生成で再汚染し得る。
- TODO: build_datasheet(quiz_fanout.py)に _NEG_SHAPE除外 + 答えのcorpus実在チェック(clean_datasheetsの_answer_ok)を配線。以後の生成でクイズdistractorを事実化しない。
- 参考: 決定論cleaner=答えのcorpus桁列/特徴語一致で捏造のみdrop・正当な数値/散文は温存。

## [キュー] ES kit メタ記述フィルタ(次回バッチ) 2026-07-22
- 軽微改善: 「〜を公開/紹介/伝えています」型=サイト自体についての記述(会社の事実でない)を材料から除外。
  CA(サイバーエージェント)で2件検出。gen_es_kit.load_prose_facts / enrich_datasheet の生成に _META_DESC 除外を追加。
- 例パターン: (公開|紹介|掲載|伝え|発信|お知らせ)(して|する)?(います|いる|中)。「当サイトでは」「ページでは」等。
- 保留9社(takeda等=非公式corpus)は es_thin 管理・公式corpus取得後に追補。

## [キュー] (c) ファクトシートに製品単位の一次情報URLを記録 (2026-07-23)
- 難易度v2.2で#4=(b)headlessクロールを採用したが、根本解決は factsheet生成側で製品ごとに一次情報URLを記録すること。
- Web Claude側でキュー管理。四半期鮮度リフレッシュの監視URLレジストリ(quiz-live-and-freshness)と統合設計予定。
