#!/usr/bin/env python3
"""
Test del endpoint de cuentas con debug
"""

import requests
import json

def test_cuentas_endpoint():
    """Prueba el endpoint de cuentas webhook"""
    try:
        print("🧪 Testing /cuentas endpoint...")
        
        url = "http://localhost:5000/panel_cliente/aura/meta_ads/api/webhooks/cuentas"
        
        print(f"📡 Haciendo request a: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                print(f"📈 Success: {data.get('success', 'N/A')}")
                
                if 'estadisticas' in data:
                    stats = data['estadisticas']
                    print("\n📊 ESTADÍSTICAS:")
                    print(f"   Total cuentas: {stats.get('total_cuentas', 0)}")
                    print(f"   Con webhook: {stats.get('con_webhook', 0)}")
                    print(f"   Sin webhook: {stats.get('sin_webhook', 0)}")
                    print(f"   Cuentas activas: {stats.get('cuentas_activas', 0)}")
                    print(f"   Webhooks verificados: {stats.get('webhooks_verificados', 0)}")
                    print(f"   Errores verificación: {stats.get('errores_verificacion', 0)}")
                else:
                    print("⚠️ No hay estadísticas en la respuesta")
                
                if 'cuentas' in data:
                    cuentas = data['cuentas']
                    print(f"\n📋 CUENTAS ({len(cuentas)}):")
                    for i, cuenta in enumerate(cuentas[:3]):  # Solo primeras 3
                        webhook_status = "✅" if cuenta.get('webhook_registrado') else "❌"
                        print(f"   {i+1}. {cuenta.get('nombre_cliente', 'Sin nombre')} - {webhook_status}")
                    
                    if len(cuentas) > 3:
                        print(f"   ... y {len(cuentas) - 3} más")
                
                print(f"\n📄 Respuesta completa (JSON):")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Respuesta cruda: {response.text}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - ¿Está el servidor corriendo en localhost:5000?")
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor tardó más de 30 segundos en responder")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_cuentas_endpoint()
