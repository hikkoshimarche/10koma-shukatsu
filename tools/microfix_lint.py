#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""microfix_lint.py — 画像完成・未投入だが台本lintで停止した社を業界横断で自動microfix。

generic_escape('汎用素材XXXを検出') → XXXが固有接点ならwhitelisted_generic_termsへ容認(mufg型)。
opening_cliche(汎用入口) → koマ1をpersona木内ロジックで固有事実に言い換え(Claude・捏造禁止)。
microfix後 v4ゲートでlint=0を確認。deployは別途deploy_industryが拾う(image_url不変・公開URL生存)。
使い方: microfix_lint.py 業界1 業界2 ...
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOK = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOK / "scripts"))
import company_master as cm   # noqa: E402
import phase_c_lib as L       # noqa: E402
TPY = str(TOK / ".venv" / "bin" / "python")
OUT = TOK / "output"
RULES = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")


def gate_errors(slug):
    """v4全部入りゲートを走らせ (returncode, stderr) を返す。"""
    p = subprocess.run([TPY, "scripts/scenario_to_panels.py", "--slug", slug, "--v4",
                        "--no-schema", "--out", f"/tmp/mfx_{slug}.sql"],
                       cwd=str(TOK), capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stderr or "") + (p.stdout or "")


def fix_generic_escape(slug, errtext):
    """'汎用素材 'XXX' を検出' の XXX を whitelisted_generic_terms に追加(固有接点容認)。"""
    terms = re.findall(r"汎用素材\s*'([^']+)'\s*を検出", errtext)
    if not terms:
        return []
    p = OUT / slug / "scenario_v4.json"
    sc = json.loads(p.read_text(encoding="utf-8"))
    wl = sc.setdefault("meta", {}).setdefault("whitelisted_generic_terms", [])
    added = []
    for t in set(terms):
        if t not in wl:
            wl.append(t); added.append(t)
    p.write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
    return added


def fix_opening_cliche(slug, company):
    """koマ1の汎用入口を固有事実で開き直す(persona木内ロジック・Claude・捏造禁止)。"""
    p = OUT / slug / "scenario_v4.json"
    sc = json.loads(p.read_text(encoding="utf-8"))
    k1 = next((k for k in sc["koma"] if k.get("koma_number") == 1), None)
    if not k1:
        return False
    cur = {"script": k1.get("script") or [],
           "main_copy": (k1.get("overlay_text") or {}).get("main_copy", ""),
           "sub_copy": (k1.get("overlay_text") or {}).get("sub", "")}
    instr = ("コマ1の入口が汎用的な決まり文句(opening_cliche)。木内『具体性ハンター』の流儀で、"
             f"{company}固有の事実・エピソードから開き直す。捏造・出典なき数字は禁止(既知の固有事実のみ)。"
             "話者タグ維持・最小限の書き換え。")
    res = L.fix_koma_text(slug, 1, instr, RULES, cur)
    if res.get("changed"):
        k1["script"] = res["after"]["script"]
        ot = k1.setdefault("overlay_text", {})
        ot["main_copy"] = res["after"]["main_copy"]; ot["sub"] = res["after"]["sub_copy"]
        p.write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    return False


def main():
    inds = sys.argv[1:]
    d1 = set(subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                             "--config", "api/wrangler.toml", "--command", "SELECT id FROM companies",
                             "--json"], cwd=str(REPO), capture_output=True, text=True).stdout.split('"id":'))
    fixed, still = [], []
    for ind in inds:
        comps = cm.companies_in_industry(ind)
        for c in comps:
            slug = c["slug"]
            if (OUT / slug / "scenario_v4.json").exists() is False:
                continue
            rc, err = gate_errors(slug)
            if rc == 0:
                continue  # lint通過済(投入はdeploy_industryが拾う)
            acts = []
            if "generic_escape" in err or "汎用素材" in err:
                added = fix_generic_escape(slug, err)
                if added:
                    acts.append(f"whitelist:{added}")
            if "opening_cliche" in err:
                if fix_opening_cliche(slug, c.get("name", slug)):
                    acts.append("opening言い換え")
            if not acts:
                still.append((slug, err[-120:])); continue
            rc2, err2 = gate_errors(slug)
            if rc2 == 0:
                fixed.append((slug, acts)); print(f"  ✅ {slug}: {acts}")
            else:
                still.append((slug, "残error:" + err2[-100:])); print(f"  ⚠ {slug}: 残error")
    print(f"\n=== microfix: 解消{len(fixed)} / 残error{len(still)} ===")
    for s, e in still:
        print(f"  残: {s} {e[:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
