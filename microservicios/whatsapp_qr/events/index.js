// ✅ Carpeta: events/index.js
// 👉 Setup de eventos QR, conexión y mensajes
const setupMessageEvent = require('./message');

function setupEvents(client, nombreNora) {
  client.on('qr', qr => {
    console.log(`🟡 QR disponible para ${nombreNora}`);
    require('./storeQr')(qr, nombreNora);
  });

  client.on('ready', () => {
    console.log(`✅ WhatsApp conectado para ${nombreNora}`);
  });

  setupMessageEvent(client, nombreNora);
}

module.exports = setupEvents;
