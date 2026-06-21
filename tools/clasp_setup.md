# GAS(clasp) セットアップ手順 — 既存プロジェクトを絶対clobberしない

Phase C 自動ループの GAS 変更（mode拡張・共通修正案タブ・書き戻し・LINE 3hトリガー）を
既存GASプロジェクト（Phase A+B の 9時ダイジェスト）に **追記** で反映するための一度きり手順。

## あなたが一度だけやること（対話認証が要るため）

```bash
# 1. clasp 導入
npm install -g @google/clasp

# 2. Google ログイン（ブラウザが開く。GASを持つGoogleアカウントで許可）
clasp login

# 3. Apps Script API を有効化（未なら）
#    https://script.google.com/home/usersettings → 「Google Apps Script API」を ON
```

## scriptID を教えてください（これが唯一の不足物）

既存GASの **スクリプトID** が必要です。取得方法のどちらかで：
- script.google.com で対象プロジェクトを開く → 「プロジェクトの設定（⚙）」→「スクリプト ID」をコピー
- またはWebアプリURL `https://script.google.com/macros/s/XXXXXXXX/exec` の `XXXXXXXX` 部分

→ この scriptID を貼ってください。受け取ったら **私が** 以下を安全に実施します：

```bash
# 私が実行（既存コードを必ず先に取り込む＝clobber防止）
mkdir -p tools/gas && cd tools/gas
clasp clone <scriptID>          # 既存 .gs を全て取り込む（上書きしない）
# → 取り込んだ実物のシート列/関数を確認し、衝突しない名前で additive に追記
clasp push                       # 追記分のみ反映（pull済みの既存は保持）
```

## トリガー（時刻起動）
LINE 3時間スケジュール等は、私が `setupTriggers()` 関数を用意します。
clasp push 後、**GASエディタで `setupTriggers` を1回だけ手動実行**（または `clasp run setupTriggers`）で
既存トリガーを消さずに追加します。再認証を求められたら教えてください。

## 安全
- `clasp clone` で既存全コードをローカルに取り込んでから追記するため、9時ダイジェストのコードは保持されます。
- push前に `git add tools/gas` で差分をコミットし、いつでも戻せる状態にします。
