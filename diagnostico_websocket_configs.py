#!/usr/bin/env python3
"""
Diagnóstico simple de WebSocket con diferentes configuraciones
"""

import socketio
import time
import sys

BACKEND_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

def test_websocket_config(config_name, connect_kwargs=None, client_kwargs=None):
    """Probar configuración específica de WebSocket"""
    print(f"\n🔍 PROBANDO: {config_name}")
    print("-" * 50)
    
    connected = False
    events = []
    
    # Crear cliente con configuración específica
    client_kwargs = client_kwargs or {}
    connect_kwargs = connect_kwargs or {}
    
    sio = socketio.Client(logger=False, engineio_logger=False, **client_kwargs)
    
    # Event handlers
    @sio.event
    def connect():
        nonlocal connected
        connected = True
        events.append("CONNECT")
        print("✅ Conectado")
    
    @sio.event
    def disconnect():
        nonlocal connected
        connected = False
        events.append("DISCONNECT")
        print("🔌 Desconectado")
    
    @sio.event
    def connect_error(data):
        events.append(f"CONNECT_ERROR: {data}")
        print(f"❌ Error de conexión: {data}")
    
    @sio.event
    def connected(data):
        events.append(f"CONNECTED: {data}")
        print(f"📡 Backend confirmó: {data}")
    
    try:
        print(f"🔗 Conectando a: {BACKEND_URL}")
        print(f"🔧 Parámetros de conexión: {connect_kwargs}")
        
        sio.connect(BACKEND_URL, **connect_kwargs)
        
        # Esperar conexión
        timeout = 10
        while timeout > 0 and not connected:
            time.sleep(1)
            timeout -= 1
            print(f"⏱️ {timeout}s")
        
        if connected:
            print("✅ ÉXITO - Conexión establecida")
            
            # Probar envío de evento
            print("📤 Enviando evento de prueba...")
            sio.emit('get_qr', {'test': True})
            
            # Esperar respuesta
            time.sleep(3)
            
            # Desconectar
            sio.disconnect()
            
        else:
            print("❌ FALLO - Timeout")
        
        print(f"📋 Eventos recibidos: {events}")
        return connected
        
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False

def main():
    """Probar diferentes configuraciones"""
    print("🧪 DIAGNÓSTICO DE CONFIGURACIONES WEBSOCKET")
    print("=" * 60)
    
    results = {}
    
    # 1. Configuración estándar
    results['standard'] = test_websocket_config(
        "Configuración estándar",
        connect_kwargs={'transports': ['websocket', 'polling']}
    )
    
    # 2. Solo polling
    results['polling'] = test_websocket_config(
        "Solo polling",
        connect_kwargs={'transports': ['polling']}
    )
    
    # 3. Solo websocket
    results['websocket'] = test_websocket_config(
        "Solo WebSocket",
        connect_kwargs={'transports': ['websocket']}
    )
    
    # 4. Con namespace específico
    results['namespace'] = test_websocket_config(
        "Con namespace '/'",
        connect_kwargs={'namespaces': ['/'], 'transports': ['websocket', 'polling']}
    )
    
    # 5. Sin parámetros especiales
    results['basic'] = test_websocket_config(
        "Configuración básica",
        connect_kwargs={}
    )
    
    # 6. Con reconexión deshabilitada
    results['no_reconnect'] = test_websocket_config(
        "Sin reconexión",
        client_kwargs={'reconnection': False},
        connect_kwargs={'transports': ['websocket', 'polling']}
    )
    
    # Resumen
    print("\n🏁 RESUMEN DE RESULTADOS")
    print("=" * 60)
    for config, success in results.items():
        status = "✅ ÉXITO" if success else "❌ FALLO"
        print(f"{config:15} - {status}")
    
    # Identificar configuración que funciona
    working_configs = [k for k, v in results.items() if v]
    if working_configs:
        print(f"\n🎯 CONFIGURACIONES QUE FUNCIONAN: {working_configs}")
    else:
        print("\n❌ NINGUNA CONFIGURACIÓN FUNCIONA")
        print("💡 Posible problema:")
        print("  - El backend no soporta Socket.IO")
        print("  - El backend usa WebSocket nativo")
        print("  - Problema de firewall/proxy")

if __name__ == "__main__":
    main()
