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


def main():
    dry = "--dry" in sys.argv
    _load_env()
    keyok = "有" if os.environ.get("OPENAI_API_KEY") else "✗無(fanout不可)"
    _log(f"===== 四半期鮮度リフレッシュ {'[DRY]' if dry else '[実走]'} 開始 (QUIZ_MAX_USD=${os.environ.get('QUIZ_MAX_USD','30')} / OPENAI_KEY={keyok}) =====")
    results = {}
    if "--skip-fanout" not in sys.argv:
        results["fanout"] = stage_fanout(dry)
    if "--skip-d1" not in sys.argv:
        results["d1"] = stage_d1(dry)
    results["product_urls"] = stage_product_urls(dry)
    ok = all(results.values())
    _log(f"===== 完了 {'✅全段OK' if ok else '⚠️一部失敗 '+str(results)} =====")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
