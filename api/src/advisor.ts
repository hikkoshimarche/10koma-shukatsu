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

// ---- R1【安全・最優先】危機シグナルの決定論検出（LLM分類の前段・機能ルーティングから外す専用経路）----
// 明示的な希死念慮・自傷 + 周辺表現を拾う。就活の「つらい/落ち込む/しんどい/疲れた」程度は拾わない（通常フロー）。
// 第1段: 決定論キーワード（日本語＋英語を対称に守る。英語をLLM任せにしない）。iフラグで英語は大小文字無視。
const CRISIS_RE = new RegExp([
  // --- 日本語 ---
  '死にたい', '死んでしまいたい', 'しにたい', '死のうか?', '自殺', '首を(つ|吊)',
  '飛び降り', '飛びおり', 'リストカット', 'リスカ', '手首を切', '自傷', '過剰摂取', 'オーバードーズ',
  '消えたい', '消えてしまいたい', '消えてなくなりたい', 'きえたい', 'いなくなりたい', 'この世から(いなく|消え)',
  '生きていたくない', '生きてても', '生きてる意味', '生きている意味', '生きる(意味|価値)がない',
  '生きるのをやめ', 'もう生きて(いけ|られ)', '(もう)?終わりにしたい', '消えてしまお',
  // --- 日本語の遠回し表現（時が過ぎてほしくない／存在を消したい系。就活の愚痴に紛れやすいが、誤発火は後段のやわらかい初手で吸収） ---
  '明日が(来|こ)(なけれ|ないで|てほしくな)', '明日なんて(来|こ)(なけれ|ないで)', 'このまま(朝|明日)が(来|こ)なけれ',
  '朝が(来|こ)(なけれ|ないで|てほしくな)', '目が覚め(なけれ|ないで)', '(もう)?目を覚ましたくない',
  'いなくなった方が(いい|まし|楽)', 'いない方が(いい|まし|楽|みんな)', '自分がいない方', '私(も|なんて)終わりに',
  // --- 英語（先頭\\bのみ。末尾に\\bを付けると self-harm[ing] 等の語形変化を取りこぼす＝Fの穴。時制/省略形を系統展開） ---
  "\\b(do ?n'?t|do not|dont) want to (be alive|live)", '\\bno longer want to (be alive|live)',
  '\\bwant(ing|ed|s)? to die', '\\bwanna die', '\\bwish (i )?(was|were) dead',
  '\\bkill(ing|ed|s)? myself', '\\bhurt(ing|s)? myself', '\\bcut(ting|s)? (myself|my wrist)',
  '\\bself[ -]?harm(ing|ed|s)?', '\\btake (my )?(own )?life', '\\bend(ing|ed|s)? (my life|it all)',
  "\\b(can'?t|cannot|can ?not|couldn'?t|could ?not) go on",
  '\\bno reason to (live|be alive)', '\\bwant(ing|ed)? to disappear', '\\bsuicid(e|al)',
].join('|'), 'i')
// 相談窓口は公式ページから実取得した値のみ（Source-or-Silence厳守・番号/受付時間は記憶で書かない）。
// 受付時間の裏取り: #いのちSOS の電話は運営ライフリンク公式で「毎日24時間 受付中」(https://www.lifelink.or.jp/inochisos/)。
//   ※時間限定なのは同窓口のチャット(月金6:00-22:30/日火水木土8:00-22:30)であり電話ではない。
//   よりそいホットラインは厚労省「まもろうよ こころ」で24時間対応。こころの健康相談統一ダイヤルは地域で時間が異なる→注記。
const CRISIS_SOURCE = 'https://www.mhlw.go.jp/mamorouyokokoro/'
const CRISIS_SUPPORT = [
  { label: '#いのちSOS（電話・24時間・通話料無料）', tel: '0120-061-338' },
  { label: 'よりそいホットライン（電話・24時間・通話料無料）', tel: '0120-279-338' },
  { label: 'こころの健康相談統一ダイヤル', tel: '0570-064-556', note: '受付時間は地域により異なります' },
  { label: '文字で相談したいとき（SNS相談の窓口一覧・厚労省）', href: 'https://www.mhlw.go.jp/mamorouyokokoro/soudan/sns/' },
]
// 切迫時は窓口(これから相談する人向け)では届かない → 119 を窓口リストの後に短く。
const CRISIS_EMERGENCY = 'いますぐ強い危険を感じているときは、ためらわず 119 に連絡してください。'
// ★R1応答文面（デプロイ前にオスカー承認）: 受け止め(1回)→AIだから人へ委ねる明示→選べる形で窓口→急かさない。断定(匿名/秘密保証)しない・短く温かく。
// 初手はやわらかく（誤発火した学生を驚かせない）。断定的な安心の約束・守秘/対応の保証は書かない。
const CRISIS_MESSAGE =
  'ふと気になって、声をかけますね。大丈夫ですか。\n' +
  'つらいことがあったのかもしれません。ひとりで抱えこまないでほしいと思っています。\n' +
  '私はAIなので、ここから先はあなたの話を人が受け止めてくれる窓口に頼ってほしいです。よければ下の窓口へ。急がなくてかまいません。'
