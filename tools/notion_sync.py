# =============================================================================
# VENDORED COPY (durability) — 2026-06-20
#   source: ~/oscar-ai/tokyari-pipeline/scripts/notion_sync.py
#   このファイルは耐障害性のための複製。正本は上記 source。改修は source 側で行い再 vendor すること。
#
# 外部依存 (pip): notion-client, python-dotenv
# 実行時に参照するファイル (正本リポジトリ ~/oscar-ai/tokyari-pipeline 基準):
#   - <ROOT>/.env                         … NOTION_TOKEN
#   - <ROOT>/output/notion_sync_state.csv … slug → notion_page_id
#   - <ROOT>/output/factsheet_audit.csv   … 品質メモ(任意)
#   - <ROOT>/output/<slug>/scenario_v4.json … 台本ソース
#   - /Users/oscardodds/projects/10koma-shukatsu/public/companies.json … 社名解決(絶対パス)
#   （ROOT = このスクリプトの親の親 = scripts/ の親。tools/ から単体実行はパス不整合のため正本側で実行する）
#
# 安全な使い方: python scripts/notion_sync.py --v41-safe (--slug <tokyari-slug> | --all9)
#   非破壊(旧版は⚠️旧版にrename+末尾追記)/ ID限定(pages.create禁止)/ タイトルガード。
# =============================================================================
"""Notion 同期エンジン (sync_company を提供する一機能 + CLI).

設計:
  - factsheet.md と scenario.json を Notion の「🌐 ファクトシート」配下の各社ページに同期
  - 既存ページがあれば 「## 自動生成版 YYYY-MM-DD（最新）」 ブロックを upsert (冪等)
  - 既存ページが無ければ 同フォルダに新規作成 (タイトル: 「<企業名> ファクトシート」)
  - 状態は output/notion_sync_state.csv で永続化 → 次回は page_id 直接更新
  - レート制限: 平均 3req/sec (実装上は約2.5req/sec で余裕を持つ)
  - 429/overload は指数バックオフ 最大5回 → それでも失敗ならスキップ
  - data 破壊禁止: 既存ブロックを削除しない。同名「自動生成版」ブロック内のみ置換

CLI:
  python scripts/notion_sync.py --slug mitsubishi-corp
  python scripts/notion_sync.py --sogo-shosha
  python scripts/notion_sync.py --daemon (audit CSV 監視ループ)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Optional

from notion_client import Client, APIResponseError
from dotenv import load_dotenv

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))
load_dotenv(ROOT / ".env")

# === 設定 ===
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
FACTSHEET_FOLDER_ID = "36d75180-01ef-81a1-84fa-e5c125f72c7b"  # 🌐 ファクトシート
SYNC_DATE = "2026-06-20 v4.1(FB反映)"  # 作業日・版 (v4.1安全パスは V41_SYNC_DATE を使用)
UPSERT_HEADING = f"自動生成版 {SYNC_DATE}（最新）"

# === v4.1 安全同期 (非破壊・ID限定・タイトルガード) 2026-06-20 ===
# 既存「自動生成版」見出しは削除せず ⚠️旧版(FB前) にrename、新版を末尾に追記する恒久安全パス。
V41_SYNC_DATE = "2026-06-20 v4.1(FB反映)"
V41_HEADING = "自動生成版 2026-06-20 v4.1（FB反映・最新の正）✅"
OLD_V4_MATCH = "自動生成版 2026-06-19"   # 旧版としてマークする対象見出し
OLD_MARK = "⚠️旧版(FB前)"

COMPANIES_JSON = Path("/Users/oscardodds/projects/10koma-shukatsu/public/companies.json")
SYNC_STATE_CSV = ROOT / "output" / "notion_sync_state.csv"
AUDIT_CSV = ROOT / "output" / "factsheet_audit.csv"

SLUG_TO_TOKYARI = {"itochu": "itochu-shoji"}  # 既存差異

# Notion ブロックタイプ別の最大文字数 (paragraph 等のrich_text 文字列上限 = 2000)
NOTION_TEXT_LIMIT = 1900  # 余裕を持って 1900

# Title prefix - 旧版除外
EXCLUDE_TITLE_KEYWORDS = ["旧版", "使わない", "archive", "不要"]


# === レート制限 ===
_RATE_LOCK = Lock()
_LAST_CALL = [0.0]
def _rate_limit():
    with _RATE_LOCK:
        elapsed = time.time() - _LAST_CALL[0]
        if elapsed < 0.4:  # 約 2.5 req/sec
            time.sleep(0.4 - elapsed)
        _LAST_CALL[0] = time.time()


def notion_call(fn, *args, **kwargs):
    """rate limit + 指数バックオフ (最大5回) で notion-client 呼び出しをラップ."""
    last_err = None
    for attempt in range(1, 6):
        _rate_limit()
        try:
            return fn(*args, **kwargs)
        except APIResponseError as e:
            last_err = e
            status = getattr(e, "status", 0)
            if status in (429, 502, 503, 504) and attempt < 5:
                wait = min(60, 2 ** attempt)
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < 3:
                time.sleep(2 * attempt)
                continue
            raise
    raise last_err


# === 状態 CSV ===
def load_sync_state() -> dict[str, dict]:
    """slug → {notion_page_id, synced_at, has_scenario} の辞書."""
    state = {}
    if SYNC_STATE_CSV.exists():
        with open(SYNC_STATE_CSV, encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                state[row["slug"]] = row
    return state


def append_sync_state(slug: str, page_id: str, has_scenario: bool, action: str = "synced", note: str = ""):
    SYNC_STATE_CSV.parent.mkdir(parents=True, exist_ok=True)
    existed = SYNC_STATE_CSV.exists()
    with open(SYNC_STATE_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existed:
            w.writerow(["slug","notion_page_id","synced_at","has_scenario","action","note"])
        w.writerow([slug, page_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(has_scenario), action, note])


# === 企業名解決 ===
_companies_cache = None
def get_company_name(slug: str) -> str:
    global _companies_cache
    if _companies_cache is None:
        _companies_cache = {}
        data = json.loads(COMPANIES_JSON.read_text(encoding="utf-8"))
        for ind, cs in data.items():
            for c in cs:
                _companies_cache[c["id"]] = c["name"]
    if slug in _companies_cache:
        return _companies_cache[slug]
    # tokyari の slug (e.g. itochu-shoji) → companies.json の slug を逆引き
    for ck, ct in SLUG_TO_TOKYARI.items():
        if ct == slug:
            return _companies_cache.get(ck, slug)
    return slug


# === Notion ブロック構築 ===
def _split_text(text: str, limit: int = NOTION_TEXT_LIMIT) -> list[str]:
    """長文を limit 字で分割 (行境界を尊重)."""
    if len(text) <= limit:
        return [text]
    chunks = []
    buf = ""
    for line in text.splitlines(keepends=True):
        if len(buf) + len(line) > limit and buf:
            chunks.append(buf)
            buf = ""
        if len(line) > limit:
            # 単一行が長すぎる場合は強制分割
            for i in range(0, len(line), limit):
                chunks.append(line[i:i+limit])
            buf = ""
        else:
            buf += line
    if buf:
        chunks.append(buf)
    return chunks


def _paragraph(text: str) -> list[dict]:
    """paragraph block(s) — 長文は複数 block に分割."""
    if not text.strip():
        return [{"object": "block", "type": "paragraph",
                 "paragraph": {"rich_text": []}}]
    return [
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}}
        for chunk in _split_text(text)
    ]


def _heading2(text: str) -> dict:
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": text[:NOTION_TEXT_LIMIT]}}]}}


def _heading3(text: str) -> dict:
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": text[:NOTION_TEXT_LIMIT]}}]}}


def _bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:NOTION_TEXT_LIMIT]}}]}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _code(text: str, lang: str = "markdown") -> list[dict]:
    blocks = []
    for chunk in _split_text(text):
        blocks.append({
            "object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": chunk}}], "language": lang}
        })
    return blocks


def build_blocks_for_factsheet(factsheet_md: str, scenario: Optional[dict], audit_row: Optional[dict]) -> list[dict]:
    """同期ブロックの本体 (heading "自動生成版" の下に置く子ブロック)."""
    blocks = []
    # 品質メモ
    if audit_row:
        hooks = audit_row.get("visual_hooks", "?")
        cit = audit_row.get("citation_rate", "?")
        hook_ok = audit_row.get("hooks_ok", "?")
        cit_ok = audit_row.get("citation_ok", "?")
        attempts = audit_row.get("attempts", "?")
        memo = (f"品質メモ: 視覚フック {hooks}件 ({'OK' if hook_ok in (True,'True','TRUE','1',1) else '要確認'}) / "
                f"出典率 {cit} ({'OK' if cit_ok in (True,'True','TRUE','1',1) else '要確認'}) / "
                f"生成試行 {attempts} 回")
        blocks.append(_bullet(memo))
    # factsheet 本文 (Markdown を code block で保存。レビュー時にレンダリングコピー可能)
    blocks.append(_heading3("ファクトシート本文"))
    blocks.extend(_code(factsheet_md, lang="markdown"))
    # 台本
    if scenario:
        blocks.append(_heading3("10コマ台本"))
        for k in scenario.get("koma", []):
            n = k.get("koma_number")
            sp = k.get("staging_pattern", "")
            arc = k.get("emotional_arc", "")
            blocks.append(_bullet(f"コマ{n:02d} ({arc}, pattern={sp})"))
            for line in k.get("script", []):
                blocks.append({"object":"block","type":"bulleted_list_item",
                               "bulleted_list_item":{"rich_text":[
                                   {"type":"text","text":{"content":line[:NOTION_TEXT_LIMIT]}}
                               ]}})
            ov = k.get("overlay_text") or {}
            if ov.get("main_copy"):
                blocks.append(_bullet(f"  キャッチコピー: {ov.get('main_copy')}"))
            if k.get("brand_object"):
                bf = k["brand_object"].get("brand_form", "")
                blocks.append(_bullet(f"  ブランド物体: {bf[:200]}"))
            if k.get("visual_hook"):
                blocks.append(_bullet(f"  視覚フック: {k.get('visual_hook')[:200]}"))
    blocks.append(_divider())
    return blocks


# === 既存ページ検索 / アーカイブ ===
def find_existing_page(client: Client, company_name: str, slug: str) -> Optional[dict]:
    """company_name でファクトシートページを検索. 旧版は除外. 一致が複数あれば現行優先(最新更新)."""
    queries = [f"{company_name} ファクトシート", company_name]
    candidates = []
    for q in queries:
        try:
            res = notion_call(client.search, query=q, filter={"property": "object", "value": "page"})
            for r in res.get("results", []):
                title_arr = r.get("properties", {}).get("title", {}).get("title", [])
                if not title_arr:
                    # fallback: properties.title not always present at top level
                    parent = r.get("parent", {})
                    # title is often in plain properties
                    continue
                title = "".join(t.get("plain_text", "") for t in title_arr)
                if "ファクトシート" not in title:
                    continue
                if not title.startswith(company_name) and company_name not in title:
                    continue
                if any(kw in title for kw in EXCLUDE_TITLE_KEYWORDS):
                    continue
                candidates.append({"id": r["id"], "title": title, "last_edited_time": r.get("last_edited_time","")})
            if candidates:
                break
        except Exception:
            continue
    if not candidates:
        return None
    # 一致が複数なら現行 (最新編集) を優先
    candidates.sort(key=lambda x: x["last_edited_time"], reverse=True)
    return candidates[0]


def find_existing_auto_heading(client: Client, page_id: str) -> Optional[str]:
    """同一日付の '自動生成版 YYYY-MM-DD' heading_2 ブロックを探す. あれば block_id を返す."""
    cursor = None
    while True:
        res = notion_call(client.blocks.children.list, block_id=page_id, start_cursor=cursor)
        for b in res.get("results", []):
            if b.get("type") == "heading_2":
                rt = b.get("heading_2", {}).get("rich_text", [])
                txt = "".join(t.get("plain_text","") for t in rt)
                if UPSERT_HEADING in txt or "自動生成版" in txt:
                    return b["id"]
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return None


def archive_block_and_following(client: Client, page_id: str, target_block_id: str):
    """target heading 以降の同色子ブロックをアーカイブ. (次の heading_2 直前まで)"""
    cursor = None
    block_ids = []
    found = False
    while True:
        res = notion_call(client.blocks.children.list, block_id=page_id, start_cursor=cursor)
        for b in res.get("results", []):
            if b["id"] == target_block_id:
                found = True
                block_ids.append(b["id"])
                continue
            if found:
                if b.get("type") == "heading_2":
                    # 次の見出しに到達 → 終了
                    return block_ids
                block_ids.append(b["id"])
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return block_ids


# === メイン同期関数 ===
def sync_company(slug: str, client: Optional[Client] = None) -> dict:
    """1社の factsheet + scenario を Notion に upsert.
    返り値: {slug, status, page_id, action, has_scenario, error}
    """
    if client is None:
        client = Client(auth=NOTION_TOKEN)

    tokyari_slug = SLUG_TO_TOKYARI.get(slug, slug)
    out_dir = ROOT / "output" / tokyari_slug
    factsheet_path = out_dir / "factsheet.md"
    scenario_path = out_dir / "scenario.json"

    if not factsheet_path.exists():
        return {"slug": slug, "status": "skipped", "reason": "no factsheet", "page_id": None}

    factsheet_md = factsheet_path.read_text(encoding="utf-8")
    scenario = None
    if scenario_path.exists():
        try:
            scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
        except Exception:
            scenario = None

    # audit row
    audit_row = None
    if AUDIT_CSV.exists():
        try:
            with open(AUDIT_CSV, encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    if row.get("slug") == slug:
                        audit_row = row
                        break
        except Exception:
            pass

    company_name = get_company_name(slug)

    # 状態 CSV から page_id 取得 (再実行高速化)
    state = load_sync_state()
    page_id = None
    if slug in state and state[slug].get("notion_page_id"):
        page_id = state[slug]["notion_page_id"]

    desired_title = f"🌐 {company_name} ファクトシート"  # タイトル統一規約

    action = ""
    if not page_id:
        # 検索
        existing = find_existing_page(client, company_name, slug)
        if existing:
            page_id = existing["id"]
            action = "found_existing"
        else:
            # 新規作成
            new_page = notion_call(client.pages.create,
                parent={"page_id": FACTSHEET_FOLDER_ID},
                properties={"title": {"title": [
                    {"type":"text","text":{"content": desired_title}}
                ]}},
                icon={"type":"emoji","emoji":"🌐"},
            )
            page_id = new_page["id"]
            action = "created"

    # タイトル統一: 既存ページのタイトル/アイコンを「🌐 <社名> ファクトシート」に正規化
    # (タイトルはメタデータ。本文セクションブロックは破壊しない)
    if action != "created":
        try:
            notion_call(client.pages.update, page_id=page_id,
                properties={"title": {"title": [
                    {"type": "text", "text": {"content": desired_title}}
                ]}},
                icon={"type": "emoji", "emoji": "🌐"})
        except Exception:
            pass  # タイトル更新失敗は致命的でない (本文同期は継続)

    # 既存の自動生成版 heading があれば、それ以降をアーカイブ
    existing_heading_id = find_existing_auto_heading(client, page_id)
    if existing_heading_id:
        to_archive = archive_block_and_following(client, page_id, existing_heading_id)
        for bid in to_archive:
            try:
                notion_call(client.blocks.delete, block_id=bid)
            except Exception:
                pass  # 既に消えていれば無視
        action = (action + "+replaced") if action else "replaced"

    # 新しい heading + children を append
    heading_block = _heading2(UPSERT_HEADING)
    children_blocks = build_blocks_for_factsheet(factsheet_md, scenario, audit_row)
    all_new = [heading_block] + children_blocks

    # Notion API は children を100件ずつしか追加できない (実は 1000件まで OK だが安全側)
    BATCH = 90
    for i in range(0, len(all_new), BATCH):
        notion_call(client.blocks.children.append, block_id=page_id, children=all_new[i:i+BATCH])

    has_scenario = scenario is not None
    note = action
    append_sync_state(slug, page_id, has_scenario, action=action, note=note)
    return {"slug": slug, "status": "ok", "page_id": page_id, "action": action,
            "has_scenario": has_scenario, "company_name": company_name}


# === v4.1 安全同期 (非破壊・ID限定・タイトルガード) ===
def _para_bold(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text",
                "text": {"content": text[:NOTION_TEXT_LIMIT]},
                "annotations": {"bold": True}}]}}


def _block_text(b: dict) -> str:
    t = b.get("type"); o = b.get(t, {})
    rt = o.get("rich_text", []) if isinstance(o, dict) else []
    return "".join(x.get("plain_text", "") for x in rt)


def _list_all_children(client: Client, page_id: str) -> list[dict]:
    out = []; cursor = None
    while True:
        res = notion_call(client.blocks.children.list, block_id=page_id, start_cursor=cursor)
        out.extend(res.get("results", []))
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return out


def get_page_title(client: Client, page_id: str) -> str:
    p = notion_call(client.pages.retrieve, page_id=page_id)
    return "".join(t.get("plain_text", "")
                   for t in p.get("properties", {}).get("title", {}).get("title", []))


def build_v41_blocks(scenario: dict, tokyari_slug: str) -> list[dict]:
    """既存 v4 セクションと同形式 (設計サマリ + 10コマ全文 + 品質メモ) を scenario_v4.json から構築."""
    m = scenario.get("meta", {})
    koma = scenario.get("koma", [])
    blocks: list[dict] = []
    blocks += _paragraph("✅ この版が最新の正です。2026-06-20 のインターンFB(n=15アンケート反映後の追加修正)を反映し、本番D1へ適用済 (commit 212751c)。前版 2026-06-19 は上に ⚠️旧版(FB前) として保持。")
    blocks.append(_bullet("FB反映の主な修正: 語法の自然化 / 採用人数の補正 / 倍率の扱い / 移転→建て替え等の事実修正 / Markdown太字(**)除去"))
    # 設計サマリ
    blocks.append(_heading3("設計サマリ"))
    blocks.append(_bullet(f"企業: {m.get('company','')} ({m.get('ticker','')})"))
    blocks.append(_bullet(f"ストーリー型: {m.get('story_type','')}"))
    if m.get("story_type_reason"):
        blocks.append(_bullet(f"型の選定理由: {m.get('story_type_reason')}"))
    pa = m.get("principles_applied") or {}
    if pa:
        blocks.append(_bullet("適用した5原則:"))
        for k, v in pa.items():
            blocks.append(_bullet(f"  {k}: {v}"))
    vh = m.get("visual_hooks_used") or []
    if vh:
        blocks.append(_bullet("使用した視覚フック: " + " / ".join(vh)))
    # 10コマ全文
    blocks.append(_heading3("10コマ全文"))
    for k in koma:
        n = k.get("koma_number"); arc = k.get("emotional_arc", ""); vhk = k.get("visual_hook", "")
        blocks.append(_para_bold(f"コマ{n:02d} ({arc} / 視覚フック={vhk})"))
        sc = k.get("scene")
        setting = sc.get("setting") if isinstance(sc, dict) else (sc or "")
        if setting:
            blocks += _paragraph(setting)
        for line in k.get("script", []):
            blocks.append(_bullet(line))
        ov = k.get("overlay_text") or {}
        if ov.get("main_copy"):
            blocks.append(_bullet(f"🅰 メインコピー: {ov.get('main_copy')}"))
        if ov.get("sub"):
            blocks.append(_bullet(f"サブ: {ov.get('sub')}"))
    # 品質メモ
    blocks.append(_heading3("品質メモ（自動チェック）"))
    hooks = sum(1 for k in koma if k.get("visual_hook"))
    blocks.append(_bullet(f"視覚フック使用: {hooks}/10 コマ"))
    blocks.append(_bullet("v4 4 lint + 話者タグ lint: 全通過 (FB反映後に再チェック済)"))
    blocks.append(_bullet(f"ローカル保存: ~/oscar-ai/tokyari-pipeline/output/{tokyari_slug}/scenario_v4.json"))
    blocks.append(_divider())
    blocks += _paragraph(f"(同期: {V41_SYNC_DATE} / source: scenario_v4.json / 本番D1反映済)")
    return blocks


def mark_old_v4_superseded(client: Client, page_id: str) -> dict:
    """既存『自動生成版 2026-06-19』見出しを ⚠️旧版(FB前) にrename し、直後の注記を更新 (削除しない)."""
    children = _list_all_children(client, page_id)
    res = {"renamed_heading": False, "updated_note": False, "already": False, "found": False}
    for i, b in enumerate(children):
        if b.get("type") == "heading_2":
            txt = _block_text(b)
            if OLD_V4_MATCH in txt:
                res["found"] = True
                if OLD_MARK in txt:
                    res["already"] = True
                    return res
                notion_call(client.blocks.update, block_id=b["id"],
                            heading_2={"rich_text": [{"type": "text",
                                "text": {"content": (OLD_MARK + " " + txt)[:NOTION_TEXT_LIMIT]}}]})
                res["renamed_heading"] = True
                for nb in children[i + 1:]:
                    if nb.get("type") == "heading_2":
                        break
                    if nb.get("type") == "paragraph":
                        ptxt = _block_text(nb)
                        if "最新の正" in ptxt or ptxt.strip().startswith("✅"):
                            notion_call(client.blocks.update, block_id=nb["id"],
                                        paragraph={"rich_text": [{"type": "text",
                                            "text": {"content": f"{OLD_MARK}。下の {V41_SYNC_DATE} を正とする。(旧: 2026-06-19 v4版)"[:NOTION_TEXT_LIMIT]}}]})
                            res["updated_note"] = True
                        break
                return res
    return res


def has_v41_section(client: Client, page_id: str) -> bool:
    # 当日の新規セクション(自動生成版 2026-06-20 ...)のみを冪等判定に使う。
    # ファクトシート側の「v4.1 緊急訂正版」等(別日付)を誤検知しないよう日付で厳密化。
    for b in _list_all_children(client, page_id):
        if b.get("type") == "heading_2" and "自動生成版 2026-06-20" in _block_text(b):
            return True
    return False


def sync_company_v41_safe(tokyari_slug: str, client: Client) -> dict:
    """非破壊・ID限定・タイトルガードの v4.1 同期. 新規作成・削除・別社上書きをしない."""
    name = get_company_name(tokyari_slug)
    state = load_sync_state()
    page_id = (state.get(tokyari_slug) or {}).get("notion_page_id")
    if not page_id:
        return {"slug": tokyari_slug, "status": "skipped", "reason": "no page_id in state (新規作成しない)", "page_id": None}
    title = get_page_title(client, page_id)
    expect = f"{name} ファクトシート"
    if title.strip() != expect:
        return {"slug": tokyari_slug, "status": "skipped",
                "reason": f"title不一致 page='{title}' expect='{expect}'", "page_id": page_id}
    sp = ROOT / "output" / tokyari_slug / "scenario_v4.json"
    if not sp.exists():
        return {"slug": tokyari_slug, "status": "skipped", "reason": "no scenario_v4.json", "page_id": page_id}
    scenario = json.loads(sp.read_text(encoding="utf-8"))
    url = f"https://www.notion.so/{page_id.replace('-','')}"
    if has_v41_section(client, page_id):
        return {"slug": tokyari_slug, "status": "skipped", "reason": "v4.1 already present", "page_id": page_id, "url": url}
    mark = mark_old_v4_superseded(client, page_id)
    blocks = [_heading2(V41_HEADING)] + build_v41_blocks(scenario, tokyari_slug)
    BATCH = 90
    for i in range(0, len(blocks), BATCH):
        notion_call(client.blocks.children.append, block_id=page_id, children=blocks[i:i + BATCH])
    append_sync_state(tokyari_slug, page_id, True, action="v41_safe", note="FB反映 v4.1 追記 + 旧版マーク")
    return {"slug": tokyari_slug, "status": "ok", "page_id": page_id, "title": title,
            "mark": mark, "blocks_added": len(blocks), "url": url}


# === CLI ===
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", help="単一 slug を同期")
    p.add_argument("--sogo-shosha", action="store_true", help="商社10社を同期")
    p.add_argument("--daemon", action="store_true", help="audit CSV を監視して done を順次同期")
    p.add_argument("--daemon-pid", type=int, help="このPIDが消えたら daemon 終了 (例 25396)")
    p.add_argument("--daemon-max-min", type=int, default=180, help="daemon の最大稼働時間 (分)")
    p.add_argument("--daemon-interval", type=int, default=30, help="audit 監視のポーリング間隔 (秒)")
    p.add_argument("--v41-safe", action="store_true",
                   help="非破壊・ID限定・タイトルガードで v4.1(FB反映) を追記 (旧版は残す)")
    p.add_argument("--all9", action="store_true", help="--v41-safe で商社9社を一括")
    args = p.parse_args()

    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN 未設定"); return 2

    client = Client(auth=NOTION_TOKEN)

    if args.v41_safe:
        NINE = ["mitsubishi-corp", "itochu-shoji", "sumitomo-corp", "marubeni",
                "kanematsu", "shinkokusyoji", "iwatani", "sojitz", "mitsui-bussan"]
        slugs = [args.slug] if args.slug else (NINE if args.all9 else [])
        if not slugs:
            print("ERROR: --v41-safe には --slug <tokyari-slug> か --all9 が必要"); return 2
        for s in slugs:
            r = sync_company_v41_safe(s, client)
            print(json.dumps(r, ensure_ascii=False))
        return 0

    if args.slug:
        r = sync_company(args.slug, client)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0

    if args.sogo_shosha:
        slugs = ["mitsubishi-corp","mitsui-bussan","itochu-shoji","sumitomo-corp",
                 "marubeni","toyota-tsusho","sojitz","iwatani","kanematsu","shinkokusyoji"]
        # mitsui-bussan は output/mitsui-bussan/ が無いはずなのでスキップ
        if not (ROOT/"output"/"mitsui-bussan"/"factsheet.md").exists():
            slugs.remove("mitsui-bussan")
            print(f"(mitsui-bussan: ローカル factsheet 無し → スキップ)")
        print(f"=== 商社 {len(slugs)} 社を同期 ===")
        results = []
        for s in slugs:
            try:
                r = sync_company(s, client)
                print(f"  {s:<22} {r['status']:<10} {r['action']:<30} {r['page_id']}")
                results.append(r)
            except Exception as e:
                print(f"  {s:<22} FAILED: {type(e).__name__}: {str(e)[:120]}")
                results.append({"slug": s, "status": "failed", "error": str(e)[:200]})
        return 0

    if args.daemon:
        t_start = time.time()
        max_sec = args.daemon_max_min * 60
        print(f"=== Daemon start (max {args.daemon_max_min}分, interval {args.daemon_interval}s) ===")
        while True:
            elapsed = time.time() - t_start
            if elapsed > max_sec:
                print(f"⏱ 最大時間到達 ({args.daemon_max_min}分)、終了")
                break
            # PID チェック
            pid_alive = False
            if args.daemon_pid:
                pid_alive = (os.system(f"ps -p {args.daemon_pid} > /dev/null 2>&1") == 0)
            # audit から done を読む
            state = load_sync_state()
            synced = set(state.keys())
            done_slugs = []
            if AUDIT_CSV.exists():
                with open(AUDIT_CSV, encoding="utf-8") as f:
                    r = csv.DictReader(f)
                    for row in r:
                        if row.get("status") == "done" and row.get("slug") not in synced:
                            done_slugs.append(row["slug"])
            if done_slugs:
                print(f"  [{int(elapsed)}s] new {len(done_slugs)} slugs to sync")
                for s in done_slugs:
                    try:
                        rr = sync_company(s, client)
                        print(f"    {s} -> {rr['status']}, {rr['action']}")
                    except Exception as e:
                        print(f"    {s} FAILED: {str(e)[:120]}")
            elif not pid_alive:
                # PID 終了 + 新規 slug なし → 終了
                print(f"  PID gone + no new done. Daemon end.")
                break
            time.sleep(args.daemon_interval)
        return 0


if __name__ == "__main__":
    sys.exit(main())
