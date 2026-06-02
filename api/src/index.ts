import { Hono } from 'hono'
import { cors } from 'hono/cors'

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
        max_tokens: 1024,
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
    const aiText = claudeData.content.find(b => b.type === 'text')?.text ?? ''

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
        languageCode?: string
        name?: string
        ssmlGender?: string
      }
    }>()

    if (!text) {
      return c.json({ error: 'missing text' }, 400)
    }

    const voiceConfig = voice_config ?? { languageCode: 'ja-JP', name: 'ja-JP-Neural2-B', ssmlGender: 'MALE' }

    // キャッシュキー生成（SHA-256）
    const cacheData = JSON.stringify({ text, voiceConfig })
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
          voice: voiceConfig,
          audioConfig: { audioEncoding: 'MP3' },
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
        max_tokens: 256,
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
    const greeting = claudeData.content.find(b => b.type === 'text')?.text ?? ''

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

export default app