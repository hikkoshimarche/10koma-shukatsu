#!/usr/bin/env python3
import os, json, datetime, urllib.request, urllib.parse, pathlib
SHEET_URL=os.environ["SHEET_WEBAPP_URL"]; SHEET_TOKEN=os.environ["SHEET_API_TOKEN"]; ANTHROPIC_KEY=os.environ["ANTHROPIC_API_KEY"]
REPO=pathlib.Path(__file__).resolve().parents[1]
COMPANY_SLUG={"三菱商事":"mitsubishi-corp","伊藤忠商事":"itochu","住友商事":"sumitomo-corp","丸紅":"marubeni","兼松":"kanematsu","神鋼商事":"shinkokusyoji","岩谷産業":"iwatani","双日":"sojitz","三井物産":"mitsui-bussan","豊田通商":"toyota-tsusho"}
def fetch_attention():
    url=f"{SHEET_URL}?mode=attention&token={urllib.parse.quote(SHEET_TOKEN)}"
    with urllib.request.urlopen(url,timeout=60) as r: return json.loads(r.read().decode())
def read_current(slug):
    p=REPO/"api"/f"migration_v4_{slug}.sql"; return p.read_text(encoding="utf-8") if p.exists() else None
def call_claude(rules,company,cur,fb):
    prompt=("あなたはトーキャリ10コマの校正担当。下記ルールに従い、FBを①バグ・誤り(即修正)と②好み・感想(要オスカー判断)に切り分け、①は現行→新の具体的差替案まで。現行が既にFBを満たすなら『反映済・変更不要』。捏造・出典なき数字禁止。\n\n【ルール】\n"+rules+"\n\n【会社】"+company+"\n\n【現行台本SQL】\n"+cur+"\n\n【FB】\n"+fb+"\n\n出力:\n## "+company+"\n### ①バグ・誤り(即修正案)\n- コマX 現行「…」→ 新「…」(理由)\n### ②好み・感想(要オスカー判断)\n- …")
    body=json.dumps({"model":"claude-sonnet-4-6","max_tokens":2000,"messages":[{"role":"user","content":prompt}]}).encode()
    req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=body,headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r: data=json.loads(r.read().decode())
    return "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
def main():
    rules=(REPO/"tools"/"koma_rules.md").read_text(encoding="utf-8")
    items=[it for it in fetch_attention().get("items",[]) if it.get("content")=="10コマ"]
    today=datetime.date.today().isoformat()
    out=[f"# Phase C 修正案ドラフト {today}","",f"要対応(10コマ): {len(items)}件。これは**提案**です。承認後にMac側で安全手順反映（本番自動反映なし）。",""]
    for it in items:
        company=it.get("company",""); slug=COMPANY_SLUG.get(company)
        if not slug: out+=[f"## {company}","- ⚠️ slug未登録のためスキップ(COMPANY_SLUGに追加要)",""]; continue
        cur=read_current(slug)
        if not cur: out+=[f"## {company} ({slug})",f"- ⚠️ api/migration_v4_{slug}.sql が無くスキップ",""]; continue
        out+=[call_claude(rules,company,cur,it.get("fb","")),""]
    d=REPO/"proposals"; d.mkdir(exist_ok=True)
    (d/f"phase_c_{today}.md").write_text("\n".join(out),encoding="utf-8")
    print(f"wrote proposals/phase_c_{today}.md ({len(items)} items)")
if __name__=="__main__": main()
