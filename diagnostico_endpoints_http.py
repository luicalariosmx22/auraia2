#!/usr/bin/env python3
"""
Diagnóstico específico de los endpoints HTTP que se cuelgan
"""

import requests
import time
import threading
from datetime import datetime
import json

# Configuración
NORA_URL = 'http://localhost:5000'
ENDPOINTS_TO_TEST = [
    '/aura/panel_cliente_whatsapp_web/connect',
    '/aura/panel_cliente_whatsapp_web/qr',
    '/aura/panel_cliente_whatsapp_web/get_qr_auto',
    '/aura/panel_cliente_whatsapp_web/status',
    '/aura/panel_cliente_whatsapp_web/login'
]

class HTTPEndpointDiagnostic:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, endpoint, method, status, elapsed_time, response_data=None, error=None):
        """Registrar resultado de prueba"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'elapsed_time': elapsed_time,
            'response_data': response_data,
            'error': str(error) if error else None
        }
        self.results.append(result)
        
    def test_endpoint_with_timeout(self, endpoint, method='GET', timeout=10, data=None):
        """Probar endpoint con timeout específico"""
        full_url = f"{NORA_URL}{endpoint}"
        
        print(f"\n🔍 Probando: {method} {endpoint}")
        print(f"🌐 URL completa: {full_url}")
        print(f"⏱️ Timeout: {timeout}s")
        
        start_time = time.time()
        status = 'UNKNOWN'
        response_data = None
        error = None
        
        try:
            if method == 'GET':
                response = self.session.get(full_url, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(full_url, json=data or {}, timeout=timeout)
            
            elapsed_time = time.time() - start_time
            status = f'HTTP_{response.status_code}'
            
            # Intentar obtener JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text[:200]  # Primeros 200 chars
            
            print(f"✅ Respuesta en {elapsed_time:.2f}s - Status: {response.status_code}")
            
            if response_data:
                print(f"📄 Respuesta: {response_data}")
            
            self.log_result(endpoint, method, status, elapsed_time, response_data)
            return True
            
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            status = 'TIMEOUT'
            error = f'Timeout después de {timeout}s'
            print(f"❌ TIMEOUT después de {elapsed_time:.2f}s")
            self.log_result(endpoint, method, status, elapsed_time, error=error)
            return False
            
        except requests.exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            status = 'CONNECTION_ERROR'
            error = str(e)
            print(f"❌ Error de conexión: {e}")
            self.log_result(endpoint, method, status, elapsed_time, error=error)
            return False
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            status = 'ERROR'
            error = str(e)
            print(f"❌ Error: {e}")
            self.log_result(endpoint, method, status, elapsed_time, error=error)
            return False
    
    def test_endpoint_with_cancellation(self, endpoint, cancel_after=5):
        """Probar endpoint con cancelación para detectar cuelgues"""
        full_url = f"{NORA_URL}{endpoint}"
        
        print(f"\n🚫 Probando cancelación: {endpoint}")
        print(f"⏱️ Cancelar después de: {cancel_after}s")
        
        start_time = time.time()
        request_cancelled = False
        
        def make_request():
            nonlocal request_cancelled
            try:
                response = self.session.get(full_url, timeout=30)
                elapsed_time = time.time() - start_time
                if not request_cancelled:
                    print(f"✅ Respuesta recibida en {elapsed_time:.2f}s")
                    self.log_result(endpoint, 'GET', f'HTTP_{response.status_code}', elapsed_time)
                else:
                    print(f"⚠️ Respuesta recibida después de cancelación: {elapsed_time:.2f}s")
            except Exception as e:
                elapsed_time = time.time() - start_time
                if not request_cancelled:
                    print(f"❌ Error en request: {e}")
                    self.log_result(endpoint, 'GET', 'ERROR', elapsed_time, error=str(e))
        
        # Iniciar request en hilo separado
        request_thread = threading.Thread(target=make_request)
        request_thread.daemon = True
        request_thread.start()
        
        # Esperar tiempo de cancelación
        time.sleep(cancel_after)
        
        if request_thread.is_alive():
            request_cancelled = True
            print(f"❌ Request aún corriendo después de {cancel_after}s - CUELGUE DETECTADO")
            
            # Esperar un poco más para ver si responde
            time.sleep(5)
            
            if request_thread.is_alive():
                print(f"❌ Request aún corriendo después de {cancel_after + 5}s - CUELGUE CONFIRMADO")
                elapsed_time = time.time() - start_time
                self.log_result(endpoint, 'GET', 'HANGING', elapsed_time, error='Request colgado')
                return False
            else:
                print(f"✅ Request terminó después de la cancelación")
                return True
        else:
            print(f"✅ Request terminó antes de la cancelación")
            return True
    
    def test_concurrent_requests(self, endpoint, num_requests=3):
        """Probar múltiples requests concurrentes"""
        print(f"\n👥 Probando {num_requests} requests concurrentes: {endpoint}")
        
        results = []
        threads = []
        
        def make_concurrent_request(request_id):
            full_url = f"{NORA_URL}{endpoint}"
            start_time = time.time()
            
            try:
                response = self.session.get(full_url, timeout=15)
                elapsed_time = time.time() - start_time
                result = {
                    'request_id': request_id,
                    'status': response.status_code,
                    'elapsed_time': elapsed_time,
                    'success': True
                }
                results.append(result)
                print(f"✅ Request #{request_id} completado en {elapsed_time:.2f}s")
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                result = {
                    'request_id': request_id,
                    'status': 'ERROR',
                    'elapsed_time': elapsed_time,
                    'error': str(e),
                    'success': False
                }
                results.append(result)
                print(f"❌ Request #{request_id} falló: {e}")
        
        # Lanzar requests concurrentes
        start_time = time.time()
        for i in range(num_requests):
            thread = threading.Thread(target=make_concurrent_request, args=(i+1,))
            threads.append(thread)
            thread.start()
            time.sleep(0.1)  # Pequeña separación
        
        # Esperar a que terminen (con timeout)
        for thread in threads:
            thread.join(timeout=20)
        
        total_elapsed = time.time() - start_time
        
        # Analizar resultados
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        print(f"\n📊 Resultados concurrentes:")
        print(f"  ✅ Exitosos: {len(successful)}/{num_requests}")
        print(f"  ❌ Fallidos: {len(failed)}/{num_requests}")
        print(f"  ⏱️ Tiempo total: {total_elapsed:.2f}s")
        
        if successful:
            avg_time = sum(r['elapsed_time'] for r in successful) / len(successful)
            print(f"  📈 Tiempo promedio: {avg_time:.2f}s")
        
        # Registrar resultado general
        self.log_result(endpoint, 'GET_CONCURRENT', f'SUCCESS_{len(successful)}', total_elapsed, {
            'successful': len(successful),
            'failed': len(failed),
            'total_requests': num_requests
        })
        
        return len(successful) == num_requests
    
    def run_comprehensive_test(self):
        """Ejecutar prueba completa"""
        print("🔍 DIAGNÓSTICO COMPLETO DE ENDPOINTS HTTP")
        print("=" * 60)
        print(f"🎯 NORA URL: {NORA_URL}")
        print(f"🕒 Inicio: {datetime.now()}")
        
        # 1. Probar conectividad básica
        print("\n1️⃣ PRUEBA DE CONECTIVIDAD BÁSICA")
        print("=" * 40)
        
        try:
            response = requests.get(NORA_URL, timeout=5)
            print(f"✅ NORA responde - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ NORA no responde: {e}")
            return
        
        # 2. Probar cada endpoint con timeout corto
        print("\n2️⃣ PRUEBA DE ENDPOINTS CON TIMEOUT CORTO (5s)")
        print("=" * 40)
        
        for endpoint in ENDPOINTS_TO_TEST:
            self.test_endpoint_with_timeout(endpoint, timeout=5)
            time.sleep(1)
        
        # 3. Probar endpoints problemáticos con timeout largo
        print("\n3️⃣ PRUEBA DE ENDPOINTS PROBLEMÁTICOS CON TIMEOUT LARGO (15s)")
        print("=" * 40)
        
        problematic_endpoints = [
            '/aura/panel_cliente_whatsapp_web/qr',
            '/aura/panel_cliente_whatsapp_web/get_qr_auto'
        ]
        
        for endpoint in problematic_endpoints:
            self.test_endpoint_with_timeout(endpoint, timeout=15)
            time.sleep(2)
        
        # 4. Probar con cancelación
        print("\n4️⃣ PRUEBA DE CANCELACIÓN (detectar cuelgues)")
        print("=" * 40)
        
        for endpoint in problematic_endpoints:
            self.test_endpoint_with_cancellation(endpoint, cancel_after=8)
            time.sleep(2)
        
        # 5. Probar requests concurrentes
        print("\n5️⃣ PRUEBA DE REQUESTS CONCURRENTES")
        print("=" * 40)
        
        # Probar endpoint que funciona
        self.test_concurrent_requests('/aura/panel_cliente_whatsapp_web/connect', num_requests=3)
        time.sleep(2)
        
        # Probar endpoint problemático
        self.test_concurrent_requests('/aura/panel_cliente_whatsapp_web/qr', num_requests=2)
        
        # 6. Mostrar resumen
        print("\n6️⃣ RESUMEN DE RESULTADOS")
        print("=" * 40)
        self.show_results_summary()
    
    def show_results_summary(self):
        """Mostrar resumen de resultados"""
        print("\n📊 RESUMEN DE PRUEBAS")
        print("=" * 30)
        
        # Agrupar por endpoint
        by_endpoint = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = []
            by_endpoint[endpoint].append(result)
        
        # Mostrar resumen por endpoint
        for endpoint, tests in by_endpoint.items():
            print(f"\n🔗 {endpoint}:")
            
            # Contar por status
            status_counts = {}
            total_time = 0
            
            for test in tests:
                status = test['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                total_time += test['elapsed_time']
            
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            if tests:
                avg_time = total_time / len(tests)
                print(f"  ⏱️ Tiempo promedio: {avg_time:.2f}s")
            
            # Identificar problemas
            timeouts = [t for t in tests if t['status'] == 'TIMEOUT']
            hanging = [t for t in tests if t['status'] == 'HANGING']
            
            if timeouts:
                print(f"  ⚠️ TIMEOUTS detectados: {len(timeouts)}")
            if hanging:
                print(f"  ❌ CUELGUES detectados: {len(hanging)}")
        
        # Estadísticas generales
        print(f"\n📈 ESTADÍSTICAS GENERALES")
        print(f"  Total de pruebas: {len(self.results)}")
        
        timeouts = [r for r in self.results if r['status'] == 'TIMEOUT']
        hanging = [r for r in self.results if r['status'] == 'HANGING']
        errors = [r for r in self.results if r['status'] == 'ERROR']
        
        print(f"  ⚠️ Timeouts: {len(timeouts)}")
        print(f"  ❌ Cuelgues: {len(hanging)}")
        print(f"  💥 Errores: {len(errors)}")
        
        # Endpoints más problemáticos
        print(f"\n🚨 ENDPOINTS MÁS PROBLEMÁTICOS:")
        problem_endpoints = []
        
        for endpoint, tests in by_endpoint.items():
            problem_count = len([t for t in tests if t['status'] in ['TIMEOUT', 'HANGING', 'ERROR']])
            if problem_count > 0:
                problem_endpoints.append((endpoint, problem_count))
        
        problem_endpoints.sort(key=lambda x: x[1], reverse=True)
        
        for endpoint, problems in problem_endpoints:
            print(f"  {endpoint}: {problems} problemas")

def main():
    """Función principal"""
    diagnostic = HTTPEndpointDiagnostic()
    
    try:
        diagnostic.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⛔ Diagnóstico interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante el diagnóstico: {e}")
    
    print(f"\n🏁 Diagnóstico completado - {datetime.now()}")

if __name__ == "__main__":
    main()
