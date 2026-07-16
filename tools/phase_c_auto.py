#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""phase_c_auto.py — Phase C 自動化オーケストレータ(毎時ループ拡張分)。

deploy_fb.py(台本FB反映)の後段で呼ばれ、画像系の人手工程を型別に自走させる。
既存の phase_c_image_fix.py(安全型エンジン)と fix_and_deploy / deploy_salary の
ゲート済み部品を再利用し、新規は「協調反映」「混在型=候補生成+人QA」「人QA消化」の
オーケストレーションのみ。**全ゲート(lint/QA/canary/404)は絶対に外さない。**

自動化レベル(型別フラグ・既定は安全側):
  master  AUTO_IMAGE_FIX_ENABLED=1 でのみライブ稼働(既定OFF=dry。テキストFB反映とは独立)。
  安全型   AUTO_SAFE_TYPES=meta_frame,white_band,hline,text_leak → full auto(QA/canary/404通過分のみ反映)。
  協調型   AUTO_COORDINATED=1 → 入口3社型(台本+画像を同一トランザクションで反映。片方だけの反映を構造禁止)。
  混在型   AUTO_MIXED_MODE=notify → 候補画像を自動生成→レビューURL→LINEで人QA依頼まで(自動反映しない)。
           人は OK/NG を返すだけ。OK は次ループの consume_human_qa が全ゲート付きで反映。

