#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el webhook de Meta con debug habilitado
"""

import requests
import json
import hashlib
import hmac
import os
from dotenv import load_dotenv

load_dotenv()

def test_webhook_verification():
    """Probar la verificación del webhook"""
    print("🧪 Probando verificación del webhook...")
    
    # URL del webhook local (ajusta según tu configuración)
    webhook_url = "http://localhost:5000/webhooks/meta/webhook"
    
    # Token de verificación
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')
    
    # Simular verificación de Meta
    verification_params = {
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge_123',
        'hub.verify_token': verify_token
    }
    
    try:
        response = requests.get(webhook_url, params=verification_params)
        print(f"✅ Verificación - Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def test_webhook_data():
    """Probar webhook con datos de ejemplo"""
    print("🧪 Probando webhook con datos de ejemplo...")
    
    webhook_url = "http://localhost:5000/webhooks/meta/webhook"
    
    # Datos de ejemplo que podrían venir de Meta
    webhook_payload = {
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "changes": [
                    {
                        "field": "campaign",
                        "value": {
                            "campaign_id": "120330000123456789",
                            "status": "ACTIVE",
                            "name": "Test Campaign",
                            "nombre_nora": "TestNora"  # Este campo está causando problemas
                        }
                    }
                ]
            }
        ]
    }
    
    # Convertir a JSON
    payload_json = json.dumps(webhook_payload)
    payload_bytes = payload_json.encode('utf-8')
    
    # Generar firma válida
    app_secret = os.getenv('META_WEBHOOK_SECRET', '1002ivimyH!')
    signature = hmac.new(
        app_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': f'sha256={signature}'
    }
    
    print(f"📤 Enviando payload: {json.dumps(webhook_payload, indent=2)}")
    print(f"🔐 Signature: sha256={signature}")
    
    try:
        response = requests.post(webhook_url, data=payload_json, headers=headers)
        print(f"✅ Webhook - Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando webhook: {e}")
        return False

def test_webhook_without_problematic_field():
    """Probar webhook sin el campo problemático"""
    print("🧪 Probando webhook SIN campo problemático...")
    
    webhook_url = "http://localhost:5000/webhooks/meta/webhook"
    
    # Datos de ejemplo sin campos problemáticos
    webhook_payload = {
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "changes": [
                    {
                        "field": "campaign",
                        "value": {
                            "campaign_id": "120330000123456789",
                            "status": "ACTIVE",
                            "name": "Test Campaign"
                            # NO incluir nombre_nora
                        }
                    }
                ]
            }
        ]
    }
    
    # Convertir a JSON
    payload_json = json.dumps(webhook_payload)
    payload_bytes = payload_json.encode('utf-8')
    
    # Generar firma válida
    app_secret = os.getenv('META_WEBHOOK_SECRET', '1002ivimyH!')
    signature = hmac.new(
        app_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': f'sha256={signature}'
    }
    
    print(f"📤 Enviando payload limpio: {json.dumps(webhook_payload, indent=2)}")
    
    try:
        response = requests.post(webhook_url, data=payload_json, headers=headers)
        print(f"✅ Webhook limpio - Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando webhook limpio: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando tests de webhook...")
    print(f"🔑 META_WEBHOOK_SECRET configurado: {'Sí' if os.getenv('META_WEBHOOK_SECRET') else 'No'}")
    print(f"🎟️ META_WEBHOOK_VERIFY_TOKEN: {os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')}")
    print()
    
    # Test 1: Verificación
    test_webhook_verification()
    print()
    
    # Test 2: Webhook con campo problemático
    test_webhook_data()
    print()
    
    # Test 3: Webhook sin campo problemático
    test_webhook_without_problematic_field()
    print()
    
    print("🏁 Tests completados")
