#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_sync_personas_pilot.py — room_personas(v3 staging) → personas(ライブAPI) 写像同期。
パイロット1社(既定 astroscale-hd)のみ。三井GOLD(mitsui_corp)には一切触れない(persona_id空間が別=衝突不能)。
冪等: INSERT OR REPLACE (persona_id=<slug>_<role小文字> で再実行しても重複行を作らない)。
写像: role→role_code / persona_name→display_name / v3 role.label→position / v3 role.gist→short_description /
      system_prompt→system_prompt。room_personasに無い列(kana/age/department/image_url/voice_config)は NULL(=欠損を明示)。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
sys.path.insert(0, os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts")); sys.path.insert(0, str(REPO / "tools"))
import room_industry_roles_v3 as V3

WCONF = REPO / "api" / "wrangler.toml"
SLUG = sys.argv[1] if len(sys.argv) > 1 else "astroscale-hd"
IND = "その他（外資・新興等）"
COMPANY_ID = SLUG   # ライブAPI /api/room/personas/<company_id> で叩くid = slug


def wj(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--json", "--command", sql], cwd=str(REPO), capture_output=True, text=True, timeout=90)
    return json.loads(p.stdout[p.stdout.find("["):])[0]["results"]


def wx(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", str(WCONF),
                        "--command", sql], cwd=str(REPO), capture_output=True, text=True, timeout=90)
    return p.returncode == 0, p.stderr[:150]


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


roster = {r["role_key"]: r for r in V3.roles_for_company(SLUG, IND)}
rows = wj(f"SELECT role, persona_name, system_prompt FROM room_personas WHERE company_slug='{SLUG}' ORDER BY role")
print(f"=== {SLUG}: room_personas {len(rows)}人格 → personas 写像同期 ===")
print(f"  アーキタイプ: {V3.archetype_for(SLUG, IND)} / company_id(ライブ): {COMPANY_ID}")

filled, empty_cols = {}, set()
for x in rows:
    role = x["role"]
    rd = roster.get(role, {})
    label = rd.get("label", role)
    gist = rd.get("gist", "")
    cols = {
        "persona_id": f"{SLUG}_{role.lower()}",   # 決定的=冪等(再実行で同一行をREPLACE)
        "company_id": COMPANY_ID,
        "role_code": role,
        "display_name": x["persona_name"],        # 氏名3層の個人名
        "display_name_kana": None,                # 欠損: room_personasにkanaなし
        "age": None,                              # 欠損: 年齢なし
        "department": None,                        # 欠損: 部署なし
        "position": label,                        # v3役割ラベル(例 修士新卒の若手)
        "short_description": (gist[:78] if gist else None),  # v3 gist(役割の語ること)
        "image_url": None,                        # 欠損: アバター画像なし(★実害候補)
        "system_prompt": x["system_prompt"],      # v3人格本文(AI開示/SoS/人格差入り)
        "voice_config": None,                     # 欠損: 音声設定なし(★実害候補)
        "is_active": 1,
    }
    for k, v in cols.items():
        if v is None:
            empty_cols.add(k)
    collist = ",".join(cols.keys())
    vallist = ",".join(q(v) for v in cols.values())
    ok, err = wx(f"INSERT OR REPLACE INTO personas ({collist}) VALUES ({vallist})")
    print(f"  {'✅' if ok else '❌'} {role} {x['persona_name']} → persona_id={cols['persona_id']} pos={label}" + ("" if ok else f" ERR:{err}"))
    filled[role] = cols

print(f"\n  写像で埋めた列: persona_id/company_id/role_code/display_name/position/short_description/system_prompt/is_active")
print(f"  NULL(欠損)列: {sorted(empty_cols)}")
