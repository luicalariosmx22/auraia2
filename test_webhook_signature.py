#!/usr/bin/env python3
"""
Test para verificar si el webhook funcionaría con las variables correctas
"""
import hashlib
import hmac
import json

# Simular datos de webhook
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
                        "status": "ACTIVE"
                    }
                }
            ]
        }
    ]
}

payload_json = json.dumps(webhook_payload)
payload_bytes = payload_json.encode('utf-8')

# Probar con el secret correcto
correct_secret = "1002ivimyH!"
signature = hmac.new(
    correct_secret.encode('utf-8'),
    payload_bytes,
    hashlib.sha256
).hexdigest()

print("🧪 TEST DE VERIFICACIÓN DE WEBHOOK")
print("=" * 50)
print(f"📦 Payload: {payload_json}")
print(f"🔐 Secret usado: {correct_secret}")
print(f"📏 Longitud del secret: {len(correct_secret)}")
print(f"✅ Firma generada: {signature}")
print()
print("💡 Esta es la firma que Meta debería enviar")
print("   si usa el mismo secret en su configuración.")
print()
print("🎯 ACCIÓN REQUERIDA:")
print("1. Configurar META_WEBHOOK_SECRET=1002ivimyH! en Railway")
print("2. Verificar que Meta Developers también use este mismo secret")
print("3. Si el secret en Meta es diferente, usar ese en Railway")
