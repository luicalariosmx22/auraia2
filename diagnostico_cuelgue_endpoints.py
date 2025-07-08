#!/usr/bin/env python3
"""
Diagnóstico específico de cuelgues en endpoints HTTP de WhatsApp
"""

import requests
import time
import threading
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración
NORA_URL = "http://localhost:5000"
BACKEND_URL = "https://whatsapp-server-production-8f61.up.railway.app"

class EndpointHangDiagnostic:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 15  # Timeout de 15 segundos
        
    def log_result(self, endpoint, method, status, elapsed_time, error=None):
        """Registrar resultado de prueba"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'elapsed_time': elapsed_time,
            'error': str(error) if error else None
        }
        self.results.append(result)
        return result
    
    def test_endpoint_with_timeout(self, endpoint, method='GET', data=None, timeout=10):
        """Probar endpoint con timeout específico"""
        start_time = time.time()
        
        try:
            print(f"🔍 Probando {method} {endpoint} (timeout: {timeout}s)...")
            
            if method == 'GET':
                response = self.session.get(endpoint, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(endpoint, json=data, timeout=timeout)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK en {elapsed_time:.2f}s")
                return self.log_result(endpoint, method, 'OK', elapsed_time)
            else:
                print(f"⚠️ {endpoint} - HTTP {response.status_code} en {elapsed_time:.2f}s")
                return self.log_result(endpoint, method, f'HTTP_{response.status_code}', elapsed_time)
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"⏱️ {endpoint} - TIMEOUT después de {elapsed_time:.2f}s")
            return self.log_result(endpoint, method, 'TIMEOUT', elapsed_time, 'Timeout')
            
        except requests.exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            print(f"🔌 {endpoint} - CONNECTION ERROR en {elapsed_time:.2f}s: {e}")
            return self.log_result(endpoint, method, 'CONNECTION_ERROR', elapsed_time, e)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ {endpoint} - ERROR en {elapsed_time:.2f}s: {e}")
            return self.log_result(endpoint, method, 'ERROR', elapsed_time, e)
    
    def test_whatsapp_endpoints(self):
        """Probar todos los endpoints de WhatsApp"""
        print("\n🔍 DIAGNÓSTICO DE ENDPOINTS DE WHATSAPP")
        print("=" * 60)
        
        # Endpoints a probar
        endpoints = [
            # Endpoint principal del panel
            f"{NORA_URL}/panel_cliente/aura/whatsapp/",
            
            # Endpoints AJAX problemáticos
            f"{NORA_URL}/panel_cliente/aura/whatsapp/qr",
            f"{NORA_URL}/panel_cliente/aura/whatsapp/get_qr_auto",
            f"{NORA_URL}/panel_cliente/aura/whatsapp/connect",
            f"{NORA_URL}/panel_cliente/aura/whatsapp/status",
            f"{NORA_URL}/panel_cliente/aura/whatsapp/login",
            
            # Endpoints de health check
            f"{NORA_URL}/health",
            f"{NORA_URL}/",
        ]
        
        # Probar cada endpoint
        for endpoint in endpoints:
            self.test_endpoint_with_timeout(endpoint, timeout=12)
            time.sleep(0.5)  # Pequeña pausa entre pruebas
    
    def test_concurrent_requests(self):
        """Probar solicitudes concurrentes para detectar deadlocks"""
        print("\n🔄 PRUEBA DE SOLICITUDES CONCURRENTES")
        print("=" * 60)
        
        # Endpoint problemático
        endpoint = f"{NORA_URL}/panel_cliente/aura/whatsapp/qr"
        
        def make_request(request_id):
            """Hacer una solicitud con ID específico"""
            start_time = time.time()
            try:
                response = requests.get(endpoint, timeout=10)
                elapsed_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'status': 'OK' if response.status_code == 200 else f'HTTP_{response.status_code}',
                    'elapsed_time': elapsed_time
                }
            except Exception as e:
                elapsed_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'status': 'ERROR',
                    'elapsed_time': elapsed_time,
                    'error': str(e)
                }
        
        # Hacer 5 solicitudes concurrentes
        print(f"🚀 Enviando 5 solicitudes concurrentes a {endpoint}...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            
            # Recoger resultados
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"📋 Solicitud #{result['request_id']}: {result['status']} en {result['elapsed_time']:.2f}s")
        
        total_elapsed = time.time() - start_time
        print(f"\n⏱️ Tiempo total: {total_elapsed:.2f}s")
        
        # Analizar resultados
        success_count = sum(1 for r in results if r['status'] == 'OK')
        timeout_count = sum(1 for r in results if 'timeout' in r.get('error', '').lower())
        
        print(f"✅ Exitosas: {success_count}/5")
        print(f"⏱️ Timeouts: {timeout_count}/5")
        
        if timeout_count > 0:
            print("⚠️ POSIBLE DEADLOCK O BLOQUEO DETECTADO")
        
        return results
    
    def test_step_by_step_flow(self):
        """Probar flujo paso a paso para identificar el punto exacto del cuelgue"""
        print("\n🔍 PRUEBA PASO A PASO DEL FLUJO")
        print("=" * 60)
        
        # Simular el flujo del frontend
        steps = [
            ("1. Cargar panel", f"{NORA_URL}/panel_cliente/aura/whatsapp/"),
            ("2. Verificar estado", f"{NORA_URL}/panel_cliente/aura/whatsapp/status"),
            ("3. Conectar WhatsApp", f"{NORA_URL}/panel_cliente/aura/whatsapp/connect"),
            ("4. Obtener QR", f"{NORA_URL}/panel_cliente/aura/whatsapp/qr"),
            ("5. QR automático", f"{NORA_URL}/panel_cliente/aura/whatsapp/get_qr_auto"),
        ]
        
        for step_name, endpoint in steps:
            print(f"\n📍 {step_name}")
            print(f"🔗 URL: {endpoint}")
            
            # Probar con timeout progresivo
            timeouts = [5, 10, 15]
            success = False
            
            for timeout in timeouts:
                result = self.test_endpoint_with_timeout(endpoint, timeout=timeout)
                if result['status'] == 'OK':
                    success = True
                    break
                elif result['status'] == 'TIMEOUT':
                    print(f"⏱️ Timeout de {timeout}s excedido")
                    continue
                else:
                    break
            
            if not success:
                print(f"❌ FALLO EN: {step_name}")
                print("💡 El cuelgue ocurre en este paso")
                break
            else:
                print(f"✅ {step_name} - OK")
    
    def test_backend_websocket_comparison(self):
        """Comparar rendimiento con backend WebSocket"""
        print("\n🔄 COMPARACIÓN CON BACKEND WEBSOCKET")
        print("=" * 60)
        
        # Probar health check del backend
        backend_health = f"{BACKEND_URL}/health"
        print(f"🔍 Probando backend: {backend_health}")
        
        result = self.test_endpoint_with_timeout(backend_health, timeout=5)
        
        if result['status'] == 'OK':
            print("✅ Backend WebSocket responde rápidamente")
        else:
            print("⚠️ Backend WebSocket también tiene problemas")
        
        # Comparar con NORA
        nora_health = f"{NORA_URL}/health"
        print(f"🔍 Probando NORA: {nora_health}")
        
        result = self.test_endpoint_with_timeout(nora_health, timeout=5)
        
        if result['status'] == 'OK':
            print("✅ NORA responde rápidamente")
            print("💡 El problema está específicamente en los endpoints de WhatsApp")
        else:
            print("⚠️ NORA también tiene problemas generales")
    
    def show_summary(self):
        """Mostrar resumen de resultados"""
        print("\n📊 RESUMEN DE DIAGNÓSTICO")
        print("=" * 60)
        
        # Estadísticas por estado
        status_counts = {}
        time_stats = {'min': float('inf'), 'max': 0, 'total': 0, 'count': 0}
        
        for result in self.results:
            status = result['status']
            elapsed = result['elapsed_time']
            
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if elapsed < time_stats['min']:
                time_stats['min'] = elapsed
            if elapsed > time_stats['max']:
                time_stats['max'] = elapsed
            time_stats['total'] += elapsed
            time_stats['count'] += 1
        
        print("📋 Resultados por estado:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        if time_stats['count'] > 0:
            avg_time = time_stats['total'] / time_stats['count']
            print(f"\n⏱️ Estadísticas de tiempo:")
            print(f"  Mínimo: {time_stats['min']:.2f}s")
            print(f"  Máximo: {time_stats['max']:.2f}s")
            print(f"  Promedio: {avg_time:.2f}s")
        
        # Endpoints problemáticos
        slow_endpoints = [r for r in self.results if r['elapsed_time'] > 5]
        if slow_endpoints:
            print(f"\n🐌 Endpoints lentos (>5s):")
            for result in slow_endpoints:
                print(f"  {result['endpoint']}: {result['elapsed_time']:.2f}s ({result['status']})")
        
        # Endpoints con timeout
        timeout_endpoints = [r for r in self.results if r['status'] == 'TIMEOUT']
        if timeout_endpoints:
            print(f"\n⏱️ Endpoints con timeout:")
            for result in timeout_endpoints:
                print(f"  {result['endpoint']}: {result['elapsed_time']:.2f}s")

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE CUELGUES EN ENDPOINTS HTTP")
    print("=" * 70)
    print(f"🎯 NORA: {NORA_URL}")
    print(f"🎯 Backend: {BACKEND_URL}")
    print(f"🕒 Inicio: {datetime.now()}")
    
    diagnostic = EndpointHangDiagnostic()
    
    try:
        # 1. Probar endpoints básicos
        print("\n1️⃣ FASE DE PRUEBA DE ENDPOINTS")
        print("=" * 40)
        diagnostic.test_whatsapp_endpoints()
        
        # 2. Probar solicitudes concurrentes
        print("\n2️⃣ FASE DE PRUEBA CONCURRENTE")
        print("=" * 40)
        diagnostic.test_concurrent_requests()
        
        # 3. Probar flujo paso a paso
        print("\n3️⃣ FASE DE FLUJO PASO A PASO")
        print("=" * 40)
        diagnostic.test_step_by_step_flow()
        
        # 4. Comparar con backend
        print("\n4️⃣ FASE DE COMPARACIÓN")
        print("=" * 40)
        diagnostic.test_backend_websocket_comparison()
        
        # 5. Mostrar resumen
        print("\n5️⃣ RESUMEN FINAL")
        print("=" * 40)
        diagnostic.show_summary()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Diagnóstico interrumpido por el usuario")
    
    except Exception as e:
        print(f"\n\n❌ Error durante el diagnóstico: {e}")
    
    # Conclusiones
    print("\n🎯 CONCLUSIONES")
    print("=" * 70)
    
    timeouts = [r for r in diagnostic.results if r['status'] == 'TIMEOUT']
    slow_requests = [r for r in diagnostic.results if r['elapsed_time'] > 5]
    
    if timeouts:
        print("❌ PROBLEMA CONFIRMADO: Endpoints con timeout detectados")
        print("💡 Causa probable: Deadlock o bloqueo en el código Python")
        print("🔧 Solución: Revisar locks, timeouts y llamadas bloqueantes")
    elif slow_requests:
        print("⚠️ PROBLEMA PARCIAL: Endpoints lentos detectados")
        print("💡 Causa probable: Operaciones lentas o esperas innecesarias")
        print("🔧 Solución: Optimizar tiempos de espera y operaciones")
    else:
        print("✅ NO HAY PROBLEMAS: Todos los endpoints responden correctamente")
        print("💡 El problema podría ser intermitente o específico de contexto")

if __name__ == "__main__":
    main()
