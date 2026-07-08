#!/usr/bin/env python3
"""Minimal D1 query helper for this task session. Read/exec against remote prod.
Usage: python3 tools/_d1.py "SELECT ..."   (prints JSON rows)
Importable: from _d1 import d1(sql) -> list[dict]
"""
import subprocess, json, sys, os

DB = "10koma-shukatsu-db"
CFG = "api/wrangler.toml"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def d1(sql):
    p = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB, "--remote", "--config", CFG, "--json", "--command", sql],
        cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-2000:])
        raise SystemExit(f"D1 error rc={p.returncode}")
    # wrangler --json prints a JSON array of result objects (possibly after log noise)
    txt = p.stdout
    start = txt.find("[")
    data = json.loads(txt[start:])
    # data is list of {results:[...], success:..., meta:...}
    rows = []
    for blk in data:
        rows.extend(blk.get("results", []))
    return rows

if __name__ == "__main__":
    sql = sys.argv[1]
    rows = d1(sql)
    print(json.dumps(rows, ensure_ascii=False, indent=1))
