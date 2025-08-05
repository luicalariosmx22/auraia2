#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el webhook de anuncios Meta Ads
"""

import requests
import json
from datetime import datetime

def simular_webhook_anuncio():
    """Simula un webhook de Meta para probar el procesamiento de anuncios"""
    
    webhook_url = "http://localhost:5000/meta/webhook"
    
    # Payload simulado de Meta cuando cambia un anuncio
    payload_meta = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": int(datetime.now().timestamp()),
                "changes": [
                    {
                        "field": "ad",
                        "value": {
                            "ad_id": "120234740965470322",
                            "ad_account_id": "295436653620645",
                            "campaign_id": "23851234567890123",
                            "adset_id": "23851234567890124",
                            "name": "Anuncio Test - Webhook Update",
                            "status": "ACTIVE",
                            "effective_status": "ACTIVE",
                            "configured_status": "ACTIVE",
                            "created_time": "2025-01-01T00:00:00+0000",
                            "updated_time": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                ]
            }
        ]
    }
    
    print("🧪 SIMULANDO WEBHOOK DE ANUNCIO META ADS")
    print("=" * 50)
    print(f"🎯 URL: {webhook_url}")
    print(f"📦 Payload:")
    print(json.dumps(payload_meta, indent=2, ensure_ascii=False))
    
    try:
        # Enviar webhook simulado
        response = requests.post(
            webhook_url,
            json=payload_meta,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 RESPUESTA DEL WEBHOOK:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ¡WEBHOOK PROCESADO EXITOSAMENTE!")
            print("🔄 El anuncio debería estar marcado para sincronización")
        else:
            print(f"\n❌ Error en webhook: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️ No se pudo conectar al servidor.")
        print("   Asegúrate de que la aplicación Flask esté ejecutándose")
        print("   Comando: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

def verificar_token_webhook():
    """Verifica que el token del webhook sea correcto"""
    
    verify_url = "http://localhost:5000/meta/webhook"
    params = {
        "hub.verify_token": "nora123",
        "hub.challenge": "test_challenge_12345"
    }
    
    print("\n🔐 VERIFICANDO TOKEN DEL WEBHOOK")
    print("=" * 40)
    
    try:
        response = requests.get(verify_url, params=params, timeout=10)
        
        if response.status_code == 200 and response.text == "test_challenge_12345":
            print("✅ Token verificado correctamente")
        else:
            print(f"❌ Error en verificación: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def main():
    print("🧪 PRUEBA DE WEBHOOK META ADS - ANUNCIOS")
    print("=" * 60)
    
    # Verificar token primero
    verificar_token_webhook()
    
    # Simular webhook de anuncio
    simular_webhook_anuncio()
    
    print("\n📋 QUÉ DEBERÍA PASAR:")
    print("1. ✅ Webhook recibe y valida el payload")
    print("2. ✅ Se registra evento en logs_webhooks_meta")
    print("3. ✅ Se identifica como evento de anuncio")
    print("4. ✅ Se marca anuncio para sincronización prioritaria")
    print("5. ✅ Se retorna respuesta exitosa")
    
    print("\n🔍 PARA VERIFICAR:")
    print("1. Revisar logs de la aplicación Flask")
    print("2. Consultar tabla logs_webhooks_meta en Supabase")
    print("3. Verificar que el anuncio esté marcado para sync")
    
    print("\n✨ ¡Prueba de webhook completada!")

if __name__ == "__main__":
    main()
