#!/usr/bin/env python3
"""
🧪 Script simple para iniciar servidor y probar endpoints
"""

import subprocess
import time
import requests
import json
import sys
import os

def iniciar_servidor():
    """Iniciar el servidor en background"""
    print("🚀 Iniciando servidor Flask...")
    try:
        # Cambiar al directorio del proyecto
        os.chdir(r"c:\Users\PC\PYTHON\AuraAi2")
        
        # Iniciar servidor en background
        proceso = subprocess.Popen(
            [sys.executable, "dev_start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Esperando que el servidor inicie...")
        time.sleep(10)  # Dar tiempo al servidor para iniciar
        
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def probar_endpoint():
    """Probar el endpoint de conocimiento"""
    print("\n🔍 Probando endpoint de conocimiento...")
    
    try:
        url = "http://localhost:5000/admin/nora/aura/entrenar/bloques"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta JSON: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"🎉 ¡Endpoint funcionando! {len(data.get('data', []))} bloques encontrados")
            else:
                print(f"⚠️ Endpoint responde pero success=False: {data.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor - ¿está ejecutándose?")
    except Exception as e:
        print(f"❌ Error: {e}")

def crear_datos_prueba():
    """Crear datos de prueba usando el endpoint debug"""
    print("\n➕ Creando datos de prueba...")
    
    try:
        url = "http://localhost:5000/admin/nora/aura/test-create"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos creados: {data}")
        else:
            print(f"❌ Error creando datos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 SCRIPT DE PRUEBA RÁPIDA")
    print("=" * 40)
    
    # Primero probar si el servidor ya está ejecutándose
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor ya está ejecutándose")
    except:
        print("⚠️ Servidor no está ejecutándose, iniciando...")
        proceso = iniciar_servidor()
        if not proceso:
            print("❌ No se pudo iniciar el servidor")
            return
    
    # Probar endpoints
    probar_endpoint()
    
    # Si no hay datos, crearlos
    print("\n" + "="*40)
    crear_datos_prueba()
    
    # Probar de nuevo después de crear datos
    print("\n" + "="*40)
    probar_endpoint()
    
    print("\n🌐 Panel de entrenamiento: http://localhost:5000/admin/nora/aura/entrenar")
    print("🧪 Abre la consola del navegador (F12) para ver logs detallados")

if __name__ == "__main__":
    main()
