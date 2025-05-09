// ✅ Archivo: docker/whatsapp_worker/worker.js
// 👉 Genera QR, persiste sesión en Supabase y emite eventos Socket.IO
import wppconnect from 'wppconnect';
import { createClient } from '@supabase/supabase-js';
import { io } from 'socket.io-client';

const {
  SUPABASE_URL,
  SUPABASE_KEY,        // 🔄 usamos el nombre presente en Railway
  NOMBRE_NORA,
  SOCKET_SERVER_URL
} = process.env;

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
const socket = io(SOCKET_SERVER_URL, { transports: ['websocket'] });

async function loadSession() {
  const { data } = await supabase
    .from('whatsapp_sessions')
    .select('session_data')
    .eq('nombre_nora', NOMBRE_NORA)
    .single();
  return data?.session_data || null;
}

async function saveSession(session) {
  await supabase.rpc('upsert_whatsapp_session', {
    p_nombre_nora: NOMBRE_NORA,
    p_session_data: session
  });
}

(async () => {
  const sessionData = await loadSession();
  wppconnect
    .create({
      session: NOMBRE_NORA,
      catchQR: (base64QR, asciiQR, attempts) => {
        socket.emit('whatsapp_qr', { nombre_nora: NOMBRE_NORA, qr: base64QR });
      },
      statusFind: (statusSession, session) => {
        socket.emit('whatsapp_status', { nombre_nora: NOMBRE_NORA, status: statusSession });
      },
      headless: true,
      browserArgs: ['--no-sandbox'],
      sessionData
    })
    .then((client) => {
      socket.emit('whatsapp_ready', { nombre_nora: NOMBRE_NORA });
      client.onMessage(async (message) => {
        await supabase.from('whatsapp_mensajes').insert({
          nombre_nora: NOMBRE_NORA,
          telefono: message.from,
          mensaje: message.body,
          direction: 'in'
        });
        socket.emit('whatsapp_in', { nombre_nora: NOMBRE_NORA, ...message });
      });
      client.onAck(async (ack) => {
        if (ack.ack === 3) {
          socket.emit('whatsapp_out_delivered', { nombre_nora: NOMBRE_NORA, ack });
        }
      });
      client.onStateChange((state) => {
        socket.emit('whatsapp_state', { nombre_nora: NOMBRE_NORA, state });
      });
      client.defaultSender = async (data) => {
        await supabase.from('whatsapp_mensajes').insert({
          nombre_nora: NOMBRE_NORA,
          telefono: data.to,
          mensaje: data.body,
          direction: 'out'
        });
      };
      client.onStreamChange(() => saveSession(client.getSessionTokenBrowser()));
    })
    .catch((e) => socket.emit('whatsapp_error', { nombre_nora: NOMBRE_NORA, error: e.message }));
})();
