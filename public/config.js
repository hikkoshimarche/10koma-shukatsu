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
