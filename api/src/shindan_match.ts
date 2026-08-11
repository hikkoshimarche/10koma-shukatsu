// shindan/matching.py の決定論マッチングを移植（AI課金なし・即応答）。
import { SHINDAN_QUESTIONS as QS, SHINDAN_ATTRS } from './shindan_data'

const QBYID: Record<string, any> = {}
for (const q of QS as any[]) QBYID[q.id] = q
const MISSING_SALARY_SCORE = 0.25

// 根拠可視化(バー表示)用の軸ラベル。総合%は各軸の重み付き平均であることを学生に見せるため、
// 回答された各軸の一致度(0..1)を rationale.axes として返す。ラベルは質問idごとの短名。
const AXIS_LABELS: Record<string,string> = {
  q_salary_wlb:'年収・働き方', q_kaigai:'海外志向', q_tenkin:'転勤', q_stability:'安定/成長',
  q_growth:'成長性', q_remote:'柔軟な働き方', q_young:'若手裁量', q_bunri:'文理適性',
  q_jobtags:'希望職種', q_salary_avg:'年収志向', q_salary_start:'初任給',
}

function avgBand(man: number){ for (const [thr,b] of [[1200,5],[900,4],[700,3],[550,2]]) if (man>=thr) return b; return 1 }
function startBand(yen: number){ for (const [thr,b] of [[280000,5],[250000,4],[220000,3],[200000,2]]) if (yen>=thr) return b; return 1 }
function closeness(v: number, t: number){ return 1.0 - Math.abs(v - t)/4.0 }

function sel(answers: any, qid: string){
  if (!(qid in answers)) return []
  const v = answers[qid]; const idxs = Array.isArray(v) ? v : [v]
  const opts = QBYID[qid].options
  return idxs.filter((i:number)=> i>=0 && i<opts.length).map((i:number)=> opts[i])
}
function why(q: any, opt: any){ return `${String(q.text).replace(/[？?]+$/,'')}→「${opt.label}」に合致` }

// 決定論tie-breaker(0〜eps)。md5の代わりに決定論ハッシュ（同点社を回答依存で入替＝全社に登場チャンス）。
function detHash(s: string){ let h=2166136261>>>0; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619)>>>0 } return h }
function tiebreak(slug: string, answers: any, eps: number){
  if (!eps) return 0.0
  const key = JSON.stringify(answers, Object.keys(answers).sort()) + '|' + slug
  return (detHash(key) % 100000) / 100000.0 * eps
}

function scoreCompany(d: any, answers: any){
  let wsum=0, acc=0; const matched:string[]=[]; const meta:any={missing_salary_pref:false}
  const axesArr:{key:string,m:number}[]=[]   // 回答された各軸の一致度(0..1)。根拠バー表示用(総合s=これらの重み付き平均)。
  const soft = d.soft || {}
  for (const q of QS as any[]){
    const opts = sel(answers, q.id); if (!opts.length) continue
    const w = q.weight ?? 1.0; const kind = q.kind
    if (kind==='soft'){
      const target = opts[0].target; if (target==null) continue
      const v = soft[q.attr]; if (typeof v!=='number') continue
      const m = closeness(v, target); acc+=w*m; wsum+=w; axesArr.push({key:q.id,m})
      if (m>=0.75) matched.push(why(q,opts[0]))
    } else if (kind==='salary_avg'){
      const target = opts[0].target; if (target==null) continue
      const av = d.av
      if (av){ const m=closeness(avgBand(av.v),target); acc+=w*m; wsum+=w; axesArr.push({key:q.id,m}); if(m>=0.75) matched.push(`年収志向に合致(平均年収${av.v}万円)`) }
      else if (target>=4){ acc+=w*MISSING_SALARY_SCORE; wsum+=w; axesArr.push({key:q.id,m:MISSING_SALARY_SCORE}); meta.missing_salary_pref=true }
    } else if (kind==='salary_start'){
      const target = opts[0].target; if (target==null) continue
      const st = d.st
      if (st){ const m=closeness(startBand(st.v),target); acc+=w*m; wsum+=w; axesArr.push({key:q.id,m}); if(m>=0.75) matched.push(`初任給重視に合致`) }
      else if (target>=4){ acc+=w*MISSING_SALARY_SCORE; wsum+=w; axesArr.push({key:q.id,m:MISSING_SALARY_SCORE}) }
    } else if (kind==='salary_wlb'){
      const tgt = opts[0].target || {}
      let axM:number|null=null
      if (tgt.salary){
        const sT = tgt.salary; const av = d.av
        if (av){ const m=closeness(avgBand(av.v),sT); acc+=w*m; wsum+=w; axM=m; if(m>=0.75) matched.push(`年収志向に合致(平均年収${av.v}万円)`) }
        else if (sT>=4){ acc+=w*MISSING_SALARY_SCORE; wsum+=w; axM=MISSING_SALARY_SCORE; meta.missing_salary_pref=true }
        const st = d.st
        if (st){ const m2=closeness(startBand(st.v),sT); acc+=w*0.5*m2; wsum+=w*0.5; if(axM==null) axM=m2 }
      } else if (tgt.wlb){
        const wT = tgt.wlb; const v = soft.remote_flex
        if (typeof v==='number'){ const m=closeness(v,wT); acc+=w*m; wsum+=w; axM=m; if(m>=0.75) matched.push('柔軟な働き方(WLB)を重視する傾向に合致') }
      }
      if (axM!=null) axesArr.push({key:q.id,m:axM})
    } else if (kind==='bunri'){
      const target = opts[0].target; if (target==null) continue
      const v = soft.bunri; if (!v) continue
      const m = v===target ? 1.0 : (v==='文理両方' ? 0.6 : 0.2); acc+=w*m; wsum+=w; axesArr.push({key:q.id,m})
    } else if (kind==='tags'){
      const want = new Set<string>(); for (const o of opts) if (o.target) o.target.forEach((x:string)=>want.add(x))
      if (!want.size) continue
      const have = new Set<string>(soft.job_tags || []); if (!have.size) continue
      const inter = [...want].filter(x=>have.has(x)); const m = Math.min(1.0, inter.length/Math.max(1,want.size))
      acc+=w*m; wsum+=w; axesArr.push({key:q.id,m}); if (inter.length) matched.push(`希望職種と重なり(${inter.sort().join('・')})`)
    }
    // 注: kind==='industry'(「気になる業界」)は相性%の計算から意図的に除外(学生FB: 気になる業界≠向いている業界)。
    // 設問自体を SHINDAN_QUESTIONS から削除済のため到達しないが、万一データが戻っても加点しないようブランチも撤去。

  }
  if (wsum===0) return { s:0.0, matched:[], meta, axes:[] }
  return { s: acc/wsum, matched, meta, axes: axesArr }
}

