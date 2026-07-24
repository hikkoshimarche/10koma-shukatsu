#!/usr/bin/env python3
"""夜間第3便: 新規社のcorpus増強(render_official_pages強化版で追加クロール・skip-cached)。checkpoint resumable。"""
import json,os,subprocess,sys,datetime
OUT=os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
PIPE=os.path.expanduser("~/oscar-ai/tokyari-pipeline")
VENV=os.path.join(PIPE,".venv/bin/python")
targets=json.load(open('/tmp/enrich_targets.json'))
stp="/tmp/enrich_state.json"
st=json.load(open(stp)) if os.path.exists(stp) else {"done":[],"pages":{}}
def log(m): print(f"[{datetime.datetime.now():%H:%M:%S}] {m}",flush=True)
log(f"corpus増強 開始/再開: 対象{len(targets)} 完了{len(st['done'])}")
for i,slug in enumerate(targets):
    if slug in st["done"]: continue
    try:
        subprocess.run([VENV,"scripts/render_official_pages.py",slug],cwd=PIPE,capture_output=True,text=True,timeout=400)
        cf=os.path.join(OUT,slug,"rendered_corpus.json")
        n=len(json.load(open(cf))) if os.path.exists(cf) else 0
        st["pages"][slug]=n; st["done"].append(slug)
        log(f"  {slug} 累計{n}頁 [{i+1}/{len(targets)}]")
    except Exception as e:
        st["done"].append(slug); log(f"  {slug} ERR {str(e)[:50]}")
    if (i+1)%5==0: json.dump(st,open(stp,"w"),ensure_ascii=False)
json.dump(st,open(stp,"w"),ensure_ascii=False)
tot=sum(st["pages"].values())
log(f"ENRICH_DONE: {len(st['done'])}社 総{tot}頁 平均{tot//max(1,len(st['pages']))}頁")
