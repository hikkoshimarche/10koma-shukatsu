#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_staleness.py — 再生成の前に『配信中の画像がまだその症状を持っているか』を確認する関所。

背景(2026-08-24 nidec#10): 12〜19日滞留したキューでは、その間に別経路で直った画像がある。
古いFBに従って再生成すると【直っているものを壊す】(nidec#10は配信画像に既に吹き出しが無いのに
再生成で背景フックが東京駅→無地ビルにドリフトした)。よって消化役フローの最初にこの関所を置き、
症状が既に無いコマは再生成せずキューから落とす。判定は『配信中(D1 image_url=jsDelivr)の画像』を
取得し、そのFBの症状が今も在るかをGemini(flash)へ限定質問する(汎用7観点QAでなくFB症状ピンポイント)。

安全側の既定: 判定不能/エラーは present 扱い(=関所を通さない=再生成側に残す)。
              誤って『resolved』で落とすと壊れたコマを放置するため、resolvedは確信時のみ。
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(REPO / "tools"))

_CLIENT = None


def _client():
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        from google.genai import types as _t
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        # per-request タイムアウト(ms)。ハングした1件が worker を占有し全体を止めるのを防ぐ。
        _CLIENT = genai.Client(api_key=key,
                               http_options=_t.HttpOptions(timeout=30_000))
    return _CLIENT


def deployed_image_url(slug: str, koma: int):
    """live(D1 company_panels.image_url)=jsDelivrが実際に配信しているURL。panel_num=komaで引く。"""
    import deploy_salary as D
    r = D.d1_query(f"SELECT image_url FROM company_panels WHERE company_id='{slug}' AND panel_num={int(koma)}")
    return (r[0]["image_url"] if r else None)


def _fetch(url: str) -> bytes:
    import requests
    return requests.get(url, timeout=60).content


_PROMPT = (
    "あなたは10コマ漫画の画像レビュアーです。以下のインターン指摘が、"
    "この画像に『今も』当てはまるかだけを判定してください。作り直しの良し悪しは問いません。\n"
    "指摘:「{detail}」\n"
    "判定基準: 指摘された症状(焼き込み文字/吹き出し・上端や縁の白い空白帯/余白・画像を横切る不自然な線・"
    "余分/複製/浮遊した腕手指・人物の縮尺破綻・浮遊物 等)が画像に現存するなら present、"
    "既に解消され見当たらないなら resolved。確信が持てなければ present。\n"
    'JSONのみ: {{"status":"present"|"resolved","confidence":0.0-1.0,"reason":"短い日本語"}}'
)


def symptom_status(image_bytes: bytes, detail: str, model: str = "gemini-3-flash-preview") -> dict:
    """配信画像に症状が現存するか。{'status','confidence','reason'}。失敗時は present(安全側)。"""
    from io import BytesIO
    from PIL import Image
    from google.genai import types
    try:
        img = Image.open(BytesIO(image_bytes)); img.load()
        resp = _client().models.generate_content(
            model=model, contents=[img, _PROMPT.format(detail=str(detail)[:300])],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0))
        data = json.loads((resp.text or "").strip() or "{}")
        st = data.get("status")
        if st not in ("present", "resolved"):
            return {"status": "present", "confidence": 0.0, "reason": "判定不能→安全側present"}
        return {"status": st, "confidence": float(data.get("confidence", 0.0)),
                "reason": str(data.get("reason", ""))[:120]}
    except Exception as e:
        return {"status": "present", "confidence": 0.0, "reason": f"error→安全側present:{type(e).__name__}"}


# resolved で『落として良い』確信閾値。これ未満は present 同様に再生成側へ残す(壊れ放置を防ぐ)。
RESOLVED_MIN_CONF = 0.7


def is_stale(slug: str, koma: int, detail: str) -> dict:
    """配信中画像を取得→症状判定。返り値に stale(bool=落として良いか)を含む。"""
    url = deployed_image_url(slug, koma)
    if not url:
        return {"slug": slug, "koma": koma, "stale": False, "status": "present",
                "reason": "D1にimage_url無し→残す", "url": None}
    try:
        b = _fetch(url)
    except Exception as e:
        return {"slug": slug, "koma": koma, "stale": False, "status": "present",
                "reason": f"取得失敗→残す:{type(e).__name__}", "url": url}
    s = symptom_status(b, detail)
    stale = (s["status"] == "resolved" and s["confidence"] >= RESOLVED_MIN_CONF)
    return {"slug": slug, "koma": koma, "stale": stale, **s, "url": url}


if __name__ == "__main__":
    # 単体テスト: 引数 slug koma "detail"
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("koma", type=int); ap.add_argument("detail")
    a = ap.parse_args()
    print(json.dumps(is_stale(a.slug, a.koma, a.detail), ensure_ascii=False, indent=1))
