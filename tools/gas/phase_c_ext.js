/*****************************************************************
 * phase_c_ext.js — Phase C 自動ループ用の追加機能（別ファイル＝既存コード.jsをclobberしない）
 *  doGet から handleExt(mode,e,token) で呼ばれる。書き込みは token 必須。
 *  追加mode:
 *    commonfixes   … 「共通の修正案」タブの未適用行を返す
 *    addcommonfix  … 共通の修正案を1行起票 (rule, scope)
 *    setpublicurl  … 10コマ表の公開URL列(D)に記入 (company,url)
 *    setreflected  … 反映=反映済 を立てる (company,round) → ステータス1次完了
 *  時刻トリガー: setupTriggers() を1回実行 → 9時=要対応リスト / 12,15,18,21,0時=直近3h要約
 *****************************************************************/
const COMMON_SHEET = '共通の修正案';   // A日時 B規則 Cスコープ D状態 E備考
const KOMA_SHEET = '10コマ';
const IMAGE_QA_SHEET = '画像人QA';   // A日時 B会社 Cslug Dコマ Esha Fレビューurl G指摘 H判定(待ち/OK/NG/反映済)
const IMAGE_QA_HEAD = ['日時','会社','slug','コマ','sha','レビューurl','指摘','判定'];

function _json(obj){
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
function _authed(e, token){
  return !(token && (!e.parameter.token || e.parameter.token !== token));
}
function _findRowByCompany(sh, company){
  const last = sh.getLastRow();
  if(last < CONFIG.FIRST_ROW) return -1;
  const names = sh.getRange(CONFIG.FIRST_ROW, CONFIG.COL.会社名, last-CONFIG.FIRST_ROW+1, 1).getValues();
  for(let i=0;i<names.length;i++){
    if(String(names[i][0]).trim() === String(company).trim()) return CONFIG.FIRST_ROW + i;
  }
  return -1;
}

function handleExt(mode, e, token){
  if(mode === 'commonfixes'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(COMMON_SHEET);
    const items = [];
    if(sh){
      const last = sh.getLastRow();
      for(let r=2; r<=last; r++){
        const row = sh.getRange(r,1,1,5).getValues()[0];
        if(String(row[3]).trim() !== '適用済'){
          items.push({row:r, date:row[0], rule:row[1], scope:row[2], status:row[3], note:row[4]});
        }
      }
    }
    return _json({count:items.length, items:items});
  }

  if(mode === 'addcommonfix'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sh = ss.getSheetByName(COMMON_SHEET);
    if(!sh){ sh = ss.insertSheet(COMMON_SHEET); sh.appendRow(['日時','規則','スコープ','状態','備考']); }
    sh.appendRow([Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd HH:mm'),
                  e.parameter.rule||'', e.parameter.scope||'全社', '未適用', e.parameter.note||'']);
    return _json({ok:true, row:sh.getLastRow()});
  }

  // ---- 画像人QA(混在型): 候補画像を人が OK/NG で承認 → OKは次ループが全ゲート付きで反映 ----
  if(mode === 'addimageqa'){
    // 候補起票。同一 slug+koマ の『待ち/OK』既存行があれば sha/url/日時を上書き(重複膨張防止)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sh = ss.getSheetByName(IMAGE_QA_SHEET);
    if(!sh){ sh = ss.insertSheet(IMAGE_QA_SHEET); sh.appendRow(IMAGE_QA_HEAD); }
    const slug=String(e.parameter.slug||''), koma=String(e.parameter.koma||'');
    const now=Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd HH:mm');
    const row=[now, e.parameter.company||'', slug, koma, e.parameter.sha||'',
               e.parameter.url||'', e.parameter.detail||'', '待ち'];
    const lr=sh.getLastRow();
    for(let r=2;r<=lr;r++){
      const v=sh.getRange(r,1,1,8).getValues()[0];
      if(String(v[2])===slug && String(v[3])===koma && (String(v[7])==='待ち'||String(v[7])==='OK')){
        sh.getRange(r,1,1,8).setValues([row]); return _json({ok:true, updated:r});
      }
    }
    sh.appendRow(row);
    return _json({ok:true, row:sh.getLastRow()});
  }
  if(mode === 'imageqa_approved'){
    // 人が『OK』にした候補を返す(次ループが反映する対象)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(IMAGE_QA_SHEET);
    const items=[];
    if(sh){ const lr=sh.getLastRow();
      for(let r=2;r<=lr;r++){ const v=sh.getRange(r,1,1,8).getValues()[0];
        if(String(v[7]).trim()==='OK'){
          items.push({row:r, company:v[1], slug:v[2], koma:v[3], sha:v[4], url:v[5], detail:v[6]});
        }
      }
    }
    return _json({count:items.length, items:items});
  }
  if(mode === 'imageqa_list'){
    // 起票済(待ち/OK)の {slug,koma} 一覧(混在型の再通知dedup用)。反映済は除外(再起票を許す)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(IMAGE_QA_SHEET);
    const items=[];
    if(sh){ const lr=sh.getLastRow();
      for(let r=2;r<=lr;r++){ const v=sh.getRange(r,1,1,8).getValues()[0];
        const st=String(v[7]).trim();
        if(st==='待ち'||st==='OK'){ items.push({slug:v[2], koma:v[3], status:st}); }
      }
    }
    return _json({count:items.length, items:items});
  }
  if(mode === 'setimageqa'){
    // 反映完了した候補を『反映済』に(冪等)。slug+koma 一致行の判定列を更新。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(IMAGE_QA_SHEET);
    if(!sh) return _json({error:'no sheet'});
    const slug=String(e.parameter.slug||''), koma=String(e.parameter.koma||''),
          st=String(e.parameter.status||'反映済'); let n=0; const lr=sh.getLastRow();
    for(let r=2;r<=lr;r++){ const v=sh.getRange(r,1,1,8).getValues()[0];
      if(String(v[2])===slug && String(v[3])===koma){ sh.getRange(r,8).setValue(st); n++; }
    }
    return _json({ok:true, updated:n});
  }

  if(mode === 'cleanfailnoise'){
    // 「処理失敗・要確認: ...npx」ノイズ行(launchd PATH欠落で毎時溜まった分)を共通の修正案から除去。
    // 実FB/実judgmentは規則にこの文字列を含まないので温存。row1(見出し)は保持。冪等。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(COMMON_SHEET);
    if(!sh) return _json({error:'no sheet'});
    const lr=sh.getLastRow(), lc=Math.max(sh.getLastColumn(),5);
    if(lr<2) return _json({removed:0, kept:0});
    const vals=sh.getRange(1,1,lr,lc).getValues();
    const keep=[vals[0]]; let removed=0;
    for(let i=1;i<vals.length;i++){
      const rule=String(vals[i][1]||'');
      if(rule.indexOf('処理失敗・要確認')>=0 && rule.indexOf('npx')>=0){ removed++; continue; }
      keep.push(vals[i]);
    }
    sh.getRange(1,1,lr,lc).clearContent();
    if(keep.length) sh.getRange(1,1,keep.length,lc).setValues(keep);
    return _json({removed:removed, kept:keep.length-1});
  }

  if(mode === 'dedupecommonfix'){
    // [要画像再生成]等の同一FB毎時再投入で膨張した重複を圧縮。冪等。row1(見出し)保持。
    //  キー: 要画像再生成は (社+コマ番号) で正規化(数値/引用文の揺れを吸収)、その他は規則の完全一致。
    //  未適用の重複は『最新1行』のみ残す。適用済(status=適用済)は履歴として全保持。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(COMMON_SHEET);
    if(!sh) return _json({error:'no sheet'});
    const lr=sh.getLastRow(), lc=Math.max(sh.getLastColumn(),5);
    if(lr<2) return _json({removed:0, kept:0});
    const vals=sh.getRange(1,1,lr,lc).getValues();
    function keyOf(rule){
      const r=String(rule||'');
      const m=r.match(/^\[要画像再生成\]\s*([^:：]+?)[\s　]*(?:コマ|koma|:|：)/);
      if(m){
        const comp=m[1].trim();
        let ks=(r.match(/(?:koma|コマ)\s*0*(\d+)/g)||[]).map(function(s){return s.replace(/\D/g,'');});
        ks=ks.filter(function(v,i){return ks.indexOf(v)===i;}).sort();
        return '要画像再生成|'+comp+'|'+ks.join(',');
      }
      return r.trim();
    }
    // 未適用行について keyごとの『最後の行index』を記録(最新を残す)
    const lastIdx={};
    for(let i=1;i<vals.length;i++){
      if(String(vals[i][3]).trim()==='適用済') continue;
      lastIdx[keyOf(vals[i][1])]=i;
    }
    const keep=[vals[0]]; let removed=0;
    for(let i=1;i<vals.length;i++){
      const applied=String(vals[i][3]).trim()==='適用済';
      if(applied){ keep.push(vals[i]); continue; }      // 履歴は全保持
      const k=keyOf(vals[i][1]);
      if(lastIdx[k]===i){ keep.push(vals[i]); }           // key最新のみ残す
      else { removed++; }
    }
    sh.getRange(1,1,lr,lc).clearContent();
    if(keep.length) sh.getRange(1,1,keep.length,lc).setValues(keep);
    return _json({removed:removed, kept:keep.length-1, uniqueUnapplied:Object.keys(lastIdx).length});
  }

  if(mode === 'deltrigger'){
    // 指定関数名のトリガーを削除し、残トリガーを列挙(429対策のレガシー重複除去用)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const fn = e.parameter.fn || '';
    let deleted = 0;
    ScriptApp.getProjectTriggers().forEach(function(t){
      if(t.getHandlerFunction() === fn){ ScriptApp.deleteTrigger(t); deleted++; }
    });
    const remain = ScriptApp.getProjectTriggers().map(function(t){ return t.getHandlerFunction(); });
    const tally = {}; remain.forEach(function(f){ tally[f] = (tally[f]||0)+1; });
    return _json({deleted:deleted, count:remain.length, tally:tally});
  }

  if(mode === 'line3hdryrun'){
    // line3hSummaryの送信なしドライラン。done/pendingNewFbをJSONで返す(検証用・LINEは送らない)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const res = computeLine3h();
    return _json({done_count:res.done.length, done:res.done,
                  pendingNewFb_count:res.pendingNewFb.length, pendingNewFb:res.pendingNewFb,
                  since:String(res.since)});
  }

  if(mode === 'linequota'){
    // 実測: 当月quota(type/value) + consumption(totalUsage) + bot情報(どのチャネルか) + 生レスポンス。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const props = PropertiesService.getScriptProperties();
    const tk = props.getProperty('LINE_CHANNEL_ACCESS_TOKEN');
    const gid = props.getProperty('LINE_GROUP_ID');
    if(!tk) return _json({error:'no token in ScriptProperties'});
    const hdr = { headers:{ Authorization:'Bearer '+tk }, muteHttpExceptions:true };
    const out = { token_tail: tk.slice(-6), group_id: (gid||'') };
    [['quota','https://api.line.me/v2/bot/message/quota'],
     ['consumption','https://api.line.me/v2/bot/message/quota/consumption'],
     ['botinfo','https://api.line.me/v2/bot/info']].forEach(function(p){
      try{
        const r = UrlFetchApp.fetch(p[1], hdr);
        out[p[0]] = { code:r.getResponseCode(), body:r.getContentText() };
      }catch(err){ out[p[0]] = { error:String(err) }; }
    });
    return _json(out);
  }

  if(mode === 'pushline'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const text = e.parameter.text || '';
    if(!text) return _json({error:'no text'});
    _pushLine(text);
    return _json({ok:true, pushed:text.length});
  }

  if(mode === 'pushlinefull'){
    // LINE push実行し、実APIレスポンス(HTTPコード + X-Line-Request-Id + sentMessages id + 送信先groupId)を返す。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const text = e.parameter.text || '';
    if(!text) return _json({error:'no text'});
    const props = PropertiesService.getScriptProperties();
    const tk = props.getProperty('LINE_CHANNEL_ACCESS_TOKEN');
    const gid = props.getProperty('LINE_GROUP_ID');
    if(!tk || !gid) return _json({error:'LINE未設定', has_token:!!tk, has_group:!!gid});
    const resp = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
      method:'post', contentType:'application/json',
      headers:{ Authorization:'Bearer '+tk },
      payload: JSON.stringify({ to: gid, messages:[{ type:'text', text: text }] }),
      muteHttpExceptions:true
    });
    const hdrs = resp.getAllHeaders();
    return _json({ code: resp.getResponseCode(), to: gid, chars: text.length,
                   request_id: hdrs['x-line-request-id'] || hdrs['X-Line-Request-Id'] || '',
                   body: resp.getContentText() });
  }

  if(mode === 'roomtabheader'){
    // L4「AI OB訪問（ルーム）」タブを新モデルに再構成: ヘッダ刷新 + CF。FBループ列は使わない。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName('AI OB訪問（ルーム）');
    if(!sh) return _json({error:'no room tab'});
    // 3層: 役割記号(C=R1-R6)/役割名(D=若手エース等)/氏名(E=個人名)。計13列。
    const hdr = ['会社名','slug','役割記号','役割名','氏名','人格の具体(部署/語り口)','退職パターン(R6)',
                 '検証(lint5)','ステータス','生成日','D1','Notion','要スポット確認'];
    sh.getRange(1,1,1,2).setValues([['🎭 トーキャリ・ルーム L4（6人格・生成+lint5=完成／人FBループ無し）','']]);
    // 旧45列由来のヘッダ残骸(14列目以降 FB3/状態3.../最終更新)を消去
    if(sh.getLastColumn()>hdr.length){
      sh.getRange(1,hdr.length+1,2,sh.getLastColumn()-hdr.length).clearContent();
    }
    sh.getRange(2,1,1,hdr.length).setValues([hdr]).setFontWeight('bold').setBackground('#cfe2f3'); // 青=Claude生成
    // 既存CFを除去して新規(完成=緑/未生成=グレー/検証✗=赤) I列ステータス(9) + H列検証(8)
    let rules = sh.getConditionalFormatRules().filter(function(rl){
      try{ var rs=rl.getRanges(); return !rs.some(function(r){return r.getColumn()===9||r.getColumn()===8;}); }catch(e){return true;}
    });
    const R = function(col){ return sh.getRange(3,col,2400,1); };
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('完成').setBackground('#c6efce').setRanges([R(9)]).build());
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('未生成').setBackground('#d9d9d9').setRanges([R(9)]).build());
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('✗').setBackground('#f4cccc').setRanges([R(8)]).build());
    sh.setConditionalFormatRules(rules);
    return _json({ok:true, header:hdr.length});
  }

  if(mode === 'roomtabwrite'){
    // 6人格行を一括書込。rows='A|B|...(13列タブ区切り);;...'。startRowから上書き。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('AI OB訪問（ルーム）');
    const start = parseInt(e.parameter.start||'3',10);
    const rows = (e.parameter.rows||'').split(';;').filter(String).map(function(r){
      const a=r.split('\t'); while(a.length<13) a.push(''); return a.slice(0,13);
    });
    if(rows.length===0) return _json({written:0});
    sh.getRange(start,1,rows.length,13).setValues(rows);
    sh.getRange(start,1,rows.length,13).setFontColor('#1155cc'); // 入力者色=青(Claude生成)
    return _json({written:rows.length, start:start, next:start+rows.length});
  }

  if(mode === 'roomtabclear'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('AI OB訪問（ルーム）');
    const last = sh.getLastRow();
    if(last>=3) sh.getRange(3,1,last-2,Math.max(13,sh.getLastColumn())).clearContent();
    return _json({cleared:last-2});
  }

  if(mode === 'roomtabvalidation'){
    // 旧10コマ45列由来のプルダウン(状態1-10/反映1-10等)を全列除去し、L4新12列に必要な4種のみ再設定。
    // 役割C=R1-R6 / ステータスH=完成・未生成 / 検証G=✓・✗ / 退職パターンF=A/B/C(R6行のみ)。冪等。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('AI OB訪問（ルーム）');
    if(!sh) return _json({error:'no sheet'});
    const lr = Math.max(sh.getLastRow(),2402), lc = Math.max(sh.getLastColumn(),45);
    // (1) 既存データ検証を列挙(報告用)
    const before = [];
    const dvAll = sh.getRange(3,1,lr-2,lc).getDataValidations();
    const colHit = {};
    for(let i=0;i<dvAll.length;i++) for(let j=0;j<lc;j++){ if(dvAll[i][j]){ colHit[j+1]=(colHit[j+1]||0)+1; } }
    Object.keys(colHit).forEach(function(c){ before.push('col'+c+':'+colHit[c]+'cells'); });
    // (2) 全データ検証を一掃(rows3+, 全45列)
    sh.getRange(3,1,lr-2,lc).clearDataValidations();
    // (3) 必要4種を再設定 (allowInvalid=true=警告のみ・ブロックしない) ※13列化で列位置シフト
    const mk = function(list){ return SpreadsheetApp.newDataValidation().requireValueInList(list,true).setAllowInvalid(true).build(); };
    sh.getRange(3,3,lr-2,1).setDataValidation(mk(['R1','R2','R3','R4','R5','R6']));   // C 役割記号
    sh.getRange(3,9,lr-2,1).setDataValidation(mk(['完成','未生成']));                  // I ステータス
    sh.getRange(3,8,lr-2,1).setDataValidation(mk(['✓','✗']));                          // H 検証
    // G 退職パターン: R6行のみ(データ行3起点で6行周期=row 8,14,20,...)
    const r6 = []; for(let row=8; row<=lr; row+=6){ r6.push('G'+row); }
    if(r6.length){ const dvF = mk(['A','B','C']); sh.getRangeList(r6).getRanges().forEach(function(rg){ rg.setDataValidation(dvF); }); }
    return _json({ok:true, removed_before:before, set:['C役割記号R1-R6','Iステータス完成/未生成','H検証✓/✗','G退職A/B/C(R6行'+r6.length+'件)']});
  }

  if(mode === 'roomblockedtab'){
    // 「ルーム要個別対応」タブ(AI OB訪問の隣)を恒久lintブロック社で再構成。
    // 既存の状態(未対応/対応中/解消)は人の編集を保護。今回incomingに無い既存slug=解消扱いで残す。冪等。
    // rows='会社名\tslug\tlint種別\t理由\t手当て方針;;...'
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const ref = ss.getSheetByName('AI OB訪問（ルーム）');
    let sh = ss.getSheetByName('ルーム要個別対応');
    if(!sh){ sh = ss.insertSheet('ルーム要個別対応', ref ? ref.getIndex() : ss.getNumSheets()); }
    const hdr=['会社名','slug','lint種別','理由','手当て方針','状態','更新日'];
    const today = Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd');
    // 既存行を退避(状態=人の編集を保護)
    const last = sh.getLastRow();
    const prev = {};
    if(last>=2){
      const ex = sh.getRange(2,1,last-1,7).getValues();
      ex.forEach(function(r){ if(r[1]) prev[String(r[1]).trim()]={name:r[0],kind:r[2],reason:r[3],plan:r[4],state:r[5]}; });
    }
    const incoming = (e.parameter.rows||'').split(';;').filter(String).map(function(r){ return r.split('\t'); });
    const inSlugs={}; const out=[];
    incoming.forEach(function(r){
      const slug=r[1]; inSlugs[slug]=true;
      const keep = (prev[slug] && prev[slug].state && prev[slug].state!=='解消') ? prev[slug].state : '未対応';
      out.push([r[0],slug,r[2]||'',r[3]||'',r[4]||'',keep,today]);
    });
    // 今回incomingに無い既存slug = 解消(行は残す)
    Object.keys(prev).forEach(function(slug){
      if(!inSlugs[slug]){ const p=prev[slug]; out.push([p.name,slug,p.kind,p.reason,p.plan,'解消',today]); }
    });
    sh.clear();
    sh.getRange(1,1,1,7).setValues([hdr]).setFontWeight('bold').setBackground('#cfe2f3');
    if(out.length) sh.getRange(2,1,out.length,7).setValues(out).setFontColor('#1155cc'); // 青=自動転記
    const n = Math.max(out.length,1);
    const dv = SpreadsheetApp.newDataValidation().requireValueInList(['未対応','対応中','解消'],true).setAllowInvalid(true).build();
    sh.getRange(2,6,n,1).setDataValidation(dv);  // 状態プルダウン
    const R = sh.getRange(2,6,n,1); const rules=[];
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('解消').setBackground('#c6efce').setRanges([R]).build());
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('未対応').setBackground('#f4cccc').setRanges([R]).build());
    rules.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('対応中').setBackground('#fff2cc').setRanges([R]).build());
    sh.setConditionalFormatRules(rules);
    return _json({ok:true, written:out.length, resolved:out.filter(function(r){return r[5]==='解消';}).length});
  }

  if(mode === 'bulkregister'){
    // wave投入済をスプシに一括起票(行指定=二重行ゼロ)。rows='row|slug|kind;;…' kind=gemini|old。
    // gemini: 公開URL記入+状態1空け→CFオレンジ(FB1待ち)。old: 公開URL記入+Note『要Gemini再生成』。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(KOMA_SHEET);
    const rows = (e.parameter.rows||'').split(';;').filter(String);
    const base = 'https://10koma-shukatsu.pages.dev/company?id=';
    const QUARANTINE = '旧画像・再生成待ち';   // 機械可読・可視の状態値(非オレンジ)。セルコメントは事故原因なので不可。
    let matched=0, oranged=0, quarantined=0; const errs=[];
    rows.forEach(function(item){
      const a=item.split('|'); const row=parseInt(a[0],10), slug=a[1], kind=a[2];
      if(!(row>=CONFIG.FIRST_ROW)){ errs.push('badrow:'+a[0]); return; }
      sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
      if(kind==='gemini'){
        // Gemini完成のみFB1待ち面へ: 公開URL記入 + 状態1空 + ステータス『公開済・FB待ち』(本番ライブ=未着手の嘘を解消)
        sh.getRange(row, CONFIG.COL.公開URL).setValue(base+slug).clearNote();
        sh.getRange(row, jotCol(1)).setValue('');
        // FB未記入(状態1空)の時だけ公開済・FB待ちに。既にFB進行中(N次完了等)は上書きしない=冪等。
        var stcell = sh.getRange(row, CONFIG.COL.ステータス);
        var st = String(stcell.getValue()).trim();
        if(st==='' || st==='未着手' || st==='公開済・FB待ち') stcell.setValue('公開済・FB待ち');
        oranged++;
      } else {
        // old/quarantine(旧ChatGPT画像): FB面に出さない。公開URL列を空に + 状態1を可視の隔離状態値に。
        sh.getRange(row, CONFIG.COL.公開URL).setValue('').clearNote();
        sh.getRange(row, jotCol(1)).setValue(QUARANTINE);
        quarantined++;
      }
      matched++;
    });
    return _json({matched:matched, oranged:oranged, quarantined:quarantined, errs:errs});
  }

  if(mode === 'cfpublished'){
    // CFオレンジを『公開済・FB待ち』ステータスに紐付け(C列限定で追記・既存ルール非破壊)。冪等。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(KOMA_SHEET);
    const rng = sh.getRange(CONFIG.FIRST_ROW, CONFIG.COL.ステータス, 403, 1); // C3:C405限定(他列に混入させない)
    let rules = sh.getConditionalFormatRules();
    // 既存の同等ルール(公開済・FB待ち)を除去してから1本だけ追加=冪等
    rules = rules.filter(function(rl){
      try{ var c=rl.getBooleanCondition(); var vs=c?c.getCriteriaValues():[];
        return !(vs && String(vs[0]).indexOf('公開済・FB待ち')>=0); }catch(e){ return true; }
    });
    const rule = SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo('公開済・FB待ち').setBackground('#f4b183').setRanges([rng]).build();
    rules.push(rule);
    sh.setConditionalFormatRules(rules);
    return _json({ok:true, rules_total:rules.length, range:'C3:C405'});
  }

  if(mode === 'fixdashboard'){
    // ダッシュボードの未使用バケツ『制作中』を『公開済・FB待ち』に転用(COUNTIF式+ヘッダ文言)。
    // 母数(COUNTA 398)は不変。公開済・FB待ちが未着手でなく進行中側に算入される。冪等。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ダッシュボード');
    if(!sh) return _json({error:'no dashboard'});
    const lr=sh.getLastRow(), lc=sh.getLastColumn();
    const rng=sh.getRange(1,1,lr,lc);
    const fs=rng.getFormulas(), vs=rng.getValues();
    let f_changed=0, h_changed=0;
    for(let i=0;i<lr;i++){
      for(let j=0;j<lc;j++){
        const f=fs[i][j];
        if(f && f.indexOf('"制作中"')>=0){
          sh.getRange(i+1,j+1).setFormula(f.split('"制作中"').join('"公開済・FB待ち"')); f_changed++;
        } else if(!f && String(vs[i][j]).trim()==='制作中'){
          sh.getRange(i+1,j+1).setValue('公開済・FB待ち'); h_changed++;
        }
      }
    }
    return _json({formula_changed:f_changed, header_changed:h_changed});
  }

  if(mode === 'fixdashnjikan'){
    // ダッシュボードの「1次完了」COUNTIFを "*次完了"(1次/2次/…/N次完了を全集約)に一般化。冪等。
    // "*次完了" は "完了"単体(サインオフ済=別カテゴリ)に非マッチ→二重計上しない。
    // 列見出しの "1次完了" も "1次完了以上" にリネーム(実態表記)。数式のみ・他集計不変。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ダッシュボード');
    if(!sh) return _json({error:'no dashboard'});
    const lr=sh.getLastRow(), lc=sh.getLastColumn();
    const rng=sh.getRange(1,1,lr,lc);
    const fs=rng.getFormulas(), vs=rng.getValues();
    const changed=[]; let hdr=0;
    for(let i=0;i<lr;i++){
      for(let j=0;j<lc;j++){
        const f=fs[i][j];
        if(f && f.indexOf('"1次完了"')>=0){
          const nf=f.split('"1次完了"').join('"*次完了"');
          if(nf!==f){ sh.getRange(i+1,j+1).setFormula(nf);
            changed.push({cell:(j<26?String.fromCharCode(65+j):'A'+String.fromCharCode(65+j-26))+(i+1)}); }
        } else if(!f && String(vs[i][j]).trim()==='1次完了'){
          sh.getRange(i+1,j+1).setValue('1次完了以上'); hdr++;
        }
      }
    }
    return _json({formula_generalized:changed.length, changed:changed, header_relabeled:hdr});
  }

  if(mode === 'roomdashboard'){
    // AI OB訪問(ルーム)行をL4機械ゲートモデルに修正: ステータスH列(完成/未生成)を6で割り社数化。
    // 旧式はC列(役割R1-R6)を指し常に0%だった不整合を解消。人FBループ列は概念無し→「—」。
    // 全体サマリーE7の完了数にL4完成社を算入。進捗モデル注記(人確認=3/4)を追記。母数(C7=COUNTA398)不変。冪等。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ダッシュボード');
    if(!sh) return _json({error:'no dashboard'});
    const RT = "'AI OB訪問（ルーム）'!$I$3:$I$2402";  // ステータス列I(13列化でH→I)×2400行
    sh.getRange('B14').setValue('AI OB訪問（ルーム）★L4機械ゲート(lint5+D1)');
    sh.getRange('C14').setFormula('=COUNTIF('+RT+',"完成")/6');   // 完成社数=完成行/6
    sh.getRange('D14').setValue('—');  // 公開済・FB待ち: L4は概念無し
    sh.getRange('E14').setValue('—');  // FB対応中: 人FBループ無し
    sh.getRange('F14').setValue('—');  // 1次完了: 人ゲート無し
    sh.getRange('G14').setFormula('=COUNTIF('+RT+',"未生成")/6');  // 未生成社数
    sh.getRange('H14').setFormula('=IF(C14="",0,C14/400)');        // 完成率=完成社/400
    // 全体サマリー完了数: 旧AI OB COUNTIF"完了"(=0)をL4完成社(C14)に置換
    sh.getRange('E7').setFormula(
      '=COUNTIF(\'10コマ\'!$C$3:$C$405,"完了")+COUNTIF(\'企業紹介動画\'!$C$3:$C$405,"完了")'+
      '+COUNTIF(\'決算書分析動画\'!$C$3:$C$405,"完了")+C14');
    // 進捗モデル注記(人確認=3/4)
    sh.getRange('B44').setValue('■ 進捗モデル');
    sh.getRange('B45').setValue('AI OB訪問（ルーム）= L4機械ゲート: room-lint5全通過 AND D1登録 のときのみ「完成」（これでOK不要・人FBループ無し）。完成率=完成社/400。');
    sh.getRange('B46').setValue('人確認対象 = 10コマ／企業紹介動画／決算書分析動画 の3コンテンツ（全体の3/4）。母数 C7=COUNTA 398/400 不変。');
    return _json({ok:true, model:'L4 machine-gate row14 + E7 + 3/4 annotation'});
  }

  if(mode === 'markpublished'){
    // 一括是正: 公開URL有 かつ 状態1空 かつ ステータス=未着手 → 『公開済・FB待ち』(本番ライブの嘘を解消)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(KOMA_SHEET);
    const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return _json({changed:0});
    const n = last-CONFIG.FIRST_ROW+1;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,n,45).getValues();
    let changed=0;
    for(let i=0;i<n;i++){
      const r=vals[i]; if(!r[1]) continue;
      const url=String(r[CONFIG.COL.公開URL-1]).trim();
      const jot1=String(r[jotCol(1)-1]).trim();
      const st=String(r[CONFIG.COL.ステータス-1]).trim();
      if(url.indexOf('http')===0 && jot1==='' && st==='未着手'){
        sh.getRange(CONFIG.FIRST_ROW+i, CONFIG.COL.ステータス).setValue('公開済・FB待ち');
        sh.getRange(CONFIG.FIRST_ROW+i, CONFIG.COL.最終更新).setValue(new Date());  // 公開済社を直近3hレポートに載せる
        changed++;
      }
    }
    return _json({changed:changed});
  }

  if(mode === 'markcommonfix'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(COMMON_SHEET);
    const row = parseInt(e.parameter.row,10);
    if(sh && row>=2){ sh.getRange(row,4).setValue(e.parameter.status||'適用済'); return _json({ok:true}); }
    return _json({error:'row not found'});
  }

  if(mode === 'setpublicurl'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const row = _findRowByCompany(sh, e.parameter.company);
    if(row < 0) return _json({error:'company not found', company:e.parameter.company});
    sh.getRange(row, CONFIG.COL.公開URL).setValue(e.parameter.url||'');
    sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
    return _json({ok:true, row:row});
  }

  if(mode === 'appendrow10koma'){
    // 10コマタブ末尾に1行追加(業界/会社名/公開URL/ステータス+最終更新)。既存モード不変の純加算。
    // 冪等: 同名会社が既存ならスキップし existing 報告(重複行を作らない)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(KOMA_SHEET);
    if(!sh) return _json({error:'no sheet'});
    const company = String(e.parameter.company||'').trim();
    if(!company) return _json({error:'no company'});
    const existing = _findRowByCompany(sh, company);
    if(existing >= 0) return _json({ok:true, existing:true, row:existing, note:'既存行あり=追加せず'});
    const before = sh.getLastRow();
    const row = before + 1;
    sh.getRange(row, CONFIG.COL.業界).setValue(e.parameter.industry||'');
    sh.getRange(row, CONFIG.COL.会社名).setValue(company);
    sh.getRange(row, CONFIG.COL.公開URL).setValue(e.parameter.url||'');
    sh.getRange(row, CONFIG.COL.ステータス).setValue(e.parameter.status||'公開済・FB待ち');
    sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
    // 見本行から書式・入力規則(プルダウン)を継承(内容は不変・純加算)。CFはrange(3-2402)方式で自動適用。
    var _sample = parseInt(e.parameter.sample||String(CONFIG.FIRST_ROW),10);
    var _lc = sh.getLastColumn();
    if(_sample>=CONFIG.FIRST_ROW && _sample!==row){
      var _src = sh.getRange(_sample,1,1,_lc);
      _src.copyTo(sh.getRange(row,1,1,_lc), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
      _src.copyTo(sh.getRange(row,1,1,_lc), SpreadsheetApp.CopyPasteType.PASTE_DATA_VALIDATION, false);
    }
    return _json({ok:true, added:true, row:row, before:before, after:sh.getLastRow(), format_from:_sample});
  }

  if(mode === 'setcompanyname'){
    // 会社名セルの表記揺れ是正(マスターDB基準)。sheet上でfrom社名の行を特定→会社名セルをtoへ。
    // 純粋なセル値変更(行移動なし=FB/状態列はそのまま)。冪等: 既にto/該当行なしはno-op報告。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(e.parameter.sheet || KOMA_SHEET);
    if(!sh) return _json({error:'no sheet', sheet:e.parameter.sheet||''});
    const from = String(e.parameter.from||'').trim();
    const to = String(e.parameter.to||'').trim();
    if(!from || !to) return _json({error:'from/to required'});
    let row = _findRowByCompany(sh, from);
    if(row < 0){
      // 既にtoに是正済かも(冪等)
      if(_findRowByCompany(sh, to) >= 0) return _json({ok:true, noop:true, note:'既にto表記=変更不要'});
      return _json({error:'from not found', from:from, sheet:sh.getName()});
    }
    sh.getRange(row, CONFIG.COL.会社名).setValue(to);
    return _json({ok:true, renamed:true, row:row, from:from, to:to, sheet:sh.getName()});
  }

  if(mode === 'appendrowsheet'){
    // appendrow10koma の sheet 一般化版(企業紹介動画/決算書分析動画 等の欠落社追加用)。
    // 業界/会社名/ステータス列に記入し、見本行から書式・入力規則を継承(純加算)。冪等: 同名既存はskip。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(e.parameter.sheet || KOMA_SHEET);
    if(!sh) return _json({error:'no sheet', sheet:e.parameter.sheet||''});
    const company = String(e.parameter.company||'').trim();
    if(!company) return _json({error:'no company'});
    const existing = _findRowByCompany(sh, company);
    if(existing >= 0) return _json({ok:true, existing:true, row:existing, note:'既存行あり=追加せず', sheet:sh.getName()});
    const before = sh.getLastRow();
    const row = before + 1;
    sh.getRange(row, CONFIG.COL.業界).setValue(e.parameter.industry||'');
    sh.getRange(row, CONFIG.COL.会社名).setValue(company);
    if(e.parameter.status) sh.getRange(row, CONFIG.COL.ステータス).setValue(e.parameter.status);
    var _sample = parseInt(e.parameter.sample||String(CONFIG.FIRST_ROW),10);
    var _lc = sh.getLastColumn();
    if(_sample>=CONFIG.FIRST_ROW && _sample!==row){
      var _src = sh.getRange(_sample,1,1,_lc);
      _src.copyTo(sh.getRange(row,1,1,_lc), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
      _src.copyTo(sh.getRange(row,1,1,_lc), SpreadsheetApp.CopyPasteType.PASTE_DATA_VALIDATION, false);
    }
    return _json({ok:true, added:true, row:row, before:before, after:sh.getLastRow(), sheet:sh.getName(), format_from:_sample});
  }

  if(mode === 'fixrowformat'){
    // 既存の追加行(appendrow等)の書式・入力規則(プルダウン)を見本行から複製(内容は不変・純加算)。
    // 対象は company or row で指定。CFはrange方式で自動適用済ゆえ触らない(新規ルール乱造しない)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(e.parameter.sheet || KOMA_SHEET);
    if(!sh) return _json({error:'no sheet'});
    const sample = parseInt(e.parameter.sample||String(CONFIG.FIRST_ROW),10);
    let target = 0;
    if(e.parameter.row) target = parseInt(e.parameter.row,10);
    else if(e.parameter.company) target = _findRowByCompany(sh, e.parameter.company);
    if(!(target>=CONFIG.FIRST_ROW)) return _json({error:'target row not found', company:e.parameter.company||''});
    if(!(sample>=CONFIG.FIRST_ROW) || sample===target) return _json({error:'bad sample'});
    const lc = sh.getLastColumn();
    const src = sh.getRange(sample,1,1,lc);
    src.copyTo(sh.getRange(target,1,1,lc), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
    src.copyTo(sh.getRange(target,1,1,lc), SpreadsheetApp.CopyPasteType.PASTE_DATA_VALIDATION, false);
    const dvInfo = function(col){
      const d = sh.getRange(target,col).getDataValidation();
      if(!d) return 'none';
      try{ const cv=d.getCriteriaValues(); if(cv&&cv[0]&&cv[0].map) return 'list('+cv[0].length+')'; return String(d.getCriteriaType()); }
      catch(err){ return 'err'; }
    };
    return _json({ok:true, target:target, sample:sample,
      dv_status: dvInfo(CONFIG.COL.ステータス), dv_jot1: dvInfo(jotCol(1)), dv_han1: dvInfo(hanCol(1))});
  }

  if(mode === 'setreflected'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const row = _findRowByCompany(sh, e.parameter.company);
    if(row < 0) return _json({error:'company not found', company:e.parameter.company});
    // round未指定なら、FBが入っている最新ラウンドを自動検出
    let round = parseInt(e.parameter.round||'0',10);
    if(!round){
      const r = sh.getRange(row,1,1,45).getValues()[0];
      for(let n=1;n<=CONFIG.ROUNDS;n++){ if(r[fbCol(n)-1]) round=n; }
      if(!round) round=1;
    }
    sh.getRange(row, hanCol(round)).setValue('反映済');
    sh.getRange(row, CONFIG.COL.ステータス).setValue(round + '次完了');  // ラウンドで一般化
    sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
    return _json({ok:true, row:row, round:round});
  }
  if(mode === 'setescalated'){
    // 判断系(Source-or-Silence/主観/複数コマ等)=人へ。反映列は触らず status=要判断(オスカー)。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const row = _findRowByCompany(sh, e.parameter.company);
    if(row < 0) return _json({error:'company not found', company:e.parameter.company});
    sh.getRange(row, CONFIG.COL.ステータス).setValue('要判断(オスカー)');
    sh.getRange(row, CONFIG.COL.最終更新).setValue(new Date());
    if(e.parameter.reason){ sh.getRange(row, CONFIG.COL.ステータス).setNote('要判断: '+String(e.parameter.reason).slice(0,500)); }
    return _json({ok:true, row:row, status:'要判断(オスカー)'});
  }

  if(mode === 'attention_robust'){
    // 取りこぼし対策: ステータス=FB対応中 に加え、最新ラウンドが「状態=提出 かつ 反映=空」の行も拾う
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet(); const items=[];
    CONFIG.CONTENT_SHEETS.forEach(function(name){
      const sh = ss.getSheetByName(name); if(!sh) return;
      const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return;
      const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
      vals.forEach(function(r){
        const statusAtt = CONFIG.ATTENTION.indexOf(String(r[CONFIG.COL.ステータス-1]).trim())!==-1;
        // 最新のFBラウンド
        let latest=0; for(let n=1;n<=CONFIG.ROUNDS;n++){ if(r[fbCol(n)-1]) latest=n; }
        const pending = latest>0 && String(r[jotCol(latest)-1]).trim()==='提出'
                        && !String(r[hanCol(latest)-1]).trim();
        if(statusAtt || pending){
          items.push({content:name, industry:r[0], company:r[1], round:latest,
                      owner:latestVal(r,tanCol), fb:latestVal(r,fbCol),
                      reason: statusAtt?'FB対応中':'提出&反映空'});
        }
      });
    });
    return _json({count:items.length, items:items});
  }

  if(mode === 'setuptriggers'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    setupTriggers();
    return _json({ok:true, note:'9時=要対応 / 12,15,18,21,0時=直近3h'});
  }

  if(mode === 'celldiag'){
    // 診断: D列(4)/J列(10)の背景色+値、各行のステータス・round2状態/反映、条件付き書式の有無
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const last = sh.getLastRow();
    const n = last - CONFIG.FIRST_ROW + 1;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,n,45).getValues();
    const dBgs = sh.getRange(CONFIG.FIRST_ROW,4,n,1).getBackgrounds();   // D列 一括
    const jBgs = sh.getRange(CONFIG.FIRST_ROW,10,n,1).getBackgrounds();  // J列 一括
    const out = [];
    for(let i=0;i<n;i++){
      const v = vals[i];
      if(!v[1]) continue;
      out.push({
        row:CONFIG.FIRST_ROW+i, company:String(v[1]), status:String(v[2]||''),
        D_val:String(v[3]||''), D_bg:dBgs[i][0],
        J_val:String(v[9]||'').slice(0,20), J_bg:jBgs[i][0],
        r2_state:String(v[10]||''), r2_reflect:String(v[11]||'')
      });
    }
    // 条件付き書式ルール数(色の自動付与があるか)
    let cfCount = 0;
    try { cfCount = sh.getConditionalFormatRules().length; } catch(err){}
    return _json({conditional_format_rules: cfCount, rows: out});
  }

  if(mode === 'fixcf12'){
    // rule#12是正: 全ルールから『純粋J列(col10のみ)』のrangeを除去(=J6:J7,J9:J28)。他range/条件/書式は不変。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const rules = sh.getConditionalFormatRules();
    const removed = [];
    const newRules = rules.map(function(rule){
      const ranges = rule.getRanges();
      const kept = ranges.filter(function(r){
        const isPureJ = (r.getColumn()===10 && r.getLastColumn()===10);
        if(isPureJ) removed.push(r.getA1Notation());
        return !isPureJ;
      });
      if(kept.length===ranges.length) return rule;           // 変更なし
      if(kept.length===0) return null;                       // 全rangeがJ→ルール削除(該当しない想定)
      return rule.copy().setRanges(kept).build();
    }).filter(function(x){return x!==null;});
    sh.setConditionalFormatRules(newRules);
    return _json({ok:true, removed_ranges:removed, rules_after:newRules.length});
  }

  if(mode === 'cfforcell'){
    // 指定セル(col,row)に range が掛かるCFルールを全列挙(条件・色付き)。CF実塗りの特定用。
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(e.parameter.sheet || KOMA_SHEET);
    const col = parseInt(e.parameter.col||'4',10);
    const rowsP = (e.parameter.rows||'3,4,5,8,9,10').split(',').map(function(x){return parseInt(x,10);});
    const rules = sh.getConditionalFormatRules();
    const out = {};
    rowsP.forEach(function(rw){
      const hits = [];
      rules.forEach(function(rule,idx){
        const inRange = rule.getRanges().some(function(r){
          return rw>=r.getRow() && rw<=r.getLastRow() && col>=r.getColumn() && col<=r.getLastColumn();
        });
        if(!inRange) return;
        let cond=null,bg=null;
        try{ const bc=rule.getBooleanCondition(); if(bc){cond={type:String(bc.getCriteriaType()),values:bc.getCriteriaValues()}; bg=bc.getBackgroundObject()?bc.getBackgroundObject().asRgbColor().asHexString():null;} }catch(err){}
        hits.push({rule:idx, bg:bg, cond:cond, ranges:rule.getRanges().map(function(r){return r.getA1Notation();})});
      });
      // セル値+明示背景も付ける
      out["row"+rw] = {value:String(sh.getRange(rw,col).getValue()), explicit_bg:sh.getRange(rw,col).getBackground(), matching_rules:hits};
    });
    return _json({col:col, cells:out});
  }

  if(mode === 'fixstatusrounds'){
    // 既存行のステータス『N次完了』を、実際の最高『反映済』ラウンドに合わせて是正(完了/未着手等は触らない)
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const names = e.parameter.sheet ? [e.parameter.sheet] : CONFIG.CONTENT_SHEETS;
    const fixed = [];
    names.forEach(function(name){
      const sh = ss.getSheetByName(name); if(!sh) return;
      const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return;
      const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
      vals.forEach(function(r,i){
        const status = String(r[CONFIG.COL.ステータス-1]||'').trim();
        if(!/^\d+次完了$/.test(status)) return;   // 反映済由来の『N次完了』のみ対象
        let maxr = 0;
        for(let n=1;n<=CONFIG.ROUNDS;n++){ if(String(r[hanCol(n)-1]).trim()==='反映済') maxr=n; }
        if(maxr>0){
          const correct = maxr + '次完了';
          if(status !== correct){
            sh.getRange(CONFIG.FIRST_ROW+i, CONFIG.COL.ステータス).setValue(correct);
            fixed.push({sheet:name, row:CONFIG.FIRST_ROW+i, company:String(r[1]), from:status, to:correct});
          }
        }
      });
    });
    return _json({fixed_count:fixed.length, fixed:fixed});
  }

  if(mode === 'readsheet'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(e.parameter.sheet);
    if(!sh) return _json({error:'no sheet'});
    const lr=sh.getLastRow(), lc=sh.getLastColumn();
    const vals = sh.getRange(1,1,lr,lc).getValues();
    const formulas = (e.parameter.formulas==="1") ? sh.getRange(1,1,lr,lc).getFormulas() : null;
    return _json({name:e.parameter.sheet, values:vals, formulas:formulas});
  }

  if(mode === 'statusvalidation'){
    // ステータス列の入力規則を読取報告 + N次完了(N=1..10)を許可値に拡張(allowInvalid=true=警告/拒否しない)
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const apply = (e.parameter.apply === '1');
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const want = ['未着手','公開済・FB待ち','記入中','提出','FB対応中','要判断(オスカー)','これでOK','完了'];
    for(let n=1;n<=10;n++) want.push(n+'次完了');
    const report = {};
    CONFIG.CONTENT_SHEETS.forEach(function(name){
      const sh = ss.getSheetByName(name); if(!sh) return;
      const last = sh.getLastRow();
      const cell = sh.getRange(CONFIG.FIRST_ROW, CONFIG.COL.ステータス);
      const dv = cell.getDataValidation();
      let oldList = [], oldType = 'なし';
      if(dv){
        oldType = String(dv.getCriteriaType());
        try{
          const cv = dv.getCriteriaValues();
          if(cv && cv[0] && cv[0].map){ oldList = cv[0].map(String); }
          else if(cv && cv[0] && cv[0].getValues){ oldList = cv[0].getValues().map(function(r){return String(r[0]);}).filter(String); }
        }catch(err){ oldList = ['(read不可:'+err+')']; }
      }
      const merged = want.slice();
      oldList.forEach(function(v){ if(v && merged.indexOf(v)<0) merged.push(v); });
      if(apply && last>=CONFIG.FIRST_ROW){
        const rule = SpreadsheetApp.newDataValidation().requireValueInList(merged, true).setAllowInvalid(true).build();
        sh.getRange(CONFIG.FIRST_ROW, CONFIG.COL.ステータス, last-CONFIG.FIRST_ROW+1, 1).setDataValidation(rule);
      }
      report[name] = {old_type: oldType, old_list: oldList, new_list_count: merged.length, applied: apply, rows: Math.max(0,last-CONFIG.FIRST_ROW+1)};
    });
    return _json({want: want, sheets: report});
  }

  if(mode === 'morningpreview'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    return _json({digest: buildMorningDigest()});
  }

  if(mode === 'listsheets'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const out = ss.getSheets().map(function(sh){
      const lc = sh.getLastColumn();
      const hdr = lc>0 ? sh.getRange(1,1,2,Math.min(lc,50)).getValues() : [];
      return {name:sh.getName(), rows:sh.getLastRow(), cols:lc, header:hdr};
    });
    return _json({sheets:out});
  }

  if(mode === 'listtriggers'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    try {
      const trs = ScriptApp.getProjectTriggers();
      const out = trs.map(function(t){
        return {fn:t.getHandlerFunction(), type:String(t.getEventType()), source:String(t.getTriggerSource())};
      });
      return _json({count:out.length, triggers:out});
    } catch(err){
      return _json({error:String(err)});
    }
  }

  if(mode === 'cfrules'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(KOMA_SHEET);
    const rules = sh.getConditionalFormatRules();
    const out = rules.map(function(rule){
      const ranges = rule.getRanges().map(function(r){return r.getA1Notation();});
      let cond=null, bg=null;
      try {
        const bc = rule.getBooleanCondition();
        if(bc){ cond={type:String(bc.getCriteriaType()), values:bc.getCriteriaValues()}; bg=bc.getBackgroundObject()?bc.getBackgroundObject().asRgbColor().asHexString():null; }
      } catch(err){ cond={err:String(err)}; }
      return {ranges:ranges, condition:cond, background:bg};
    });
    return _json({count:out.length, rules:out});
  }

  if(mode === 'companyrow'){
    if(!_authed(e, token)) return _json({error:'unauthorized'});
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(e.parameter.sheet || KOMA_SHEET);
    const row = _findRowByCompany(sh, e.parameter.company);
    if(row < 0) return _json({error:'company not found', company:e.parameter.company});
    const r = sh.getRange(row,1,1,45).getValues()[0];
    const rounds = [];
    for(let n=1;n<=CONFIG.ROUNDS;n++){
      const tan=r[tanCol(n)-1], fb=r[fbCol(n)-1], jot=r[jotCol(n)-1], han=r[hanCol(n)-1];
      if(tan||fb||jot||han) rounds.push({round:n, owner:String(tan||''), fb:String(fb||''),
                                         state:String(jot||''), reflected:String(han||'')});
    }
    return _json({row:row, company:String(r[1]), status:String(r[2]), publicUrl:String(r[3]||''), rounds:rounds});
  }
  return null; // 未知mode → 既存doGetのfallbackへ
}

/* ---------- LINE 共通 ---------- */
function _pushLine(text){
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('LINE_CHANNEL_ACCESS_TOKEN');
  const groupId = props.getProperty('LINE_GROUP_ID');
  if(!token || !groupId){ Logger.log('LINE未設定:\n'+text); return; }
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method:'post', contentType:'application/json',
    headers:{ Authorization:'Bearer '+token },
    payload: JSON.stringify({ to: groupId, messages:[{ type:'text', text: text }] })
  });
}

