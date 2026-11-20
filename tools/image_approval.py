#!/usr/bin/env python3
"""image_approval — 画像の承認台帳(2026-11-20 オスカー承認の再発防止設計 ■4)。

背景: 人QA待ちの「候補」画像を public/images に commit していたため、7/21 の一括軽量化が作業ツリーの
候補を圧縮して commit → refbump migration で D1 の ref を一括更新 → 未承認の描き直し157コマが本番に出た。
「repo の新しい画像 = 承認済み」ではない。承認は、この台帳(ファイル → git blob hash)だけが表す。

台帳: tools/image_approval_ledger.json
  items[<repo相対パス>][<blob sha1>] = {"by": 承認の経路, "at": ISO時刻, "note": 根拠}
  ・同じファイルに承認済み blob が複数あってよい(元画像と、のちに採用された候補など)。
  ・by には個人名を書かない(公開repo)。経路名(init / CC目視 / 人QA(画像検分タブ) / 派生(圧縮) …)。

守ること(各ツールがこのモジュールを呼ぶ):
  1. 候補は review/candidates/<slug>/panel_NN.<timestamp>.png に置く(public/images には置かない)。
  2. 圧縮など画像を一括で触るツールは、作業ツリーの中身が台帳と一致するファイルだけを対象にする
     (is_approved_file)。触った結果は derived として台帳に追記(approve(..., derived_from=元blob))。
  3. D1 の ref を動かす migration は、新しい ref の画像が台帳と一致しなければ止まる(assert_ref_approved)。
  4. 検分で「採用」になった候補は approve で台帳に追加してから public/images に昇格する(promote_candidate)。

CLI:
  python3 tools/image_approval.py init --exclude <img157.json> [--approved-by-cc kanigen]   # 初期化(1回)
  python3 tools/image_approval.py verify-ref <ref> [--slugs a,b]   # その ref に動かしてよいか(未承認があれば exit 3)
  python3 tools/image_approval.py check-worktree [--slugs a,b]     # 作業ツリーの未承認ファイル一覧
  python3 tools/image_approval.py approve <path> (--ref R | --file) --by 経路 --note 根拠
  python3 tools/image_approval.py stats | --selftest
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
LEDGER = TOOLS / "image_approval_ledger.json"
CAND_DIR = "review/candidates"
URL_RE = re.compile(r"10koma-shukatsu@([0-9A-Za-z_.-]+)/(public/images/[^?#\s]+)")


class ImageNotApproved(RuntimeError):
    """台帳に無い画像を本番/一括処理に使おうとした。"""


def _git(*a, check=True, inp=None):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, input=inp)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a[:3])} 失敗: {r.stderr[-300:]}")
    return r


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# ── 台帳 ────────────────────────────────────────────────────────────────
def load(allow_missing=False) -> dict:
    if not LEDGER.exists():
        if allow_missing:
            return {"_doc": "", "items": {}}
        raise ImageNotApproved(f"承認台帳が無い: {LEDGER}(空=失敗。未初期化なら init)")
    d = json.loads(LEDGER.read_text(encoding="utf-8"))
    if not d.get("items"):
        raise ImageNotApproved("承認台帳が空(空=失敗。全部未承認として扱わず止める)")
    return d


def save(d: dict) -> None:
    d["items"] = {k: dict(sorted(v.items())) for k, v in sorted(d["items"].items())}
    LEDGER.write_text(json.dumps(d, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")


def approve(path: str, blob: str, by: str, note: str, derived_from: str | None = None, d: dict | None = None,
            write=True) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", blob or ""):
        raise ValueError(f"blob が40桁でない: {blob!r}")
    if not path.startswith("public/images/"):
        raise ValueError(f"承認対象は public/images/ 配下のみ: {path}")
    d = d if d is not None else load(allow_missing=True)
    ent = {"by": by, "at": _now(), "note": note}
    if derived_from:
        ent["derived_from"] = derived_from
    d["items"].setdefault(path, {})[blob] = ent
    if write:
        save(d)
    return d


# ── blob ────────────────────────────────────────────────────────────────
def blobs_at(ref: str, paths: list[str]) -> dict:
    """ref 時点の各パスの blob(無ければ None)。cat-file --batch-check で一括。"""
    if not paths:
        return {}
    inp = "".join(f"{ref}:{p}\n" for p in paths)
    out = _git("cat-file", "--batch-check", inp=inp).stdout.splitlines()
    if len(out) != len(paths):
        raise RuntimeError(f"cat-file 応答数 {len(out)} != {len(paths)}")
    res = {}
    for p, line in zip(paths, out):
        parts = line.split()
        res[p] = parts[0] if len(parts) >= 2 and parts[1] == "blob" else None
    return res


def blob_of_file(path: str | Path) -> str:
    p = Path(path)
    p = p if p.is_absolute() else REPO / p
    return _git("hash-object", str(p)).stdout.strip()


def is_approved(path: str, blob: str | None, d: dict | None = None) -> bool:
    d = d if d is not None else load()
    return bool(blob) and blob in d["items"].get(path, {})


def is_approved_file(path: str | Path, d: dict | None = None) -> bool:
    """作業ツリーのファイルの中身が台帳と一致するか(一括ツールの対象判定)。"""
    p = Path(path)
    rel = str(p.relative_to(REPO)) if p.is_absolute() else str(p)
    return is_approved(rel, blob_of_file(rel), d)


def assert_ref_approved(ref: str, paths: list[str], d: dict | None = None) -> None:
    """D1 の ref を ref に動かす前の関所。1件でも台帳と一致しなければ ImageNotApproved。"""
    d = d if d is not None else load()
    b = blobs_at(ref, paths)
    bad = [p for p in paths if not is_approved(p, b[p], d)]
    if bad:
        raise ImageNotApproved(f"ref {ref[:12]} の画像 {len(bad)}/{len(paths)} 件が承認台帳と一致しない → 止める: "
                               + ", ".join(bad[:12]) + (" …" if len(bad) > 12 else ""))


def parse_url(url: str):
    m = URL_RE.search(url or "")
    return (m.group(1), m.group(2)) if m else (None, None)


# ── 候補(review/candidates) ───────────────────────────────────────────────
def candidate_rel(slug: str, koma: int, ts: str | None = None) -> str:
    ts = ts or datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{CAND_DIR}/{slug}/panel_{int(koma):02d}.{ts}.png"


def promote_candidate(cand_ref: str, cand_path: str, slug: str, koma: int, by: str, note: str) -> tuple[str, str]:
    """承認済み候補を public/images へ昇格: 台帳に追記 → ファイルを置く。commit/push は呼び出し側。
    返り値 (public/images の相対パス, blob)。cand_path は review/candidates/… でも旧方式の public/images/… でもよい。"""
    dst = f"public/images/{slug}/panel_{int(koma):02d}.png"
    blob = blobs_at(cand_ref, [cand_path])[cand_path]
    if not blob:
        raise ImageNotApproved(f"候補が見つからない: {cand_ref[:12]}:{cand_path}")
    data = subprocess.run(["git", "cat-file", "blob", blob], cwd=REPO, capture_output=True, check=True).stdout
    (REPO / dst).parent.mkdir(parents=True, exist_ok=True)
    (REPO / dst).write_bytes(data)
    if blob_of_file(dst) != blob:
        raise RuntimeError("昇格後の blob が候補と一致しない")
    d = load(allow_missing=True)
    approve(dst, blob, by, f"{note}(候補 {cand_ref[:12]}:{cand_path})", d=d)
    return dst, blob


# ── 本番参照の列挙 ───────────────────────────────────────────────────────
def live_refs():
    """本番 D1 が参照している (ref, path) を列挙。personas は @main 参照のため origin/main で解決。"""
    sys.path.insert(0, str(TOOLS))
    import deploy_salary as D
    q = [("company_panels", "image_url", "company_id || '#' || panel_num"),
         ("companies", "thumbnail_url", "id"),
         ("industries", "thumbnail_url", "id"),
         ("personas", "image_url", "persona_id")]
    out = []
    for t, c, key in q:
        n = D.d1_query(f"SELECT COUNT(*) n FROM {t} WHERE {c} LIKE '%/public/images/%'")[0]["n"]
        rows = D.d1_query(f"SELECT {key} AS k, {c} AS u FROM {t} WHERE {c} LIKE '%/public/images/%'")
        if len(rows) != n:
            raise RuntimeError(f"{t}.{c}: 取得 {len(rows)}/{n}(空≠不在) → 止める")
        for r in rows:
            ref, path = parse_url(r["u"])
            if ref:
                out.append((t, r["k"], ref, path))
    return out


def _resolve(ref: str) -> str:
    if ref == "main":
        _git("fetch", "-q", "origin", "main", check=False)
        return _git("rev-parse", "origin/main").stdout.strip()
    return _git("rev-parse", f"{ref}^{{commit}}").stdout.strip()


# ── CLI ─────────────────────────────────────────────────────────────────
def cmd_init(argv):
    if LEDGER.exists():
        raise SystemExit(f"台帳が既にある: {LEDGER}(init は1回だけ。上書きしない)")
    excl_file = argv[argv.index("--exclude") + 1]
    excl = json.load(open(excl_file))
    if len(excl) != 157:
        raise SystemExit(f"除外リストが157件でない({len(excl)})→ 止める")
    # 除外は (ファイル, 候補の中身=blob) で判定(ref の短縮/40桁表記の違いに左右されない)
    ex_blobs = set()
    for x in excl:
        b = blobs_at(_resolve(x["served_ref"]), [x["file"]])[x["file"]]
        if not b:
            raise SystemExit(f"除外対象の blob を解決できない {x['file']}@{x['served_ref']}")
        ex_blobs.add((x["file"], b))
    if len(ex_blobs) != 157:
        raise SystemExit(f"除外 blob が157件でない({len(ex_blobs)})→ 止める")
    cc = set(argv[argv.index("--approved-by-cc") + 1].split(",")) if "--approved-by-cc" in argv else set()
    refs = live_refs()
    by_ref = {}
    for t, k, ref, path in refs:
        by_ref.setdefault(ref, set()).add(path)
    d = {"_doc": __doc__.split("\n\n")[0] + " 初期化=本番D1が参照中の画像から未承認157(人QA待ち候補)を除いたもの。",
         "items": {}}
    excluded = set()
    for ref, paths in by_ref.items():
        full = _resolve(ref)
        bl = blobs_at(full, sorted(paths))
        for p, b in bl.items():
            if not b:
                raise SystemExit(f"本番参照先が git に無い {ref}:{p} → 止める(空≠不在)")
            if (p, b) in ex_blobs:
                excluded.add((p, b))
                continue
            slug = p.split("/")[2]
            if slug in cc and "/personas/" not in p:
                by, note = "CC目視", f"2026-11-20 CCが10コマを目視確認(本番 @{ref[:12]})"
            else:
                by, note = "init(本番配信中)", f"2026-11-20 本番D1参照 @{ref[:12]}・未承認157を除外"
            approve(p, b, by, note, d=d, write=False)
    if len(excluded) != 157:
        raise SystemExit(f"除外できたのが {len(excluded)}/157 件 → 本番の ref が想定とずれている。止める")
    # 除外した blob が別経路(サムネ等)で承認に紛れていないこと
    leak = [p for p, b in ex_blobs if b in d["items"].get(p, {})]
    if leak:
        raise SystemExit(f"除外 blob が承認に混入: {leak[:5]}")
    save(d)
    n = sum(len(v) for v in d["items"].values())
    print(f"init: 本番参照 {len(refs)} 行 → 承認 {n} blob / {len(d['items'])} ファイル・除外 {len(excluded)}")
    return 0


def cmd_verify_ref(argv):
    ref = argv[0]
    slugs = set(argv[argv.index("--slugs") + 1].split(",")) if "--slugs" in argv else None
    paths = sorted({p for _, _, _, p in live_refs() if slugs is None or p.split("/")[2] in slugs})
    try:
        assert_ref_approved(_resolve(ref), paths)
    except ImageNotApproved as e:
        print("❌", e)
        return 3
    print(f"OK: {ref[:12]} の {len(paths)} ファイルはすべて承認台帳と一致")
    return 0


def cmd_check_worktree(argv):
    slugs = set(argv[argv.index("--slugs") + 1].split(",")) if "--slugs" in argv else None
    d = load()
    files = sorted(str(p.relative_to(REPO)) for p in (REPO / "public/images").glob("*/**/*.png")
                   if slugs is None or p.relative_to(REPO / "public/images").parts[0] in slugs)
    bad = [f for f in files if not is_approved(f, blob_of_file(f), d)]
    print(f"作業ツリー {len(files)} ファイル中 未承認 {len(bad)}")
    for f in bad[:40]:
        print("  ", f)
    return 1 if bad else 0


def cmd_approve(argv):
    path = argv[0]
    by = argv[argv.index("--by") + 1]
    note = argv[argv.index("--note") + 1]
    blob = blobs_at(_resolve(argv[argv.index("--ref") + 1]), [path])[path] if "--ref" in argv else blob_of_file(path)
    if not blob:
        raise SystemExit("blob を解決できない")
    approve(path, blob, by, note)
    print("approved", path, blob[:12], by)
    return 0


def cmd_stats(_argv):
    d = load()
    from collections import Counter
    c = Counter(e["by"] for v in d["items"].values() for e in v.values())
    print(f"files {len(d['items'])} / blobs {sum(len(v) for v in d['items'].values())} / by {dict(c)}")
    return 0


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("OK " if cond else "NG ") + name)
        ok = ok and bool(cond)
    d = {"items": {}}
    b1, b2 = "a" * 40, "b" * 40
    approve("public/images/x/panel_01.png", b1, "t", "n", d=d, write=False)
    chk("承認済み blob は通る", is_approved("public/images/x/panel_01.png", b1, d))
    chk("別 blob(候補)は通らない", not is_approved("public/images/x/panel_01.png", b2, d))
    chk("台帳に無いファイルは通らない", not is_approved("public/images/y/panel_01.png", b1, d))
    chk("blob None は通らない", not is_approved("public/images/x/panel_01.png", None, d))
    try:
        approve("review/candidates/x/panel_01.1.png", b1, "t", "n", d=d, write=False)
        chk("候補パスは承認対象にできない", False)
    except ValueError:
        chk("候補パスは承認対象にできない", True)
    chk("候補パスは review/candidates 配下", candidate_rel("x", 3, "20260101").startswith("review/candidates/x/panel_03."))
    chk("URL から ref/path", parse_url("https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@abc123/public/images/x/panel_01.png")
        == ("abc123", "public/images/x/panel_01.png"))
    head = _git("rev-parse", "HEAD").stdout.strip()
    try:
        assert_ref_approved(head, ["public/images/__nope__/panel_01.png"], d)
        chk("未承認を含む ref は止まる", False)
    except ImageNotApproved:
        chk("未承認を含む ref は止まる", True)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--selftest":
        return selftest()
    cmds = {"init": cmd_init, "verify-ref": cmd_verify_ref, "check-worktree": cmd_check_worktree,
            "approve": cmd_approve, "stats": cmd_stats}
    if argv[0] not in cmds:
        raise SystemExit(__doc__)
    return cmds[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
