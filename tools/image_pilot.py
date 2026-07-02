#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_pilot.py — 画像再生成パイロット (3社限定・レビュー保存まで・本番反映しない)。

目的: 画像FBキューの真の画像バグに対し、画像エンジン(phase_c_image_fix / fix_and_deploy)の
      「翻訳→fix指示注入→再生成→ハードQA」パイプラインが実運用で使えるかを、
      3社の該当コマ"だけ"で実証する。生成物はレビュー用フォルダへ before/after 並置。

【安全境界(物理)】
  - WHITELIST に無い社・コマは物理的に処理しない(504件全消化・暴発の防止)。
  - AUTO_IMAGE_FIX_ENABLED は読まない/変えない。launchd も触らない。
  - 本番へ書かない: copy_panel_to_deploy / git push / D1 update / setreflected は一切呼ばない。
  - 生成は output/<slug>/scenario.json + char-ref(Gemini) 経由。実行後に scenario.json と
    koma<NN>.png を元に戻し、ローカル output/ を無改変に保つ(誤デプロイ源を残さない)。
  - 出力: review/image_pilot_<DATE>/<slug>/koma<N>_before.png と _after.png、manifest.json。

使い方:
  python tools/image_pilot.py --date 20260702                 # WHITELIST全件
  python tools/image_pilot.py --date 20260702 --only daikin:1 # 単体(検証用)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(TOKYARI / "scripts"))

# === 物理ホワイトリスト(この3社・このコマ以外は処理不能) ===
WHITELIST = {
    "fanuc":   [1, 6],   # koma1=人物/建物の縮尺, koma6=上部の白い空白帯
    "daikin":  [1, 2],   # koma1=上部の四角い空白ボックス, koma2=腕の破綻
    "komatsu": [1, 5, 6],  # koma1=横線, koma6=縮尺 / koma5=四角い空白枠(拡張ルーブリック auto検証・未反映)
}
NAMES = {"fanuc": "ファナック", "daikin": "ダイキン工業", "komatsu": "コマツ（小松製作所）"}

# v2差し戻し(Web Claude目視): char-ref厳守＋固有の背景フック保持を明示。翻訳を介さず手書き指示で再生成。
V2_INSTRUCTIONS = {
    ("daikin", 2): (
        "【キャラ設定画(char-ref)を厳守】ナナ=淡い青のカーディガン、ハルキ=ダークグリーンのシャツ＋"
        "ジャケット。2名の顔の同一性(char-ref)を保つ。前回修正した右腕/手指の破綻解消は維持し、"
        "腕は左右各1本・肩肘手首が自然につながること。天井は業務用の天井カセット型エアコン。"
        "コラージュ禁止・文字焼き込み禁止。"),
    ("fanuc", 1): (
        "【縮尺是正は維持】人物(ナナ・ハルキ)を画面高さ約1/3以下に縮小し遠近を自然化。"
        "【背景すり替え禁止】背景はファナック固有の『黄色い工場・オフィスビル群』をbefore同等の"
        "建物形状・黄色で保持し、別の背景に描き直さない。char-ref厳守(ナナ淡青カーデ/ハルキ緑ジャケ・"
        "顔の同一性)。コラージュ禁止・文字焼き込み禁止。"),
    ("komatsu", 6): (
        "【縮尺是正は維持】人物を背景に対し自然な比率へ。【背景すり替え禁止】背景はコマツの建機"
        "(before同等の車体形状の油圧ショベル/建設機械)を固有の視覚フックとして保持し、別形状の機械に"
        "すり替えない。char-ref厳守(ナナ淡青カーデ/ハルキ緑ジャケ・顔の同一性)。"
        "コラージュ禁止・文字焼き込み禁止。"),
}

# 本番へ書く関数は import すらしない(呼べないことをコードで担保)。


