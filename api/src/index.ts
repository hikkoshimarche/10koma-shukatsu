import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { recommend } from './shindan_match'
import { bundleCompany, COMPARE_DISCLAIMER } from './compare'

type Bindings = {
  DB: D1Database
  ASSETS: R2Bucket
  TTS_CACHE: R2Bucket
  ANTHROPIC_API_KEY: string
  GOOGLE_TTS_API_KEY: string
}

const app = new Hono<{ Bindings: Bindings }>()

app.use('*', cors())

// ヘルスチェック
app.get('/api/health', (c) => {
  return c.json({ ok: true })
})

// ユーザーのupsert
app.post('/api/users/upsert', async (c) => {
  const { line_user_id, display_name, picture_url } = await c.req.json<{
    line_user_id: string
    display_name?: string
    picture_url?: string
  }>()

  if (!line_user_id) {
    return c.json({ error: 'line_user_id is required' }, 400)
  }

  await c.env.DB.prepare(
    `INSERT INTO users (line_user_id, display_name, picture_url, updated_at)
     VALUES (?, ?, ?, datetime('now'))
     ON CONFLICT (line_user_id) DO UPDATE SET
       display_name = excluded.display_name,
       picture_url  = excluded.picture_url,
       updated_at   = excluded.updated_at`
  )
    .bind(line_user_id, display_name ?? null, picture_url ?? null)
    .run()

  return c.json({ ok: true })
})

// 業種一覧
app.get('/api/industries', async (c) => {
  const { results } = await c.env.DB.prepare(
    'SELECT * FROM industries ORDER BY id'
  ).all()
  return c.json(results)
})

// 業界研究10コマ詳細 (industry_10koma__<slug> の疑似会社+company_panels を返す)
// フロント company.html renderIndustry は { panels: [...] } を期待。未反映時は404→クイズ導線にフォールバック。
app.get('/api/industries/:slug', async (c) => {
  const slug = c.req.param('slug')
  const companyId = `industry_10koma__${slug}`

  const industry = await c.env.DB.prepare(
    'SELECT * FROM companies WHERE id = ?'
  )
    .bind(companyId)
    .first<{ id: string; name: string; industry_id: string }>()

  if (!industry) {
    return c.json({ error: 'not found', slug }, 404)
  }

  const { results: panels } = await c.env.DB.prepare(
    'SELECT * FROM company_panels WHERE company_id = ? ORDER BY panel_num'
  )
    .bind(companyId)
    .all()

  return c.json({ slug, name: industry.name, industry_id: industry.industry_id, panels })
})

// 会社一覧
app.get('/api/companies', async (c) => {
  const { results } = await c.env.DB.prepare(
    'SELECT * FROM companies ORDER BY id'
  ).all()
  return c.json(results)
})

// 会社詳細
app.get('/api/companies/:id', async (c) => {
  const id = c.req.param('id')
  const userId = c.req.query('user_id') ?? null

  const company = await c.env.DB.prepare(
    'SELECT * FROM companies WHERE id = ?'
  )
    .bind(id)
    .first<{ id: string; industry_id: string; [key: string]: unknown }>()

  if (!company) {
    return c.json({ error: 'not found' }, 404)
  }

  const { results: panels } = await c.env.DB.prepare(
    'SELECT * FROM company_panels WHERE company_id = ? ORDER BY panel_num'
  )
    .bind(id)
    .all()

  const { results: recommendations } = await c.env.DB.prepare(
    `SELECT id, name, description, thumbnail_url
     FROM companies
     WHERE industry_id = ? AND id != ?
     ORDER BY id
     LIMIT 5`
  )
    .bind(company.industry_id, id)
    .all()

  let liked = false
  let bookmarked = false
  let likedPanels: number[] = []

  if (userId) {
    const likeRow = await c.env.DB.prepare(
      `SELECT 1 FROM likes WHERE line_user_id = ? AND content_type = 'company' AND content_id = ?`
    ).bind(userId, id).first()
    liked = !!likeRow

    const bookmarkRow = await c.env.DB.prepare(
      'SELECT 1 FROM bookmarks WHERE line_user_id = ? AND company_id = ?'
    ).bind(userId, id).first()
    bookmarked = !!bookmarkRow

    const { results: panelLikes } = await c.env.DB.prepare(
      `SELECT content_id FROM likes
       WHERE line_user_id = ? AND content_type = 'panel' AND content_id LIKE ?`
    ).bind(userId, `${id}:%`).all<{ content_id: string }>()

    likedPanels = panelLikes
      .map((r) => Number((r.content_id as string).split(':')[1]))
      .filter((n) => !isNaN(n))
  }

  return c.json({
    ...company,
    panels,
    recommendations,
    liked,
    bookmarked,
    liked_panels: likedPanels,
  })
})

// いいね toggle
app.post('/api/like', async (c) => {
  const { line_user_id, content_type, content_id } = await c.req.json<{
    line_user_id: string
    content_type: string
    content_id: string
  }>()

  if (!line_user_id || !content_type || !content_id) {
    return c.json({ error: 'missing params' }, 400)
  }

  const existing = await c.env.DB.prepare(
    'SELECT 1 FROM likes WHERE line_user_id = ? AND content_type = ? AND content_id = ?'
  ).bind(line_user_id, content_type, content_id).first()

  if (existing) {
    await c.env.DB.prepare(
      'DELETE FROM likes WHERE line_user_id = ? AND content_type = ? AND content_id = ?'
    ).bind(line_user_id, content_type, content_id).run()
    return c.json({ liked: false })
  } else {
    await c.env.DB.prepare(
      'INSERT INTO likes (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
    ).bind(line_user_id, content_type, content_id).run()
    return c.json({ liked: true })
  }
})

// ブックマーク toggle
app.post('/api/bookmark', async (c) => {
  const { line_user_id, company_id } = await c.req.json<{
    line_user_id: string
    company_id: string
  }>()

  if (!line_user_id || !company_id) {
    return c.json({ error: 'missing params' }, 400)
  }

  const existing = await c.env.DB.prepare(
    'SELECT 1 FROM bookmarks WHERE line_user_id = ? AND company_id = ?'
  ).bind(line_user_id, company_id).first()

  if (existing) {
    await c.env.DB.prepare(
      'DELETE FROM bookmarks WHERE line_user_id = ? AND company_id = ?'
    ).bind(line_user_id, company_id).run()
    return c.json({ bookmarked: false })
  } else {
    await c.env.DB.prepare(
      'INSERT INTO bookmarks (line_user_id, company_id) VALUES (?, ?)'
    ).bind(line_user_id, company_id).run()
    return c.json({ bookmarked: true })
  }
})

