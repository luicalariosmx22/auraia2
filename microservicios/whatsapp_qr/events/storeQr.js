// ✅ Carpeta: events/storeQr.js
// 👉 Almacena QR en archivo o memoria (puedes adaptar a DB o Redis)
const qrcode = require('qrcode');
const fs = require('fs');
const path = require('path');

module.exports = async function storeQr(qr, noraId) {
    const ruta = path.join(__dirname, '..', 'sessions', `${noraId}.png`);
    await qrcode.toFile(ruta, qr);
    console.log(`✅ QR de ${noraId} guardado en ${ruta}`);
};
