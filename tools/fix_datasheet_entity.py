#!/usr/bin/env python3
"""(c) datasheet エンティティ汚染 監査＋修正。子会社/銀行/事業会社のslugに 親会社/持株/連結 の財務値が
混入している datasheet を機械検出し、当該汚染factを非表示化(除去)。正しい主体の一次値が別途取れれば差替(手動)。
検出信号: ①fact本文が他社(親/持株)名を名指し ②大額財務値が他社datasheetと重複 ③子会社slug+持株メトリクス(親会社株主に帰属/HD・FG名/src=持株ドメイン)。
出力: 変更datasheet.json + .backups + scratchpad/dsentity_update.sql。--dry で判定のみ。
"""
import json, os, sys, re, glob, subprocess
from collections import defaultdict

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
UPD = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/dsentity_update.sql"
SEC_MAP = {"事業内容・セグメント": "事業", "主要財務": "財務", "社風・求める人物像": "社風", "沿革・基本情報": "沿革"}

# fact が「持株/親会社」エンティティを名指しする形(自身の連結メトリクスではなく他主体)
HOLDING_ENTITY = re.compile(r"[一-龥ァ-ヶA-Za-zＡ-Ｚ]{1,12}(ホールディングス|フィナンシャル・?グループ)|"
                            r"[一-龥ァ-ヶA-Za-z]{2,10}グループの(連結|売上)")
HOLDING_SRC = re.compile(r"smfg\.co\.jp|mufg\.jp")                 # 持株会社IRドメイン(子会社datasheetのsrcにあれば混入)
# ownが子会社形態(自身が上場親会社の『三菱商事/住友商事/ゆうちょ』は連結値が正当なので、名指し or 値重複 or 持株srcで判定)
SUB_NAME = re.compile(r"銀行|信託|証券|商事|自動織機|生命|海上")
BIGYEN = re.compile(r"([\d,]{7,})\s*百万円")


def _load():
    data, name2slug = {}, {}
    for f in glob.glob(OUT + "/*/datasheet.json"):
        s = os.path.basename(os.path.dirname(f))
        if s.startswith("industry"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        data[s] = d
        nm = (d.get("name") or "").replace("株式会社", "").replace("・", "").strip()
        if len(nm) >= 3:
            name2slug[nm] = s
    return data, name2slug


def _big_values(d):
    vals = set()
    for it in d.get("sections", {}).get("主要財務", []):
        for m in BIGYEN.findall(it.get("fact", "") if isinstance(it, dict) else ""):
            v = m.replace(",", "")
            if len(v) >= 6:
                vals.add(v)
    return vals


def audit(data, name2slug):
    # 大額値→保有社
    val2slugs = defaultdict(set)
    for s, d in data.items():
        for v in _big_values(d):
            val2slugs[v].add(s)
    flagged = {}   # slug -> list[(section, idx, fact, reason)]
    for s, d in data.items():
        own = (d.get("name") or "")
        own_core = own.replace("株式会社", "").replace("・", "")
        is_sub = bool(SUB_NAME.search(own)) and not re.search(r"ホールディングス|フィナンシャル", own)
        for sec in ("主要財務",):
            arr = d.get("sections", {}).get(sec, []) or []
            for i, it in enumerate(arr):
                if not isinstance(it, dict):
                    continue
                fact = it.get("fact", ""); src = it.get("source_url", "")
                reason = None
                # A: 子会社名義 かつ fact が持株/親会社エンティティ(Xホールディングス/FG/グループの連結)を名指し
                if is_sub:
                    mh = HOLDING_ENTITY.search(fact)
                    if mh and mh.group(0) not in own_core:
                        reason = f"親/持株名指し({mh.group(0)[:12]})"
                # B: fact が別の実在他社名(≧4字・own無関係・後続がカナ語尾でない)を名指し
                if not reason:
                    for core, sl in name2slug.items():
                        if sl == s or len(core) < 4 or core in own_core or own_core in core:
                            continue
                        pos = fact.find(core)
                        if pos < 0:
                            continue
                        nxt = fact[pos + len(core): pos + len(core) + 1]
                        if not re.match(r"[ァ-ヶー]", nxt):          # 部分語(アミューズ→メント)を除外
                            reason = f"他社名混入({core})"; break
                # C: 大額値が他社datasheetと重複(持株/連結の使い回し)
                if not reason:
                    for m in BIGYEN.findall(fact):
                        v = m.replace(",", "")
                        if len(v) >= 6 and len(val2slugs[v]) >= 2:
                            reason = f"財務値重複({sorted(val2slugs[v] - {s})[0]})"; break
                # D: 子会社名義 かつ src が持株会社IRドメイン
                if not reason and is_sub and HOLDING_SRC.search(src) and BIGYEN.search(fact):
                    reason = "持株src(子会社datasheet)"
                if reason:
                    flagged.setdefault(s, []).append((sec, i, fact[:48], reason))
    return flagged


def qq(x):
    return "'" + str(x).replace("'", "''") + "'"


def main():
    dry = "--dry" in sys.argv
    data, name2slug = _load()
    flagged = audit(data, name2slug)
    total_facts = sum(len(v) for v in flagged.values())
    print(f"汚染検出: {len(flagged)}社 / 汚染fact {total_facts}件", flush=True)
    for s, items in sorted(flagged.items()):
        print(f"  {s:16}({data[s].get('name','')[:16]}) x{len(items)}: {items[0][3]} | {items[0][2]}")
    if dry:
        return
    # 修正: 汚染factを除去(非表示化) → datasheet.json書換 + D1 UPDATE生成
    upd = []
    bak_rows = []
    for s, items in flagged.items():
        d = data[s]
        drop_idx = defaultdict(set)
        for sec, i, _f, _r in items:
            drop_idx[sec].add(i)
        for sec, idxs in drop_idx.items():
            arr = d["sections"].get(sec, [])
            d["sections"][sec] = [it for j, it in enumerate(arr) if j not in idxs]
        json.dump(d, open(os.path.join(OUT, s, "datasheet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # D1形状(datasheet.html)へ変換
        sections = []
        for k, arr in d.get("sections", {}).items():
            it2 = [{"label": "", "value": it.get("fact", ""), "source_url": it.get("source_url", "")}
                   for it in (arr or []) if isinstance(it, dict) and it.get("fact")]
            if it2:
                sections.append({"title": SEC_MAP.get(k, k), "items": it2})
        payload = json.dumps({"name": d.get("name", s), "sections": sections}, ensure_ascii=False)
        upd.append(f"INSERT OR REPLACE INTO datasheets (company_id,data,updated_at) VALUES ({qq(s)},{qq(payload)},unixepoch());")
    open(UPD, "w", encoding="utf-8").write("\n".join(upd) + "\n")
    print(f"\n非表示化 {total_facts}件 / D1 UPDATE {len(upd)}社 -> {UPD}")


if __name__ == "__main__":
    main()
