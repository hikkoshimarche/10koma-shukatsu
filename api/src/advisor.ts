// advisor.ts — AIキャリアアドバイザーの対話エンジン（バックエンド）
//
// 設計方針（設計書 tokyari_purpose_nav_design より）:
//  ・選択肢型を主、自由入力を従。まず企業と場面を確定 → purpose_map の目的から複数提案（必ず直リンク）。
//  ・ハイブリッド速度設計: 頻出は「定型」（LLM 0回・即応）で返し、外れた自由入力だけ LLM fallback。
//    LLM は「意図分類（purpose/company を選ぶだけ）」に限定 → 事実文を一切生成させない＝Source-or-Silence を構造的に担保。
//  ・制約ガード §4.4:
//     1) AI宣言（初回に名乗る）  2) Source-or-Silence（事実は datasheets の出典付きfactからのみ）
//     3) 合否/適性/倍率の断定禁止（提供するのは準備の材料と手順であって評価ではない）
//     4) 分からないときは分からないと言い、一番近い機能を提案（無理に答えを作らない）
//
// 出力は選択肢(choices)を即座に返す。提案(proposals)は purpose_map の steps を会社スラッグで直リンク化。

type DB = D1Database

// ---- purpose_map.js の写し（Worker はブラウザJSを読めないため）----
// ★ public/purpose_map.js が single source of truth（設計書§2）。同ファイルの SYNC メモに従い
//   id/label/icon/needsCompany/steps(href,note)/next を §2 と完全一致で保つこと（勝手に変えない）。
type Step = { feature: string; href: string; note: string }
type Purpose = { id: string; label: string; icon: string; needsCompany: boolean; steps: Step[]; next: string[] }
export const PURPOSE_MAP: Purpose[] = [
  { id:'know', label:'この会社ってどんな会社？', icon:'🔰', needsCompany:true,
    steps:[
      { feature:'10コマ',       href:'/company?id={slug}',   note:'5分で読める' },
      { feature:'データシート', href:'/datasheet?id={slug}', note:'出典付きの事実' }],
    next:['deep','quiz'] },
  { id:'deep', label:'もっと深く知りたい', icon:'🔎', needsCompany:true,
    steps:[
      { feature:'データシート', href:'/datasheet?id={slug}',           note:'出典付きの事実' },
      { feature:'ニュース',     href:'/company?id={slug}#company-news', note:'最近の動き' },
      { feature:'企業比較',     href:'/compare?add={slug}',            note:'他社と横並び' }],
    next:['es','quiz'] },
  { id:'find', label:'自分に合う会社を探したい', icon:'🧭', needsCompany:false,
    steps:[
      { feature:'相性診断',   href:'/shindan',  note:'まず自己分析' },
      { feature:'業界研究',   href:'/gyokai',   note:'業界を丸ごと' },
      { feature:'企業を探す', href:'/industry', note:'会社を一覧から' }],
    next:['know'] },
  { id:'es', label:'ESを書く', icon:'✍️', needsCompany:true,
    steps:[
      { feature:'ESキット',     href:'/es_kit?id={slug}',    note:'志望動機の材料' },
      { feature:'データシート', href:'/datasheet?id={slug}', note:'裏付けの事実' }],
    next:['mensetsu','deep'] },
  { id:'mensetsu', label:'面接の準備をする', icon:'🎤', needsCompany:true,
    steps:[
      { feature:'ESキット',  href:'/es_kit?id={slug}',    note:'想定質問' },
      { feature:'AI OB訪問', href:'/room?company={slug}', note:'社員に質問' },
      { feature:'クイズ',    href:'/quiz?company={slug}', note:'理解度チェック' }],
    next:['omamori','ob'] },
  { id:'quiz', label:'どれくらい分かっているか試す', icon:'🧠', needsCompany:true,
    steps:[{ feature:'クイズ', href:'/quiz?company={slug}', note:'会社別で腕試し' }],
    next:['mensetsu','deep'] },
  { id:'ob', label:'社員のリアルを聞く', icon:'🚪', needsCompany:true,
    steps:[{ feature:'AI OB訪問ルーム', href:'/room?company={slug}', note:'ぶっちゃけを聞く' }],
    next:['mensetsu','es'] },
  { id:'omamori', label:'緊張をほぐす（本番前）', icon:'🛡️', needsCompany:false,
    steps:[{ feature:'お守り', href:'/omamori.html', note:'本番前に一言' }],
    next:[] },
]
const P = (id: string) => PURPOSE_MAP.find(p => p.id === id)!
const VALID_PURPOSES = new Set(PURPOSE_MAP.map(p => p.id))

