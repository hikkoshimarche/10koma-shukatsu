#!/usr/bin/env python3
"""⑤ 四半期鮮度リフレッシュ orchestrator (launchd: 6/9/12/3月1日)。
段: (1)鮮度fanout(最新期へ再生成・取れない社はhold) (2)D1反映(backup→UPDATE) (3)製品URLレジストリ再構築
     (4)ログ要約。LINE送信なし(QUIZ_LINE_SEND=0固定)。$ガード=QUIZ_MAX_USD(既定$30/四半期)。
--dry: 各段の実行可否を検証しプランのみ出力(書き込み/課金なし)。--skip-fanout/--skip-d1 で段限定。
実行=launchd or 手動。ログ: logs/quarterly_refresh.log(追記)。
"""
import os, sys, subprocess, datetime

ROOT = os.path.expanduser("~/projects/10koma-shukatsu")
OUT = os.path.expanduser("~/oscar-ai/tokyari-pipeline/output")
LOG = os.path.join(ROOT, "logs", "quarterly_refresh.log")
APPLY_FRESH = "/private/tmp/quarterly_freshness_update.sql"
PY = sys.executable


def _load_env():
    """launchdはshell環境を継承しないため .env を依存フリーで読込(OPENAI_API_KEY等)。"""
    for p in ("~/oscar-ai/tokyari-pipeline/.env", "~/projects/10koma-shukatsu/tools/.env.phase_c",
              "~/projects/10koma-shukatsu/.env"):
        fp = os.path.expanduser(p)
        if not os.path.exists(fp):
            continue
        for ln in open(fp, encoding="utf-8"):
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:      # 既存envを上書きしない
                os.environ[k] = v


def _log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _run(cmd, env=None, timeout=7200):
    e = dict(os.environ, QUIZ_LINE_SEND="0", QUIZ_MAX_USD=os.environ.get("QUIZ_MAX_USD", "30"))
    if env:
        e.update(env)
    return subprocess.run(cmd, cwd=ROOT, env=e, capture_output=True, text=True, timeout=timeout)


def stage_fanout(dry):
    if dry:
        ok = os.path.exists(os.path.join(ROOT, "tools/quiz_fanout.py"))
        _log(f"(1)鮮度fanout: {'実行可' if ok else '✗欠落'} (`python tools/quiz_fanout.py --freshness`)")
        return ok
    _log("(1)鮮度fanout 開始 (最新期へ再生成・取れない社hold)")
    r = _run([PY, "tools/quiz_fanout.py", "--freshness"])
    tail = "\n".join(r.stdout.strip().splitlines()[-4:])
    _log(f"(1)鮮度fanout 終了 rc={r.returncode}\n{tail}")
    return r.returncode == 0


def stage_d1(dry):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    if dry:
        ok = os.path.exists(os.path.join(ROOT, "tools/build_freshness_d1_update.py"))
        _log(f"(2)D1反映: {'実行可' if ok else '✗欠落'} (build_freshness_d1_update.py → wrangler --file)")
        return ok
    _log("(2)D1反映 開始 (backup→UPDATE)")
    b = _run([PY, "tools/build_freshness_d1_update.py", ts])
    if b.returncode != 0:
        _log(f"(2)D1 SQL構築失敗 rc={b.returncode}: {b.stderr[-200:]}"); return False
    sqlpath = "/private/tmp/claude-501"  # build script既定の出力先を尊重(stderr/ stdoutにpath)
    upd = next((l.split("->", 1)[1].strip().split(" ")[0] for l in b.stdout.splitlines() if "update ->" in l), "")
    if not upd or not os.path.exists(upd):
        _log(f"(2)更新SQL不明={upd} → skip"); return False
    a = _run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
              "--config", "api/wrangler.toml", "--file", upd])
    written = next((l.strip() for l in a.stdout.splitlines() if "rows_written" in l), a.stderr[-120:])
    _log(f"(2)D1反映 終了 rc={a.returncode} {written}")
    return a.returncode == 0


