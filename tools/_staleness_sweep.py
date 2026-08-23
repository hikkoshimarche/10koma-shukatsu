#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""505コマ一括の陳腐化スイープ: 配信中(D1 image_url)画像の症状残存をGemini(flash)で判定。
resolved(確信>=0.7)= 既に直っている= キューから落として良い候補。present= 再生成側に残す。"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, ".")
import phase_c_image_fix as PCI
import phase_c_auto as PA
import phase_c_autoloop as A
import deploy_salary as D
import image_staleness as ST

# 1) pending map(505) + detail
cf_items = PCI.commonfixes_fast().get("items", [])
qa_items = PCI.gas({"mode": "imageqa_list"}).get("items", [])
pmap = PA._pending_image_map(cf_items=cf_items, qa_items=qa_items)
detail_map = {}
for x in cf_items:
    m = re.match(r"\[要画像再生成\]\s*([^:：]+?)[:：]\s*(.*)", str(x.get("rule", "")), re.S)
    if not m:
        continue
    slug = A.resolve_slug(m.group(1).strip())
    if not slug:
        continue
    for km in re.split(r"(?:^|;|；)\s*(?=koma\s*\d+|コマ\s*\d+)", m.group(2)):
        kk = re.search(r"(?:koma|コマ)\s*0*(\d+)\s*[:：]?\s*(.*)", km, re.S)
        if kk:
            detail_map.setdefault((slug, int(kk.group(1))), []).append(kk.group(2).strip())
for it in qa_items:
    if it.get("slug") and it.get("koma") is not None:
        d = it.get("detail") or it.get("note") or ""
        if d:
            detail_map.setdefault((it["slug"], int(it["koma"])), []).append(str(d))

# 2) 全 image_url を1クエリで取得
rows = D.d1_query("SELECT company_id, panel_num, image_url FROM company_panels")
url_map = {(r["company_id"], int(r["panel_num"])): r["image_url"] for r in rows if r.get("image_url")}

# 3) 対象コマ列挙
targets = []
for slug, komas in pmap.items():
    for koma in sorted(komas):
        detail = " / ".join(detail_map.get((slug, koma), [])) or "(詳細本文なし)"
        targets.append((slug, koma, detail, url_map.get((slug, koma))))
print(f"対象 {len(targets)} コマ / image_url有 {sum(1 for t in targets if t[3])}", flush=True)

# 4) 並列で症状判定
def work(t):
    slug, koma, detail, url = t
    if not url:
        return {"slug": slug, "koma": koma, "status": "present", "stale": False,
                "confidence": 0.0, "reason": "D1 image_url無し→残す", "detail": detail[:80]}
    try:
        b = ST._fetch(url)
        s = ST.symptom_status(b, detail)
    except Exception as e:
        s = {"status": "present", "confidence": 0.0, "reason": f"err:{type(e).__name__}"}
    stale = (s["status"] == "resolved" and s["confidence"] >= ST.RESOLVED_MIN_CONF)
    return {"slug": slug, "koma": koma, "status": s["status"], "stale": stale,
            "confidence": s["confidence"], "reason": s.get("reason", ""), "detail": detail[:80]}

results = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for i, r in enumerate(ex.map(work, targets), 1):
        results.append(r)
        if i % 25 == 0:
            print(f"  ...{i}/{len(targets)}", flush=True)
            json.dump({"partial": True, "done": i, "total": len(targets), "results": results},
                      open("_staleness_sweep.json", "w", encoding="utf-8"), ensure_ascii=False)

stale = [r for r in results if r["stale"]]
present = [r for r in results if not r["stale"]]
print(f"\n=== 陳腐化スイープ結果 (505コマ) ===")
print(f"  陳腐化(resolved・落として良い): {len(stale)} コマ / {len(set(r['slug'] for r in stale))} 社")
print(f"  症状残存(present・再生成へ):    {len(present)} コマ / {len(set(r['slug'] for r in present))} 社")
json.dump({"total": len(results), "stale": len(stale), "present": len(present),
           "stale_rows": stale, "results": results},
          open("_staleness_sweep.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("詳細 → _staleness_sweep.json")
print("\n陳腐化の例(先頭15):")
for r in stale[:15]:
    print(f"  {r['slug']}#{r['koma']}: {r['reason'][:60]}")
