"""cf_env.py — wrangler 実行環境(認証トークン + node PATH)の単一解決点。

正本: 10koma-shukatsu/tools/cf_env.py
複製: tokyari-pipeline/scripts/cf_env.py  ← **編集時は両方を必ず同期**(check_wrangler_auth.py が差分を検出)

なぜ必要か (2026-11-18 是正):
  wrangler の OAuth(~/Library/Preferences/.wrangler/config/default.toml) は 2026-08-05 に失効。
  対話シェルは ~/.zshrc の CLOUDFLARE_API_TOKEN で動くが、launchd(bash -l / 直接exec)は zshrc を読まない
  → トークン無しの wrangler は非対話で即死する。これで phasec 画像経路(311回ループ)・content_health
  (3ヶ月半停止)・user_profiles 同期・quarterly 等が 2026-08-05 から静かに死んでいた。
  2026-08 に deploy_salary._cloudflare_token だけ直して同型を探さなかったのが真因。
  → 解決ロジックをここ1箇所に集約し、wrangler を呼ぶ全経路がここを通る。

解決順: 環境変数 CLOUDFLARE_API_TOKEN → login キーチェーン(service=tokyari-cloudflare-api-token)。
値はログ・例外文に一切出さない。plist にも焼かない(public repo 露出なし)。
"""
from __future__ import annotations

import getpass
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

KEYCHAIN_SERVICE = "tokyari-cloudflare-api-token"


def token() -> str:
    """CLOUDFLARE_API_TOKEN を env→keychain の順で解決。解決不可なら ""。"""
    t = (os.environ.get("CLOUDFLARE_API_TOKEN") or "").strip()
    if t:
        return t
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or getpass.getuser()
    try:
        r = subprocess.run(["/usr/bin/security", "find-generic-password",
                            "-a", user, "-s", KEYCHAIN_SERVICE, "-w"],
                           capture_output=True, text=True, timeout=10)
        return (r.stdout or "").strip()
    except Exception as e:  # 握り潰さない: 理由を stderr に残す(値は含まない)
        sys.stderr.write(f"[cf_env] keychain 参照失敗: {type(e).__name__}\n")
        return ""


def node_bin() -> str | None:
    """npx/wrangler/node のある bin ディレクトリ。launchd 最小PATHでも nvm 最新版を glob で拾う。"""
    p = shutil.which("npx")
    if p:
        return str(Path(p).parent)          # resolve() すると npm 内部dirを指すので解決しない
    for pat in (str(Path.home() / ".nvm/versions/node/*/bin"), "/opt/homebrew/bin", "/usr/local/bin"):
        hits = sorted(h for h in glob.glob(pat) if Path(h, "npx").exists())
        if hits:
            return hits[-1]
    return None


def wrangler_env(base: dict | None = None) -> dict:
    """subprocess に渡す env。PATH に node bin を前置し、トークンを注入する(deploy_salary 方式)。"""
    env = dict(os.environ if base is None else base)
    nb = node_bin()
    if nb and nb not in env.get("PATH", "").split(os.pathsep):
        env["PATH"] = nb + os.pathsep + env.get("PATH", "")
    tok = token()
    if tok:
        env["CLOUDFLARE_API_TOKEN"] = tok
    return env


def apply() -> bool:
    """このプロセスの os.environ に適用(以後の全 subprocess/子プロセスが継承)。
    エントリポイントの先頭で1回呼ぶ。トークン解決不可なら stderr に警告し False。"""
    env = wrangler_env()
    os.environ["PATH"] = env.get("PATH", os.environ.get("PATH", ""))
    if env.get("CLOUDFLARE_API_TOKEN"):
        os.environ["CLOUDFLARE_API_TOKEN"] = env["CLOUDFLARE_API_TOKEN"]
        return True
    sys.stderr.write("[cf_env] ⚠ CLOUDFLARE_API_TOKEN 未解決(env/keychain 共に無し) — "
                     "非対話の wrangler は失敗します\n")
    return False


def require() -> None:
    """トークン必須の経路用。解決不可なら即例外(静かな失敗を作らない)。"""
    if not apply():
        raise RuntimeError("CLOUDFLARE_API_TOKEN 未解決: keychain service="
                           f"{KEYCHAIN_SERVICE} を確認")


if __name__ == "__main__":
    ok = apply()
    print(f"token={'resolved' if ok else 'MISSING'} node_bin={node_bin()}")
    sys.exit(0 if ok else 1)
