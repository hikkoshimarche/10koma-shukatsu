/* Cloudflare Pages Function — ルート「/」だけを対象（_middleware は使わない＝全ルート影響の事故を回避）。
 * 目的: LINE外の通常ブラウザで talkcareer.jp/ を開いたら公式LP(/lp/)へ302。LINE内WebView/liff起動はLIFFをそのまま返す。
 * 安全側の原則: 判定がつかない(UA空 等)は必ず LIFF を返す＝既存導線を絶対に壊さない。
 * 注意: このファイルは /index (=ルート) のみにマッチ。/lp/* や /company 等・静的ファイルには一切効かない。 */
export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);
  const ua = request.headers.get('user-agent') || '';

  const isLine = /\bLine\//i.test(ua) || ua.indexOf('LIFF') >= 0;   // LINE内WebView / LIFFブラウザ
  const hasLiff = /liff/i.test(url.search);                          // liff.state / liffRedirectUri 等
  // 既存のアプリ用ディープリンク(?company= 等)はLIFF側へ(導線保護)
  const appQuery = ['company', 'industry', 'id', 'u', 'from'].some((k) => url.searchParams.has(k));

  if (isLine || hasLiff || appQuery) return next();                 // → LIFF(index.html)を配信
  if (ua) return Response.redirect('https://talkcareer.jp/lp/', 302); // 明確に非LINEブラウザ → LP へ302
  return next();                                                     // UA空=判定不能 → 安全側(LIFF)
}
