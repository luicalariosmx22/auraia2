#!/usr/bin/env python3
"""
Test específico WebSocket para diagnosticar conexión
"""

import asyncio
import socketio
import requests
import json

async def test_websocket_connection():
    """Test directo de conexión WebSocket"""
    print("🔗 TEST WEBSOCKET DIRECTO")
    print("="*40)
    
    # URLs a probar
    backend_urls = [
        "https://whatsapp-server-production-7e82.up.railway.app",
        "https://whatsapp-server-production-8f61.up.railway.app",  # URL del log anterior
    ]
    
    for backend_url in backend_urls:
        print(f"\n🧪 Probando backend: {backend_url}")
        
        # Test HTTP primero
        try:
            print("📡 Test HTTP /health...")
            response = requests.get(f"{backend_url}/health", timeout=10)
            print(f"✅ HTTP Status: {response.status_code}")
            print(f"📄 Content: {response.text[:200]}")
        except Exception as e:
            print(f"❌ HTTP Error: {e}")
        
        # Test HTTP raíz
        try:
            print("📡 Test HTTP /...")
            response = requests.get(backend_url, timeout=10)
            print(f"✅ Root Status: {response.status_code}")
            print(f"📄 Root Content: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Root Error: {e}")
            continue
        
        # Test WebSocket
        print("🔌 Test WebSocket...")
        client = socketio.AsyncClient(
            logger=False,
            engineio_logger=False
        )
        
        connected = False
        
        @client.event
        async def connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket conectado!")
            
            # Intentar solicitar QR
            print("📱 Solicitando QR...")
            await client.emit('init_session')
        
        @client.event
        async def disconnect():
            print("🔌 WebSocket desconectado")
        
        @client.event
        async def qr_code(data):
            print(f"📱 QR recibido: {data}")
        
        @client.event  
        async def error(data):
            print(f"❌ Error WebSocket: {data}")
        
        @client.event
        async def log(data):
            print(f"📋 Log: {data}")
            
        @client.event
        async def status_update(data):
            print(f"📊 Status: {data}")
        
        try:
            # Intentar conectar
            await client.connect(backend_url)
            
            # Esperar eventos
            await asyncio.sleep(10)
            
            if connected:
                print("✅ Conexión WebSocket exitosa")
            else:
                print("❌ No se pudo conectar via WebSocket")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"❌ WebSocket Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
