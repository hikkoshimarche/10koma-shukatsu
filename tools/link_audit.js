#!/usr/bin/env node
/*
 * link_audit.js — トーキャリ web app 全ページ リンク健全性監査
 * ------------------------------------------------------------
 * 使い方:
 *   node tools/link_audit.js [baseUrl]
 *   （既定 baseUrl = https://10koma-shukatsu.pages.dev）
 *
 * 何をするか:
 *   - App HTML ページ + LP ページを列挙し、LIFF スタブを注入して 1 枚ずつ描画。
 *   - 各ページの a[href] を全て収集（ミニナビ #tk-mininav の 4 リンク含む=これらは <a>）。
 *     加えて .co-chip / [data-href] など JS 遷移候補も収集して記録。
 *   - internal ターゲットは (a) request.get で最終ステータス（リダイクト追従）、
 *     (b) 実ナビゲーションで描画確認（本文あり・.error-text/「見つかりません」等が無い）を検証。
 *   - external / mailto / tel / lin.ee は URL を記録（監査を落とさない）。
 *   - 特別フロー（talkcareer.jp リダイレクト, index 挙動, bookmarks→mypage,
 *     gyokai→industry フィルタ, 戻るボタン, howto 特集リンク, LP フッター/ヘッダ）を明示検証。
 *   - Markdown 結果表 + 集計 + NG 詳細を stdout に出力。NG が 1 件でもあれば exit 1。
 *
 * 依存: Playwright（下記固定パス）のみ。channel:'chrome'。
 */

const PW_PATH = '/Users/oscardodds/Desktop/Claude/FPスクレイピング/node_modules/playwright';
const { chromium } = require(PW_PATH);

const BASE = (process.argv[2] || 'https://10koma-shukatsu.pages.dev').replace(/\/$/, '');
const MARKETING = 'https://talkcareer.jp';

// id を要するページの実データ
const CID = 'denso';
const CNAME = encodeURIComponent('デンソー');

// 監査対象ページ（path は BASE 相対）
const APP_PAGES = [
  ['index', '/index.html'],
  ['home', '/home.html'],
  ['hub', '/hub.html'],
  ['howto', '/howto.html'],
  ['gyokai', '/gyokai.html'],
  ['industry', '/industry.html'],
  ['company-list', '/company-list.html'],
  ['company', `/company.html?id=${CID}`],
  ['compare', '/compare.html'],
  ['datasheet', `/datasheet.html?id=${CID}`],
  ['es_kit', `/es_kit.html?id=${CID}`],
  ['es_guide', '/es_guide.html'],
  ['quiz', `/quiz.html?company=${CID}&name=${CNAME}`],
  ['shindan', '/shindan.html'],
  ['mypage', '/mypage.html'],
  ['bookmarks', '/bookmarks.html'],
  ['room', `/room.html?company=${CID}&name=${CNAME}`],
  ['obs', '/obs.html'],
  ['videos', '/videos.html'],
  ['omamori', '/omamori.html'],
  ['chat', '/chat.html'],
];
const LP_PAGES = [
  ['lp/index', '/lp/'],
  ['lp/features', '/lp/features'],
  ['lp/about', '/lp/about'],
  ['lp/companies', '/lp/companies'],
  ['lp/contact', '/lp/contact'],
  ['lp/terms', '/lp/terms'],
  ['lp/privacy', '/lp/privacy'],
];

const ERROR_MARKERS = ['見つかりません', 'お探しのページ', 'Not Found', '404 ', 'ページが存在'];

function classify(url) {
  if (!url) return 'empty';
  if (url.startsWith('mailto:')) return 'external';
  if (url.startsWith('tel:')) return 'external';
  if (url.startsWith('javascript:')) return 'js';
  let u;
  try { u = new URL(url, BASE); } catch (e) { return 'invalid'; }
  const baseHost = new URL(BASE).host;
  if (u.host === baseHost) return 'internal';
  return 'external';
}

function normKey(url) {
  try { const u = new URL(url, BASE); return u.pathname.replace(/\.html$/, '') + u.search; }
  catch (e) { return url; }
}

async function stubContext(browser) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.route('**/liff/edge/2/sdk.js', r => r.abort());
  await ctx.addInitScript(() => {
    window.liff = {
      init: () => Promise.resolve(), isLoggedIn: () => true, isInClient: () => false,
      login: () => {}, getProfile: () => Promise.resolve({ userId: 'guest-preview', displayName: 'P' }),
      openWindow: () => {}, isApiAvailable: () => false,
    };
  });
  return ctx;
}