def _load_env():
    # ANTHROPIC(翻訳) は .env.phase_c、GEMINI(生成) は tokyari/.env
    for envp in (REPO / "tools" / ".env.phase_c", TOKYARI / ".env"):
        if envp.exists():
            for line in envp.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def _fb_detail_for(slug, koma):
    """進捗スプシの最新FBから、その社の該当コマの画像FB本文を取得(read-only)。"""
    import requests
    import re
    url = os.environ["SHEET_WEBAPP_URL"].strip()
    tok = os.environ["SHEET_API_TOKEN"].strip()
    d = requests.get(url, params={"mode": "companyrow", "company": NAMES[slug], "token": tok}, timeout=60).json()
    rounds = [r for r in d.get("rounds", []) if r.get("fb")]
    if not rounds:
        return ""
    fb = rounds[-1]["fb"]
    parts = re.split(r"【\s*(\d+)\s*(?:枚目|コマ目|コマ)】", fb)
    for i in range(1, len(parts), 2):
        if int(parts[i]) == koma:
            return parts[i + 1].strip()[:300]
    return ""


def run_one(slug, koma, review_dir, custom_instruction=None, suffix=""):
    import phase_c_lib as L                 # _anthropic 等
    import phase_c_image_fix as IMG         # translate_image_fb / hard_gate / _scenario_excerpt
    import fix_and_deploy as FAD            # add_fix_instructions_to_scenario / regenerate_panel(=生成のみ)

    tslug = slug  # 3社は tokyari slug 同一(確認済)
    out_dir = TOKYARI / "output" / tslug
    scen = out_dir / "scenario.json"
    png = out_dir / f"koma{koma:02d}.png"
    rec = {"slug": slug, "koma": koma, "action": None, "instruction": "",
           "qa_ok": None, "severity": None, "char_match": None, "cost": 0.0,
           "before": None, "after": None, "note": "", "suffix": suffix}

    detail = _fb_detail_for(slug, koma)
    rec["fb"] = detail[:200]

    # before は本番CDNからDL済(review_dir/<slug>/koma<N>_before.png)。無ければローカルkomaを暫定before。
    before = review_dir / slug / f"koma{koma}_before.png"
    if before.exists():
        rec["before"] = str(before)

    # 1) 指示決定。custom_instruction(v2差し戻し=手書き指示)があれば翻訳を介さずそれを使う。
    if custom_instruction:
        rec["action"] = "custom"
        rec["instruction"] = custom_instruction
        rec["forced"] = True
        rec["note"] = "v2: char-ref厳守＋背景フック保持の手書き指示で再生成"
    else:
        # エンジンの翻訳(FB→範囲限定の再生成指示 or escalate)。判定は記録する。
        excerpt = IMG._scenario_excerpt(tslug, koma)
        tr = IMG.translate_image_fb(NAMES[slug], slug, koma, detail, excerpt)
        rec["action"] = tr.get("action")
        rec["reason"] = tr.get("reason", "")
        # 翻訳がescalateでも、生成能力の実証のためFB本文を指示にして強制再生成する。
        if tr.get("action") == "auto" and tr.get("instruction"):
            rec["instruction"] = tr["instruction"]
            rec["forced"] = False
        else:
            rec["instruction"] = f"【画像FB(強制再生成・翻訳はescalate判定)】{detail}"
            rec["forced"] = True
            rec["note"] = f"翻訳=escalate({tr.get('reason','')[:50]}); FB本文で強制再生成し目視用afterを作成"

    # 2) ローカルを退避(実行後に必ず戻す=本番/ローカル無改変)
    bak_scen = scen.with_suffix(".json.pilotbak")
    bak_png = png.with_suffix(".png.pilotbak") if png.exists() else None
    shutil.copy2(scen, bak_scen)
    if bak_png:
        shutil.copy2(png, bak_png)
    try:
        # 3) fix指示注入 → 該当コマだけ再生成(QA込み・生成のみ、deployしない)
        FAD.add_fix_instructions_to_scenario(tslug, koma, [rec["instruction"]])
        ok, qa = FAD.regenerate_panel(tslug, koma)
        gate_ok, sev, cmv, cost = IMG.hard_gate(tslug, koma)
        rec["qa_ok"] = bool(gate_ok)
        rec["severity"] = sev
        rec["char_match"] = cmv
        rec["cost"] = cost
        # 4) after を review へ保存 (suffix指定時は koma<N>_after_<suffix>.png)
        aname = f"koma{koma}_after{('_'+suffix) if suffix else ''}.png"
        after = review_dir / slug / aname
        if png.exists():
            shutil.copy2(png, after)
            rec["after"] = str(after)
        else:
            rec["note"] = "生成物(koma png)が見つからない"
    finally:
        # 5) ローカルを完全復元(誤デプロイ源を残さない)
        shutil.move(str(bak_scen), str(scen))
        if bak_png:
            shutil.move(str(bak_png), str(png))
    return rec


