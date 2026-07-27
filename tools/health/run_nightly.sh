#!/bin/bash
# 夜間ヘルスチェック runner (launchd com.tokyari.healthcheck から毎晩3:00)。
# caffeinate で確実に完走。レポートは reports/ (gitignore・push しない)。検知のみ・修正しない。
cd "$HOME/projects/10koma-shukatsu/tools" || exit 1
VENV="$HOME/oscar-ai/tokyari-pipeline/.venv/bin/python"
LOG="$HOME/projects/10koma-shukatsu/tools/health/reports/_run_$(date +%Y%m%d_%H%M).log"
# ① ページ/API/画像巡回 + 禁止語チェック(One Spirit Diamond / デンソ 等)
/usr/bin/caffeinate -dimsu "$VENV" healthcheck.py >> "$LOG" 2>&1

# ② 導線チェック(全リンク+パラメータ伝搬・Playwright)。node は nvm 管理のため動的PATH前置。
export PATH="$(/bin/ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1):/usr/local/bin:/opt/homebrew/bin:$PATH"
echo "=== 導線チェック (link_audit.js) $(date) ===" >> "$LOG"
if command -v node >/dev/null 2>&1; then
  /usr/bin/caffeinate -dimsu node "$HOME/projects/10koma-shukatsu/tools/link_audit.js" >> "$LOG" 2>&1
  echo "link_audit exit=$?" >> "$LOG"
  # ③ 画像アスペクト比チェック(全ページ×多端末幅・歪み検出)。NGがあれば exit1。
  echo "=== 画像アスペクト比チェック (img_aspect_check.js) $(date) ===" >> "$LOG"
  /usr/bin/caffeinate -dimsu node "$HOME/projects/10koma-shukatsu/tools/img_aspect_check.js" >> "$LOG" 2>&1
  echo "img_aspect_check exit=$?" >> "$LOG"
else
  echo "⚠ node 未解決のため導線/画像チェックskip" >> "$LOG"
fi