// 危機検出後の同一セッションで続けて話しかけられたときの継続文面（機能案内には戻さない）。
const CRISIS_MESSAGE_CONT =
  '聞いています。ひとりで抱えこまないで。\n' +
  '私はAIなので、ここから先は下の窓口の人に話してみてほしいです。いつ連絡しても大丈夫です。'

// 窓口・119・出典を message 本文にも必ず含める（構造化 support を描画しないクライアントでも確実に見えるように）。
function crisisMessage(cont: boolean): string {
  const lead = cont ? CRISIS_MESSAGE_CONT : CRISIS_MESSAGE
  const wins = CRISIS_SUPPORT.map(s => s.tel
    ? `・${s.label}\n　${s.tel}${(s as any).note ? '（' + (s as any).note + '）' : ''}`
    : `・${s.label}\n　${s.href}`).join('\n')
  return `${lead}\n\n【相談窓口】\n${wins}\n\n${CRISIS_EMERGENCY}\n\n出典：厚生労働省「まもろうよ こころ」\n${CRISIS_SOURCE}`
}
// ---- 危機セッションのサーバ側二重化（必須2）----
// クライアントの crisis_mode フラグに100%依存させない。サーバに「sid が直近◯分に危機応答を受けた」
// 事実と時刻だけを持つ（本文は絶対に残さない）。クライアントフラグ or サーバ状態の**どちらか**で危機モード維持。
const CRISIS_TTL_MS = 30 * 60 * 1000
async function recordCrisis(db: DB, sid: string) {
  const now = Date.now()
  try {
    await db.prepare('INSERT OR REPLACE INTO advisor_crisis_sessions (sid, last_crisis_at) VALUES (?, ?)').bind(sid, now).run()
    await db.prepare('DELETE FROM advisor_crisis_sessions WHERE last_crisis_at < ?').bind(now - CRISIS_TTL_MS).run() // 肥大防止(本文なし)
  } catch {}
}
async function recentServerCrisis(db: DB, sid: string): Promise<boolean> {
  try {
    const row = await db.prepare('SELECT last_crisis_at FROM advisor_crisis_sessions WHERE sid = ?')
      .bind(sid).first<{ last_crisis_at: number }>()
    return !!row && (Date.now() - row.last_crisis_at) < CRISIS_TTL_MS
  } catch { return false }
}
// 学生が明示的に「就活の相談に戻る」を選んだときだけサーバ側状態を消す（自動では消さない＝安全側）。
async function clearCrisis(db: DB, sid: string) {
  try { await db.prepare('DELETE FROM advisor_crisis_sessions WHERE sid = ?').bind(sid).run() } catch {}
}

