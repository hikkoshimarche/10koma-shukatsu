#!/usr/bin/env python3
"""lint-gated 置換エンジン: 削除対象を除いた集合に、corpus由来の新問を『追加しても新lint errorが1件も増えない』
候補だけ採用して15へ。人名/予想値0・Source-or-Silence(corpus接地)・解説は指標定義化。
corpusで15に届かなければ止めて不足報告(捏造しない)。生成結果→/tmp/replace_out.json(D1未書込)。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_lint as QL
import quiz_fanout as q
import quiz_difficulty as D
import _person_v3 as P
from _d1 import d1

OUT = q.OUT
FORECAST = re.compile(r'見込み|見通し|となる予定|とする予定|予想配当|来期予想|来期|予想')
NONPRAC = re.compile(r'資本金|包括利益|実効税率|法人所得税|持分比率')   # 非実用財務(F条件)を置換候補から除外
plan = json.load(open('/tmp/replace_plan.json'))
remove = set(plan['remove'])
sets = plan['plan']

def corpus_of(slug):
    for fn in ("quiz_corpus_locked_v3.json", "rendered_corpus.json"):
        p = os.path.join(OUT, slug, fn)
        if os.path.exists(p):
            d = json.load(open(p))
            return {u: (v.get("text", "") if isinstance(v, dict) else str(v)) for u, v in d.items()} if fn == "rendered_corpus.json" else d
    return {}

def as_quiz(r):
    try: o = json.loads(r['options'])
    except: o = []
    return {'id': r['id'], 'q_text': r.get('q_text') or '', 'options': o, 'correct': r['correct'],
            'category': r.get('category') or '', 'source_url': r.get('source_url') or '',
            'as_of': r.get('as_of') or '', 'explanation': r.get('explanation') or '', 'difficulty': r.get('difficulty')}

def cand_quiz(x, lv, cid='CAND'):
    return {'id': cid, 'q_text': x.get('q_text', ''), 'options': x.get('options') or [], 'correct': int(x.get('correct', 0)),
            'category': x.get('category', ''), 'source_url': x.get('source_url', ''), 'as_of': x.get('as_of', ''),
            'explanation': x.get('explanation', ''), 'difficulty': lv}

out = {}
for sid, info in sets.items():
    need = info['need']
    if need <= 0:
        continue
    st = info['st']
    corpus = corpus_of(sid)
    rows = d1(f"SELECT id,q_text,options,correct,category,source_url,as_of,explanation,difficulty FROM quiz_questions WHERE set_id='{sid}'")
    kept = [as_quiz(r) for r in rows if r['id'] not in remove]
    base_err = QL.run_quiz_lints(kept, corpus).get('errors', 0)
    name = json.load(open(os.path.join(OUT, sid, 'datasheet.json'))).get('name', sid) if os.path.exists(os.path.join(OUT, sid, 'datasheet.json')) else sid.replace('industry__', '')
    try:
        final, _, _ = q.converge_locked(sid, name, corpus, target=30, fin_floor=3)
    except Exception as e:
        out[sid] = {'need': need, 'accepted': [], 'short': need, 'err': str(e)[:60]}
        print(f"  {sid:38} need{need} GEN_ERR {str(e)[:40]}", flush=True)
        continue
    accepted = []
    working = list(kept)
    for x in final:
        if len(accepted) >= need:
            break
        opts = x.get('options') or []
        corr = int(x.get('correct', 0))
        cval = str(opts[corr]) if corr < len(opts) else ''
        prow = {'id': 'c', 'q_text': x.get('q_text', ''), 'options': json.dumps(opts, ensure_ascii=False), 'correct': corr}
        if P.detect([prow]):            # 人名
            continue
        if FORECAST.search(x.get('q_text', '')):  # 予想値
            continue
        if NONPRAC.search(x.get('q_text', '')):   # 非実用財務(資本金/包括利益/実効税率/法人所得税/持分比率)
            continue
        if 'Access Denied' in cval:
            continue
        lv = 4 if D.rule_level(x) >= 4 else (1 if (x.get('category') or '') in {'製品・サービス', '事業セグメント', '会社概要'} else 2)
        cq = cand_quiz(x, lv, cid=f"{sid}_rp{len(accepted)+1}")   # 候補idをユニーク化(id衝突でのsingle_correct誤発火を回避)
        trial = working + [cq]
        rep = QL.run_quiz_lints(trial, corpus)
        if rep.get('errors', 0) > base_err:   # 新errorを1件でも増やす候補は却下(concept_dedup/address/source等 全種)
            continue
        working = trial
        accepted.append((x, lv))
    out[sid] = {'st': st, 'need': need, 'accepted_n': len(accepted), 'short': need - len(accepted),
                'accepted': [(x, lv) for x, lv in accepted]}
    mark = '✓' if len(accepted) >= need else f'✗不足{need-len(accepted)}'
    print(f"  {sid:38} need{need} 採用{len(accepted)} {mark} ${q._cost['usd']:.2f}", flush=True)

# 解説を指標定義化(採用分)
SYS = ("解説を『答えの数値の言い換え』でなく『その指標が一般に何を表すか/なぜ重要か』の1〜2文に。"
       "新しい固有数値/年号を足さない(捏造禁止)。設問/選択肢/正解不変。JSON {\"items\":[{\"id\":,\"explanation\":}]}のみ")
for sid, info in out.items():
    acc = info.get('accepted') or []
    if not acc:
        continue
    payload = [{"id": f"{sid}#{i}", "q": x.get('q_text'), "a": (x.get('options') or [''])[int(x.get('correct', 0))], "old": x.get('explanation', '')} for i, (x, lv) in enumerate(acc)]
    try:
        txt = q.openai_chat([{"role": "system", "content": SYS}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}], max_tokens=1500, json_mode=True, temperature=0.2)
        fx = {it['id']: it['explanation'].strip() for it in json.loads(txt).get('items', []) if it.get('id') and it.get('explanation')}
        for i, (x, lv) in enumerate(acc):
            k = f"{sid}#{i}"
            new = fx.get(k)
            if new:
                on = set(re.findall(r'\d{3,}', re.sub(r'[,\s]', '', x.get('explanation', '')))); nn = set(re.findall(r'\d{3,}', re.sub(r'[,\s]', '', new)))
                if nn.issubset(on):
                    x['explanation'] = new
    except Exception as e:
        pass

json.dump(out, open('/tmp/replace_out.json', 'w'), ensure_ascii=False)
tot_need = sum(v['need'] for v in out.values())
tot_acc = sum(v.get('accepted_n', 0) for v in out.values())
short = {s: v['short'] for s, v in out.items() if v.get('short', 0) > 0}
print(f"\n=== 置換生成完了: 要{tot_need} 採用{tot_acc} / 不足セット{len(short)} {short} ${round(q._cost['usd'],2)} ===")