/* 次ラウンドFB待ち = スプシのCFオレンジと同一条件:
   AND(反映N="反映済", OR(round(N+1)状態="", "記入中"))。最も高い開放ラウンドで集計。 */
function _collectFBwait(){
  const ss = SpreadsheetApp.getActiveSpreadsheet(); const by = {};
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
    vals.forEach(function(r){
      if(!r[1]) return;
      let opened = 0;
      for(let n=1;n<=CONFIG.ROUNDS-1;n++){
        const han = String(r[hanCol(n)-1]).trim();
        const nextJot = String(r[jotCol(n+1)-1]).trim();
        if(han==='反映済' && (nextJot==='' || nextJot==='記入中')) opened = n+1;
      }
      if(opened>0){
        const key = name+'|'+r[0]+'|FB'+opened;
        by[key] = (by[key]||0)+1;
      }
    });
  });
  return by;
}

/* システム停止/エスカレ: 「共通の修正案」タブで [停止]/[CANARY]/[エスカレ] 始まりの行 */
function _collectSystemStops(){
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('共通の修正案');
  const out = []; if(!sh) return out;
  const last = sh.getLastRow();
  for(let r=2; r<=last; r++){
    const vals = sh.getRange(r,1,1,5).getValues()[0];
    const txt = [vals[0],vals[1]].map(function(x){return String(x||'');}).join(' ');
    const status = String(vals[3]||'');
    const mk = txt.match(/\[(停止|CANARY|エスカレ|要対応)\][\s\S]*/);
    if(mk && status!=='解消'){ out.push(mk[0].trim().slice(0,90)); }
  }
  return out;
}