// ---- §4.4-1 AI宣言（＋ ルームとの役割の線引きを明示: アドバイザー=運営の道案内／ルーム=社員に聞く）----
const AI_INTRO =
  '私はトーキャリ運営のAIナビゲーターです（実在の特定のアドバイザーではありません）。' +
  'あなたの状況に合わせて、トーキャリの機能への近道をご案内します。合否や向き不向きの判断はしません。' +
  '会社で働くリアル（配属・社風・仕事の実際など）は、社員AIに直接きける「AI OB訪問ルーム」へおつなぎします。'

const DISCLAIMER = '※ 私は機能への道案内役です。会社固有の内情や働くリアルは社員AI「AI OB訪問ルーム」でどうぞ。合否・適性の判断や倍率の提示はしません。'

// 企業固有の話の受け皿＝ルーム。会社が特定できたら常に提案先に含める（役割分担: 内情はルームへ誘導）。
function roomHandoff(slug: string) {
  return { feature: 'AI OB訪問ルーム', label: '🚪 AI OB訪問ルーム',
    href: `/room?company=${encodeURIComponent(slug)}`, note: '配属・働き方など会社のリアルは社員AIへ' }
}

// ---- §4.4-3 断定/倍率ガード（防御的サニタイズ。定型文は元々クリーンだが echo される全文を最終チェック）----
const FORBIDDEN = [
  /向いて(い|ます|る)/, /受かр|受かり|受かる|合格でき/, /落ちр|落ちる|不合格/,
  /難しいです|厳しいです|楽勝/, /\d+\s*倍/, /倍率/, /適性がある|適性が高い/,
]
function guardText(s: string): string {
  let out = s
  for (const re of FORBIDDEN) {
    if (re.test(out)) {
      // 断定表現が混入したら中立文に置換（LLM経路でも事実/評価文は出さない設計だが二重の保険）
      out = out.replace(re, '')
    }
  }
  return out.replace(/\s{2,}/g, ' ').trim()
}

// ---- 会社マッチャ（テキストから会社名を拾う。定型・LLM 0回）----
let _companies: { id: string; name: string; norm: string }[] | null = null
function norm(s: string): string {
  return (s || '')
    .replace(/株式会社|\(株\)|（株）|ホールディングス|ホールディング|グループ|ＨＤ|HD|Holdings|Inc\.?|Corporation|Corp\.?/gi, '')
    .replace(/[\s　・,.，、]/g, '')
    .toLowerCase()
}
async function loadCompanies(db: DB) {
  if (_companies) return _companies
  const { results } = await db.prepare(
    "SELECT id, name FROM companies WHERE id NOT LIKE 'industry_10koma__%'"
  ).all<{ id: string; name: string }>()
  _companies = (results || []).map(r => ({ id: r.id, name: r.name, norm: norm(r.name) }))
  return _companies
}
function matchCompany(text: string, comps: { id: string; name: string; norm: string }[]) {
  const t = norm(text)
  if (!t) return null
  // 正規化した会社名がテキストに含まれる中で、最長一致を採用（三井→三井物産 等の取り違え回避）
  let best: { id: string; name: string } | null = null
  let bestLen = 0
  for (const c of comps) {
    if (c.norm.length >= 2 && t.includes(c.norm) && c.norm.length > bestLen) {
      best = { id: c.id, name: c.name }; bestLen = c.norm.length
    }
  }
  return best
}

// ---- 場面/目的の定型検出（順序 = 具体的なものを先に）----
function detectPurpose(text: string): string | null {
  const t = text
  if (/GD|グループディスカッション|グルディス|ケース/i.test(t)) return 'mensetsu'
  if (/面接|面談|一次|二次|三次|最終選考|最終面接/.test(t)) return 'mensetsu'
  if (/ES|エントリーシート|志望動機|ガクチカ|自己PR|自己ピーアール|書き方|書け/i.test(t)) return 'es'
  if (/OB|OG|社員に|話を聞|訪問/i.test(t)) return 'ob'
  if (/クイズ|理解度|小テスト|問題を解/.test(t)) return 'quiz'
  if (/決算|財務|業績|売上|深く|詳しく|もっと知/.test(t)) return 'deep'
  if (/どんな会社|どういう会社|会社概要|事業内容|どんなとこ|会社のこと|知りたい/.test(t)) return 'know'
  if (/迷って|どこを?受け|どの会社|選び方|決まってな|決まってい?ない|わからない|おすすめの会社/.test(t)) return 'find'
  return null
}
function detectEmotion(text: string): boolean {
  return /不安|緊張|こわ|怖|心配|落ち着か|どうしよ|自信がな|自信ない|やばい|パニック/.test(text)
}

