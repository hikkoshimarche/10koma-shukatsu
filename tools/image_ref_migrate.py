#!/usr/bin/env python3
"""image_ref_migrate — D1 の画像 ref を一括で動かす migration の唯一の生成口(2026-11-20 ■4)。

7/21 の refbump は「全行の @ref を新 commit に置換する」SQL 1文で、新 ref の public/images に
人QA待ちの候補が入っていたため未承認157コマが本番に出た。以後、ref の一括移動はこのツールで作る:
  ・対象行ごとに 旧ref の blob と 新ref の blob を比べ、変わる行だけを UPDATE(旧URL一致条件付き)
  ・変わる行の新 blob が承認台帳(image_approval)に無ければ、SQL を1行も出さずに exit 3
  ・画像の中身が変わらない行(ref表記だけ変わる)も出すのは --include-same のとき(40桁化など)
SQL を書き出すだけで D1 は叩かない。適用は wrangler d1 execute --config api/wrangler.toml --file、
前後に tools/_canary.py snapshot/diff。

  python3 tools/image_ref_migrate.py --ref <commit> [--slugs a,b] [--include-same] --out api/migration_xxx.sql
"""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import image_approval as IA  # noqa: E402


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def main(argv):
    if "--ref" not in argv or "--out" not in argv:
        raise SystemExit(__doc__)
    new_ref = IA._resolve(argv[argv.index("--ref") + 1])
    out = Path(argv[argv.index("--out") + 1])
    slugs = set(argv[argv.index("--slugs") + 1].split(",")) if "--slugs" in argv else None
    include_same = "--include-same" in argv
    tables = {"company_panels": ("image_url", "company_id || '#' || panel_num"),
              "companies": ("thumbnail_url", "id")}
    rows = [r for r in IA.live_refs() if r[0] in tables and r[2] != "main"
            and (slugs is None or r[3].split("/")[2] in slugs)]
    if not rows:
        raise SystemExit("対象行が0件(空=失敗。slug/条件を確認)")
    d = IA.load()
    sql, changed, same, bad = [], 0, 0, []
    for t, key, old_ref, path in rows:
        ob = IA.blobs_at(IA._resolve(old_ref), [path])[path]
        nb = IA.blobs_at(new_ref, [path])[path]
        if not nb:
            bad.append(f"{path}(新refに無い)")
            continue
        if nb == ob:
            same += 1
            if not include_same:
                continue
        elif not IA.is_approved(path, nb, d):
            bad.append(path)
            continue
        else:
            changed += 1
        col = tables[t][0]
        old_url_like = f"%10koma-shukatsu@{old_ref}/{path}"
        new_url_expr = (f"substr({col},1,instr({col},'10koma-shukatsu@')+15) || {q(new_ref)} || "
                        f"substr({col}, instr({col},'/public/images/'))")
        where = (f"company_id={q(key.split('#')[0])} AND panel_num={int(key.split('#')[1])}"
                 if t == "company_panels" else f"id={q(key)}")
        sql.append(f"UPDATE {t} SET {col}={new_url_expr} WHERE {where} AND {col} LIKE {q(old_url_like)};")
    if bad:
        print(f"❌ 新 ref {new_ref[:12]} の画像 {len(bad)} 件が承認台帳と一致しない → SQL を出さない(止める)")
        for b in bad[:30]:
            print("   ", b)
        print("   人QAで採用したものは image_approval.py approve で台帳に入れてから再実行。")
        return 3
    if not sql:
        print(f"変更なし(中身が変わる行 0・同一 {same})")
        return 0
    out.write_text("-- image_ref_migrate: 新ref " + new_ref + f" / 変更 {changed} 行・同一 {same if include_same else 0} 行\n"
                   + "\n".join(sql) + "\n", encoding="utf-8")
    print(f"OK: {out}  UPDATE {len(sql)} 文(中身が変わる {changed}・同一 {same if include_same else 0})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
