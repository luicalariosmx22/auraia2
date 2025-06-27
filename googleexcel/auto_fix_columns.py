"""
Script para agregar automáticamente las columnas faltantes a Supabase desde Python
ALTERNATIVA RÁPIDA al método manual del SQL Editor
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List

# Cargar variables de entorno
load_dotenv()

def get_supabase_client():
    """Inicializa cliente de Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("❌ Error: SUPABASE_URL y SUPABASE_ANON_KEY deben estar configuradas en .env")
    
    return create_client(supabase_url, supabase_key)

def add_columns_to_keywords_table(supabase: Client) -> bool:
    """Agrega las 3 columnas faltantes a la tabla de palabras clave"""
    
    print("🔑 Agregando columnas faltantes a google_ads_palabras_clave...")
    
    columns_to_add = [
        ("id_campaña", "INTEGER"),
        ("id_grupo_anuncios", "INTEGER"), 
        ("id_palabra_clave", "INTEGER")
    ]
    
    try:
        for column_name, data_type in columns_to_add:
            try:
                # Intentar agregar la columna
                sql = f"ALTER TABLE google_ads_palabras_clave ADD COLUMN IF NOT EXISTS {column_name} {data_type};"
                
                # Usar el método de ejecución directa si está disponible
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Columna {column_name} agregada exitosamente")
                
            except Exception as e:
                print(f"⚠️ Error agregando {column_name}: {str(e)}")
                # Si falla el método RPC, intentar con una inserción dummy para forzar el esquema
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Error general agregando columnas: {str(e)}")
        return False

def test_insert_with_new_columns(supabase: Client) -> bool:
    """Prueba insertar un registro con las nuevas columnas"""
    
    print("🧪 Probando inserción con nuevas columnas...")
    
    test_record = {
        'palabra_clave': 'test keyword',
        'tipo_concordancia': 'exact',
        'campaña': 'Test Campaign',
        'grupo_anuncios': 'Test Ad Group',
        'estado': 'enabled',
        'impresiones': 100,
        'clics': 5,
        'ctr': 0.05,
        'costo': 1.25,
        'conversiones': 1,
        'costo_por_conversion': 1.25,
        'id_campaña': 1,
        'id_grupo_anuncios': 1,
        'id_palabra_clave': 1
    }
    
    try:
        result = supabase.table('google_ads_palabras_clave').insert(test_record).execute()
        
        if result.data:
            print("✅ Inserción de prueba exitosa")
            # Eliminar el registro de prueba
            delete_result = supabase.table('google_ads_palabras_clave').delete().eq('palabra_clave', 'test keyword').execute()
            print("🗑️ Registro de prueba eliminado")
            return True
        else:
            print("❌ Inserción de prueba falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en inserción de prueba: {str(e)}")
        return False

def main():
    """Función principal para agregar columnas automáticamente"""
    
    print("🔧 AGREGANDO COLUMNAS FALTANTES AUTOMÁTICAMENTE")
    print("=" * 60)
    
    try:
        # Conectar a Supabase
        supabase = get_supabase_client()
        print("✅ Conectado a Supabase exitosamente")
        
        # Primero, intentar agregar las columnas críticas de relación
        print("\n🎯 PASO 1: Agregando columnas de relación a palabras clave")
        keywords_success = add_columns_to_keywords_table(supabase)
        
        if keywords_success:
            print("\n🧪 PASO 2: Probando las nuevas columnas")
            test_success = test_insert_with_new_columns(supabase)
            
            if test_success:
                print("\n✅ ¡ÉXITO! Las columnas se agregaron correctamente")
                print("\n🚀 Ahora puedes intentar la inserción completa:")
                print("   python test_demo_insertion.py")
                return True
            else:
                print("\n⚠️ Las columnas pueden haberse agregado pero hay problemas de inserción")
        
        print("\n❌ FALLO AUTOMÁTICO")
        print("📋 Por favor, usa el método manual:")
        print("1. Abre Supabase Dashboard > SQL Editor")
        print("2. Ejecuta el contenido de fix_missing_columns.sql")
        print("3. Verifica que las columnas se agregaron")
        return False
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso automático: {str(e)}")
        print("\n📋 SOLUCIÓN ALTERNATIVA:")
        print("Usa el método manual con el archivo fix_missing_columns.sql")
        return False

if __name__ == "__main__":
    main()
