#!/usr/bin/env python3
"""
Test directo de la función registrar_evento_supabase para debug
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_registrar_evento_directo():
    """Test directo de la función registrar_evento_supabase"""
    print("🧪 Probando registrar_evento_supabase directamente...")
    
    try:
        from clientes.aura.utils.meta_webhook_helpers import registrar_evento_supabase
        
        # Test con datos normales
        resultado = registrar_evento_supabase(
            objeto='campaign',
            objeto_id='120330000123456789',
            campo='status',
            valor='ACTIVE',
            hora_evento=datetime.utcnow().isoformat()
        )
        
        print(f"✅ Resultado test normal: {resultado}")
        
        # Test con valor que podría tener nombre_nora
        valor_problemático = {
            'campaign_id': '120330000123456789',
            'status': 'ACTIVE',
            'nombre_nora': 'TestNora'
        }
        
        # Este debería funcionar porque ahora solo enviamos el valor como string
        resultado2 = registrar_evento_supabase(
            objeto='campaign',
            objeto_id='120330000123456789',
            campo='complex_data',
            valor=str(valor_problemático),  # Convertir a string
            hora_evento=datetime.utcnow().isoformat()
        )
        
        print(f"✅ Resultado test complejo: {resultado2}")
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")

def test_webhook_processing():
    """Test del procesamiento completo de webhook"""
    print("🧪 Probando procesamiento completo de webhook...")
    
    try:
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import recibir_webhook
        from flask import Flask, request
        import json
        
        # Datos de webhook con nombre_nora
        webhook_data = {
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
                                "nombre_nora": "TestNora"  # Este campo debería ser filtrado
                            }
                        }
                    ]
                }
            ]
        }
        
        print(f"📤 Datos de webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Nota: No podemos probar la función Flask directamente sin contexto de request
        print("⚠️ Para probar el webhook completo, necesitarías hacer una request HTTP real")
        
    except Exception as e:
        print(f"❌ Error en test de webhook: {e}")

if __name__ == "__main__":
    print("🔧 Iniciando tests directos...")
    
    test_registrar_evento_directo()
    print()
    test_webhook_processing()
    print()
    
    print("🏁 Tests directos completados")
