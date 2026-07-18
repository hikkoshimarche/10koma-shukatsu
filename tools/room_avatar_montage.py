#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_avatar_montage.py — アバターの見比べモンタージュ生成。
①各社の新gpt版を1行(役割ラベル付き)＋三井GOLD行＝会社間で別人か・GOLD質かが一目。
②版比較: 各社R1を [現行Gemini | 新gpt | 三井GOLD] 横並び。
出力: <outbase>/_montage_companies.png ・ _montage_versions.png
"""
import json, os, sys
from pathlib import Path
from PIL import Image, ImageDraw
REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
OUTBASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.path.expanduser("~/Desktop/kindle_受け渡し/avatar_pilot_gpt"))
SLUGS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["sumitomo-corp", "keyence", "daiichi-life"]
TH = 200; PAD = 8; LBL = 22


def strip(imgs_labels, title):
    n = len(imgs_labels)
    w = n * (TH + PAD) + PAD; h = TH + LBL + 30
    canvas = Image.new("RGB", (w, h), "white"); d = ImageDraw.Draw(canvas)
    d.text((PAD, 4), title, fill="black")
    for i, (p, lab) in enumerate(imgs_labels):
        x = PAD + i * (TH + PAD); y = 26
        try:
            im = Image.open(p).convert("RGB").resize((TH, TH))
            canvas.paste(im, (x, y))
        except Exception:
            d.rectangle([x, y, x + TH, y + TH], outline="red"); d.text((x + 10, y + TH // 2), "(none)", fill="red")
        d.text((x + 2, y + TH + 4), lab[:26], fill="black")
    return canvas


def vstack(strips):
    w = max(s.width for s in strips); h = sum(s.height for s in strips)
    c = Image.new("RGB", (w, h), "white"); y = 0
    for s in strips:
        c.paste(s, (0, y)); y += s.height
    return c


def main():
    cj = json.loads((REPO / "public/companies.json").read_text(encoding="utf-8"))
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    # ① 会社別モンタージュ + GOLD行
    rows = []
    gold = REPO / "public/images/mitsui/personas"
    gold_imgs = [(gold / f"{r}.png", r) for r in ["r1_sato", "r2_yamada", "r3_takahashi", "r4_suzuki", "r5_tanaka", "r6_watanabe"]]
    rows.append(strip(gold_imgs, "三井GOLD (gpt-image-1・質の目標)"))
    for slug in SLUGS:
        d = OUTBASE / slug
        imgs = sorted(d.glob("r*.png"), key=lambda p: p.name)
        rows.append(strip([(p, p.stem.upper()) for p in imgs], f"新gpt: {id2name.get(slug, slug)} ({slug})"))
    comp = vstack(rows)
    comp.save(OUTBASE / "_montage_companies.png")
    print(f"  ① 会社別モンタージュ: {OUTBASE/'_montage_companies.png'} ({comp.size})")
    # ② 版比較(各社R1)
    vrows = []
    for slug in SLUGS:
        cur = REPO / "public/images" / slug / "personas" / "r1.png"      # 現行Gemini
        new = OUTBASE / slug / "r1.png"                                   # 新gpt
        goldp = gold / "r1_sato.png"
        vrows.append(strip([(cur, "現行Gemini"), (new, "新gpt-image-1"), (goldp, "三井GOLD")], f"{id2name.get(slug,slug)} R1 版比較"))
    vc = vstack(vrows); vc.save(OUTBASE / "_montage_versions.png")
    print(f"  ② 版比較モンタージュ: {OUTBASE/'_montage_versions.png'} ({vc.size})")


if __name__ == "__main__":
    main()
