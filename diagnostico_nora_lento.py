#!/usr/bin/env python3
"""
Diagnóstico rápido para NORA local lento
"""

import requests
import time
import psutil
import json
import os
from datetime import datetime

def check_system_resources():
    """Verificar recursos del sistema"""
    print("=== RECURSOS DEL SISTEMA ===")
    print(f"CPU: {psutil.cpu_percent(interval=1):.1f}%")
    print(f"RAM: {psutil.virtual_memory().percent:.1f}%")
    print(f"Procesos activos: {len(psutil.pids())}")
    
    # Buscar procesos que consuman mucha CPU/RAM
    print("\n=== PROCESOS QUE CONSUMEN MÁS RECURSOS ===")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    
    # Ordenar por CPU
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    for i, proc in enumerate(processes[:5]):
        print(f"{i+1}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}% RAM: {proc['memory_percent']:.1f}%")

def check_backend_health():
    """Verificar salud del backend"""
    print("\n=== VERIFICANDO BACKEND ===")
    
    backends = [
        "http://localhost:8080",
        "http://localhost:3000", 
        "http://localhost:5000"
    ]
    
    for backend in backends:
        try:
            start_time = time.time()
            response = requests.get(f"{backend}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ {backend} - OK ({response_time:.0f}ms)")
            else:
                print(f"⚠️  {backend} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {backend} - Error: {str(e)}")

def check_whatsapp_endpoint():
    """Verificar endpoint específico de WhatsApp"""
    print("\n=== VERIFICANDO WHATSAPP ENDPOINT ===")
    
    backends = [
        "http://localhost:8080",
        "http://localhost:3000"
    ]
    
    for backend in backends:
        try:
            start_time = time.time()
            response = requests.get(f"{backend}/qr", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ {backend}/qr - OK ({response_time:.0f}ms)")
                # Verificar si es un QR válido
                if "data:image" in response.text or "qr_code" in response.text:
                    print(f"   📱 QR válido detectado")
                else:
                    print(f"   ⚠️  Respuesta no parece ser QR: {response.text[:100]}...")
            else:
                print(f"⚠️  {backend}/qr - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {backend}/qr - Error: {str(e)}")

def check_chrome_processes():
    """Verificar procesos de Chrome/Puppeteer"""
    print("\n=== VERIFICANDO CHROME/PUPPETEER ===")
    
    chrome_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
        try:
            if 'chrome' in proc.info['name'].lower() or 'chromium' in proc.info['name'].lower():
                chrome_processes.append(proc.info)
        except:
            pass
    
    if chrome_processes:
        print(f"Procesos Chrome encontrados: {len(chrome_processes)}")
        for proc in chrome_processes[:3]:  # Mostrar solo los primeros 3
            print(f"  - {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}% RAM: {proc['memory_percent']:.1f}%")
    else:
        print("❌ No se encontraron procesos Chrome")

def check_log_files():
    """Buscar archivos de log para errores"""
    print("\n=== VERIFICANDO LOGS ===")
    
    log_files = [
        "error.log",
        "nora_restart.log", 
        "ejecucion_supabase.log",
        "ejecucion_google_ads_test.txt"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"📄 {log_file} - Últimas líneas:")
                        for line in lines[-3:]:  # Últimas 3 líneas
                            print(f"   {line.strip()}")
                    else:
                        print(f"📄 {log_file} - Vacío")
            except Exception as e:
                print(f"❌ Error leyendo {log_file}: {e}")
        else:
            print(f"📄 {log_file} - No existe")

def main():
    print("=== DIAGNÓSTICO NORA LOCAL LENTO ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_system_resources()
    check_backend_health()
    check_whatsapp_endpoint()
    check_chrome_processes()
    check_log_files()
    
    print("\n=== RECOMENDACIONES ===")
    print("1. Si hay muchos procesos Chrome, reinicia el backend WhatsApp")
    print("2. Si el CPU/RAM está alto, cierra aplicaciones innecesarias")
    print("3. Si /qr tarda mucho, el problema está en Puppeteer/Chrome")
    print("4. Revisa los logs para errores específicos")
    print("5. Considera usar el backend deployado en Railway si local es muy lento")

if __name__ == "__main__":
    main()
