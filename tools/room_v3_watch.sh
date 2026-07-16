#!/bin/bash
# room_v3_watch.sh — ルームv3 本体rolloutの完走を見張り、完走時に締め処理(タブ更新+LINE通知)を発火。
# caffeinateは付けない(オスカーのスリープを妨げない)。スリープ中はこのwatcherも凍結し、復帰で再開する。
# 本体rolloutがプロセスとして消えたら: 残≤閾値=完走→complete.py / 残>閾値=途中死→STATUSに一時停止を記す。
cd /Users/oscardodds/projects/10koma-shukatsu
LOG=tools/_room_v3_watch.log
echo "[watch開始 $(date '+%m-%d %H:%M')]" >> $LOG
while true; do
  if pgrep -f "room_phase3_rollout" >/dev/null 2>&1; then
    sleep 300; continue                      # 本体稼働中(スリープ凍結含む)→待つ
  fi
  # 本体プロセスが消えた → 完走 or 途中死 を判定
  sleep 30
  if pgrep -f "room_phase3_rollout" >/dev/null 2>&1; then continue; fi   # 再確認(誤検知回避)
  echo "[watch $(date '+%H:%M')] 本体プロセス消滅 → 締め判定" >> $LOG
  python3 tools/room_v3_complete.py >> $LOG 2>&1
  RC=$?
  if [ "$RC" -eq 0 ]; then
    echo "[watch] 完走締め完了(タブ更新+LINE通知済)" >> $LOG
  else
    echo "[watch] 未完走で本体停止 → 手動resume待ち(ROOM_V3_STATUS.md先頭コマンド)" >> $LOG
    { echo ""; echo "## ⏸ $(date '+%Y-%m-%d %H:%M') 本体停止を検知(未完走)"; \
      echo "再開: 先頭の【再開コマンド】を実行してください。registered-v3スキップで二重登録なし。"; } >> ROOM_V3_STATUS.md
  fi
  break
done
