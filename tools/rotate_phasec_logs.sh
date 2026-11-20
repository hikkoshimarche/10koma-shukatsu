#!/bin/bash
# phasec等の logs/*.log を 20MB超で gzipローテーション(最新2世代保持)。毎日launchdで実行。
LOGDIR="/Users/oscardodds/projects/10koma-shukatsu/logs"
ARCH="$LOGDIR/archive"; mkdir -p "$ARCH"
MAX=$((20*1024*1024))
for f in "$LOGDIR"/*.log; do
  [ -f "$f" ] || continue
  sz=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [ "$sz" -gt "$MAX" ]; then
    b=$(basename "$f")
    gzip -c "$f" > "$ARCH/${b}.$(date +%Y%m%d_%H%M%S).gz"
    : > "$f"
    # 各ログ最新2世代のみ保持
    ls -1t "$ARCH/${b}."*.gz 2>/dev/null | tail -n +3 | xargs -I{} rm -f {}
  fi
done
