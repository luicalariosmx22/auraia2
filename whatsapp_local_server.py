#!/usr/bin/env python3
"""
Servidor local de WhatsApp Web con Chromium
Para usar cuando queremos QR real sin depender de Railway
"""

import os
import sys
import json
import time
import base64
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import socketio
from flask import Flask
from flask_socketio import SocketIO, emit

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
PORT = 3001  # Puerto diferente a Railway
CHROME_PATH = "/usr/bin/chromium-browser"

class LocalWhatsAppWebServer:
    def __init__(self):
        self.driver = None
        self.qr_data = None
        self.is_authenticated = False
        self.session_active = False
        self.session_id = None
        
        # Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'local-whatsapp-web-server'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.setup_events()
        
    def setup_chrome_driver(self):
        """Configurar ChromeDriver local"""
        try:
            chrome_options = Options()
            chrome_options.binary_location = CHROME_PATH
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # No usar headless para poder ver el QR si es necesario
            # chrome_options.add_argument('--headless')
            
            logger.info("🌐 Iniciando ChromeDriver...")
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ ChromeDriver iniciado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando ChromeDriver: {e}")
            return False
    
    def setup_events(self):
        """Configurar eventos de Socket.IO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info("🔗 Cliente conectado")
            emit('connected', {
                'client_id': 'local-server',
                'message': 'Conectado al servidor local WhatsApp Web'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("🔌 Cliente desconectado")
        
        @self.socketio.on('get_qr')
        def handle_get_qr(data):
            logger.info("📱 Solicitud de QR recibida")
            try:
                qr_result = self.get_qr_code()
                if qr_result:
                    emit('qr_code', qr_result)
                else:
                    emit('error', {
                        'type': 'error',
                        'message': 'No se pudo obtener QR'
                    })
            except Exception as e:
                logger.error(f"❌ Error obteniendo QR: {e}")
                emit('error', {
                    'type': 'error',
                    'message': f'Error: {str(e)}'
                })
        
        @self.socketio.on('get_status')
        def handle_get_status(data):
            logger.info("📊 Solicitud de estado recibida")
            status = {
                'type': 'status',
                'session_id': self.session_id,
                'status': 'authenticated' if self.is_authenticated else 'qr_ready' if self.qr_data else 'disconnected',
                'authenticated': self.is_authenticated,
                'created_at': datetime.now().isoformat(),
                'phone_number': None,
                'message': f'Estado: {"autenticado" if self.is_authenticated else "QR disponible" if self.qr_data else "desconectado"}',
                'is_real': True
            }
            emit('status', status)
        
        @self.socketio.on('test_whatsapp')
        def handle_test_whatsapp(data):
            logger.info("🧪 Solicitud de prueba recibida")
            if not self.is_authenticated:
                emit('error', {
                    'type': 'error',
                    'message': 'WhatsApp no está autenticado'
                })
            else:
                emit('test_result', {
                    'type': 'test_result',
                    'message': 'WhatsApp funcionando correctamente',
                    'is_real': True
                })
    
    def start_whatsapp_session(self):
        """Iniciar sesión de WhatsApp Web"""
        try:
            if not self.driver:
                if not self.setup_chrome_driver():
                    return False
            
            logger.info("🚀 Navegando a WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Generar session_id único
            self.session_id = f"local-{int(time.time())}"
            self.session_active = True
            
            logger.info("⏳ Esperando que aparezca el QR...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def get_qr_code(self):
        """Obtener código QR de WhatsApp Web"""
        try:
            if not self.session_active:
                if not self.start_whatsapp_session():
                    return None
            
            # Esperar que aparezca el elemento QR
            logger.info("🔍 Buscando elemento QR...")
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # Buscar el canvas del QR
                qr_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label*='QR']"))
                )
                
                logger.info("📱 QR encontrado, capturando...")
                
                # Capturar el QR como imagen
                qr_screenshot = qr_element.screenshot_as_base64
                qr_data_url = f"data:image/png;base64,{qr_screenshot}"
                
                self.qr_data = qr_data_url
                
                return {
                    'type': 'qr_code',
                    'qr_data': qr_data_url,
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'message': 'QR real obtenido de Chromium local',
                    'is_real': True
                }
                
            except TimeoutException:
                # Verificar si ya está autenticado
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "[data-testid='chat-list']")
                    logger.info("🎉 WhatsApp ya está autenticado!")
                    self.is_authenticated = True
                    return {
                        'type': 'authenticated',
                        'message': 'WhatsApp ya está autenticado',
                        'session_id': self.session_id,
                        'is_real': True
                    }
                except NoSuchElementException:
                    logger.warning("⏱️ QR no apareció en tiempo esperado")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error obteniendo QR: {e}")
            return None
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🧹 ChromeDriver cerrado")
            except:
                pass
    
    def run(self):
        """Ejecutar servidor"""
        try:
            logger.info(f"🚀 Iniciando servidor local WhatsApp Web en puerto {PORT}")
            logger.info(f"🌐 Chrome path: {CHROME_PATH}")
            
            # Verificar que Chrome existe
            if not os.path.exists(CHROME_PATH):
                logger.error(f"❌ Chrome no encontrado en: {CHROME_PATH}")
                return
            
            # Ruta de health check
            @self.app.route('/health')
            def health():
                return {
                    'status': 'ok',
                    'message': 'Servidor local WhatsApp Web funcionando',
                    'chrome_available': os.path.exists(CHROME_PATH),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Iniciar servidor
            self.socketio.run(
                self.app,
                host='0.0.0.0',
                port=PORT,
                debug=False,
                allow_unsafe_werkzeug=True
            )
            
        except KeyboardInterrupt:
            logger.info("⛔ Servidor interrumpido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en servidor: {e}")
        finally:
            self.cleanup()

def main():
    """Función principal"""
    print("🔧 SERVIDOR LOCAL WHATSAPP WEB CON CHROMIUM")
    print("=" * 60)
    print(f"🌐 Chrome: {CHROME_PATH}")
    print(f"🚪 Puerto: {PORT}")
    print(f"🕒 Inicio: {datetime.now()}")
    
    # Verificar Chrome
    if not os.path.exists(CHROME_PATH):
        print(f"❌ ERROR: Chrome no encontrado en {CHROME_PATH}")
        print("💡 Instala Chromium: sudo apt install chromium-browser")
        return
    
    server = LocalWhatsAppWebServer()
    server.run()

if __name__ == "__main__":
    main()
