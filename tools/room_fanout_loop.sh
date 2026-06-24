#!/bin/bash
# --all を最大4巡。各巡でskip社(不運な抽出ゆらぎ)をretry。D1完成数が増えなくなったら終了。
cd ~/oscar-ai/tokyari-pipeline
WCONF=/Users/oscardodds/projects/10koma-shukatsu/api/wrangler.toml
d1count(){ cd /Users/oscardodds/projects/10koma-shukatsu; npx wrangler d1 execute 10koma-shukatsu-db --remote --config "$WCONF" --command "SELECT COUNT(DISTINCT company_slug) s FROM room_personas GROUP BY company_slug HAVING COUNT(*)=6" --json 2>/dev/null | python3 -c "import json,sys;print(len(json.load(sys.stdin)[0]['results']))"; cd ~/oscar-ai/tokyari-pipeline; }
for pass in 1 2 3 4; do
  before=$(d1count)
  echo "[$(date '+%m-%d %H:%M')] === fanout pass $pass 開始 (D1=$before) ===" >> ~/oscar-ai/resume_room.log
  .venv/bin/python -u scripts/room_harness.py --all >> ~/oscar-ai/resume_room.log 2>&1
  after=$(d1count)
  echo "[$(date '+%H:%M')] pass $pass 終了 (D1 $before→$after)" >> ~/oscar-ai/resume_room.log
  [ "$after" -le "$before" ] && { echo "[増分0=収束→ループ終了]" >> ~/oscar-ai/resume_room.log; break; }
done
# 最終sync
.venv/bin/python scripts/room_tab_sync.py >> ~/oscar-ai/resume_room.log 2>&1
.venv/bin/python scripts/room_blocked_sync.py >> ~/oscar-ai/resume_room.log 2>&1
curl -sL "https://script.google.com/macros/s/AKfycbyhe5TuRbl0I8zV6-BUCmDGGL3MITkoqJSJZy_JzpkgPJWtSQNuPK9E7PDsPleCaQdYbw/exec?mode=roomdashboard&token=tokyari-7h2k9q4w8z" >> ~/oscar-ai/resume_room.log 2>&1
echo "[$(date '+%H:%M')] 全ループ完了・最終sync済" >> ~/oscar-ai/resume_room.log
