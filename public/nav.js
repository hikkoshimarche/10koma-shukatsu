/* 共通ナビ: 「来た場所に戻る」を ?from= で明示。document.referrer/history.back に依存しない
   (LINE内ブラウザはリッチメニュータップで履歴なしに開くことがあるため from を正とする)。
   使い方: 戻るボタン → onclick="tkBack('<このページの親の既定戻り先>')"
           発リンク → href に &from=<originKey> (必要なら &fromId=/&fromInd=) を付ける */
(function () {
  function q(k) { try { return new URLSearchParams(location.search).get(k); } catch (e) { return null; } }
  // fallback URL(.html) → 行き先ラベル
  function labelForUrl(url) {
    var b = String(url || '').split('/').pop().split('?')[0].replace(/\.html?$/, '');
    return ({ home: 'ホーム', industry: '企業一覧', gyokai: '業界研究TOP', company: '企業ページ',
      mypage: 'マイページ', compare: '企業比較', howto: '使い方', shindan: '診断結果',
      quiz: 'クイズ', datasheet: 'データシート', es_guide: '選考対策', es_kit: 'ESキット' })[b] || '戻る';
  }
  // 戻り先を {href, label} で返す（from= を正・無ければ fallback）。tkBack と表示ラベルが必ず一致する。
  window.tkBackDest = function (fallback) {
    var from = q('from');
    switch (from) {
      case 'home':    return { href: '/home.html', label: 'ホーム' };
      case 'mypage':  return { href: '/mypage.html', label: 'マイページ' };
      case 'gyokai': {
        // fromOpen があれば、戻り時にその業界カードを再展開(どの業界を見ていたか失わない)。
        var op = q('fromOpen');
        return { href: op ? ('/gyokai.html?open=' + encodeURIComponent(op)) : '/gyokai.html', label: '業界研究TOP' };
      }
      case 'howto':   return { href: '/howto.html', label: '使い方' };
      case 'compare': return { href: '/compare.html', label: '企業比較' };
      case 'shindan': return { href: '/shindan.html?view=result', label: '診断結果' };
      case 'list': {
        var ind = q('fromInd');
        return { href: ind ? ('/industry.html?ind=' + encodeURIComponent(ind)) : '/industry.html', label: '企業一覧' };
      }
      case 'company': {
        var id = q('fromId');
        return { href: id ? ('/company.html?id=' + encodeURIComponent(id)) : (fallback || '/home.html'), label: '企業ページ' };
      }
    }
    return { href: fallback || '/home.html', label: labelForUrl(fallback || '/home.html') };
  };
  window.tkBack = function (fallback) { location.href = window.tkBackDest(fallback).href; };
  // [data-tkback="<fallbackUrl>"] を「‹ 行き先ラベル」ピルに整える。
  //   data-tkback-keep があれば onclick は各ページの既存ハンドラを尊重（ラベルのみ差し込み）。
  window.tkInitBack = function () {
    var els = document.querySelectorAll('[data-tkback]');
    for (var i = 0; i < els.length; i++) {
      (function (el) {
        var fb = el.getAttribute('data-tkback') || '/home.html';
        var d = window.tkBackDest(fb);
        el.textContent = '‹ ' + d.label;
        el.setAttribute('aria-label', d.label + 'へ戻る');
        if (!el.hasAttribute('data-tkback-keep')) {
          el.onclick = function (e) { if (e && e.preventDefault) e.preventDefault(); location.href = d.href; return false; };
        }
      })(els[i]);
    }
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
      // コンテンツ末尾がナビに隠れないよう、ナビ実高(=約56px)＋iPhoneホームバー(safe-area)分を確保。
      // 一部ページは独自の固定下部バーを持つため、それらは env 分を別途上げられるよう CSS変数も公開。
      + ':root{--tk-navh:62px;--tk-safe:env(safe-area-inset-bottom,0px)}'
      + 'body{padding-bottom:calc(62px + env(safe-area-inset-bottom,0px))!important}';
    var st = document.createElement('style'); st.id = 'tk-mininav-css'; st.textContent = css;
    document.head.appendChild(st);
    var nav = document.createElement('nav'); nav.id = 'tk-mininav'; nav.setAttribute('aria-label', '主要ナビ');
    nav.innerHTML = MININAV.map(function (m) {
      return '<a href="' + m.href + '"' + (m.key === act ? ' class="on"' : '')
        + '><span class="mi">' + m.ic + '</span><span>' + m.l + '</span></a>';
    }).join('');
    document.body.appendChild(nav);
  }
  // 戻るピル: 各ページのテーマ色は保ちつつ、ラベルが収まるようサイズだけ整える。
  function injectBackCss() {
    if (document.getElementById('tk-back-css')) return;
    var css = '[data-tkback]{width:auto!important;height:auto!important;min-width:0!important;'
      + 'border-radius:999px!important;padding:6px 13px 6px 11px!important;font-size:13px!important;'
      + 'line-height:1!important;white-space:nowrap!important;display:inline-flex!important;'
      + 'align-items:center!important;justify-content:center!important;gap:0!important}';
    var st = document.createElement('style'); st.id = 'tk-back-css'; st.textContent = css;
    document.head.appendChild(st);
  }
  /* === 全ページ共通スクロール位置復元（一覧→詳細→戻る で元の位置に戻す） ===
     industry.html の作法(sessionStorage に scrollY を保存→戻り時に復元)を全ページに一般化。
     各ページ実装不要＝追加コストは pagehide 保存＋復帰時の数フレーム待ちのみ(速度非退行)。
     - キーは pathname(.html正規化)+search 単位＝検索/フィルタ違いごとに別位置を保持。
     - 非同期で伸びる一覧に対応: 本文が保存位置まで伸びるまで rAF で待って復元(最大~40フレーム)。
     - アンカー(#…)付き遷移や data-tk-scroll-self(自前で位置管理: industry) は復元をスキップ。 */
  // pathname のみでキー化(search は含めない)。理由: 戻る導線は from= からURLを再構成するため、
  // 離脱時と復帰時で query がドリフトしやすい。search をキーに含めると save/restore が別キーになり復元が外れる。
  // pathname 単位なら同一ページに確実に復元。フィルタ違いで別スクロールを持ちたいページ(industry)は
  // data-tk-scroll-self で本汎用復元を無効化し、自前でstate込み復元する。
  function tkScrollKey() {
    return 'tk_scroll:' + location.pathname.replace(/\.html?$/, '');
  }
  function tkScrollSelfManaged() {
    return !!(document.body && document.body.hasAttribute('data-tk-scroll-self'));
  }
  function tkSaveScroll() {
    if (tkScrollSelfManaged()) return;
    try {
      var y = window.scrollY || window.pageYOffset || 0;
      if (y > 0) sessionStorage.setItem(tkScrollKey(), String(y));
      else sessionStorage.removeItem(tkScrollKey());
    } catch (e) {}
  }
  function tkRestoreScroll() {
    if (tkScrollSelfManaged()) return;
    if (location.hash) return;               // アンカー遷移はブラウザ挙動を尊重
    var raw = null;
    try { raw = sessionStorage.getItem(tkScrollKey()); } catch (e) { return; }
    if (!raw) return;
    var y = parseInt(raw, 10);
    if (!(y > 0)) return;
    // 本文が保存位置まで伸びたら復元。非同期一覧(fetch後に描画)は伸びるまで待つ必要があるため
    // フレーム数ではなく時間予算(最大~4s)で待つ＝遅い回線でも先頭に落ちない。伸び切ったら1回だけ復元。
    var now = (window.performance && performance.now) ? function () { return performance.now(); } : function () { return 0; };
    var start = now(), done = false;
    function contentMax() {
      return Math.max(document.body ? document.body.scrollHeight : 0,
                      document.documentElement.scrollHeight) - window.innerHeight;
    }
    function tryScroll() {
      if (done) return true;
      if (contentMax() >= y - 2) { done = true; window.scrollTo(0, y); return true; }
      if (now() - start > 4000) { done = true; window.scrollTo(0, y); return true; }  // 予算切れ: できる範囲で復元
      return false;
    }
    (function raf() { if (!tryScroll()) requestAnimationFrame(raf); })();
    // rAF が絞られる環境の保険として、本文増加も監視(伸びた瞬間に復元→即 disconnect)。
    if (window.MutationObserver && document.body) {
      var mo = new MutationObserver(function () { if (tryScroll()) mo.disconnect(); });
      mo.observe(document.body, { childList: true, subtree: true });
      setTimeout(function () { try { mo.disconnect(); } catch (e) {} }, 4200);
    }
  }
  // 保存の取りこぼし防止: 離脱(pagehide)と、LINE/iOSで pagehide が飛ばない場合に備え可視性喪失でも保存。
  window.addEventListener('pagehide', tkSaveScroll);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') tkSaveScroll();
  });
  window.tkSaveScroll = tkSaveScroll;        // ページ側で任意に呼べるよう公開(遷移直前保存など)

  function tkInit() { injectBackCss(); injectMiniNav(); window.tkInitBack(); tkRestoreScroll(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tkInit);
  else tkInit();
})();
