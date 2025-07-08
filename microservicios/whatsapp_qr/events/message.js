// 👉 Evento que escucha mensajes nuevos y notifica a Flask con retry básico
const axios = require('axios');

module.exports = function setupMessageEvent(client, nombreNora) {
  client.on('message', async (message) => {
    const numero = `+${message.from.replace('@c.us', '')}`;
    const contenido = message.body;
    const timestamp = new Date().toISOString();

    const payload = {
      nombre_nora: nombreNora,
      numero,
      mensaje: contenido,
      timestamp,
    };

    const endpoint = 'https://app.soynoraai.com/webhook_mensaje_qr'; // 🌐 Producción en Railway

    try {
      const res = await axios.post(endpoint, payload);
      console.log(`✅ [${nombreNora}] Mensaje enviado al backend (${res.status})`);
    } catch (error) {
      console.error(`❌ [${nombreNora}] Error al enviar mensaje a backend: ${error.message}`);

      // Reintento simple con delay
      setTimeout(async () => {
        try {
          await axios.post(endpoint, payload);
          console.log(`🔁 [${nombreNora}] Reenvío exitoso del mensaje`);
        } catch (err) {
          console.error(`❌ [${nombreNora}] Reintento fallido: ${err.message}`);
        }
      }, 3000);
    }
  });
};
