// ✅ Carpeta: sessions/qr.js
// 👉 Generador de QR a partir de cliente WhatsApp
const fs = require('fs');
const path = require('path');

async function generateQR(noraId, crearCliente, sessions) {
    if (!sessions[noraId]) crearCliente(noraId);
    const ruta = path.join(__dirname, `${noraId}.png`);
    if (fs.existsSync(ruta)) {
        const qrBase64 = fs.readFileSync(ruta).toString('base64');
        return `data:image/png;base64,${qrBase64}`;
    }
    return null;
}

module.exports = { generateQR };
