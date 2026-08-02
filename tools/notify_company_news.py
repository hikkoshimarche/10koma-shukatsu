#!/usr/bin/env python3
"""お気に入り企業(bookmarks)の『新着ニュース』を週次でユーザーごとに1通にまとめてLINE通知。

設計方針(過去の教訓を織り込み):
  ・「新着」= company_news.fetched_at が直近ウィンドウ内(既定8日=crawlの週次直後に走る前提) かつ
    news_notifications(通知台帳)に未記録のもの。台帳は per(user,url) で冪等 → 重複送信ゼロ・
    部分失敗ユーザーの取りこぼしゼロ・後からブックマークした人への過去分の垂れ流しゼロ。
  ・新着0件のユーザーには送らない(無意味な通知=ブロック要因)。
  ・1ユーザー1通(企業ごとに何通も出さない)。企業名・見出し・やさしい要約・企業ページリンクを含む。
  ・送信は既存作法どおり GAS webapp 経由(Mac直叩きは 429 monthly-limit の経路地雷)。
    個別ユーザー宛は新設 mode=pushuser(認証付き・単一userId・broadcast/multicast禁止)。
  ・「空応答を成功にしない」: pushuser は実LINE APIの code/request_id を返す。code==200 を実測できた
    ユーザーのみ台帳に記録する(送れていないのに送信済み扱いにしない)。
  ・広告色を出さない(「登録した企業の“動き”の共有」というトーン)。

使い方:
  python tools/notify_company_news.py                 # dry-run: 誰に何が届くかを表示のみ(送信/台帳書き込みなし)
  python tools/notify_company_news.py --window-days 30 # dry-run のウィンドウを広げてプレビュー(古い新着も含める)
  python tools/notify_company_news.py --test-oscar     # 先頭ユーザー分の実文面をオスカー個人(pushoscar)へ試送
  python tools/notify_company_news.py --test-oscar --user U... --window-days 30  # 指定ユーザー分をオスカーへ試送
  python tools/notify_company_news.py --send --i-am-approved  # 本番: 全対象ユーザーへ pushuser 送信+台帳記録

  --send は誤送信防止のため --i-am-approved を必須にしている(オスカーの承認後にのみ付ける)。
"""
import subprocess, os, sys, json, argparse, urllib.parse

TENK = os.path.expanduser("~/projects/10koma-shukatsu")
CFG = os.path.join(TENK, "api/wrangler.toml")
DB = "10koma-shukatsu-db"
LOG = os.path.join(TENK, "logs/company_news_notify.log")
PAGES = "https://10koma-shukatsu.pages.dev"           # 企業ページの本番ホスト(nav.js /company.html?id= と一致)
# 初回ゲート用の実行時状態(コミットしない・.gitignore済)。存在=自動送信アーム済(以降ゲート無し)。
ARMED = os.path.join(TENK, "tools/.company_news_notify_armed")
PREVIEW = os.path.join(TENK, "logs/company_news_firstbatch_preview.txt")

MAX_ITEMS_PER_COMPANY = 3    # 1社あたり見出しは最大3件(残りは「ほかN件」)
SUMMARY_CHARS = 70           # やさしい要約の表示上限
CHUNK = 4900                 # LINE 1メッセージ上限5000 → 安全側で分割(基本は1通に収める)
# gen_news_summary.py が「対象外」記事に入れるセンチネル(UIで要約箱ごと非表示にする値)。通知でも要約は出さない。
SUMMARY_EXCLUDE = "__EXCLUDED__"


def logline(m):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(m + "\n")
    print(m, flush=True)


def d1_json(sql):
    p = subprocess.run(["npx", "wrangler", "d1", "execute", DB, "--remote", "--config", CFG,
                        "--json", "--command", sql], cwd=TENK, capture_output=True, text=True)
    t = p.stdout or ""
    i = t.find("[")
    if i < 0:
        logline(f"[d1エラー] {p.stderr[:300] or t[:300]}")
        return []
    rows = []
    for blk in json.loads(t[i:]):
        if isinstance(blk, dict):
            rows.extend(blk.get("results", []))
    return rows


