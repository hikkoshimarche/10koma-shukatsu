#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LP各ページの表示テキストに BudouX 文節境界で <wbr> を物理挿入する（ビルド時・実行時JS不要）。
CSS側は word-break:keep-all にするため、テキストは <wbr>(=文節境界)でのみ折り返す＝
「見てみましょう」「はじめて」「しません」等が全ブラウザで絶対に途中で割れない。
HTMLは文字列として最小改変（テキストrunにのみ<wbr>挿入・タグ/属性/script/style/title/コメントは不変）。"""
import re, sys
from pathlib import Path
import budoux

PARSER = budoux.load_default_japanese_parser()
JP = re.compile(r'[぀-ゟ゠-ヿ一-鿿]')  # かな・カナ・漢字を含むか
TOKEN = re.compile(r'(<[^>]+>)', re.S)  # タグ/コメントで分割（テキストと交互）

# テキストを処理しない領域（開始タグ名）。閉じるまでスキップ。
SKIP_ELEMENTS = {'script', 'style', 'title'}

def wbr_text(text: str) -> str:
    # 既に<wbr>や実体参照を壊さない。日本語を含む run のみ文節分割。
    if ' ' in text:  # nbsp等はそのまま
        pass
    if not JP.search(text):
        return text
    phrases = PARSER.parse(text)
    if len(phrases) <= 1:
        return text
    return '<wbr>'.join(phrases)

def process(html: str) -> str:
    parts = TOKEN.split(html)
    out = []
    skip_depth_tag = None  # スキップ中の要素名
    for seg in parts:
        if not seg:
            continue
        if seg.startswith('<'):
            low = seg.lower()
            # コメントはそのまま
            if low.startswith('<!--'):
                out.append(seg); continue
            m = re.match(r'</?\s*([a-zA-Z0-9]+)', low)
            name = m.group(1) if m else ''
            if skip_depth_tag:
                if low.startswith('</') and name == skip_depth_tag:
                    skip_depth_tag = None
                out.append(seg); continue
            if not low.startswith('</') and name in SKIP_ELEMENTS and not low.endswith('/>'):
                skip_depth_tag = name
            out.append(seg); continue
        # テキストrun
        if skip_depth_tag:
            out.append(seg); continue
        out.append(wbr_text(seg))
    return ''.join(out)

def main(argv):
    files = argv[1:]
    for f in files:
        p = Path(f)
        src = p.read_text(encoding='utf-8')
        if '<wbr>' in src:
            # 既処理分を一旦除去して再適用（冪等）
            src = src.replace('<wbr>', '')
        dst = process(src)
        p.write_text(dst, encoding='utf-8')
        print(f'{f}: <wbr> count = {dst.count("<wbr>")}')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