// ---- Source-or-Silence（§4.4-2）:
// アドバイザーは「道案内役」であり、会社固有の事実・内情は自ら語らない（＝ルームと役割を分ける）。
// 事実は datasheet 等の“行き先”を案内するに留め、断定・推定・数字加工は一切しない。これがSoSの最強形。

// ---- LLM fallback（意図分類のみ。事実/評価は生成させない。外れた自由入力の時だけ）----
async function llmClassify(text: string, comps: { id: string; name: string }[], apiKey: string):
  Promise<{ purpose: string | null; company: string | null } | null> {
  const sys =
    'あなたは就活ナビの意図分類器です。ユーザーの入力を、次の8つの目的IDのいずれか1つに分類します。' +
    'know(会社を知る)/deep(深く知る)/find(会社を選ぶ・迷い)/es(ES作成)/mensetsu(面接・GD)/quiz(理解度)/ob(OB訪問)/omamori(不安・緊張)。' +
    '入力に会社名があれば会社名も返します。事実・評価・合否・倍率は一切書かないこと。' +
    '出力は必ず JSON のみ: {"purpose":"<id or null>","company":"<会社名 or null>"}'
  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01', 'x-api-key': apiKey },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5', max_tokens: 200, system: sys,
        messages: [{ role: 'user', content: text }],
      }),
    })
    if (!res.ok) return null
    const data = await res.json<{ content: Array<{ type: string; text: string }> }>()
    const raw = data.content.find(b => b.type === 'text')?.text ?? ''
    const m = raw.match(/\{[\s\S]*\}/)
    if (!m) return null
    const j = JSON.parse(m[0]) as { purpose?: string; company?: string }
    const purpose = j.purpose && VALID_PURPOSES.has(j.purpose) ? j.purpose : null
    let company: string | null = null
    if (j.company) {
      const hit = matchCompany(j.company, _companies || [])
      company = hit ? hit.id : null
    }
    return { purpose, company }
  } catch { return null }
}

// ---- 提案の直リンク化 ----
function proposalsFor(purposeId: string, slug: string | null) {
  const p = P(purposeId)
  return p.steps.map(s => ({
    feature: s.feature,
    label: `${p.icon} ${s.feature}`,
    href: slug ? s.href.replace('{slug}', encodeURIComponent(slug)) : s.href,
    note: s.note,
  }))
}
function nextChoices(purposeId: string, slug: string | null) {
  return P(purposeId).next.map(nid => ({
    label: `${P(nid).icon} ${P(nid).label}`,
    value: { purpose: nid, company: slug || undefined },
    kind: 'next' as const,
  }))
}

// 場面（company確定・purpose未確定）の選択肢
function sceneChoices(slug: string) {
  const mk = (label: string, purpose: string) => ({ label, value: { company: slug, purpose }, kind: 'scene' as const })
  return [
    mk('🎤 GD・面接の準備', 'mensetsu'),
    mk('✍️ ES提出（志望動機など）', 'es'),
    mk('🚪 OB・OG訪問', 'ob'),
    mk('🔰 どんな会社か知りたい', 'know'),
    mk('🧭 まだ決まっていない', 'know'),
  ]
}
// エントリー/未特定時の目的選択肢
function onboardingChoices() {
  const mk = (purpose: string) => ({ label: `${P(purpose).icon} ${P(purpose).label}`, value: { purpose }, kind: 'purpose' as const })
  return [mk('know'), mk('mensetsu'), mk('es'), mk('find'), mk('omamori')]
}

