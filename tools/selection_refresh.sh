#!/bin/bash
# 月次: 選考情報を全社再取得(腐りやすいため)→D1反映。マナー=ニュース巡回と同じ(1req/秒/深掘り抑制)。
cd ~/projects/10koma-shukatsu
export QUIZ_MAX_USD=10
python3 tools/gen_selection_info.py --all --force > /tmp/selection_monthly.log 2>&1
TS=$(date +%Y%m%d_%H%M)
python3 tools/build_selection_d1.py "$TS" >> /tmp/selection_monthly.log 2>&1
INS=/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/selection_insert.sql
npx wrangler d1 execute 10koma-shukatsu-db --remote --config api/wrangler.toml --file "$INS" >> /tmp/selection_monthly.log 2>&1
echo "SELECTION_REFRESH_DONE $(date)" >> /tmp/selection_monthly.log