// ブックマーク一覧
app.get('/api/bookmarks', async (c) => {
  const userId = c.req.query('user_id')
  if (!userId) return c.json([])

  const { results } = await c.env.DB.prepare(
    `SELECT c.id, c.name, c.description, c.industry_id, c.thumbnail_url, b.created_at
     FROM bookmarks b
     JOIN companies c ON c.id = b.company_id
     WHERE b.line_user_id = ?
     ORDER BY b.created_at DESC`
  ).bind(userId).all()
  return c.json(results)
})

// 閲覧ログ
app.post('/api/log-view', async (c) => {
  const { line_user_id, content_type, content_id } = await c.req.json<{
    line_user_id: string
    content_type: string
    content_id: string
  }>()
  await c.env.DB.prepare(
    'INSERT INTO view_logs (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
  ).bind(line_user_id, content_type, content_id).run()
  return c.json({ ok: true })
})

// シェアログ
app.post('/api/share-log', async (c) => {
  const { line_user_id, content_type, content_id } = await c.req.json<{
    line_user_id: string
    content_type: string
    content_id: string
  }>()
  await c.env.DB.prepare(
    'INSERT INTO share_logs (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
  ).bind(line_user_id, content_type, content_id).run()
  return c.json({ ok: true })
})

// =====================================================
// 動画一覧（業界別＋企業別）
// =====================================================
app.get('/api/videos', async (c) => {
  // 業界別動画
  const { results: industryVideos } = await c.env.DB.prepare(
    `SELECT iv.industry_id, i.name AS industry_name, iv.video_url, iv.title, iv.display_order
     FROM industry_videos iv
     JOIN industries i ON i.id = iv.industry_id
     ORDER BY i.id, iv.display_order`
  ).all()

  // 企業別動画（video_urlがあり、PLACEHOLDERでないもの）
  const { results: companyVideos } = await c.env.DB.prepare(
    `SELECT c.id AS company_id, c.name AS company_name, c.industry_id, i.name AS industry_name, c.video_url, c.thumbnail_url
     FROM companies c
     JOIN industries i ON i.id = c.industry_id
     WHERE c.video_url IS NOT NULL AND c.video_url NOT LIKE '%PLACEHOLDER%'
     ORDER BY i.id, c.id`
  ).all()

  return c.json({
    industry_videos: industryVideos,
    company_videos: companyVideos,
  })
})

// =====================================================
// OB認証
// =====================================================
app.post('/api/ob/auth', async (c) => {
  const { password, line_user_id } = await c.req.json<{
    password: string
    line_user_id?: string
  }>()

  if (!password) {
    return c.json({ ok: false, error: 'missing password' }, 400)
  }

  const row = await c.env.DB.prepare(
    `SELECT value FROM settings WHERE key = 'ob_password'`
  ).first<{ value: string }>()

  if (!row) {
    return c.json({ ok: false, error: 'password not configured' }, 500)
  }

  const correct = row.value === password

  // 認証試行ログ（成否問わず）
  if (line_user_id) {
    await c.env.DB.prepare(
      'INSERT INTO view_logs (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
    ).bind(line_user_id, 'ob_auth', correct ? 'success' : 'fail').run().catch(() => {})
  }

  return c.json({ ok: correct })
})

// =====================================================
// OB一覧（認証後）
// =====================================================
app.post('/api/ob/list', async (c) => {
  const { password } = await c.req.json<{ password: string }>()

  if (!password) {
    return c.json({ error: 'missing password' }, 400)
  }

  const row = await c.env.DB.prepare(
    `SELECT value FROM settings WHERE key = 'ob_password'`
  ).first<{ value: string }>()

  if (!row || row.value !== password) {
    return c.json({ error: 'unauthorized' }, 401)
  }

  const { results } = await c.env.DB.prepare(
    `SELECT id, name, affiliation, university, line_id, industry_id, display_order, graduation_year
     FROM obs
     ORDER BY display_order, id`
  ).all()

  return c.json(results)
})

// =====================================================
// トーキャリ・ルーム API
// =====================================================

