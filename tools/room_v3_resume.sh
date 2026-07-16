#!/bin/bash
# room_v3_resume.sh — ルームv3 本体rolloutを手動再開(reboot/kill後)。turnkey。
# registered-v3スキップで二重登録なし・並列3・三井除外・room-lint5ゲート・429→並列2自動降格を維持。
# 完走したら締め処理(タブ更新+LINE通知・重複防止)まで自動実行。
cd /Users/oscardodds/projects/10koma-shukatsu
LOG=tools/_room_phase3_resume.log
if pgrep -f "room_phase3_rollout" >/dev/null 2>&1; then
  echo "[resume] 本体rolloutは既に稼働中 → 再開不要" | tee -a $LOG; exit 0
fi
echo "[resume $(date '+%m-%d %H:%M')] rollout再開(並列3・resumable)" >> $LOG
python3 -u tools/room_phase3_rollout.py --conc 3 >> $LOG 2>&1
echo "[resume $(date '+%H:%M')] rollout終了 → 締め判定" >> $LOG
python3 tools/room_v3_complete.py >> $LOG 2>&1
echo "[resume] 完了" >> $LOG
