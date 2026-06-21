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
    const formulas = (e.parameter.formulas==="1") ? sh.getRange(1,1,Math.min(lr,4),lc).getFormulas() : null;
    return _json({name:e.parameter.sheet, values:vals, formulas:formulas});
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

/* 9時: 要対応リスト */
function lineMorningList(){
  const items = collectAttention();
  const url = SpreadsheetApp.getActiveSpreadsheet().getUrl();
  const byC = {};
  items.forEach(function(it){ byC[it.content]=(byC[it.content]||0)+1; });
  const head = '【おはようございます☀️ 本日の要対応】' + items.length + '件';
  const lines = Object.keys(byC).map(function(k){return '・'+k+': '+byC[k]+'件';});
  const detail = items.slice(0,15).map(function(it){return '└ '+it.content+'/'+it.company;});
  if(items.length>15) detail.push('…他'+(items.length-15)+'件');
  _pushLine([head, lines.join('\n'), detail.join('\n'), url].filter(String).join('\n'));
}

/* 12/15/18/21/0時: 直近3hでAIが反映したこと(反映済かつ最終更新が3h以内) */
function line3hSummary(){
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const since = new Date(Date.now() - 3*60*60*1000);
  const done = [];
  CONFIG.CONTENT_SHEETS.forEach(function(name){
    const sh = ss.getSheetByName(name); if(!sh) return;
    const last = sh.getLastRow(); if(last < CONFIG.FIRST_ROW) return;
    const vals = sh.getRange(CONFIG.FIRST_ROW,1,last-CONFIG.FIRST_ROW+1,45).getValues();
    vals.forEach(function(r){
      const upd = r[CONFIG.COL.最終更新-1];
      let reflected = false;
      for(let n=1;n<=CONFIG.ROUNDS;n++){ if(String(r[hanCol(n)-1]).trim()==='反映済') reflected=true; }
      if(reflected && upd instanceof Date && upd >= since){
        done.push('・'+name+'/'+r[CONFIG.COL.会社名-1]);
      }
    });
  });
  const hh = Utilities.formatDate(new Date(),'Asia/Tokyo','HH:mm');
  if(done.length===0){ _pushLine('【'+hh+' 直近3h】AIの反映はありませんでした。'); return; }
  _pushLine(['【'+hh+' 直近3hでAIが反映】'+done.length+'件', done.slice(0,20).join('\n')].join('\n'));
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
