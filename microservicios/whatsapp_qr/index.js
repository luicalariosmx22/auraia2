// ✅ Archivo: microservicios/whatsapp_qr/index.js
// 👉 Inicializa microservicio con consulta dinámica a Supabase para obtener nombre_nora
require('dotenv').config();
const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const setupEvents = require('./events');
const { createClient } = require('@supabase/supabase-js');

const app = express();
const PORT = process.env.PORT || 3001;

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const NUMERO_NORA = process.env.NUMERO_NORA;

if (!SUPABASE_URL || !SUPABASE_KEY || !NUMERO_NORA) {
  console.error("❌ ERROR: Variables SUPABASE_URL, SUPABASE_KEY o NUMERO_NORA faltantes");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

(async () => {
  const { data, error } = await supabase
    .from('configuracion_bot')
    .select('nombre_nora')
    .eq('numero_nora', NUMERO_NORA)
    .single();

  if (error || !data) {
    console.error("❌ ERROR: No se encontró nombre_nora para NUMERO_NORA:", NUMERO_NORA);
    process.exit(1);
  }

  const nombre_nora = data.nombre_nora;

  const client = new Client({
    authStrategy: new LocalAuth({ clientId: nombre_nora }),
    puppeteer: { headless: true, args: ['--no-sandbox'] }
  });

  setupEvents(client, nombre_nora);
  client.initialize();

  app.use(express.json());

  app.get('/status', (_, res) => {
    res.send({ nora: nombre_nora, status: 'activo' });
  });

  app.listen(PORT, () => {
    console.log(`🚀 Microservicio Nora "${nombre_nora}" corriendo en puerto ${PORT}`);
  });
})();
