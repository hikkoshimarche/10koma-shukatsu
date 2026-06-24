/*****************************************************************
 * トーキャリ 進捗管理シート 自動化 (Google Apps Script) v7
 *  ※45列レイアウト（10ラウンド・4列/回：担当/FB/状態/反映）対応
 *  ※doPost で groupId を自動保存（ログを読まなくてOK）
 *  ※doGet ?mode=attention で「要対応」JSONを返す（Phase C: GitHub Action用）
 * --------------------------------------------------------------
 *  列: A業界 B会社名 C状態 D公開URL(オスカー)
 *      ラウンドn: 担当=5+(n-1)*4 / FB=6+(n-1)*4 / 状態=7+(n-1)*4 / 反映=8+(n-1)*4
 *      最終更新=45
 *
 *  「状態」(インターンが選ぶ) → 自動連動:
 *      記入中 … 書いている途中（Claudeは動かない）
 *      提出   … ステータス自動「FB対応中」
 *      これでOK … ステータス自動「完了」
 *  「反映」(直した人＝オスカー/将来Claude Code自動):
 *      反映済 … ステータス自動「1次完了」＋次の回が開く
 * --------------------------------------------------------------
 *  1) onEdit … 最終更新＋（状態/反映）→ステータス自動連動＋タブ色更新
 *  2) updateTabColors … 要対応=赤/全完了=緑/全未着手=灰/進行中=青
 *  3) dailyDigestToLine … 1日1回 要対応サマリーをLINEグループへ1通
 *  4) generateDailyInstruction … 要対応を「今日の指示書(Markdown)」へ
 *  5) doPost … LINE Webhook受け口（groupIdを自動でスクリプトプロパティに保存）
 *  5b) doGet … ?mode=attention&token=… で要対応JSONを返す（Phase C用）
 *  6) draftFixWithClaude … (任意) Anthropic APIで修正案ドラフト ※デプロイは人の承認後
 *
 *  ※ LINE Notifyは2025/3/31終了。グループ通知はLINE Messaging API（公式アカウント）。
 *  セットアップ: スクリプトプロパティに
 *    LINE_CHANNEL_ACCESS_TOKEN（必須）/ LINE_GROUP_ID（doPostが自動保存）/
 *    SHEET_API_TOKEN（doGet認証用・Phase C）/（任意）ANTHROPIC_API_KEY
 *  → トリガーで dailyDigestToLine を毎日午前9時等。
 *****************************************************************/

const CONFIG = {
  CONTENT_SHEETS: ['10コマ', '企業紹介動画', '決算書分析動画', 'AI OB訪問（ルーム）'],
  COL: { 業界:1, 会社名:2, ステータス:3, 公開URL:4, 最終更新:45 },
  ROUNDS: 10, FIRST_ROW: 3,
  ATTENTION: ['FB対応中','要判断(オスカー)'],
  TAB: { 要対応:'#E06666', 完了:'#93C47D', 未着手:'#CCCCCC', 進行中:'#6FA8DC' },
};
function tanCol(n){ return 5 + (n-1)*4; }  // 担当
function fbCol(n){  return 6 + (n-1)*4; }  // FB
function jotCol(n){ return 7 + (n-1)*4; }  // 状態(インターン)
function hanCol(n){ return 8 + (n-1)*4; }  // 反映(Claude/オスカー)

/* ---------- 1) onEdit ---------- */
function onEdit(e){
  if(!e || !e.range) return;
  const sh = e.range.getSheet();
  if(CONFIG.CONTENT_SHEETS.indexOf(sh.getName())===-1) return;
  const row = e.range.getRow(), col = e.range.getColumn();
  if(row < CONFIG.FIRST_ROW) return;
  sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
  const c = sh.getRange(row, CONFIG.COL.ステータス);
  for(let n=1;n<=CONFIG.ROUNDS;n++){
    if(col===jotCol(n)){                      // 状態(インターン)
      const v=String(e.value||'');
      if(v==='提出') c.setValue('FB対応中');
      else if(v==='これでOK') c.setValue('完了');
      break;
    }
    if(col===hanCol(n)){                       // 反映(Claude/オスカー)
      if(String(e.value||'')==='反映済') c.setValue(n + '次完了');  // ラウンドで一般化(反映2→2次完了)
      break;
    }
  }
  updateTabColors();
}

/* ---------- 2) タブ自動変色 ---------- */
function updateTabColors(){
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last < CONFIG.FIRST_ROW){ sh.setTabColor(CONFIG.TAB.未着手); return; }
    const st = sh.getRange(CONFIG.FIRST_ROW, CONFIG.COL.ステータス, last-CONFIG.FIRST_ROW+1, 1)
                 .getValues().map(function(r){return String(r[0]||'').trim();}).filter(String);
    let color = CONFIG.TAB.進行中;
    if(st.some(function(s){return CONFIG.ATTENTION.indexOf(s)!==-1;})) color = CONFIG.TAB.要対応;
    else if(st.length && st.every(function(s){return s==='完了';})) color = CONFIG.TAB.完了;
    else if(st.length && st.every(function(s){return s==='未着手';})) color = CONFIG.TAB.未着手;
    sh.setTabColor(color);
  });
}

