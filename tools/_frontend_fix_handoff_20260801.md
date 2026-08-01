# フロントエンド3修正の申し送り（2026-08-01・タブE）

通し確認で見つけた3件を修正→push したが、**Cloudflare Pages への配信が確認できず**、
中核画面 company.html の安全ルール（未検証なら revert）に従い company.html のみ revert した。

## push した commit
- `f1b3d5cc` fix1 company.html（LINE外でゲスト10コマ表示・isInClientガード統一・ゲスト時log-view非発火・bookmark/like案内） → **revert 済（`60604b4c`）**
- `7d0ca626` fix2 mypage.html（未ログイン時に共有guest-previewの個人記録を出さずログイン案内・?u=は維持） → **保持**
- `49a29871` fix3 company-list.html（industry未指定時に業界選択カードを出し前へ進める） → **保持**
- 参考: `d0bc521b` fix(quiz) は**タブDの修正**（レベルはしご・全0問社は非表示）。rebaseで取り込まれただけ＝私は quiz.html 未介入。

## 配信状況（実測）
- 私のfixより前の `8c37bdeb` fix(lp) は **本番配信済**（"400社以上"がlive）＝自動デプロイは機能している。
- しかし fix1/2/3（後続commit）は **未配信**（`company.html?cb=` に "guest: true" が出ない=0）。ビルド保留か失敗か未特定。
- → **本番 company.html は旧コードのまま＝未変更＝安全**（在LINEの従来動作を維持）。

## 検証できた / できなかった
- できた: 本番が旧コード（fix未配信）であること。auto-deploy自体は機能（LP配信済）。
- できなかった: fix1/2/3 の**修正後の実機挙動**（未配信のため）。company.html はそもそも headless では在LINE検証不可（LINE外ゲスト経路のみ headless で確認可能）。

## revert したか
- **YES（company.html のみ）**。理由: 「5分待ってデプロイ完了せず＋中核画面を未検証で放置しない＋安全側」の事前ルール。
- fix2/fix3 は現状が壊れ状態（mypage=共有レコード漏れ / company-list=行き止まり）の是正で低回帰リスクゆえ**保持**（配信されれば改善）。

## 次セッションでやること
1. company.html fix を**再適用**（`git revert 60604b4c` で戻せる／または f1b3d5cc を cherry-pick）。**在LINE挙動は不変**（`isInClient()`分岐追加のみ・logged-in経路は無変更）。
2. なぜ fix1/2/3 が配信されなかったか確認（Pagesのビルドログ・失敗有無）。auto-deployが後追いで fix2/3 を配信するはず。
3. 配信後、**LINE外ゲスト経路（headless）＋在LINE実機**の両方で company.html を検証してから fix1 を本番へ。
4. mypage は ?u= override が従来どおり動くこと、更新フィード(非個人)の扱いを確認。
