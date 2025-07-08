#!/usr/bin/env python3
"""
Script de prueba para el módulo WhatsApp Web
Verifica que todo funcione correctamente
"""

import sys
import os
import traceback

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar todos los imports necesarios"""
    print("🧪 Probando imports...")
    
    try:
        import flask
        print("✅ Flask OK")
    except ImportError as e:
        print(f"❌ Flask error: {e}")
        return False
    
    try:
        import socketio
        print("✅ SocketIO OK")
    except ImportError as e:
        print(f"❌ SocketIO error: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests OK")
    except ImportError as e:
        print(f"❌ Requests error: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv OK")
    except ImportError as e:
        print(f"❌ Python-dotenv error: {e}")
        return False
    
    return True

def test_whatsapp_client():
    """Probar el cliente WhatsApp Web"""
    print("\n📱 Probando cliente WhatsApp Web...")
    
    try:
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        print("✅ Import WhatsAppWebSocketClient OK")
        
        # Crear cliente
        client = WhatsAppWebSocketClient()
        print("✅ Cliente creado OK")
        
        # Probar health check
        health = client.get_health_status()
        if health:
            print(f"✅ Health check OK: {health.get('status', 'unknown')}")
        else:
            print("⚠️ Health check sin respuesta")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cliente WhatsApp: {e}")
        traceback.print_exc()
        return False

def test_blueprint():
    """Probar el blueprint de WhatsApp Web"""
    print("\n🔧 Probando blueprint...")
    
    try:
        from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_web import panel_cliente_whatsapp_web_bp
        print("✅ Blueprint importado OK")
        
        # Probar función del cliente
        from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_web import get_whatsapp_client_instance
        client = get_whatsapp_client_instance()
        print("✅ Cliente singleton OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error blueprint: {e}")
        traceback.print_exc()
        return False

def test_websocket_connection():
    """Probar conexión WebSocket real"""
    print("\n🌐 Probando conexión WebSocket...")
    
    try:
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        client = WhatsAppWebSocketClient()
        
        # Health check
        health = client.get_health_status()
        if not health:
            print("❌ Backend no responde")
            return False
            
        print(f"✅ Backend OK: {health.get('status')}")
        
        # Intentar conexión WebSocket
        print("🔗 Conectando WebSocket...")
        if client.connect():
            print("✅ WebSocket conectado")
            
            # Obtener estado
            status = client.get_detailed_status()
            print(f"📊 Estado: {status}")
            
            # Desconectar
            client.disconnect()
            print("✅ WebSocket desconectado")
            
            return True
        else:
            print("❌ No se pudo conectar WebSocket")
            return False
            
    except Exception as e:
        print(f"❌ Error WebSocket: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del módulo WhatsApp Web\n")
    
    # Configurar logging básico para evitar errores
    import logging
    logging.basicConfig(
        level=logging.WARNING,  # Solo warnings y errores
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Suprimir logs detallados de librerías
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    
    tests = [
        ("Imports básicos", test_imports),
        ("Cliente WhatsApp", test_whatsapp_client),
        ("Blueprint", test_blueprint),
        ("Conexión WebSocket", test_websocket_connection)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((name, result))
            
            if result:
                print(f"✅ {name}: EXITOSO")
            else:
                print(f"❌ {name}: FALLIDO")
                
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results.append((name, False))
    
    # Resumen
    print(f"\n{'='*50}")
    print("📋 RESUMEN DE PRUEBAS")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n📊 Total: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El módulo está listo.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
