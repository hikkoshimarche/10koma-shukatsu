#!/usr/bin/env python3
"""A: 誤答カテゴリ整合 修復スイープ。理念・方針系の問いで誤答が事業ジャンル(ゲーム開発等)=消去法で解ける不成立問を修復。
 誤答を「他社corpus実在の看板理念フレーズ」(同型＋自社corpus不在=機械検証可＋比較の学び)に差替。正解は不変(誤答のみ再生成)。
 対象=全266社+業界(D1実データ)。lint(型整合=全誤答が理念フレーズ)を満たす分のみ D1 UPDATE(options)。
 backup(.backups/pre_distractor_cat_<ts>.sql) → scratchpad/distractor_cat_update.sql。--dry で判定のみ。
"""
import subprocess, json, re, os, sys, glob

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
UPD = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad/distractor_cat_update.sql"

PHIL = re.compile(r"理念|方針|価値観|重視|大切に|パーパス|ミッション|ビジョン|バリュー|スローガン|経営の要素|"
                  r"行動指針|信条|使命|哲学|目指す|大事にし|大切にし|カルチャー|求める人物|グループポリシー|社是|クレド")
PERSON = re.compile(r"社長|代表取締役|会長|役員|取締役|CEO|COO|CFO|は誰|の名前")
NUM = re.compile(r"\d.*(円|%|％|名|年|人|件|店|拠点|億|万|倍|位)")
_VALUE = re.compile(r"社会|価値|貢献|挑戦|誠実|信頼|創造|健康|未来|文化|倫理|品質|安全|力|発想|プロ|お客様|幸せ|豊か|"
                    r"融合|革新|誇り|信託|情熱|絆|共に|人|夢|笑顔|技術で|世の中|快適|喜び|真心|尊重|自由|感動")
# 志望・スローガン型(「日本一の保険会社」等)は理念系の正当な同型誤答=不整合でない。
_ASPIRE = re.compile(r"(日本一|世界一|地域一|アジア一|業界一|No\.?1|ナンバーワン|トップ|唯一)")
_CREED_END = re.compile(r"(する|しよう|であること|を追求|を大切|を目指|に貢献|であり続け)$")
# 単独の異業種ジャンル語(＋任意の開発/製造/販売接尾)= 理念問の誤答に混ざると消去法で解ける明白な不整合。
# 完全一致に限定(precision優先): 並列acronym(CSR×IT)・志望型(世界一の保険会社)・活動句(ITサービスの提供)は誤検出しない。
_BAREGENRE = re.compile(r"(ゲーム|自動車|銀行|医薬品?|化学|鉄鋼|証券|不動産|建設|食品|飲料|通信|小売|物流|商社|半導体|"
                        r"電機|機械|エネルギー|石油|ガス|航空|鉄道|アパレル|化粧品|広告|人材|保険|旅客|貨物|"
                        r"農業|畜産|外食|飲食|アニメ|映画|出版|玩具|衣料|旅行|教育|鉄道|物流)"
                        r"(開発|製造|販売|事業|業|制作|品)?")


def _philosophy_ok(s):
    s = str(s).strip()
    return bool(_VALUE.search(s) or _ASPIRE.search(s) or _CREED_END.search(s))


def d1(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                        "--config", "api/wrangler.toml", "--json", "--command", sql], cwd=ROOT, capture_output=True, text=True)
    t = p.stdout or ""; i = t.find("[")
    rows = []
    for blk in json.loads(t[i:]) if i >= 0 else []:
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


def is_bizgenre(o):
    """理念問の誤答としての『単独異業種ジャンル語』(消去法で解ける明白な不整合)。完全一致・志望型除外。"""
    o = str(o).strip()
    if _philosophy_ok(o):                       # 志望型/価値語/信条=同型の正当な誤答→不整合でない
        return False
    return bool(_BAREGENRE.fullmatch(o))


def qq(s):
    return "'" + str(s).replace("'", "''") + "'"


