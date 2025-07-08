#!/usr/bin/env python3
"""
Prueba de integración WhatsApp Web con NORA
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.append('/mnt/c/Users/PC/PYTHON/Auraai2')

from clientes.aura.utils.whatsapp_web_client import initialize_whatsapp_client

# Cargar variables de entorno
load_dotenv()

async def test_whatsapp_integration():
    """Prueba básica de integración"""
    print("🧪 Iniciando prueba de integración WhatsApp Web...")
    
    # URL del backend en Railway
    backend_url = os.getenv('WHATSAPP_BACKEND_URL', 'https://whatsapp-server-production-8f61.up.railway.app')
    print(f"🔗 URL del backend: {backend_url}")
    
    # Inicializar cliente
    client = initialize_whatsapp_client(backend_url)
    
    # Configurar callbacks
    async def on_authenticated(user_info):
        print(f"✅ WhatsApp autenticado: {user_info}")
    
    async def on_qr_code(qr_data):
        print(f"📱 QR Code recibido (longitud: {len(qr_data)} chars)")
        print("🔍 Debes escanear el QR en el backend web")
    
    async def on_status_change(status, message):
        print(f"📊 Estado: {status} - {message}")
    
    client.set_on_authenticated_callback(on_authenticated)
    client.set_on_qr_code_callback(on_qr_code)
    client.set_on_status_change_callback(on_status_change)
    
    try:
        # Verificar salud del backend
        print("🏥 Verificando salud del backend...")
        health = client.get_health_status()
        if health:
            print(f"✅ Backend saludable: {health}")
        else:
            print("❌ Backend no responde")
            return
        
        # Conectar al WebSocket
        print("🔌 Conectando al WebSocket...")
        if await client.connect():
            print("✅ Conectado al WebSocket")
            
            # Mostrar estado inicial
            print(f"📋 Estado inicial: {client.status_info}")
            
            # Esperar un poco para estabilizar
            await asyncio.sleep(2)
            
            # Iniciar sesión WhatsApp
            print("🚀 Iniciando sesión WhatsApp Web...")
            if await client.init_whatsapp_session():
                print("✅ Solicitud de sesión enviada")
                
                # Esperar eventos
                print("⏳ Esperando eventos (30 segundos)...")
                await asyncio.sleep(30)
                
                # Verificar estado final
                print("🔍 Verificando estado final...")
                await client.check_whatsapp_status()
                
                # Mostrar estado final
                print(f"📋 Estado final: {client.status_info}")
                
            else:
                print("❌ Error iniciando sesión")
            
            # Desconectar
            print("🔌 Desconectando...")
            await client.disconnect()
            
        else:
            print("❌ Error conectando al WebSocket")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔥 Prueba de integración WhatsApp Web + NORA")
    print("=" * 50)
    asyncio.run(test_whatsapp_integration())
    print("=" * 50)
    print("✅ Prueba completada")
