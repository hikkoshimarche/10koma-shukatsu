#!/bin/bash
# 夜間ヘルスチェック runner (launchd com.tokyari.healthcheck から毎晩3:00)。
# caffeinate で確実に完走。レポートは reports/ (gitignore・push しない)。検知のみ・修正しない。
cd "$HOME/projects/10koma-shukatsu/tools" || exit 1
VENV="$HOME/oscar-ai/tokyari-pipeline/.venv/bin/python"
LOG="$HOME/projects/10koma-shukatsu/tools/health/reports/_run_$(date +%Y%m%d_%H%M).log"
/usr/bin/caffeinate -dimsu "$VENV" healthcheck.py >> "$LOG" 2>&1