// 危機専用応答（機能ルーティング一切なし）。cont=継続ターン, viaLLM=第2段LLMで検出。
function crisisResponse(c: any, cont: boolean, viaLLM: boolean) {
  try { console.log(`[advisor] crisis-path served (${viaLLM ? 'llm' : cont ? 'mode' : 'kw'}; body not logged)`) } catch {}
  return c.json({
    crisis: true, crisis_mode: true,
    message: crisisMessage(cont),
    support: CRISIS_SUPPORT, emergency: CRISIS_EMERGENCY, source: CRISIS_SOURCE,
    // 機能へのルーティングはしないが、就活の相談に戻りたい学生のための明示的な導線だけ1つ残す
    // （自動では戻さない＝安全側。押したときだけサーバ側状態も消す）。
    choices: [{ label: '🗒 就活の相談に戻る', value: { resume: true }, kind: 'resume' }], proposals: [],
    disclaimer: '※ 出典：厚生労働省「まもろうよ こころ」' + CRISIS_SOURCE,
    meta: { matched: 'crisis', llm_used: viaLLM, company: null, purpose: null },
  })
}

// ---- R2: ascii/ローマ字・英語入力は会社照合の確信度が低い（誤解決は未解決より有害）→ テキストからは会社を取らない ----
function asciiDominant(s: string): boolean {
  if (!s) return false
  const hasJP = /[぀-ヿ一-鿿ぁ-んァ-ヶ々〆ヵヶ]/.test(s)
  const hasAlpha = /[A-Za-z]/.test(s)
  return hasAlpha && !hasJP
}

// ---- Source-or-Silence（§4.4-2）:
// アドバイザーは「道案内役」であり、会社固有の事実・内情は自ら語らない（＝ルームと役割を分ける）。
// 事実は datasheet 等の“行き先”を案内するに留め、断定・推定・数字加工は一切しない。これがSoSの最強形。

