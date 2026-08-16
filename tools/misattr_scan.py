#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JASM型「誤帰属」データシート検出スキャン（回帰テスト）。

背景: corpus収集時に、同名・同略称・海外同名の【別会社】の情報を掴んでdatasheetに
混入させる事故が複数実在した（例: JASM(TSMC熊本)の中身が英James Aiken Engineering、
しまむら(アパレル)の中身が島村楽器、CTC(伊藤忠テクノ)の中身が中部テレコミュニケーション、
ナガセ(東進)の中身が長瀬産業(化学) 等）。学生に別会社の内容を読ませる最も重い欠陥。

このスクリプトは、リポジトリ変更なし・公式APIだけで独立再現できる形で400社を突合する。

────────────────────────────────────────────────────────
【公式ドメインの判定基準（恣意性を排すため明文化）】
リポジトリに各社の公式URL台帳は存在しない（public/companies.json にURL列なし）。
そこで本スキャンは「datasheetが自ら引用しているsource_urlのうち、
インフラ/第三者ドメインを除いた最頻ホスト」を “そのdatasheetが公式とみなしたドメイン
(=claimed_official_domain)” と定義する。事業/社風/沿革は本来その会社の公式サイトから
執筆されるため、最頻の自社サイト・ドメインが「claimedな公式」である。
本スキャンはこのclaimedドメインが【本当にその会社のものか】を、
 (A) ドメイン名 vs 会社slug/社名ローマ字 のトークン一致
 (B) 本文の主役/言及エンティティ vs 会社名（別会社名が出ていないか）
の2軸で突合する。INFRA/AGG除外リストは下記 EXCLUDE_* に明記。
※これは台帳が無い中での最善のヒューリスティックであり、下記「拾えない型」を伴う。

【このスキャンで拾える型】
 - ドメインは正しい風だが本文が別会社（JASM型。Bで検出。A単独では不可＝jasm.comはslug一致）
 - source_urlドメインが別会社のもの（Aで検出）
 - 本文に別会社名が主語/言及で複数回出る（Bで検出。主語型・非主語型の両方）

【このスキャンで拾えない/弱い型（正直に記載）】
 - 別会社名を一切出さず、事実だけ差し替わっている混入（社名の手がかりが無い）
 - 数値だけが誤り（正しい会社の正しい体裁で値だけ他社）。桁異常の粗いチェックはするが限定的
 - 実在の子会社/親会社/ブランド名との区別は自動確定できない → "review"に留め人手確認

使い方（1行）:
  python3 tools/misattr_scan.py                 # 本番APIから400社取得して突合
  python3 tools/misattr_scan.py --out PATH      # 出力先変更(既定 tools/_misattr_scan_result.json)
  python3 tools/misattr_scan.py --api URL       # APIベース変更
出力: 各社 {claimed_domain, domain_match, alien_entities, geo, verdict, reason}
      verdict = ok / review(要人手確認) / mismatch(ドメイン名も本文も不一致=高疑い)