def d1_exec_file(sql_text):
    fn = "/tmp/_cnews_notify.sql"
    open(fn, "w", encoding="utf-8").write(sql_text)
    p = subprocess.run(["npx", "wrangler", "d1", "execute", DB, "--remote", "--config", CFG, "--file", fn],
                       cwd=TENK, capture_output=True, text=True)
    ok = "rows_written" in (p.stdout or "") or p.returncode == 0
    if not ok:
        logline(f"[d1書込エラー] {p.stderr[:300]}")
    return ok


def sqlq(s):
    return "'" + str(s).replace("'", "''") + "'"


def gas_call(params):
    """GAS webapp を叩き JSON を返す。requests 不在時は curl フォールバック(依存を増やさない)。"""
    url = (os.environ.get("SHEET_WEBAPP_URL") or "").strip()
    token = (os.environ.get("SHEET_API_TOKEN") or "").strip()
    if not url:
        return {"error": "SHEET_WEBAPP_URL未設定"}
    params = {**params, "token": token}
    # POST(form)で送る: text は最大4900字になり得るため GET だと URL長で 400(GSE Bad Request)になる。
    # quiz_fanout.py の pushlinefull と同じ POST data= パターンに合わせる。
    try:
        import requests
        r = requests.post(url, data=params, timeout=60)
        try:
            return r.json()
        except Exception:
            return {"error": "non-json", "text": r.text[:200]}
    except ImportError:
        args = ["curl", "-sL", "-X", "POST", url]
        for k, v in params.items():
            args += ["--data-urlencode", f"{k}={v}"]
        p = subprocess.run(args, capture_output=True, text=True, timeout=90)
        try:
            return json.loads(p.stdout)
        except Exception:
            return {"error": "non-json", "text": (p.stdout or "")[:200]}
    except Exception as e:
        return {"error": str(e)}


# ── 新着ニュース取得(未通知 かつ 直近ウィンドウ内) ─────────────────────────────
def fetch_new_by_user(window_days, only_user=None, ignore_ledger=False):
    ledger_clause = "" if ignore_ledger else (
        " AND NOT EXISTS (SELECT 1 FROM news_notifications x "
        "WHERE x.line_user_id=b.line_user_id AND x.url=n.url)")
    user_clause = f" AND b.line_user_id={sqlq(only_user)}" if only_user else ""
    sql = (
        "SELECT b.line_user_id AS uid, n.company_id AS cid, c.name AS company, "
        "n.title AS title, COALESCE(n.summary_easy,'') AS summary, n.url AS url, "
        "COALESCE(n.published_at, substr(n.fetched_at,1,10)) AS pub "
        "FROM bookmarks b "
        "JOIN company_news n ON n.company_id = b.company_id "
        "JOIN companies c ON c.id = b.company_id "
        f"WHERE n.fetched_at >= datetime('now','-{int(window_days)} days') "
        # 見出しが空/URLそのもの(crawl抽出不良)の項目は通知に出さない(壊れた見出しの捏造回避)
        "AND n.title IS NOT NULL AND TRIM(n.title) <> '' AND n.title NOT LIKE 'http%' "
        f"{ledger_clause}{user_clause} "
        "ORDER BY b.line_user_id, c.name, n.published_at DESC, n.fetched_at DESC")
    rows = d1_json(sql)
    by_user = {}
    for r in rows:
        by_user.setdefault(r["uid"], []).append(r)
    return by_user


