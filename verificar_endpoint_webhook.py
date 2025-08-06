#!/usr/bin/env python3
"""
Script para verificar correctamente el endpoint /meta/webhook
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local', override=True)

def test_webhook_verification():
    """Probar la verificación del webhook (simulando Facebook)"""
    print("🔍 PROBANDO VERIFICACIÓN DEL WEBHOOK")
    print("=" * 50)
    
    webhook_url = os.getenv('META_WEBHOOK_URL')
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    if not webhook_url or not verify_token:
        print("❌ Variables no configuradas")
        return
    
    print(f"🔗 URL: {webhook_url}")
    print(f"🔑 Verify Token: {verify_token}")
    
    # Simular la verificación que hace Facebook
    params = {
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge_12345',
        'hub.verify_token': verify_token
    }
    
    print(f"\n📡 Enviando verificación...")
    print(f"Parámetros: {params}")
    
    try:
        response = requests.get(webhook_url, params=params)
        
        print(f"\n🌐 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            if response.text == 'test_challenge_12345':
                print("✅ WEBHOOK VERIFICACIÓN EXITOSA")
                print("El endpoint responde correctamente a Facebook")
            else:
                print("⚠️ Respuesta inesperada")
        else:
            print("❌ Error en verificación")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_webhook_invalid_token():
    """Probar con token inválido (como cuando accedes desde navegador)"""
    print("\n" + "=" * 50)
    print("🔍 PROBANDO CON TOKEN INVÁLIDO (como navegador)")
    print("=" * 50)
    
    webhook_url = os.getenv('META_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ URL del webhook no configurada")
        return
    
    # Simular acceso desde navegador (sin parámetros correctos)
    params = {
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge_12345',
        'hub.verify_token': 'token_incorrecto'
    }
    
    print(f"📡 Enviando con token incorrecto...")
    
    try:
        response = requests.get(webhook_url, params=params)
        
        print(f"🌐 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if "Token inválido" in response.text or response.status_code == 403:
            print("✅ COMPORTAMIENTO CORRECTO")
            print("El endpoint rechaza tokens inválidos (como debe ser)")
        else:
            print("⚠️ Comportamiento inesperado")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_webhook_no_params():
    """Probar sin parámetros (como acceso directo desde navegador)"""
    print("\n" + "=" * 50)
    print("🔍 PROBANDO SIN PARÁMETROS (acceso directo)")
    print("=" * 50)
    
    webhook_url = os.getenv('META_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ URL del webhook no configurada")
        return
    
    print(f"📡 Accediendo directamente sin parámetros...")
    
    try:
        response = requests.get(webhook_url)
        
        print(f"🌐 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if "Token inválido" in response.text or response.status_code in [400, 403]:
            print("✅ COMPORTAMIENTO CORRECTO")
            print("Esto es lo que ves cuando accedes desde el navegador")
        else:
            print("⚠️ Comportamiento inesperado")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_webhook_health():
    """Verificar si hay un endpoint de health check"""
    print("\n" + "=" * 50)
    print("🔍 PROBANDO HEALTH CHECK")
    print("=" * 50)
    
    webhook_url = os.getenv('META_WEBHOOK_URL')
    if not webhook_url:
        print("❌ URL del webhook no configurada")
        return
        
    base_url = webhook_url.replace('/meta/webhook', '')
    health_urls = [
        f"{base_url}/health",
        f"{base_url}/status", 
        f"{base_url}/",
        f"{base_url}/meta/health"
    ]
    
    for url in health_urls:
        print(f"\n📡 Probando: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Respuesta: {response.text[:100]}...")
            else:
                print(f"   📄 Respuesta: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🎯 VERIFICACIÓN COMPLETA DEL WEBHOOK ENDPOINT")
    print("=" * 60)
    
    # 1. Verificación correcta (como Facebook)
    test_webhook_verification()
    
    # 2. Token inválido (como tu prueba)
    test_webhook_invalid_token()
    
    # 3. Sin parámetros (acceso directo)
    test_webhook_no_params()
    
    # 4. Health check
    test_webhook_health()
    
    print("\n" + "=" * 60)
    print("💡 CONCLUSIÓN:")
    print("Si ves 'Token inválido' al acceder directamente,")
    print("eso significa que el webhook está funcionando CORRECTAMENTE")
    print("y rechazando accesos no autorizados.")
    print("=" * 60)

if __name__ == "__main__":
    main()
