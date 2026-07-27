/* =========================================================
   トーキャリ 共通エンドポイント設定（一元化）
   ---------------------------------------------------------
   コード内に散在していた API / LIFF のハードコードURLを1箇所に集約。
   ドメイン移行（例: tokyari.app）や worker 名変更の際は、
   原則このファイル1枚を書き換えれば全ページに反映される。
   ※ 実切替はオスカー確認後。現時点は現行URLをそのまま定義。
   ========================================================= */
window.TOKYARI = {
  // room / chat API（Cloudflare Workers）
  API_BASE: 'https://10koma-shukatsu-api.oscar-dodds.workers.dev',
  // LIFF ID（LINEミニアプリ）
  LIFF_ROOM: '2010075487-d4TJ2xZc', // room.html / chat.html 用
  LIFF_HUB:  '2010075487-89AJxZnA', // hub / 一覧系 用
};

/* 軽量ファネル計測: 既存 /api/log-view(view_logs) を再利用。個人情報は追加保存しない
   (line_user_id は各ページが window.__tkUser にセット済みの匿名/LINE識別子・未取得時は 'anon')。
   使い方: tkEvent('liff_start') / tkEvent('reach','industry') / tkEvent('koma_read', slug) / tkEvent('tap', 'quiz') 等。 */
window.tkEvent = function (type, id) {
  try {
    var url = (window.TOKYARI && window.TOKYARI.API_BASE) + '/api/log-view';
    var payload = JSON.stringify({ line_user_id: (window.__tkUser || 'anon'), content_type: String(type || 'event'), content_id: String(id || '') });
    // text/plain = CORSシンプルリクエスト → プリフライト不要(sendBeaconはプリフライト不可)＝CORSエラーを出さない。
    // 受け側 Hono c.req.json() は Content-Type に関係なく本文をJSONとして解釈するため text/plain でも記録される。
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, new Blob([payload], { type: 'text/plain' }));
    } else {
      fetch(url, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: payload, keepalive: true, mode: 'no-cors' }).catch(function () {});
    }
  } catch (e) { /* 計測失敗はUXに影響させない */ }
};
