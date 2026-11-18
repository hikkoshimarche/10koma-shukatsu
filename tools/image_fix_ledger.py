"""image_fix_ledger.py — 画像自動修正の試行台帳(slug#koma 単位・日付リセットなし)。

2026-11-18 是正 B。ibm-consulting koma08 が 311回 再生成→commit→push→D1失敗 を繰り返した真因の一つは、
per_koma カウンタが run_batch 末尾の save_state でしか保存されず、途中の例外で一度も永続化されなかったこと。
この台帳は **生成の前に加算して即保存** する(原子的書込)。例外で落ちても試行は必ず残る。

ルール:
  - begin(key) を生成直前に呼ぶ → attempts+1 を即保存
  - succeed(key, sha) で解消(status=resolved)
  - fail(key, err) で失敗記録。未反映の試行が MAX_ATTEMPTS(既定3) に達したら status=human_review へ移し、
    スプシ(commonfix: [要人レビュー:画像自動上限])に起票。以後 blocked() が True で自動処理から外れる
  - 起票に失敗しても human_review は維持(ticketed=False)→ 次回 retry_tickets() で再起票。握り潰さない
  - 人が直した後の再開: release(key)(手動)。台帳から消すのではなく status=released と履歴を残す
ファイル: tools/.image_fix_attempts.json(.gitignore 済。public repo に出さない)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

LEDGER = Path(__file__).resolve().parent / ".image_fix_attempts.json"
MAX_ATTEMPTS = int(os.environ.get("IMG_FIX_MAX_ATTEMPTS", "3"))


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def load() -> dict:
    if not LEDGER.exists():
        return {}
    # 壊れた台帳を「空=初回」と解釈しない(それが今回のループの型)。読めなければ例外で止める。
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _save(d: dict) -> None:
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, LEDGER)  # 原子的置換(書込途中のクラッシュで台帳を壊さない)


def key(slug, koma) -> str:
    return f"{slug}#{int(koma)}"


def get(k: str) -> dict:
    return load().get(k, {})


def blocked(k: str) -> tuple[bool, str]:
    e = get(k)
    if e.get("status") == "human_review":
        return True, f"human_review(未反映{e.get('attempts', 0)}回)→自動処理対象外"
    if e.get("status") != "resolved" and e.get("attempts", 0) >= MAX_ATTEMPTS:
        return True, f"試行上限 {e.get('attempts')}>={MAX_ATTEMPTS}(未反映)"
    return False, "ok"


def begin(k: str, kind: str, detail: str = "", company: str = "") -> int:
    """生成直前に呼ぶ。加算して即保存し、加算後の試行回数を返す。"""
    d = load()
    e = d.setdefault(k, {"attempts": 0, "first": _now(), "status": "active", "history": []})
    if e.get("status") in ("resolved", "released"):
        e["status"] = "active"          # 新しいFBで再度対象になった
        e["attempts"] = 0
    e["attempts"] = e.get("attempts", 0) + 1
    e["last"] = _now()
    e["kind"] = kind
    e["company"] = company or e.get("company", "")
    e["detail"] = (detail or e.get("detail", ""))[:200]
    e["history"] = (e.get("history", []) + [{"t": _now(), "ev": "begin", "n": e["attempts"]}])[-30:]
    _save(d)
    return e["attempts"]


def note(k: str, **kw) -> None:
    d = load()
    e = d.setdefault(k, {"attempts": 0, "first": _now(), "status": "active", "history": []})
    e.update(kw)
    e["history"] = (e.get("history", []) + [{"t": _now(), "ev": "note", **{x: str(y)[:80] for x, y in kw.items()}}])[-30:]
    _save(d)


def succeed(k: str, sha: str = "") -> None:
    d = load()
    e = d.setdefault(k, {"attempts": 0, "first": _now(), "history": []})
    e.update(status="resolved", resolved_at=_now(), resolved_sha=sha, last_error=None)
    e["history"] = (e.get("history", []) + [{"t": _now(), "ev": "resolved", "sha": sha}])[-30:]
    _save(d)


def fail(k: str, err: str, gas=None) -> dict:
    """失敗を記録。未反映試行が上限に達したら human_review へ移し起票。entry を返す。"""
    d = load()
    e = d.setdefault(k, {"attempts": 0, "first": _now(), "status": "active", "history": []})
    e["last_error"] = str(err)[:300]
    e["history"] = (e.get("history", []) + [{"t": _now(), "ev": "fail", "err": str(err)[:120]}])[-30:]
    if e.get("attempts", 0) >= MAX_ATTEMPTS and e.get("status") != "human_review":
        e["status"] = "human_review"
        e["human_review_at"] = _now()
        e["ticketed"] = False
    _save(d)
    if e.get("status") == "human_review" and not e.get("ticketed") and gas is not None:
        _ticket(k, e, gas)
    return e


def _ticket(k: str, e: dict, gas) -> bool:
    slug, koma = k.split("#")
    rule = (f"[要人レビュー:画像自動上限] {e.get('company') or slug} koma{koma}: "
            f"自動修正{e.get('attempts')}回未反映→自動処理から除外。最終エラー: {str(e.get('last_error'))[:80]}")
    try:
        r = gas({"mode": "addcommonfix", "scope": "system", "rule": rule,
                 "note": "phase_c 試行台帳(tools/.image_fix_attempts.json)。人が直したら image_fix_ledger.release で再開"})
        ok = isinstance(r, dict) and r.get("ok", True) is not False
    except Exception as ex:
        ok = False
        r = f"{type(ex).__name__}: {ex}"
    d = load()
    d[k]["ticketed"] = bool(ok)
    d[k]["ticket_result"] = str(r)[:160]
    _save(d)
    return ok


def retry_tickets(gas) -> int:
    n = 0
    for k, e in load().items():
        if e.get("status") == "human_review" and not e.get("ticketed"):
            n += _ticket(k, e, gas)
    return n


def release(k: str, by: str = "manual") -> None:
    d = load()
    e = d[k]
    e.update(status="released", released_at=_now(), released_by=by, attempts=0)
    e["history"] = (e.get("history", []) + [{"t": _now(), "ev": "released", "by": by}])[-30:]
    _save(d)


def summary() -> dict:
    d = load()
    rep = [k for k, e in d.items() if e.get("status") not in ("resolved", "released") and e.get("attempts", 0) >= 2]
    return {"total": len(d),
            "human_review": sorted(k for k, e in d.items() if e.get("status") == "human_review"),
            "repeating": sorted(rep),
            "unticketed": sorted(k for k, e in d.items() if e.get("status") == "human_review" and not e.get("ticketed"))}


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "release":
        release(sys.argv[2]); print("released", sys.argv[2])
    else:
        print(json.dumps(summary(), ensure_ascii=False, indent=1))
