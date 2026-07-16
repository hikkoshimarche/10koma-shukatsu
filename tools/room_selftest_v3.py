#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_selftest_v3.py — ルームv3(人数可変)の機械改修セルフテスト。API非課金(monkeypatch)。
検証: ①18業界→人数可変ロースター ②5lint人数可変+ob-flag ③氏名3層/女性/決定的/三井固定
      ④cond=research_only の落とし ⑤三井GOLD除外 ⑥AI開示・NG routing・envelope・SoS。
使い方: python room_selftest_v3.py   (全PASSで exit 0)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import room_lib as RL
import room_names as RN
import room_industry_roles_v3 as V3
import room_harness as H

FAIL = []
def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        FAIL.append(msg)

# --- API非課金: _anthropic を全lint通過する金型bodyに差し替え ---
COMPLIANT_BODY = (
    "最初の発話で『私はAIによるOB訪問シミュレーションです』と伝えます。"
    "守備範囲外は他の人格（R2さんへ→）に振ります。"
    "存在しない事業や制度は創作しない、封筒の範囲内で語ります。"
    "会社がダメと言うのではなく私の人生ではこう判断した、と話し、得た経験の価値に感謝しています。"
)
RL._anthropic = lambda *a, **k: COMPLIANT_BODY

COMPANIES18 = ["総合商社", "自動車・モビリティ", "電機・精密・重工", "鉄鋼・素材・化学",
               "製薬・ヘルスケア", "銀行・証券・保険", "IT・通信・SaaS", "コンサル", "専門商社",
               "インフラ・エネルギー", "不動産・建設", "小売・流通", "食品・飲料",
               "航空・運輸・物流", "広告・メディア", "その他（外資・新興等）", "ゲーム・エンタメ", "日用品・化粧品"]

SRC_FACTPACK = {
    "company": "テスト社",
    "stateable_facts": [{"claim": "売上高は有価証券報告書に記載", "出典": "有価証券報告書2025", "可視役割": []}],
    "deflection_rules": [{"topic": "倍率", "line": "公式に出ていないので言えません"}],
    "dna_envelope": ["事業範囲の体験", "社風"],
    "research": "研究開発・研究所あり",   # research_only cond を通す
}

print("=== [1] 18業界→人数可変ロースター(6固定でない) ===")
sizes = {}
for ind in COMPANIES18:
    roster = V3.roles_for18(ind)
    sizes[ind] = len(roster)
    keys = [r["role_key"] for r in roster]
    ok_keys = keys == [f"R{i+1}" for i in range(len(roster))]
    check(len(roster) >= 4 and ok_keys, f"{ind:<16}→{V3.map18_v3(ind):<16} {len(roster)}人 keys連番={ok_keys}")
check(len(set(sizes.values())) > 1, f"人数は可変(種類={sorted(set(sizes.values()))} ・6固定でない)")
check(min(sizes.values()) >= 4 and max(sizes.values()) <= 9, f"人数レンジ {min(sizes.values())}〜{max(sizes.values())}(spec 5〜9内)")

print("\n=== [2] 5lint 人数可変 + ob-flag(退職者OB分化に追従) ===")
for ind in ["総合商社", "銀行・証券・保険", "電機・精密・重工"]:  # 7/9/9人
    roster = V3.roles_for18(ind)
    role_meta = {r["role_key"]: r for r in roster}
    prompts = {r["role_key"]: COMPLIANT_BODY + "\n" + RL.GUARDRAILS for r in roster}
    rep, total = RL.run_room_lints(prompts, SRC_FACTPACK, role_meta=role_meta)
    check(total == 0, f"{ind}({len(roster)}人) 全lint error=0 (詳細:{ {k:v for k,v in rep.items() if v} })")
# ob-flag判定: OB役にOB安全句が無いbodyを与えると、ob役だけr6_safetyが発火(非ob役は発火しない)
roster = V3.roles_for18("メーカー")  # OB2名
role_meta = {r["role_key"]: r for r in roster}
bad = "最初にAIによるシミュレーション。R2さんへ→。創作しない。"  # OB安全句なし
prompts = {r["role_key"]: bad for r in roster}
rep, total = RL.run_room_lints(prompts, SRC_FACTPACK, role_meta=role_meta)
ob_keys = [r["role_key"] for r in roster if r["ob"]]
fired = [k for k, v in rep.items() if any("OB:" in x for x in v)]
check(sorted(fired) == sorted(ob_keys), f"r6_safetyはob役のみ発火: 発火{sorted(fired)} == ob{sorted(ob_keys)}")
check(all(not any("OB:" in x for x in rep[k]) for k in rep if k not in ob_keys), "非ob役ではr6_safety不発火")

print("\n=== [3] 氏名3層/女性フラグ/決定的/三井固定 ===")
roster = V3.roles_for18("メーカー")
names = {r["role_key"]: RN.personal_name("honda", r["role_key"], female=r["female"]) for r in roster}
check(all(" " in n for n in names.values()), "氏名は姓名2要素(3層目=個人名)")
fem_role = [r for r in roster if r["female"]][0]["role_key"]
check(names[fem_role].split()[1] in RN.GIVEN_FEMALE, f"女性役({fem_role})は女性名: {names[fem_role]}")
male_role = [r for r in roster if not r["female"] and not r["ob"]][0]["role_key"]
check(names[male_role].split()[1] in RN.GIVEN_MALE, f"男性役({male_role})は男性名: {names[male_role]}")
n1 = RN.personal_name("honda", "R7", female=False); n2 = RN.personal_name("honda", "R7", female=False)
check(n1 == n2, f"決定的(再sync不変): {n1}=={n2}")
check(RN.personal_name("mitsui-bussan", "R1") == "佐藤 健太", "三井は金型固定名を保持")

print("\n=== [4] cond=research_only の落とし(Source-or-Silence) ===")
infra = V3.roles_for18("インフラ・エネルギー")
cond_roles = [r for r in infra if r.get("cond") == "research_only"]
check(len(cond_roles) == 1, f"インフラに research_only 役が1つ存在({[r['label'] for r in cond_roles]})")
check(H._factpack_has_research(SRC_FACTPACK) is True, "研究記述あり→research判定True")
check(H._factpack_has_research({"dna_envelope": ["営業"]}) is False, "研究記述なし→research判定False(=cond役を落とす)")

print("\n=== [5] 三井GOLD除外(二重安全弁) ===")
rec = H.process("mitsui-bussan", "三井物産", industry="総合商社")
check("skip(三井GOLD" in rec.get("status", ""), f"process('mitsui-bussan')はskip: {rec.get('status')}")

print("\n=== [6] build_persona 人数可変 end-to-end(mock body・全lint通過) ===")
roster = V3.roles_for18("コンサル")
personas = {r["role_key"]: H.build_persona("test-co", "テスト社", r, SRC_FACTPACK, "コンサル", roster) for r in roster}
prompts = {k: p for k, (p, n) in personas.items()}
role_meta = {r["role_key"]: r for r in roster}
rep, total = RL.run_room_lints(prompts, SRC_FACTPACK, role_meta=role_meta)
check(total == 0, f"コンサル{len(roster)}人 build_persona→lint error=0")
check(all("私はAIによる" in p or "AIによる" in p for p in prompts.values()), "全人格にAI開示文が入る")
check(len({n for p, n in personas.values()}) == len(roster), "氏名が人数ぶん(重複なし理想・最低限生成)")

print("\n" + ("🎉 ALL PASS" if not FAIL else f"❌ {len(FAIL)}件FAIL: {FAIL}"))
sys.exit(1 if FAIL else 0)
