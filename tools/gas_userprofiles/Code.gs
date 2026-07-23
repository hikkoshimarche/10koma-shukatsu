/**
 * トーキャリ_ユーザープロフィール同期（GAS Web App・オスカー所有・別スプシ）。
 * D1 user_profiles を tools/sync_user_profiles.py から受け取り、全件洗い替えで書き込む。
 * 進捗管理表(インターン共有)とは別スプシ・相互リンクなし。
 * Script Properties に SYNC_TOKEN と SPREADSHEET_ID を設定して使う（下記 申し送り 参照）。
 */
function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var props = PropertiesService.getScriptProperties();
    var tok = props.getProperty('SYNC_TOKEN');
    if (!tok || body.token !== tok) return json_({ ok: false, error: 'unauthorized' });
    var ss = SpreadsheetApp.openById(props.getProperty('SPREADSHEET_ID'));
    var n = (body.detail ? body.detail.length - 1 : 0);
    writeDetail_(ss, body.detail || []);
    writeSummary_(ss, body.summary || {});
    appendLog_(ss, n, '');
    return json_({ ok: true, rows: n });
  } catch (err) {
    try { appendLog_(SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID')), -1, String(err)); } catch (e2) {}
    return json_({ ok: false, error: String(err) });
  }
}
function doGet() { return json_({ ok: true, note: 'user profile sync webapp. POST only.' }); }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function sheet_(ss, name) { var s = ss.getSheetByName(name); if (!s) s = ss.insertSheet(name); return s; }

function writeDetail_(ss, detail) {
  var s = sheet_(ss, '明細');
  s.clearContents();
  if (detail.length) s.getRange(1, 1, detail.length, detail[0].length).setValues(detail);
  s.setFrozenRows(1);
}
function writeSummary_(ss, sm) {
  var s = sheet_(ss, 'サマリ');
  s.clearContents();
  var now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');
  var out = [];
  out.push(['トーキャリ ユーザープロフィール サマリ', '', '最終更新', now]);
  out.push(['登録総数', sm.total || 0]); out.push(['']);
  out.push(['■ 所属種別 別 件数']); (sm.by_type || []).forEach(function (r) { out.push([r[0], r[1]]); }); out.push(['']);
  out.push(['■ 大学 別 件数（多い順）']); (sm.by_university || []).forEach(function (r) { out.push([r[0], r[1]]); }); out.push(['']);
  out.push(['■ 卒業年度 別 件数']); (sm.by_grad_year || []).forEach(function (r) { out.push([r[0], r[1]]); }); out.push(['']);
  out.push(['■ 日次 登録推移（同意日ベース）']); (sm.by_date || []).forEach(function (r) { out.push([r[0], r[1]]); });
  var w = Math.max.apply(null, out.map(function (r) { return r.length; }));
  out = out.map(function (r) { while (r.length < w) r.push(''); return r; });
  s.getRange(1, 1, out.length, w).setValues(out);
}
function appendLog_(ss, n, err) {
  var s = sheet_(ss, '実行ログ');
  if (s.getLastRow() === 0) s.appendRow(['実行日時(JST)', '同期件数', '結果']);
  var now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');
  s.appendRow([now, n < 0 ? '' : n, err ? ('ERROR: ' + err) : 'OK']);
}
