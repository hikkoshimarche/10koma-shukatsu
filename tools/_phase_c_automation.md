# Phase C 全面自動化 — 棚卸し・配線・運用
2026-07-11 実装。方針「自動化できるものは全部する／ゲートは絶対に外さない」。既存の台本FB毎時ループ(deploy_fb.py)は不変で、画像系の人手工程を型別に自走させる拡張を追加。

## STEP1 人手待ち棚卸し(実データ・2026-07-11時点)
| 区分 | 実数 | 分類 | 根拠 |
|---|---|---|---|
| attention(intern提出FB・未反映) | 62社 | (a)/(b) | 台本=deploy_fbが自動反映(既存)。画像=下記型別 |
| 共通の修正案 未適用 | 1355行 | — | 内訳↓ |
| ├ [要画像再生成] 社×koマ distinct | 274 | 型別↓ | |
| │ ├ 安全型(meta_frame/white_band/hline) | 47 | **(a)完全自動** | QA/canary/404通過で人手ゼロ反映(実証済型) |
| │ ├ 描画型(scale/hands/accuracy/compound) | 25 | **(b)半自動** | 候補生成→QA→人QA(OK/NGだけ) |
| │ └ 未知/主観(将来像・本社リアル等) | 202 | **(b)半自動** | 候補生成→人QA。真に好みは(c) |
| ├ [判断ダイジェスト](真の判断) | 67 | **(c)自動化不可** | 経営/ブランド/好み判断=人の領分 |
| └ [要調査](裏取り) | 226 | (a)/(b) | Claude自動裏取り(取れねばぼかす)=既存経路 |
| 入口3社(富士通/三菱商事/双日 k1) | 3 | **(a')協調full-auto** | 台本+画像を同一Tx反映・片方反映を構造禁止 |
| text_leak(焼き込み文字: ABEJA k7等) | — | **(a)完全自動** | 本実装で安全型に追加 |

(a)完全自動化=ゲート通過なら人手ゼロで本番まで / (b)半自動=生成は自動・反映前に人がOK/NG 1回 / (c)自動化不可=人の判断そのもの。

## STEP2 配線(自動化の本丸)
### 型別 自動化レベル(フラグ)
- `AUTO_IMAGE_FIX_ENABLED`(master, 既定**0=OFF**): 1でのみ画像系がライブ。OFF時は毎時ループは従来通り(台本反映のみ)+拡張はdryで無変・**Claude再トリアージも走らせない**(浪費防止)。
- `AUTO_SAFE_TYPES`(既定 `meta_frame,white_band,hline,text_leak`): 安全型=full auto。
- `AUTO_COORDINATED`(既定 `1`): 入口型=協調full-auto(ゲート付)。
- `AUTO_MIXED_MODE`(既定 `notify`): 混在型=候補生成+人QA依頼まで(自動反映しない)。`off`で無効。
- 予算/レート/コマ上限/一時停止 は既存 `phase_c_image_fix.cfg()` を継承(day<$5, hour<10コマ, per-koma<2, QA連続失敗×3で自動停止)。

### 消化パス(`phase_c_auto.run_batch`, deploy_fb 後段が呼ぶ)
1. **人QA消化** `consume_human_qa`: スプシ『画像人QA』で人が`OK`にした候補を canary/404付きで反映(image_urlのみ)。
2. **協調反映** `coordinated_reflect_one`(入口3社): 台本(scenario_v4.json, lint error0)+画像(再生成→QA)が**両方**整った時のみ、台本列+image_urlを**同一wranglerコマンド**で反映→canary(対象外不変)→404。
   - **片方反映の構造禁止**: `can_coordinate_reflect(lint_err, qa_pass)` を通らない限りD1へ1バイトも書かない。lint NG→画像も反映しない/QA NG→台本も反映しない。selftestで「片方成立時 書き込み0回」を実証。
3. **型別ルーティング** `route_image_fbs`(master ON時のみ): attention+`_image_targets_extra.json`の画像FBを translate→型分類→安全型=`PCI.run_one`でfull auto / 混在型=`mixed_notify_one`で候補生成+人QA。overlay文字は台本経路(deploy_fbが担当)へ。

### ゲート(絶対不変・自動化≠省略)
lint error0(台本) / ハードQA(overall_severity≠severe & char_match=ok, 3回不可→反映せず) / 一般化canary(対象社以外 全hash不変) / API 404/URL整合検証 / D1バックアップ(可逆) / 予算・レート上限。**全ゲート通過分だけが自動反映、不通過は自動で据置/エスカレ。**

### launchd / キルスイッチ(不変)
- `com.tokyari.phasec`(毎時 deploy_fb.py)は既存のまま。拡張は同ループ後段に載る。
- キル: `launchctl unload ~/Library/LaunchAgents/com.tokyari.phasec.plist`(または `AUTO_IMAGE_FIX_ENABLED=0`)。

## STEP3 通知(人は見るだけ)
- 3hレポート(`line3hSummary`)に統合: AI反映社 + **🖼画像人QA待ち候補URL**(人はURLを見てスプシ『画像人QA』にOK/NG記入→次ループが自動反映)+ OK済反映待ち件数。真の判断(c)は朝9時ダイジェスト。
- GAS新mode: `addimageqa`(候補起票・重複上書き) / `imageqa_approved`(OK候補を返す) / `setimageqa`(反映済化)。

## STEP4 即時消化対象(次ループで自動処理される状態)
- 入口3社: `_coordinated_targets.json` に登録済(image_komas=[1], text_komas=各隣接)。
- ABEJA k7(text_leak安全型): `_image_targets_extra.json` に登録済。
- どちらも **Mac側ループが `AUTO_IMAGE_FIX_ENABLED=1`** かつ **GEMINI_API_KEY** を持つ次回実行で自動消化。

## STEP5 検証結果(実値)
- selftest 3種 ALL PASS: `deploy_fb`(既存関所・無傷) / `phase_c_image_fix`(text_leak含む型分類) / `phase_c_auto`(協調ゲート=片方反映0回を構造実証)。
- 協調dry-run: 3社とも台本lint_err=0・image/text koマ分離正しく計画。
- ABEJA k7 dry: text_leak→安全型full-auto経路・DRYで生成せず。
- LINE transport: linequota HTTP200(group_id有・quota 1515/5000)=/exec到達可。3h新書式はnode構文OK。
- 既存毎時ループ: 直近実行 正常終了(=== 着地 反映0/画像保留5/... オスカー即時エスカレ=0 ===)。
- キルスイッチ: com.tokyari.phasec ロード確認(exit 0)。

## 未完了(資格情報を扱わないため次アクションに委譲)
- **GEMINI_API_KEY** はこの環境に無し → 画像生成/協調反映のライブ実行はMac側ループ(キー保持)に委譲。実装・登録・ゲート・selftestは完了、`AUTO_IMAGE_FIX_ENABLED=1` で次回自動稼働。
- **clasp 認証が期限切れ**(invalid_grant) → GAS新mode/3h書式は実装・構文検証済だが `/exec` 未反映。オスカーが `clasp login` 後 `clasp push && clasp deploy -i <deploymentId>` で反映(scriptId=1XvXUHZU4ud-yk1eIZ__HJWDbIKKTG8SLzikP0uev04wMlyf5C65waaYb)。未反映でもPython側は graceful(人QAモードが空を返すだけ・既存ループ無傷)。