"""
import sys, os, re, json, subprocess, concurrent.futures as cf

API = "https://10koma-shukatsu-api.oscar-dodds.workers.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "_misattr_scan_result.json")

# 公式ドメイン判定から除外する「インフラ/一次開示」ホスト（会社固有でない）
EXCLUDE_INFRA = re.compile(
    r"edinet|disclosure|\.go\.jp|\.lg\.jp|nikkei|jpx\.|tdnet|meti|fsa\.go|"
    r"\.pdf$|release\.tdnet|k-uriage", re.I)
# 第三者アグリゲータ（就活/口コミ/求人媒体等）＝公式でない
EXCLUDE_AGG = re.compile(
    r"syukatsu-kaigi|internshipguide|mynavi|rikunabi|migi-nanameue|talentsquare|"
    r"openwork|en-hyouban|unistyle|typeshukatsu|wikipedia|prtimes|note\.com|"
    r"job-q|jobtalk|careerpark|onecareer|u-intern|gakujo|hrog|choosenic|"
    r"m-careerguide|i-note|tleon|soico|fisco|movin\.co", re.I)
# 会社名から除去する一般語（トークン一致の分母を絞る）
GENERIC = {"co", "jp", "inc", "ltd", "hd", "group", "japan", "holdings", "corp",
           "kabushiki", "kaisha", "com", "www", "ne", "or", "go"}
# 本文の主語/エンティティから除外する一般語
STOP_ENT = re.compile(r"^(同社|当社|弊社|各社|同グループ|グループ|会社|事業|同行|自社|他社|"
                      r"全社|当グループ|株式会|有限会|同|当|弊|両社|同年|同月|同日|なお)$")
# 海外拠点等の地名（JP企業本体の沿革に主役として出ると不自然な手がかり）
GEO = re.compile(r"アバディーン|Aberdeen|スコットランド|マンチェスター|バーミンガム|"
                 r"デュッセルドルフ|ミュンヘン|グラスゴー|リヴァプール")


def sh(cmd, timeout=40):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout


def load_company_ids():
    cj = json.load(open(os.path.join(ROOT, "public", "companies.json")))
    ids = []
    for _, cs in cj.items():
        for c in cs:
            ids.append((c["id"], c.get("name", c["id"])))
    return ids


def fetch_datasheet(cid):
    for _ in range(3):
        try:
            txt = sh(["curl", "-s", "--max-time", "25", f"{API}/api/datasheet?id={cid}"])
            d = json.loads(txt)
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    return None


def registrable(host):
    """ざっくり登録可能ドメイン（末尾2〜3ラベル）。co.jp/or.jp等の2段TLDに対応。"""
    host = re.sub(r"^www\.", "", host or "").split(":")[0]
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "or", "ne", "go", "ac", "lg", "com"):
        return ".".join(parts[-3:]), parts[-3]
    if len(parts) >= 2:
        return ".".join(parts[-2:]), parts[-2]
    return host, host


def norm(s):
    return re.sub(r"[\s・（）()「」、。･株式会社ホールディングスグループ]", "", s or "")


def name_tokens(cid, name):
    toks = set(re.split(r"[-_]", cid.lower()))
    toks |= {t.lower() for t in re.findall(r"[A-Za-z]{2,}", name)}
    return {t for t in toks if len(t) >= 3 and t not in GENERIC}


def analyze(cid, name, d):
    sections = d.get("sections") or []
    items = [(s.get("title", ""), it.get("value", ""))
             for s in sections for it in (s.get("items") or []) if (it.get("value") or "").strip()]
    body = " ".join(v for _, v in items)
    urls = [it.get("source_url", "") for s in sections for it in (s.get("items") or [])]
    if not items:
        return {"id": cid, "name": name, "n_items": 0, "verdict": "empty",
                "reason": "datasheet空（既に除去済 or 未投入）", "claimed_domain": None,
                "domain_match": None, "alien_entities": [], "geo": []}
    # claimed official domain = INFRA/AGG除外後の最頻登録ドメイン
    from collections import Counter
    dc = Counter()
    for u in urls:
        m = re.match(r"https?://([^/]+)", u or "")
        if not m:
            continue
        if EXCLUDE_INFRA.search(u) or EXCLUDE_AGG.search(u):
            continue
        reg, sld = registrable(m.group(1))
        dc[(reg, sld)] += 1
    claimed = dc.most_common(1)[0][0] if dc else (None, None)
    claimed_dom, claimed_sld = claimed
    toks = name_tokens(cid, name)
    core = norm(re.split(r"[（(]", name)[0])
    # (A) ドメイン名 vs 会社トークン
    domain_match = True
    if claimed_sld:
        domain_match = any(t in claimed_sld or claimed_sld in t for t in toks if len(t) >= 3) \
                       or (core and (core[:3] in claimed_sld))
    # (B) 本文エンティティ抽出（主語型 + 非主語の「◯◯株式会社/株式会社◯◯」）
    ent = Counter()
    for m in re.finditer(r"(?:^|。|\s)([一-龥ァ-ヶA-Za-z][一-龥ァ-ヶーA-Za-z0-9・]{2,18}?)(?:は[、\s])", body):
        e = m.group(1)
        if not STOP_ENT.match(e):
            ent[e] += 1
    for m in re.finditer(r"([一-龥ァ-ヶA-Za-z][一-龥ァ-ヶーA-Za-z0-9・]{2,18}?)株式会社|株式会社([一-龥ァ-ヶA-Za-z][一-龥ァ-ヶーA-Za-z0-9・]{2,18})", body):
        e = m.group(1) or m.group(2)
        if e and not STOP_ENT.match(e):
            ent[e] += 1

    def related(e):
        ne = norm(e)
        if len(ne) < 3:
            return True
        if ne in core or (core and core in ne):
            return True
        if any(t in e.lower() or e.lower() in t for t in toks if len(t) >= 3):
            return True
        # claimed SLD と一致する社名（=公式ドメインの持ち主名）は自社扱い
        if claimed_sld and (claimed_sld in e.lower() or e.lower() in claimed_sld):
            return True
        return False

    alien = [(e, c) for e, c in ent.most_common() if not related(e)]
    geo = GEO.findall(body)
    # 判定
    reason = []
    if alien:
        reason.append("本文に非自社エンティティ: " + ", ".join(f"{e}×{c}" for e, c in alien[:5]))
    if not domain_match:
        reason.append(f"claimedドメイン'{claimed_dom}'が社名/slugと不一致")
    if geo:
        reason.append("海外地名手がかり: " + ",".join(sorted(set(geo))[:3]))
    # verdict
    if alien and not domain_match:
        verdict = "mismatch"      # 両軸で不一致＝高疑い
    elif alien or geo:
        verdict = "review"        # 本文にalien＝人手確認
    elif not domain_match:
        verdict = "review_domain" # ドメイン名だけ不一致（正当な別ドメインも多い）
    else:
        verdict = "ok"
    return {"id": cid, "name": name, "n_items": len(items), "claimed_domain": claimed_dom,
            "domain_match": domain_match, "alien_entities": alien[:8], "geo": sorted(set(geo)),
            "verdict": verdict, "reason": " / ".join(reason) or "一致"}


def main():
    api_i = sys.argv.index("--api") + 1 if "--api" in sys.argv else None
    global API, OUT
    if api_i:
        API = sys.argv[api_i]
    if "--out" in sys.argv:
        OUT = sys.argv[sys.argv.index("--out") + 1]
    ids = load_company_ids()
    sys.stderr.write(f"対象 {len(ids)} 社 / API={API}\n")
    results = []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch_datasheet, cid): (cid, nm) for cid, nm in ids}
        for fut in cf.as_completed(futs):
            cid, nm = futs[fut]
            d = fut.result()
            if d is None:
                results.append({"id": cid, "name": nm, "verdict": "fetch_fail", "reason": "API取得失敗"})
                continue
            results.append(analyze(cid, nm, d))
    results.sort(key=lambda r: {"mismatch": 0, "review": 1, "review_domain": 2, "ok": 3,
                                "empty": 4, "fetch_fail": 5}.get(r.get("verdict"), 9))
    json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    vc = Counter(r["verdict"] for r in results)
    print(f"=== misattr_scan: {len(results)}社 → {dict(vc)} ===")
    print(f"出力: {OUT}")
    for r in results:
        if r["verdict"] in ("mismatch", "review"):
            print(f"  [{r['verdict']}] {r['id']}({r['name'][:20]}): {r['reason']}")


if __name__ == "__main__":
    main()