/* 朝ダイジェスト本文を組み立て(2バケツ)。両方ゼロのとき初めて0件。 */
/* ステータス別 社数集計(content別) — 完了/これでOK は除外。{content: n} を返す。 */
function _collectByStatus(statusName){
  const ss = SpreadsheetApp.getActiveSpreadsheet(); const by = {};
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last<CONFIG.FIRST_ROW) return;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
    vals.forEach(function(r){
      if(!r[1]) return;
      if(String(r[CONFIG.COL.ステータス-1]).trim()===statusName){ by[name]=(by[name]||0)+1; }
    });
  });
  return by;
}

/* ラベル是正: 反映(実適用待ち=FB対応中) / 要判断(オスカー=人へ) / FB待ち(次ラウンド) を明確分離。
   完了・これでOK・FB無しは混ぜない(伊藤忠など完了社が"反映"に出る誤りを止める)。 */
/* 判断ダイジェスト: 共通の修正案 scope=judgment_daily の未解消行(=真にブランド判断が要る稀なもの)。 */
function _collectJudgmentDaily(){
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(COMMON_SHEET);
  const out = []; if(!sh) return out;
  const last = sh.getLastRow();
  for(let r=2; r<=last; r++){
    const row = sh.getRange(r,1,1,5).getValues()[0];
    if(String(row[2]).trim()==='judgment_daily' && String(row[3]).trim()!=='解消' && String(row[3]).trim()!=='適用済'){
      out.push(String(row[1]));
    }
  }
  return out;
}

