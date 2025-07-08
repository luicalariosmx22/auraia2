#!/usr/bin/env python3
"""
Test específico del flujo automático que se colgaba
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
CLIENTE = "aura"
WHATSAPP_URL = f"{BASE_URL}/panel_cliente/{CLIENTE}/whatsapp"

def test_flujo_automatico():
    """Probar específicamente el flujo automático"""
    print("🧪 TEST DEL FLUJO AUTOMÁTICO")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        print(f"📡 POST {WHATSAPP_URL}/get_qr_auto")
        response = requests.post(f"{WHATSAPP_URL}/get_qr_auto", 
                               json={}, 
                               headers={'Content-Type': 'application/json'},
                               timeout=15)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Tiempo de respuesta: {duration:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta exitosa:")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Has QR: {data.get('has_qr', False)}")
                print(f"   - Authenticated: {data.get('authenticated', False)}")
                print(f"   - Message: {data.get('message', 'N/A')}")
                print(f"   - Session ID: {data.get('session_id', 'N/A')}")
                
                if data.get('qr_data'):
                    qr_length = len(data['qr_data'])
                    print(f"   - QR Data: {qr_length} chars")
                
                return True
            except Exception as e:
                print(f"❌ Error parsing JSON: {e}")
                print(f"📄 Raw response: {response.text[:200]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏰ TIMEOUT después de {duration:.2f}s")
        return False
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error después de {duration:.2f}s: {e}")
        return False

def test_refresh_qr():
    """Probar específicamente el refresh QR"""
    print("\n🔄 TEST DEL REFRESH QR")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        print(f"📡 GET {WHATSAPP_URL}/qr")
        response = requests.get(f"{WHATSAPP_URL}/qr", timeout=10)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Tiempo de respuesta: {duration:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta exitosa:")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Message: {data.get('message', 'N/A')}")
                print(f"   - Is Test: {data.get('is_test', False)}")
                
                if data.get('qr_data'):
                    qr_length = len(data['qr_data'])
                    qr_preview = data['qr_data'][:50] + "..." if len(data['qr_data']) > 50 else data['qr_data']
                    print(f"   - QR Data: {qr_length} chars - {qr_preview}")
                
                return True
            except Exception as e:
                print(f"❌ Error parsing JSON: {e}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏰ TIMEOUT después de {duration:.2f}s")
        return False
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error después de {duration:.2f}s: {e}")
        return False

def test_multiples_llamadas():
    """Probar múltiples llamadas seguidas"""
    print("\n🔁 TEST DE MÚLTIPLES LLAMADAS")
    print("=" * 50)
    
    tests = [
        ("Flujo Auto 1", "get_qr_auto"),
        ("Refresh QR 1", "qr"),  
        ("Flujo Auto 2", "get_qr_auto"),
        ("Refresh QR 2", "qr"),
        ("Connect", "connect"),
    ]
    
    results = []
    
    for test_name, endpoint in tests:
        print(f"\n🔄 {test_name}...")
        start_time = time.time()
        
        try:
            if endpoint == "get_qr_auto" or endpoint == "connect":
                url = f"{WHATSAPP_URL}/{endpoint}"
                response = requests.post(url, json={}, timeout=8)
            else:
                url = f"{WHATSAPP_URL}/{endpoint}"
                response = requests.get(url, timeout=8)
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = response.status_code == 200
            results.append((test_name, success, duration))
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {duration:.2f}s - Status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            duration = end_time - start_time
            results.append((test_name, False, duration))
            print(f"   ⏰ TIMEOUT {duration:.2f}s")
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            results.append((test_name, False, duration))
            print(f"   ❌ ERROR {duration:.2f}s: {e}")
    
    # Resumen
    print(f"\n📊 RESUMEN DE MÚLTIPLES LLAMADAS:")
    total_time = sum(duration for _, _, duration in results)
    successful = sum(1 for _, success, _ in results if success)
    
    for test_name, success, duration in results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}: {duration:.2f}s")
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   - Exitosas: {successful}/{len(results)}")
    print(f"   - Tiempo total: {total_time:.2f}s")
    print(f"   - Tiempo promedio: {total_time/len(results):.2f}s")
    
    return successful == len(results)

def main():
    """Función principal"""
    print("🧪 TEST ESPECÍFICO DE FLUJOS QUE SE COLGABAN")
    print("=" * 60)
    print(f"🕒 Inicio: {datetime.now()}")
    
    # Test 1: Flujo automático
    success1 = test_flujo_automatico()
    
    # Test 2: Refresh QR  
    success2 = test_refresh_qr()
    
    # Test 3: Múltiples llamadas
    success3 = test_multiples_llamadas()
    
    # Resultado final
    print(f"\n🏁 RESULTADO FINAL")
    print("=" * 60)
    print(f"✅ Flujo Automático: {'OK' if success1 else 'FAIL'}")
    print(f"✅ Refresh QR: {'OK' if success2 else 'FAIL'}")
    print(f"✅ Múltiples Llamadas: {'OK' if success3 else 'FAIL'}")
    
    all_success = success1 and success2 and success3
    
    if all_success:
        print(f"\n🎉 TODOS LOS TESTS PASARON - YA NO SE CUELGA")
    else:
        print(f"\n⚠️ ALGUNOS TESTS FALLARON - REVISAR")
    
    print(f"🕒 Fin: {datetime.now()}")

if __name__ == "__main__":
    main()
