#!/usr/bin/env python3
"""本番D1のクイズを全社エクスポート→quiz_lintにかける常設経路(本番の品質を本番で測る)。
ローカルv3ファイルでなく live D1 を検証対象にする(v3とD1の乖離で品質を測れない構造穴を塞ぐ)。
入力: live D1(quiz_questions) + corpus台帳(output/<slug>/quiz_corpus_locked_v3.json 無ければ rendered_corpus.json)。
usage:
  python3 tools/_lint_live.py            # 全社。error>0の社を一覧+総error数
  python3 tools/_lint_live.py <slug>     # 1社詳細
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_lint as QL
from _d1 import d1

OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")


def corpus_of(slug):
    for fn in ("quiz_corpus_locked_v3.json", "rendered_corpus.json"):
        p = os.path.join(OUT, slug, fn)
        if os.path.exists(p):
            d = json.load(open(p))
            if fn == "rendered_corpus.json":
                return {u: (v.get("text", "") if isinstance(v, dict) else str(v)) for u, v in d.items()}
            return d
    return {}


def lint_company(slug, rows):
    quiz = []
    for r in rows:
        try:
            opts = json.loads(r["options"])
        except Exception:
            opts = []
        quiz.append({"id": r["id"], "q_text": r.get("q_text") or "", "options": opts, "correct": r["correct"],
                     "category": r.get("category") or "", "source_url": r.get("source_url") or "",
                     "as_of": r.get("as_of") or "", "explanation": r.get("explanation") or "",
                     "difficulty": r.get("difficulty")})
    corpus = corpus_of(slug)
    return QL.run_quiz_lints(quiz, corpus)


def main():
    one = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    where = f" AND set_id='{one}'" if one else ""
    rows = d1(f"SELECT id,set_id,category,q_text,options,correct,source_url,as_of,explanation,difficulty FROM quiz_questions WHERE set_type='company'{where}")
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        by[r["set_id"]].append(r)
    total_err = 0
    bad = []
    for slug, rs in sorted(by.items()):
        rep = lint_company(slug, rs)
        e = rep.get("errors", 0)
        total_err += e
        if e > 0:
            bad.append((slug, e))
            if one:
                for f in rep.get("findings", []):
                    if f.get("severity") == "error":
                        print(f"  [{slug}] {f.get('lint')}: {f.get('detail')}")
    print(f"\n=== live D1 quiz_lint: {len(by)}社 / error社={len(bad)} / 総error={total_err} ===")
    for s, e in sorted(bad, key=lambda x: -x[1])[:30]:
        print(f"  {s}: error{e}")


if __name__ == "__main__":
    main()
