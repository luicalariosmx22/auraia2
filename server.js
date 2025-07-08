const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const cors = require('cors');
require('dotenv').config();

// Configuración de la aplicación
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

app.use(cors());
app.use(express.json());

// Puerto para Railway
const PORT = process.env.PORT || 3000;

// Variables globales
let whatsappClient = null;
let isClientReady = false;
let currentQR = null;
let clientSessions = new Map();

// Función para inicializar cliente WhatsApp con Chrome
function initializeWhatsAppClient() {
    console.log('🚀 Inicializando cliente WhatsApp Web con Chrome...');
    
    const clientOptions = {
        authStrategy: new LocalAuth(),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--mute-audio',
                '--no-default-browser-check',
                '--no-first-run',
                '--disable-logging',
                '--disable-permissions-api',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-default-apps',
                '--disable-domain-reliability',
                '--disable-extensions',
                '--disable-features=VizDisplayCompositor',
                '--disable-ipc-flooding-protection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--no-default-browser-check',
                '--no-first-run',
                '--safebrowsing-disable-auto-update',
                '--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain'
            ],
            executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome-stable'
        }
    };

    whatsappClient = new Client(clientOptions);

    // Eventos del cliente
    whatsappClient.on('qr', (qr) => {
        console.log('📱 QR Code recibido');
        currentQR = qr;
        
        // Generar QR como imagen base64
        qrcode.toDataURL(qr, (err, url) => {
            if (!err) {
                const qrData = {
                    type: 'qr_code',
                    qr_data: url, // Imagen PNG en base64
                    qr_text: qr,  // Texto QR para backup
                    session_id: generateSessionId(),
                    timestamp: new Date().toISOString(),
                    is_real: true
                };
                
                console.log('✅ QR generado como imagen PNG');
                
                // Enviar a todos los clientes conectados
                io.emit('qr_code', qrData);
            }
        });
    });

    whatsappClient.on('ready', () => {
        console.log('✅ WhatsApp Web está listo!');
        isClientReady = true;
        
        io.emit('whatsapp_status', {
            type: 'status',
            status: 'ready',
            authenticated: true,
            message: 'WhatsApp Web autenticado exitosamente',
            timestamp: new Date().toISOString(),
            is_real: true
        });
    });

    whatsappClient.on('authenticated', () => {
        console.log('🎉 WhatsApp Web autenticado');
        
        io.emit('authenticated', {
            type: 'authenticated',
            message: 'Autenticación exitosa',
            timestamp: new Date().toISOString(),
            is_real: true
        });
    });

    whatsappClient.on('auth_failure', (msg) => {
        console.error('❌ Fallo de autenticación:', msg);
        
        io.emit('error', {
            type: 'error',
            message: 'Error de autenticación en WhatsApp Web',
            details: msg,
            timestamp: new Date().toISOString()
        });
    });

    whatsappClient.on('disconnected', (reason) => {
        console.log('🔌 WhatsApp Web desconectado:', reason);
        isClientReady = false;
        currentQR = null;
        
        io.emit('whatsapp_status', {
            type: 'status',
            status: 'disconnected',
            authenticated: false,
            message: 'WhatsApp Web desconectado',
            reason: reason,
            timestamp: new Date().toISOString()
        });
        
        // Reintentar conexión después de 10 segundos
        console.log('🔄 Reintentando conexión en 10 segundos...');
        setTimeout(() => {
            console.log('🔄 Reintentando conexión por desconexión...');
            initializeWhatsAppClient();
        }, 10000);
    });

    // Inicializar cliente con manejo de errores mejorado
    whatsappClient.initialize().catch(err => {
        console.error('❌ Error inicializando WhatsApp Client:', err);
        
        io.emit('error', {
            type: 'error',
            message: 'Error iniciando sesión real de WhatsApp Web',
            details: err.message,
            timestamp: new Date().toISOString()
        });
        
        // Reintentar después de 5 segundos con diferentes estrategias
        if (err.message.includes('Session closed') || 
            err.message.includes('Protocol error') || 
            err.message.includes('Connection closed') ||
            err.message.includes('Target closed')) {
            
            console.log('🔄 Reintentando inicialización debido a error de protocolo...');
            setTimeout(() => {
                console.log('🔄 Ejecutando reintento con nueva instancia...');
                
                // Destruir cliente anterior si existe
                if (whatsappClient) {
                    try {
                        whatsappClient.destroy();
                    } catch (destroyErr) {
                        console.log('⚠️ Error al destruir cliente anterior:', destroyErr.message);
                    }
                }
                
                // Reinicializar completamente
                initializeWhatsAppClient();
            }, 5000);
        }
    });

    // Agregar timeout para detectar inicialización colgada
    setTimeout(() => {
        if (!isClientReady && !currentQR) {
            console.log('⚠️ Inicialización tardando mucho, reintentando...');
            if (whatsappClient) {
                whatsappClient.destroy().catch(console.error);
            }
            setTimeout(() => {
                console.log('🔄 Reintentando por timeout...');
                initializeWhatsAppClient();
            }, 2000);
        }
    }, 30000); // 30 segundos timeout
}

