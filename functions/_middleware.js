// Cloudflare Pages Functions middleware
// 目的: マーケLP用ドメイン talkcareer.jp では、URLバーを talkcareer.jp のまま（/lp/ を露出させず）LP内容を「内部リライト」で表示する。
// 安全設計: talkcareer.jp / www.talkcareer.jp 以外のホスト（= LIFFアプリ本体 pages.dev 等）は一切変更せず next() で素通し。
//           → アプリのルーティング／LIFFには影響ゼロ。リライト対象もルート + 既知LPページのみに限定。
// 注意: このリライトを有効化するには、ゾーン側の「/ → /lp/ 301リダイレクトルール」を削除すること
//       （Redirect Rule はエッジで Pages Functions より先に発火し、URLが /lp/ に変わってしまうため）。
const LP_HOSTS = new Set(['talkcareer.jp', 'www.talkcareer.jp']);
const LP_PAGES = new Set(['features', 'about', 'companies', 'contact', 'terms', 'privacy']);

export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);

  if (LP_HOSTS.has(url.hostname)) {
    const p = (url.pathname.replace(/\/+$/, '') || '/');
    // ルート → LPトップを内部配信（URLは talkcareer.jp のまま）
    if (p === '/' || p === '/lp') {
      return next(new Request(new URL('/lp/index.html', url), request));
    }
    // 拡張子なしの既知LPページ（/features 等）→ /lp/features.html を内部配信
    const seg = p.slice(1);
    if (LP_PAGES.has(seg)) {
      return next(new Request(new URL('/lp/' + seg + '.html', url), request));
    }
    // それ以外（/lp/*, /images/*, アプリ資産など）は素通し
  }
  return next();
}