def _own_corpus_text(slug):
    parts = []
    for fn in ("quiz_corpus_locked_v3.json", "datasheet.json"):
        fp = os.path.join(OUT, slug, fn)
        if os.path.exists(fp):
            try:
                parts.append(json.dumps(json.load(open(fp)), ensure_ascii=False))
            except Exception:
                pass
    return " ".join(parts)


def main():
    dry = "--dry" in sys.argv
    rows = d1("SELECT id,set_type,set_id,q_text,options,correct FROM quiz_questions")
    # (1) 理念フレーズプール: {phrase: set(source set_id)}  (理念問の正解フレーズ=他社の看板理念)
    pool = {}
    for r in rows:
        try:
            opts = json.loads(r["options"])
        except Exception:
            continue
        ci = r.get("correct", 0)
        if not isinstance(opts, list) or ci >= len(opts):
            continue
        ans = str(opts[ci]).strip()
        if PHIL.search(r["q_text"]) and not PERSON.search(r["q_text"]) and not NUM.search(ans) \
                and _VALUE.search(ans) and 3 <= len(ans) <= 22 and not is_bizgenre(ans):
            pool.setdefault(ans, set()).add(r["set_id"])
    phrases = sorted(pool)
    # (2) 不整合問の検出＋修復
    updates, backups, examples, fixed, unfixable = [], [], [], 0, 0
    for r in rows:
        try:
            opts = json.loads(r["options"])
        except Exception:
            continue
        ci = r.get("correct", 0)
        if not isinstance(opts, list) or len(opts) < 2 or ci >= len(opts):
            continue
        ans = str(opts[ci]); qt = r["q_text"]
        if PERSON.search(qt) or NUM.search(ans) or not PHIL.search(qt):
            continue
        bad_idx = [k for k in range(len(opts)) if k != ci and is_bizgenre(opts[k])]
        if not bad_idx:
            continue
        own = _own_corpus_text(r["set_id"])
        before = list(opts)
        used = set(str(o).strip() for o in opts)
        corr = str(opts[ci]).strip()
        # id をシードに決定論選択(他社発・自社corpus不在・未使用・正解と非類似)
        seed = sum(ord(c) for c in r["id"])
        cand = [p for p in phrases if r["set_id"] not in pool[p] and p not in used and p not in own
                and p not in corr and corr not in p             # 正解と包含関係(酷似)を除外
                and not (len(set(p) & set(corr)) >= 0.7 * min(len(set(p)), len(set(corr))))]
        ok = True
        for j, k in enumerate(bad_idx):
            if not cand:
                ok = False; break
            pick = cand[(seed + j * 7) % len(cand)]
            opts[k] = pick; used.add(pick)
            cand = [p for p in cand if p != pick]
        if not ok:
            unfixable += 1
            continue
        fixed += 1
        updates.append(f"UPDATE quiz_questions SET options={qq(json.dumps(opts, ensure_ascii=False))} WHERE id={qq(r['id'])};")
        backups.append(f"UPDATE quiz_questions SET options={qq(r['options'])} WHERE id={qq(r['id'])};")
        if len(examples) < 3:
            examples.append((r["set_id"], qt[:40], ans, before, opts))
    print(f"理念フレーズプール: {len(phrases)}種 / 不整合検出: {fixed+unfixable} / 修復: {fixed} / 修復不可: {unfixable}", flush=True)
    for e in examples:
        print(f"\n  [{e[0]}] {e[1]}  (正解:{e[2]})")
        print(f"    before: {e[3]}")
        print(f"    after : {e[4]}")
    if not dry and updates:
        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M")
        bpath = os.path.join(ROOT, ".backups", f"pre_distractor_cat_{ts}.sql")
        open(bpath, "w", encoding="utf-8").write("\n".join(backups) + "\n")
        open(UPD, "w", encoding="utf-8").write("\n".join(updates) + "\n")
        print(f"\nbackup -> {bpath} ({len(backups)}問) / update -> {UPD} ({len(updates)}問)")


if __name__ == "__main__":
    main()
