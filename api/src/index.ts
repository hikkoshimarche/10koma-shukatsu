import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
  ASSETS: R2Bucket
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

export default app