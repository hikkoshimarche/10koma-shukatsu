# 10koma-shukatsu / トーキャリ 開発ガイド

このリポジトリ（Cloudflare Pages + Workers + D1 = `10koma-shukatsu-db`）と、台本ソース（`~/oscar-ai/tokyari-pipeline/output/<slug>/scenario_v4.json`）を扱う際の恒久ルール。

## 【必須】台本のNotion保存（Definition of Done）
台本を新規作成・変更・本番デプロイしたら、その作業は「Notionファクトシートへの台本同期」まで終えて初めて"完了"とする。ローカル(scenario_v4.json / D1)だけで終えない。未同期で作業を閉じない。
- 同期は非破壊の notion_sync.py を使う：既存版は削除せず見出しを「⚠️旧版(...)」にrename、新版を「## 自動生成版 <日付> <版>（最新の正）✅」として末尾に追記。
- ID限定：登録済み page_id のみ更新。pages.create は禁止（新規ページを作らない）。slugにpage_idが無ければ skip＋報告。
- 別社上書き防止：書き込み前にタイトルが「🌐 {社名} ファクトシート」であることを fetch で確認。不一致なら skip＋報告。
- SYNC_DATE は実際の作業日・版（例: 2026-06-20 v4.1）に更新する。
- 本番デプロイ手順の最後に必ず「scenario_v4.json同期 ＋ Notion台本同期」を含める。どちらか欠けたら未完了。

## 【必須】台本の品質ゲート（本番反映前・Definition of Done）
台本を本番D1（`company_panels`）に入れる前に、加算式lint `scenario_lints_v5_ext` を **error=0** で通すこと。**error>0 はマージ/反映不可**。warning は人間レビュー（ブロックしない）。
- このゲートは `tokyari-pipeline/scripts/scenario_to_panels.py` の `build_sql_for_company`（v4経路）に**埋め込み済み**。`--slug X --v4` で生成すると error 時は **SQLを生成せず exit 1**（壊れた台本は migration 化できない＝本番に入らない）。`run_batch.py` はサブプロセス実行なので非ゼロ終了が伝播。
- 単体確認: `python tokyari-pipeline/scripts/scenario_lints_v5_ext.py output/<slug>/scenario_v4.json`（vendor: `10koma-shukatsu/tools/scenario_lints_v5_ext.py`）。回帰: `--selftest`。
- 緊急回避は `--no-lint`。**バイパス時は stderr に「⚠️ LINT GATE DISABLED」を出すので必ず監査記録を残す**（黙ってのバイパス禁止）。
- 検出項目: 倍率数値(原則D)/生Markdown/採用数レンジ無出典/同語連発/終端記号/第三者(OB先輩)主役化。`RATIO_WHITELIST`(住友189倍・岩谷暫定)で意図的容認は warning 化。

### 埋め込みゲートの実コード（再構築用・`scenario_to_panels.py` は未追跡repoのため消失時はこれで復元）
`scenario_to_panels.py` 冒頭（import直後）:
```python
class LintError(RuntimeError):
    """scenario_lints_v5_ext の error 検出時に SQL 生成を中止するための例外。"""
```
`build_sql_for_company(tokyari_slug, ref, warnings=None, use_v4=False, lint=True)` の scenario 読込直後（**全部入りゲート**: v4 4-lint＋話者主役表記揺れ＋v5_ext）:
```python
    if lint and use_v4:
        _sd = str(Path(__file__).resolve().parent)   # cwd非依存: scripts/ を import path に
        if _sd not in sys.path:
            sys.path.insert(0, _sd)
        _errs = []
        # (1) v5_ext (倍率/生MD/採用数/同語連発/終端/第三者主役化)
        try:
            from scenario_lints_v5_ext import run_ext_lints, format_report as _fmt_ext
        except Exception as _e:
            raise LintError(f"lint module 読込失敗 (scenario_lints_v5_ext): {_e}")
        _rep = run_ext_lints(scenario, tokyari_slug)
        if _rep["errors"] > 0:
            _errs.append(_fmt_ext(_rep))
        # (2) 本家 v4 4-lint (story_type_repeat は history連携要のため対象外) / (3) 話者: 主役表記揺れのみerror
        try:
            from scenario_lints import run_all_v4_lints, lint_speaker_tag
        except Exception as _e:
            raise LintError(f"lint module 読込失敗 (scenario_lints): {_e}")
        _v4 = run_all_v4_lints(scenario, tokyari_slug)
        for _k, _items in _v4.items():
            if _k == "story_type_repeat" or not _items:
                continue
            _errs.append(f"[{_k}] (v4)\n" + "\n".join(f"  - {_i}" for _i in _items))
        _spk_fatal = [w for w in lint_speaker_tag(scenario) if "★主役の表記揺れ★" in w]
        if _spk_fatal:
            _errs.append("[speaker_tag] 主役表記揺れ(error)\n" + "\n".join(f"  - {w}" for w in _spk_fatal))
        if _errs:
            sys.stderr.write("\n".join(_errs) + "\n")
            raise LintError(f"[lint] {tokyari_slug}: 品質ゲート error 検出 → SQL生成中止 (--no-lint で回避可)")
```
※ 未知タグ(OB先輩等)は warning＝通す。story_type_repeat は生成バッチ側で history 突合（関所ではgateしない）。
`main()`（argparse に `--no-lint` 追加、生成ループ）:
```python
    parser.add_argument("--no-lint", action="store_true",
                        help="品質ゲート(scenario_lints_v5_ext)をバイパス (監査用に stderr 警告を出す)")
    ...
    if args.no_lint:
        sys.stderr.write("⚠️ LINT GATE DISABLED (--no-lint) — 品質ゲートをバイパスしています。監査用に記録してください。\n")
    lint_failed = []
    for t in targets:
        try:
            chunks.append(build_sql_for_company(t, args.ref, warnings=warnings, use_v4=args.v4, lint=not args.no_lint))
        except LintError as e:
            sys.stderr.write(str(e) + "\n"); lint_failed.append(t)
    if lint_failed:
        sys.stderr.write(f"\n❌ LINT GATE: {lint_failed} で error → SQL生成せず\n"); return 1
```
※ `--all` は `SLUG_MAP` のうち scenario 実在slugのみ対象に限定（テスト用 `__lint_test__` 等で batch が壊れないため）。
