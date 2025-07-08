#!/usr/bin/env python3
"""
Test específico para diagnosticar cuelgues en endpoints de QR
Analiza los endpoints /get_qr_auto y /qr que están colgándose
"""

import sys
import time
import threading
import requests
import signal
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# Configuración
NORA_URL = "http://localhost:5000"
BACKEND_URL = "https://whatsapp-backend-production-4b6c.up.railway.app"

class TimeoutDiagnostic:
    def __init__(self):
        self.results = []
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Manejar interrupción del usuario"""
        print("\n\n⛔ Interrumpido por el usuario")
        self.running = False
        sys.exit(0)
    
    def test_endpoint_with_timeout(self, endpoint, method="GET", timeout=30, data=None):
        """Probar endpoint con timeout específico"""
        print(f"\n🔍 Probando {method} {endpoint} (timeout: {timeout}s)")
        
        start_time = time.time()
        result = {
            'endpoint': endpoint,
            'method': method,
            'timeout': timeout,
            'start_time': start_time,
            'success': False,
            'elapsed': 0,
            'error': None,
            'response': None
        }
        
        try:
            if method == "GET":
                response = requests.get(endpoint, timeout=timeout)
            elif method == "POST":
                response = requests.post(endpoint, json=data or {}, timeout=timeout)
            else:
                raise ValueError(f"Método {method} no soportado")
            
            elapsed = time.time() - start_time
            result.update({
                'success': True,
                'elapsed': elapsed,
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_length': len(response.content),
                    'content_preview': response.text[:200] if response.text else None
                }
            })
            
            print(f"✅ {endpoint} - {response.status_code} ({elapsed:.2f}s)")
            
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            result.update({
                'elapsed': elapsed,
                'error': f'TIMEOUT después de {elapsed:.2f}s'
            })
            print(f"❌ {endpoint} - TIMEOUT ({elapsed:.2f}s)")
            
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            result.update({
                'elapsed': elapsed,
                'error': str(e)
            })
            print(f"❌ {endpoint} - ERROR: {e} ({elapsed:.2f}s)")
            
        except Exception as e:
            elapsed = time.time() - start_time
            result.update({
                'elapsed': elapsed,
                'error': f'Excepción: {str(e)}'
            })
            print(f"❌ {endpoint} - EXCEPCIÓN: {e} ({elapsed:.2f}s)")
        
        self.results.append(result)
        return result
    
    def test_concurrent_requests(self, endpoints, max_workers=5):
        """Probar múltiples endpoints concurrentemente"""
        print(f"\n🔄 Probando {len(endpoints)} endpoints concurrentemente (max_workers: {max_workers})")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for endpoint_config in endpoints:
                future = executor.submit(
                    self.test_endpoint_with_timeout,
                    endpoint_config['url'],
                    endpoint_config.get('method', 'GET'),
                    endpoint_config.get('timeout', 30),
                    endpoint_config.get('data', None)
                )
                futures.append(future)
            
            # Esperar resultados
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f"❌ Error en hilo: {e}")
    
    def test_nora_endpoints(self):
        """Probar endpoints de NORA"""
        print("\n🎯 PROBANDO ENDPOINTS DE NORA")
        print("=" * 50)
        
        # Endpoints de NORA a probar
        endpoints = [
            {
                'url': urljoin(NORA_URL, '/whatsapp/connect'),
                'method': 'POST',
                'timeout': 10,
                'data': {'timestamp': datetime.now().isoformat()}
            },
            {
                'url': urljoin(NORA_URL, '/whatsapp/status'),
                'method': 'GET',
                'timeout': 10
            },
            {
                'url': urljoin(NORA_URL, '/whatsapp/qr'),
                'method': 'GET',
                'timeout': 15  # Más tiempo para QR
            },
            {
                'url': urljoin(NORA_URL, '/whatsapp/get_qr_auto'),
                'method': 'GET',
                'timeout': 20  # Más tiempo para QR auto
            }
        ]
        
        # Probar uno por uno
        for endpoint_config in endpoints:
            if not self.running:
                break
            self.test_endpoint_with_timeout(
                endpoint_config['url'],
                endpoint_config['method'],
                endpoint_config['timeout'],
                endpoint_config.get('data')
            )
            time.sleep(1)  # Pausa entre pruebas
    
    def test_backend_endpoints(self):
        """Probar endpoints del backend Railway"""
        print("\n🚂 PROBANDO ENDPOINTS DEL BACKEND RAILWAY")
        print("=" * 50)
        
        # Endpoints del backend a probar
        endpoints = [
            {
                'url': urljoin(BACKEND_URL, '/health'),
                'method': 'GET',
                'timeout': 10
            },
            {
                'url': urljoin(BACKEND_URL, '/status'),
                'method': 'GET',
                'timeout': 10
            },
            {
                'url': urljoin(BACKEND_URL, '/connect'),
                'method': 'POST',
                'timeout': 15,
                'data': {'timestamp': datetime.now().isoformat()}
            },
            {
                'url': urljoin(BACKEND_URL, '/qr'),
                'method': 'GET',
                'timeout': 20
            }
        ]
        
        # Probar uno por uno
        for endpoint_config in endpoints:
            if not self.running:
                break
            self.test_endpoint_with_timeout(
                endpoint_config['url'],
                endpoint_config['method'],
                endpoint_config['timeout'],
                endpoint_config.get('data')
            )
            time.sleep(1)  # Pausa entre pruebas
    
    def test_concurrent_qr_requests(self):
        """Probar múltiples solicitudes de QR concurrentemente"""
        print("\n🔄 PROBANDO SOLICITUDES DE QR CONCURRENTES")
        print("=" * 50)
        
        # Múltiples solicitudes de QR
        qr_endpoints = [
            {
                'url': urljoin(NORA_URL, '/whatsapp/qr'),
                'method': 'GET',
                'timeout': 15
            },
            {
                'url': urljoin(NORA_URL, '/whatsapp/get_qr_auto'),
                'method': 'GET',
                'timeout': 20
            },
            {
                'url': urljoin(BACKEND_URL, '/qr'),
                'method': 'GET',
                'timeout': 15
            }
        ]
        
        # Ejecutar concurrentemente
        self.test_concurrent_requests(qr_endpoints * 3, max_workers=3)
    
    def test_sequential_qr_requests(self):
        """Probar solicitudes de QR secuenciales para identificar patrones"""
        print("\n📊 PROBANDO SOLICITUDES DE QR SECUENCIALES")
        print("=" * 50)
        
        qr_endpoints = [
            urljoin(NORA_URL, '/whatsapp/qr'),
            urljoin(NORA_URL, '/whatsapp/get_qr_auto'),
            urljoin(BACKEND_URL, '/qr')
        ]
        
        # Probar cada endpoint múltiples veces
        for i in range(3):
            print(f"\n🔄 Ronda {i+1}/3")
            for endpoint in qr_endpoints:
                if not self.running:
                    break
                self.test_endpoint_with_timeout(endpoint, timeout=15)
                time.sleep(2)  # Pausa entre solicitudes
    
    def monitor_endpoint_continuously(self, endpoint, duration=60):
        """Monitorear endpoint continuamente"""
        print(f"\n📡 MONITOREO CONTINUO DE {endpoint}")
        print(f"⏱️ Duración: {duration}s")
        print("=" * 50)
        
        start_time = time.time()
        request_count = 0
        success_count = 0
        
        while time.time() - start_time < duration and self.running:
            request_count += 1
            print(f"\n📡 Solicitud {request_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            result = self.test_endpoint_with_timeout(endpoint, timeout=10)
            if result['success']:
                success_count += 1
            
            # Pausa antes de la siguiente solicitud
            time.sleep(5)
        
        # Estadísticas del monitoreo
        elapsed = time.time() - start_time
        success_rate = (success_count / request_count) * 100 if request_count > 0 else 0
        
        print(f"\n📊 ESTADÍSTICAS DEL MONITOREO")
        print(f"🕒 Duración: {elapsed:.1f}s")
        print(f"📊 Solicitudes: {request_count}")
        print(f"✅ Exitosas: {success_count}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    def analyze_results(self):
        """Analizar resultados de las pruebas"""
        print("\n📊 ANÁLISIS DE RESULTADOS")
        print("=" * 50)
        
        if not self.results:
            print("❌ No hay resultados para analizar")
            return
        
        # Estadísticas generales
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        
        print(f"📊 Total de solicitudes: {total_requests}")
        print(f"✅ Exitosas: {successful_requests}")
        print(f"❌ Fallidas: {failed_requests}")
        print(f"📈 Tasa de éxito: {(successful_requests/total_requests)*100:.1f}%")
        
        # Análisis por endpoint
        print(f"\n📋 ANÁLISIS POR ENDPOINT")
        print("-" * 30)
        
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'total': 0, 'success': 0, 'timeouts': 0, 'errors': 0, 'avg_time': 0}
            
            stats = endpoint_stats[endpoint]
            stats['total'] += 1
            
            if result['success']:
                stats['success'] += 1
            elif result['error'] and 'TIMEOUT' in result['error']:
                stats['timeouts'] += 1
            else:
                stats['errors'] += 1
            
            stats['avg_time'] = (stats['avg_time'] * (stats['total'] - 1) + result['elapsed']) / stats['total']
        
        for endpoint, stats in endpoint_stats.items():
            print(f"\n🔗 {endpoint}")
            print(f"   📊 Total: {stats['total']}")
            print(f"   ✅ Éxito: {stats['success']}")
            print(f"   ⏱️ Timeouts: {stats['timeouts']}")
            print(f"   ❌ Errores: {stats['errors']}")
            print(f"   🕒 Tiempo promedio: {stats['avg_time']:.2f}s")
            if stats['total'] > 0:
                print(f"   📈 Tasa de éxito: {(stats['success']/stats['total'])*100:.1f}%")
        
        # Identificar endpoints problemáticos
        print(f"\n🚨 ENDPOINTS PROBLEMÁTICOS")
        print("-" * 30)
        
        for endpoint, stats in endpoint_stats.items():
            if stats['total'] > 0:
                success_rate = (stats['success'] / stats['total']) * 100
                if success_rate < 80:
                    print(f"⚠️ {endpoint} - {success_rate:.1f}% éxito")
                if stats['timeouts'] > 0:
                    print(f"🕒 {endpoint} - {stats['timeouts']} timeouts")
                if stats['avg_time'] > 10:
                    print(f"🐌 {endpoint} - {stats['avg_time']:.2f}s promedio")

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE CUELGUES EN ENDPOINTS")
    print("=" * 60)
    print(f"🎯 NORA: {NORA_URL}")
    print(f"🚂 Backend: {BACKEND_URL}")
    print(f"🕒 Inicio: {datetime.now()}")
    
    diagnostic = TimeoutDiagnostic()
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, diagnostic.signal_handler)
    
    try:
        # 1. Probar endpoints de NORA
        diagnostic.test_nora_endpoints()
        
        # 2. Probar endpoints del backend
        diagnostic.test_backend_endpoints()
        
        # 3. Probar solicitudes concurrentes
        diagnostic.test_concurrent_qr_requests()
        
        # 4. Probar solicitudes secuenciales
        diagnostic.test_sequential_qr_requests()
        
        # 5. Monitoreo continuo (opcional)
        print("\n❓ ¿Realizar monitoreo continuo? (30s)")
        print("Presiona Ctrl+C para omitir...")
        try:
            time.sleep(3)
            diagnostic.monitor_endpoint_continuously(
                urljoin(NORA_URL, '/whatsapp/get_qr_auto'),
                duration=30
            )
        except KeyboardInterrupt:
            print("\n⏭️ Monitoreo omitido")
        
        # 6. Análisis de resultados
        diagnostic.analyze_results()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Diagnóstico interrumpido por el usuario")
    
    except Exception as e:
        print(f"\n\n❌ Error durante el diagnóstico: {e}")
    
    # Resumen final
    print("\n🏁 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)
    diagnostic.analyze_results()

if __name__ == "__main__":
    main()
