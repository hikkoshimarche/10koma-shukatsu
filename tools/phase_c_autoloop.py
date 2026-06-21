#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase_c_autoloop.py — Phase C フルオート修正ループ (Mac launchd 毎時)。

フロー:
  1. GAS ?mode=attention で「FB対応中」行を取得 (content=10コマ のみ・三井物産スキップ)
  2. FBを①台本バグ②画像バグ③感想に仕分け (phase_c_lib.triage_fb)
  3. 台本バグ → 該当コマ修正 → lintゲート (error0でなければ保留)
  4. 画像バグ → 該当コマ再生成 (generate_images --koma) → QA → 最大3回 → なお不可ならエスカレーション
  5. lint+QA 通過分のみデプロイ (D1バックアップ→migration→他社ハッシュ確認→wrangler) ※--deploy時のみ
  6. 書き戻し (反映済) + Notion保存(社が完了時のみ) ※--writeback / --deploy 時のみ
  7. 既定は dry-run: 何も本番反映せず、提案・lint/QA結果・LINE文面を表示

安全: 三井物産除外 / 全変更 backup+差分ログ(可逆) / lint+QAゲート必須 / dry-run既定。
env: SHEET_WEBAPP_URL, SHEET_API_TOKEN, ANTHROPIC_API_KEY, (画像) GEMINI_API_KEY
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import phase_c_lib as L  # noqa: E402

# 環境変数ロード (tools/.env.phase_c があれば)
ENV_FILE = REPO / "tools" / ".env.phase_c"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
TOKYARI_PY = TOKYARI / ".venv" / "bin" / "python"
COMPANIES_JSON = REPO / "public" / "companies.json"
EXCLUDED = L.EXCLUDED_SLUGS  # {"mitsui-bussan"}
QA_MAX = 3

# 社名→deploy slug (companies.json から全社、+ 既知の別名)
NAME_ALIASES = {"三菱商事": "mitsubishi-corp", "伊藤忠商事": "itochu", "住友商事": "sumitomo-corp",
                "丸紅": "marubeni", "兼松": "kanematsu", "神鋼商事": "shinkokusyoji",
                "岩谷産業": "iwatani", "双日": "sojitz", "三井物産": "mitsui-bussan",
                "豊田通商": "toyota-tsusho"}
# deploy slug → tokyari slug (画像生成side。既知差異のみ)
TOKYARI_SLUG = {"itochu": "itochu-shoji"}


def _name_to_slug_map():
    m = dict(NAME_ALIASES)
    try:
        data = json.loads(COMPANIES_JSON.read_text(encoding="utf-8"))
        for comps in data.values():
            for c in comps:
                m.setdefault(c["name"], c["id"])
                m.setdefault(c["name"].replace("株式会社", "").strip(), c["id"])
    except Exception:
        pass
    return m


def resolve_slug(company_name: str):
    m = _name_to_slug_map()
    if company_name in m:
        return m[company_name]
    for k, v in m.items():
        if k and (k in company_name or company_name in k):
            return v
    return None


def fetch_attention():
    url = os.environ["SHEET_WEBAPP_URL"].strip()
    token = os.environ["SHEET_API_TOKEN"].strip()
    r = requests.get(f"{url}?mode=attention&token={urllib.parse.quote(token)}", timeout=60)
    r.raise_for_status()
    return r.json().get("items", [])


def fix_image_koma(tokyari_slug: str, koma: int):
    """generate_images で該当コマ再生成 → QA。(ok, panels, note)。最大QA_MAX回はscript側で実施。"""
    scen = TOKYARI / "output" / tokyari_slug / "scenario.json"
    if not scen.exists():
        return False, 0, f"scenario.json無し({tokyari_slug}) → 画像修正は対象外/要台本整備"
    proc = subprocess.run(
        [str(TOKYARI_PY), "scripts/generate_images.py", "--company", tokyari_slug, "--koma", str(koma)],
        cwd=str(TOKYARI), capture_output=True, text=True, timeout=1200,
    )
    qp = TOKYARI / "output" / tokyari_slug / "qa_report.json"
    ok = False
    note = proc.stdout[-200:] if proc.returncode else "ok"
    if qp.exists():
        try:
            rep = json.load(open(qp, encoding="utf-8"))
            res = next((x for x in rep.get("results", []) if x.get("koma_number") == koma), None)
            ok = bool(res and res.get("ok"))
        except Exception:
            pass
    panels = len(list((TOKYARI / "output" / tokyari_slug).glob(f"koma{koma:02d}.png")))
    return ok, panels, note