キルスイッチ: launchctl unload com.tokyari.phasec / または AUTO_IMAGE_FIX_ENABLED=0。
"""
from __future__ import annotations
import json, os, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
TOKYARI = Path.home() / "oscar-ai" / "tokyari-pipeline"
sys.path.insert(0, str(TOKYARI / "scripts"))

import phase_c_image_fix as PCI      # noqa: E402  (translate/classify/guard/hard_gate/state)
import deploy_salary as D            # noqa: E402  (update_sql/canary/backup/wrangler/API_BASE)

COORD_REGISTRY = REPO / "tools" / "_coordinated_targets.json"
EXTRA_IMG_REGISTRY = REPO / "tools" / "_image_targets_extra.json"
DRAINED_FILE = REPO / "tools" / ".image_drained.json"
SAFE_TYPES_DEFAULT = "meta_frame,white_band,hline,text_leak"


def _drained_set():
    """反映成功した安全型backlog(slug#koma)の集合。再生成防止(良い画像を上書きしない)。"""
    try:
        return set(json.load(open(DRAINED_FILE, encoding="utf-8")))
    except Exception:
        return set()


def _mark_drained(keys):
    if not keys:
        return
    cur = _drained_set() | set(keys)
    try:
        json.dump(sorted(cur), open(DRAINED_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass


def _unmark_drained(keys):
    cur = _drained_set() - set(keys)
    try:
        json.dump(sorted(cur), open(DRAINED_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass


NG_HINTS_FILE = REPO / "tools" / ".image_ng_hints.json"


def _set_ng_hint(slug, koma, comment):
    try:
        h = json.load(open(NG_HINTS_FILE, encoding="utf-8"))
    except Exception:
        h = {}
    h[f"{slug}#{koma}"] = comment
    try:
        json.dump(h, open(NG_HINTS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception:
        pass


def _get_ng_hint(slug, koma):
    try:
        return json.load(open(NG_HINTS_FILE, encoding="utf-8")).get(f"{slug}#{koma}", "")
    except Exception:
        return ""


# ============================================================================
# 型別フラグ
# ============================================================================
def auto_cfg():
    base = PCI.cfg()
    def _env(k, d):
        v = os.environ.get(k)
        return v if v not in (None, "") else d
    base.update({
        "safe_types": set(s.strip() for s in _env("AUTO_SAFE_TYPES", SAFE_TYPES_DEFAULT).split(",") if s.strip()),
        "coordinated": _env("AUTO_COORDINATED", "1") == "1",
        "mixed_mode": _env("AUTO_MIXED_MODE", "notify"),   # notify | off
        # FIX1: 混在型は 1ループ上限件数を絞る(既定3)。安全型→協調→混在の順で枠(hour上限)を配分し、
        #   安全型が常に先に枠を取る。per_koマ到達/起票済は再生成しない(洪水=クレジット浪費の停止)。
        "mixed_max_per_loop": int(_env("AUTO_MIXED_MAX_PER_LOOP", "3")),
    })
    return base


# ============================================================================
# 協調反映ゲート(STEP2.2 の核) — 片方だけの反映を構造的に禁止する純関数
# ============================================================================
def can_coordinate_reflect(lint_err: int, qa_pass: bool) -> bool:
    """台本(lint error0)と画像(QA通過)の**両方**が整った時のみ True。

    片方だけ True では False を返す = 新画像/旧台本 も 新台本/旧画像 も作らない。
    この関数を通らない限り D1書き込みに到達できない構造にすること(壊れFB防止の関所)。
    """
    return bool(lint_err == 0 and qa_pass)


def decide_coordinated(lint_err: int, qa_pass: bool) -> str:
    """反映判断を明示。書き込み側は 'reflect_both' 以外では一切D1へ書かない。"""
    if lint_err != 0:
        return "abort_text_not_ready"       # 台本未整備 → 画像も反映しない
    if not qa_pass:
        return "abort_image_not_ready"       # 画像QA不可 → 台本も反映しない
    return "reflect_both"


# ============================================================================
# 協調反映 1件(入口3社型: 台本+画像を同一トランザクションで)
# ============================================================================
def _v4_after(tslug, koma):
    """scenario_v4.json の該当koマから D1反映用 after={script,main_copy,sub_copy} を作る。"""
    p = TOKYARI / "output" / tslug / "scenario_v4.json"
    sc = json.load(open(p, encoding="utf-8"))
    k = next((x for x in sc.get("koma", []) if x.get("koma_number") == koma), None)
    if not k:
        return None
    ov = k.get("overlay_text") or {}
    return {"script": list(k.get("script") or []),
            "main_copy": ov.get("main_copy", ""), "sub_copy": ov.get("sub", ov.get("sub_copy", ""))}


def _v4_lint_err(tslug):
    """scenario_v4.json 全体の v5_ext error 数(台本readiness ゲート)。"""
    import scenario_lints_v5_ext as v5
    sc = json.load(open(TOKYARI / "output" / tslug / "scenario_v4.json", encoding="utf-8"))
    return v5.run_ext_lints(sc, tslug)["errors"]


def coordinated_reflect_one(target, dry, st, c):
    """入口型1社を協調反映。target={slug,tslug,image_komas,text_komas,label}。
      image_komas: 画像再生成が要るコマ(k1等)。text_komas: 台本反映が要るコマ(k1+隣接)。
    構造保証: can_coordinate_reflect(両ゲート)を通らない限り D1へは1バイトも書かない。"""
    slug = target["slug"]; tslug = target.get("tslug", slug)
    image_komas = target["image_komas"]; text_komas = target.get("text_komas", image_komas)
    komas = sorted(set(image_komas) | set(text_komas))
    rec = {"mode": "coordinated", "slug": slug, "tslug": tslug,
           "image_komas": image_komas, "text_komas": text_komas,
           "label": target.get("label", ""), "lint_err": None, "qa_pass": None,
           "decision": None, "reflected": False, "escalate": None, "qa": []}

    # --- 台本readiness(lint error0) ---
    try:
        lint_err = _v4_lint_err(tslug)
    except Exception as e:
        rec["escalate"] = f"lint読込失敗: {e}"; return rec
    rec["lint_err"] = lint_err
    afters = {}
    for koma in text_komas:
        a = _v4_after(tslug, koma)
        if a is None:
            rec["escalate"] = f"scenario_v4 koma{koma}不在"; return rec
        afters[koma] = a

    # --- master/協調フラグ ---
    if not c["enabled"] or not c["coordinated"]:
        rec["decision"] = "flag_off_dry"
        rec["note"] = f"AUTO_IMAGE_FIX_ENABLED={int(c['enabled'])}/AUTO_COORDINATED={int(c['coordinated'])} → dry"
        dry = True

    # --- DRY: 生成せず、両ゲートの現状と判断のみ ---
    if dry:
        # 画像側は未生成なので qa_pass 未知。lint のみ提示し、判断は「画像QA後に確定」。
        rec["decision"] = "dry_plan"
        rec["note"] = (f"DRY: 台本lint_err={lint_err}({'OK' if lint_err==0 else 'NG'}). "
                       f"ライブなら 画像{image_komas}再生成→QA→(lint0 & 全QA両立時のみ)"
                       f"台本{text_komas}+画像{image_komas}を同一トランザクション反映→canary→404。"
                       f"片方成立では一切反映しない。")
        return rec

    # ===== ライブ =====
    import fix_and_deploy as FAD
    FAD.SLUG_MAP.setdefault(tslug, slug)
    # 早期関所: 台本NGなら画像生成にクレジットを使わず中止(画像も反映しない)。
    if lint_err != 0:
        rec["decision"] = "abort_text_not_ready"
        rec["escalate"] = f"lint error={lint_err} → 台本未整備。画像も反映しない(協調中止)"
        return rec

    D.backup_d1(slug)
    canary_before = D.canary_snapshot({slug})

    # 画像を image_komas 再生成→ハードQA。1つでも不可なら img_ready=False(=台本も反映しない)。
    shas = {}; img_ready = True
    for koma in image_komas:
        allowed, reason, showcase = PCI.guard(slug, koma, st, c)
        if not allowed:
            rec["escalate"] = f"koma{koma} ガード不可: {reason}"; img_ready = False; break
        excerpt = PCI._scenario_excerpt(tslug, koma)
        instr = PCI.build_regen_instruction(f"入口固有化: {target.get('label','')}", ["text_leak"])  # baseline制約
        FAD.add_fix_instructions_to_scenario(tslug, koma, [instr])
        gate_ok = False
        for attempt in range(1, PCI.QA_MAX + 1):
            FAD.regenerate_panel(tslug, koma)
            gate_ok, sev, cmv, cost = PCI.hard_gate(tslug, koma)
            st["day_cost"] += cost; st["hour_events"].append(time.time())
            rec["qa"].append({"koma": koma, "attempt": attempt, "severity": sev, "char_match": cmv})
            if gate_ok:
                break
        st["per_koma"][f"{slug}#{koma}"] = st["per_koma"].get(f"{slug}#{koma}", 0) + 1
        if not gate_ok:
            img_ready = False
            rec["escalate"] = f"koma{koma} QA{PCI.QA_MAX}回不可 → 台本も反映しない(協調中止)"
            break
        panel = FAD.copy_panel_to_deploy(tslug, koma)
        shas[koma] = FAD.git_commit_push(panel, f"fix(image:{slug}): koma{koma:02d} 入口固有化(協調)")
        FAD.wait_jsdelivr(slug, koma, shas[koma])
    rec["qa_pass"] = img_ready

    # ★構造ゲート: 両方揃った時のみ書き込みに進む
    decision = decide_coordinated(lint_err, img_ready)
    rec["decision"] = decision
    if not can_coordinate_reflect(lint_err, img_ready):
        # ここに来たら D1へは書かない(画像はpush済みだがD1のimage_urlは更新しない=liveは旧画像+旧台本のまま整合)
        rec["escalate"] = rec["escalate"] or f"協調ゲート不成立({decision}) → D1反映せず"
        return rec

    # --- 台本(text_komas)+画像(image_komas)を同一wranglerコマンドで反映(両方 or どちらも無し) ---
    stmts = []
    for koma in text_komas:
        stmts.append(D.update_sql(slug, koma, afters[koma]).rstrip(";"))    # 台本列(image_url不変)
    for koma in image_komas:
        img_url = f"https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@{shas[koma]}/public/images/{slug}/panel_{koma:02d}.png"
        stmts.append(f"UPDATE company_panels SET image_url='{img_url}' WHERE company_id='{slug}' AND panel_num={koma}")
    proc = D.wrangler(["--command", ";\n".join(stmts) + ";"])
    if proc.returncode != 0:
        rec["escalate"] = f"D1協調UPDATE失敗: {proc.stderr[:160]}"; return rec

    # --- canary(対象外不変) + 404/整合検証 ---
    drift = D.canary_diff(canary_before, D.canary_snapshot({slug}))
    if drift:
        rec["escalate"] = f"🛑canary異常 対象外変化{drift} → 要revert(backup有)"
        PCI.push_line(f"🛑【協調反映 canary異常】{slug}: 対象外{drift}変化。要調査。")
        return rec
    ok_all = True
    for koma in image_komas:
        if not FAD.verify_api_url_updated(slug, koma, shas[koma]):
            ok_all = False
    rec["reflected"] = ok_all
    if ok_all:
        PCI.gas({"mode": "setreflected", "company": target.get("company", slug)})
        rec["note"] = "協調反映成功: 台本+画像を同時反映・canary/404通過"
        # FIX2: DoD完備 — 該当社のみ Notion同期(非破壊v41-safe)。3層一致(D1=source=Notion)。
        rec["notion"] = _notion_sync_one(tslug, label=target.get("label", ""))
    else:
        rec["escalate"] = "API検証NG(画像URL未更新の社あり)"
    return rec


def _notion_sync_one(tslug, label=""):
    """該当社のみ Notion を非破壊同期(正本 notion_sync.py --v41-safe)。反映は既に成功済のため非ブロック。"""
    import subprocess
    try:
        p = subprocess.run(
            [str(TOKYARI / ".venv" / "bin" / "python"), str(TOKYARI / "scripts" / "notion_sync.py"),
             "--v41-safe", "--slug", tslug,
             "--version-label", "v4.1 入口固有化(協調反映)",
             "--change-summary", (label or "入口k1差替を協調反映に伴いNotion同期")],
            cwd=str(TOKYARI), capture_output=True, text=True, timeout=180)
        return {"rc": p.returncode, "tail": (p.stdout or p.stderr or "")[-160:]}
    except Exception as e:
        return {"rc": -1, "err": str(e)[:160]}


# ============================================================================
# 混在型: 候補生成 → レビューURL → LINEで人QA依頼(自動反映しない)
# ============================================================================
def review_url(slug, koma, sha):
    """人が見る候補画像URL(jsDelivr pinned)。"""
    return f"https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@{sha}/public/images/{slug}/panel_{koma:02d}.png"


def mixed_notify_one(company, slug, tslug, koma, detail, instruction, dry, st, c):
    """混在型: 候補画像を生成(反映せず)→レビューURL発行→LINE人QA依頼→スプシ人QA列に起票。
    自動反映は一切しない。人が OK を返すと次ループ consume_human_qa が全ゲート付きで反映。"""
    rec = {"mode": "mixed_notify", "company": company, "slug": slug, "koma": koma,
           "detail": detail, "candidate_url": None, "notified": False, "escalate": None}
    if c["mixed_mode"] != "notify":
        rec["escalate"] = f"AUTO_MIXED_MODE={c['mixed_mode']} → 混在型は通知しない"; return rec
    if dry or not c["enabled"]:
        rec["note"] = "DRY: ライブなら候補生成(反映せず)→レビューURL→LINE人QA依頼→スプシ起票"
        return rec

    import fix_and_deploy as FAD
    FAD.SLUG_MAP.setdefault(tslug, slug)
    allowed, reason, showcase = PCI.guard(slug, koma, st, c)
    if not allowed:
        rec["escalate"] = f"ガード不可: {reason}"; return rec
    ng_hint = _get_ng_hint(slug, koma)   # 前回NG理由があれば次プロンプトに反映
    instr2 = (instruction + f" 【前回のNG指摘を必ず反映】{ng_hint}") if ng_hint else instruction
    FAD.add_fix_instructions_to_scenario(tslug, koma, [instr2])
    gate_ok = False
    for attempt in range(1, PCI.QA_MAX + 1):
        FAD.regenerate_panel(tslug, koma)
        gate_ok, sev, cmv, cost = PCI.hard_gate(tslug, koma)
        st["day_cost"] += cost; st["hour_events"].append(time.time())
        if gate_ok:
            break
    st["per_koma"][f"{slug}#{koma}"] = st["per_koma"].get(f"{slug}#{koma}", 0) + 1
    if not gate_ok:
        rec["escalate"] = f"候補QA{PCI.QA_MAX}回不可(sev={sev}) → 通知せず据置"; return rec
    # 候補をレビュー用にpush(D1のimage_urlは更新しない=liveは旧画像のまま)
    panel = FAD.copy_panel_to_deploy(tslug, koma)
    sha = FAD.git_commit_push(panel, f"review(image:{slug}): koma{koma:02d} 候補(混在型・人QA待ち)")
    rec["candidate_url"] = review_url(slug, koma, sha)
    # スプシ人QA列に起票(OK記入で次ループ反映)
    PCI.gas({"mode": "addimageqa", "company": company, "slug": slug, "koma": str(koma),
             "sha": sha, "url": rec["candidate_url"], "detail": detail[:80]})
    PCI.push_line(f"🖼【人QA依頼】{company} koマ{koma}\n候補: {rec['candidate_url']}\n"
                  f"OKなら反映/NGなら再生成。スプシ『画像人QA』にOK/NG記入で自動反映。")
    rec["notified"] = True
    return rec


# ============================================================================
# 人QA消化: スプシ『画像人QA』でOKの候補を全ゲート付きで反映
# ============================================================================
def consume_human_qa(dry, st, c):
    """スプシ人QA列で status=OK の候補(sha)を、canary/404付きでD1反映(image_urlのみ)。"""
    out = []
    try:
        d = PCI.gas({"mode": "imageqa_approved"})
    except Exception as e:
        return [{"escalate": f"imageqa取得失敗: {e}"}]
    for it in d.get("items", []):
        slug = it.get("slug"); koma = int(it.get("koma", 0)); sha = it.get("sha", "")
        rec = {"mode": "human_qa_consume", "slug": slug, "koma": koma, "sha": sha, "reflected": False}
        if not (slug and koma and sha):
            rec["escalate"] = "行不備(slug/koma/sha)"; out.append(rec); continue
        if dry or not c["enabled"]:
            rec["note"] = f"DRY: OK候補 {slug}#{koma}@{sha} をライブなら反映(canary/404)"; out.append(rec); continue
        import fix_and_deploy as FAD
        D.backup_d1(slug); cb = D.canary_snapshot({slug})
        FAD.update_d1_panel(slug, koma, sha)
        if D.canary_diff(cb, D.canary_snapshot({slug})):
            rec["escalate"] = "🛑canary異常"; out.append(rec); continue
        rec["reflected"] = FAD.verify_api_url_updated(slug, koma, sha)
        if rec["reflected"]:
            PCI.gas({"mode": "setimageqa", "slug": slug, "koma": str(koma), "status": "反映済"})
            _mark_drained([f"{slug}#{koma}"])   # 反映済=以後再生成しない/pending集計から除外
        out.append(rec)
    # NG → 再生成キューへ差し戻し(NG理由を次プロンプトに反映)。
    try:
        ng = PCI.gas({"mode": "imageqa_ng"}).get("items", [])
    except Exception:
        ng = []
    for it in ng:
        slug = it.get("slug"); koma = int(it.get("koma", 0)); comment = str(it.get("comment", "")).strip()
        if not (slug and koma):
            continue
        rec = {"mode": "human_qa_ng", "slug": slug, "koma": koma, "requeued": False}
        if dry or not c["enabled"]:
            rec["note"] = f"DRY: NG {slug}#{koma} を再生成キューへ(理由:{comment[:40]})"; out.append(rec); continue
        _set_ng_hint(slug, koma, comment)                       # NG理由を次生成プロンプトへ
        st["per_koma"].pop(f"{slug}#{koma}", None)              # cap解除=再生成を許可
        _unmark_drained([f"{slug}#{koma}"])                     # 再びpending対象に
        PCI.gas({"mode": "setimageqa", "slug": slug, "koma": str(koma), "status": "再生成待ち"})
        rec["requeued"] = True; out.append(rec)
    return out


# ============================================================================
# バッチ・オーケストレーション(deploy_fb 後段から呼ばれる)
# ============================================================================
def _tslug(slug):
    try:
        import company_master as CM
        if hasattr(CM, "TOKYARI_SLUG_OVERRIDES"):
            return {v: k for k, v in CM.TOKYARI_SLUG_OVERRIDES.items()}.get(slug, slug)
    except Exception:
        pass
    return slug


def _classify_image_item(company, slug, tslug, koma, detail, c):
    """画像FB1件を translate→型分類。返り値 {kind:'safe'|'mixed'|'skip', instruction, ...}。生成はしない。"""
    try:
        tr = PCI.translate_image_fb(company, slug, koma, detail, PCI._scenario_excerpt(tslug, koma))
    except Exception as e:
        return {"kind": "mixed", "company": company, "slug": slug, "tslug": tslug, "koma": koma,
                "detail": detail, "instruction": PCI.build_regen_instruction(detail, ["scale"]),
                "note": f"translate失敗→mixed:{e}"}
    if tr.get("route") == "script":
        return {"kind": "skip", "slug": slug, "koma": koma}    # overlay文字=台本経路(deploy_fbが担当)
    typ = tr.get("type", ""); cats = set(tr.get("cats", []))
    is_safe = tr.get("action") == "auto" and (
        typ in c["safe_types"] or (typ == "compound" and cats and cats <= c["safe_types"]))
    instr = tr.get("instruction") or PCI.build_regen_instruction(detail, list(cats) or ["scale"])
    return {"kind": "safe" if is_safe else "mixed", "company": company, "slug": slug, "tslug": tslug,
            "koma": koma, "detail": detail, "instruction": instr, "type": typ}


def collect_image_fbs(c, results):
    """attention由来の画像FB + 追加ターゲットを収集・型分類(生成しない)。返り値 (safe_items, mixed_items)。"""
    safe_items, mixed_items = [], []
    def _add(company, slug, tslug, koma, detail):
        item = _classify_image_item(company, slug, tslug, koma, detail, c)
        if item["kind"] == "safe":
            safe_items.append(item)
        elif item["kind"] == "mixed":
            mixed_items.append(item)
    try:
        import phase_c_autoloop as A
        items = [it for it in A.fetch_attention() if it.get("content") == "10コマ"]
    except Exception as e:
        items = []; results["note"] += f" [attention取得失敗:{e}]"
    for it in items:
        company = it.get("company", "")
        try:
            slug = A.resolve_slug(company)
        except Exception:
            slug = None
        if not slug:
            continue
        try:
            tri = PCI.L.triage_fb(company, it.get("fb", ""))
        except Exception as e:
            results["note"] += f" [{company} triage失敗:{e}]"; continue
        tslug = _tslug(slug)
        for b in tri.get("image_bugs", []):
            koma = b.get("koma") or PCI.L.extract_koma(b.get("detail", ""))
            if koma:
                _add(company, slug, tslug, koma, b.get("detail", ""))
    if EXTRA_IMG_REGISTRY.exists():
        try:
            extra = json.load(open(EXTRA_IMG_REGISTRY, encoding="utf-8")).get("targets", [])
        except Exception:
            extra = []
        for t in extra:
            _add(t.get("company", ""), t.get("slug", ""), t.get("tslug", t.get("slug", "")),
                 int(t.get("koma", 0)), t.get("detail", ""))
    # (c) 安全型backlogドレイン: コモンフィックス[要画像再生成]の安全型のみ決定的分類で追加(LLM不使用)。
    #     反映済(drained)は除外=良い画像を上書きしない。混在型はここでは足さない(attention+人QAで処理)。
    import re as _re
    try:
        import phase_c_autoloop as A
        drained = _drained_set()
        cf = PCI.gas({"mode": "commonfixes"})
        seen_bk = set(f"{it['slug']}#{it['koma']}" for it in safe_items)
        for x in cf.get("items", []):
            m = _re.match(r"\[要画像再生成\]\s*([^:：]+?)[:：]\s*(.*)", str(x.get("rule", "")), _re.S)
            if not m:
                continue
            company = m.group(1).strip()
            try:
                slug = A.resolve_slug(company)
            except Exception:
                slug = None
            if not slug:
                continue
            tslug = _tslug(slug)
            for km in _re.split(r"(?:^|;|；)\s*(?=koma\s*\d+|コマ\s*\d+)", m.group(2)):
                kk = _re.search(r"(?:koma|コマ)\s*0*(\d+)\s*[:：]?\s*(.*)", km, _re.S)
                if not kk:
                    continue
                koma = int(kk.group(1)); detail = kk.group(2).strip()
                key = f"{slug}#{koma}"
                if key in seen_bk or key in drained:
                    continue
                cats = PCI.classify_image_bug_cats(detail)
                if set(cats) & c["safe_types"]:      # 安全型のみ(混在/描画型は足さない)
                    seen_bk.add(key)
                    safe_items.append({"kind": "safe", "company": company, "slug": slug, "tslug": tslug,
                                       "koma": koma, "detail": detail,
                                       "instruction": PCI.build_regen_instruction(detail, cats),
                                       "type": cats[0], "from_backlog": True})
    except Exception as e:
        results["note"] += f" [backlog drain失敗:{e}]"
    return safe_items, mixed_items


def _pending_image_map(cf_items=None, qa_items=None):
    """全社の未反映画像コマ map {slug: set(koma)} を1パスで構築(GAS呼び出しを最小化)。"""
    import re as _re
    import phase_c_autoloop as A
    drained = _drained_set()
    if cf_items is None:
        cf_items = PCI.gas({"mode": "commonfixes"}).get("items", [])
    if qa_items is None:
        qa_items = PCI.gas({"mode": "imageqa_list"}).get("items", [])
    m = {}
    for x in cf_items:
        mm = _re.match(r"\[要画像再生成\]\s*([^:：]+?)[:：]\s*(.*)", str(x.get("rule", "")), _re.S)
        if not mm:
            continue
        slug = A.resolve_slug(mm.group(1).strip())
        if not slug:
            continue
        for km in _re.findall(r"(?:koma|コマ)\s*0*(\d+)", mm.group(2)):
            if f"{slug}#{int(km)}" not in drained:
                m.setdefault(slug, set()).add(int(km))
    for it in qa_items:
        slug = it.get("slug"); koma = int(it.get("koma", 0))
        if slug and f"{slug}#{koma}" not in drained:
            m.setdefault(slug, set()).add(koma)
    return m


def _pending_image_komas(slug, pmap=None):
    """slugの未反映画像コマ集合(pmap未指定なら都度構築)。"""
    if pmap is None:
        pmap = _pending_image_map()
    return pmap.get(slug, set())


PENDING_SNAPSHOT = REPO / "tools" / ".image_pending_snapshot.json"


def _pending_stall_map(pmap, persist=True):
    """pending画像数が『減っていない』日数を社別に返す {slug: stall_days}。
       setpartialが最終更新をbumpしても影響されない停滞検知(安全型がまた静かに詰まっても3日で浮上)。
       pending数が減れば(=消化が進めば)since=now にリセット。副作用: スナップショット更新(persist時)。"""
    from datetime import datetime as _dt
    now = _dt.now()
    try:
        snap = json.load(open(PENDING_SNAPSHOT, encoding="utf-8"))
    except Exception:
        snap = {}
    cur = {s: len(k) for s, k in pmap.items() if k}
    out = {}
    for slug, count in cur.items():
        prev = snap.get(slug)
        if not prev or prev.get("count") != count:      # 数が変化(消化 or 新規)→ 停滞リセット
            snap[slug] = {"count": count, "since": now.isoformat()}
        try:
            out[slug] = (now - _dt.fromisoformat(snap[slug]["since"])).days
        except Exception:
            out[slug] = 0
    for slug in list(snap):                              # pendingが0になった社は除去
        if slug not in cur:
            snap.pop(slug, None)
    if persist:
        try:
            json.dump(snap, open(PENDING_SNAPSHOT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        except Exception:
            pass
    return out


def refresh_label(slug, company):
    """【根治】画像反映イベント直後に呼ぶ: 残画像FB数を再計算し反映列ラベルを更新(stale表示の再発防止)。
       残>0 → 『台本済・画像待ちN件』/ 残0 → 反映済。手動setpartialのズレを構造的に無くす。"""
    # 画像人QAシートの反映済(drained)行を『反映済』化(stale待ち行の掃除)。
    try:
        drained = _drained_set()
        for it in PCI.gas({"mode": "imageqa_list"}).get("items", []):
            if it.get("slug") == slug and f"{slug}#{int(it.get('koma', 0))}" in drained:
                PCI.gas({"mode": "setimageqa", "slug": slug, "koma": str(it.get("koma")), "status": "反映済"})
    except Exception:
        pass
    n = len(_pending_image_komas(slug))
    if n > 0:
        PCI.gas({"mode": "setpartial", "company": company, "nimg": str(n)})
    else:
        PCI.gas({"mode": "setreflected", "company": company})
    # 【恒久結線】反映イベント→監査タブ自動追従。手動/out-of-band反映でもFB滞留監査タブのstaleを防ぐ
    # (run_batchは末尾で_rebuild_audit_tabを別途呼ぶが、refresh_labelはバッチ外では未追従だった=今回のstale原因)。
    try:
        _rebuild_audit_tab()
    except Exception:
        pass
    return n


def _rebuild_audit_tab(pmap=None, stall=None):
    """監査タブ FB滞留監査 を最新化(画像反映で消えた行を反映・滞留日数/要対応/pending停滞を記載)。"""
    import re as _re
    try:
        import phase_c_autoloop as A
        from datetime import datetime as _dt
        now = _dt.now()
        d = PCI.gas({"mode": "unreflected_audit"})
        if pmap is None:
            pmap = _pending_image_map()   # 全社1パスで構築(GAS最小化)
        if stall is None:
            stall = _pending_stall_map(pmap, persist=False)   # pending数が72h以上減っていない社
        comp = {}
        for it in d.get("items", []):
            c = it["company"]
            if c not in comp:
                fb = str(it.get("fb", ""))
                img = bool(_re.search(r"画像|イラスト|吹き出し|空白|左手|右腕|腕|指|足|位置関係|外観|本社|リアル|将来像|余白|網掛け|構図|背景", fb))
                slug = A.resolve_slug(c)
                pend = sorted(pmap.get(slug, set())) if slug else []
                # 滞留日数 = 最終更新からの経過日数(空欄化バグの是正)。
                try:
                    sd = (now - _dt.strptime(str(it.get("updated", ""))[:10], "%Y-%m-%d")).days
                except Exception:
                    sd = ""
                # 反映済(drained)コマは要約から除外=済んだコマ(例:住友k4)は監査に残さない。
                summary = (f"画像待ちコマ: {pend}" if pend else _re.sub(r"\s+", " ", fb)[:90])
                # pending停滞(72h以上減っていない)は最終更新bumpに関係なく要対応。
                stall_days = stall.get(slug, 0) if slug else 0
                need = bool((isinstance(sd, int) and sd > 7) or stall_days >= 3)
                comp[c] = {"company": c, "sheet": it.get("sheet", "10コマ"), "round": it.get("round", ""),
                           "owner": it.get("owner", ""), "updated": it.get("updated", ""), "stale_days": sd,
                           "reason": ("画像のみ(台本反映済)" if img else "要個別確認") + (f" / pending停滞{stall_days}日" if stall_days >= 3 else ""),
                           "needs_action": need, "summary": summary}
        import requests, os as _os
        url = _os.environ.get("SHEET_WEBAPP_URL", "").strip()
        tok = _os.environ.get("SHEET_API_TOKEN", "").strip()
        if url:
            requests.post(url, data={"mode": "write_audit_tab", "token": tok, "tab": "FB滞留監査_20260715",
                                     "rows": json.dumps(list(comp.values()), ensure_ascii=False)}, timeout=90)
    except Exception:
        pass


def _ticketed_set(c):
    """画像人QA sheet に既に 待ち/OK で起票済の {slug#koma} 集合(混在型の再通知を止める)。
    GAS未展開時は空集合(→per_koマ状態でdedup)。"""
    try:
        d = PCI.gas({"mode": "imageqa_list"})
        return set(f"{it.get('slug')}#{it.get('koma')}" for it in d.get("items", []))
    except Exception:
        return set()


def _per_koma_capped(slug, koma, st, c):
    return st["per_koma"].get(f"{slug}#{koma}", 0) >= c["per_koma_max"]


def load_coord_targets():
    if COORD_REGISTRY.exists():
        try:
            return json.load(open(COORD_REGISTRY, encoding="utf-8")).get("targets", [])
        except Exception:
            return []
    return []


def run_batch(dry=True):
    PCI._load_env()
    c = auto_cfg(); st = PCI.load_state()
    print("=" * 64)
    print(f"=== phase_c_auto バッチ [{'DRY' if dry else 'LIVE'}] ===")
    print(f"master AUTO_IMAGE_FIX_ENABLED={'ON' if c['enabled'] else 'OFF'} / "
          f"safe={sorted(c['safe_types'])} / coordinated={c['coordinated']} / mixed={c['mixed_mode']}")
    print(f"state day_cost=${st['day_cost']:.2f} hour={len(st['hour_events'])} paused={st['paused']}")
    print("=" * 64)
    results = {"human_qa": [], "coordinated": [], "safe": [], "mixed": [], "note": ""}

    # 1) 人QA OK候補の反映(前ラウンド承認分) — 最安・最優先で着地
    results["human_qa"] = consume_human_qa(dry, st, c)

    # master OFF(dry)では生成系(Claude triage/画像)を走らせない(浪費防止)。協調のdry計画のみ提示。
    if not (c["enabled"] or results.get("_force_route")):
        results["note"] += " [safe/mixed skip: master OFF(dry)。協調はdry計画のみ]"
        for t in load_coord_targets():
            results["coordinated"].append(coordinated_reflect_one(t, dry, st, c))
        return results

    # 収集(型分類のみ・生成しない)
    safe_items, mixed_items = collect_image_fbs(c, results)
    results["counts"] = {"safe_candidates": len(safe_items), "mixed_candidates": len(mixed_items)}

    # 2) 【優先1】安全型 full-auto を先に hour 枠へ(安全型が常に先に枠を取る)
    _drain_ok = []
    for it in safe_items:
        rec = PCI.run_one(it["company"], it["slug"], it["koma"], it["detail"], dry, st, c)
        results["safe"].append(rec)
        # backlogドレイン由来で反映成功 → drained記録(再生成防止=良い画像を上書きしない)
        if not dry and it.get("from_backlog") and rec.get("deployed"):
            _drain_ok.append(f"{it['slug']}#{it['koma']}")
    _mark_drained(_drain_ok)

    # 3) 【優先2】協調反映(入口型)
    for t in load_coord_targets():
        results["coordinated"].append(coordinated_reflect_one(t, dry, st, c))

    # 4) 【優先3】混在型: 1ループ上限件数・起票済/per_koマ到達は再生成しない(洪水=クレジット浪費の停止)。
    ticketed = _ticketed_set(c)
    mixed_done = 0
    for it in mixed_items:
        key = f"{it['slug']}#{it['koma']}"
        if _per_koma_capped(it["slug"], it["koma"], st, c) or key in ticketed:
            results["mixed"].append({"slug": it["slug"], "koma": it["koma"],
                                     "skip": "起票済/per_koマ到達→再生成せず"})
            continue
        if mixed_done >= c["mixed_max_per_loop"]:
            results["mixed"].append({"slug": it["slug"], "koma": it["koma"],
                                     "skip": f"1ループ上限{c['mixed_max_per_loop']}件到達→次ループへ"})
            continue
        results["mixed"].append(
            mixed_notify_one(it["company"], it["slug"], it["tslug"], it["koma"], it["detail"], it["instruction"], dry, st, c))
        mixed_done += 1
    results["counts"]["mixed_generated_this_loop"] = mixed_done

    # 【根治】毎回 pending停滞を検知し、反映イベント時はラベル/監査を自動更新(stale表示・サイレント滞留の再発防止)。
    if not dry and c["enabled"]:
        try:
            pmap = _pending_image_map()               # 全社の未反映画像コマ(1パス)
            stall = _pending_stall_map(pmap, persist=True)   # pending数が減っていない日数(最終更新bumpに非依存)
            # pending停滞72h超の社を GASへ投函(朝9時アラートが最終更新bumpに関係なく必ず拾う)
            stuck = sorted([(s, dd) for s, dd in stall.items() if dd >= 3], key=lambda x: -x[1])
            slug2name = {}
            try:
                import phase_c_autoloop as A
                slug2name = {v: k for k, v in A._name_to_slug_map().items()}
            except Exception:
                pass
            payload = "|".join(f"{slug2name.get(s, s)}:{dd}日" for s, dd in stuck[:30])
            PCI.gas({"mode": "setimgstall", "stall": payload})
        except Exception:
            pmap = None; stall = None
        # 反映が起きた社はラベルを即更新
        reflected = {}
        for key, flag in (("safe", "deployed"), ("coordinated", "reflected"), ("human_qa", "reflected")):
            for r in results.get(key, []):
                if isinstance(r, dict) and r.get(flag) and r.get("slug"):
                    reflected[r["slug"]] = r.get("company") or r["slug"]
        if reflected and pmap is not None:
            for slug, company in reflected.items():
                n = len(pmap.get(slug, set()))
                try:
                    PCI.gas({"mode": "setpartial" if n > 0 else "setreflected",
                             "company": company, **({"nimg": str(n)} if n > 0 else {})})
                except Exception:
                    pass
            _rebuild_audit_tab(pmap=pmap, stall=stall)
        results["labels_refreshed"] = sorted(reflected)

    # 画像自動化の状態を朝9時digestへ投函(常時1行: ON/OFF・今回消化・キュー残)。低コスト(property書込)。
    try:
        safe_ok = sum(1 for r in results.get("safe", []) if isinstance(r, dict) and r.get("deployed"))
        mixed_n = sum(1 for r in results.get("mixed", []) if isinstance(r, dict) and r.get("notified"))
        qn = 0
        try:
            import re as _re
            cf = PCI.gas({"mode": "commonfixes"})
            seen = set()
            for x in cf.get("items", []):
                m = _re.match(r"\[要画像再生成\]\s*([^:：]+?)[:：]\s*(.*)", str(x.get("rule", "")), _re.S)
                if not m:
                    continue
                for km in _re.findall(r"(?:koma|コマ)\s*0*(\d+)", m.group(2)):
                    seen.add((m.group(1).strip(), km))
            qn = len(seen)
        except Exception:
            pass
        status = f"{'ON' if c['enabled'] else 'OFF'}|今回:安全auto{safe_ok}/混在候補{mixed_n}|キュー残{qn}コマ"
        PCI.gas({"mode": "setimgstatus", "status": status})
    except Exception:
        pass

    if not dry:
        PCI.save_state(st)
    return results


def selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + name); ok = ok and cond

    print("[selftest] 協調ゲート can_coordinate_reflect (片方だけの反映を構造禁止)")
    chk("台本OK(0)+画像OK → 反映", can_coordinate_reflect(0, True) is True)
    chk("台本OK+画像NG → 反映しない(新台本/旧画像を作らない)", can_coordinate_reflect(0, False) is False)
    chk("台本NG(1)+画像OK → 反映しない(新画像/旧台本を作らない)", can_coordinate_reflect(1, True) is False)
    chk("両方NG → 反映しない", can_coordinate_reflect(1, False) is False)

    print("[selftest] decide_coordinated の分岐(書き込みは reflect_both のみ)")
    chk("lint0&QA → reflect_both", decide_coordinated(0, True) == "reflect_both")
    chk("lintNG → abort_text_not_ready", decide_coordinated(1, True) == "abort_text_not_ready")
    chk("QANG → abort_image_not_ready", decide_coordinated(0, False) == "abort_image_not_ready")

    print("[selftest] 構造保証: fake writer で 片方成立時に D1書き込み0回 を実証")
    writes = {"n": 0}
    def fake_reflect(lint_err, qa_pass):
        # 実コードと同じ構造: ゲートを通らない限り writer に到達しない
        if not can_coordinate_reflect(lint_err, qa_pass):
            return "no_write"
        writes["n"] += 1
        return "wrote"
    chk("lint0+QA → 1回書き込み", fake_reflect(0, True) == "wrote" and writes["n"] == 1)
    before = writes["n"]
    fake_reflect(0, False); fake_reflect(1, True); fake_reflect(1, False)
    chk("片方/両方NG × 3 → 追加書き込み0回", writes["n"] == before)

    print("[selftest] 型別フラグ既定(安全側)")
    os.environ.pop("AUTO_IMAGE_FIX_ENABLED", None)
    c = auto_cfg()
    chk("master 既定OFF(未設定)", c["enabled"] is False)
    chk("safe_types 既定に text_leak 含む", "text_leak" in c["safe_types"])
    chk("mixed 既定 notify(自動反映しない)", c["mixed_mode"] == "notify")
    chk("mixed_max_per_loop 既定3(洪水停止)", c["mixed_max_per_loop"] == 3)

    print("[selftest] FIX1 混在型の洪水停止(1ループ上限・起票済/per_koマ到達skip・連続再生成なし)")
    cc = {"per_koma_max": 2, "mixed_max_per_loop": 3}
    st = {"per_koma": {"a#1": 2, "b#2": 0}}
    chk("per_koマ到達 a#1 → 再生成しない(skip)", _per_koma_capped("a", 1, st, cc) is True)
    chk("未到達 b#2 → 処理対象", _per_koma_capped("b", 2, st, cc) is False)

    def simulate_loop(items, st, cc, ticketed):
        """run_batch の混在選抜と同一ロジック(生成の代わりに起票=次ループskip)。"""
        done, gen = 0, []
        for it in items:
            key = f"{it['slug']}#{it['koma']}"
            if _per_koma_capped(it["slug"], it["koma"], st, cc) or key in ticketed:
                continue
            if done >= cc["mixed_max_per_loop"]:
                continue
            gen.append(key); done += 1
            st["per_koma"][key] = st["per_koma"].get(key, 0) + 1
            ticketed.add(key)      # 起票(addimageqa)→次ループでdedup
        return gen
    items = [{"slug": "m", "koma": k} for k in range(1, 11)]   # 混在10件
    st2 = {"per_koma": {}}; ticketed = set()
    g1 = simulate_loop(items, st2, cc, ticketed)
    g2 = simulate_loop(items, st2, cc, ticketed)
    chk("1ループ上限3件のみ生成(108件洪水を停止)", len(g1) == 3)
    chk("loop2はloop1と別item(起票済dedup=同一項目の連続再生成なし)", set(g1).isdisjoint(g2) and len(g2) == 3)
    st3 = {"per_koma": {}}
    g3 = simulate_loop(items, st3, cc, {"m#1", "m#2"})
    chk("起票済(m#1,m#2)はskipされ生成対象に入らない", "m#1" not in g3 and "m#2" not in g3)

    print("[selftest] 安全型優先: run_batch は safe→協調→混在の順(安全型が先にhour枠を取る)")
    import inspect
    src = inspect.getsource(run_batch)
    i_safe = src.find("優先1】安全型"); i_coord = src.find("優先2】協調"); i_mixed = src.find("優先3】混在")
    chk("コード順が 安全型→協調→混在", 0 < i_safe < i_coord < i_mixed)

    print("\n=== phase_c_auto selftest: " + ("ALL PASS ✅" if ok else "FAIL ❌") + " ===")
    return 0 if ok else 1


def main(argv=None):
    import argparse
    if argv is None and "--selftest" in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser(description="Phase C 自動化オーケストレータ(既定dry)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--live", dest="dry", action="store_false", default=True)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    res = run_batch(dry=args.dry)
    print("\n--- 人QA消化 ---")
    for r in res["human_qa"]:
        print(" ", {k: r.get(k) for k in ("slug", "koma", "reflected", "escalate", "note") if r.get(k) is not None})
    print("--- 協調反映 ---")
    for r in res["coordinated"]:
        print(" ", {k: r.get(k) for k in ("slug", "image_komas", "text_komas", "decision", "lint_err", "reflected", "escalate", "note") if r.get(k) is not None})
    print(f"--- 安全型auto: {len(res.get('safe', []))}件 / 混在型notify: {len(res.get('mixed', []))}件 ---")
    (REPO / "tools" / "_phase_c_auto_last.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
