#!/bin/bash
# 月次: 選考情報を全社再取得(腐りやすいため)→D1反映。マナー=ニュース巡回と同じ(1req/秒/深掘り抑制)。
# 2026-11-18 是正: ①wrangler認証を cf_env と同方式(env→keychain)で解決 ②SQL出力先を別セッションの
#   Claude scratchpad固定から repo .backups/sql へ ③ログを /tmp(再起動で消える)から logs/ へ
#   ④set -euo pipefail で途中失敗を握り潰さない(旧版は取得/構築が失敗しても古いSQLを流し得た)。
set -euo pipefail
cd ~/projects/10koma-shukatsu
export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$(/usr/bin/security find-generic-password -a "$(id -un)" -s tokyari-cloudflare-api-token -w 2>/dev/null || true)}"  # cf_env と同方式
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then echo "✗ CLOUDFLARE_API_TOKEN 未解決(env/keychain)" >&2; exit 1; fi
export QUIZ_MAX_USD=10
export TOKYARI_SQL_OUT="$HOME/projects/10koma-shukatsu/.backups/sql"
mkdir -p "$TOKYARI_SQL_OUT" logs
LOG=logs/selection_monthly.log
echo "=== SELECTION_REFRESH_START $(date) ===" >> "$LOG"
python3 tools/gen_selection_info.py --all --force >> "$LOG" 2>&1
TS=$(date +%Y%m%d_%H%M)
python3 tools/build_company_selection.py "$TS" >> "$LOG" 2>&1
INS="$TOKYARI_SQL_OUT/company_selection.sql"
if [ ! -s "$INS" ]; then echo "✗ $INS が空/欠落 → D1反映せず(空=失敗)" >> "$LOG"; exit 1; fi
npx wrangler d1 execute 10koma-shukatsu-db --remote --config api/wrangler.toml --file "$INS" >> "$LOG" 2>&1
echo "SELECTION_REFRESH_DONE $(date)" >> "$LOG"
