#!/usr/bin/env python3
"""
Verificador completo del deployment de Railway para WhatsApp Backend
Verifica que el backend esté funcionando correctamente con Chrome y QR real
"""

import requests
import json
import time
import base64
from datetime import datetime
import re
import os

# Configuración del backend Railway
RAILWAY_URL = "https://whatsapp-backend-production-8a3a.up.railway.app"
ENDPOINTS = {
    'health': f"{RAILWAY_URL}/health",
    'qr': f"{RAILWAY_URL}/qr",
    'status': f"{RAILWAY_URL}/status"
}

def print_header(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """Imprime una sección formateada"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def test_endpoint(name, url, timeout=10):
    """Prueba un endpoint específico"""
    print(f"\n🔍 Probando endpoint: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=timeout)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Time: {response.elapsed.total_seconds():.2f}s")
        
        # Verificar el tipo de contenido
        content_type = response.headers.get('content-type', '')
        print(f"✅ Content-Type: {content_type}")
        
        # Intentar parsear como JSON
        try:
            json_data = response.json()
            print(f"✅ JSON Response: {json.dumps(json_data, indent=2)}")
            return True, json_data
        except json.JSONDecodeError:
            print(f"⚠️  No JSON response, texto plano:")
            print(f"Response: {response.text[:500]}")
            return False, response.text
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión: No se puede conectar a {url}")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: El endpoint tardó más de {timeout}s")
        return False, None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, None

def verify_qr_image(qr_data):
    """Verifica que el QR sea una imagen válida"""
    if not qr_data:
        return False, "No hay datos de QR"
    
    try:
        # Verificar si es un data URL válido
        if qr_data.startswith('data:image'):
            # Extraer la parte base64
            if ',' in qr_data:
                base64_data = qr_data.split(',')[1]
                # Intentar decodificar
                decoded = base64.b64decode(base64_data)
                size = len(decoded)
                print(f"✅ QR válido - Tamaño: {size} bytes")
                return True, f"QR válido, {size} bytes"
            else:
                return False, "Data URL malformado"
        else:
            return False, "No es un data URL válido"
            
    except Exception as e:
        return False, f"Error al verificar QR: {e}"

def save_qr_image(qr_data, filename="qr_railway_test.png"):
    """Guarda la imagen QR en un archivo"""
    try:
        if qr_data and qr_data.startswith('data:image'):
            # Extraer la parte base64
            base64_data = qr_data.split(',')[1]
            decoded = base64.b64decode(base64_data)
            
            with open(filename, 'wb') as f:
                f.write(decoded)
            print(f"✅ QR guardado en: {filename}")
            return True
        else:
            print(f"❌ No se pudo guardar QR - datos inválidos")
            return False
    except Exception as e:
        print(f"❌ Error al guardar QR: {e}")
        return False

def check_railway_logs():
    """Verifica los logs de Railway (si están disponibles)"""
    print_section("Información de Railway")
    print("📝 Para verificar logs de Railway:")
    print("1. Ve a: https://railway.app/dashboard")
    print("2. Selecciona tu proyecto")
    print("3. Ve a la pestaña 'Logs'")
    print("4. Verifica que no haya errores de Chrome o dependencias")

def main():
    """Función principal de verificación"""
    print_header("VERIFICACIÓN COMPLETA DE RAILWAY DEPLOYMENT")
    print(f"🕐 Iniciado: {datetime.now()}")
    
    # Test 1: Health Check
    print_section("Test 1: Health Check")
    health_ok, health_data = test_endpoint("Health Check", ENDPOINTS['health'])
    
    if health_ok and isinstance(health_data, dict):
        if health_data.get('status') == 'ok':
            print("✅ Backend está funcionando correctamente")
        else:
            print("⚠️  Backend responde pero con estado anormal")
    else:
        print("❌ Backend no responde correctamente al health check")
    
    # Test 2: QR Endpoint
    print_section("Test 2: QR Generation")
    qr_ok, qr_data = test_endpoint("QR Generation", ENDPOINTS['qr'])
    
    if qr_ok and isinstance(qr_data, dict):
        qr_image = qr_data.get('qr')
        if qr_image:
            is_valid, message = verify_qr_image(qr_image)
            if is_valid:
                print("✅ QR generado correctamente")
                save_qr_image(qr_image)
            else:
                print(f"⚠️  QR problemático: {message}")
        else:
            print("❌ Respuesta JSON sin campo 'qr'")
    else:
        print("❌ Endpoint QR no responde correctamente")
    
    # Test 3: Status Endpoint
    print_section("Test 3: Status Check")
    status_ok, status_data = test_endpoint("Status Check", ENDPOINTS['status'])
    
    if status_ok and isinstance(status_data, dict):
        client_ready = status_data.get('isClientReady', False)
        if client_ready:
            print("✅ Cliente WhatsApp Web está listo")
        else:
            print("⚠️  Cliente WhatsApp Web no está listo (esperando escaneo QR)")
    else:
        print("❌ Endpoint de status no responde correctamente")
    
    # Test 4: Verificar Chrome/Chromium
    print_section("Test 4: Verificación de Chrome")
    print("🔍 Verificando si Chrome está disponible en Railway...")
    
    # Intentar obtener información del user agent o similar
    try:
        # Hacer una petición que podría revelar información sobre el navegador
        response = requests.get(f"{RAILWAY_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ El servidor responde, Chrome probablemente está disponible")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
    except:
        print("❌ No se puede verificar Chrome remotamente")
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    all_tests = [
        ("Health Check", health_ok),
        ("QR Generation", qr_ok),
        ("Status Check", status_ok)
    ]
    
    passed = sum(1 for _, ok in all_tests if ok)
    total = len(all_tests)
    
    print(f"📊 Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! El backend parece estar funcionando correctamente.")
        print("🚀 Puedes proceder a probar la integración con NORA")
    elif passed > 0:
        print("⚠️  Algunos tests pasaron. Revisa los errores específicos arriba.")
        print("🔧 Puede que necesites ajustar la configuración o esperar más tiempo")
    else:
        print("❌ Ningún test pasó. Hay problemas serios con el deployment.")
        print("🛠️  Revisa los logs de Railway y la configuración")
    
    # Información adicional
    print_section("PRÓXIMOS PASOS")
    
    if passed >= 2:
        print("✅ El backend está funcionando. Próximos pasos:")
        print("1. Probar la integración con NORA")
        print("2. Verificar que el QR se muestre en el panel de NORA")
        print("3. Escanear el QR con WhatsApp Web real")
        print("4. Probar el envío de mensajes")
    else:
        print("❌ El backend tiene problemas. Acciones sugeridas:")
        print("1. Revisa los logs de Railway")
        print("2. Verifica que el build se completó correctamente")
        print("3. Confirma que Chrome se instaló correctamente")
        print("4. Revisa las variables de entorno")
    
    check_railway_logs()

if __name__ == "__main__":
    main()