function rationale(d: any, matched: string[], meta: any, axes: {key:string,m:number}[]=[]){
  // axes: 回答された各軸の一致度(0..1)。総合%の内訳を学生に見せる根拠バー用。一致度の高い順。
  const axesOut = (axes||[])
    .map(a=>({ label: AXIS_LABELS[a.key]||a.key, score: Math.round(a.m*100)/100 }))
    .sort((a,b)=> b.score - a.score)
  const r:any = { trend: d.t||'', matched: matched.slice(0,4), facts:{}, notes:[], axes: axesOut }
  if (d.av) r.facts.avg_salary = { text:`平均年収 約${d.av.v}万円`, source:d.av.u||'', as_of:d.av.a||'' }
  else if (meta && meta.missing_salary_pref) r.notes.push('年収データなし（出典のある平均年収が非公開のため、年収面は参考程度に）')
  if (d.st) r.facts.starting_salary = { text:`初任給 ${d.st.v.toLocaleString()}円/月`, source:d.st.u||'' }
  return r
}

export function recommend(answers: any, topCompanies=8, topIndustries=5, tiebreakEps=0.01){
  const scored = (SHINDAN_ATTRS as any[]).map(d=>{
    const { s, matched, meta, axes } = scoreCompany(d, answers)
    return { sortKey: s + tiebreak(d.s, answers, tiebreakEps), s, matched, meta, axes, d }
  })
  scored.sort((a,b)=> b.sortKey - a.sortKey)
  const comps = scored.slice(0, topCompanies).map(({s,matched,meta,axes,d})=>({
    name:d.n, slug:d.s, industry:d.i, score:Math.round(s*1000)/1000,
    low_signal:(axes?.length||0) < 2,   // 加点軸が1つ以下=「こだわらない」中心。UIで%を過信表示させない honest フラグ。
    rationale:rationale(d,matched,meta,axes)
  }))
  const indAcc: Record<string, number[]> = {}
  for (const {s,d} of scored){ (indAcc[d.i] ||= []).push(s) }
  const indRank = Object.entries(indAcc).map(([k,v])=>({ industry:k, score:Math.round(v.reduce((a,b)=>a+b,0)/v.length*1000)/1000, n:v.length }))
  indRank.sort((a,b)=> b.score - a.score)
  return {
    top_industries: indRank.slice(0, topIndustries),
    top_companies: comps,
    disclaimer: 'この診断は公式公開情報と業界傾向に基づく参考提案です。断定・優劣付けではありません。',
    answered: (QS as any[]).filter(q=> q.id in answers).length,
  }
}