function stripMarkdown(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, (m) => m.replace(/```/g, '').trim())
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*\*([^*\n]+)\*\*/g, '$1')
    .replace(/__([^_\n]+)__/g, '$1')
    .replace(/\*([^*\n]+)\*/g, '$1')
    .replace(/_([^_\n]+)_/g, '$1')
    .replace(/#{1,6}\s+(.+)/gm, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^[-*+]\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

// ペルソナ一覧
app.get('/api/room/personas/:company_id', async (c) => {
  try {
    const companyId = c.req.param('company_id')
    const { results } = await c.env.DB.prepare(
      `SELECT persona_id, company_id, role_code, display_name, display_name_kana,
              age, department, position, short_description, image_url, voice_config
       FROM personas
       WHERE company_id = ? AND is_active = 1
       ORDER BY persona_id`
    ).bind(companyId).all()
    return c.json(results)
  } catch (e) {
    console.error('personas error:', e)
    return c.json({ error: 'internal error' }, 500)
  }
})

// 会話取得・作成
app.get('/api/room/conversation', async (c) => {
  try {
    const lineUserId = c.req.query('line_user_id')
    const personaId = c.req.query('persona_id')
    if (!lineUserId || !personaId) {
      return c.json({ error: 'missing params' }, 400)
    }

    let conversation = await c.env.DB.prepare(
      `SELECT * FROM room_conversations WHERE line_user_id = ? AND persona_id = ?`
    ).bind(lineUserId, personaId).first()

    if (!conversation) {
      const conversationId = crypto.randomUUID()
      const persona = await c.env.DB.prepare(
        `SELECT company_id FROM personas WHERE persona_id = ?`
      ).bind(personaId).first<{ company_id: string }>()

      await c.env.DB.prepare(
        `INSERT INTO room_conversations (conversation_id, line_user_id, company_id, persona_id)
         VALUES (?, ?, ?, ?)`
      ).bind(conversationId, lineUserId, persona?.company_id ?? '', personaId).run()

      conversation = await c.env.DB.prepare(
        `SELECT * FROM room_conversations WHERE conversation_id = ?`
      ).bind(conversationId).first()
    }

    const conv = conversation as { conversation_id: string; [key: string]: unknown }
    const { results: messages } = await c.env.DB.prepare(
      `SELECT * FROM room_messages WHERE conversation_id = ? ORDER BY created_at ASC`
    ).bind(conv.conversation_id).all()

    return c.json({ conversation, messages })
  } catch (e) {
    console.error('conversation error:', e)
    return c.json({ error: 'internal error' }, 500)
  }
})

// メッセージ送信（Claude呼び出し）
app.post('/api/room/message', async (c) => {
  try {
    const { conversation_id, line_user_id, persona_id, content } = await c.req.json<{
      conversation_id: string
      line_user_id: string
      persona_id: string
      content: string
    }>()

    if (!conversation_id || !line_user_id || !content) {
      return c.json({ error: 'missing params' }, 400)
    }

    // ユーザーメッセージをDB保存
    const userMsgId = crypto.randomUUID()
    await c.env.DB.prepare(
      `INSERT INTO room_messages (message_id, conversation_id, role, content) VALUES (?, ?, 'user', ?)`
    ).bind(userMsgId, conversation_id, content).run()

    // ペルソナのシステムプロンプト取得
    const persona = await c.env.DB.prepare(
      `SELECT system_prompt, display_name FROM personas WHERE persona_id = ?`
    ).bind(persona_id).first<{ system_prompt: string; display_name: string }>()

    // 会話履歴取得
    const { results: history } = await c.env.DB.prepare(
      `SELECT role, content FROM room_messages WHERE conversation_id = ? ORDER BY created_at ASC`
    ).bind(conversation_id).all<{ role: string; content: string }>()

    // Claude API呼び出し
    const claudeRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
        'x-api-key': c.env.ANTHROPIC_API_KEY,
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5',
        max_tokens: 2048,
        system: persona?.system_prompt ?? '',
        messages: history.map(m => ({ role: m.role, content: m.content })),
      }),
    })

    if (!claudeRes.ok) {
      const err = await claudeRes.text()
      console.error('Claude API error:', err)
      return c.json({ error: 'Claude API error' }, 500)
    }

    const claudeData = await claudeRes.json<{
      content: Array<{ type: string; text: string }>
    }>()
    const aiText = stripMarkdown(claudeData.content.find(b => b.type === 'text')?.text ?? '')

    // AIメッセージをDB保存
    const aiMsgId = crypto.randomUUID()
    await c.env.DB.prepare(
      `INSERT INTO room_messages (message_id, conversation_id, role, content) VALUES (?, ?, 'assistant', ?)`
    ).bind(aiMsgId, conversation_id, aiText).run()

    // 会話の最終更新・カウント更新
    await c.env.DB.prepare(
      `UPDATE room_conversations
       SET last_message_at = datetime('now'), message_count = message_count + 2
       WHERE conversation_id = ?`
    ).bind(conversation_id).run()

    return c.json({ message_id: aiMsgId, role: 'assistant', content: aiText })
  } catch (e) {
    console.error('message error:', e)
    return c.json({ error: 'internal error' }, 500)
  }
})

// TTS（Google TTS + R2キャッシュ）
app.post('/api/room/tts', async (c) => {
  try {
    const { text, voice_config } = await c.req.json<{
      text: string
      voice_config?: {
        voiceName?: string  // DBのフォーマット
        name?: string       // Google TTS直接フォーマット
        languageCode?: string
        ssmlGender?: string
        speakingRate?: number
        pitch?: number
      }
    }>()

    if (!text) {
      return c.json({ error: 'missing text' }, 400)
    }

    const vc = voice_config ?? {}
    const voiceName = vc.voiceName ?? vc.name ?? 'ja-JP-Neural2-B'
    const speakingRate = vc.speakingRate ?? 1.0
    const pitch = vc.pitch ?? 0.0

    // キャッシュキー生成（SHA-256）
    const cacheData = JSON.stringify({ text, voiceName, speakingRate, pitch })
    const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(cacheData))
    const hashHex = Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('')
    const r2Key = `tts/${hashHex}.mp3`

    // R2キャッシュ確認
    const cached = await c.env.TTS_CACHE.get(r2Key)
    if (cached) {
      const audioBytes = await cached.arrayBuffer()
      const audioArr = new Uint8Array(audioBytes)
      let binary = ''
      for (let i = 0; i < audioArr.length; i++) binary += String.fromCharCode(audioArr[i])
      return c.json({ audio_base64: btoa(binary), cached: true })
    }

    // Google TTS API呼び出し
    const ttsRes = await fetch(
      `https://texttospeech.googleapis.com/v1/text:synthesize?key=${c.env.GOOGLE_TTS_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: { text },
          voice: { languageCode: 'ja-JP', name: voiceName },
          audioConfig: { audioEncoding: 'MP3', speakingRate, pitch },
        }),
      }
    )

    if (!ttsRes.ok) {
      const err = await ttsRes.text()
      console.error('TTS API error:', err)
      return c.json({ error: 'TTS API error' }, 500)
    }

    const ttsData = await ttsRes.json<{ audioContent: string }>()
    const audioBase64 = ttsData.audioContent

    // バイナリに変換してR2に保存
    const binaryStr = atob(audioBase64)
    const audioBytes2 = new Uint8Array(binaryStr.length)
    for (let i = 0; i < binaryStr.length; i++) audioBytes2[i] = binaryStr.charCodeAt(i)
    await c.env.TTS_CACHE.put(r2Key, audioBytes2, {
      httpMetadata: { contentType: 'audio/mpeg' },
    })

    return c.json({ audio_base64: audioBase64, cached: false })
  } catch (e) {
    console.error('tts error:', e)
    return c.json({ error: 'internal error' }, 500)
  }
})

