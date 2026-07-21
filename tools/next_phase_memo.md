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

## 【恒久ルール】決算データは常に最新期(2026-07-21起票)
- クイズ・データシートの財務は**常に最新の決算期を一次情報で取得**する。IR library indexで年度を確認し、
  PDF本文に「<最新>年3月期」が verbatim 実在することを確認してから採用（別表記/概算/推定は不可＝Source-or-Silence）。
- corpus取得は**最新期優先**（`acquire_corpus_thick` の `_prefer_latest_tanshin`：短信URLのFY変種推定＋IR索引再クロール＋verbatim確認）。
  未公表・取得不能の社のみ旧期を維持し `freshness_hold.csv` に記録（捏造で埋めない）。
- 鮮度lint（`lint_financial_freshness`/`lint_datasheet_freshness`）: 財務as_ofが corpus最新期より古い→error。最新期が取れない社はfireせず現状維持。
- **決算シーズン(毎年5〜6月)に全社定期リフレッシュ**: `QUIZ_LATEST_FY` を当年の「YYYY年3月期」に更新→ `--locked-all`(財務再生成)＋D1 UPDATE。
