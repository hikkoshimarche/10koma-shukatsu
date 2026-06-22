#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""close_shosha_fb.py — 商社FB3を本番D1へ安全反映(D1ライブ基準=旧FB巻き戻し防止)。

5社auto反映(三菱/住友/丸紅/双日/神鋼)+三井koマ05のみ。各社:
  D1から現台本読込 → Claudeで該当koマを最小修正(FB指示) → v5_ext error0ゲート →
  台本列UPDATE(image_url不変) → 一般化canary(反映前に存在した対象外社のみbefore/after比較
  =wave新規INSERT誤検知なし) → 検証(200) → setreflected(三井除く)。
backup・可逆。D1書込のみ(wave画像生成は別レーン継続)。
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path.home() / "oscar-ai" / "tokyari-pipeline" / "scripts"))
import phase_c_lib as L      # noqa: E402
import deploy_salary as D    # noqa: E402
import scenario_lints_v5_ext as v5  # noqa: E402

ENV = REPO / "tools" / ".env.phase_c"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
GAS_URL = os.environ["SHEET_WEBAPP_URL"].strip()
GAS_TOKEN = os.environ["SHEET_API_TOKEN"].strip()
RULES = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")

# 社名(setreflected用) と koマ別FB指示
TARGETS = {
    "mitsubishi-corp": {"name": "三菱商事", "reflect": True, "fixes": {
        1: "「それは三菱が丸の内で150年前から続いてる…見方変わるかも」が意味不明。三菱の歴史と丸の内の繋がりが自然に伝わる会話にリライト。",
        4: "「今は三菱食品とローソンで日本の食卓を支えてる」だと食品専業の印象。食品はあくまで一事業の例と分かる表現に。",
        10: "「数字じゃわからないのが、この会社の選び方だよ」の意味が不明瞭。会社選びの軸が伝わる自然な表現にリライト。"}},
    "sumitomo-corp": {"name": "住友商事", "reflect": True, "fixes": {
        3: "「実家のリモコン、これ、ずっと住友商事だったの!?」→「住友商事がかかわっているの？」の趣旨で自然な日本語に。",
        5: "「額じゃなくて、続けることでリターンが育つ仕組みなんだ」→「一時の利益じゃなくて、続けることでリターンが育つ仕組み」の趣旨で自然に。"}},
    "marubeni": {"name": "丸紅", "reflect": True, "fixes": {
        9: "「シカゴで小麦トレーディングをドル建てで動かしてる」のドル建てが分かりにくい。平易に分かりやすくリライト。"}},
    "sojitz": {"name": "双日", "reflect": True, "fixes": {
        1: "「だから、10年後の双日を作るのは、まだ誰も決めていない」→「まだ決まっていない」の趣旨で自然な表現にリライト。"}},
    "shinkokusyoji": {"name": "神鋼商事", "reflect": True, "fixes": {
        8: "「別の5大商社ならではの『総合』とは違う、神戸製鋼一本での『深さ』」の『別の』が不要で不自然。自然な表現に調整。"}},
    # 三井: koマ05のみ scenario_v4.json の承認版で反映(Claude不使用)。setreflectしない。
    "mitsui-bussan": {"name": "三井物産", "reflect": False, "koma05_from_scenario": True},
}


def gas(params):
    return requests.get(GAS_URL, params={**params, "token": GAS_TOKEN}, timeout=60).json()


def d1_panels(slug):
    return D.d1_query("SELECT panel_num,dialogue,script_json,main_copy,sub_copy "
                      f"FROM company_panels WHERE company_id='{slug}' ORDER BY panel_num")


def build_scenario(slug, panels, overrides=None):
    overrides = overrides or {}
    koma = []
    for r in panels:
        kn = r["panel_num"]
        ov = overrides.get(kn)
        if ov:
            script = ov["script"]; mc = ov["main_copy"]; sub = ov["sub_copy"]
        else:
            try:
                script = json.loads(r.get("script_json") or "[]")
            except Exception:
                script = [x for x in (r.get("dialogue") or "").split("\n") if x.strip()]
            mc = r.get("main_copy") or ""; sub = r.get("sub_copy") or ""
        koma.append({"koma_number": kn, "script": script,
                     "overlay_text": {"main_copy": mc, "sub": sub}})
    return {"meta": {"slug": slug}, "koma": koma}


def fix_koma(slug, koma, instruction, current):
    cur_script = current["script"]
    prompt = (f"【ルール】\n{RULES}\n\n【会社】{slug} koマ{koma}\n"
              f"【現行script(JSON配列)】{json.dumps(cur_script, ensure_ascii=False)}\n"
              f"【現行main_copy】{current['main_copy']}\n【現行sub_copy】{current['sub_copy']}\n\n"
              f"【修正指示(インターンFB)】{instruction}\n\n"
              "ルール厳守・最小限の修正。話者タグ([nana]/[haruki]/[OB先輩]等)は維持。"
              "生Markdown禁止/倍率数値禁止/出典なき数字禁止。"
              '出力はJSONのみ: {"script":[...], "main_copy":"...", "sub_copy":"...", "note":"何を直したか"}')
    import re
    txt = L._anthropic(prompt, max_tokens=1500)
    m = re.search(r"\{.*\}", txt, re.S)
    new = json.loads(m.group(0))
    return {"script": new.get("script", cur_script),
            "main_copy": new.get("main_copy", current["main_copy"]),
            "sub_copy": new.get("sub_copy", current["sub_copy"]),
            "note": new.get("note", "")}


