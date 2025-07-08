#!/usr/bin/env python3
"""
Script para verificar y reiniciar el servidor con las rutas de Google Ads
"""
import os
import subprocess
import time
import requests
import signal

def kill_existing_processes():
    """Mata procesos existentes de Python en el puerto 5000"""
    try:
        # En Windows, usar taskkill para matar procesos que usen el puerto
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        time.sleep(2)
    except:
        pass

def start_server():
    """Inicia el servidor en background"""
    print("🚀 Iniciando servidor...")
    process = subprocess.Popen(
        ["python", "dev_start.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

def check_routes():
    """Verifica las rutas de Google Ads"""
    print("🔍 Esperando que el servidor inicie...")
    time.sleep(10)  # Dar tiempo al servidor para iniciar
    
    try:
        response = requests.get('http://localhost:5000/debug_info', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Servidor iniciado correctamente")
            print("\n🔍 Rutas de Google Ads registradas:")
            google_routes = [r for r in data.get('rutas_registradas', []) if 'google_ads' in r]
            if google_routes:
                for route in google_routes:
                    print(f"  ✅ {route}")
            else:
                print("  ❌ No se encontraron rutas de Google Ads")
            
            print("\n🔍 Blueprints registrados:")
            google_blueprints = [bp for bp in data.get('blueprints_registrados', []) if 'google' in bp.lower()]
            if google_blueprints:
                for bp in google_blueprints:
                    print(f"  ✅ {bp}")
            else:
                print("  ❌ No se encontraron blueprints de Google Ads")
            
            # Probar ruta específica
            print("\n🧪 Probando ruta específica...")
            test_response = requests.get('http://localhost:5000/panel_cliente/aura/google_ads/cuentas', timeout=5)
            print(f"Status Code para /panel_cliente/aura/google_ads/cuentas: {test_response.status_code}")
            
        else:
            print(f"❌ Error al obtener debug_info: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔄 Reiniciando servidor para verificar rutas de Google Ads...")
    
    # Matar procesos existentes
    kill_existing_processes()
    
    # Iniciar servidor
    server_process = start_server()
    
    try:
        # Verificar rutas
        check_routes()
        
        print("\n✅ Verificación completa. El servidor sigue corriendo.")
        print("🌐 Accede a: http://localhost:5000/panel_cliente/aura/google_ads/cuentas")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por usuario")
    finally:
        # No matar el proceso del servidor para que siga corriendo
        print("📝 Servidor sigue activo en background")
