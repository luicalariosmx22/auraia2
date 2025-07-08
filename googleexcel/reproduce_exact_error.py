#!/usr/bin/env python3
"""
Test directo para reproducir el error usando el flujo real del backend
"""
from campaigns_generator import CampaignsExcelToSQL
from google_ads_sql_generator import GoogleAdsExcelAnalyzer
from supabase_client import SupabaseGoogleAdsClient
import os
import pandas as pd

def reproduce_actual_error():
    """Reproduce el error exacto que está ocurriendo"""
    print("🎯 REPRODUCIENDO ERROR REAL DE 'absolute_top_impression_share'")
    print("=" * 60)
    
    excel_file = "demo_campaigns.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Archivo {excel_file} no existe. Ejecuta 'python create_demo_files.py' primero")
        return
    
    try:
        client = SupabaseGoogleAdsClient()
        print("✅ Cliente Supabase inicializado")
        
        # Paso 1: Limpiar tablas (usando el método correcto)
        print("🧹 Limpiando todas las tablas...")
        clear_result = client.clear_all_tables()
        
        if clear_result['success']:
            print("✅ Tablas limpiadas exitosamente")
        else:
            print(f"⚠️ Problema limpiando tablas: {clear_result.get('message')}")
        
        # Paso 2: Generar datos usando el generador de campañas específico
        print("\n📊 Generando datos con campaigns_generator...")
        campaigns_generator = CampaignsExcelToSQL()
        
        # Generar archivo SQL
        sql_output = "error_test_campaigns.sql"
        success = campaigns_generator.process_excel_to_sql(excel_file, sql_output)
        
        if not success:
            print("❌ Error generando SQL")
            return
            
        print("✅ SQL generado exitosamente")
        
        # Paso 3: Intentar leer y procesar los datos como hace el backend
        print("\n📤 Intentando insertar datos en Supabase...")
        
        # Leer el archivo SQL generado y parsearlo
        try:
            campaigns_data = client._parse_sql_file(sql_output)
            print(f"📋 Datos parseados: {len(campaigns_data)} registros")
            
            # Mostrar las primeras columnas del primer registro para debug
            if campaigns_data:
                first_record = campaigns_data[0]
                print(f"🔍 Columnas en el primer registro: {len(first_record.keys())}")
                
                # Verificar si contiene la columna problemática
                if 'absolute_top_impression_share' in first_record:
                    print("✅ Registro contiene 'absolute_top_impression_share'")
                    print(f"   Valor: {first_record['absolute_top_impression_share']}")
                else:
                    print("❌ Registro NO contiene 'absolute_top_impression_share'")
                
                # Mostrar algunas columnas para debug
                print("🔍 Primeras 10 columnas del registro:")
                for i, (key, value) in enumerate(list(first_record.items())[:10]):
                    print(f"  {i+1}. {key}: {value}")
            
            # Ahora intentar la inserción real que debería causar el error
            print("\n🚨 INTENTANDO INSERCIÓN QUE CAUSARÁ EL ERROR...")
            insert_result = client.insert_campaigns(campaigns_data)
            
            if insert_result['success']:
                print("✅ ¡Inserción exitosa! (El error ya fue solucionado)")
                print(f"📊 Registros insertados: {insert_result.get('inserted_count', 0)}")
            else:
                print(f"❌ ERROR REPRODUCIDO: {insert_result.get('error', 'Error desconocido')}")
                
                # Analizar el error
                error_msg = str(insert_result.get('error', ''))
                if 'absolute_top_impression_share' in error_msg:
                    print("🎯 CONFIRMADO: El error es por la columna 'absolute_top_impression_share'")
                    print("\n💡 DIAGNÓSTICO:")
                    print("- El generador campaigns_generator NO incluye esta columna")
                    print("- Pero Supabase espera que esté presente")
                    print("- Solución: Agregar la columna al generador o filtrar antes de insertar")
        
        except Exception as parse_error:
            print(f"❌ Error parseando archivo SQL: {parse_error}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def compare_generators_output():
    """Compara la salida de ambos generadores para ver las diferencias"""
    print("\n🔍 COMPARANDO SALIDA DE GENERADORES")
    print("=" * 50)
    
    excel_file = "demo_campaigns.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Archivo {excel_file} no existe")
        return
    
    try:
        client = SupabaseGoogleAdsClient()
        
        # Generar con campaigns_generator
        print("📊 Generando con campaigns_generator...")
        campaigns_gen = CampaignsExcelToSQL()
        campaigns_gen.process_excel_to_sql(excel_file, "compare_campaigns.sql")
        
        campaigns_data = client._parse_sql_file("compare_campaigns.sql")
        print(f"✅ Campaigns generator: {len(campaigns_data)} registros")
        
        if campaigns_data:
            campaigns_columns = set(campaigns_data[0].keys())
            print(f"📋 Columnas: {len(campaigns_columns)}")
            
            has_absolute_top = 'absolute_top_impression_share' in campaigns_columns
            print(f"🔍 Contiene absolute_top_impression_share: {'✅ SÍ' if has_absolute_top else '❌ NO'}")
        
        # Generar con AI generator
        print("\n🤖 Generando con AI generator...")
        ai_gen = GoogleAdsExcelAnalyzer()
        ai_result = ai_gen.process_excel_to_sql(excel_file, "compare_ai.sql", table_type='campaigns')
        
        if ai_result['success']:
            ai_data = client._parse_sql_file("compare_ai.sql")
            print(f"✅ AI generator: {len(ai_data)} registros")
            
            if ai_data:
                ai_columns = set(ai_data[0].keys())
                print(f"📋 Columnas: {len(ai_columns)}")
                
                has_absolute_top_ai = 'absolute_top_impression_share' in ai_columns
                print(f"🔍 Contiene absolute_top_impression_share: {'✅ SÍ' if has_absolute_top_ai else '❌ NO'}")
                
                # Mostrar diferencias
                print(f"\n📊 DIFERENCIAS:")
                only_in_campaigns = campaigns_columns - ai_columns
                only_in_ai = ai_columns - campaigns_columns
                
                print(f"🔸 Solo en campaigns generator: {len(only_in_campaigns)}")
                if only_in_campaigns:
                    for col in list(only_in_campaigns)[:5]:  # Mostrar solo las primeras 5
                        print(f"   - {col}")
                
                print(f"🔸 Solo en AI generator: {len(only_in_ai)}")
                if only_in_ai:
                    for col in list(only_in_ai)[:5]:  # Mostrar solo las primeras 5
                        print(f"   - {col}")
                        
                # La columna problemática
                if 'absolute_top_impression_share' in only_in_ai:
                    print(f"\n🎯 'absolute_top_impression_share' está SOLO en AI generator")
                
        else:
            print(f"❌ Error con AI generator: {ai_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error comparando generadores: {e}")

if __name__ == "__main__":
    # Reproducir el error real
    reproduce_actual_error()
    
    # Comparar generadores
    compare_generators_output()
    
    print("\n" + "=" * 60)
    print("🔧 SOLUCIONES POSIBLES:")
    print("1. ✅ Agregar 'absolute_top_impression_share' al campaigns_generator.py")
    print("2. ✅ Modificar el backend para usar siempre el AI generator para campañas")
    print("3. ✅ Filtrar columnas no esperadas antes de insertar en Supabase")
    print("4. ✅ Hacer que Supabase sea más permisivo con columnas faltantes")