function buildMorningDigest(){
  const fbwait = _collectFBwait();                 // 次ラウンドFB待ち(CFオレンジ)
  const reflectWait = _collectByStatus('FB対応中'); // AIが反映予定(実適用待ち)
  const judgments = _collectJudgmentDaily();        // 真のブランド判断のみ(朝1通・要れば後で覆せる)
  const stops = _collectSystemStops();
  const url = SpreadsheetApp.getActiveSpreadsheet().getUrl();
  const sum = function(o){ var t=0; Object.keys(o).forEach(function(k){t+=o[k];}); return t; };
  const waitTotal = sum(fbwait), reflTotal = sum(reflectWait);
  if(waitTotal===0 && reflTotal===0 && judgments.length===0 && stops.length===0){
    return '【おはようございます☀️】FB待ち・判断ダイジェストともに0件です 🎉';
  }
  const p = ['【おはようございます☀️ 本日】'];
  p.push('━━【インターンの皆さんへ】次ラウンドFB待ち '+waitTotal+'社');
  const wk = Object.keys(fbwait);
  if(wk.length===0) p.push('・なし');
  wk.forEach(function(k){ const a=k.split('|'); p.push('・'+a[0]+' '+a[1]+' '+fbwait[k]+'社：'+a[2]+'をお願いします'); });
  p.push('━━【AIが反映予定(実適用待ち)】'+reflTotal+'件');
  if(reflTotal===0) p.push('・なし');
  Object.keys(reflectWait).forEach(function(k){ p.push('・'+k+': '+reflectWait[k]+'件'); });
  // オスカー宛は『判断ダイジェスト』のみ(朝9時1通に集約・好み/事実/明確修正はAIが自走で処理済)
  p.push('━━【判断ダイジェスト(オスカー・要れば後で覆せる)】'+judgments.length+'件');
  if(judgments.length===0) p.push('・なし(AIが自走で処理済)');
  judgments.slice(0,15).forEach(function(s){ p.push('・'+s.slice(0,70)); });
  stops.forEach(function(s){ p.push('⚠ '+s); });
  p.push(url);
  return p.join('\n');
}

