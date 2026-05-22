import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
  ASSETS: R2Bucket
}

const app = new Hono<{ Bindings: Bindings }>()

// CORSを全オリジンに許可（LIFFフロントからのリクエスト対応）
app.use('*', cors())

// ヘルスチェック
app.get('/api/health', (c) => {
  return c.json({ ok: true })
})

// ユーザーのupsert（LINEログイン後に呼ぶ）
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

// 会社詳細（10コマ・既存like/bookmark状態・同業他社レコメンド込み）
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

  // 同業他社レコメンド（最大5社、自社を除く）
  const { results: recommendations } = await c.env.DB.prepare(
    `SELECT id, name, description, thumbnail_url
     FROM companies
     WHERE industry_id = ? AND id != ?
     ORDER BY id
     LIMIT 5`
  )
    .bind(company.industry_id, id)
    .all()

  // 既存like / bookmark 状態（user_idが渡された時のみ）
  let liked = false
  let bookmarked = false
  let likedPanels: number[] = []

  if (userId) {
    const likeRow = await c.env.DB.prepare(
      `SELECT 1 FROM likes
       WHERE line_user_id = ? AND content_type = 'company' AND content_id = ?`
    )
      .bind(userId, id)
      .first()
    liked = !!likeRow

    const bookmarkRow = await c.env.DB.prepare(
      'SELECT 1 FROM bookmarks WHERE line_user_id = ? AND company_id = ?'
    )
      .bind(userId, id)
      .first()
    bookmarked = !!bookmarkRow

    // パネル単位のいいねは content_id = `${company_id}:${panel_num}` で保存
    const { results: panelLikes } = await c.env.DB.prepare(
      `SELECT content_id FROM likes
       WHERE line_user_id = ? AND content_type = 'panel' AND content_id LIKE ?`
    )
      .bind(userId, `${id}:%`)
      .all<{ content_id: string }>()

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

// いいね toggle（company/panel共通）
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
  )
    .bind(line_user_id, content_type, content_id)
    .first()

  if (existing) {
    await c.env.DB.prepare(
      'DELETE FROM likes WHERE line_user_id = ? AND content_type = ? AND content_id = ?'
    )
      .bind(line_user_id, content_type, content_id)
      .run()
    return c.json({ liked: false })
  } else {
    await c.env.DB.prepare(
      'INSERT INTO likes (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
    )
      .bind(line_user_id, content_type, content_id)
      .run()
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
  )
    .bind(line_user_id, company_id)
    .first()

  if (existing) {
    await c.env.DB.prepare(
      'DELETE FROM bookmarks WHERE line_user_id = ? AND company_id = ?'
    )
      .bind(line_user_id, company_id)
      .run()
    return c.json({ bookmarked: false })
  } else {
    await c.env.DB.prepare(
      'INSERT INTO bookmarks (line_user_id, company_id) VALUES (?, ?)'
    )
      .bind(line_user_id, company_id)
      .run()
    return c.json({ bookmarked: true })
  }
})

// 閲覧ログ記録
app.post('/api/log-view', async (c) => {
  const { line_user_id, content_type, content_id } = await c.req.json<{
    line_user_id: string
    content_type: string
    content_id: string
  }>()

  await c.env.DB.prepare(
    'INSERT INTO view_logs (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
  )
    .bind(line_user_id, content_type, content_id)
    .run()

  return c.json({ ok: true })
})

// シェアログ記録
app.post('/api/share-log', async (c) => {
  const { line_user_id, content_type, content_id } = await c.req.json<{
    line_user_id: string
    content_type: string
    content_id: string
  }>()

  await c.env.DB.prepare(
    'INSERT INTO share_logs (line_user_id, content_type, content_id) VALUES (?, ?, ?)'
  )
    .bind(line_user_id, content_type, content_id)
    .run()

  return c.json({ ok: true })
})

export default app