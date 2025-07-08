// Función para inicializar WhatsApp con fallback
async function initializeWhatsAppWithFallback() {
    const maxRetries = 3;
    let retryCount = 0;
    
    while (retryCount < maxRetries) {
        try {
            console.log(`🔄 Intento ${retryCount + 1} de ${maxRetries} para inicializar WhatsApp...`);
            
            // Configuración más conservadora para evitar session closed
            const clientOptions = {
                authStrategy: new LocalAuth(),
                puppeteer: {
                    headless: true,
                    args: [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-default-apps',
                        '--no-default-browser-check',
                        '--disable-hang-monitor',
                        '--disable-popup-blocking',
                        '--disable-translate',
                        '--disable-sync',
                        '--single-process',
                        '--no-zygote',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ],
                    executablePath: '/usr/bin/google-chrome-stable',
                    timeout: 30000,
                    handleSIGINT: false,
                    handleSIGTERM: false,
                    handleSIGHUP: false
                },
                // Configuración más simple para evitar errores
                webVersionCache: {
                    type: 'none'
                }
            };
            
            const client = new Client(clientOptions);
            
            // Configurar eventos antes de inicializar
            client.on('ready', () => {
                console.log('✅ WhatsApp Client está listo!');
                isClientReady = true;
            });
            
            client.on('qr', (qr) => {
                console.log('📱 QR Code recibido');
                currentQR = qr;
                
                // Enviar QR a todos los clientes conectados
                io.emit('qr', qr);
                
                // Generar QR como imagen
                qrcode.toDataURL(qr, (err, url) => {
                    if (err) {
                        console.error('Error generando QR:', err);
                    } else {
                        console.log('✅ QR generado como imagen');
                        io.emit('qr_image', url);
                    }
                });
            });
            
            client.on('disconnected', (reason) => {
                console.log('❌ Cliente desconectado:', reason);
                isClientReady = false;
                currentQR = null;
                
                // Reintentar conexión después de un delay
                setTimeout(() => {
                    console.log('🔄 Reintentando conexión...');
                    initializeWhatsAppWithFallback();
                }, 5000);
            });
            
            // Inicializar con timeout
            await Promise.race([
                client.initialize(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Timeout en inicialización')), 45000)
                )
            ]);
            
            console.log('✅ WhatsApp Client inicializado exitosamente');
            return client;
            
        } catch (error) {
            console.error(`❌ Error en intento ${retryCount + 1}:`, error.message);
            retryCount++;
            
            if (retryCount < maxRetries) {
                const delay = Math.min(5000 * retryCount, 15000);
                console.log(`⏳ Esperando ${delay}ms antes del siguiente intento...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            } else {
                console.error('❌ Máximo número de reintentos alcanzado');
                throw error;
            }
        }
    }
}

module.exports = { initializeWhatsAppWithFallback };
