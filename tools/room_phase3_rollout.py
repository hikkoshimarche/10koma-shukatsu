#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""room_phase3_rollout.py — Phase3 全社展開(三井除く・業界段階・人数可変v3・★並列3)。
Phase2ゲート全通過が前提。各社独立: v3生成→room-lint5→pass時のみD1登録／error社は隔離(非登録・ログ・GAS転記)。
並列度3(画像fanoutで429ゼロ実証済)。429検出で自動的に並列2へ降格。20社毎gitチェックポイント。各業界完了時にタブ更新。
resumable: room_sync_state.csv の registered-v3 はスキップ。三井GOLD(personas表)は不可侵。
使い方: nohup caffeinate -dimsu python3 -u room_phase3_rollout.py > _room_phase3.log 2>&1 &
        [--industry <アーキタイプ>] [--limit N] [--push-every 20] [--conc 3]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path("/Users/oscardodds/projects/10koma-shukatsu")
SCR = Path(os.path.expanduser("~/oscar-ai/tokyari-pipeline/scripts"))
sys.path.insert(0, str(REPO / "tools")); sys.path.insert(0, str(SCR))  # scripts優先(ROOT=factsheet所在)
try:
    from dotenv import load_dotenv as _ld; _ld(os.path.expanduser("~/oscar-ai/tokyari-pipeline/.env"))
except Exception:
    pass
import room_lib as RL
import room_harness as H
import room_industry_roles_v3 as V3
import requests

ISO_FILE = REPO / "tools" / "_room_isolated.json"
PROG_FILE = REPO / "tools" / "_room_phase3_progress.json"
GAS_URL = os.environ.get("SHEET_WEBAPP_URL", "").strip()
GAS_TOKEN = os.environ.get("SHEET_API_TOKEN", "").strip()

# ---- 並列制御 + 429監視/自動降格 ----
_LOCK = threading.Lock()          # save_state/counters/checkpoint/git を直列化
_GITLOCK = threading.Lock()       # git操作は排他
CONC = threading.Semaphore(3)     # 並列度(既定3)。429検出で1permit恒久取得→実効2へ降格。
_STATE = {"downgraded": False, "r429": 0, "in": 0, "out": 0, "calls": 0}
_KEY = re.sub(r"\s", "", os.environ["ANTHROPIC_API_KEY"])


def _downgrade():
    """429検出時: 並列3→2へ自動降格(permitを1つ恒久取得)。1回のみ。"""
    with _LOCK:
        if _STATE["downgraded"]:
            return
        _STATE["downgraded"] = True
    CONC.acquire()  # 実効並列を1減(空くまでブロック=次に1社終わり次第2並列に)
    print(f"⚠️ 429検出({_STATE['r429']}件) → 並列3→2へ自動降格", flush=True)