def build_message(items):
    """1ユーザー分の items(company/title/summary/url/cid) → 1通のテキスト。company_id 単位でまとめる。"""
    # 企業ごとにグルーピング(取得順=会社名昇順・新しい順を維持)
    companies = []  # [(cid, company_name, [items...])]
    idx = {}
    for it in items:
        if it["cid"] not in idx:
            idx[it["cid"]] = len(companies)
            companies.append((it["cid"], it["company"], []))
        companies[idx[it["cid"]]][2].append(it)

    total = sum(len(c[2]) for c in companies)
    head = ("📰 お気に入り企業の新着ニュース\n"
            f"登録した{len(companies)}社で、新しい動きが{total}件ありました。\n"
            "――――――――――")
    blocks = [head]
    for cid, name, its in companies:
        lines = [f"🏢 {name}"]
        for it in its[:MAX_ITEMS_PER_COMPANY]:
            title = it["title"].strip()
            lines.append(f"・{title}")
            s = (it["summary"] or "").strip()
            if s and s != SUMMARY_EXCLUDE:
                if len(s) > SUMMARY_CHARS:
                    s = s[:SUMMARY_CHARS] + "…"
                lines.append(f"　{s}")
        extra = len(its) - MAX_ITEMS_PER_COMPANY
        if extra > 0:
            lines.append(f"　ほか{extra}件")
        lines.append(f"▶ {name}のページ: {PAGES}/company.html?id={cid}")
        blocks.append("\n".join(lines))
    blocks.append("――――――――――\n通知は各企業ページの「お気に入り」に連動しています。")
    return "\n\n".join(blocks)


def chunks(text):
    return [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)] or [text]


def send_to_user(uid, text):
    """pushuser(mode)で uid 個人へ送信。実APIの code==200 を全チャンクで確認できた時のみ True。"""
    ok_all = True
    for part in chunks(text):
        res = gas_call({"mode": "pushuser", "id": uid, "text": part})
        code = res.get("code")
        if code != 200:
            logline(f"  ✗ 送信失敗 uid=...{uid[-6:]} code={code} resp={json.dumps(res, ensure_ascii=False)[:200]}")
            ok_all = False
            break
        logline(f"  ✓ 送信 uid=...{uid[-6:]} code=200 req_id={res.get('request_id','')} chars={res.get('chars')}")
    return ok_all


def record_notified(uid, items):
    stmts = ["INSERT OR IGNORE INTO news_notifications(line_user_id,company_id,url) VALUES "
             + ",".join(f"({sqlq(uid)},{sqlq(it['cid'])},{sqlq(it['url'])})" for it in items) + ";"]
    return d1_exec_file("\n".join(stmts))


def send_all(by_user):
    """全対象ユーザーへ pushuser 送信し、成功(code==200)ユーザーのみ台帳記録。送信人数を返す。"""
    sent_users = 0
    for uid, items in by_user.items():
        text = build_message(items)
        if send_to_user(uid, text):
            if record_notified(uid, items):
                sent_users += 1
            else:
                logline(f"  ⚠️ 送信は成功したが台帳記録に失敗 uid=...{uid[-6:]}(次回二重送信の恐れ→要確認)")
    return sent_users


