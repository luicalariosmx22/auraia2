#!/usr/bin/env python3
"""
Diagnóstico DEFINITIVO del problema QR WhatsApp Web
Identifica la causa raíz del problema de visualización
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

def test_full_flow():
    """Probar el flujo completo paso a paso"""
    print("🔍 DIAGNÓSTICO DEFINITIVO QR WHATSAPP WEB")
    print("=" * 60)
    
    # 1. Verificar que NORA está corriendo
    print("\n1️⃣ VERIFICANDO QUE NORA ESTÁ CORRIENDO")
    try:
        nora_response = requests.get("http://localhost:5000", timeout=5)
        if nora_response.status_code == 200:
            print("✅ NORA está funcionando en localhost:5000")
        else:
            print(f"❌ NORA responde con código {nora_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ NORA no está funcionando: {e}")
        print("🔧 SOLUCIÓN: Ejecutar './start_nora.sh' primero")
        return False
    
    # 2. Verificar que el endpoint principal del panel existe
    print("\n2️⃣ VERIFICANDO ENDPOINT PRINCIPAL DEL PANEL")
    try:
        panel_response = requests.get("http://localhost:5000/panel_cliente/aura/whatsapp", timeout=5)
        if panel_response.status_code == 200:
            print("✅ Panel WhatsApp Web accesible")
        else:
            print(f"❌ Panel responde con código {panel_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Panel no accesible: {e}")
        print("🔧 SOLUCIÓN: Verificar que el blueprint está registrado")
        return False
    
    # 3. Verificar que el backend Railway está funcionando
    print("\n3️⃣ VERIFICANDO BACKEND RAILWAY")
    try:
        railway_response = requests.get("https://whatsapp-server-production-8f61.up.railway.app/health", timeout=10)
        if railway_response.status_code == 200:
            print("✅ Backend Railway funcionando")
        else:
            print(f"❌ Backend Railway responde con código {railway_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Railway no funciona: {e}")
        return False
    
    # 4. Probar el endpoint connect del panel
    print("\n4️⃣ PROBANDO ENDPOINT CONNECT DEL PANEL")
    try:
        connect_response = requests.post("http://localhost:5000/panel_cliente/aura/whatsapp/connect", 
                                       headers={'Content-Type': 'application/json'}, 
                                       timeout=10)
        print(f"📡 Connect status: {connect_response.status_code}")
        
        if connect_response.status_code == 200:
            connect_data = connect_response.json()
            print(f"✅ Connect exitoso: {connect_data}")
        else:
            print(f"❌ Connect falló: {connect_response.status_code}")
            print(f"❌ Respuesta: {connect_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en connect: {e}")
        return False
    
    # 5. Probar el endpoint get_qr_auto
    print("\n5️⃣ PROBANDO ENDPOINT GET_QR_AUTO")
    try:
        qr_response = requests.post("http://localhost:5000/panel_cliente/aura/whatsapp/get_qr_auto", 
                                  headers={'Content-Type': 'application/json'}, 
                                  timeout=15)
        print(f"📱 QR Auto status: {qr_response.status_code}")
        
        if qr_response.status_code == 200:
            qr_data = qr_response.json()
            print(f"✅ QR Auto exitoso: {qr_data.get('success', False)}")
            
            if qr_data.get('has_qr') and qr_data.get('qr_data'):
                qr_length = len(qr_data['qr_data'])
                print(f"📱 QR Data obtenido: {qr_length} caracteres")
                print(f"📱 QR Preview: {qr_data['qr_data'][:50]}...")
                
                # Verificar que es Base64
                if qr_data['qr_data'].startswith('data:image/png;base64,'):
                    print("✅ QR en formato Base64 PNG correcto")
                    return True
                else:
                    print("⚠️ QR no está en formato Base64 PNG")
                    return False
            else:
                print("❌ No se obtuvo QR data")
                return False
        else:
            print(f"❌ QR Auto falló: {qr_response.status_code}")
            print(f"❌ Respuesta: {qr_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en get_qr_auto: {e}")
        return False

def test_frontend_rendering():
    """Probar si el frontend puede renderizar QR"""
    print("\n6️⃣ PROBANDO RENDERIZADO FRONTEND")
    
    # Crear un QR de prueba
    test_qr = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    print(f"📱 QR de prueba: {test_qr[:50]}...")
    
    # Verificar que QRCode.js está disponible
    try:
        qrcode_response = requests.get("https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js", timeout=5)
        if qrcode_response.status_code == 200:
            print("✅ QRCode.js disponible")
        else:
            print("❌ QRCode.js no disponible")
            return False
    except Exception as e:
        print(f"❌ Error verificando QRCode.js: {e}")
        return False
    
    return True

def provide_solution():
    """Proporcionar solución basada en el diagnóstico"""
    print("\n" + "=" * 60)
    print("🔧 SOLUCIÓN PASO A PASO")
    print("=" * 60)
    
    print("\n1️⃣ VERIFICAR QUE NORA ESTÁ CORRIENDO:")
    print("   cd /mnt/c/Users/PC/PYTHON/Auraai2")
    print("   source venv/bin/activate")
    print("   ./start_nora.sh")
    
    print("\n2️⃣ ACCEDER AL PANEL:")
    print("   http://localhost:5000/panel_cliente/aura/whatsapp")
    
    print("\n3️⃣ GENERAR QR:")
    print("   - Hacer clic en 'Flujo Automático'")
    print("   - Esperar 3-5 segundos")
    print("   - El QR debería aparecer automáticamente")
    
    print("\n4️⃣ SI NO APARECE EL QR:")
    print("   - Abrir DevTools (F12)")
    print("   - Verificar Console por errores")
    print("   - Verificar Network por llamadas fallidas")
    
    print("\n5️⃣ ALTERNATIVA DIRECTA:")
    print("   https://whatsapp-server-production-8f61.up.railway.app")
    print("   - Usar el backend directamente")

def main():
    """Función principal"""
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Probar flujo completo
    if test_full_flow():
        print("\n✅ FLUJO COMPLETO EXITOSO")
        print("💡 El problema puede estar en el frontend (JavaScript)")
        
        if test_frontend_rendering():
            print("✅ FRONTEND LISTO")
            print("🎉 TODO DEBERÍA FUNCIONAR CORRECTAMENTE")
            print("\n🔧 PRÓXIMO PASO: Verificar en navegador")
        else:
            print("❌ PROBLEMA EN FRONTEND")
            
    else:
        print("\n❌ PROBLEMA EN FLUJO BACKEND")
        print("🔧 Revisar logs y configuración")
    
    provide_solution()

if __name__ == "__main__":
    main()