/* ---------- 共通：要対応の収集（最新ラウンドの担当・FB） ---------- */
function latestVal(row, colFn){
  let v='';
  for(let n=1;n<=CONFIG.ROUNDS;n++){ const x=row[colFn(n)-1]; if(x) v=String(x); }
  return v;
}
function collectAttention(){
  const ss = SpreadsheetApp.getActiveSpreadsheet(); const items=[];
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
    vals.forEach(function(r){
      if(CONFIG.ATTENTION.indexOf(String(r[CONFIG.COL.ステータス-1]).trim())!==-1){
        items.push({content:name, industry:r[0], company:r[1],
          owner:latestVal(r,tanCol), fb:latestVal(r,fbCol)});
      }
    });
  });
  return items;
}

/* ---------- 3) 1日1回 LINEダイジェスト ----------
 * [削除 2026-06-22] dailyDigestToLine は lineMorningList(buildMorningDigest) と
 * 朝の二重送信源だったため関数・トリガーともに撤去。朝の通知は lineMorningList(9時) に一本化。
 * 経緯: LINE 429調査の過程でトリガーを line3hSummary×5 + lineMorningList×1 の計6本に正常化。
 */

/* ---------- 4) 今日の指示書(Markdown) ---------- */
function generateDailyInstruction(){
  const items = collectAttention();
  let md = '# トーキャリ 今日の修正指示書（自動生成）\n\n';
  md += '対象: 要対応(FB対応中) ' + items.length + '件。各社、本番scenarioを読み内容で照合してから差替・lint・安全手順デプロイ・git push。捏造禁止。\n\n';
  const byC = {};
  items.forEach(function(it){ (byC[it.content]=byC[it.content]||[]).push(it); });
  Object.keys(byC).forEach(function(c){
    md += '## ' + c + '\n';
    byC[c].forEach(function(it){ md += '### ' + it.company + '（担当: ' + (it.owner||'-') + '）\n' + (it.fb||'(コメントなし)') + '\n\n'; });
  });
  Logger.log(md);
  return md;
}

/* ---------- 5) doPost：LINE Webhook（groupIdを自動保存） ---------- */
function doPost(e){
  // mode付きPOST(大きいrowsペイロード=GET URL長制限回避)はdoGetと同じrouterへ委譲。LINE Webhook(mode無し)は従来通り。
  const mode = (e && e.parameter && e.parameter.mode) || '';
  if(mode){
    const token = PropertiesService.getScriptProperties().getProperty('SHEET_API_TOKEN');
    if (typeof handleExt === 'function'){
      const r = handleExt(mode, e, token);
      if (r) return r;
    }
    return ContentService.createTextOutput('ok');
  }
  try{
    const body = JSON.parse(e.postData.contents);
    (body.events||[]).forEach(function(ev){
      if(ev.source){
        Logger.log('source: '+JSON.stringify(ev.source));
        if(ev.source.type==='group' && ev.source.groupId){
          PropertiesService.getScriptProperties().setProperty('LINE_GROUP_ID', ev.source.groupId);
        }
      }
    });
  }catch(err){ Logger.log('doPost err: '+err); }
  return ContentService.createTextOutput('ok');
}

/* ---------- 5b) doGet：要対応JSON（Phase C: GitHub Action用） ---------- */
function doGet(e){
  const token = PropertiesService.getScriptProperties().getProperty('SHEET_API_TOKEN');
  const mode = (e && e.parameter && e.parameter.mode) || '';
  if(mode === 'attention'){
    if(token && (!e.parameter.token || e.parameter.token !== token)){
      return ContentService.createTextOutput(JSON.stringify({error:'unauthorized'}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    const items = collectAttention();
    return ContentService.createTextOutput(JSON.stringify({
      generated_at: new Date().toISOString(),
      count: items.length,
      items: items
    })).setMimeType(ContentService.MimeType.JSON);
  }
  // --- Phase C 拡張(別ファイル phase_c_ext.js)。既存modeに非干渉 ---
  if (typeof handleExt === 'function'){
    const r = handleExt(mode, e, token);
    if (r) return r;
  }
  return ContentService.createTextOutput('ok');
}

/* ---------- 6) (任意) 自動修正ドラフト ※デプロイは人の承認後 ---------- */
function draftFixWithClaude(feedbackText){
  const key = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  if(!key){ Logger.log('ANTHROPIC_API_KEY 未設定'); return; }
  const res = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages',{
    method:'post', contentType:'application/json',
    headers:{ 'x-api-key':key, 'anthropic-version':'2023-06-01' },
    payload: JSON.stringify({ model:'claude-sonnet-4-6', max_tokens:1500,
      messages:[{role:'user', content:'トーキャリ10コマの校正担当として、次のFBを①バグ(即修正・差替文言提示)と②感想(要オスカー判断)に切り分け、①は具体的な差替文言まで。捏造・出典なき数字禁止。\n\nFB:\n'+feedbackText}] })
  });
  const data = JSON.parse(res.getContentText());
  const text = (data.content||[]).filter(function(b){return b.type==='text';}).map(function(b){return b.text;}).join('\n');
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let d = ss.getSheetByName('修正案ドラフト') || ss.insertSheet('修正案ドラフト');
  if(d.getLastRow()===0) d.appendRow(['日時','元FB','Claude修正案ドラフト']);
  d.appendRow([Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd HH:mm'), feedbackText, text]);
  return text;
}