/* 9時: 朝ダイジェスト(2バケツ) */
function lineMorningList(){
  _pushLine(buildMorningDigest());
}

/* 直近3hのAI活動を算出(送信しない・検証と本送信の共通ロジック)。
   厳格化(2026-07-07): 「反映した社」= 最新FBラウンドが反映済 OR 公開済・FB待ち、かつ 最終更新が3h以内。
   過去反映済&新FB未対応(=最新FBが未反映)は done から除外し pendingNewFb に分離。 */
function computeLine3h(){
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const since = new Date(Date.now() - 3*60*60*1000);
  const done = [], pendingNewFb = [];
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last < CONFIG.FIRST_ROW) return;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
    vals.forEach(function(r){
      if(!r[CONFIG.COL.会社名-1]) return;
      const upd = r[CONFIG.COL.最終更新-1];
      if(!(upd instanceof Date && upd >= since)) return;      // 直近3h以内のみ
      const status = String(r[CONFIG.COL.ステータス-1]).trim();
      let maxFbRound=0, maxReflectedRound=0;
      for(let n=1;n<=CONFIG.ROUNDS;n++){
        if(String(r[fbCol(n)-1]).trim()!=='')   maxFbRound=n;
        if(String(r[hanCol(n)-1]).trim()==='反映済') maxReflectedRound=n;
      }
      const strictReflected = (maxFbRound>0 && maxReflectedRound>=maxFbRound); // 最新FBが反映済
      const published       = (status==='公開済・FB待ち');
      const newFbPending    = (maxReflectedRound>0 && maxFbRound>maxReflectedRound); // 過去反映済&新FB未対応
      const label = '・'+name+'/'+r[CONFIG.COL.会社名-1];
      if(strictReflected || published){ done.push(label); }
      else if(newFbPending){ pendingNewFb.push(label); }
    });
  });
  return {done:done, pendingNewFb:pendingNewFb, since:since};
}