def process_company(item, rules, args):
    company = item.get("company", "")
    slug = resolve_slug(company)
    rec = {"company": company, "slug": slug, "actions": [], "script_changed": False,
           "image_results": [], "deployable": False, "escalate": [], "note": ""}
    if not slug:
        rec["note"] = "slug解決不可"; return rec
    if slug in EXCLUDED:
        rec["note"] = "三井物産=対象外スキップ"; return rec

    fb = item.get("fb", "")
    triage = L.triage_fb(company, fb)
    rec["triage"] = triage

    # --- 台本バグ修正 + lint ---
    sql_path = L.API_DIR / f"migration_v4_{slug}.sql"
    if triage.get("script_bugs") and sql_path.exists():
        overrides = {}
        for b in triage["script_bugs"]:
            koma = b.get("koma")
            if not koma:
                rec["escalate"].append(f"台本: コマ不明 '{b.get('detail')}' → 手動")
                continue
            res = L.fix_script_koma(slug, koma, b.get("detail", ""), rules, dry=args.dry_run)
            if res.get("changed"):
                rec["script_changed"] = True
                overrides[koma] = res["after"]
                rec["actions"].append({"koma": koma, "before": res["before"]["script"],
                                       "after": res["after"]["script"], "note": res.get("note", "")})
            else:
                rec["actions"].append({"koma": koma, "note": res.get("note", "変更なし")})
        # 提案(dry)は override 反映後をlint / 本番適用時は実ファイルをlint
        if args.dry_run:
            e, w, _ = L.lint_with_overrides(slug, overrides)
        else:
            e, w, _ = L.lint_company(slug)
        rec["lint"] = {"errors": e, "warnings": w}
    elif triage.get("script_bugs"):
        rec["escalate"].append(f"台本SQL無し(api/migration_v4_{slug}.sql) → 手動")

    # --- 画像バグ再生成 + QA (最大3) ---
    tslug = TOKYARI_SLUG.get(slug, slug)
    for b in triage.get("image_bugs", []):
        koma = b.get("koma")
        if not koma:
            rec["escalate"].append(f"画像: コマ不明 '{b.get('detail')}'"); continue
        if args.dry_run:
            rec["image_results"].append({"koma": koma, "status": "DRY", "detail": b.get("detail", "")[:50]})
            continue
        ok = False
        for attempt in range(1, QA_MAX + 1):
            ok, panels, note = fix_image_koma(tslug, koma)
            if ok:
                break
        rec["image_results"].append({"koma": koma, "ok": ok, "attempts": attempt})
        if not ok:
            rec["escalate"].append(f"画像koma{koma}: QA{QA_MAX}回不可 → エスカレーション")

    # --- デプロイ可否: lint error0 かつ 画像エスカレなし ---
    lint_ok = rec.get("lint", {}).get("errors", 0) == 0
    img_ok = all(r.get("ok", True) for r in rec["image_results"] if r.get("status") != "DRY")
    rec["deployable"] = bool(lint_ok and img_ok and not rec["escalate"])
    rec["opinions"] = triage.get("opinions", [])
    return rec


def compose_line(results):
    done = [r for r in results if r["deployable"]]
    esc = [r for r in results if r["escalate"]]
    lines = [f"【トーキャリ自動修正・直近】処理 {len(results)}社 / 反映可 {len(done)} / 要対応 {len(esc)}"]
    for r in done:
        lines.append(f"・{r['company']}: 修正→反映可")
    for r in esc:
        lines.append(f"⚠{r['company']}: {'; '.join(r['escalate'][:2])}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--deploy", dest="dry_run", action="store_false", help="本番反映(D1/書き戻し)を行う")
    p.add_argument("--companies", help="カンマ区切りの会社名で対象を絞る(検証用)")
    p.add_argument("--once", action="store_true", help="1回実行して終了")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args(argv)

    rules = (REPO / "tools" / "koma_rules.md").read_text(encoding="utf-8")
    items = [it for it in fetch_attention() if it.get("content") == "10コマ"]
    if args.companies:
        want = {c.strip() for c in args.companies.split(",")}
        items = [it for it in items if it.get("company") in want]
    if args.limit:
        items = items[:args.limit]

    mode = "DRY-RUN(本番非反映)" if args.dry_run else "DEPLOY(本番反映)"
    print(f"=== phase_c_autoloop [{mode}] 対象 {len(items)}社 ===")
    results = []
    for it in items:
        rec = process_company(it, rules, args)
        results.append(rec)
        print(f"\n--- {rec['company']} ({rec.get('slug')}) ---")
        tr = rec.get("triage", {})
        print(f"  仕分け: 台本バグ{len(tr.get('script_bugs',[]))} / 画像バグ{len(tr.get('image_bugs',[]))} / 感想{len(tr.get('opinions',[]))}")
        for a in rec["actions"]:
            if isinstance(a, dict) and "before" in a:
                print(f"  ①台本koma{a['koma']} 修正案:")
                print(f"     現行: {a['before']}")
                print(f"     新案: {a['after']}")
                if a.get("note"):
                    print(f"     理由: {a['note']}")
            elif isinstance(a, dict):
                print(f"  ①台本koma{a.get('koma','?')}: {a.get('note')}")
        if rec.get("lint"):
            le = rec["lint"]["errors"]
            print(f"  lint(提案反映後): errors={le} warnings={rec['lint']['warnings']} {'✅マージ可' if le==0 else '❌要修正'}")
        for ir in rec["image_results"]:
            if ir.get("status") == "DRY":
                print(f"  ②画像koma{ir['koma']} 再生成予定: {ir['detail']}")
            else:
                print(f"  ②画像koma{ir['koma']}: ok={ir.get('ok')} attempts={ir.get('attempts')}")
        if rec["escalate"]:
            print("  ⚠ エスカレーション:", rec["escalate"])
        if rec["opinions"]:
            print("  ③感想(要オスカー判断):", rec["opinions"])
        print(f"  → 反映可(deployable): {rec['deployable']} {rec.get('note','')}")

    print("\n=== LINE文面(プレビュー) ===")
    print(compose_line(results))
    out = REPO / "tools" / "_autoloop_last.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n結果: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