def present_first_batch(by_user):
    """初回ゲート: 実ユーザーへは送らず、生成した実文面をファイル保存＋オスカー個人(pushoscar)へ提示。"""
    parts = [f"🔔【初回ゲート】お気に入り企業ニュースの週次LINE通知・初回分プレビュー",
             f"対象 {len(by_user)}名。この内容で各ユーザーへ送ってよければ承認コマンドを実行してください:",
             f"  python tools/notify_company_news.py --approve-first-batch",
             "(承認するとこの分を送信し、以降は毎週自動送信になります。送らない場合は何もしないでください)",
             "════════════════════"]
    for uid, items in by_user.items():
        parts.append(f"▼ 送信先ユーザー ...{uid[-6:]}({len(items)}件)")
        parts.append(build_message(items))
        parts.append("════════════════════")
    full = "\n\n".join(parts)
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    open(PREVIEW, "w", encoding="utf-8").write(full)
    logline(f"[notify] 初回ゲート: 未アーム → 送信保留。プレビュー全文を {PREVIEW} に保存。オスカーへ提示します。")
    ok = True
    for chunk in chunks(full):
        res = gas_call({"mode": "pushoscar", "text": chunk})
        sent = bool(res.get("ok") or res.get("sent"))
        logline(f"  pushoscar(初回ゲート提示) resp={json.dumps(res, ensure_ascii=False)[:160]} sent={sent}")
        ok = ok and sent
    logline("[notify] 初回ゲート提示 完了。承認待ち(実ユーザー未送信・台帳未記録)。"
            if ok else "[notify] 初回ゲート提示の送信に失敗(応答確認)。")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-days", type=int, default=8, help="新着とみなす fetched_at のウィンドウ(既定8日)")
    ap.add_argument("--test-oscar", action="store_true", help="実文面をオスカー個人(pushoscar)へ試送(台帳は書かない)")
    ap.add_argument("--user", default=None, help="対象ユーザーを1人に限定(test-oscar/dry-runのプレビュー用)")
    ap.add_argument("--send", action="store_true", help="本番: 全対象ユーザーへ pushuser 送信+台帳記録")
    ap.add_argument("--i-am-approved", action="store_true", help="--send の安全ピン(オスカー承認後に付与)")
    ap.add_argument("--approve-first-batch", action="store_true",
                    help="初回ゲート解除: 現在の新着分を実ユーザーへ送信し、以降を自動送信にアームする(オスカーが提示確認後に実行)")
    args = ap.parse_args()

    # ---- 初回ゲート解除(承認アクション): この分を送信し、以降を自動送信にアーム ----
    if args.approve_first_batch:
        by_user = fetch_new_by_user(args.window_days)   # 本番と同条件(台帳尊重)
        if not by_user:
            open(ARMED, "w", encoding="utf-8").write("armed (approved with 0 new)\n")
            logline("[approve] 現在 新着0件 → 送信なし。以降の自動送信をアームしました。")
            return 0
        logline(f"[approve] 初回分を {len(by_user)}名へ送信開始。")
        sent = send_all(by_user)
        open(ARMED, "w", encoding="utf-8").write("armed\n")
        logline(f"[approve] 初回送信 {sent}/{len(by_user)}名 完了。以降は毎週 launchd で自動送信(アーム済)。")
        return 0

    # --test-oscar は台帳を無視して(=既通知でも)実文面を作れるようにし、プレビューを容易にする。
    ignore_ledger = args.test_oscar
    by_user = fetch_new_by_user(args.window_days, only_user=args.user, ignore_ledger=ignore_ledger)

    if not by_user:
        logline(f"[notify] 新着0件(window={args.window_days}d, user={args.user or 'ALL'}) → 送信なし。")
        return 0

    logline(f"[notify] 対象ユーザー {len(by_user)}名 / window={args.window_days}d / mode="
            + ("SEND" if args.send else ("TEST-OSCAR" if args.test_oscar else "DRY-RUN")))

    # ---- TEST-OSCAR: 先頭(または指定)ユーザーの実文面をオスカーへ ----
    if args.test_oscar:
        uid = args.user or next(iter(by_user))
        text = build_message(by_user[uid])
        logline(f"--- オスカー試送プレビュー (元ユーザー ...{uid[-6:]}, {len(text)}字) ---\n{text}\n---")
        ok = True
        for part in chunks(text):
            res = gas_call({"mode": "pushoscar", "text": part})
            sent = bool(res.get("ok") or res.get("sent"))
            logline(f"  pushoscar resp={json.dumps(res, ensure_ascii=False)[:200]} sent={sent}")
            ok = ok and sent
        logline("[notify] 試送完了(台帳は未記録)。" if ok else "[notify] 試送に失敗(応答を確認)。")
        return 0 if ok else 1

    # ---- DRY-RUN(既定) ----
    if not args.send:
        for uid, items in by_user.items():
            text = build_message(items)
            logline(f"\n===== to ...{uid[-6:]} ({len(items)}件, {len(text)}字) =====\n{text}")
        logline(f"\n[notify] DRY-RUN。実送信は --send --i-am-approved。対象 {len(by_user)}名。")
        return 0

    # ---- 本番送信(--send) ----
    if not args.i_am_approved:
        logline("❌ --send にはオスカーの承認を示す --i-am-approved が必須です(誤送信は取り消せません)。中止。")
        return 2
    # 初回ゲート: 未アームなら実ユーザーへは送らず、実文面をオスカーへ提示して停止(承認は --approve-first-batch)。
    if not os.path.exists(ARMED):
        present_first_batch(by_user)
        return 0
    sent_users = send_all(by_user)
    logline(f"[notify] 本番送信完了(自動): {sent_users}/{len(by_user)}名に送信・台帳記録。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
