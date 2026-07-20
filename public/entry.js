/* =========================================================
   トーキャリ 入口フロー 共通スクリプト
   ナナ(青)・ハルキ(緑) の案内役アバター＋フキダシ（2人が主役／第三者は登場させない）
   ========================================================= */
const NANA_SVG = `
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-label="ナナ">
  <circle cx="32" cy="32" r="31" fill="#eaf3fc"/>
  <path d="M13 41 V30 C13 16 21 9 32 9 C43 9 51 16 51 30 V41 Z" fill="#4a90d9"/>
  <circle cx="32" cy="34" r="13" fill="#ffe4cf"/>
  <path d="M19 31 C21 21 27 17 32 17 C37 17 43 21 45 31 C40 27 36 26 32 26 C28 26 24 27 19 31 Z" fill="#4a90d9"/>
  <circle cx="27" cy="34" r="2" fill="#3a2a20"/>
  <circle cx="37" cy="34" r="2" fill="#3a2a20"/>
  <circle cx="24" cy="38.5" r="2.3" fill="#ffb6a2" opacity="0.7"/>
  <circle cx="40" cy="38.5" r="2.3" fill="#ffb6a2" opacity="0.7"/>
  <path d="M28 40.5 Q32 44 36 40.5" stroke="#3a2a20" stroke-width="1.8" fill="none" stroke-linecap="round"/>
</svg>`;

const HARUKI_SVG = `
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-label="ハルキ">
  <circle cx="32" cy="32" r="31" fill="#e9f6ef"/>
  <path d="M15 35 V29 C15 17 22 10 32 10 C42 10 49 17 49 29 V35 C44 28 38 26 32 26 C26 26 20 28 15 35 Z" fill="#2d8659"/>
  <circle cx="32" cy="35" r="13" fill="#ffe0c4"/>
  <path d="M18 31 C20 21 26 16 32 16 C38 16 44 21 46 31 C40 27 36 26 32 26 C28 26 24 27 18 31 Z" fill="#2d8659"/>
  <circle cx="27" cy="35" r="2" fill="#3a2a20"/>
  <circle cx="37" cy="35" r="2" fill="#3a2a20"/>
  <path d="M28 41 Q32 44 36 41" stroke="#3a2a20" stroke-width="1.8" fill="none" stroke-linecap="round"/>
</svg>`;

function guideHTML(text) {
  return `<div class="guide">
    <div class="guide-faces">
      <span class="mascot"><img src="/images/brand/char_nana.jpg" alt="ナナ" decoding="async"></span>
      <span class="mascot"><img src="/images/brand/char_haruki.jpg" alt="ハルキ" decoding="async"></span>
    </div>
    <div class="guide-bubble">${text}</div>
  </div>`;
}

// #guide プレースホルダに案内役を差し込む（データ取得を待たず即表示）
function mountGuide(text) {
  const el = document.getElementById('guide');
  if (el) el.innerHTML = guideHTML(text);
}

// フッターの横長ロゴをタップでホーム(index)へ。全入口ページ共通の導線。
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.e-footer .brand-panel').forEach(el => {
    el.style.cursor = 'pointer';
    el.setAttribute('role', 'link');
    el.setAttribute('aria-label', 'ホームへ');
    el.addEventListener('click', () => { location.href = '/index.html'; });
  });
});