// 初回挨拶（Phase 5用）
app.post('/api/room/init', async (c) => {
  try {
    const { conversation_id, persona_id } = await c.req.json<{
      conversation_id: string
      persona_id: string
    }>()

    if (!conversation_id || !persona_id) {
      return c.json({ error: 'missing params' }, 400)
    }

    // 既にメッセージがある場合はスキップ
    const existing = await c.env.DB.prepare(
      `SELECT COUNT(*) as cnt FROM room_messages WHERE conversation_id = ?`
    ).bind(conversation_id).first<{ cnt: number }>()

    if (existing && existing.cnt > 0) {
      return c.json({ skipped: true })
    }

    const persona = await c.env.DB.prepare(
      `SELECT system_prompt, display_name FROM personas WHERE persona_id = ?`
    ).bind(persona_id).first<{ system_prompt: string; display_name: string }>()

    if (!persona) {
      return c.json({ error: 'persona not found' }, 404)
    }

    // Claude APIで挨拶生成
    const claudeRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
        'x-api-key': c.env.ANTHROPIC_API_KEY,
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5',
        max_tokens: 2048,
        system: persona.system_prompt,
        messages: [{ role: 'user', content: 'はじめまして。自己紹介をお願いします。' }],
      }),
    })

    if (!claudeRes.ok) {
      return c.json({ error: 'Claude API error' }, 500)
    }

    const claudeData = await claudeRes.json<{
      content: Array<{ type: string; text: string }>
    }>()
    const greeting = stripMarkdown(claudeData.content.find(b => b.type === 'text')?.text ?? '')

    const msgId = crypto.randomUUID()
    await c.env.DB.prepare(
      `INSERT INTO room_messages (message_id, conversation_id, role, content) VALUES (?, ?, 'assistant', ?)`
    ).bind(msgId, conversation_id, greeting).run()

    await c.env.DB.prepare(
      `UPDATE room_conversations SET last_message_at = datetime('now'), message_count = 1 WHERE conversation_id = ?`
    ).bind(conversation_id).run()

    return c.json({ message_id: msgId, role: 'assistant', content: greeting })
  } catch (e) {
    console.error('init error:', e)
    return c.json({ error: 'internal error' }, 500)
  }
})

// options(JSON文字列)を安全にparse
function safeJson(s: any) { try { return typeof s === 'string' ? JSON.parse(s) : s } catch { return s } }

// === クイズ 難易度4段階（difficulty 1..4）===
// 正解1問あたりXP重み。NULL は Lv2 相当（COALESCE(difficulty,2)）。
const QUIZ_LV_WEIGHT: Record<number, number> = { 1: 10, 2: 20, 3: 40, 4: 80 }
const QUIZ_PASS_RATE = 0.8        // Lv正答率≥80%で次Lv解放
const QUIZ_PASS_MIN = 8           // 判定に必要な最小回答数（levelの実在問数が少なければそれに合わせる）
const QUIZ_BONUS_LEVEL = 100      // 各Lv初回80%達成ボーナス
const QUIZ_BONUS_SET = 300        // setのLv4クリア（全Lv制覇）ボーナス
const diffWeightSql = `CASE COALESCE(q.difficulty,2) WHEN 1 THEN 10 WHEN 3 THEN 40 WHEN 4 THEN 80 ELSE 20 END`

// (set_id,level) ごとの解放判定。空Lv(実在0問)は透過的にpass扱い＝次の実在Lvへ進める。
type LvStat = { level: number; available: number; answered: number; correct: number; rate: number; passed: boolean; unlocked: boolean }
async function computeUnlock(env: any, userId: string, setType: string, setId: string): Promise<{ unlocked_max: number; by_level: Record<string, LvStat> }> {
  // 実在問数 / 回答・正答（COALESCEでNULL→Lv2）
  const avail: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0 }
  const ans: Record<number, { answered: number; correct: number }> = { 1: { answered: 0, correct: 0 }, 2: { answered: 0, correct: 0 }, 3: { answered: 0, correct: 0 }, 4: { answered: 0, correct: 0 } }
  try {
    const a = await env.DB.prepare(
      `SELECT COALESCE(difficulty,2) lv, COUNT(*) n FROM quiz_questions WHERE set_type=? AND set_id=? GROUP BY lv`
    ).bind(setType, setId).all()
    for (const r of (a.results || []) as any[]) if (avail[r.lv] != null) avail[r.lv] = r.n
  } catch (e) { /* graceful */ }
  if (userId) {
    try {
      const p = await env.DB.prepare(
        `SELECT COALESCE(q.difficulty,2) lv, COUNT(*) answered, SUM(p.is_correct) correct
         FROM user_quiz_progress p JOIN quiz_questions q ON q.id = p.question_id
         WHERE p.line_user_id=? AND p.set_type=? AND p.set_id=? GROUP BY lv`
      ).bind(userId, setType, setId).all()
      for (const r of (p.results || []) as any[]) if (ans[r.lv]) ans[r.lv] = { answered: r.answered || 0, correct: r.correct || 0 }
    } catch (e) { /* graceful */ }
  }
  const by_level: Record<string, LvStat> = {}
  let prevPassed: boolean = true, unlocked_max = 1
  for (let lv = 1; lv <= 4; lv++) {
    const available = avail[lv], { answered, correct } = ans[lv]
    const rate = answered ? correct / answered : 0
    const need = Math.min(QUIZ_PASS_MIN, available || QUIZ_PASS_MIN)
    // 実在0問のLvは透過pass（次の実在Lvへ）。実在ありは 回答≥need かつ 正答率≥80% でpass。
    const passed = available === 0 ? true : (answered >= need && rate >= QUIZ_PASS_RATE)
    const unlocked: boolean = lv === 1 ? true : prevPassed
    if (unlocked) unlocked_max = lv
    by_level[String(lv)] = { level: lv, available, answered, correct, rate: Math.round(rate * 100) / 100, passed, unlocked }
    prevPassed = unlocked && passed
  }
  return { unlocked_max, by_level }
}

app.get('/api/quiz', async (c) => {
  const setType = c.req.query('set_type'); const setId = c.req.query('set_id')
  const levelRaw = c.req.query('level'); const userId = c.req.query('user_id')
  if (!setType || !setId) return c.json([])
  const cols = `id, category, q_text, options, correct, explanation, source_url, as_of, COALESCE(difficulty,2) difficulty`
  try {
    let results: any[]
    if (levelRaw) {
      const level = Math.max(1, Math.min(4, parseInt(levelRaw, 10) || 1))
      const r = await c.env.DB.prepare(
        `SELECT ${cols} FROM quiz_questions WHERE set_type=? AND set_id=? AND COALESCE(difficulty,2)=? ORDER BY ord, id`
      ).bind(setType, setId, level).all()
      results = r.results || []
    } else if (userId) {
      // level省略＋user_id: 解放済み最大levelまで
      const { unlocked_max } = await computeUnlock(c.env, userId, setType, setId)
      const r = await c.env.DB.prepare(
        `SELECT ${cols} FROM quiz_questions WHERE set_type=? AND set_id=? AND COALESCE(difficulty,2)<=? ORDER BY COALESCE(difficulty,2), ord, id`
      ).bind(setType, setId, unlocked_max).all()
      results = r.results || []
    } else {
      // 従来互換: level・user_id無し＝全問
      const r = await c.env.DB.prepare(
        `SELECT ${cols} FROM quiz_questions WHERE set_type=? AND set_id=? ORDER BY ord, id`
      ).bind(setType, setId).all()
      results = r.results || []
    }
    return c.json(results.map((r: any) => ({ ...r, options: safeJson(r.options) })))
  } catch (e) { return c.json([]) }
})

