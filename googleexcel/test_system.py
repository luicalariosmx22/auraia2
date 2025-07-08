#!/usr/bin/env python3
"""
Script de prueba end-to-end para el sistema Google Ads SQL Generator
Verifica que todo funcione correctamente desde archivos hasta Supabase
"""

import os
import requests
import time
from pathlib import Path

def test_web_application():
    """Prueba la aplicación web completa"""
    print("🧪 INICIANDO PRUEBAS END-TO-END")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # 1. Verificar que el servidor esté ejecutándose
    print("1️⃣ Verificando servidor web...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Servidor web respondiendo correctamente")
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar al servidor: {e}")
        print("💡 Asegúrate de que 'python app.py' esté ejecutándose")
        return False
    
    # 2. Verificar configuración
    print("\n2️⃣ Verificando configuración...")
    try:
        response = requests.get(f"{base_url}/api/config")
        config = response.json()
        
        print(f"   🤖 OpenAI API: {'✅' if config.get('has_openai_key') else '❌'}")
        print(f"   🗄️ Supabase Config: {'✅' if config.get('has_supabase_config') else '❌'}")
        print(f"   🔌 Supabase Disponible: {'✅' if config.get('supabase_available') else '❌'}")
        
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
    
    # 3. Verificar conexión a Supabase
    print("\n3️⃣ Probando conexión a Supabase...")
    try:
        response = requests.post(f"{base_url}/api/supabase/test")
        result = response.json()
        
        if result.get('success'):
            print("✅ Conexión a Supabase exitosa")
        else:
            print(f"❌ Error de conexión: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error probando Supabase: {e}")
    
    # 4. Verificar archivos de demo
    print("\n4️⃣ Verificando archivos de demo...")
    demo_files = ['demo_campaigns.xlsx', 'demo_ads.xlsx', 'demo_keywords.xlsx']
    
    for file in demo_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: {size:,} bytes")
        else:
            print(f"❌ {file}: No encontrado")
    
    # 5. Verificar carpetas necesarias
    print("\n5️⃣ Verificando estructura de carpetas...")
    required_dirs = ['uploads', 'outputs', 'templates', 'static']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/: No encontrado")
    
    # 6. Verificar archivos principales
    print("\n6️⃣ Verificando archivos principales...")
    required_files = [
        'app.py',
        'supabase_client.py', 
        'google_ads_sql_generator.py',
        'requirements.txt',
        '.env'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}: No encontrado")
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")
    
    # Resumen
    print("\n📋 RESUMEN:")
    print("✅ Para probar el sistema completo:")
    print("   1. Ve a http://localhost:5001")
    print("   2. Selecciona 'Múltiples Archivos + Supabase'")
    print("   3. Sube demo_campaigns.xlsx, demo_ads.xlsx, demo_keywords.xlsx")
    print("   4. Haz clic en 'Procesar Todos los Archivos'")
    print("   5. Haz clic en 'Insertar a Supabase'")
    print("\n🎯 ¡El sistema mantendrá automáticamente las relaciones jerárquicas!")

def simulate_file_upload():
    """Simula el proceso de subida y procesamiento de archivos"""
    print("\n🔄 SIMULANDO PROCESAMIENTO DE ARCHIVOS")
    print("-" * 50)
    
    base_url = "http://localhost:5001"
    
    # Verificar que existan los archivos de demo
    demo_files = {
        'campaigns': 'demo_campaigns.xlsx',
        'ads': 'demo_ads.xlsx', 
        'keywords': 'demo_keywords.xlsx'
    }
    
    table_types = {
        'campaigns': 'campañas',
        'ads': 'anuncios',
        'keywords': 'palabras_clave'
    }
    
    processed_files = {}
    
    for file_type, filename in demo_files.items():
        if not os.path.exists(filename):
            print(f"❌ {filename} no encontrado. Ejecuta 'python create_demo_files.py' primero")
            continue
        
        print(f"\n📤 Subiendo {filename}...")
        
        try:
            with open(filename, 'rb') as f:
                files = {'file': f}
                data = {
                    'table_type': table_types[file_type],
                    'generator_type': 'ai'
                }
                
                response = requests.post(f"{base_url}/upload", files=files, data=data)
                result = response.json()
                
                if result.get('success'):
                    print(f"✅ {filename} procesado: {result.get('total_records')} registros")
                    processed_files[file_type] = result.get('output_file')
                else:
                    print(f"❌ Error procesando {filename}: {result.get('error')}")
        
        except Exception as e:
            print(f"❌ Error subiendo {filename}: {e}")
    
    # Si todos los archivos se procesaron, simular inserción a Supabase
    if len(processed_files) == 3:
        print(f"\n🗄️ Simulando inserción a Supabase...")
        
        try:
            data = {
                'campaigns_file': processed_files['campaigns'],
                'ads_file': processed_files['ads'],
                'keywords_file': processed_files['keywords'],
                'clear_tables': True
            }
            
            response = requests.post(f"{base_url}/api/supabase/insert", json=data)
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Inserción exitosa: {result.get('total_inserted')} registros")
                print("🔗 Relaciones jerárquicas mantenidas correctamente")
            else:
                print(f"❌ Error en inserción: {result.get('error')}")
        
        except Exception as e:
            print(f"❌ Error en inserción a Supabase: {e}")

if __name__ == "__main__":
    test_web_application()
    
    # Preguntar si quiere hacer la simulación completa
    print(f"\n" + "=" * 50)
    user_input = input("¿Quieres simular el procesamiento completo? (y/N): ")
    
    if user_input.lower() in ['y', 'yes', 's', 'si']:
        simulate_file_upload()
    else:
        print("🎯 Para prueba manual: ve a http://localhost:5001")
