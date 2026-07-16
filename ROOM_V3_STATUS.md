# 🎭 ルームv3 全社展開 現在地（スリープ保全用）

## 【再開コマンド】(reboot/kill でプロセスが消えていた時だけ実行)
```bash
cd /Users/oscardodds/projects/10koma-shukatsu
# まず生存確認（生きていれば再開不要・スリープからは自動継続する）:
pgrep -f room_phase3_rollout && echo '稼働中=再開不要' || \
  ( nohup caffeinate -dimsu bash tools/room_v3_resume.sh > tools/_room_phase3_resume.log 2>&1 & )
```
- registered-v3スキップで**二重登録なし**・**並列3**・**三井GOLD除外**・**room-lint5ゲート**・**429→並列2自動降格**・20社毎push を維持。
- 完走すると自動で タブ/ダッシュボード更新 + LINE完了通知(重複防止) まで走る。
- 完走監視は `room_v3_watch.sh`(別プロセス)が担当。スリープ中は本体もwatcherも凍結し、復帰で自動再開。

## 現在地（2026-07-17 06:52 時点・実D1）
- **v3登録済: 228/400社**（三井GOLD別枠1・不可侵）
- **残: 170社**（factsheetあり・未v3。本体rolloutが処理中）
- **隔離(room-lint5未通過): 11社**
- 最終処理slug: `nippon-express-hd`
- 本体rollout pid: 49541

### アーキタイプ別 v3登録
- IT・AI・SaaS・ゲーム: 57社
- インフラ・エネルギー: 30社
- 小売・流通: 27社
- 広告・メディア: 26社
- 専門商社: 20社
- コンサル: 19社
- 航空・運輸・物流: 11社
- 医療・ヘルスケア: 9社
- 総合商社: 8社
- メーカー: 7社
- 教育・人材: 5社
- スタートアップ: 4社
- ディープテック・宇宙・AI: 3社
- 銀行・証券・保険: 1社
- 食品・飲料: 1社

### 隔離社（要個別対応・再fanoutで回復し得る）
- cosmos-pharma (小売・流通) — lint error 1→登録ブロック
- matsukiyococokara (小売・流通) — lint error 1→登録ブロック
- ryohin-keikaku (小売・流通) — lint error 1→登録ブロック
- asahi-shimbun (広告・メディア) — lint error 1→登録ブロック
- nikkei (広告・メディア) — lint error 1→登録ブロック
- shueisha (広告・メディア) — lint error 1→登録ブロック
- usj (広告・メディア) — lint error 1→登録ブロック
- fujitsu (IT・AI・SaaS・ゲーム) — lint error 1→登録ブロック
- jri (コンサル) — lint error 1→登録ブロック
- takeda (医療・ヘルスケア) — lint error 1→登録ブロック
- jr-east (航空・運輸・物流) — D1失敗:⚠️  Warning: Unsupported macOS vers

### 単社の再fanout(隔離社の回収など)
```bash
cd /Users/oscardodds/projects/10koma-shukatsu
nohup caffeinate -dimsu python3 -u tools/room_phase3_rollout.py --slugs '<slug1,slug2>' --no-git --no-tabsync --conc 3 > tools/_room_refanout.log 2>&1 &
```

---
## ⚠️ 重大: ライブ描画ギャップ（2026-07-17 実証）— D1登録 ≠ ライブ描画
**「roomtab未デプロイ型」の再発**。実LINE/LIFFルームAPIで実証した結果：

- ライブ室APIは `/api/room/personas/:id`（と /message）で **`personas`テーブル** を読む（rich schema: display_name/role_code/department/position/short_description/image_url/voice_config）。
- v3展開先は **`room_personas`テーブル**（company_slug/role/persona_name/system_prompt/fact_pack_json）。**APIはroom_personasを一切読まない**。room_personas→personas の**同期は存在しない**。
- 実測（本番 10koma-shukatsu-api.oscar-dodds.workers.dev）：
  - `mitsui_corp`: HTTP200 / **6人格**（唯一ライブ描画）。
  - astroscale-hd / sap-japan / k-line / meitetsu（v3登録済）: HTTP200 / **0人格（空）**。
  - 未処理社も同様に空。
- **今この瞬間LINEからルームを開いて「動く室」が出る社数 = 1（三井GOLDのみ）**。v3新版=0 / 旧6人版=0 / 未表示(空)=399。
- v3 staged品質は良好（astroscale-hd: 5人格・氏名3層・全人格AI開示あり・出典付きSoS）だが**ライブ未反映**。

**要対応（次アクション・要オスカー判断）**: room_personas → personas への同期（role→role_code/persona_name→display_name等のスキーマ写像＋不足列 age/department/position/short_description/image_url/voice_config の補完）か、ライブAPIを room_personas 読みに再ポイント。これをやって初めて228社がユーザーに見える。
