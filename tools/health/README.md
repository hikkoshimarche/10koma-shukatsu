# 夜間ヘルスチェック巡回 (com.tokyari.healthcheck)

本番の全ページ・全APIを毎晩 **3:00** に機械巡回し、朝までに異常リストを作る。**検知と報告のみ・修正はしない**（修正は昼に人が判断）。

## 対象
- 全400社: `company?id=<slug>` ページ + `/api/companies/<slug>`(panels10確認) + 画像10枚(jsDelivr 200確認)
- 業界ハブ: `/gyokai` + 実在16業界の `gyokai?id=<slug>` + `/api/industries/<slug>`(panels)
- 主要ページ: home/hub/gyokai/quiz/mypage/shindan/company-list/compare/datasheet/es_kit/… (20)
- 全APIエンドポイント: health/industries/companies/company-list/videos/recent/quiz/datasheet/es-kit/company-news/company-selection/industry-selection-schedule/compare/mypage/profile

## 検知
404等HTTP異常 / 壊れ画像(画像URL≠200) / 空レスポンス / 応答3秒超 / console error(Chrome headless+CDP・テンプレ+業界+社サンプル・best-effort)。

判定の較正: エンドポイントを **data**(非空必須) / **ok**(200必須・空OK) / **graceful**(5xxのみ異常・4xx/空はデータ未投入の正常応答)に分類。datasheet/es-kit は `?id=`・データ保有社(abeam)でプローブ。業界API は実在16スラグ(ハイフン)のみ。→ 誤検知を出さない。

## 運用
- 1req/秒・checkpoint(`health/_state.json`・`--resume`で再開)・caffeinate(runner)。
- 出力: `health/reports/health_<日時>.md`(+`LATEST.md`)。異常0なら「✅ 全て正常」1行。
- **レポートは public repo に push しない**(内部レポート=commit禁止ルール)。`reports/` と `_state.json` は `.gitignore` 済。CC は本タブでテキスト報告。

## 手動実行 / 管理
```
# 即時フル実行
~/oscar-ai/tokyari-pipeline/.venv/bin/python tools/healthcheck.py
# 動作確認(先頭N社・console無し)
python tools/healthcheck.py --limit-companies 5 --no-console
# launchd
launchctl list | grep tokyari.healthcheck
launchctl unload/load ~/Library/LaunchAgents/com.tokyari.healthcheck.plist
```

## 構成
- `healthcheck.py` — 巡回本体
- `health/run_nightly.sh` — caffeinate 付き runner(launchd が叩く)
- `com.tokyari.healthcheck.plist` — launchd 定義(控え。実体は `~/Library/LaunchAgents/`)
- `health/reports/` — 出力(gitignore)
