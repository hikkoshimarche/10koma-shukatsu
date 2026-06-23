#!/bin/bash
# shutdown_and_snapshot.sh — 出発時に1発で: スナップショット保存→3プロセス停止→再開コマンド出力。
# 自走FBループ(launchd com.tokyari.phasec)は触らない(海外でMac起動時に自動復帰)。
set +e
TOK=/Users/oscardodds/oscar-ai/tokyari-pipeline
OUT=$TOK/output
PY=$TOK/.venv/bin/python
STATE=/Users/oscardodds/oscar-ai/RESUME_STATE.txt
SNAP_ONLY="${1:-}"   # --snap-only で停止せずカウントのみ

# ---- スナップショット計測 ----
count_industry() {  # 業界名→10/10完成社数
  $PY - "$1" <<'PYEOF'
import sys
sys.path.insert(0,'/Users/oscardodds/oscar-ai/tokyari-pipeline/scripts')
import company_master as cm
from pathlib import Path
OUT=Path('/Users/oscardodds/oscar-ai/tokyari-pipeline/output')
ind=sys.argv[1]; comps=cm.companies_in_industry(ind)
done=sum(1 for c in comps if (OUT/c['slug']).exists() and len(list((OUT/c['slug']).glob('koma*.png')))>=10)
print(f"{done}/{len(comps)}")
PYEOF
}
A=$(count_industry "航空・運輸・物流")
B=$(count_industry "広告・メディア")
C=$(count_industry "不動産・建設")
D=$(count_industry "IT・通信・SaaS")
SYNCED=$(grep -c ',d1_sync,' "$TOK/output/notion_sync_state.csv" 2>/dev/null || echo 0)
NOW=$(date '+%Y-%m-%d %H:%M:%S')

# ---- RESUME_STATE.txt 書き出し(再開コマンドを先頭に) ----
cat > "$STATE" <<EOF
==== 再開コマンド（帰国後コピペ1発で続きから）====
# 1) 夜間画像生成（completed済みは自動スキップ・未生成社だけ生成）
caffeinate -dims bash -c 'cd $TOK; for I in "航空・運輸・物流" "広告・メディア" "不動産・建設" "IT・通信・SaaS"; do .venv/bin/python scripts/drive_images_industry.py "\$I"; done' > ~/oscar-ai/tokyari-pipeline/../resume_imggen.log 2>&1 &

# 2) Notionバックフィル（notion_sync_state.csvで未同期の社だけ・重複作成しない=タイトルガード）
cd /Users/oscardodds/projects/10koma-shukatsu && \\
SLUGS=\$(npx wrangler d1 execute 10koma-shukatsu-db --remote --config api/wrangler.toml --command "SELECT id FROM companies" --json 2>/dev/null | $PY -c "import json,sys,csv;d=set(r['id'] for r in json.load(sys.stdin)[0]['results']);s=set(r[0] for r in csv.reader(open('$TOK/output/notion_sync_state.csv')) if len(r)>4 and r[4]=='d1_sync');print(','.join(d-s))") && \\
caffeinate -dims $PY $TOK/scripts/notion_sync_d1.py --slugs "\$SLUGS" > ~/oscar-ai/resume_notion.log 2>&1 &

# 3) 完成業界の投入（任意・harness_deploy/deploy_industry経由）
# cd /Users/oscardodds/projects/10koma-shukatsu && .venv… (各業界 deploy_industry.py を完成枚数に応じて)

==== スナップショット (${NOW}) ====
夜間画像生成 完成社(10/10):
  航空・運輸・物流 : ${A}
  広告・メディア   : ${B}
  不動産・建設     : ${C}
  IT・通信・SaaS   : ${D}
Notionバックフィル 同期済(d1_sync): ${SYNCED} 社
自走FBループ(launchd com.tokyari.phasec): 触らない=海外でMac起動時に自動復帰
EOF

echo "=== スナップショット保存: $STATE ==="
cat "$STATE" | sed -n '/==== スナップショット/,$p'

if [ "$SNAP_ONLY" = "--snap-only" ]; then
  echo ""; echo "[--snap-only] プロセスは停止しません(計測のみ)。"
  exit 0
fi

# ---- 3プロセスをキレイに停止 ----
echo ""; echo "=== プロセス停止 ==="
# 画像生成(特定パターン限定=brew等を誤killしない)
for pat in "drive_images_industry" "scripts/generate_images.py"; do
  for pid in $(pgrep -f "$pat"); do kill "$pid" 2>/dev/null && echo "  killed $pat ($pid)"; done
done
# Notionバックフィル
for pid in $(pgrep -f "notion_sync_d1.py"); do kill "$pid" 2>/dev/null && echo "  killed notion_sync_d1 ($pid)"; done
# caffeinate
for pid in $(pgrep -f "caffeinate -dims"); do kill "$pid" 2>/dev/null && echo "  killed caffeinate ($pid)"; done

# 破損png削除(サイズ0=生成途中)。完成済みは保持。
echo "=== 破損png(サイズ0)削除 ==="
DEL=$(find "$OUT" -name "koma*.png" -size 0 -print -delete 2>/dev/null | wc -l | tr -d ' ')
echo "  削除 ${DEL} 枚(サイズ0)"

echo ""; echo "=== 停止完了。launchd phasec は稼働継続(海外で自動復帰)。RESUME_STATE.txt に再開コマンド有り。==="
echo "蓋を閉じてOKです。✈️"
