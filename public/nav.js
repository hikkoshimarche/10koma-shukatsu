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
})();