def measured_anthropic(prompt, system="", model="claude-sonnet-4-6", max_tokens=3000):
    """RL._anthropic互換 + 429カウント/トークン計測。429を観測したら降格をトリガ。"""
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    for attempt in range(5):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                              headers={"x-api-key": _KEY, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json"}, json=body, timeout=180)
            if r.status_code == 429:
                with _LOCK:
                    _STATE["r429"] += 1
                _downgrade()
                raise requests.exceptions.RequestException("429")
            if r.status_code in (500, 502, 503, 529):
                raise requests.exceptions.RequestException(f"retry {r.status_code}")
            r.raise_for_status()
            j = r.json(); u = j.get("usage", {})
            with _LOCK:
                _STATE["in"] += u.get("input_tokens", 0); _STATE["out"] += u.get("output_tokens", 0); _STATE["calls"] += 1
            return "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)
    raise RuntimeError("anthropic失敗")


RL._anthropic = measured_anthropic


def git(*a):
    return subprocess.run(["git", *a], cwd=str(REPO), capture_output=True, text=True, timeout=120)


def checkpoint(msg, isolated, reg, blocked, total, t0):
    with _GITLOCK:
        ISO_FILE.write_text(json.dumps(isolated, ensure_ascii=False, indent=2), encoding="utf-8")
        PROG_FILE.write_text(json.dumps({"reg": reg, "blocked": blocked, "total": total,
                                         "conc": (2 if _STATE["downgraded"] else 3), "r429": _STATE["r429"],
                                         "elapsed_min": round((time.time() - t0) / 60)},
                                        ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            (REPO / "tools" / "room_sync_state_snapshot.csv").write_text(
                (SCR.parent / "output" / "room_sync_state.csv").read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass
        git("add", "tools/_room_isolated.json", "tools/_room_phase3_progress.json",
            "tools/room_sync_state_snapshot.csv")
        c = git("commit", "-m", msg)
        if c.returncode == 0:
            git("push", "origin", "main")


def run_tab_sync():
    try:
        subprocess.run([sys.executable, str(SCR / "room_tab_sync.py")], cwd=str(SCR),
                       capture_output=True, text=True, timeout=1800)  # POST大バッチ化で通常~数十秒
        if GAS_URL:
            requests.get(GAS_URL, params={"mode": "roomdashboard", "token": GAS_TOKEN}, timeout=90)
    except Exception as e:
        print(f"  ⚠ tab_sync失敗: {e}", flush=True)


def push_isolated(isolated):
    if not (GAS_URL and isolated):
        return
    rows = ";;".join(f"{it['name']}\t{it['slug']}\troom-lint5\t{it['reason']}\tv3再生成で再挑戦" for it in isolated)
    try:
        requests.post(GAS_URL, data={"mode": "roomblockedtab", "token": GAS_TOKEN, "rows": rows}, timeout=90)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--industry")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--push-every", type=int, default=20)
    ap.add_argument("--conc", type=int, default=3)
    ap.add_argument("--slugs", help="対象slugをカンマ区切りで限定(再fanout用・registered-v3でも強制処理)")
    ap.add_argument("--no-git", action="store_true", help="gitチェックポイントを行わない(本体rollout並走時の競合回避)")
    ap.add_argument("--no-tabsync", action="store_true", help="業界完了時のタブ同期を行わない(本体並走時の競合回避)")
    args = ap.parse_args()
    only = set(s.strip() for s in args.slugs.split(",")) if args.slugs else None
    global CONC
    CONC = threading.Semaphore(args.conc)

    cj = json.loads((REPO / "public" / "companies.json").read_text(encoding="utf-8"))
    id2name = {x["id"]: x["name"] for l in cj.values() for x in l}
    id2ind = {x["id"]: ind for ind, l in cj.items() for x in l}
    done = H.load_state()
    _rev = {v: k for k, v in getattr(H._cm, "TOKYARI_SLUG_OVERRIDES", {}).items()}

    targets = []
    for s, ind in id2ind.items():
        if s == "mitsui-bussan":
            continue
        if only is not None:
            if s not in only:
                continue                      # 再fanout: 指定slugのみ(registered-v3でも強制)
        elif done.get(s) == "registered-v3":
            continue
        tslug = _rev.get(s, s)
        if not ((H.ROOT / "output" / tslug / "factsheet.md").exists() or (H.ROOT / "output" / s / "factsheet.md").exists()):
            continue
        arch = V3.archetype_for(s, ind)   # ★slug対応(「その他」外資大手の誤バケツ防止)
        if args.industry and arch != args.industry:
            continue
        targets.append((s, id2name.get(s, s), ind, arch))
    targets.sort(key=lambda t: (V3.expected_size_company(t[0], t[2]), t[3], t[0]))
    by_arch = {}
    for t in targets:
        by_arch.setdefault(t[3], []).append(t)

    isolated = json.loads(ISO_FILE.read_text()) if ISO_FILE.exists() else []
    iso_slugs = {it["slug"] for it in isolated}
    ctr = {"reg": 0, "blocked": 0}
    total = len(targets); t0 = time.time()
    print(f"=== Phase3 全社展開(並列{args.conc}): 対象{total}社 / {len(by_arch)}アーキタイプ (三井除外・resumable) ===", flush=True)

    def work(item):
        slug, name, ind18, arch = item
        CONC.acquire()
        try:
            ts = time.time()
            try:
                rec = H.process(slug, name, force=True, industry=ind18)
            except Exception as e:
                rec = {"status": f"例外:{e}"}
            rec["_sec"] = round(time.time() - ts)
            return item, rec
        finally:
            CONC.release()

    for arch, lst in by_arch.items():
        print(f"\n--- 業界: {arch} ({len(lst)}社) 並列{args.conc if not _STATE['downgraded'] else 2} ---", flush=True)
        arch_iso = []
        with ThreadPoolExecutor(max_workers=args.conc) as ex:
            futs = [ex.submit(work, it) for it in lst]
            for fut in as_completed(futs):
                (slug, name, ind18, a), rec = fut.result()
                st = rec.get("status", "?")
                with _LOCK:
                    if st == "registered":
                        ctr["reg"] += 1
                        H.save_state(slug, "registered-v3")
                        done_n = ctr["reg"] + ctr["blocked"]
                        print(f"  ✅ {slug:<18} {rec.get('n_roles')}人 {arch} ({rec.get('_sec')}s) [{ctr['reg']}登録/{done_n}済/{total}]", flush=True)
                    else:
                        ctr["blocked"] += 1
                        if slug not in iso_slugs:
                            reason = st if "lint" in st else st[:40]
                            isolated.append({"slug": slug, "name": name, "arch": arch, "reason": reason,
                                             "detail": rec.get("lint_detail", {})}); iso_slugs.add(slug); arch_iso.append(isolated[-1])
                        H.save_state(slug, st)
                        print(f"  ⚠ 隔離 {slug:<18} {st[:40]}", flush=True)
                    done_n = ctr["reg"] + ctr["blocked"]
                if not args.no_git and done_n % args.push_every == 0:
                    checkpoint(f"chore(room-v3): Phase3 checkpoint {ctr['reg']}登録/{ctr['blocked']}隔離 (/{total})",
                               isolated, ctr["reg"], ctr["blocked"], total, t0)
                if args.limit and done_n >= args.limit:
                    break
        push_isolated(arch_iso)
        if not args.no_tabsync:
            run_tab_sync()
        print(f"  [業界 {arch} 完了] 累計 登録{ctr['reg']}/隔離{ctr['blocked']} 経過{round((time.time()-t0)/60)}分 並列{'2' if _STATE['downgraded'] else str(args.conc)}", flush=True)
        if args.limit and (ctr["reg"] + ctr["blocked"]) >= args.limit:
            break

    if not args.no_git:
        checkpoint(f"chore(room-v3): Phase3 完了 {ctr['reg']}登録/{ctr['blocked']}隔離 (/{total})",
                   isolated, ctr["reg"], ctr["blocked"], total, t0)
    else:
        ISO_FILE.write_text(json.dumps(isolated, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== Phase3 完了: 登録{ctr['reg']} / 隔離{ctr['blocked']} / 対象{total} "
          f"経過{round((time.time()-t0)/60)}分 429={_STATE['r429']} 最終並列{'2' if _STATE['downgraded'] else str(args.conc)} ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