// Lv解放状態（フロントのレベルはしご表示用）
app.get('/api/quiz/unlock', async (c) => {
  const userId = c.req.query('user_id') || ''
  const setType = c.req.query('set_type'); const setId = c.req.query('set_id')
  if (!setType || !setId) return c.json({ unlocked_max: 1, by_level: {} })
  try {
    return c.json(await computeUnlock(c.env, userId, setType, setId))
  } catch (e) { return c.json({ unlocked_max: 1, by_level: {} }) }
})

app.post('/api/quiz/answer', async (c) => {
  try {
    const { line_user_id, question_id, chosen, is_correct, set_type, set_id } = await c.req.json()
    if (!line_user_id || !question_id) return c.json({ ok: false })
    await c.env.DB.prepare(
      `INSERT OR REPLACE INTO user_quiz_progress
       (line_user_id, question_id, set_type, set_id, chosen, is_correct, answered_at)
       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))`
    ).bind(line_user_id, question_id, set_type ?? null, set_id ?? null, chosen ?? null, is_correct ?? 0).run()
    return c.json({ ok: true })
  } catch (e) { return c.json({ ok: true, skipped: true }) }
})

app.get('/api/quiz/review', async (c) => {
  const userId = c.req.query('user_id'); const mode = c.req.query('mode') || 'recent'
  if (!userId) return c.json([])
  const cols = `q.id, q.category, q.q_text, q.options, q.correct, q.explanation, q.source_url, q.as_of`
  let sql: string
  if (mode === 'frequent') {
    sql = `SELECT ${cols}, COUNT(*) ng FROM user_quiz_progress p JOIN quiz_questions q ON q.id = p.question_id
           WHERE p.line_user_id = ? AND p.is_correct = 0
           GROUP BY p.question_id ORDER BY ng DESC, MAX(p.answered_at) DESC LIMIT 10`
  } else if (mode === 'weak_category') {
    sql = `WITH cat AS (SELECT q.category, AVG(p.is_correct) acc FROM user_quiz_progress p
             JOIN quiz_questions q ON q.id = p.question_id WHERE p.line_user_id = ? GROUP BY q.category)
           SELECT ${cols} FROM quiz_questions q JOIN cat ON cat.category = q.category
           ORDER BY cat.acc ASC LIMIT 10`
  } else {
    sql = `SELECT ${cols} FROM user_quiz_progress p JOIN quiz_questions q ON q.id = p.question_id
           WHERE p.line_user_id = ? AND p.is_correct = 0 ORDER BY p.answered_at DESC LIMIT 10`
  }
  try {
    const { results } = await c.env.DB.prepare(sql).bind(userId).all()
    return c.json((results || []).map((r: any) => ({ ...r, options: safeJson(r.options) })))
  } catch (e) { return c.json([]) }
})

