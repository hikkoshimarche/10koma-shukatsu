-- Phase: トーキャリ・ルーム MVP
-- 3 new tables: personas, room_conversations, room_messages

CREATE TABLE IF NOT EXISTS personas (
  persona_id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  role_code TEXT NOT NULL,
  display_name TEXT NOT NULL,
  display_name_kana TEXT,
  age INTEGER,
  department TEXT,
  position TEXT,
  short_description TEXT,
  image_url TEXT,
  system_prompt TEXT NOT NULL,
  voice_config TEXT,
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_personas_company ON personas(company_id);

CREATE TABLE IF NOT EXISTS room_conversations (
  conversation_id TEXT PRIMARY KEY,
  line_user_id TEXT NOT NULL,
  company_id TEXT NOT NULL,
  persona_id TEXT NOT NULL,
  started_at TEXT DEFAULT (datetime('now')),
  last_message_at TEXT DEFAULT (datetime('now')),
  message_count INTEGER DEFAULT 0,
  FOREIGN KEY (persona_id) REFERENCES personas(persona_id)
);
CREATE INDEX IF NOT EXISTS idx_room_conv_user ON room_conversations(line_user_id, persona_id);

CREATE TABLE IF NOT EXISTS room_messages (
  message_id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  audio_url TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (conversation_id) REFERENCES room_conversations(conversation_id)
);
CREATE INDEX IF NOT EXISTS idx_room_msg_conv ON room_messages(conversation_id, created_at);
