/* Cloudflare Pages Function — ルート「/」だけを対象（_middleware は使わない＝全ルート影響の事故を回避）。
 * 目的:
 *  - LINE外の通常ブラウザ: talkcareer.jp/ を「その場で LP 配信」(302しない=URLは / のまま /lp/ を出さない)。
 *  - LINE内WebView / liff起動 / 既存アプリ ?company= 等: LIFF(index.html)をそのまま返す(導線保護)。
 *  - 判定不能(UA空)や ASSETS不可: 安全側で LIFF を返す(壊さない)。
 * 注意: このファイルは / のみにマッチ。/features 等の綺麗URLは _redirects(200リライト)で /lp/*.html を配信。 */
export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  const ua = request.headers.get('user-agent') || '';

  const isLine = /\bLine\//i.test(ua) || ua.indexOf('LIFF') >= 0;   // LINE内WebView / LIFFブラウザ
  const hasLiff = /liff/i.test(url.search);                          // liff.state / liffRedirectUri 等
  const appQuery = ['company', 'industry', 'id', 'u', 'from'].some((k) => url.searchParams.has(k));

  if (isLine || hasLiff || appQuery) return next();                 // → LIFF(index.html)

  // 非LINEブラウザ → LP を「その場配信」。/lp/(クリーン形=200)を取得して返す。302もURL書換もしない。
  try {
    if (env && env.ASSETS) {
      const lp = await env.ASSETS.fetch(new Request(new URL('/lp/', url), request));
      if (lp && lp.status === 200) return new Response(lp.body, lp);
    }
  } catch (e) { /* ASSETS不可 → 下の安全側へ */ }
  return next();                                                     // 取得不可=安全側(LIFF・壊さない)
}
