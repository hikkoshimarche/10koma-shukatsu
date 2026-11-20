#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room-lint 5種(disclosure/source_or_silence/ng_routing/envelope/r6_safety)を第三者が単独で実行する検証ツール。
★LLM不要・D1読取のみ・書込なし(フリーズ中でも安全)。error 0 が合格。

使い方(1行):  python3 tools/room_lint_check.py <slug>          # 例: kepco / iwatani / tokyo-gas
全28社まとめ:  for s in $(cat tools/_infra28.txt); do python3 tools/room_lint_check.py $s; done

入力(すべて本番D1・companies.jsonから自動取得。手で用意するものは無い):
  - personas.system_prompt       … 各人格のsystem prompt(検査対象本文)  [D1 personas]
  - room_personas.fact_pack_json … source_or_silence/envelope が参照するfactpack [D1 room_personas]
  - role_meta                     … roles_for_company(companies.jsonの18キー→archetype)。'ob'フラグで r6_safety を退職者OB(R7)に適用
     public/companies.json / tools/room_industry_roles_v3.py / ~/oscar-ai/tokyari-pipeline/scripts/room_lib.py

出力: role別に各lintのerror、合計 total_error。exit code = (total>0)?1:0。
"""
import sys, os, json, subprocess
from pathlib import Path
REPO = Path("/Users/oscardodds/projects/10koma-shukatsu"); API = REPO/"api"
sys.path.insert(0, str(REPO/"tools"))
sys.path.insert(0, os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts"))
import room_lib as RL                     # noqa: E402  (run_room_lints・5lint本体・LLM不使用)
import room_industry_roles_v3 as V3       # noqa: E402  (roles_for_company: role_meta/'ob')

def d1(sql):
    """本番D1読取(cwd=api・config自動検出=wrangler.toml)。空/失敗は例外(0=合格に流さない)。"""
    p = subprocess.run(["npx","wrangler","d1","execute","10koma-shukatsu-db","--remote","--json","--command",sql],
                       cwd=str(API), capture_output=True, text=True, timeout=120)
    o = p.stdout; i = o.find("[")
    if i < 0:
        raise SystemExit(f"d1 取得失敗(空/エラー rc={p.returncode}): {p.stderr[-200:]}")
    return json.loads(o[i:])[0]["results"]

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 tools/room_lint_check.py <slug>")
    slug = sys.argv[1]
    ps = d1(f"SELECT role_code, system_prompt FROM personas WHERE company_id='{slug}' AND is_active=1 ORDER BY role_code")
    if not ps:
        raise SystemExit(f"personas 0件(取得失敗の可能性): {slug}")   # 空を合格に流さない
    prompts = {r["role_code"]: r["system_prompt"] for r in ps}
    fp = d1(f"SELECT fact_pack_json FROM room_personas WHERE company_slug='{slug}' AND fact_pack_json IS NOT NULL LIMIT 1")
    factpack = json.loads(fp[0]["fact_pack_json"]) if fp else {}
    comp = json.load(open(REPO/"public/companies.json"))
    id2ind = {c["id"]: k for k, a in comp.items() for c in a}
    roster = V3.roles_for_company(slug, id2ind.get(slug, ""))
    role_meta = {r["role_key"]: r for r in roster}                    # 'ob'フラグ入り(退職者OB=R7にr6_safety)
    report, total = RL.run_room_lints(prompts, factpack, role_meta=role_meta)
    print(f"=== room-lint {slug}: total_error={total} (personas {len(prompts)}人・factpack {'有' if factpack else '無'}) ===")
    for role in sorted(report):
        errs = report[role]
        print(f"  {role}: {'OK' if not errs else errs}")
    print("PASS" if total == 0 else "FAIL")
    sys.exit(1 if total else 0)

if __name__ == "__main__":
    main()