// ---- LLM fallback（意図分類のみ。事実/評価は生成させない。外れた自由入力の時だけ）----
async function llmClassify(text: string, comps: { id: string; name: string }[], apiKey: string):
  Promise<{ purpose: string | null; company: string | null } | null> {
  const sys =
    'あなたは就活ナビの意図分類器です。ユーザーの入力を、次の目的IDのいずれか1つに分類します。' +
    'crisis / know(会社を知る)/deep(深く知る)/find(会社を選ぶ・迷い)/es(ES作成)/mensetsu(面接・GD)/quiz(理解度)/ob(OB訪問)/omamori(不安・緊張)。' +
    // 第2段の危機検出（最優先）: 遠回し・絵文字・外国語も拾う。過検出は許容。
    '【最優先】crisis は他のどの分類よりも優先する。入力が「死にたい・消えたい・いなくなりたい・生きていたくない・自分を傷つけたい・自傷・もう終わりにしたい」、' +
    '英語なら "I don\'t want to live" "I want to die" "kill myself" "end my life/it all" "no reason to live" "I can\'t go on" 等、' +
    '自分の生存や存在をやめたい／自分を害したい気持ちに、直接でも遠回しでも、絵文字でも、どの言語（日本語・英語・中国語・韓国語など）でも触れていれば、必ず crisis にする。少しでも迷ったら crisis に倒す。' +
    '同じ文に就活の話（"job hunting broke me" 等）が混ざっていても、生存・自傷のシグナルがあれば ob 等ではなく crisis を最優先にすること。' +
    '特に self-harm 系（self-harm / self-harming / cut myself / cutting myself / hurt myself 等、語形変化・時制を含む）は、どんな文脈でも最優先で crisis にする。' +
    '日本語の遠回し表現も同様に crisis：「明日が来てほしくない」「明日が来なければ」「朝が来なければ」「朝目が覚めなければ」「目が覚めないでほしい」' +
    '「自分がいない方がみんな楽」「いなくなった方がいい」「親に申し訳ないから、もういい」「就活が終わったら私も終わりにします」——これらは全て crisis として扱う。' +
    'ただし、単なる就活の落ち込み（"就活がつらい""しんどい""疲れた""落ちて落ち込む""不安"、英語なら "job hunting is so hard" "I\'m exhausted" "I\'m so tired" 程度）で、生存・自傷に触れていないものは crisis ではない（通常の分類か null）。' +
    // R3: それ以外で迷ったら omamori に寄せない。判別できなければ null。
    'crisis でない場合、確信が持てない・就活の意図として判別できない・外国語で意図が不明なときは purpose を null にする（omamori 等へ無理に寄せない）。' +
    'omamori は「本人が不安・緊張・落ち着かないと述べている」ときだけ。合否・倍率・採用確率・競争率を問う質問は omamori ではなく null。' +
    // R2: 英語・ローマ字・略称は確信が持てなければ会社を返さない。
    '会社名は、日本語で明示され確実に特定できるときだけ company に入れる。英語・ローマ字・略称・愛称で少しでも確信が持てなければ company は null。' +
    '事実・評価・合否・倍率は一切書かないこと。出力は必ず JSON のみ: {"purpose":"<id or crisis or null>","company":"<日本語の会社名 or null>"}'
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
    const purpose = j.purpose === 'crisis' ? 'crisis'
      : (j.purpose && VALID_PURPOSES.has(j.purpose) ? j.purpose : null)
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

  // ★R1【最優先・安全】危機シグナル検出は最前段（会社/目的解決・LLM分類より前）。
  // 検出したら機能ルーティングを一切せず（お守りにも回さない）専用経路で返す。
  // さらに、一度危機を検出したセッションでは以降 crisis_mode を維持し、続けて話しかけられても
  // 機能案内フローに戻さない（クライアントが crisis_mode:true を送り続ける）。
  const sid = (typeof body.sid === 'string' && body.sid) ? body.sid.slice(0, 64) : null

  // 学生が明示的に「就活の相談に戻る」を選んだ場合のみ、サーバ側の危機状態を消して通常フローへ戻す（自動では戻さない）。
  if (body.resume === true && sid) await clearCrisis(c.env.DB, sid)

  // 第1段: 決定論キーワード（即時・確実）。危機語があれば resume より常に優先。
  // それ以外は crisis_mode フラグ or サーバ側の直近記録で維持（resume 選択時は維持しない）。
  const crisisHit = !!text && CRISIS_RE.test(text)
  if (crisisHit || (body.crisis_mode === true && body.resume !== true)) {
    // ★入力本文は一切ログ/DB/LLMに残さない（最前段returnでAnthropicにもDBにも渡らない・事実のみ記録）。
    if (sid) await recordCrisis(c.env.DB, sid)   // サーバ側にも「危機だった事実＋時刻」を記録（本文なし）
    return crisisResponse(c, body.crisis_mode === true && !crisisHit, false)
  }
  // 二重化: クライアントがフラグを落としても、サーバに直近の危機記録があれば危機モードを維持（機能へ流さない）。
  if (body.resume !== true && sid && await recentServerCrisis(c.env.DB, sid)) {
    return crisisResponse(c, true, false)
  }

  const comps = await loadCompanies(c.env.DB)
  const asciiText = asciiDominant(text)  // R2: ローマ字/英語入力は会社照合の確信度が低い

  // 1) 会社解決: テキストからの検出を優先（話題転換に追随）、無ければ引き継ぎ値。ただし ascii入力からは取らない（誤解決回避）。
  let slug: string | null = null
  let cname: string | null = null
  const tHit = (text && !asciiText) ? matchCompany(text, comps) : null
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
    // 第2段: LLMが危機と判定したら、キーワードで拾えなかった遠回し・絵文字・外国語も専用応答へ（機能に流さない）。
    if (cls && cls.purpose === 'crisis') {
      if (sid) await recordCrisis(c.env.DB, sid)
      return crisisResponse(c, false, true)
    }
    if (cls && (cls.purpose || cls.company)) {
      // R2: ascii/ローマ字入力では LLM の会社解決も採用しない（黙って別社に送らない＝聞き返す）
      if (cls.company && !asciiText) { slug = cls.company; cname = comps.find(x => x.id === slug)?.name ?? null }
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