async function settle(page, ms = 1200) {
  try { await page.waitForLoadState('networkidle', { timeout: 15000 }); } catch (e) {}
  await page.waitForTimeout(ms);
}

// 1 ページ内の全リンク/遷移候補を収集
async function collectLinks(page) {
  return await page.evaluate(() => {
    const out = [];
    const clip = s => (s || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    document.querySelectorAll('a[href]').forEach(a => {
      out.push({ kind: 'a', href: a.href, raw: a.getAttribute('href'),
        text: clip(a.innerText || a.getAttribute('aria-label') || a.title) });
    });
    // JS 遷移候補（記録のみ）
    document.querySelectorAll('[data-href],.co-chip').forEach(el => {
      const dh = el.getAttribute('data-href');
      out.push({ kind: 'js', href: dh ? new URL(dh, location.href).href : null,
        raw: dh || '(js-click)', text: clip(el.innerText || el.getAttribute('aria-label')) });
    });
    return out;
  });
}

// internal ターゲットのステータス + 描画を検証（結果はキャッシュ）
const verifyCache = new Map();
async function verifyInternal(ctx, absUrl) {
  const key = normKey(absUrl);
  if (verifyCache.has(key)) return verifyCache.get(key);
  const res = { status: null, redirected: false, chain: [], renders: false, note: '' };
  // (a) ステータス（APIRequest はリダイレクト追従。最終 URL 差で redirect 判定）
  try {
    const req = await ctx.request.get(absUrl, { timeout: 20000 });
    res.status = req.status();
    const finalUrl = req.url();
    if (normKey(finalUrl) !== normKey(absUrl)) { res.redirected = true; res.chain = [absUrl, finalUrl]; }
  } catch (e) { res.note += 'status-err:' + e.message.slice(0, 60) + '; '; }
  // (b) 描画
  const page = await ctx.newPage();
  try {
    const resp = await page.goto(absUrl, { waitUntil: 'domcontentloaded', timeout: 25000 });
    await settle(page, 900);
    const info = await page.evaluate((markers) => {
      const bodyLen = (document.body ? document.body.innerText : '').replace(/\s+/g, '').length;
      let visErr = null;
      document.querySelectorAll('.error-text').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.display !== 'none' && cs.visibility !== 'hidden' && el.offsetParent !== null) {
          const t = (el.innerText || '').trim(); if (t) visErr = t.slice(0, 60);
        }
      });
      const txt = (document.body ? document.body.innerText : '');
      const marker = markers.find(m => txt.includes(m)) || null;
      return { bodyLen, visErr, marker, title: document.title };
    }, ERROR_MARKERS);
    if (res.status == null && resp) res.status = resp.status();
    if (info.visErr) { res.renders = false; res.note += 'visible-error:' + info.visErr + '; '; }
    else if (info.marker) { res.renders = false; res.note += 'marker:' + info.marker + '; '; }
    else if (info.bodyLen < 40) { res.renders = false; res.note += 'empty-body(' + info.bodyLen + '); '; }
    else res.renders = true;
  } catch (e) {
    res.renders = false; res.note += 'nav-err:' + e.message.slice(0, 60) + '; ';
  } finally { await page.close(); }
  verifyCache.set(key, res);
  return res;
}

async function externalStatus(ctx, url) {
  if (url.startsWith('mailto:') || url.startsWith('tel:')) return 'n/a';
  try {
    const r = await ctx.request.get(url, { timeout: 12000, maxRedirects: 5 });
    return String(r.status());
  } catch (e) { return 'unchecked'; }
}

const rows = [];
function addRow(source, text, target, type, status, renders, verdict, note) {
  rows.push({ source, text, target, type, status, renders, verdict, note });
}

