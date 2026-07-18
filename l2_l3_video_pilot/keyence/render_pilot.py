#!/usr/bin/env python3
"""
パイロット動画レンダラ（試作スライド版）
lines.json (nana/haruki 対話) → Google TTS 音声 → 試作スライドPNG → ffmpeg合成 → MP4

※試作スライドは「レンダリング経路をエンドツーエンドで検証」するための簡易カード。
  本番は工程06/07(方式C)のChatGPTイラストに S01.png … を差し替えるだけで同じ経路で完成する。

使い方:
  venv/bin/python pilot_keyence/render_pilot.py <lines.json> <out.mp4> "<見出し>"
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from modules import synthesize_dialogue

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
W, H = 1920, 1080
NAVY = (0, 42, 92)
NAVY2 = (0, 20, 48)
RED = (216, 40, 40)
GOLD = (212, 175, 55)
NANA_C = (150, 205, 255)   # 就活生ナナ=青系
HARUKI_C = (200, 230, 205)  # 先輩ハルキ=緑系
WHITE = (245, 247, 250)


def font(sz, index=0):
    return ImageFont.truetype(FONT, sz, index=index)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def make_slide(slide_id, lines_for_slide, headline, png_path):
    img = Image.new("RGB", (W, H), NAVY2)
    d = ImageDraw.Draw(img)
    # 背景グラデーション
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY2[i] + (NAVY[i] - NAVY2[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # 上部ブランドバー
    d.rectangle([0, 0, W, 96], fill=(0, 12, 30))
    d.rectangle([0, 92, W, 100], fill=RED)
    d.text((60, 26), "KEYENCE ｜ キーエンス", font=font(46), fill=WHITE)
    d.text((W - 430, 34), headline, font=font(30), fill=GOLD)
    # スライドID
    d.text((60, 140), slide_id, font=font(120), fill=(255, 255, 255))
    d.rectangle([64, 280, 300, 292], fill=GOLD)
    # 対話字幕
    y = 360
    max_w = W - 260
    for it in lines_for_slide:
        spk = it["speaker"]
        tag = "ナナ" if spk == "nana" else ("ハルキ" if spk == "haruki" else "二人")
        col = NANA_C if spk == "nana" else (HARUKI_C if spk == "haruki" else WHITE)
        d.text((70, y), f"● {tag}", font=font(34), fill=col)
        y += 52
        for ln in wrap(d, it["text"], font(40), max_w):
            if y > H - 130:
                break
            d.text((110, y), ln, font=font(40), fill=WHITE)
            y += 58
        y += 18
        if y > H - 130:
            break
    # フッター注記
    d.rectangle([0, H - 64, W, H], fill=(0, 12, 30))
    d.text((60, H - 52), "※試作スライド（レンダリング経路の実証用）｜本番は工程07 方式CのChatGPTイラストに差し替え",
           font=font(26), fill=(170, 185, 205))
    img.save(png_path)


def main():
    lines_json = Path(sys.argv[1])
    out_mp4 = Path(sys.argv[2])
    headline = sys.argv[3] if len(sys.argv) > 3 else "企業動画"

    base = Path(__file__).resolve().parent
    audio_dir = base / "audio" / out_mp4.stem
    parts_dir = base / "audio" / (out_mp4.stem + "_parts")
    slides_dir = base / "slides" / out_mp4.stem
    clips_dir = base / "clips" / out_mp4.stem
    for p in (audio_dir, slides_dir, clips_dir):
        p.mkdir(parents=True, exist_ok=True)

    data = json.loads(lines_json.read_text(encoding="utf-8"))
    # 出現順のスライド並び（S02B等も自然順で保持）
    order, seen = [], set()
    by_slide = {}
    for it in data:
        s = it["slide"]
        if s not in seen:
            seen.add(s)
            order.append(s)
        by_slide.setdefault(s, []).append(it)

    print(f"[1/3] 音声合成 {len(data)}行 / {len(order)}スライド")
    synthesize_dialogue.run(str(lines_json), audio_dir_override=str(audio_dir),
                            parts_dir_override=str(parts_dir))

    print(f"[2/3] 試作スライド生成 {len(order)}枚")
    for s in order:
        make_slide(s, by_slide[s], headline, slides_dir / f"{s}.png")

    print(f"[3/3] クリップ合成→連結")
    clip_paths = []
    for s in order:
        png = slides_dir / f"{s}.png"
        mp3 = audio_dir / f"{s}.mp3"
        if not mp3.exists():
            print(f"  [skip] 音声なし {s}")
            continue
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(mp3)],
            capture_output=True, text=True).stdout.strip())
        clip = clips_dir / f"{s}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(png), "-i", str(mp3),
             "-t", str(dur), "-c:v", "libx264", "-tune", "stillimage",
             "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
             "-vf", f"scale={W}:{H}", "-r", "30", str(clip)],
            check=True, capture_output=True)
        clip_paths.append(clip)

    concat = clips_dir / "concat.txt"
    concat.write_text("".join(f"file '{c.resolve()}'\n" for c in clip_paths))
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-c", "copy", str(out_mp4)], check=True, capture_output=True)
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(out_mp4)],
        capture_output=True, text=True).stdout.strip())
    mb = out_mp4.stat().st_size / 1024 / 1024
    print(f"\n🎬 完成: {out_mp4}")
    print(f"   総尺 {int(total//60)}分{total%60:.0f}秒 / {mb:.1f}MB / {len(clip_paths)}スライド")


if __name__ == "__main__":
    main()
