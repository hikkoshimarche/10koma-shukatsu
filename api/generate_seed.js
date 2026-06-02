const fs = require('fs');
const path = require('path');

function esc(s) {
  return String(s).replace(/'/g, "''");
}

const promptDir = path.join(__dirname, 'persona_prompts');

const personas = [
  {
    persona_id: 'mitsui_r1_sato',
    company_id: 'mitsui_corp',
    role_code: 'R1',
    display_name: '佐藤健太',
    display_name_kana: 'さとう けんた',
    age: 27,
    department: '金属資源本部 鉄鋼原料部',
    position: 'アソシエイト',
    short_description: '入社4年目の若手エース。日常業務・新人時代のリアル・若手の裁量を語れる',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r1_sato.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-C","speakingRate":1.15,"pitch":1.0}',
    prompt_file: 'r1_sato.md',
  },
  {
    persona_id: 'mitsui_r2_yamada',
    company_id: 'mitsui_corp',
    role_code: 'R2',
    display_name: '山田俊介',
    display_name_kana: 'やまだ しゅんすけ',
    age: 35,
    department: 'エネルギーソリューション本部 LNG事業部',
    position: 'マネージャー',
    short_description: 'プロジェクト規模で語る中堅。カタール駐在3年。出世スピード・転職市場価値',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r2_yamada.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-D","speakingRate":1.05,"pitch":0.0}',
    prompt_file: 'r2_yamada.md',
  },
  {
    persona_id: 'mitsui_r3_takahashi',
    company_id: 'mitsui_corp',
    role_code: 'R3',
    display_name: '高橋誠一郎',
    display_name_kana: 'たかはし せいいちろう',
    age: 48,
    department: '機械・インフラ本部 交通インフラ部',
    position: '部長',
    short_description: '入社25年目の事業部長。採用・組織・面接対策（擬似面接モード）に対応',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r3_takahashi.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-D","speakingRate":0.95,"pitch":-2.0}',
    prompt_file: 'r3_takahashi.md',
  },
  {
    persona_id: 'mitsui_r4_suzuki',
    company_id: 'mitsui_corp',
    role_code: 'R4',
    display_name: '鈴木美咲',
    display_name_kana: 'すずき みさき',
    age: 33,
    department: 'ウェルネス事業本部 ヘルスケア事業部',
    position: 'シニアアソシエイト',
    short_description: '管理職一歩手前の中堅女性。等身大で女性キャリア・両立・社内環境を語れる',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r4_suzuki.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-B","speakingRate":1.0,"pitch":1.0}',
    prompt_file: 'r4_suzuki.md',
  },
  {
    persona_id: 'mitsui_r5_tanaka',
    company_id: 'mitsui_corp',
    role_code: 'R5',
    display_name: '田中浩二',
    display_name_kana: 'たなか こうじ',
    age: 38,
    department: '化学品本部 機能材料部',
    position: 'マネージャー',
    short_description: '海外駐在2回（ヒューストン・シンガポール）、家族帯同。海外駐在のリアルを語れる',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r5_tanaka.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-C","speakingRate":1.1,"pitch":0.5}',
    prompt_file: 'r5_tanaka.md',
  },
  {
    persona_id: 'mitsui_r6_watanabe',
    company_id: 'mitsui_corp',
    role_code: 'R6',
    display_name: '渡辺潤',
    display_name_kana: 'わたなべ じゅん',
    age: 33,
    department: '（元）機械・インフラ本部 → 現職BCG',
    position: 'プロジェクトリーダー（現職BCG）',
    short_description: '4年で三井物産を退職、現職BCG。客観的視点で良し悪し両方を語る退職OB',
    image_url: 'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsui/personas/r6_watanabe.png',
    voice_config: '{"voiceName":"ja-JP-Neural2-D","speakingRate":1.0,"pitch":-1.0}',
    prompt_file: 'r6_watanabe.md',
  },
];

const rows = personas.map(p => {
  const prompt = fs.readFileSync(path.join(promptDir, p.prompt_file), 'utf-8');
  return (
    `INSERT OR IGNORE INTO personas ` +
    `(persona_id, company_id, role_code, display_name, display_name_kana, age, department, position, short_description, image_url, system_prompt, voice_config, is_active) VALUES ` +
    `('${esc(p.persona_id)}', '${esc(p.company_id)}', '${esc(p.role_code)}', '${esc(p.display_name)}', '${esc(p.display_name_kana)}', ${p.age}, '${esc(p.department)}', '${esc(p.position)}', '${esc(p.short_description)}', '${esc(p.image_url)}', '${esc(prompt)}', '${esc(p.voice_config)}', 1);`
  );
});

const sql = `-- Seed: 三井物産 6人格 personas\n-- Generated: ${new Date().toISOString()}\n\n${rows.join('\n\n')}\n`;

fs.writeFileSync(path.join(__dirname, 'seed_mitsui_personas.sql'), sql, 'utf-8');
console.log('Generated seed_mitsui_personas.sql');
personas.forEach(p => {
  const prompt = fs.readFileSync(path.join(promptDir, p.prompt_file), 'utf-8');
  console.log(`  ${p.persona_id}: system_prompt ${prompt.length} chars`);
});