// Función para generar session ID
function generateSessionId() {
    return Math.random().toString(36).substr(2, 9);
}

// Rutas HTTP
app.get('/', (req, res) => {
    res.json({
        status: 'ok',
        service: 'WhatsApp Web Backend con Chrome',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        chrome_available: process.env.CHROME_PATH ? true : false,
        whatsapp_ready: isClientReady
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        whatsapp_ready: isClientReady,
        chrome_path: process.env.CHROME_PATH,
        timestamp: new Date().toISOString()
    });
});

app.get('/qr', (req, res) => {
    if (currentQR) {
        // Generar QR como imagen
        qrcode.toDataURL(currentQR, (err, url) => {
            if (!err) {
                res.json({
                    success: true,
                    qr_data: url,
                    qr_text: currentQR,
                    is_real: true
                });
            } else {
                res.json({
                    success: false,
                    message: 'Error generando imagen QR'
                });
            }
        });
    } else {
        res.json({
            success: false,
            message: 'QR no disponible'
        });
    }
});

// Socket.IO eventos
io.on('connection', (socket) => {
    console.log(`📡 Cliente conectado: ${socket.id}`);
    
    // Enviar estado inicial
    socket.emit('connected', {
        client_id: socket.id,
        whatsapp_ready: isClientReady,
        timestamp: new Date().toISOString()
    });

    // Manejar solicitud de QR
    socket.on('get_qr', (data) => {
        console.log('📱 Solicitud de QR recibida');
        
        if (currentQR) {
            qrcode.toDataURL(currentQR, (err, url) => {
                if (!err) {
                    socket.emit('qr_code', {
                        type: 'qr_code',
                        qr_data: url,
                        qr_text: currentQR,
                        session_id: data?.session_id || generateSessionId(),
                        timestamp: new Date().toISOString(),
                        is_real: true
                    });
                }
            });
        } else {
            socket.emit('error', {
                type: 'error',
                message: 'QR no disponible aún. WhatsApp Web se está inicializando...',
                timestamp: new Date().toISOString()
            });
        }
    });

    // Manejar solicitud de estado
    socket.on('get_status', (data) => {
        console.log('📊 Solicitud de estado recibida');
        
        socket.emit('whatsapp_status', {
            type: 'status',
            status: isClientReady ? 'ready' : (currentQR ? 'qr_ready' : 'initializing'),
            authenticated: isClientReady,
            has_qr: currentQR !== null,
            timestamp: new Date().toISOString(),
            is_real: true
        });
    });

    // Manejar desconexión
    socket.on('disconnect', () => {
        console.log(`🔌 Cliente desconectado: ${socket.id}`);
    });
});

// Inicializar WhatsApp al arrancar
console.log('🎯 Iniciando servidor WhatsApp Web con Chrome...');
console.log(`🌐 Puerto: ${PORT}`);
console.log(`🔍 Chrome Path: ${process.env.CHROME_PATH || '/usr/bin/google-chrome-stable'}`);

// Verificar Chrome
const fs = require('fs');
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome-stable';
if (fs.existsSync(chromePath)) {
    console.log('✅ Chrome encontrado, inicializando WhatsApp Web...');
    initializeWhatsAppClient();
} else {
    console.log('⚠️ Chrome no encontrado en:', chromePath);
    console.log('📝 WhatsApp Web no se puede inicializar sin Chrome');
}

// Iniciar servidor
server.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor corriendo en puerto ${PORT}`);
});

// Manejo de errores no capturados
process.on('uncaughtException', (err) => {
    console.error('💥 Error no capturado:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('💥 Promesa rechazada:', reason);
});