def stage_industry(dry):
    """業界セット再生成(会社鮮度後=最新member corpusでmerge)→D1再同期→difficulty再充填。
    gen_gyokai_sets.MAP のセットのみ再生成。初期5セット(consulting等未MAP)は locked→D1 再同期で拾う。"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    for f in ("tools/gen_gyokai_sets.py", "tools/build_gyokai_d1_insert.py"):
        if not os.path.exists(os.path.join(ROOT, f)):
            _log(f"(1b)業界再生成: ✗{f}欠落"); return False
    if dry:
        _log("(1b)業界再生成: 実行可 (gen_gyokai_sets→build_gyokai_d1_insert→difficulty再充填)")
        return True
    _log("(1b)業界再生成 開始 (最新corpusでmerge)")
    g = _run([PY, "tools/gen_gyokai_sets.py"])
    _log(f"(1b)gen_gyokai rc={g.returncode}: " + "\n".join(g.stdout.strip().splitlines()[-3:]))
    # 生成済industry__* を locked→D1 再同期(slug自動=会社5本除外)
    b = _run([PY, "tools/build_gyokai_d1_insert.py", ts])
    if b.returncode != 0:
        _log(f"(1b)D1 SQL構築失敗: {b.stderr[-160:]}"); return False
    ins = next((l.split("->", 1)[1].strip().split(" ")[0] for l in b.stdout.splitlines() if "insert ->" in l), "")
    if ins and os.path.exists(ins):
        a = _run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                  "--config", "api/wrangler.toml", "--file", ins])
        _log(f"(1b)業界D1再同期 rc={a.returncode} " + next((l.strip() for l in a.stdout.splitlines() if "rows_written" in l), ""))
    # difficulty再充填(再同期でNULL化した industry 行: 財務Lv4/数値Lv3/他Lv2)
    for sql in ("UPDATE quiz_questions SET difficulty=4 WHERE difficulty IS NULL AND set_type='industry' AND (category='財務数値' OR as_of LIKE '%年3月期%' OR q_text LIKE '%利益%' OR q_text LIKE '%売上%' OR q_text LIKE '%収益%' OR q_text LIKE '%配当%' OR q_text LIKE '%資産%');",
                "UPDATE quiz_questions SET difficulty=3 WHERE difficulty IS NULL AND set_type='industry' AND (q_text LIKE '%従業員%' OR q_text LIKE '%拠点%' OR q_text LIKE '%資本金%');",
                "UPDATE quiz_questions SET difficulty=2 WHERE difficulty IS NULL AND set_type='industry';"):
        _run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote", "--config", "api/wrangler.toml", "--command", sql])
    _log("(1b)業界再生成 完了 (difficulty再充填済)")
    return True


def stage_product_urls(dry):
    if dry:
        ok = os.path.exists(os.path.join(ROOT, "tools/build_product_urls.py"))
        _log(f"(3)製品URLレジストリ再構築: {'実行可' if ok else '✗欠落'} (rendered_corpus保有社)")
        return ok
    _log("(3)製品URLレジストリ再構築 開始")
    r = _run([PY, "tools/build_product_urls.py"])
    tail = "\n".join(r.stdout.strip().splitlines()[-6:])
    _log(f"(3)製品URL 終了 rc={r.returncode}\n{tail}")
    return r.returncode == 0


def stage_salary(dry):
    """(1c)年収スイープ: EDINET有報の平均年間給与を最新期へ一括反映(6月=有報提出後に有効)。
    EDINET_API_KEY必須。index再構築→相互照合±5%採用→10コマkoma5/datasheet/shindan反映→panels再生成→D1。
    ※来年6月からの自動化: 走査窓は当年3〜7月。要人間確認(乖離)社は据置し受け渡しmdへ。"""
    for f in ("tools/edinet_salary_sweep.py", "tools/apply_salary_update.py", "tools/batch_salary_d1.py"):
        if not os.path.exists(os.path.join(ROOT, f)):
            _log(f"(1c)年収スイープ: ✗{f}欠落"); return False
    if not os.environ.get("EDINET_API_KEY"):
        _log("(1c)年収スイープ: skip(EDINET_API_KEY未設定・鍵投入後に有効)"); return True
    if dry:
        _log("(1c)年収スイープ: 実行可 (edinet_salary_sweep→apply_salary_update→batch_salary_d1→D1)")
        return True
    _log("(1c)年収スイープ 開始 (EDINET有報→相互照合採用→反映)")
    idx = os.path.join(OUT, "_edinet_filing_index.json")   # 当年の有報を拾うため前年indexは破棄
    try:
        os.remove(idx)
    except OSError:
        pass
    sw = _run([PY, "tools/edinet_salary_sweep.py", "--dry"], timeout=10800)
    _log(f"(1c)スイープ rc={sw.returncode}: " + "\n".join(sw.stdout.strip().splitlines()[-6:]))
    if sw.returncode != 0:
        return False
    ap = _run([PY, "tools/apply_salary_update.py"])
    _log(f"(1c)反映 rc={ap.returncode}: " + "\n".join(ap.stdout.strip().splitlines()[-2:]))
    bd = _run([PY, "tools/batch_salary_d1.py"])
    _log(f"(1c)panels生成 rc={bd.returncode}: " + "\n".join(bd.stdout.strip().splitlines()[-2:]))
    SCR = "/private/tmp/claude-501/-Users-oscardodds-projects-10koma-shukatsu/7bb93f17-be86-4a51-a16e-c0b146625361/scratchpad"
    for sql in ("salary_panels.sql", "salary_datasheets.sql"):
        p = os.path.join(SCR, sql)
        if os.path.exists(p):
            a = _run(["npx", "wrangler", "d1", "execute", "10koma-shukatsu-db", "--remote",
                      "--config", "api/wrangler.toml", "--file", p])
            _log(f"(1c)D1 {sql} rc={a.returncode} " + next((l.strip() for l in a.stdout.splitlines() if "rows_written" in l), ""))
    _log("(1c)年収スイープ 完了 (要人間確認社は据置=受け渡しmd)")
    return True


def main():
    dry = "--dry" in sys.argv
    _load_env()
    keyok = "有" if os.environ.get("OPENAI_API_KEY") else "✗無(fanout不可)"
    _log(f"===== 四半期鮮度リフレッシュ {'[DRY]' if dry else '[実走]'} 開始 (QUIZ_MAX_USD=${os.environ.get('QUIZ_MAX_USD','30')} / OPENAI_KEY={keyok}) =====")
    results = {}
    if "--skip-fanout" not in sys.argv:
        results["fanout"] = stage_fanout(dry)
    if "--skip-industry" not in sys.argv:
        results["industry"] = stage_industry(dry)
    if "--skip-salary" not in sys.argv:
        results["salary"] = stage_salary(dry)
    if "--skip-d1" not in sys.argv:
        results["d1"] = stage_d1(dry)
    results["product_urls"] = stage_product_urls(dry)
    ok = all(results.values())
    _log(f"===== 完了 {'✅全段OK' if ok else '⚠️一部失敗 '+str(results)} =====")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
