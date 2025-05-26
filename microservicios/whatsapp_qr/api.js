// ✅ Archivo: api.js
// 👉 API REST con rutas: estado, qr, desconectar y enviar mensaje
const { generateQR } = require('./sessions/qr');

function setupAPI(app, sessions, crearCliente) {
    app.get('/estado/:noraId', (req, res) => {
        const client = sessions[req.params.noraId];
        res.send({ conectado: !!(client && client.info) });
    });

    app.get('/qr/:noraId', async (req, res) => {
        const { noraId } = req.params;
        const qr = await generateQR(noraId, crearCliente, sessions);
        res.send({ qr });
    });

    app.post('/desconectar/:noraId', (req, res) => {
        const client = sessions[req.params.noraId];
        if (client) client.logout();
        delete sessions[req.params.noraId];
        res.send({ ok: true });
    });

    app.post('/enviar/:noraId', async (req, res) => {
        const client = sessions[req.params.noraId];
        const { numero, mensaje } = req.body;
        if (client) {
            await client.sendMessage(numero + '@c.us', mensaje);
            res.send({ enviado: true });
        } else {
            res.status(400).send({ error: 'No conectado' });
        }
    });
}

module.exports = { setupAPI };
