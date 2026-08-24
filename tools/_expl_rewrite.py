#!/usr/bin/env python3
"""Lv4等の explanation『数値+単位+です』言い換えを、指標の一般定義へ機械的に書き直す(FB5)。
条件: explanation が『[数字]+単位(円/%/人/年/社…)+です』で終端。q_text/options/correct/difficulty は不変=explanation列のみUPDATE。
捏造ガード: 新explanationに旧に無い3桁以上数値が入ったら旧維持。会社ごとバッチ。
安全: 対象idを肯定確認→before/after explanation-hash canary→対象id以外UNEXPECTED0を検証。
出力: /tmp/expl_plan.json(適用前レビュー用)。--apply でD1書込。"""
import json, os, re, sys, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q
from _d1 import d1

APPLY = "--apply" in sys.argv
PAT = re.compile(r'[0-9０-９,，]+\s*(円|百万円|億円|兆円|千円|万円|％|%|人|名|社|拠点|店|年|歳|件|カ国|か国|ヶ国)\s*です[。\.]?$')

rows = d1("SELECT id,set_id,q_text,options,correct,explanation FROM quiz_questions")
targets = [r for r in rows if PAT.search((r['explanation'] or '').strip())]
if not targets:
    print("対象0件 — 『取得失敗の可能性』を確認せよ(空を対象なしと解釈しない)。中止。")
    sys.exit(1)
from collections import defaultdict
by = defaultdict(list)
for r in targets:
    by[r['set_id']].append(r)
print(f"対象: {len(targets)}件 / {len(by)}セット (条件: explanation が『数値+単位+です』終端)")

SYS = ("クイズ解説の校正。各解説を『答えの数値・事実の言い換え』でなく『その指標/用語が一般に何を意味し、なぜ重要か』の"
       "1〜2文へ書き直す。厳守:(a)新しい固有の数値/年号/比率を足さない(捏造禁止)。既出の答えの数値は繰り返さず一般的意味だけ。"
       "(b)設問文・選択肢・正解は変えない。解説だけ。(c)日本語で簡潔に。JSON {\"items\":[{\"id\":,\"explanation\":}]} のみ。")

def num_ok(old, new):
    on = set(re.findall(r'\d{3,}', re.sub(r'[,\s]', '', old or ''))); nn = set(re.findall(r'\d{3,}', re.sub(r'[,\s]', '', new or '')))
    return nn.issubset(on)

plan = {}
for sid, items in by.items():
    for i in range(0, len(items), 20):
        chunk = items[i:i+20]
        payload = [{"id": r['id'], "q_text": r['q_text'], "answer": (json.loads(r['options'])[r['correct']] if r['options'] else ''), "old": r['explanation']} for r in chunk]
        try:
            txt = q.openai_chat([{"role": "system", "content": SYS}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}], max_tokens=2000, json_mode=True, temperature=0.2)
            fx = {it['id']: it['explanation'].strip() for it in json.loads(txt).get('items', []) if it.get('id') and it.get('explanation')}
        except Exception as e:
            sys.stderr.write(f"[{sid}] chunk失敗(旧維持): {str(e)[:50]}\n"); fx = {}
        for r in chunk:
            new = fx.get(r['id'])
            if new and num_ok(r['explanation'], new) and not PAT.search(new):
                plan[r['id']] = new
    print(f"  {sid:30} {sum(1 for r in items if r['id'] in plan)}/{len(items)} 書直し ${q._cost['usd']:.2f}", flush=True)

json.dump(plan, open('/tmp/expl_plan.json', 'w'), ensure_ascii=False)
print(f"\n書直し可能: {len(plan)}/{len(targets)}件 ${round(q._cost['usd'],2)}")

if not APPLY:
    print("(レビューのみ。--apply でD1書込)")
    sys.exit(0)

# --- 適用: explanation専用canary(before) → UPDATE → after → 対象id以外UNEXPECTED0 ---
ts = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
def esnap():
    rs = d1("SELECT id,explanation FROM quiz_questions")
    return {r['id']: hashlib.sha256((r['explanation'] or '').encode()).hexdigest() for r in rs}
before = esnap()
json.dump(before, open(f'.backups/canary/expl_before_{ts}.json', 'w'))
# backup対象の旧explanation
bk = {r['id']: r['explanation'] for r in targets if r['id'] in plan}
json.dump(bk, open(f'.backups/quiz_expl_backup_{ts}.json', 'w'), ensure_ascii=False)
# 肯定確認: plan内idが実在するか
ex_ids = set(before.keys())
apply_ids = [i for i in plan if i in ex_ids]
if len(apply_ids) != len(plan):
    sys.stderr.write(f"⚠️ plan{len(plan)}件中 実在{len(apply_ids)}件 — 欠落あり、書込中止(空/欠落を対象なし扱いしない)\n"); sys.exit(1)
def esc(s): return str(s).replace("'", "''")
n = 0
for i in range(0, len(apply_ids), 40):
    ch = apply_ids[i:i+40]
    sql = "; ".join(f"UPDATE quiz_questions SET explanation='{esc(plan[qid])}' WHERE id='{esc(qid)}'" for qid in ch)
    d1(sql); n += len(ch)
after = esnap()
json.dump(after, open(f'.backups/canary/expl_after_{ts}.json', 'w'))
changed = {i for i in set(before)|set(after) if before.get(i) != after.get(i)}
unexpected = changed - set(apply_ids)
print(f"UPDATE {n}件 / 変化{len(changed)} / 対象外UNEXPECTED={len(unexpected)} {list(unexpected)[:5]}")
print("✅ explanation canary PASS" if not unexpected else "❌ FAIL")
