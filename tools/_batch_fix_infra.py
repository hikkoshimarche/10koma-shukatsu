#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""インフラ・エネルギー28社: 真因修正コードで本文を再生成し、既存256pxアバターを流用して4点一致を回復。
方針(改訂): text再生成→sync→【既存image_urlをrole_code単位で復元(流用)】。R7(新規)はブランク(noimg)。
★破壊操作なし: アバターの生成も削除もしない。全社共通ルール(空を対象なしと解釈しない/肯定確認/期待vs実件数/例外を握り潰さない)を実装。
安全弁: (a)取得が空=失敗として中止(削除・スキップしない) (b)per-company control-canaryで対象外社の変化を検知したら即停止。"""
import sys, os, json, subprocess, hashlib
from pathlib import Path
REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
API = REPO/"api"
sys.path.insert(0, str(REPO/"tools")); sys.path.insert(0, str(REPO/"scripts"))
for ln in ("scripts","output"):
    if not (REPO/ln).exists():
        os.symlink(os.path.expanduser(f"~/oscar-ai/tokyari-pipeline/{ln}"), REPO/ln)
LOG = open(REPO/"tools/_batch_fix_infra.log","w")
def log(m): print(m, flush=True); LOG.write(str(m)+"\n"); LOG.flush()

TARGETS = ["chiyoda","chubu-electric","chugoku-electric","cosmo-energy","eneos","erex",
 "hokkaido-electric","hokkaido-gas","hokuriku-electric","inpex","iwatani","j-power","japex",
 "jera","jgc-hd","kepco","kurita","kyushu-electric","metawater","okinawa-electric","osaka-gas",
 "renova","saibu-gas","shizuoka-gas","toho-gas","tohoku-electric","tokyo-gas","west-hd"]
CONTROLS = ["mitsubishi-corp","toyota-motor","sony-group","nippon-life"]  # 対象外・変化してはいけない社

def d1(sql, expect_rows=None):
    """wrangler d1(cwd=api・config自動検出=wrangler.toml)。失敗/空は例外(握り潰さない)。expect_rows未満なら例外。
    ※前回インシデントの真因: 存在しない --config wrangler.jsonc を指定→wrangler rc=1→空→誤削除。
      api/ の実config は wrangler.toml。cwd=api の自動検出で正しく解決する(--config指定しない)。"""
    p = subprocess.run(["npx","wrangler","d1","execute","10koma-shukatsu-db","--remote",
                        "--json","--command",sql],
                       cwd=str(API), capture_output=True, text=True, timeout=120)
    o = p.stdout; i = o.find("[")
    if i < 0:
        raise RuntimeError(f"d1 取得失敗(空/エラー rc={p.returncode}): {p.stderr[-200:]}")
    res = json.loads(o[i:])[0]["results"]
    if expect_rows is not None and len(res) < expect_rows:
        raise RuntimeError(f"d1 期待{expect_rows}件未満(実{len(res)}件): {sql[:80]} — 取得失敗の可能性=中止")
    return res

def sh(*a):
    return subprocess.run(a, cwd=str(REPO), capture_output=True, text=True)

def company_hash(cid):
    rows = d1(f"SELECT role_code,position,display_name,image_url,length(system_prompt) L FROM personas WHERE company_id='{cid}' ORDER BY role_code")
    return hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

# control baseline
ctrl0 = {c: company_hash(c) for c in CONTROLS}
log(f"control baseline: {[(c,h[:8]) for c,h in ctrl0.items()]}")

done=[]; failed=[]; r7blank=[]
for idx,slug in enumerate(TARGETS,1):
    try:
        # 1) 既存 image_url を role_code 単位で捕捉(流用元)。空なら失敗として中止(rule1/3)。
        cur = d1(f"SELECT role_code, image_url FROM personas WHERE company_id='{slug}'", expect_rows=1)
        url_by_role = {r["role_code"]: r["image_url"] for r in cur if r["image_url"]}
        if not url_by_role:
            raise RuntimeError("既存image_urlが空=流用元取得失敗の可能性→中止(削除もスキップもしない)")
        # 2) text再生成(修正コード)。registered(lint error0)を肯定確認。
        r = sh(sys.executable, "tools/room_harness.py", "--slug", slug, "--force")
        if "registered" not in r.stdout:
            raise RuntimeError(f"room_harness未登録(lint等): {r.stdout[-160:]}{r.stderr[-160:]}")
        # 3) sync(image_url=None化)
        s = sh(sys.executable, "tools/room_personas_to_live.py", "--slug", slug)
        # 4) 新role確認(空なら失敗中止)
        roles = [x["role_code"] for x in d1(f"SELECT role_code FROM personas WHERE company_id='{slug}'", expect_rows=2)]
        # 5) 既存URLをrole単位で復元(存在するもののみ=肯定確認)。新role(R7等)は復元元なし→null据置(ブランク)。破壊操作なし。
        stmts=[]; restored=[]; blanks=[]
        for rc in roles:
            u = url_by_role.get(rc)
            if u:
                stmts.append(f"UPDATE personas SET image_url='{u}' WHERE company_id='{slug}' AND role_code='{rc}';")
                restored.append(rc)
            else:
                blanks.append(rc)
        if stmts:
            open("/tmp/_refl1.sql","w").write("\n".join(stmts))
            rp = subprocess.run(["npx","wrangler","d1","execute","10koma-shukatsu-db","--remote","--file","/tmp/_refl1.sql"], cwd=str(API), capture_output=True, text=True)
            if rp.returncode!=0: raise RuntimeError(f"image_url復元失敗: {rp.stderr[-160:]}")
        if blanks: r7blank.append((slug,blanks))
        # 6) per-company: control社が変化してないか(暴走検知→即停止)
        for c in CONTROLS:
            if company_hash(c) != ctrl0[c]:
                raise SystemExit(f"★STOP: control {c} が変化(暴走検知)。{slug}処理後に中断。")
        done.append(slug)
        log(f"[{idx}/{len(TARGETS)}] {slug} ✅ roles={roles} 復元={restored} blank={blanks}")
    except SystemExit:
        raise
    except Exception as e:
        failed.append((slug,str(e))); log(f"[{idx}/{len(TARGETS)}] {slug} ❌ {e}")

log(f"=== DONE ok={len(done)} failed={len(failed)} r7blank社={len(r7blank)} ===")
if failed: log("FAILED: "+json.dumps(failed,ensure_ascii=False))
log("R7ブランク: "+json.dumps(r7blank,ensure_ascii=False))
LOG.close()
sys.exit(1 if failed else 0)
