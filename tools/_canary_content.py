#!/usr/bin/env python3
"""会社別コンテンツ表の canary(2026-11-20)。_canary.py は companies+company_panels だけを見るため、
datasheets / es_kits / quiz_questions / room_personas / personas / persona_avatars / company_selection への
書込では「対象外の社が変わっていないか」を検知できなかった。それを補う。

大きい本文(system_prompt / fact_pack_json)は全文を落とさず、長さ+先頭/末尾64字+時刻の指紋で比較する
(本番D1から数十MBを毎回取得しないため)。小さい表は全列を比較する。
  python3 tools/_canary_content.py snapshot <out.json>
  python3 tools/_canary_content.py diff <before.json> <after.json> --expect kanigen[,slug2]
diff は 期待社以外が 変化/追加/消滅 したら exit 1(UNEXPECTED を表示)。
"""
import hashlib
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _d1 import d1  # noqa: E402


def FP(col):
    """長文列の指紋(SQL側で作る)。"""
    return (f"LENGTH(IFNULL({col},'')) || ':' || substr(IFNULL({col},''),1,64) || '…' || "
            f"substr(IFNULL({col},''),-64)")


TABLES = {
    # 表名: (会社キー列, SELECT 列式)
    "datasheets": ("company_id", "company_id, data, updated_at"),
    "es_kits": ("company_id", "company_id, data, updated_at"),
    "quiz_questions": ("set_id", "set_id, id, category, q_text, options, correct, explanation, source_url, as_of, ord, difficulty"),
    "company_selection": ("company_id", "*"),
    "persona_avatars": ("company", "*"),
    "personas": ("company_id", f"company_id, persona_id, role_code, display_name, position, short_description, image_url, is_active, updated_at, {FP('system_prompt')} AS sp_fp"),
    "room_personas": ("company_slug", f"company_slug, role, persona_name, status, created_at, {FP('system_prompt')} AS sp_fp, {FP('fact_pack_json')} AS fp_fp"),
}


def snapshot():
    out = {}
    for t, (key, cols) in TABLES.items():
        where = " WHERE set_type='company'" if t == "quiz_questions" else ""
        n = d1(f"SELECT COUNT(*) n FROM {t}{where}")[0]["n"]
        rows = d1(f"SELECT {cols} FROM {t}{where}")
        if len(rows) != n:
            raise SystemExit(f"{t}: 取得 {len(rows)}/{n} 件(空≠不在・取得失敗) → 止める")
        by = {}
        for r in rows:
            by.setdefault(r[key], []).append(json.dumps(r, ensure_ascii=False, sort_keys=True))
        out[t] = {k: hashlib.sha256("\n".join(sorted(v)).encode()).hexdigest() for k, v in by.items()}
        out[t]["__count__"] = n
    return out


def diff(b, a, expect):
    unexpected = {}
    changed_all = {}
    for t in TABLES:
        bt, at = b.get(t, {}), a.get(t, {})
        keys = (set(bt) | set(at)) - {"__count__"}
        ch = sorted(k for k in keys if bt.get(k) != at.get(k))
        changed_all[t] = ch
        un = [k for k in ch if k not in expect]
        if un:
            unexpected[t] = un
    return changed_all, unexpected


def main(argv):
    if argv[0] == "snapshot":
        s = snapshot()
        json.dump(s, open(argv[1], "w"), ensure_ascii=False)
        print("snapshot:", {t: v["__count__"] for t, v in s.items()}, "->", argv[1])
        return 0
    if argv[0] == "diff":
        expect = set(argv[argv.index("--expect") + 1].split(",")) if "--expect" in argv else set()
        ch, un = diff(json.load(open(argv[1])), json.load(open(argv[2])), expect)
        print("changed:", {t: v for t, v in ch.items() if v})
        print("UNEXPECTED:", un or 0)
        return 1 if un else 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