export async function handleAdvisor(c: any) {
  let body: any = {}
  try { body = await c.req.json() } catch { body = {} }
  const first = !!body.first
  const text = String(body.text || '').trim()
  const comps = await loadCompanies(c.env.DB)

  // 1) 会社解決: テキストからの検出を優先（話題転換に追随）、無ければ引き継ぎ値
  let slug: string | null = null
  let cname: string | null = null
  const tHit = text ? matchCompany(text, comps) : null
  if (tHit) { slug = tHit.id; cname = tHit.name }
  else if (body.company && typeof body.company === 'string') { slug = body.company; cname = comps.find(x => x.id === slug)?.name ?? null }

  // 2) 目的解決: テキストからの検出を優先、無ければ引き継ぎ値
  const emotion = detectEmotion(text)
  const tPurpose = text ? detectPurpose(text) : null
  let purpose: string | null = tPurpose || (body.purpose && VALID_PURPOSES.has(body.purpose) ? body.purpose : null)

  // 3) LLM fallback（company も purpose も未解決の自由入力のときだけ）
  let matched: 'template' | 'llm' | 'clarify' = 'template'
  let llm_used = false
  if (text && !slug && !purpose) {
    const cls = await llmClassify(text, comps, c.env.ANTHROPIC_API_KEY)
    if (cls && (cls.purpose || cls.company)) {
      if (cls.company) { slug = cls.company; cname = comps.find(x => x.id === slug)?.name ?? null }
      if (cls.purpose) purpose = cls.purpose
      matched = 'llm'; llm_used = true
    }
  }
  if (!purpose && emotion) purpose = 'omamori'

  // 4) レスポンス構築
  const resp: any = {
    choices: [], proposals: [], disclaimer: DISCLAIMER,
    meta: { company: slug, company_name: cname, purpose, matched, llm_used },
  }
  if (first) resp.ai_intro = AI_INTRO
  const reassure = emotion ? '大丈夫です、一緒に準備を整えましょう。' : ''

  const p = purpose ? P(purpose) : null

  if (p && (!p.needsCompany || slug)) {
    // A) 目的確定・会社要件も満たす → 機能への直リンク＋次の一歩（※内情は語らずルームへ誘導）
    const who = slug && cname ? `${cname}の` : ''
    resp.message = guardText(`${reassure}${who}「${p.label}」ですね。ここから直接ひらけます。`)
    resp.proposals = proposalsFor(p.id, slug)
    // 役割分担: 会社が特定できていて、まだルーム導線が無ければ「会社のリアルは社員AIへ」を必ず添える
    if (slug && !resp.proposals.some((x: any) => /\/room\?/.test(x.href))) {
      resp.proposals.push(roomHandoff(slug))
    }
    resp.choices = nextChoices(p.id, slug)
    if (emotion && p.id !== 'omamori') {
      resp.proposals.push({ feature: 'お守り', label: '🛡️ お守り', href: '/omamori.html', note: '本番前の不安に、そっとひと言' })
    }
  } else if (p && p.needsCompany && !slug) {
    // B) 目的は決まったが会社が要る → 会社を聞く（自由入力・従）
    resp.message = guardText(`${reassure}「${p.label}」ですね。どの会社について準備しますか？会社名を入力してください。`)
    resp.free_input_hint = '会社名を入力（例：三井物産）'
    resp.choices = [{ label: '🧭 受ける会社がまだ決まっていない', value: { purpose: 'find' }, kind: 'purpose' }]
    if (emotion) resp.proposals = proposalsFor('omamori', null)
  } else if (slug && !p) {
    // C) 会社は確定・場面が未確定 → 場面を聞く（選択肢・主）
    resp.message = guardText(`${reassure}${cname}ですね。何を準備しますか？`)
    resp.choices = sceneChoices(slug)
    resp.free_input_hint = 'やりたいことを入力（例：面接の準備）'
  } else {
    // D) 会社も目的も未特定
    if (emotion) {
      resp.message = guardText('大丈夫です。まずは気持ちを落ち着けて、できる準備から一緒に進めましょう。')
      resp.proposals = proposalsFor('omamori', null)
      resp.choices = [
        { label: '🎤 面接・GDの準備をする', value: { purpose: 'mensetsu' }, kind: 'purpose' },
        { label: '🧭 受ける会社を選ぶ', value: { purpose: 'find' }, kind: 'purpose' },
      ]
    } else {
      // §4.4-4 分からないときは正直に + 一番近い機能へ
      resp.message = text
        ? 'うまく汲み取れませんでした。近いものを選んでください。会社名を入れてもらえれば、その会社のページへ直接ご案内します。'
        : 'こんにちは。会社名や、やりたいこと（会社を知る・ES・面接・迷っている 等）を教えてください。'
      resp.message = guardText(resp.message)
      resp.choices = onboardingChoices()
      resp.free_input_hint = '会社名 or やりたいこと（例：三井物産、面接の準備）'
      if (matched !== 'llm') matched = 'clarify'
      resp.meta.matched = matched
    }
  }
  return c.json(resp)
}
