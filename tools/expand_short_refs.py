#!/usr/bin/env python3
"""expand_short_refs — D1 company_panels.image_url の短縮SHA(7桁等)を、同じコミットの40桁SHAに置き換える(2026-11-20)。

なぜ: jsDelivr は40桁refを immutable(1年)で、短縮refを s-maxage=43200(12時間)で返す。短縮refの行は
12時間ごとにGitHubまで取りに行き直し、repoが50MB上限を超えているため「Package size exceeded」403 を引きやすい。
同じコミットの別表記にするだけ=画像の中身は変わらない(git rev-parse で一意に解決し、そのrefにファイルが在ることを確認)。
image_url だけを SET し、旧値一致条件付き(WHERE image_url IS 旧値)。backup → canary(前後) → changes 照合。
  python3 tools/expand_short_refs.py          # dry(計画のみ)
  python3 tools/expand_short_refs.py --live
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import deploy_salary as D  # noqa: E402
import scenario_writer as SW  # noqa: E402

PAT = re.compile(r"@([0-9a-f]{4,39})/(public/images/.+)$")


def q(s):
    return "'" + s.replace("'", "''") + "'"


def plan():
    n = D.d1_query("SELECT COUNT(*) n FROM company_panels")[0]["n"]
    rows = D.d1_query("SELECT company_id,panel_num,image_url FROM company_panels")
    if not rows or len(rows) != n:
        raise SystemExit(f"D1取得件数不一致 {len(rows) if rows else 0}/{n}(空≠不在)")
    out = []
    for r in rows:
        m = PAT.search(r["image_url"] or "")
        if not m:
            continue
        ref, f = m.groups()
        p = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify", "--quiet", ref + "^{commit}"],
                           capture_output=True, text=True)
        full = p.stdout.strip()
        if p.returncode != 0 or len(full) != 40:
            raise SystemExit(f"{r['company_id']}#{r['panel_num']}: {ref} を一意に解決できない → 止める")
        if subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{full}:{f}"]).returncode != 0:
            raise SystemExit(f"{r['company_id']}#{r['panel_num']}: {full}:{f} が無い → 止める")
        new = r["image_url"].replace("@" + ref + "/", "@" + full + "/")
        out.append((r["company_id"], int(r["panel_num"]), r["image_url"], new))
    return out


def main(argv):
    p = plan()
    print(f"短縮ref {len(p)} 行 / {len({x[0] for x in p})} 社")
    if "--live" not in argv or not p:
        for x in p[:5]:
            print("  ", x[0], x[1], x[2][-70:], "→", x[3][-70:])
        return 0
    sql = [f"UPDATE company_panels SET image_url={q(new)} WHERE company_id={q(c)} AND panel_num={n} AND image_url IS {q(old)};"
           for c, n, old, new in p]
    ts = time.strftime("%Y%m%d_%H%M%S")
    (SW.BACKUP / "d1").mkdir(parents=True, exist_ok=True)
    (SW.BACKUP / "d1" / f"expand_short_refs_{ts}.json").write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    cb = SW._canary_snapshot(f"expand_short_refs_before_{ts}")
    changes = SW._exec(sql)
    ca = SW._canary_snapshot(f"expand_short_refs_after_{ts}")
    changed = SW._canary_changed(cb, ca)
    expect = sorted({x[0] for x in p})
    print(f"changes={changes}(期待 {len(sql)}) canary変化 {len(changed)}社 / 期待 {len(expect)}社 "
          f"UNEXPECTED={sorted(set(changed) - set(expect))}")
    if changes != len(sql) or set(changed) - set(expect):
        raise SystemExit("❌ 件数不一致 または 対象外の社が変化 → 要調査")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
