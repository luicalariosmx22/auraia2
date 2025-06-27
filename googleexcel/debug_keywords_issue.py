#!/usr/bin/env python3
"""
Debug de archivos de keywords para identificar el problema
"""
import os
from supabase_client import SupabaseGoogleAdsClient

def debug_keywords_files():
    """Debuggear archivos de keywords disponibles"""
    print("🔍 DEBUGGING ARCHIVOS DE KEYWORDS")
    print("=" * 50)
    
    # Buscar todos los archivos SQL de keywords
    keyword_files = []
    for file in os.listdir('.'):
        if file.endswith('.sql') and ('keyword' in file.lower() or 'palabra' in file.lower()):
            keyword_files.append(file)
    
    print(f"📄 Archivos SQL de keywords encontrados: {len(keyword_files)}")
    for file in keyword_files:
        print(f"   - {file}")
    
    # También buscar el archivo demo
    if 'demo_keywords.sql' in keyword_files:
        print(f"\n📋 Contenido de demo_keywords.sql:")
        client = SupabaseGoogleAdsClient()
        try:
            demo_data = client._parse_sql_file('demo_keywords.sql')
            print(f"   Registros parseados: {len(demo_data)}")
            
            if demo_data:
                print(f"   Primer registro:")
                first = demo_data[0]
                print(f"     palabra_clave: {first.get('palabra_clave', 'N/A')}")
                print(f"     campaña: {first.get('campaña', 'N/A')}")
                print(f"     tipo_concordancia: {first.get('tipo_concordancia', 'N/A')}")
                print(f"     estado: {first.get('estado', 'N/A')}")
                
                # Mostrar las primeras 3 palabras clave
                print(f"\n   Primeras 3 palabras clave:")
                for i, record in enumerate(demo_data[:3]):
                    kw = record.get('palabra_clave', 'N/A')
                    estado = record.get('estado', 'N/A')
                    print(f"     {i+1}. '{kw}' ({estado})")
                    
        except Exception as e:
            print(f"   ❌ Error parseando: {e}")

def check_current_supabase_keywords():
    """Verificar qué keywords están actualmente en Supabase"""
    print(f"\n🔍 KEYWORDS ACTUALES EN SUPABASE")
    print("=" * 50)
    
    try:
        client = SupabaseGoogleAdsClient()
        result = client.supabase.table('google_ads_palabras_clave').select('*').limit(20).execute()
        
        if result.data:
            print(f"📊 Total de registros encontrados: {len(result.data)}")
            
            print(f"\n📋 Primeros 10 registros:")
            for i, record in enumerate(result.data[:10]):
                kw = record.get('palabra_clave', 'NULL')
                estado = record.get('estado', 'NULL')
                campaña = record.get('campaña', 'NULL')
                print(f"   {i+1}. '{kw}' | Estado: {estado} | Campaña: {campaña}")
                
            # Verificar si hay "Habilitado" como palabra clave
            habilitado_count = len([r for r in result.data if r.get('palabra_clave') == 'Habilitado'])
            if habilitado_count > 0:
                print(f"\n⚠️ PROBLEMA DETECTADO: {habilitado_count} registros con 'Habilitado' como palabra clave")
                
            # Verificar estados únicos
            estados = set(r.get('estado') for r in result.data)
            print(f"\n📊 Estados únicos encontrados: {estados}")
            
            # Verificar palabras clave únicas
            palabras_unicas = set(r.get('palabra_clave') for r in result.data)
            print(f"📊 Palabras clave únicas: {len(palabras_unicas)}")
            
        else:
            print("📊 No hay registros en la tabla de palabras clave")
            
    except Exception as e:
        print(f"❌ Error consultando Supabase: {e}")

def debug_uploads_folder():
    """Verificar qué archivos hay en la carpeta uploads"""
    print(f"\n📁 ARCHIVOS EN CARPETA UPLOADS")
    print("=" * 50)
    
    uploads_path = 'uploads'
    if os.path.exists(uploads_path):
        files = os.listdir(uploads_path)
        excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]
        
        print(f"📊 Archivos Excel en uploads: {len(excel_files)}")
        for file in excel_files:
            file_path = os.path.join(uploads_path, file)
            stat = os.stat(file_path)
            size_mb = stat.st_size / (1024 * 1024)
            print(f"   - {file} ({size_mb:.2f} MB)")
            
        # Buscar archivos SQL también
        sql_files = [f for f in files if f.endswith('.sql')]
        print(f"📊 Archivos SQL en uploads: {len(sql_files)}")
        for file in sql_files:
            print(f"   - {file}")
    else:
        print("❌ Carpeta uploads no existe")

if __name__ == "__main__":
    debug_keywords_files()
    check_current_supabase_keywords()
    debug_uploads_folder()
    
    print("\n" + "=" * 50)
    print("💡 POSIBLES CAUSAS DEL PROBLEMA:")
    print("1. Se están usando archivos demo antiguos en lugar de los archivos subidos")
    print("2. La limpieza de tablas no está funcionando correctamente")
    print("3. Hay mapeo incorrecto en el generador de keywords")
    print("4. Los archivos se están procesando en orden incorrecto")
    print("\n🔧 ACCIONES RECOMENDADAS:")
    print("1. Verificar qué archivos se están procesando exactamente")
    print("2. Limpiar manualmente las tablas de Supabase")
    print("3. Generar nuevos archivos SQL con los datos correctos")
    print("4. Verificar el generador de keywords")
