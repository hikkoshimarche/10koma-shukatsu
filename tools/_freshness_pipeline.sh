#!/bin/bash
# 夜間ハンズオフ: ②鮮度再生成266社 → ①残11業界セット。
# balance枯渇でfreshnessがsystemic HALTした場合は業界セットをスキップ(OpenAI死亡中に無駄撃ちしない)。
set -u
cd ~/projects/10koma-shukatsu/tools
export QUIZ_LATEST_FY="2026年3月期" QUIZ_LLM=openai
PLOG=/tmp/quiz_pipeline.log
: > "$PLOG"

echo "[$(date +%H:%M)] STAGE1 freshness(266) start" >> "$PLOG"
QUIZ_MAX_USD=120 caffeinate -dims python3 -u quiz_fanout.py --freshness > /tmp/quiz_freshness_run.log 2>&1
echo "[$(date +%H:%M)] STAGE1 freshness exit=$?" >> "$PLOG"

if grep -q "HALT] OpenAI" /tmp/quiz_freshness_run.log; then
  echo "[$(date +%H:%M)] STAGE2 SKIP: OpenAI HALT(残高枯渇疑い)→業界セット非実行" >> "$PLOG"
else
  echo "[$(date +%H:%M)] STAGE2 industry-sets(残11) start" >> "$PLOG"
  # --locked-all: 既出荷266社はskip-scan(無料)→業界phaseで欠落セットのみ生成(更新corpusをmerge)
  QUIZ_MAX_USD=130 caffeinate -dims python3 -u quiz_fanout.py --locked-all > /tmp/quiz_industry_run.log 2>&1
  echo "[$(date +%H:%M)] STAGE2 industry exit=$?" >> "$PLOG"
fi

echo "[$(date +%H:%M)] PIPELINE_DONE" >> "$PLOG"
