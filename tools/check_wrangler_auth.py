"""check_wrangler_auth.py — 「launchd(非対話)で wrangler 認証が無い経路」を機械検出するガード。

2026-11-18 是正の再発防止。2026-08 に deploy_salary だけ直して同型を探さず、phasec画像経路・
content_health・user_profiles同期・quarterly が 2026-08-05(wrangler OAuth失効)から静かに死んだ。
「3箇所目が無い」を人の確認ではなく、このスクリプトの exit 0 で言い切る。

検査(FAIL=exit 1):
  1. 両repo(10koma tools/ ・ tokyari-pipeline scripts/)で wrangler を実行する全ファイルが
     cf_env / deploy_salary 経由 / keychain export のいずれかでトークンを解決している
     (未追跡=他タブ所有ファイルは WARN。tracked は FAIL)
  2. cf_env.py の正本と複製がバイト一致
  3. launchd 全ジョブ(com.tokyari.*)の到達ファイルに、別セッションの Claude scratchpad 固定パス
     (/private/tmp/claude-*) が無い(消えると静かに失敗する環境依存)
  4. launchd 最小環境(env -i)で cf_env がトークンと node bin を解決できる
  WARN: plist EnvironmentVariables の PATH に nvm 版数のハードコード(版上げで壊れる)
使い方: python tools/check_wrangler_auth.py [--json]
"""
from __future__ import annotations

import json
import plistlib
import re
import subprocess
import sys
from pathlib import Path

H = Path.home()
R10 = H / "projects/10koma-shukatsu"
RP = H / "oscar-ai/tokyari-pipeline"
T, P = R10 / "tools", RP / "scripts"
SCAN = [(R10, T), (RP, P)]
WR = re.compile(r"[\"']wrangler[\"']|npx wrangler|^\s*wrangler\s+(?:d1|deploy|pages|r2|kv)", re.M)
OK_AUTH = re.compile(r"cf_env|_cloudflare_token|tokyari-cloudflare-api-token|\b(?:D|DS|deploy_salary)\.(?:wrangler|d1_query)\b")
SCRATCH = re.compile(r"/private/tmp/claude-\d+/")
SELF = {"cf_env.py", "check_wrangler_auth.py"}


def _git_tracked(repo: Path, f: Path) -> bool:
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", str(f.relative_to(repo))],
                       capture_output=True, text=True)
    return r.returncode == 0


def _calls(text: str) -> list[int]:
    out = []
    for i, l in enumerate(text.splitlines(), 1):
        s = l.strip()
        if s.startswith("#") or not WR.search(l):
            continue
        if re.search(r"run\(|check_output|Popen|\[|npx wrangler|^\s*wrangler", l):
            out.append(i)
    return out


def check_call_sites():
    rows = []
    for repo, d in SCAN:
        for f in sorted(d.rglob("*")):
            if f.suffix not in (".py", ".sh") or ".bak" in f.name or f.name in SELF or "__pycache__" in f.parts:
                continue
            t = f.read_text(errors="ignore")
            c = _calls(t)
            if not c:
                continue
            tracked = _git_tracked(repo, f)
            auth = bool(OK_AUTH.search(t))
            lvl = "OK" if auth else ("FAIL" if tracked else "WARN")
            rows.append({"file": str(f).replace(str(H), "~"), "lines": c, "tracked": tracked,
                         "auth": auth, "level": lvl})
    return rows


def _mod(name):
    for d in (T, P, T / "health"):
        f = d / f"{name}.py"
        if f.exists():
            return f.resolve()


def _edges(f: Path):
    try:
        t = f.read_text(errors="ignore")
    except Exception:
        return set()
    out = set()
    for a, b in re.findall(r"^\s*(?:from\s+(\w+)\s+import|import\s+([\w ,]+))", t, re.M):
        for n in ([a] if a else [x.strip().split(" as ")[0] for x in b.split(",")]):
            m = _mod(n)
            if m:
                out.add(m)
    for s in re.findall(r"([\w./$~-]+\.(?:py|sh))", t):
        name = s.split("/")[-1]
        for d in (T, P, T / "health"):
            if (d / name).exists():
                out.add((d / name).resolve())
    return out


def launchd_entries():
    ents = {}
    for pl in sorted((H / "Library/LaunchAgents").glob("com.tokyari.*.plist")):
        try:
            d = plistlib.load(open(pl, "rb"))
        except Exception as e:
            ents[pl.name] = {"error": str(e)}
            continue
        args = " ".join(d.get("ProgramArguments", []))
        files = [Path(x.replace("$HOME", str(H))) for x in re.findall(r"(/[\w./$-]+\.(?:py|sh))", args)]
        files = [f.resolve() for f in files if f.exists() and "/.venv/" not in str(f)]
        path_env = (d.get("EnvironmentVariables") or {}).get("PATH", "")
        ents[pl.name] = {"files": files, "hard_nvm": bool(re.search(r"/node/v\d", path_env))}
    return ents


def check_reachable(ents):
    fails, warns = [], []
    for job, e in ents.items():
        if "error" in e:
            fails.append(f"{job}: plist読込失敗 {e['error']}")
            continue
        if e["hard_nvm"]:
            warns.append(f"{job}: EnvironmentVariables PATH に nvm 版数ハードコード(版上げで npx 消失)")
        seen, st = set(), list(e["files"])
        while st:
            x = st.pop()
            if x in seen:
                continue
            seen.add(x)
            st += [y for y in _edges(x) if y not in seen]
        for x in sorted(seen):
            t = x.read_text(errors="ignore")
            for i, l in enumerate(t.splitlines(), 1):
                if SCRATCH.search(l) and not l.strip().startswith("#"):
                    fails.append(f"{job}: {str(x).replace(str(H), '~')}:{i} Claude scratchpad 固定パス")
    return fails, warns


def check_min_env():
    r = subprocess.run(["env", "-i", f"HOME={H}", "PATH=/usr/bin:/bin:/usr/sbin:/sbin",
                        "/usr/bin/python3", str(T / "cf_env.py")], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def main():
    rows = check_call_sites()
    fails = [f"{r['file']} L{r['lines']} トークン未解決(tracked)" for r in rows if r["level"] == "FAIL"]
    warns = [f"{r['file']} L{r['lines']} トークン未解決(untracked=他タブ所有・手動実行時は対話シェル依存)"
             for r in rows if r["level"] == "WARN"]
    a, b = T / "cf_env.py", P / "cf_env.py"
    if not (a.exists() and b.exists() and a.read_bytes() == b.read_bytes()):
        fails.append("cf_env.py 正本(10koma tools)と複製(pipeline scripts)が不一致/欠落")
    f2, w2 = check_reachable(launchd_entries())
    fails += f2
    warns += w2
    ok_env, msg = check_min_env()
    if not ok_env:
        fails.append(f"launchd最小環境で cf_env 解決失敗: {msg}")
    if "--json" in sys.argv:
        print(json.dumps({"rows": rows, "fails": fails, "warns": warns}, ensure_ascii=False, indent=1))
    else:
        n_ok = sum(1 for r in rows if r["level"] == "OK")
        print(f"[check_wrangler_auth] wrangler実行ファイル {len(rows)} 件: OK {n_ok} / "
              f"FAIL {sum(r['level']=='FAIL' for r in rows)} / WARN {sum(r['level']=='WARN' for r in rows)}")
        print(f"  最小環境 cf_env: {msg}")
        for x in fails:
            print("  ❌", x)
        for x in warns:
            print("  ⚠", x)
        print("RESULT:", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
