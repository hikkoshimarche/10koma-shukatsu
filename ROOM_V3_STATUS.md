# 🎭 ルームv3 全社展開 現在地（スリープ保全用）

> ## 📌 最新チェックポイント (2026-07-17 PC閉じる前・更新)
> - ①**今ライブの室**: 356社(実描画=personas在籍・room_liff_idでLINEから開ける)。
> - ②**rollout**: 322登録/343済/364。自走継続中。
> - ③**②フルGOアバター/音声**: 未起動(0社/0枚・コスト実測なし)。
> - ④**再開コマンド**(reboot/kill時のみ): 下記【再開コマンド】。②未起動のため再開不要。
> - **sleep挙動**: rollout/watcher/caffeinateは蓋閉じで凍結→開くと自動継続。手動再開はreboot/kill時のみ。


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

---
## ✅ ライブ化パイロット: astroscale-hd (2026-07-17) — room_personas→personas 同期
**方式**: per-slug写像同期(1社パイロット)。三井GOLD不可侵(hash無変化で証明)。rolloutは並行staging継続。
- 実ライブAPI `/api/room/personas/astroscale-hd`: **HTTP200 / 5人格描画**(氏名3層・position=v3ラベル・desc=v3 gist)。chat用system_prompt 5本(3251〜3363字・全AI開示あり・SoS/人格差入り)も投入済=会話も動く。
- 三井GOLD(mitsui_corp 6行): **hash `fdda70df…` 反映前後で完全一致=無変化**。persona_id空間が別(`astroscale-hd_rN` vs `mitsui_rN_xxx`)で衝突不能。
- 冪等: 再実行しても5行のまま(INSERT OR REPLACE・重複なし)。
- **写像で埋めた列**: persona_id/company_id/role_code/display_name/position/short_description/system_prompt/is_active。
- **NULL(欠損)列と実害**:
  - `image_url`(アバター): room.htmlは`onerror`で非表示化=**破損アイコンは出ないが写真なしの空カード**。GOLD並みには 228社×N枚のアバター生成が要る。
  - `age`(年齢): カード名行が`${p.age}歳`→**「null歳」と表示される既知バグ**(要データ or フロント側`p.age?…:''`ガード)。
  - `voice_config`(音声): chat.htmlのTTS▶ボタンは出るが押すと失敗(読み上げ不可)。要 voice割当 or ボタン非表示。
  - `department`/`kana`: 空表示(graceful・実害小)。
- **判定材料**: テキストの室(人格選択+会話・品質良好)は**今すぐ228社で動く**。ただしGOLD並み(アバター/音声/年齢/部署)には追加対応が要る。最小で出すなら フロント3点(null歳ガード/アバター既定/voice無しはTTS非表示)で足りる。
- **ゲート停止**: 228社一括同期は未実施(オスカー+Web Claude判断待ち)。

---
## ✅ 最小GO: ルームv3ライブ化 完了(2026-07-17) — 動く室 1→260社
D1登録≠ライブ描画の全チェーンを結線。**今LINEで開ける室 = 260社(v3 259 + 三井GOLD 1)**。
- **フロント配線**(room.html/chat.html/hub.html・pages deploy済 9e50195): mitsui_corpハードコード→?company=slugパラメータ化(三井は写像でGOLD保持)。3修正=null歳非表示/既定SVGアバター/voice無TTS非表示。
- **personas同期**: 259社(role→role_code等の写像・冪等・孤児DELETE)。三井GOLD hash無変化。
- **room_liff_id**: companies.json 260社付与(共用LIFF `2010075487-d4TJ2xZc`)=hub室ボタン表示。pages deploy済。
- **自動化**: watcher periodic --new-only(API即ライブ)+ 完了フック --all --set-liff + companies.json commit/push(pages自動deploy)=最終400社まで取りこぼしなし。
- **ライブ対象外(要フルGO前是正)**:
  - 隔離12社(room-lint5未通過): fujitsu/takeda/nikkei/shueisha/usj/jri/odakyu/ryohin-keikaku/cosmos-pharma/matsukiyococokara/asahi-shimbun 等。
  - フルネーム重複2社: daiichi-sankyo(岡田 直樹×2)・sugi-hd(西村 啓介×2)。姓のみ重複106社は軽微(識別可)。
- **欠損(フルGO=②で上乗せ)**: image_url(写真)/voice_config(音声)/age/department。フロントは既定アバター+TTS非表示でクリーンに処理済。②で生成し上書き加算すればライブ室がその場でGOLD化。

## ⏸ 2026-07-17 15:36 本体停止を検知(未完走)
再開: 先頭の【再開コマンド】を実行してください。registered-v3スキップで二重登録なし。


---
## ✅ Phase4 完走集計 (2026-07-18 13:31)
- v3登録: **397/400社**（残1・三井GOLD別枠1）
- 隔離(lint5未通過): **1社** canon
- 実費 概算: **$128**（$0.322/社×397）
- LINE完了通知: 送信OK code=200 consumption_delta=5
- アーキタイプ別v3登録:
    - メーカー: 65社
    - IT・AI・SaaS・ゲーム: 58社
    - 銀行・証券・保険: 40社
    - インフラ・エネルギー: 30社
    - 不動産・建設: 30社
    - 小売・流通: 30社
    - 広告・メディア: 30社
    - 食品・飲料: 24社
    - コンサル: 20社
    - 専門商社: 20社
    - 航空・運輸・物流: 20社
    - 医療・ヘルスケア: 10社
    - 総合商社: 8社
    - 教育・人材: 5社
    - スタートアップ: 4社
    - ディープテック・宇宙・AI: 3社

---
## ⏳ TODO予約: Git履歴パージ（アバター本走・完走後に実行）
- 状態: **Step1完了**（内部文書を現HEADから削除+push済＝現公開ツリーはクリーン）。**履歴パージは保留**。
- 理由: jsDelivrアバターURLが**コミットハッシュ固定**のため、生成中に履歴を書き換えると全アバターが404になる。必ずアバター完走後。
- 完走後の手順:
  1. personas.image_url をハッシュ固定→`@main`等の「履歴書換で壊れない」URLへ切替（or 事前にハッシュ退避）
  2. 全auto-pushループ停止（launchd `com.tokyari.phasec`/`com.tokyari.sheetsync` ＋ `room_avatar_gen.py`）
  3. `git filter-repo --path l2_l3_video_pilot/ --invert-paths`（全履歴から除去）→ `git push --force`
  4. 実API/CDNで全社アバター表示を検証
  5. ループ再開
- 恒久ルール: 内部文書（レポート/コスト/人員/Notion内部ID/内部パス）はこのpublic repoに二度とcommitしない（ローカル~/oscar-ai/かNotionのみ）。
