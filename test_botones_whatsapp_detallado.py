#!/usr/bin/env python3
"""
Script para probar cada botón del panel WhatsApp Web detalladamente
"""

import requests
import json
import time
import sys

# Configuración
BASE_URL = "http://localhost:5000"
CLIENTE = "aura"
WHATSAPP_URL = f"{BASE_URL}/panel_cliente/{CLIENTE}/whatsapp"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Probar un endpoint específico"""
    try:
        url = f"{WHATSAPP_URL}{endpoint}"
        print(f"\n🔍 Testing: {description}")
        print(f"📡 {method} {url}")
        
        if method == "POST":
            response = requests.post(url, json=data or {}, headers={'Content-Type': 'application/json'})
        else:
            response = requests.get(url)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Response: {json.dumps(result, indent=2)}")
                return True, result
            except:
                print(f"✅ Response (HTML): {response.text[:200]}...")
                return True, response.text
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text[:500]}...")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def main():
    """Probar todos los botones del panel"""
    print("🧪 PRUEBA DETALLADA DE BOTONES WHATSAPP WEB")
    print("=" * 60)
    
    # 1. Probar acceso al panel principal
    print("\n1️⃣ ACCESO AL PANEL PRINCIPAL")
    success, result = test_endpoint("/", "GET", description="Dashboard principal")
    if not success:
        print("❌ No se puede acceder al panel principal")
        return
    
    # 2. Probar endpoint de status
    print("\n2️⃣ ENDPOINT DE STATUS")
    success, result = test_endpoint("/status", "GET", description="Obtener estado actual")
    if success and isinstance(result, dict):
        print("📊 Estado obtenido:")
        print(f"   - Health Status: {result.get('health_status', 'N/A')}")
        print(f"   - Client Status: {result.get('client_status', 'N/A')}")
        print(f"   - Detailed Status: {result.get('detailed_status', 'N/A')}")
    
    # 3. Probar botón CONECTAR
    print("\n3️⃣ BOTÓN CONECTAR")
    success, result = test_endpoint("/connect", "POST", description="Conectar al backend")
    if success:
        print("✅ Conectar: OK")
    else:
        print("❌ Conectar: FALLO")
    
    # 4. Probar botón INICIAR SESIÓN
    print("\n4️⃣ BOTÓN INICIAR SESIÓN")
    success, result = test_endpoint("/init_session", "POST", description="Iniciar sesión WhatsApp")
    if success:
        print("✅ Iniciar Sesión: OK")
    else:
        print("❌ Iniciar Sesión: FALLO")
    
    # 5. Probar botón GENERAR QR
    print("\n5️⃣ BOTÓN GENERAR QR")
    success, result = test_endpoint("/qr", "GET", description="Obtener código QR")
    if success:
        print("✅ Generar QR: OK")
        if isinstance(result, dict) and result.get('qr_data'):
            print(f"📱 QR Data: {result['qr_data'][:50]}...")
    else:
        print("❌ Generar QR: FALLO")
    
    # 6. Probar botón FLUJO AUTOMÁTICO
    print("\n6️⃣ BOTÓN FLUJO AUTOMÁTICO")
    success, result = test_endpoint("/get_qr_auto", "POST", description="Flujo automático con QR")
    if success:
        print("✅ Flujo Automático: OK")
        if isinstance(result, dict):
            print(f"   - Has QR: {result.get('has_qr', False)}")
            print(f"   - Authenticated: {result.get('authenticated', False)}")
            print(f"   - Message: {result.get('message', 'N/A')}")
    else:
        print("❌ Flujo Automático: FALLO")
    
    # 7. Probar botón VERIFICAR ESTADO
    print("\n7️⃣ BOTÓN VERIFICAR ESTADO")
    success, result = test_endpoint("/check_status", "POST", description="Verificar estado WhatsApp")
    if success:
        print("✅ Verificar Estado: OK")
    else:
        print("❌ Verificar Estado: FALLO")
    
    # 8. Probar botón MENSAJE PRUEBA
    print("\n8️⃣ BOTÓN MENSAJE PRUEBA")
    success, result = test_endpoint("/send_test", "POST", description="Enviar mensaje de prueba")
    if success:
        print("✅ Mensaje Prueba: OK")
    else:
        print("❌ Mensaje Prueba: FALLO")
    
    # 9. Probar botón CERRAR SESIÓN
    print("\n9️⃣ BOTÓN CERRAR SESIÓN")
    success, result = test_endpoint("/close_session", "POST", description="Cerrar sesión WhatsApp")
    if success:
        print("✅ Cerrar Sesión: OK")
    else:
        print("❌ Cerrar Sesión: FALLO")
    
    # 10. Probar botón DESCONECTAR
    print("\n🔟 BOTÓN DESCONECTAR")
    success, result = test_endpoint("/disconnect", "POST", description="Desconectar del backend")
    if success:
        print("✅ Desconectar: OK")
    else:
        print("❌ Desconectar: FALLO")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBA COMPLETADA")
    
    # Verificar conectividad al backend Railway
    print("\n🌐 VERIFICANDO BACKEND RAILWAY")
    try:
        response = requests.get("https://whatsapp-server-production-8f61.up.railway.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend Railway: FUNCIONANDO")
        else:
            print(f"⚠️ Backend Railway: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Railway: ERROR - {e}")

if __name__ == "__main__":
    main()
