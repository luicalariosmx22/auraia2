#!/usr/bin/env python3
"""
Verificar el esquema actual de Supabase para la tabla de campañas
"""
from supabase_client import SupabaseGoogleAdsClient

def check_supabase_schema():
    """Verificar qué columnas están disponibles en Supabase"""
    print("🔍 VERIFICANDO ESQUEMA DE SUPABASE")
    print("=" * 50)
    
    try:
        client = SupabaseGoogleAdsClient()
        print("✅ Cliente conectado")
        
        # Intentar obtener la estructura de la tabla
        try:
            # Hacer una consulta que nos muestre la estructura
            result = client.supabase.table('google_ads_campañas').select('*').limit(1).execute()
            
            if result.data:
                # Si hay datos, mostrar las columnas
                sample_record = result.data[0]
                columns = list(sample_record.keys())
                print(f"📊 Columnas disponibles en Supabase: {len(columns)}")
                
                # Verificar si la columna problemática existe
                if 'absolute_top_impression_share' in columns:
                    print("✅ 'absolute_top_impression_share' EXISTE en Supabase")
                else:
                    print("❌ 'absolute_top_impression_share' NO EXISTE en Supabase")
                
                # Mostrar algunas columnas que contengan "absolute" o "impression"
                related_columns = [col for col in columns if 'absolute' in col.lower() or 'impression' in col.lower()]
                if related_columns:
                    print(f"🔍 Columnas relacionadas con 'absolute/impression': {related_columns}")
                else:
                    print("⚠️ No se encontraron columnas relacionadas con 'absolute/impression'")
                    
            else:
                print("⚠️ No hay datos en la tabla para verificar esquema")
                
                # Intentar insertar un registro con la columna para probar
                test_record = {
                    'campaña': 'TEST_SCHEMA_CHECK',
                    'absolute_top_impression_share': 0.1234
                }
                
                try:
                    insert_result = client.supabase.table('google_ads_campañas').insert(test_record).execute()
                    print("✅ La columna 'absolute_top_impression_share' funciona en inserción")
                    
                    # Limpiar
                    if insert_result.data:
                        record_id = insert_result.data[0]['id']
                        client.supabase.table('google_ads_campañas').delete().eq('id', record_id).execute()
                        print("🧹 Registro de prueba eliminado")
                        
                except Exception as insert_error:
                    print(f"❌ Error insertando con 'absolute_top_impression_share': {insert_error}")
                    
                    # Analizar el error
                    error_str = str(insert_error)
                    if 'absolute_top_impression_share' in error_str:
                        if 'does not exist' in error_str or 'PGRST204' in error_str:
                            print("🎯 CONFIRMADO: La columna NO existe en Supabase")
                        else:
                            print("🤔 La columna existe pero hay otro problema")
                    
        except Exception as schema_error:
            print(f"❌ Error verificando esquema: {schema_error}")
            
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")

def test_problematic_column_insertion():
    """Probar inserción directa con la columna problemática"""
    print("\n🧪 PROBANDO INSERCIÓN DIRECTA")
    print("=" * 50)
    
    try:
        client = SupabaseGoogleAdsClient()
        
        test_records = [
            {
                'campaña': 'TEST_WITH_ABSOLUTE_TOP',
                'estado': 'ACTIVE',
                'tipo_campaña': 'SEARCH',
                'absolute_top_impression_share': 0.5678,
                'impresiones': 1000,
                'clics': 50,
                'costo': 100.0
            }
        ]
        
        print("📤 Intentando insertar registro con 'absolute_top_impression_share'...")
        
        result = client.insert_campaigns(test_records)
        
        if result['success']:
            print("✅ INSERCIÓN EXITOSA - La columna funciona correctamente")
            print(f"📊 Registros insertados: {result.get('inserted_count', 0)}")
            
            # Limpiar
            client.clear_all_tables()
            print("🧹 Tabla limpiada")
            
        else:
            print(f"❌ ERROR EN INSERCIÓN: {result.get('error', 'Error desconocido')}")
            
            error_msg = str(result.get('error', ''))
            if 'absolute_top_impression_share' in error_msg:
                if 'PGRST204' in error_msg or 'schema cache' in error_msg:
                    print("🎯 PROBLEMA IDENTIFICADO: La columna no está en el schema cache de Supabase")
                    print("💡 SOLUCIÓN: Ejecutar el script SQL para agregar la columna")
                    print("   👉 fix_missing_ai_columns.sql")
                
    except Exception as e:
        print(f"❌ Error en prueba de inserción: {e}")

if __name__ == "__main__":
    check_supabase_schema()
    test_problematic_column_insertion()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("- Si la columna existe ✅: El problema está en otro lado")
    print("- Si la columna NO existe ❌: Hay que ejecutar fix_missing_ai_columns.sql")
    print("- Si hay error PGRST204: La columna falta en el schema cache de Supabase")