async function auditPage(ctx, [name, path]) {
  const url = BASE + path;
  const page = await ctx.newPage();
  let links = [];
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await settle(page, 1200);
    links = await collectLinks(page);
  } catch (e) {
    addRow(name, '(PAGE LOAD)', url, 'internal', 'LOAD-ERR', false, 'NG', e.message.slice(0, 80));
    await page.close();
    return;
  }
  await page.close();

  // ページ内で (href,text) 重複排除
  const seen = new Set();
  for (const l of links) {
    const dedupe = (l.href || l.raw) + '|' + l.text;
    if (seen.has(dedupe)) continue; seen.add(dedupe);
    const type = classify(l.href || l.raw);
    const label = l.text || (l.kind === 'js' ? '(co-chip/js)' : '(no-text)');

    if (l.kind === 'js' && !l.href) {
      addRow(name, label, l.raw, 'js-nav', 'n/a', 'n/a', 'INFO', 'JS遷移(静的解決不可・記録のみ)');
      continue;
    }
    if (type === 'external') {
      const st = await externalStatus(ctx, l.href || l.raw);
      addRow(name, label, l.href || l.raw, 'external', st, 'n/a',
        (st === 'unchecked' || /^[45]/.test(st)) ? 'OK*' : 'OK', 'EXTERNAL');
      continue;
    }
    if (type === 'internal') {
      const v = await verifyInternal(ctx, l.href);
      const ok = (v.status === 200) && v.renders;
      const noteBits = [];
      if (v.redirected) noteBits.push('redirect→' + v.status);
      if (v.note) noteBits.push(v.note.trim());
      addRow(name, label + (l.kind === 'js' ? ' [co-chip]' : ''), l.href, 'internal',
        v.status == null ? 'ERR' : String(v.status), v.renders ? 'yes' : 'no',
        ok ? 'OK' : 'NG', noteBits.join(' '));
      continue;
    }
    if (type === 'empty' || type === 'invalid' || type === 'js') {
      addRow(name, label, l.raw, type, 'n/a', 'n/a',
        type === 'js' ? 'INFO' : 'NG', type === 'js' ? 'javascript: href' : (type + ' href'));
    }
  }
}

