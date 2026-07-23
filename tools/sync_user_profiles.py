#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D1 user_profiles → Googleスプレッドシート「トーキャリ_ユーザープロフィール管理」日次同期。
全件洗い替え方式。既存 reconcile_register.py と同じ Python→GAS webapp パターン。
- D1 読み取り: wrangler d1 execute(このMacのwrangler認証を利用・PIIをWorkerに露出しない)
- 書き込み: GAS webapp(オスカーのみ所有・別スプシ)へ POST {token, detail, summary}
env(tools/.env.phase_c): USER_SYNC_WEBAPP_URL, USER_SYNC_TOKEN
実行: python tools/sync_user_profiles.py            # 本番同期
      python tools/sync_user_profiles.py --dry-run  # POSTせず計算結果をJSON出力(検証用)
"""
import os, sys, json, subprocess
from collections import Counter

DB = "10koma-shukatsu-db"
API_DIR = os.path.join(os.path.dirname(__file__), "..", "api")
DETAIL_HEADER = ["user_id", "所属種別", "大学", "学部", "卒業年度", "同意日時", "登録日時"]
TYPE_LABEL = {"student_univ": "大学生・大学院生", "student_pre": "高校生・中学生", "worker": "社会人", "other": "その他"}

def d1_rows():
    cmd = ["npx", "wrangler", "d1", "execute", DB, "--remote", "--json", "--command",
           "SELECT user_id,user_type,university,faculty,grad_year,consented_at,consent_version FROM user_profiles ORDER BY consented_at"]
    out = subprocess.check_output(cmd, cwd=os.path.abspath(API_DIR))
    data = json.loads(out.decode())
    return data[0]["results"]

def build_payload(rows):
    # 明細(登録日時=同意日時。登録=同意の瞬間)
    detail = [DETAIL_HEADER]
    for r in rows:
        detail.append([
            r.get("user_id", ""), TYPE_LABEL.get(r.get("user_type"), r.get("user_type", "")),
            r.get("university") or "", r.get("faculty") or "", r.get("grad_year") or "",
            r.get("consented_at") or "", r.get("consented_at") or "",
        ])
    # サマリ
    by_type = Counter(TYPE_LABEL.get(r.get("user_type"), r.get("user_type", "")) for r in rows)
    by_uni = Counter(r.get("university") for r in rows if r.get("university"))
    by_grad = Counter(r.get("grad_year") for r in rows if r.get("grad_year"))
    by_date = Counter((r.get("consented_at") or "")[:10] for r in rows if r.get("consented_at"))
    summary = {
        "total": len(rows),
        "by_type": [[k, v] for k, v in by_type.most_common()],
        "by_university": [[k, v] for k, v in by_uni.most_common()],
        "by_grad_year": sorted([[k, v] for k, v in by_grad.items()]),
        "by_date": sorted([[k, v] for k, v in by_date.items()]),
    }
    return {"detail": detail, "summary": summary}

def main():
    dry = "--dry-run" in sys.argv
    rows = d1_rows()
    payload = build_payload(rows)
    if dry:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0
    url = os.environ["USER_SYNC_WEBAPP_URL"].strip()
    token = os.environ["USER_SYNC_TOKEN"].strip()
    import urllib.request
    body = json.dumps({"token": token, **payload}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=60).read().decode()
    print("sync result:", resp)
    return 0

if __name__ == "__main__":
    sys.exit(main())
