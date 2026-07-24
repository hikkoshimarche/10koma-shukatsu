/* 共通ナビ: 「来た場所に戻る」を ?from= で明示。document.referrer/history.back に依存しない
   (LINE内ブラウザはリッチメニュータップで履歴なしに開くことがあるため from を正とする)。
   使い方: 戻るボタン → onclick="tkBack('<このページの親の既定戻り先>')"
           発リンク → href に &from=<originKey> (必要なら &fromId=/&fromInd=) を付ける */
(function () {
  function q(k) { try { return new URLSearchParams(location.search).get(k); } catch (e) { return null; } }
  // originKey → 戻り先URL（文脈が要るものは from に添えた fromId/fromInd を使う）
  window.tkBack = function (fallback) {
    var from = q('from');
    switch (from) {
      case 'home':    location.href = '/home.html'; return;
      case 'mypage':  location.href = '/mypage.html'; return;
      case 'gyokai':  location.href = '/gyokai.html'; return;
      case 'howto':   location.href = '/howto.html'; return;
      case 'compare': location.href = '/compare.html'; return;
      case 'shindan': location.href = '/shindan.html?view=result'; return; // 診断結果を復元表示
      case 'list': {  // 企業一覧(industry.html) フィルタ状態も可能な範囲で復元
        var ind = q('fromInd');
        location.href = ind ? ('/industry.html?ind=' + encodeURIComponent(ind)) : '/industry.html';
        return;
      }
      case 'company': { // 企業ページ配下(データシート/ESキット/クイズ/ルーム等)から戻る
        var id = q('fromId');
        location.href = id ? ('/company.html?id=' + encodeURIComponent(id)) : (fallback || '/home.html');
        return;
      }
    }
    // from 無し: そのページの親(呼び出し側指定のフォールバック)へ
    location.href = fallback || '/home.html';
  };
  // 発リンクに付ける from サフィックスを組み立てる（?既存クエリの有無を考慮）
  window.tkFromSuffix = function (originKey, ctx) {
    var s = '&from=' + encodeURIComponent(originKey);
    if (ctx && ctx.id) s += '&fromId=' + encodeURIComponent(ctx.id);
    if (ctx && ctx.ind) s += '&fromInd=' + encodeURIComponent(ctx.ind);
    return s;
  };

  /* === 全ページ共通ミニナビ（迷子の保険）: ホーム/企業研究/業界研究/マイページ ===
     テーマ非依存の自己完結バー。nav.js を読む全ページに自動注入。 */
  var MININAV = [
    { key: 'home',   href: '/home.html',     ic: '🏠', l: 'ホーム' },
    { key: 'company',href: '/industry.html', ic: '🏢', l: '企業研究' },
    { key: 'gyokai', href: '/gyokai.html',   ic: '🌐', l: '業界研究' },
    { key: 'mypage', href: '/mypage.html',   ic: '👤', l: 'マイページ' }
  ];
  function activeKey() {
    // Cloudflare Pages はクリーンURL(.html無し)で配信されるため basename で判定
    var base = (location.pathname.split('/').pop() || '').replace(/\.html?$/, '');
    if (base === '' || base === 'home' || base === 'index') return 'home';
    if (base === 'industry' || base === 'company' || base === 'company-list' || base === 'hub') return 'company';
    if (base === 'gyokai') return 'gyokai';
    if (base === 'mypage' || base === 'bookmarks') return 'mypage';
    return '';
  }
  function isIndexPage() {
    var base = (location.pathname.split('/').pop() || '').replace(/\.html?$/, '');
    return base === 'index';
  }
  function injectMiniNav() {
    if (document.getElementById('tk-mininav')) return;
    if (isIndexPage()) return; // リダイレクトページには出さない
    var act = activeKey();
    var css = '#tk-mininav{position:fixed;left:0;right:0;bottom:0;z-index:900;display:flex;'
      + 'background:rgba(10,22,40,0.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);'
      + 'border-top:1px solid rgba(255,255,255,0.12);padding-bottom:env(safe-area-inset-bottom,0px);'
      + 'box-shadow:0 -3px 14px rgba(0,0,0,0.22);font-family:-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}'
      + '#tk-mininav a{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;'
      + 'padding:7px 2px 6px;text-decoration:none;color:rgba(255,255,255,0.62);font-size:10px;font-weight:700;'
      + '-webkit-tap-highlight-color:transparent}'
      + '#tk-mininav a .mi{font-size:19px;line-height:1;filter:grayscale(0.35) opacity(0.85)}'
      + '#tk-mininav a.on{color:#e7b84b}#tk-mininav a.on .mi{filter:none}'
      + '#tk-mininav a:active{background:rgba(255,255,255,0.06)}'
      + 'body{padding-bottom:62px!important}';
    var st = document.createElement('style'); st.id = 'tk-mininav-css'; st.textContent = css;
    document.head.appendChild(st);
    var nav = document.createElement('nav'); nav.id = 'tk-mininav'; nav.setAttribute('aria-label', '主要ナビ');
    nav.innerHTML = MININAV.map(function (m) {
      return '<a href="' + m.href + '"' + (m.key === act ? ' class="on"' : '')
        + '><span class="mi">' + m.ic + '</span><span>' + m.l + '</span></a>';
    }).join('');
    document.body.appendChild(nav);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', injectMiniNav);
  else injectMiniNav();
})();