// ---- 特別フロー ----
async function specialFlows(ctx) {
  const flow = 'FLOW';
  // 1) talkcareer.jp リダイレクト/リライト
  {
    const page = await ctx.newPage();
    try {
      const resp = await page.goto(MARKETING + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await settle(page, 1000);
      const info = await page.evaluate(() => ({
        url: location.href, title: document.title,
        hasLP: !!document.querySelector('.lp, [class*="lp-"], link[href*="lp.css"]') ||
               /トーキャリ|talkcareer|就活/i.test(document.body.innerText.slice(0, 400)),
        bodyLen: document.body.innerText.replace(/\s+/g, '').length,
      }));
      const ok = resp && resp.status() < 400 && info.bodyLen > 40;
      addRow(flow, 'talkcareer.jp/ → LP', info.url, 'redirect',
        resp ? String(resp.status()) : 'ERR', info.hasLP ? 'yes' : 'no',
        ok ? 'OK' : 'NG', `finalURL=${info.url} title="${info.title}" LPmarker=${info.hasLP}`);
    } catch (e) { addRow(flow, 'talkcareer.jp/ → LP', MARKETING, 'redirect', 'ERR', 'no', 'NG', e.message.slice(0, 80)); }
    await page.close();
  }
  // 2) pages.dev / と /index.html
  for (const p of ['/', '/index.html']) {
    const page = await ctx.newPage();
    try {
      const resp = await page.goto(BASE + p, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await settle(page, 1400);
      const info = await page.evaluate(() => ({ url: location.href, len: document.body.innerText.replace(/\s+/g, '').length }));
      addRow(flow, `pages.dev ${p}`, info.url, 'internal', resp ? String(resp.status()) : 'ERR',
        info.len > 10 ? 'yes' : 'no', (resp && resp.status() < 400) ? 'OK' : 'NG',
        `finalURL=${info.url} bodyLen=${info.len}`);
    } catch (e) { addRow(flow, `pages.dev ${p}`, BASE + p, 'internal', 'ERR', 'no', 'NG', e.message.slice(0, 80)); }
    await page.close();
  }
  // 3) bookmarks → mypage
  {
    const page = await ctx.newPage();
    try {
      await page.goto(BASE + '/bookmarks.html', { waitUntil: 'domcontentloaded', timeout: 25000 });
      await settle(page, 1400);
      const info = await page.evaluate(() => ({ url: location.href, len: document.body.innerText.replace(/\s+/g, '').length }));
      addRow(flow, 'bookmarks 挙動', info.url, 'internal', '200', info.len > 40 ? 'yes' : 'no',
        info.len > 40 ? 'OK' : 'NG', `landedURL=${info.url}`);
    } catch (e) { addRow(flow, 'bookmarks 挙動', BASE + '/bookmarks.html', 'internal', 'ERR', 'no', 'NG', e.message.slice(0, 80)); }
    await page.close();
  }
  // 4) gyokai → industry フィルタ（総合商社 / メーカー）
  for (const ind of ['総合商社', 'メーカー']) {
    const page = await ctx.newPage();
    try {
      const target = BASE + '/industry.html?ind=' + encodeURIComponent(ind);
      await page.goto(target, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await settle(page, 1600);
      const info = await page.evaluate((ind) => {
        const body = document.body.innerText;
        const m = body.match(/(\d+)\s*社/);
        // アクティブなチップ判定（.on/.active/aria-selected など）
        let activeChip = null;
        document.querySelectorAll('.chip,[class*="chip"],[role="tab"]').forEach(el => {
          const cls = el.className || '';
          if (/on|active|selected/.test(cls) || el.getAttribute('aria-selected') === 'true') {
            const t = (el.innerText || '').trim(); if (t && t.includes(ind.slice(0, 2))) activeChip = t.slice(0, 20);
          }
        });
        return { url: location.href, count: m ? m[1] : null, activeChip, len: body.replace(/\s+/g, '').length };
      }, ind);
      addRow(flow, `gyokai→industry (${ind})`, info.url, 'internal', '200',
        info.len > 40 ? 'yes' : 'no', info.count ? 'OK' : 'OK*',
        `件数=${info.count || '?'}社 activeChip=${info.activeChip || '未検出'}`);
    } catch (e) { addRow(flow, `gyokai→industry (${ind})`, ind, 'internal', 'ERR', 'no', 'NG', e.message.slice(0, 80)); }
    await page.close();
  }
  // 5) 戻るボタン: company?from=list&fromInd=総合商社 → 業界一覧(フィルタ)
  {
    const page = await ctx.newPage();
    try {
      const from = BASE + `/company.html?id=${CID}&from=list&fromInd=${encodeURIComponent('総合商社')}`;
      await page.goto(from, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await settle(page, 1400);
      const dest = await page.evaluate(() => {
        return (window.tkBackDest ? window.tkBackDest('/home.html') : { href: '(no tkBackDest)', label: '?' });
      });
      const ok = /industry/.test(dest.href) && /ind=/.test(dest.href);
      addRow(flow, '戻る解決(company from=list)', dest.href, 'internal', 'n/a', 'n/a',
        ok ? 'OK' : 'NG', `tkBackDest=${dest.href} label=${dest.label}`);
    } catch (e) { addRow(flow, '戻る解決(company from=list)', '-', 'internal', 'ERR', 'n/a', 'NG', e.message.slice(0, 80)); }
    await page.close();
  }
}

function mdEscape(s) { return String(s == null ? '' : s).replace(/\|/g, '\\|').replace(/\n/g, ' '); }

function printReport() {
  const lines = [];
  lines.push('# トーキャリ リンク監査結果  base=' + BASE);
  lines.push('');
  lines.push('| Source Page | Link Text | Target URL | Type | Final Status | Renders? | Verdict | Note |');
  lines.push('|---|---|---|---|---|---|---|---|');
  for (const r of rows) {
    lines.push('| ' + [r.source, r.text, r.target, r.type, r.status, r.renders, r.verdict, r.note]
      .map(mdEscape).join(' | ') + ' |');
  }
  const total = rows.length;
  const ng = rows.filter(r => r.verdict === 'NG');
  const ok = rows.filter(r => r.verdict === 'OK' || r.verdict === 'OK*').length;
  const info = rows.filter(r => r.verdict === 'INFO').length;
  lines.push('');
  lines.push('## 集計');
  lines.push(`- TOTAL: ${total}`);
  lines.push(`- OK (OK/OK*): ${ok}`);
  lines.push(`- NG: ${ng.length}`);
  lines.push(`- INFO (JS遷移・記録のみ): ${info}`);
  lines.push('');
  lines.push('## NG 詳細');
  if (!ng.length) lines.push('- なし ✅');
  else for (const r of ng) lines.push(`- [${r.source}] "${r.text}" → ${r.target} | status=${r.status} renders=${r.renders} | ${r.note}`);
  console.log(lines.join('\n'));
  return ng.length;
}

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await stubContext(browser);
  const ALL = [...APP_PAGES, ...LP_PAGES];
  for (const p of ALL) {
    process.stderr.write(`auditing ${p[0]} ...\n`);
    await auditPage(ctx, p);
  }
  process.stderr.write('running special flows ...\n');
  await specialFlows(ctx);
  await browser.close();
  const ngCount = printReport();
  process.exit(ngCount > 0 ? 1 : 0);
})().catch(e => { console.error('FATAL', e); process.exit(2); });
