#!/bin/bash
# ES kit 266社ファンアウト(ローカル生成): ①質的増強 → ③ES kit生成。
# D1更新(datasheet/es_kits)と集約・random5は完走後に手動で安全実施。resumable。
set -u
cd ~/projects/10koma-shukatsu/tools
export QUIZ_LLM=openai QUIZ_MAX_USD=100
PLOG=/tmp/es_fanout.log
: > "$PLOG"

echo "[$(date +%H:%M)] STAGE1 質的増強(266) start" >> "$PLOG"
caffeinate -dims python3 -u enrich_datasheet.py > /tmp/es_enrich.log 2>&1
echo "[$(date +%H:%M)] STAGE1 enrich exit=$?" >> "$PLOG"

echo "[$(date +%H:%M)] STAGE2 ES kit生成(--all) start" >> "$PLOG"
caffeinate -dims python3 -u gen_es_kit.py --all > /tmp/es_kit_all.log 2>&1
echo "[$(date +%H:%M)] STAGE2 eskit exit=$?" >> "$PLOG"
echo "[$(date +%H:%M)] PIPELINE_DONE" >> "$PLOG"