// === ホーム: 続きから（最近見た企業・view_logsから） ===
app.get('/api/recent-companies', async (c) => {
  const userId = c.req.query('user_id')
  const limit = Math.min(parseInt(c.req.query('limit') || '5', 10) || 5, 10)
  if (!userId) return c.json([])
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT c.id, c.name, c.description, MAX(v.viewed_at) last_viewed
       FROM view_logs v JOIN companies c ON c.id = v.content_id
       WHERE v.line_user_id = ? AND v.content_type = 'company'
       GROUP BY v.content_id ORDER BY last_viewed DESC LIMIT ?`
    ).bind(userId, limit).all()
    return c.json(results || [])
  } catch (e) { return c.json([]) }
})

// === 企業一覧ページ用（人気順=view_logs集計 + 一言hook=description）を1レスポンスで。名前/業界はcompanies.json流用 ===
app.get('/api/company-list', async (c) => {
  const out: any = { views: {}, hooks: {} }
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT content_id id, COUNT(*) n FROM view_logs WHERE content_type = 'company' GROUP BY content_id`
    ).all()
    for (const r of (results || []) as any[]) out.views[r.id] = r.n
  } catch (e) { /* graceful: 人気順は0扱い */ }
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT id, description FROM companies WHERE description IS NOT NULL AND description != ''`
    ).all()
    for (const r of (results || []) as any[]) out.hooks[r.id] = String(r.description).slice(0, 46)
  } catch (e) { /* graceful: hookは省略 */ }
  return c.json(out)
})

// === 企業データシート（タブD投入・未投入時はgraceful 404→フロントはサンプル/導線非表示） ===
app.get('/api/datasheet', async (c) => {
  const id = c.req.query('id')
  if (!id) return c.json({ error: 'id required' }, 400)
  try {
    const row = await c.env.DB.prepare(
      'SELECT company_id, data FROM datasheets WHERE company_id = ?'
    ).bind(id).first<{ company_id: string; data: string }>()
    if (!row) return c.json({ error: 'not found', id }, 404)
    return c.json({ id: row.company_id, ...safeJson(row.data) })
  } catch (e) { return c.json({ error: 'unavailable', id }, 404) }
})

// === ES・面接対策キット（会社別・タブD生成。datasheetと同型のgraceful。未投入時404→フロントは案内表示） ===
// es_kits(company_id TEXT PRIMARY KEY, data TEXT) の data JSON 想定スキーマ:
//   { "name": "会社名",
//     "motivation": [ { "text": "志望動機の材料(事実)", "source_url": "..." } ],
//     "questions":  [ { "text": "想定質問", "note": "答え方のヒント" } ] }
app.get('/api/es-kit', async (c) => {
  const id = c.req.query('id')
  if (!id) return c.json({ error: 'id required' }, 400)
  try {
    const row = await c.env.DB.prepare(
      'SELECT company_id, data FROM es_kits WHERE company_id = ?'
    ).bind(id).first<{ company_id: string; data: string }>()
    if (!row) return c.json({ error: 'not found', id }, 404)
    return c.json({ id: row.company_id, ...safeJson(row.data) })
  } catch (e) { return c.json({ error: 'unavailable', id }, 404) }
})

// === 企業比較（既存 attributes + datasheets を束ねるだけ・新規生成なし・graceful） ===
app.get('/api/compare', async (c) => {
  const idsRaw = c.req.query('ids') || ''
  // 重複除去・順序維持・最大3社
  const seen = new Set<string>()
  const ids: string[] = []
  for (const s of idsRaw.split(',').map(x => x.trim()).filter(Boolean)) {
    if (!seen.has(s)) { seen.add(s); ids.push(s) }
    if (ids.length >= 3) break
  }
  if (ids.length < 1) return c.json({ error: 'ids required (comma-separated, 1-3)' }, 400)
  const companies = []
  for (const id of ids) {
    let ds: any = null
    try {
      const row = await c.env.DB.prepare(
        'SELECT data FROM datasheets WHERE company_id = ?'
      ).bind(id).first<{ data: string }>()
      if (row) ds = safeJson(row.data)
    } catch (e) { /* datasheet未投入/不可はgraceful=データなし */ }
    companies.push(bundleCompany(id, ds))
  }
  return c.json({ companies, disclaimer: COMPARE_DISCLAIMER })
})

// === 業界・企業診断（決定論マッチング・AI課金なし・shindanタブA由来データをバンドル） ===
app.post('/api/shindan', async (c) => {
  try {
    const body = await c.req.json().catch(() => ({}))
    const answers = (body && body.answers) || {}
    return c.json(recommend(answers))
  } catch (e) { return c.json({ error: 'bad request' }, 400) }
})

// 診断結果の保存（user_idごと最新1件を上書き。shindan.htmlからfire-and-forget） ===
app.post('/api/shindan/save', async (c) => {
  try {
    const body = await c.req.json().catch(() => ({}))
    const userId = body.user_id || body.userId
    const result = body.result
    if (!userId || !result) return c.json({ ok: false })
    await c.env.DB.prepare(
      `INSERT INTO shindan_results (user_id, result_json, created_at)
       VALUES (?, ?, datetime('now'))
       ON CONFLICT(user_id) DO UPDATE SET result_json = excluded.result_json, created_at = excluded.created_at`
    ).bind(userId, JSON.stringify(result)).run()
    return c.json({ ok: true })
  } catch (e) { return c.json({ ok: true, skipped: true }) }
})

// === 初回プロフィール（所属種別 + 大学/学部/卒業年度 + 同意）。student_univ以外は学校情報NULL ===
app.get('/api/profile', async (c) => {
  const userId = c.req.query('userId') || c.req.query('user_id')
  if (!userId) return c.json({ registered: false, profile: null })
  try {
    const row = await c.env.DB.prepare(
      `SELECT user_id, user_type, university, faculty, grad_year, consented_at, consent_version FROM user_profiles WHERE user_id = ?`
    ).bind(userId).first<any>()
    return c.json({ registered: !!row, profile: row || null })
  } catch (e) { return c.json({ registered: false, profile: null }) }
})
app.post('/api/profile', async (c) => {
  try {
    const b = await c.req.json().catch(() => ({}))
    const userId = b.user_id || b.userId
    const userType = b.user_type
    const ALLOWED = ['student_univ', 'student_pre', 'worker', 'other']
    if (!userId || ALLOWED.indexOf(userType) < 0) return c.json({ ok: false, error: 'user_id and valid user_type required' }, 400)
    if (!b.consented || !b.consent_version) return c.json({ ok: false, error: 'consent required' }, 400)
    // 大学生のみ大学/学部、卒業年度は大学生・高校生(任意)のみ保持。それ以外はNULL。
    const uni = userType === 'student_univ' ? (b.university || null) : null
    const fac = userType === 'student_univ' ? (b.faculty || null) : null
    const grad = (userType === 'student_univ' || userType === 'student_pre') ? (b.grad_year || null) : null
    await c.env.DB.prepare(
      `INSERT INTO user_profiles (user_id, user_type, university, faculty, grad_year, consented_at, consent_version)
       VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
       ON CONFLICT(user_id) DO UPDATE SET user_type=excluded.user_type, university=excluded.university,
         faculty=excluded.faculty, grad_year=excluded.grad_year, consented_at=excluded.consented_at, consent_version=excluded.consent_version`
    ).bind(userId, userType, uni, fac, grad, b.consent_version).run()
    return c.json({ ok: true })
  } catch (e) { return c.json({ ok: false }, 500) }
})
app.post('/api/profile/delete', async (c) => {
  try {
    const b = await c.req.json().catch(() => ({}))
    const userId = b.user_id || b.userId
    if (!userId) return c.json({ ok: false }, 400)
    await c.env.DB.prepare(`DELETE FROM user_profiles WHERE user_id = ?`).bind(userId).run()
    return c.json({ ok: true })
  } catch (e) { return c.json({ ok: false }, 500) }
})

// === マイページ集約（続きから/お気に入り/クイズ成績/診断結果 を1レスポンスで・往復1回・各ブロックgraceful） ===
app.get('/api/mypage', async (c) => {
  const userId = c.req.query('userId') || c.req.query('user_id')
  if (!userId) return c.json({ error: 'userId required' }, 400)
  const out: any = {
    continue: { recent: [], quiz_resume: null },
    bookmarks: [],
    quiz_stats: { companies: 0, accuracy: null, answered: 0, recent_scores: [] },
    shindan: null,
    // v1.5 4本柱
    stamp_rally: { industries: [], explored: 0, total: 0 },
    level: { xp: 0, level: 1, level_name: '就活ビギナー', next_xp: 50, progress: 0, breakdown: { companies: 0, quiz_correct: 0, shindan: false }, badges: [] },
    next3: [],
    feed: { internal: [], official: [] },
  }

  // a-1. 続きから: 最近閲覧した企業 上位3社
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT c.id, c.name, c.description, MAX(v.viewed_at) last_viewed
       FROM view_logs v JOIN companies c ON c.id = v.content_id
       WHERE v.line_user_id = ? AND v.content_type = 'company'
       GROUP BY v.content_id ORDER BY last_viewed DESC LIMIT 3`
    ).bind(userId).all()
    out.continue.recent = results || []
  } catch (e) { /* graceful */ }

  // a-2. クイズの続き: 直近の会社クイズsetが未完なら
  try {
    const row = await c.env.DB.prepare(
      `SELECT set_id, COUNT(*) answered, MAX(answered_at) last_ans
       FROM user_quiz_progress
       WHERE line_user_id = ? AND set_type = 'company' AND set_id IS NOT NULL
       GROUP BY set_id ORDER BY last_ans DESC LIMIT 1`
    ).bind(userId).first<any>()
    if (row && row.set_id) {
      const tot = await c.env.DB.prepare(
        `SELECT COUNT(*) total FROM quiz_questions WHERE set_type = 'company' AND set_id = ?`
      ).bind(row.set_id).first<any>()
      const total = (tot && tot.total) || 0
      if (total > 0 && row.answered < total) {
        const cq = await c.env.DB.prepare(`SELECT name FROM companies WHERE id = ?`).bind(row.set_id).first<any>()
        out.continue.quiz_resume = { set_id: row.set_id, name: (cq && cq.name) || row.set_id, answered: row.answered, total }
      }
    }
  } catch (e) { /* graceful */ }

  // b. お気に入り
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT c.id, c.name, c.description, c.industry_id, c.thumbnail_url, b.created_at
       FROM bookmarks b JOIN companies c ON c.id = b.company_id
       WHERE b.line_user_id = ? ORDER BY b.created_at DESC`
    ).bind(userId).all()
    out.bookmarks = results || []
  } catch (e) { /* graceful */ }

  // c. クイズ成績（受験社数・累計正答率・直近3社スコア）
  try {
    const agg = await c.env.DB.prepare(
      `SELECT COUNT(DISTINCT set_id) companies, AVG(is_correct) acc, COUNT(*) answered
       FROM user_quiz_progress WHERE line_user_id = ? AND set_type = 'company'`
    ).bind(userId).first<any>()
    if (agg) {
      out.quiz_stats.companies = agg.companies || 0
      out.quiz_stats.answered = agg.answered || 0
      out.quiz_stats.accuracy = agg.answered ? Math.round((agg.acc || 0) * 100) : null
    }
    const { results } = await c.env.DB.prepare(
      `SELECT p.set_id, c.name, AVG(p.is_correct) acc, COUNT(*) answered, MAX(p.answered_at) last_ans
       FROM user_quiz_progress p LEFT JOIN companies c ON c.id = p.set_id
       WHERE p.line_user_id = ? AND p.set_type = 'company'
       GROUP BY p.set_id ORDER BY last_ans DESC LIMIT 3`
    ).bind(userId).all()
    out.quiz_stats.recent_scores = (results || []).map((r: any) => ({
      set_id: r.set_id, name: r.name || r.set_id, score: Math.round((r.acc || 0) * 100), answered: r.answered || 0,
    }))
  } catch (e) { /* graceful */ }

  // d. 診断結果（最新1件）
  try {
    const row = await c.env.DB.prepare(
      `SELECT result_json, created_at FROM shindan_results WHERE user_id = ?`
    ).bind(userId).first<any>()
    if (row && row.result_json) {
      const r = safeJson(row.result_json)
      out.shindan = {
        top_industries: (r && r.top_industries) || [],
        top_companies: (r && r.top_companies) || [],
        disclaimer: (r && r.disclaimer) || '',
        created_at: row.created_at,
      }
    }
  } catch (e) { /* graceful */ }

  // ===== v1.5 4本柱（全て既存データの集計・追加AIなし・往復1回維持） =====

  // 閲覧済み企業ID(distinct) — スタンプ/バッジ/次の3社で再利用
  const viewedIds = new Set<string>()
  try {
    const { results } = await c.env.DB.prepare(
      `SELECT DISTINCT content_id FROM view_logs WHERE line_user_id = ? AND content_type = 'company'`
    ).bind(userId).all()
    for (const r of (results || []) as any[]) viewedIds.add(r.content_id)
  } catch (e) { /* graceful */ }

  // クイズ正答数(累計) + 難易度重みXP + Lv解放ボーナス（決定論・冪等）
  let quizCorrect = 0, quizXP = 0
  try {
    const r = await c.env.DB.prepare(
      `SELECT COUNT(*) n FROM user_quiz_progress WHERE line_user_id = ? AND is_correct = 1`
    ).bind(userId).first<any>()
    quizCorrect = (r && r.n) || 0
    // (1) 正解の難易度重み合計（Lv1=10/2=20/3=40/4=80。旧形式=NULLはLv2重み）
    const wc = await c.env.DB.prepare(
      `SELECT COALESCE(SUM(${diffWeightSql}),0) xp
       FROM user_quiz_progress p JOIN quiz_questions q ON q.id = p.question_id
       WHERE p.line_user_id = ? AND p.is_correct = 1`
    ).bind(userId).first<any>()
    quizXP = (wc && wc.xp) || 0
    // (2) Lv解放ボーナス: (set_id,level)ごとに 回答/正答 と 実在問数 を突合し pass 判定
    const pl = await c.env.DB.prepare(
      `SELECT p.set_type, p.set_id, COALESCE(q.difficulty,2) lv, COUNT(*) answered, SUM(p.is_correct) correct
       FROM user_quiz_progress p JOIN quiz_questions q ON q.id = p.question_id
       WHERE p.line_user_id = ? GROUP BY p.set_type, p.set_id, lv`
    ).bind(userId).all()
    const rows = (pl.results || []) as any[]
    if (rows.length) {
      const setIds = Array.from(new Set(rows.map(r => r.set_id)))
      const ph = setIds.map(() => '?').join(',')
      const av = await c.env.DB.prepare(
        `SELECT set_type, set_id, COALESCE(difficulty,2) lv, COUNT(*) avail FROM quiz_questions
         WHERE set_id IN (${ph}) GROUP BY set_type, set_id, lv`
      ).bind(...setIds).all()
      const availMap: Record<string, number> = {}
      for (const r of (av.results || []) as any[]) availMap[`${r.set_type}${r.set_id}${r.lv}`] = r.avail
      let bonus = 0
      for (const r of rows) {
        const available = availMap[`${r.set_type}${r.set_id}${r.lv}`] || 0
        if (available === 0) continue
        const need = Math.min(QUIZ_PASS_MIN, available)
        const answered = r.answered || 0, correct = r.correct || 0
        const passed = answered >= need && (correct / answered) >= QUIZ_PASS_RATE
        if (passed) { bonus += QUIZ_BONUS_LEVEL; if (r.lv === 4) bonus += QUIZ_BONUS_SET }
      }
      quizXP += bonus
    }
  } catch (e) { /* graceful */ }

  // 1. 業界制覇スタンプラリー（分母=D1 industries×companies実在社数、n>=2の実分類業界のみ）
  try {
    const totals = await c.env.DB.prepare(
      `SELECT i.id, i.name, COUNT(c.id) total FROM industries i JOIN companies c ON c.industry_id = i.id
       GROUP BY i.id HAVING total >= 2 ORDER BY total DESC`
    ).all()
    const viewedByInd: Record<string, number> = {}
    const vr = await c.env.DB.prepare(
      `SELECT c.industry_id ind, COUNT(DISTINCT v.content_id) n
       FROM view_logs v JOIN companies c ON c.id = v.content_id
       WHERE v.line_user_id = ? AND v.content_type = 'company' GROUP BY c.industry_id`
    ).bind(userId).all()
    for (const r of (vr.results || []) as any[]) viewedByInd[r.ind] = r.n
    const inds = ((totals.results || []) as any[]).map(r => ({
      id: r.id, name: r.name, total: r.total, viewed: viewedByInd[r.id] || 0,
    }))
    out.stamp_rally.industries = inds
    out.stamp_rally.total = inds.length
    out.stamp_rally.explored = inds.filter(x => x.viewed > 0).length
  } catch (e) { /* graceful */ }

  // 2. 就活レベル＆称号（決定論。経験値=閲覧社数*10 + クイズ難易度重みXP(Lv1=10/2=20/3=40/4=80+解放ボーナス) + 診断完了*50。閾値は調整可）
  try {
    const nViewed = viewedIds.size
    const xp = nViewed * 10 + quizXP + (out.shindan ? 50 : 0)
    // レベル閾値(5段階)。後から調整しやすいよう配列で定義。
    const TIERS = [
      { min: 0, name: '就活ビギナー' }, { min: 50, name: '就活見習い' },
      { min: 150, name: '就活一人前' }, { min: 350, name: '就活ベテラン' }, { min: 700, name: '就活マスター' },
    ]
    let li = 0
    for (let i = 0; i < TIERS.length; i++) if (xp >= TIERS[i].min) li = i
    const nextMin = li < TIERS.length - 1 ? TIERS[li + 1].min : null
    const progress = nextMin != null ? Math.round(((xp - TIERS[li].min) / (nextMin - TIERS[li].min)) * 100) : 100
    // 称号バッジ(実績で決定論的に付与)
    const SHOSHA5 = ['mitsubishi-corp', 'mitsui-bussan', 'itochu', 'sumitomo-corp', 'marubeni']
    const shosha5n = SHOSHA5.filter(s => viewedIds.has(s)).length
    const explored = out.stamp_rally.explored, totalInd = out.stamp_rally.total
    const badges = [
      { id: 'first', label: 'はじめの一歩', detail: '企業を1社見た', earned: nViewed >= 1 },
      { id: 'shosha5', label: '5大商社コンプリート', detail: `${shosha5n}/5社`, earned: shosha5n >= 5 },
      { id: 'quiz10', label: 'クイズ10問正解', detail: `${Math.min(quizCorrect, 10)}/10問`, earned: quizCorrect >= 10 },
      { id: 'quiz100', label: 'クイズ100問正解', detail: `${Math.min(quizCorrect, 100)}/100問`, earned: quizCorrect >= 100 },
      { id: 'ind_half', label: '業界の半分を制覇', detail: totalInd ? `${explored}/${totalInd}業界` : '', earned: totalInd > 0 && explored >= Math.ceil(totalInd / 2) },
      { id: 'ind_all', label: '全業界制覇', detail: totalInd ? `${explored}/${totalInd}業界` : '', earned: totalInd > 0 && explored >= totalInd },
    ]
    out.level = { xp, level: li + 1, level_name: TIERS[li].name, next_xp: nextMin, progress,
      breakdown: { companies: nViewed, quiz_correct: quizCorrect, quiz_xp: quizXP, shindan: !!out.shindan }, badges }
  } catch (e) { /* graceful */ }

  // 3. 次に見るべき3社（既存診断結果の上位企業から未閲覧を抽出。新規ロジックなし）
  try {
    if (out.shindan && Array.isArray(out.shindan.top_companies)) {
      out.next3 = out.shindan.top_companies
        .filter((c2: any) => c2 && c2.slug && !viewedIds.has(c2.slug))
        .slice(0, 3)
        .map((c2: any) => ({ slug: c2.slug, name: c2.name, industry: c2.industry || '', score: c2.score }))
    }
  } catch (e) { /* graceful */ }

  // 4a. 更新フィード(内部)= 既存コンテンツのバッチ更新を要約(タイムスタンプ自動追従・手動メンテ不要)
  try {
    const norm = (t: any) => {
      if (t == null) return ''
      const s = String(t)
      if (/^\d{10,}$/.test(s)) { const d = new Date(parseInt(s, 10) * 1000); return d.toISOString().slice(0, 10) }
      return s.slice(0, 10)
    }
    const feed: any[] = []
    const q = await c.env.DB.prepare(`SELECT COUNT(DISTINCT set_id) n, MAX(created_at) ts FROM quiz_questions WHERE set_type='company'`).first<any>()
    if (q && q.n) feed.push({ kind: 'quiz', title: '企業クイズ', detail: `${q.n}社ぶん公開中`, date: norm(q.ts), href: '/quiz.html' })
    const ds = await c.env.DB.prepare(`SELECT COUNT(*) n, MAX(updated_at) ts FROM datasheets`).first<any>()
    if (ds && ds.n) feed.push({ kind: 'datasheet', title: '企業データシート', detail: `${ds.n}社ぶん公開中`, date: norm(ds.ts), href: '/home.html' })
    const ek = await c.env.DB.prepare(`SELECT COUNT(*) n, MAX(updated_at) ts FROM es_kits`).first<any>()
    if (ek && ek.n) feed.push({ kind: 'eskit', title: 'ES・面接対策キット', detail: `${ek.n}社ぶん公開中`, date: norm(ek.ts), href: '/es_guide.html' })
    feed.sort((a, b) => (a.date < b.date ? 1 : -1))
    out.feed.internal = feed
  } catch (e) { /* graceful */ }

  // 4b. 更新フィード(公式)= company_news(タブD生成) から お気に入り社分のみ。未作成/空でも壊れない。
  try {
    const favIds = (out.bookmarks || []).map((b: any) => b.id).filter(Boolean)
    if (favIds.length) {
      const ph = favIds.map(() => '?').join(',')
      const { results } = await c.env.DB.prepare(
        `SELECT n.company_id, c.name, n.title, n.url, n.published_at
         FROM company_news n JOIN companies c ON c.id = n.company_id
         WHERE n.company_id IN (${ph}) ORDER BY n.published_at DESC LIMIT 8`
      ).bind(...favIds).all()
      out.feed.official = (results || []).map((r: any) => ({
        company_id: r.company_id, name: r.name, title: r.title, url: r.url, date: String(r.published_at || '').slice(0, 10),
      }))
    }
  } catch (e) { /* company_news 未作成なら graceful に空 */ }

  return c.json(out)
})

export default app