#!/usr/bin/env python3
"""
Crear un archivo Excel con la columna absolute_top_impression_share para probar el flujo completo
"""
import pandas as pd
import os

def create_excel_with_absolute_top():
    """Crear un archivo Excel que incluya la columna problemática"""
    print("📊 CREANDO ARCHIVO EXCEL CON absolute_top_impression_share")
    print("=" * 60)
    
    # Datos de campañas que incluyan la columna problemática
    campaigns_data = {
        'Campaign': [
            'Test Campaign 001',
            'Test Campaign 002', 
            'Test Campaign 003'
        ],
        'Campaign type': ['Search', 'Display', 'Shopping'],
        'Campaign state': ['Enabled', 'Enabled', 'Paused'],
        'Budget': [1000.0, 1500.0, 800.0],
        'Bidding strategy': ['Target CPA', 'Target ROAS', 'Manual CPC'],
        'Target CPA': [50.0, None, None],
        'Target ROAS': [None, 400.0, None],
        'Impressions': [15000, 8000, 5000],
        'Clicks': [450, 200, 100],
        'CTR': [3.0, 2.5, 2.0],
        'Cost': [900.0, 600.0, 200.0],
        'Conversions': [18, 12, 4],
        'Cost/conv.': [50.0, 50.0, 50.0],
        'Conv. rate': [4.0, 6.0, 4.0],
        # ⭐ AQUÍ ESTÁ LA COLUMNA PROBLEMÁTICA
        'absolute_top_impression_share': [0.75, 0.68, 0.82],
        # Y algunas más para hacer el test más robusto
        'search_absolute_top_impression_share': [0.80, 0.72, 0.85],
        'impression_share': [0.85, 0.78, 0.90],
        'search_impression_share': [0.88, 0.82, 0.92]
    }
    
    df = pd.DataFrame(campaigns_data)
    filename = 'test_campaigns_with_absolute_top.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Archivo creado: {filename}")
    print(f"📊 Registros: {len(df)}")
    print(f"📋 Columnas: {len(df.columns)}")
    print("🎯 Columnas especiales incluidas:")
    print("   - absolute_top_impression_share")
    print("   - search_absolute_top_impression_share")
    print("   - impression_share")
    print("   - search_impression_share")
    
    return filename

def test_full_workflow_with_ai_generator(excel_file):
    """Probar el flujo completo con el generador IA"""
    print(f"\n🤖 PROBANDO FLUJO COMPLETO CON GENERADOR IA")
    print("=" * 60)
    
    try:
        from google_ads_sql_generator import GoogleAdsExcelAnalyzer
        from supabase_client import SupabaseGoogleAdsClient
        
        # Paso 1: Procesar con IA
        print("🚀 Procesando con generador IA...")
        ai_generator = GoogleAdsExcelAnalyzer()
        
        result = ai_generator.process_excel_to_sql(excel_file, 'test_ai_with_absolute.sql', table_type='campaigns')
        
        if not result['success']:
            print(f"❌ Error procesando con IA: {result.get('error')}")
            return False
            
        print("✅ Procesamiento IA exitoso")
        
        # Paso 2: Parsear y verificar datos
        print("\n📋 Verificando datos generados...")
        client = SupabaseGoogleAdsClient()
        parsed_data = client._parse_sql_file('test_ai_with_absolute.sql')
        
        print(f"📊 Registros parseados: {len(parsed_data)}")
        
        if parsed_data:
            first_record = parsed_data[0]
            print(f"🔍 Columnas en registro: {len(first_record.keys())}")
            
            # Verificar columnas específicas
            target_columns = [
                'absolute_top_impression_share',
                'search_absolute_top_impression_share',
                'impression_share',
                'search_impression_share'
            ]
            
            for col in target_columns:
                if col in first_record:
                    value = first_record[col]
                    print(f"   ✅ {col}: {value}")
                else:
                    print(f"   ❌ {col}: NO PRESENTE")
        
        # Paso 3: Insertar en Supabase
        print("\n📤 Insertando en Supabase...")
        
        # Limpiar tabla primero
        client.clear_all_tables()
        
        # Insertar datos
        insert_result = client.insert_campaigns(parsed_data)
        
        if insert_result['success']:
            print("✅ INSERCIÓN EXITOSA EN SUPABASE")
            print(f"📊 Registros insertados: {insert_result.get('inserted_count', 0)}")
            
            # Verificar datos insertados
            verify_result = client.supabase.table('google_ads_campañas').select('campaña, absolute_top_impression_share, search_absolute_top_impression_share').execute()
            
            if verify_result.data:
                print("\n🔍 DATOS VERIFICADOS EN SUPABASE:")
                for record in verify_result.data:
                    print(f"   📈 {record['campaña']}: absolute_top={record['absolute_top_impression_share']}, search_abs={record['search_absolute_top_impression_share']}")
            
            return True
            
        else:
            print(f"❌ ERROR EN INSERCIÓN: {insert_result.get('error')}")
            
            # Analizar el error
            error_msg = str(insert_result.get('error', ''))
            if 'absolute_top_impression_share' in error_msg:
                print("🎯 El error SÍ está relacionado con absolute_top_impression_share")
                if 'PGRST204' in error_msg:
                    print("💡 Error PGRST204: Problema de schema cache en Supabase")
            else:
                print("🤔 El error no está relacionado con absolute_top_impression_share")
                
            return False
            
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Crear archivo con columna problemática
    excel_file = create_excel_with_absolute_top()
    
    # Probar flujo completo
    success = test_full_workflow_with_ai_generator(excel_file)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULTADO: TODO FUNCIONA CORRECTAMENTE")
        print("✅ El error de 'absolute_top_impression_share' está SOLUCIONADO")
    else:
        print("❌ RESULTADO: AÚN HAY PROBLEMAS")
        print("🔧 Puede necesitar más investigación")
    
    # Limpiar archivo temporal
    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"🧹 Archivo temporal {excel_file} eliminado")
