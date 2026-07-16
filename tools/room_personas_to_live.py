#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_personas_to_live.py — room_personas(v3 staging) → personas(ライブAPI) 一括写像同期。
registered-v3 の全社(三井mitsui-bussanは除外=GOLDのmitsui_corpに触れない)を personas へ。冪等(INSERT OR REPLACE
+孤児DELETE)。写像はastroscaleパイロットと同一。氏名衝突(姓/フルネーム)を検出して隔離候補として報告。
使い方: room_personas_to_live.py [--all | --new-only | --slug X] [--dry]
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
ROOT = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline"))
sys.path.insert(0, os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts")); sys.path.insert(0, str(REPO / "tools"))
import room_industry_roles_v3 as V3
WCONF = REPO / "api" / "wrangler.toml"


def wj(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--json", "--command", sql], cwd=str(REPO), capture_output=True, text=True, timeout=120)
    try:
        return json.loads(p.stdout[p.stdout.find("["):])[0]["results"]
    except Exception:
        return []


def wx(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--command", sql], cwd=str(REPO), capture_output=True, text=True, timeout=120)
    return p.returncode == 0, p.stderr[:160]


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def sync_one(slug, ind, dry=False):
    roster = {r["role_key"]: r for r in V3.roles_for_company(slug, ind)}
    rows = wj(f"SELECT role, persona_name, system_prompt FROM room_personas WHERE company_slug='{slug}' ORDER BY role")
    if not rows:
        return {"slug": slug, "n": 0, "ok": False, "note": "room_personas無"}
    stmts, new_ids, names = [], [], []
    for x in rows:
        role = x["role"]; rd = roster.get(role, {})
        pid = f"{slug}_{role.lower()}"; new_ids.append(pid); names.append(x["persona_name"])
        cols = {"persona_id": pid, "company_id": slug, "role_code": role, "display_name": x["persona_name"],
                "display_name_kana": None, "age": None, "department": None, "position": rd.get("label", role),
                "short_description": (rd.get("gist", "")[:78] or None), "image_url": None,
                "system_prompt": x["system_prompt"], "voice_config": None, "is_active": 1}
        stmts.append(f"INSERT OR REPLACE INTO personas ({','.join(cols)}) VALUES ({','.join(q(v) for v in cols.values())})")
    stmts.append(f"DELETE FROM personas WHERE company_id={q(slug)} AND persona_id NOT IN ({','.join(q(i) for i in new_ids)})")
    ok = True
    if not dry:
        ok, err = wx(";\n".join(stmts))
    surn = [n.split()[0] for n in names if n]
    full = names
    return {"slug": slug, "n": len(rows), "ok": ok,
            "surname_collision": sorted(s for s, c in Counter(surn).items() if c > 1),
            "fullname_collision": sorted(n for n, c in Counter(full).items() if c > 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--new-only", action="store_true", help="personas未同期のregistered-v3のみ")
    ap.add_argument("--slug")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--set-liff", action="store_true", help="同期後、personas在籍社に room_liff_id を付与(hub室ボタン表示・要pages deploy)")
    args = ap.parse_args()
    ROOM_LIFF_ID = "2010075487-d4TJ2xZc"   # 三井の room LIFF(?company=slug で全社共用)

    cj = json.loads((REPO / "public" / "companies.json").read_text(encoding="utf-8"))
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}
    done = {}
    p = ROOT / "output" / "room_sync_state.csv"
    for r in csv.reader(open(p, encoding="utf-8")):
        if len(r) >= 2:
            done[r[0]] = r[1]
    v3 = [s for s in id2ind if s != "mitsui-bussan" and done.get(s) == "registered-v3"]

    if args.slug:
        targets = [args.slug]
    elif args.new_only:
        live = set(x["company_id"] for x in wj("SELECT DISTINCT company_id FROM personas"))
        targets = [s for s in v3 if s not in live]
    else:
        targets = v3
    print(f"=== room_personas→personas 一括同期: 対象{len(targets)}社 (registered-v3・三井除外){' [DRY]' if args.dry else ''} ===", flush=True)

    ok_n = 0; coll = []
    for i, slug in enumerate(targets):
        r = sync_one(slug, id2ind.get(slug, ""), dry=args.dry)
        if r["ok"] and r["n"]:
            ok_n += 1
        if r.get("surname_collision") or r.get("fullname_collision"):
            coll.append(r)
        if (i + 1) % 25 == 0:
            print(f"  ...{i+1}/{len(targets)} 同期済{ok_n}", flush=True)
    print(f"\n同期成功: {ok_n}/{len(targets)}社")
    print(f"氏名衝突あり(要フルGO前是正): {len(coll)}社")
    for r in coll[:40]:
        print(f"  {r['slug']}: 姓重複{r['surname_collision']} フルネーム重複{r['fullname_collision']}")
    (REPO / "tools" / "_room_name_collisions.json").write_text(json.dumps(coll, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.set_liff and not args.dry:
        # personas在籍社(=ライブAPIで人格が返る社)に room_liff_id を付与 → hub室ボタンが出る。三井(id別)はそのまま。
        live = set(x["company_id"] for x in wj("SELECT DISTINCT company_id FROM personas"))
        cjp = REPO / "public" / "companies.json"
        data = json.loads(cjp.read_text(encoding="utf-8"))
        changed = 0
        for ind, lst in data.items():
            for c in lst:
                if c["id"] in live and c.get("room_liff_id") != ROOM_LIFF_ID and c["id"] != "mitsui-bussan":
                    c["room_liff_id"] = ROOM_LIFF_ID; changed += 1
        if changed:
            cjp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  room_liff_id 付与: {changed}社 (companies.json・要 git push + pages deploy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
