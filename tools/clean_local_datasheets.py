#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ローカル全 datasheet.json を今日D1に適用したのと同じルールで一括浄化(根を断つ)。
除去: 人名trivia(「◯◯は誰」/「の名前:」等 氏名を答えにするもの) / 採用サイトメタ / 別法人(IBM Credit確定分)。
年号羅列は残す。全ファイルbackup→浄化→社別集計。all-empty社は報告(浄化はする)。"""
import json, os, sys, glob, re, shutil, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_fanout as q

OUT = q.OUT
BK = os.path.join(OUT, f"_datasheet_backup_{time.strftime('%Y%m%d_%H%M%S')}")
RECRUIT = ["選考フロー", "選考プロセス", "選考ステップ", "採用フロー", "エントリーシート", "エントリー",
           "募集要項", "採用サイト", "新卒採用サイト", "採用情報サイト", "採用活動", "採用選考方法",
           "インターンシップ", "マイページ", "本エントリー", "採用担当者", "採用ページ", "採用予定数"]


def junk_reason(fact):
    t = str(fact or "")
    if "は誰" in t:
        return "person_dare"           # 「◯◯は誰: 人名」
    if "の名前:" in t or "の氏名:" in t or re.search(r"の名前は[^。]{1,12}(氏|さん|である|です)", t):
        return "person_name"           # 氏名を答えにするもの
    if any(k in t for k in RECRUIT):
        return "recruit_meta"
    if "日本アイ・ビー・エム・クレジット" in t or "コンピューター・システム・リース株式会社" in t:
        return "other_entity"          # 別法人(今日確定のIBM Credit)
    return None


def main():
    files = sorted(glob.glob(os.path.join(OUT, "*/datasheet.json")))
    os.makedirs(BK, exist_ok=True)
    from collections import Counter
    tot = Counter()
    per = []
    allempty = []
    changed = 0
    for f in files:
        slug = os.path.basename(os.path.dirname(f))
        try:
            ds = json.load(open(f))
        except Exception:
            continue
        shutil.copy(f, os.path.join(BK, slug + ".datasheet.json"))   # backup
        secs = ds.get("sections", {})
        if not isinstance(secs, dict):
            continue
        removed = Counter()
        for k in list(secs.keys()):
            keep = []
            for it in (secs[k] or []):
                r = junk_reason(it.get("fact", ""))
                if r:
                    removed[r] += 1; tot[r] += 1
                else:
                    keep.append(it)
            secs[k] = keep
        if sum(removed.values()) > 0:
            changed += 1
            json.dump(ds, open(f, "w"), ensure_ascii=False)
            per.append((slug, ds.get("name", slug), dict(removed)))
        if all(len(v) == 0 for v in secs.values()):
            allempty.append(slug)
    print(f"=== ローカル datasheet 浄化 (全{len(files)}ファイル) ===")
    print(f"backup: {BK}")
    print(f"変更社: {changed} / 除去item合計: {sum(tot.values())}")
    print(f"  内訳: {dict(tot)}")
    print(f"全セクション空になった社: {len(allempty)} {allempty[:10]}")
    print(f"\n除去多い順 上位15社:")
    for slug, name, rm in sorted(per, key=lambda x: -sum(x[2].values()))[:15]:
        print(f"  {name}({slug}): -{sum(rm.values())} {rm}")
    json.dump([{"slug": s, "name": n, "removed": rm} for s, n, rm in per],
              open(os.path.join(os.environ.get("TK_SCRATCH") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / ".backups" / "scratch"), "local_clean_manifest.json"), "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
