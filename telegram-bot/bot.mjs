import { createReadStream, readFileSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import pg from 'pg';

const { Pool } = pg;
const token = readSecret(process.env.TELEGRAM_BOT_TOKEN_FILE);
const pairingCode = readSecret(process.env.TELEGRAM_PAIRING_CODE_FILE);
const apiBase = `https://api.telegram.org/bot${token}`;
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'postgres',
  port: Number(process.env.POSTGRES_PORT || 5432),
  database: process.env.POSTGRES_DB,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  max: 3,
});

function readSecret(path) {
  if (!path) throw new Error('Secret file path is missing');
  const value = readFileSync(path, 'utf8').trim();
  if (!value) throw new Error(`Secret file is empty: ${path}`);
  return value;
}

function safeEqual(a, b) {
  const left = Buffer.from(String(a));
  const right = Buffer.from(String(b));
  return left.length === right.length && timingSafeEqual(left, right);
}

async function telegram(method, payload = {}) {
  const response = await fetch(`${apiBase}/${method}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(70000),
  });
  const data = await response.json();
  if (!data.ok) throw new Error(`Telegram ${method}: ${data.description || response.status}`);
  return data.result;
}

async function sendPhoto(chatId, imagePath, caption, replyMarkup) {
  const form = new FormData();
  form.set('chat_id', String(chatId));
  if (caption) form.set('caption', caption);
  if (replyMarkup) form.set('reply_markup', JSON.stringify(replyMarkup));
  const bytes = readFileSync(imagePath);
  form.set('photo', new Blob([bytes], { type: 'image/png' }), imagePath.split('/').pop());
  const response = await fetch(`${apiBase}/sendPhoto`, {
    method: 'POST',
    body: form,
    signal: AbortSignal.timeout(70000),
  });
  const data = await response.json();
  if (!data.ok) throw new Error(`Telegram sendPhoto: ${data.description || response.status}`);
  return data.result;
}

function postText(post) {
  const tags = Array.isArray(post.hashtags) ? post.hashtags.join(' ') : '';
  return [post.hook, post.body, post.cta, tags].map((part) => String(part || '').trim()).filter(Boolean).join('\n\n');
}

function keyboard(postId) {
  return {
    inline_keyboard: [
      [{ text: '✅ Onayla ve planla', callback_data: `r:a:${postId}` }],
      [
        { text: '✍️ Metni yenile', callback_data: `r:t:${postId}` },
        { text: '🎨 Görseli yenile', callback_data: `r:i:${postId}` },
      ],
      [{ text: '🔄 İkisini yenile', callback_data: `r:b:${postId}` }],
      [{ text: '❌ Reddet', callback_data: `r:x:${postId}` }],
    ],
  };
}

async function getState() {
  const { rows } = await pool.query('SELECT * FROM telegram_bot_state WHERE singleton = true');
  return rows[0];
}

async function saveOffset(offset) {
  await pool.query('UPDATE telegram_bot_state SET update_offset = $1, updated_at = now() WHERE singleton = true', [offset]);
}

async function handleMessage(message) {
  const text = String(message.text || '').trim();
  if (!text.startsWith('/pair ')) return;
  const suppliedCode = text.slice(6).trim();
  const state = await getState();
  if (state.paired_chat_id) {
    await telegram('sendMessage', { chat_id: message.chat.id, text: 'Bu bot daha önce bir Telegram hesabıyla eşleştirilmiş.' });
    return;
  }
  if (!safeEqual(suppliedCode, pairingCode)) {
    await telegram('sendMessage', { chat_id: message.chat.id, text: 'Eşleştirme kodu geçersiz.' });
    return;
  }
  await pool.query(
    'UPDATE telegram_bot_state SET paired_chat_id = $1, paired_username = $2, paired_at = now(), updated_at = now() WHERE singleton = true AND paired_chat_id IS NULL',
    [message.chat.id, message.from?.username || null],
  );
  await telegram('sendMessage', { chat_id: message.chat.id, text: '✅ Eşleştirme tamamlandı. Yeni LinkedIn taslakları bu sohbete gönderilecek.' });
}

async function handleCallback(callback) {
  const state = await getState();
  if (!state.paired_chat_id || String(callback.message?.chat?.id) !== String(state.paired_chat_id)) {
    await telegram('answerCallbackQuery', { callback_query_id: callback.id, text: 'Bu işlem için yetkiniz yok.', show_alert: true });
    return;
  }
  const match = /^r:([atibx]):([0-9a-f-]{36})$/i.exec(String(callback.data || ''));
  if (!match) {
    await telegram('answerCallbackQuery', { callback_query_id: callback.id, text: 'Geçersiz işlem.', show_alert: true });
    return;
  }
  const [, action, postId] = match;
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const locked = await client.query('SELECT id, evidence_id, approval_status FROM content_posts WHERE id = $1::uuid FOR UPDATE', [postId]);
    const post = locked.rows[0];
    if (!post || post.approval_status !== 'needs_review') {
      await client.query('ROLLBACK');
      await telegram('answerCallbackQuery', { callback_query_id: callback.id, text: 'Bu taslak daha önce işlenmiş.', show_alert: true });
      return;
    }
    let feedback;
    if (action === 'a') {
      await client.query(`UPDATE content_posts SET approval_status = 'approved', approved_at = now(), reviewer_notes = 'Telegram üzerinden onaylandı', scheduled_at = CASE WHEN now() < ((date_trunc('week', now() AT TIME ZONE 'Europe/Istanbul') + interval '1 day 17 hours 45 minutes') AT TIME ZONE 'Europe/Istanbul') THEN ((date_trunc('week', now() AT TIME ZONE 'Europe/Istanbul') + interval '1 day 17 hours 45 minutes') AT TIME ZONE 'Europe/Istanbul') ELSE ((date_trunc('week', now() AT TIME ZONE 'Europe/Istanbul') + interval '8 days 17 hours 45 minutes') AT TIME ZONE 'Europe/Istanbul') END WHERE id = $1::uuid`, [postId]);
      feedback = '✅ Onaylandı ve bir sonraki salı 17:45 için planlandı.';
    } else if (action === 'x') {
      await client.query("UPDATE content_posts SET approval_status = 'rejected', reviewer_notes = 'Telegram üzerinden reddedildi' WHERE id = $1::uuid", [postId]);
      feedback = '❌ Taslak reddedildi.';
    } else if (action === 'i') {
      await client.query("UPDATE content_posts SET image_path = NULL, image_model = NULL, reviewer_notes = 'Telegram üzerinden yeni görsel istendi' WHERE id = $1::uuid", [postId]);
      feedback = '🎨 Yeni görsel üretim kuyruğuna alındı.';
    } else {
      const nextStatus = action === 't' ? 'regenerating_text' : 'regenerating_both';
      await client.query('UPDATE content_posts SET approval_status = $2, reviewer_notes = $3 WHERE id = $1::uuid', [postId, nextStatus, action === 't' ? 'Telegram üzerinden yeni metin istendi' : 'Telegram üzerinden yeni metin ve görsel istendi']);
      await client.query("INSERT INTO system_events (event_type, entity_type, entity_id, payload) VALUES ($1, 'content_post', $2::uuid, jsonb_build_object('source', 'telegram'))", [action === 't' ? 'telegram_regenerate_text' : 'telegram_regenerate_both', postId]);
      feedback = action === 't' ? '✍️ Yeni metin üretim kuyruğuna alındı.' : '🔄 Yeni metin ve görsel üretim kuyruğuna alındı.';
    }
    await client.query("UPDATE telegram_review_deliveries SET action = $2, action_at = now() WHERE post_id = $1::uuid AND post_updated_at = (SELECT max(post_updated_at) FROM telegram_review_deliveries WHERE post_id = $1::uuid)", [postId, action]);
    await client.query('COMMIT');
    await telegram('answerCallbackQuery', { callback_query_id: callback.id, text: feedback });
    await telegram('editMessageReplyMarkup', { chat_id: state.paired_chat_id, message_id: callback.message.message_id, reply_markup: { inline_keyboard: [] } });
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

async function pollTelegram() {
  const state = await getState();
  const updates = await telegram('getUpdates', { offset: Number(state.update_offset), timeout: 25, allowed_updates: ['message', 'callback_query'] });
  for (const update of updates) {
    try {
      if (update.message) await handleMessage(update.message);
      if (update.callback_query) await handleCallback(update.callback_query);
    } finally {
      await saveOffset(update.update_id + 1);
    }
  }
}

async function dispatchReviews() {
  const state = await getState();
  if (!state.paired_chat_id) return;
  const { rows } = await pool.query(`
    SELECT p.id, p.hook, p.body, p.cta, p.hashtags, p.image_path, p.updated_at
    FROM content_posts p
    WHERE p.approval_status = 'needs_review'
      AND p.image_path IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM telegram_review_deliveries d
        WHERE d.post_id = p.id AND d.action IS NULL
      )
    ORDER BY p.created_at
    LIMIT 1
  `);
  const post = rows[0];
  if (!post) return;
  const text = postText(post);
  let photo;
  let message;
  if (text.length <= 1024) {
    photo = await sendPhoto(state.paired_chat_id, post.image_path, text, keyboard(post.id));
    message = photo;
  } else {
    photo = await sendPhoto(state.paired_chat_id, post.image_path, 'Yeni LinkedIn taslağı hazır. Metin ve karar düğmeleri aşağıdaki mesajda.');
    message = await telegram('sendMessage', {
      chat_id: state.paired_chat_id,
      text,
      reply_markup: keyboard(post.id),
    });
  }
  await pool.query(
    'INSERT INTO telegram_review_deliveries (post_id, post_updated_at, chat_id, photo_message_id, text_message_id) VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING',
    [post.id, post.updated_at, state.paired_chat_id, photo.message_id, message.message_id],
  );
}

async function main() {
  await pool.query('SELECT 1');
  await telegram('getMe');
  console.log('Telegram review bot is ready');
  for (;;) {
    try {
      await pollTelegram();
      await dispatchReviews();
    } catch (error) {
      console.error(error.message);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
