/* =========================================================
   purpose_map.js — 目的ナビの「唯一の正」(single source of truth)
   ---------------------------------------------------------
   静的ハブ画面(today.html) と AIキャリアアドバイザー(api/src/advisor.ts) の
   両方がこの目的マップを参照する。片方を直したら両方に効くよう、ここを正とする。

   ★インターフェース厳守（別タブ=advisorがこの「形」に対して実装。形は変えない）:
     { id, label, icon, needsCompany:boolean,
       steps:[ {feature, href, note} ],   // href の {slug} は会社スラッグに置換
       next:[ purposeId, ... ] }
   ・目的ID(8): know / deep / find / es / mensetsu / quiz / ob / omamori
   ・label は「学生の言葉」。機能名を書かない（カードはこの label を表示）。
   ・needsCompany:false（find / omamori）は steps.href に {slug} を含めない。
   ・URL/param 規約は advisor.ts と一致（クリーンURL・id= は company/datasheet/es_kit,
     company= は quiz/room, compare は add=）。
   ・href/steps は設計書§2に準拠（advisor.ts は §2 へ同期が必要＝下記 SYNC メモ参照）。

   ── SYNC メモ（advisor.ts 担当へ）─────────────────────────
   本ファイルは設計書§2どおりに steps を更新済み。advisor.ts の PURPOSE_MAP も
   deep / find / es / mensetsu の steps・next を §2（＝本ファイル）へ揃えること。
   id・needsCompany・icon・URL規約は一致済み。
   ========================================================= */
const PURPOSE_MAP = [
  { id:'know', label:'この会社ってどんな会社？', icon:'🔰', needsCompany:true,
    steps:[
      { feature:'10コマ',       href:'/company?id={slug}',   note:'5分で読める' },
      { feature:'データシート', href:'/datasheet?id={slug}', note:'出典付きの事実' },
    ],
    next:['deep','quiz'] },

  { id:'deep', label:'もっと深く知りたい', icon:'🔎', needsCompany:true,
    steps:[
      { feature:'データシート', href:'/datasheet?id={slug}',            note:'出典付きの事実' },
      { feature:'ニュース',     href:'/company?id={slug}#company-news',  note:'最近の動き' },
      { feature:'企業比較',     href:'/compare?add={slug}',             note:'他社と横並び' },
    ],
    next:['es','quiz'] },

  { id:'find', label:'自分に合う会社を探したい', icon:'🧭', needsCompany:false,
    steps:[
      { feature:'相性診断',   href:'/shindan',   note:'まず自己分析' },
      { feature:'業界研究',   href:'/gyokai',    note:'業界を丸ごと' },
      { feature:'企業を探す', href:'/industry',  note:'会社を一覧から' },
    ],
    next:['know'] },

  { id:'es', label:'ESを書く', icon:'✍️', needsCompany:true,
    steps:[
      { feature:'ESキット',     href:'/es_kit?id={slug}',    note:'志望動機の材料' },
      { feature:'データシート', href:'/datasheet?id={slug}', note:'裏付けの事実' },
    ],
    next:['mensetsu','deep'] },

  { id:'mensetsu', label:'面接の準備をする', icon:'🎤', needsCompany:true,
    steps:[
      { feature:'ESキット',     href:'/es_kit?id={slug}',    note:'想定質問' },
      { feature:'AI OB訪問',    href:'/room?company={slug}', note:'社員に質問' },
      { feature:'クイズ',       href:'/quiz?company={slug}', note:'理解度チェック' },
    ],
    next:['omamori','ob'] },

  { id:'quiz', label:'どれくらい分かっているか試す', icon:'🧠', needsCompany:true,
    steps:[
      { feature:'クイズ', href:'/quiz?company={slug}', note:'会社別で腕試し' },
    ],
    next:['mensetsu','deep'] },

  { id:'ob', label:'社員のリアルを聞く', icon:'🚪', needsCompany:true,
    steps:[
      { feature:'AI OB訪問ルーム', href:'/room?company={slug}', note:'ぶっちゃけを聞く' },
    ],
    next:['mensetsu','es'] },

  { id:'omamori', label:'緊張をほぐす（本番前）', icon:'🛡️', needsCompany:false,
    steps:[
      { feature:'お守り', href:'/omamori.html', note:'本番前に一言' },
    ],
    next:[] },
];

/* 参照ヘルパ（任意・非破壊）。配列 PURPOSE_MAP がインターフェースの正。 */
var PURPOSE_BY_ID = {};
for (var _i = 0; _i < PURPOSE_MAP.length; _i++) PURPOSE_BY_ID[PURPOSE_MAP[_i].id] = PURPOSE_MAP[_i];

if (typeof window !== 'undefined') {
  window.PURPOSE_MAP = PURPOSE_MAP;
  window.PURPOSE_BY_ID = PURPOSE_BY_ID;
  // {slug} 差し替え（advisor.ts の href.replace('{slug}', encodeURIComponent(slug)) と同一挙動）。
  window.tkPurposeHref = function (href, slug) {
    return String(href || '').replace('{slug}', encodeURIComponent(slug || ''));
  };
}
if (typeof module !== 'undefined' && module.exports) module.exports = { PURPOSE_MAP: PURPOSE_MAP, PURPOSE_BY_ID: PURPOSE_BY_ID };