/* 画像人QA(混在型)の 待ち候補 を返す(3hレポート統合用)。人は URL を見て OK/NG を記入するだけ。 */
function imageQaPending(){
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(IMAGE_QA_SHEET);
  const waiting=[]; let okCount=0;
  if(sh){ const lr=sh.getLastRow();
    for(let r=2;r<=lr;r++){ const v=sh.getRange(r,1,1,8).getValues()[0];
      const st=String(v[7]).trim();
      if(st==='待ち'){ waiting.push({company:v[1], koma:v[3], url:v[5]}); }
      else if(st==='OK'){ okCount++; }
    }
  }
  return {waiting:waiting, okCount:okCount};
}

/* 12/15/18/21/0時: 直近3hでAIが本番反映/公開したこと(strict) + 画像人QA待ち(人は見てOK/NG返すだけ)。
   エスカレ件数は朝9時ダイジェストに集約。 */
function line3hSummary(){
  const res = computeLine3h();
  const hh = Utilities.formatDate(new Date(),'Asia/Tokyo','HH:mm');
  const q = imageQaPending();
  const p = [];
  if(res.done.length===0){ p.push('【'+hh+' 直近3h】AIの反映はありませんでした。'); }
  else {
    p.push('【'+hh+' 直近3h・AIが本番反映した社】'+res.done.length+'件');
    p.push(res.done.slice(0,20).join('\n'));
    if(res.pendingNewFb.length>0){ p.push('(反映済・新FB対応中'+res.pendingNewFb.length+'件)'); }
  }
  // 画像人QA: 候補を見て OK/NG を返すだけ(OKは次ループが全ゲート付きで自動反映)。
  if(q.waiting.length>0){
    p.push('—\n🖼画像人QA待ち '+q.waiting.length+'件(URLを見てスプシ『画像人QA』にOK/NG記入で自動反映):');
    p.push(q.waiting.slice(0,8).map(function(w){ return '・'+w.company+' コマ'+w.koma+' '+w.url; }).join('\n'));
  }
  if(q.okCount>0){ p.push('(OK済で次ループ反映待ち '+q.okCount+'件)'); }
  _pushLine(p.join('\n'));
}

/* 時刻トリガー設置(既存を消さず重複登録を防ぐ)。1回実行。夜中(3,6時)はなし。 */
function setupTriggers(){
  const want = { 'lineMorningList':[9], 'line3hSummary':[12,15,18,21,0] };
  const exist = ScriptApp.getProjectTriggers();
  const have = {};
  exist.forEach(function(t){
    const fn = t.getHandlerFunction();
    have[fn] = have[fn] || true;
  });
  Object.keys(want).forEach(function(fn){
    // 既存の同名トリガーは一旦削除して作り直し(時刻の重複防止)
    exist.forEach(function(t){ if(t.getHandlerFunction()===fn) ScriptApp.deleteTrigger(t); });
    want[fn].forEach(function(h){
      ScriptApp.newTrigger(fn).timeBased().atHour(h).everyDays(1).inTimezone('Asia/Tokyo').create();
    });
  });
  Logger.log('setupTriggers 完了: 9時=要対応 / 12,15,18,21,0時=直近3h');
}

// roomtabvalidation getRanges fix v2
