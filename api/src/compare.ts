// 企業比較: 既存データ(診断attributes + クイズdatasheets)を束ねるだけ。新規生成なし=捏造リスク最小。
// 欠損は null → フロントで「データなし」明示。優劣・順位づけはしない。
import { SHINDAN_ATTRS } from './shindan_data'

const ATTR: Record<string, any> = {}
for (const d of SHINDAN_ATTRS as any[]) ATTR[d.s] = d

// 安定/成長は soft属性(1-5)からの推定 → 傾向バッジ用ラベル
function stabilityLabel(v?: number){ if(typeof v!=='number') return null; return v>=5?'安定重視':v>=4?'やや安定':v>=3?'標準':v>=2?'変化寄り':'変化・成長重視' }
function growthLabel(v?: number){ if(typeof v!=='number') return null; return v>=5?'急成長':v>=4?'成長寄り':v>=3?'標準':v>=2?'成熟寄り':'成熟・安定' }

// datasheet の指定セクションから {text, source} を最大 limit 件抽出(空文字は除外)
function sectionItems(ds: any, title: string, limit: number){
  if(!ds || !Array.isArray(ds.sections)) return null
  const sec = ds.sections.find((s:any)=> s && s.title===title)
  if(!sec || !Array.isArray(sec.items)) return null
  const out = sec.items
    .map((it:any)=>({ text: String(it && it.value || '').trim(), source: (it && it.source_url) || '' }))
    .filter((x:any)=> x.text)
    .slice(0, limit)
  return out.length ? out : null
}

export function bundleCompany(id: string, ds: any){
  const a = ATTR[id]
  if(!a) return { id, found:false }
  const av = a.av, st = a.st
  return {
    id, name: a.n, industry: a.i, found: true,
    has_datasheet: !!ds,
    avg_salary: av ? { text:`約${av.v}万円`, source: av.u || '', as_of: av.a || '' } : null,
    starting_salary: (st && st.v) ? { text:`${Number(st.v).toLocaleString()}円/月`, source: st.u || '' } : null,
    // 推定(傾向バッジ)。soft属性由来なので断定しない。
    trend: {
      note: a.t || '',
      stability: stabilityLabel(a.soft && a.soft.stability),
      growth: growthLabel(a.soft && a.soft.growth),
      estimated: true,
    },
    segments: sectionItems(ds, '事業', 4),   // 事業セグメント(一次情報・出典付)
    culture: sectionItems(ds, '社風', 3),    // 社風・求める人物像
    financials: sectionItems(ds, '財務', 4), // 直近決算の主要数字(期は本文に明記・出典付)
  }
}

export const COMPARE_DISCLAIMER =
  'この比較は公式公開情報（有価証券報告書・決算短信・公式サイト等）と業界傾向に基づく参考情報です。優劣・順位づけではなく、あなた自身が判断するための材料です。「データなし」は非公開・未取得を意味し、推測では埋めていません。'
