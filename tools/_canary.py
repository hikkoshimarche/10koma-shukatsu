#!/usr/bin/env python3
"""Per-company canary hash of prod D1 (companies row + all panels).
Usage:
  python3 tools/_canary.py snapshot <out.json>      # capture {company_id: sha}
  python3 tools/_canary.py diff <before.json> <after.json>   # report drift
Any company whose hash changes (or appears/disappears) is reported.
"""
import sys, json, hashlib
sys.path.insert(0, __file__.rsplit('/',1)[0])
from _d1 import d1

CFIELDS = ["id","name","industry_id","description","thumbnail_url","video_url",
           "source_urls","factsheet_url","verification_status"]
PFIELDS = ["panel_num","image_url","character","dialogue","main_copy","sub_copy",
           "source_url","script_json","visual_hook","brand_object_json"]

def snapshot():
    comps = d1("SELECT " + ",".join(CFIELDS) + " FROM companies")
    panels = d1("SELECT company_id," + ",".join(PFIELDS) +
                " FROM company_panels ORDER BY company_id, panel_num")
    bycid = {}
    for p in panels:
        bycid.setdefault(p["company_id"], []).append(p)
    out = {}
    for c in comps:
        cid = c["id"]
        h = hashlib.sha256()
        h.update(json.dumps([c.get(f) for f in CFIELDS], ensure_ascii=False, sort_keys=True).encode())
        for p in bycid.get(cid, []):
            h.update(json.dumps([p.get(f) for f in PFIELDS], ensure_ascii=False, sort_keys=True).encode())
        out[cid] = {"sha": h.hexdigest(), "panels": len(bycid.get(cid, []))}
    return out

def main():
    if sys.argv[1] == "snapshot":
        snap = snapshot()
        json.dump(snap, open(sys.argv[2], "w"), ensure_ascii=False, indent=0)
        print(f"snapshot: {len(snap)} companies -> {sys.argv[2]}")
    elif sys.argv[1] == "diff":
        b = json.load(open(sys.argv[2])); a = json.load(open(sys.argv[3]))
        removed = sorted(set(b) - set(a))
        added = sorted(set(a) - set(b))
        changed = sorted([k for k in (set(a) & set(b)) if a[k] != b[k]])
        print(f"before={len(b)} after={len(a)} removed={len(removed)} added={len(added)} changed={len(changed)}")
        if removed: print("REMOVED:", removed)
        if added:   print("ADDED:", added)
        if changed: print("CHANGED:", changed)
        # drift = changes among companies present in both (should be zero)
        return 0 if not changed and not added else 1

if __name__ == "__main__":
    sys.exit(main() or 0)
