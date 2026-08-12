#!/usr/bin/env python3
"""相性診断の回帰テスト・ランナー。tools/shindan_test_personas.json の固定5入力を本番/任意APIへ投げ、
首位社・score・matched件数・low_signal・軸別一致度を出す。全タブが同一入力で再測定するための共有ハーネス。

使い方:
  python3 tools/shindan_test.py                       # 本番APIへ5ペルソナ
  python3 tools/shindan_test.py <API_BASE>            # 任意のAPIベースへ
  python3 tools/shindan_test.py --json                # 生JSONも出力(突き合わせ用)
"""
import sys, os, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PERSONAS = os.path.join(HERE, "shindan_test_personas.json")
BASE = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
RAW = "--json" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if args:
    BASE = args[0]


def post(answers):
    body = json.dumps({"answers": answers})
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST",
                        f"{BASE}/api/shindan", "-H", "Content-Type: application/json",
                        "-d", body], capture_output=True, text=True)
    return json.loads(p.stdout)


def main():
    cfg = json.load(open(PERSONAS, encoding="utf-8"))
    print(f"### BASE={BASE} / personas={PERSONAS} ###")
    tops = []
    for p in cfg["personas"]:
        d = post(p["answers"])
        comps = d.get("top_companies", [])
        if not comps:
            print(f"[{p['id']}] top_companies空!"); continue
        c0 = comps[0]
        sc = c0.get("score")
        rat = c0.get("rationale") or {}
        matched = rat.get("matched", []); axes = rat.get("axes", [])
        tops.append((p["id"], c0["name"], sc))
        print(f"[{p['id']}] {p['intent'][:22]:22s} 首位={c0['name']}({c0.get('industry')}) "
              f"score={sc} low_signal={c0.get('low_signal')} matched={len(matched)} axes={len(axes)}")
        if RAW:
            print("     top3:", [(x['name'], x['score']) for x in comps[:3]])
            print("     matched:", matched)
    scores = [s for _, _, s in tops if isinstance(s, (int, float))]
    print(f"--- 首位ユニーク={len(set(n for _,n,_ in tops))}/{len(tops)}  "
          f"scoreユニーク={len(set(round(s,3) for s in scores))}/{len(scores)}  "
          f"0%固定={sum(1 for s in scores if s==0)}  100%固定={sum(1 for s in scores if s==1.0)} ---")


if __name__ == "__main__":
    main()
