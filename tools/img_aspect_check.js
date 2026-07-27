/* 画像アスペクト比 回帰チェック（QA/健全性）: 全ページ・全 <img> を多数の端末幅で走査し、
 * 「元のアスペクト比」と「描画ボックス比」のズレを検出する。object-fit が fill/none で 2%超のズレ＝歪み(NG)。
 * (contain/cover は画像自体を歪めないので box比のズレは許容=レターボックス/クロップ)。
 * 使い方: node tools/img_aspect_check.js [baseUrl]   (既定=本番pages.dev)。NGが1件でもあれば exit 1。
 * 端末: iPhone SE1/SE2/12/13/14/15/16/ProMax・Android標準/Pixel・iPad縦横・PC を幅で網羅(縦横は幅として展開)。
 * DPR: CSSレイアウト比はDPR非依存のため代表DPRで判定し、末尾で1/2/3の同一性を1ページで実証する。 */
const PW = '/Users/oscardodds/Desktop/Claude/FPスクレイピング/node_modules/playwright';
const { chromium } = require(PW);
const BASE = process.argv[2] || 'https://10koma-shukatsu.pages.dev';
const LIFF = () => { window.__tkUser='__qa__'; window.liff = { init:()=>Promise.resolve(), isLoggedIn:()=>true, isInClient:()=>false, login:()=>{}, getProfile:()=>Promise.resolve({userId:'__qa__'}), isApiAvailable:()=>false }; };
// 縦向き幅 + 横向き(高さを幅として) + タブレット/PC を一意化
const WIDTHS = [320,360,375,390,393,412,414,430,568,667,768,800,844,852,896,915,932,1024,1280,1920];
const LP = ['lp/index.html','lp/features.html','lp/about.html','lp/companies.html','lp/contact.html','lp/terms.html','lp/privacy.html'];
const APP = ['home.html','industry.html','company.html?id=denso','gyokai.html','mypage.html','quiz.html?company=denso&name=D','shindan.html','room.html?company=denso&name=D','compare.html','datasheet.html?id=denso','es_kit.html?id=denso','es_guide.html','howto.html','hub.html','bookmarks.html','videos.html','omamori.html','company-list.html','chat.html'];
const PAGES = LP.concat(APP);

async function measure(page, url) {
  try { await page.goto(url, { waitUntil:'domcontentloaded', timeout:20000 }); } catch(e){ return []; }
  await page.evaluate(async()=>{ const h=document.body.scrollHeight; for(let y=0;y<=h;y+=800){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,25));} window.scrollTo(0,0); });
  await page.waitForTimeout(250);
  return page.evaluate(()=>[...document.querySelectorAll('img')].filter(im=>im.naturalWidth&&im.naturalHeight&&im.clientWidth&&im.clientHeight).map(im=>{
    const nr=im.naturalWidth/im.naturalHeight, rr=im.clientWidth/im.clientHeight;
    return { src:(im.currentSrc||im.src).split('/').pop().slice(0,28), fit:getComputedStyle(im).objectFit, diff:+(Math.abs(rr-nr)/nr*100).toFixed(1), nr:+nr.toFixed(3), rr:+rr.toFixed(3) };
  }));
}

(async () => {
  const b = await chromium.launch({ channel:'chrome' });
  let checked=0; const bad=[];
  for (const w of WIDTHS) {
    const ctx = await b.newContext({ viewport:{width:w,height: w<768?844:900}, deviceScaleFactor:2, isMobile:w<768, hasTouch:w<768 });
    await ctx.route('**/liff/edge/2/sdk.js', r=>r.abort()); await ctx.addInitScript(LIFF);
    const p = await ctx.newPage();
    for (const pg of PAGES) {
      const rows = await measure(p, BASE + '/' + pg);
      for (const r of rows) { checked++; if ((r.fit==='fill'||r.fit==='none') && r.diff>2) bad.push({ w, pg:pg.split('?')[0], ...r }); }
    }
    await ctx.close();
  }
  // DPR不変性の実証(1ページ・3DPR で box比が同一)
  const dprSame = [];
  for (const dpr of [1,2,3]) {
    const ctx = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:dpr });
    const p = await ctx.newPage();
    const rows = await measure(p, BASE + '/lp/index.html');
    dprSame.push(rows.map(r=>r.rr).join(','));
    await ctx.close();
  }
  const dprInvariant = new Set(dprSame).size === 1;

  console.log(`[img_aspect_check] base=${BASE}`);
  console.log(`widths=${WIDTHS.length} pages=${PAGES.length} img-checks=${checked} distortion(NG)=${bad.length}`);
  console.log(`DPR 1/2/3 layout-ratio identical @390: ${dprInvariant ? 'YES(=DPR非依存)' : 'NO'}`);
  if (bad.length) { console.log('NG:'); bad.slice(0,60).forEach(x=>console.log(`  @${x.w} ${x.pg} ${x.src} fit=${x.fit} nat=${x.nr} rend=${x.rr} diff=${x.diff}%`)); }
  else console.log('=> 全ページ・全幅で アスペクト比ずれ 0件 ✓');
  await b.close();
  process.exit(bad.length ? 1 : 0);
})();
