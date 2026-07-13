#!/usr/bin/env python3
"""Minimal D1 query helper for this task session. Read/exec against remote prod.
Usage: python3 tools/_d1.py "SELECT ..."   (prints JSON rows)
Importable: from _d1 import d1(sql) -> list[dict]
"""
import subprocess, json, sys, os

DB = "10koma-shukatsu-db"
CFG = "api/wrangler.toml"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _parse(p):
    """成功判定は stdout の JSON結果で行う(exit code/stderr の macOS互換警告ノイズは無視)。"""
    txt = p.stdout or ""
    start = txt.find("[")
    if start == -1:
        return None
    try:
        data = json.loads(txt[start:])
    except Exception:
        return None
    if not isinstance(data, list):
        return None
    rows = []
    for blk in data:
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows

def d1(sql, retries=2):
    import time
    last = None
    for attempt in range(retries + 1):
        p = subprocess.run(
            ["npx", "wrangler", "d1", "execute", DB, "--remote", "--config", CFG, "--json", "--command", sql],
            cwd=ROOT, capture_output=True, text=True)
        rows = _parse(p)
        if rows is not None:
            return rows
        last = p
        if attempt < retries:
            time.sleep(1.5)
    sys.stderr.write((last.stderr or "")[-1000:])
    raise SystemExit(f"D1 error rc={last.returncode}: stdout={(last.stdout or '')[-200:]!r}")

if __name__ == "__main__":
    sql = sys.argv[1]
    rows = d1(sql)
    print(json.dumps(rows, ensure_ascii=False, indent=1))