def main():
    targets = list(TARGETS)
    print(f"=== 商社FB クローズ {len(targets)}社 (D1ライブ基準) ===\n")

    # 各社の修正案を生成(まだD1書込しない)
    plan = {}   # slug -> {overrides:{koma:after}, notes}
    for slug, cfg in TARGETS.items():
        panels = d1_panels(slug)
        cur = {p["panel_num"]: {"script": json.loads(p.get("script_json") or "[]"),
                                "main_copy": p.get("main_copy") or "", "sub_copy": p.get("sub_copy") or ""}
               for p in panels}
        overrides = {}
        if cfg.get("koma05_from_scenario"):
            sc = json.load(open(Path.home() / "oscar-ai" / "tokyari-pipeline" / "output" / slug / "scenario_v4.json", encoding="utf-8"))
            k5 = next(x for x in sc["koma"] if x.get("koma_number") == 5)
            overrides[5] = {"script": k5["script"],
                            "main_copy": k5["overlay_text"]["main_copy"],
                            "sub_copy": k5["overlay_text"].get("sub", "")}
        else:
            for koma, instr in cfg["fixes"].items():
                after = fix_koma(slug, koma, instr, cur[koma])
                if after["script"] == cur[koma]["script"] and after["main_copy"] == cur[koma]["main_copy"] and after["sub_copy"] == cur[koma]["sub_copy"]:
                    print(f"  {cfg['name']} koマ{koma}: 変更なし(skip)")
                    continue
                overrides[koma] = after
        if not overrides:
            print(f"  {cfg['name']}: 修正なし"); continue
        # v5_ext lint (D1全台本 + override)
        scen = build_scenario(slug, panels, overrides)
        rep = v5.run_ext_lints(scen, slug)
        print(f"  {cfg['name']}: 修正koマ={sorted(overrides)} lint errors={rep['errors']} warnings={rep['warnings']}")
        if rep["errors"] > 0:
            print(f"    ❌ lint error → このsocはskip: {v5.format_report(rep)[:300]}")
            continue
        plan[slug] = {"overrides": overrides, "panels": panels}

    if not plan:
        print("反映対象なし"); return 1

    # canary before (対象社=plan全slug を除外、反映前に存在した対象外社)
    target_slugs = set(plan)
    print(f"\n[canary before] 対象外社snapshot (対象={sorted(target_slugs)})")
    cb = D.canary_snapshot(target_slugs)
    print(f"  反映前 対象外 {len(cb)}社を記録")

    # backup + D1 UPDATE
    print("\n[backup + D1 UPDATE 台本列(image_url不変)]")
    for slug, info in plan.items():
        D.backup_d1(slug)
        for koma, after in info["overrides"].items():
            proc = D.wrangler(["--command", D.update_sql(slug, koma, after)])
            print(f"  {TARGETS[slug]['name']:8} koマ{koma} {'✅' if proc.returncode==0 else '❌ '+proc.stderr[:120]}")

    # canary after (before-keysのみ比較=wave新規INSERT無視)
    ca = D.canary_snapshot(target_slugs)
    changed = [s for s in cb if cb[s] != ca.get(s)]
    print(f"\n[canary after] 反映前存在の対象外 {len(cb)}社中 変化={changed or 'なし'}")
    if changed:
        print("  🛑 対象外が変化 → 異常。setreflectせず手動確認を。"); return 2

    # 検証 + setreflected
    print("\n[検証200 + setreflected]")
    result = {}
    for slug, info in plan.items():
        name = TARGETS[slug]["name"]
        try:
            j = requests.get(f"{D.API_BASE}/api/companies/{slug}", timeout=30).json()
            ok200 = len(j.get("panels", [])) == 10
        except Exception:
            ok200 = False
        reflected = False
        if TARGETS[slug]["reflect"] and ok200:
            r = gas({"mode": "setreflected", "company": name})
            reflected = bool(r.get("ok"))
        result[slug] = {"name": name, "d1": True, "canary_ok": True, "api200": ok200,
                        "reflected": reflected, "komas": sorted(info["overrides"])}
        print(f"  {name:8} 200={ok200} setreflected={reflected if TARGETS[slug]['reflect'] else '—(据置)'}")

    json.dump(result, open(REPO / "tools" / "_close_shosha_result.json", "w"), ensure_ascii=False, indent=2)
    print("\n結果: tools/_close_shosha_result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
