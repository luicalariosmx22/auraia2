#!/usr/bin/env python3
"""
Test para verificar si la columna absolute_top_impression_share existe en Supabase
"""
from supabase_client import SupabaseGoogleAdsClient
import sys

def test_column_exists():
    """Verifica si la columna existe haciendo una consulta simple"""
    client = SupabaseGoogleAdsClient()
    
    try:
        # Intentar hacer una consulta que incluya la columna problemática
        result = client.supabase.table('google_ads_campañas').select('absolute_top_impression_share').limit(1).execute()
        print("✅ La columna 'absolute_top_impression_share' existe en Supabase")
        print(f"Resultado: {result}")
        return True
    except Exception as e:
        print(f"❌ Error al consultar la columna 'absolute_top_impression_share': {e}")
        return False

def test_insert_with_problematic_column():
    """Prueba insertar un registro con la columna problemática"""
    client = SupabaseGoogleAdsClient()
    
    test_data = {
        'campaña': 'Test Campaign - Column Check',
        'absolute_top_impression_share': 0.5234,
        'estado': 'ACTIVE',
        'tipo_campaña': 'SEARCH'
    }
    
    try:
        result = client.supabase.table('google_ads_campañas').insert(test_data).execute()
        print("✅ Inserción exitosa con absolute_top_impression_share")
        
        # Limpiar el registro de prueba
        if result.data:
            record_id = result.data[0]['id']
            client.supabase.table('google_ads_campañas').delete().eq('id', record_id).execute()
            print("🧹 Registro de prueba limpiado")
        
        return True
    except Exception as e:
        print(f"❌ Error al insertar con absolute_top_impression_share: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando columna 'absolute_top_impression_share' en Supabase...\n")
    
    column_exists = test_column_exists()
    print()
    
    if column_exists:
        insert_works = test_insert_with_problematic_column()
        print()
        
        if insert_works:
            print("✅ TODO FUNCIONA: La columna existe y se puede usar para insertar")
        else:
            print("⚠️ La columna existe pero hay problemas de inserción")
    else:
        print("❌ PROBLEMA: La columna no existe, hay que ejecutar el script SQL")
        print("👉 Ejecuta manualmente en Supabase: fix_missing_ai_columns.sql")
        sys.exit(1)