def main(argv=None):
    _load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYYMMDD (review フォルダ名)")
    ap.add_argument("--only", help="slug:koma で1件だけ(検証用)")
    ap.add_argument("--v2", action="store_true",
                    help="差し戻し3枚(char-ref厳守+背景保持)をv2再生成。既存afterはafter_v1へ退避")
    args = ap.parse_args(argv)

    review_dir = TOKYARI / "review" / f"image_pilot_{args.date}"
    targets = []
    if args.v2:
        # V2_INSTRUCTIONS のキー(=差し戻し3枚)のみ。WHITELISTに全て含まれることを物理確認。
        for (s, k) in V2_INSTRUCTIONS:
            assert s in WHITELIST and k in WHITELIST[s], f"{s}:{k} が WHITELIST外"
            targets.append((s, k))
    elif args.only:
        s, k = args.only.split(":")
        if s not in WHITELIST or int(k) not in WHITELIST[s]:
            print(f"❌ {args.only} は WHITELIST 外 → 実行拒否"); return 2
        targets = [(s, int(k))]
    else:
        for s, ks in WHITELIST.items():
            for k in ks:
                targets.append((s, k))

    print(f"=== 画像パイロット [review-only] 対象 {len(targets)}件 (WHITELIST={ {k: v for k, v in WHITELIST.items()} }) ===")
    print(f"AUTO_IMAGE_FIX_ENABLED(参考)={os.environ.get('AUTO_IMAGE_FIX_ENABLED','?')} ※本スクリプトは読むだけ/変更しない")
    results = []
    for s, k in targets:
        print(f"\n--- {s} koma{k}{' [v2差し戻し]' if args.v2 else ''} ---")
        t0 = time.time()
        custom, suffix = None, ""
        if args.v2:
            custom = V2_INSTRUCTIONS[(s, k)]
            suffix = "v2"
            # 既存 after(v1) を after_v1 へ退避(上書きしない・冪等)
            v1 = review_dir / s / f"koma{k}_after.png"
            v1r = review_dir / s / f"koma{k}_after_v1.png"
            if v1.exists() and not v1r.exists():
                import shutil as _sh
                _sh.move(str(v1), str(v1r))
                print(f"  v1退避: {v1.name} → {v1r.name}")
        try:
            rec = run_one(s, k, review_dir, custom_instruction=custom, suffix=suffix)
        except Exception as e:
            import traceback; traceback.print_exc()
            rec = {"slug": s, "koma": k, "note": f"例外:{e}", "action": "error"}
        rec["sec"] = round(time.time() - t0, 1)
        results.append(rec)
        print(f"  action={rec.get('action')} qa_ok={rec.get('qa_ok')} sev={rec.get('severity')} "
              f"char={rec.get('char_match')} cost=${rec.get('cost',0):.3f} {rec.get('sec')}s")
        if rec.get("instruction"):
            print(f"  再生成指示: {rec['instruction'][:120]}")
        if rec.get("after"):
            print(f"  after: {rec['after']}")
        if rec.get("note"):
            print(f"  note: {rec['note']}")

    manifest = review_dir / "manifest.json"
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nmanifest: {manifest}")
    print("本番D1/R2へは未反映(before/after 目視 → GO後に別途反映)。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
