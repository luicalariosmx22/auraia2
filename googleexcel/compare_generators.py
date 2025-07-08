#!/usr/bin/env python3
"""
Test para comparar qué datos envían los diferentes generadores
"""
from campaigns_generator import CampaignsExcelToSQL
from google_ads_sql_generator import GoogleAdsExcelAnalyzer
from supabase_client import SupabaseGoogleAdsClient
import pandas as pd
import os

def create_test_excel():
    """Crear un archivo de prueba pequeño"""
    test_data = {
        'Campaña': ['Test Campaign 001'],
        'Estado': ['ACTIVE'],
        'Tipo de campaña': ['SEARCH'],
        'Presupuesto': ['100.00'],
        'Impresiones': ['1000'],
        'Clics': ['50'],
        'CTR': ['5.00%'],
        'CPC promedio': ['2.00'],
        'Costo': ['100.00']
    }
    
    df = pd.DataFrame(test_data)
    filename = 'test_small_campaigns.xlsx'
    df.to_excel(filename, index=False)
    return filename

def test_campaigns_generator():
    """Probar el generador específico de campañas"""
    print("🔍 Probando generador específico de campañas...")
    
    filename = create_test_excel()
    generator = CampaignsExcelToSQL()
    
    try:
        result = generator.excel_to_sql_dict(filename)
        print(f"✅ Campañas generadas: {len(result)}")
        
        if result:
            # Mostrar las primeras claves para ver qué columnas incluye
            sample_record = result[0]
            print(f"📋 Columnas en el registro: {len(sample_record.keys())}")
            
            # Verificar si contiene la columna problemática
            if 'absolute_top_impression_share' in sample_record:
                print("✅ Contiene 'absolute_top_impression_share'")
            else:
                print("❌ NO contiene 'absolute_top_impression_share'")
                
            # Mostrar algunas columnas para debug
            print("🔍 Primeras 10 columnas:")
            for i, key in enumerate(list(sample_record.keys())[:10]):
                print(f"  {i+1}. {key}: {sample_record[key]}")
                
        return result
        
    except Exception as e:
        print(f"❌ Error en generador de campañas: {e}")
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_ai_generator():
    """Probar el generador IA"""
    print("\n🔍 Probando generador IA...")
    
    filename = create_test_excel()
    generator = GoogleAdsExcelAnalyzer()
    
    try:
        result = generator.excel_to_sql_dict(filename, 'campaigns')
        print(f"✅ Registros generados por IA: {len(result)}")
        
        if result:
            sample_record = result[0]
            print(f"📋 Columnas en el registro: {len(sample_record.keys())}")
            
            if 'absolute_top_impression_share' in sample_record:
                print("✅ Contiene 'absolute_top_impression_share'")
                print(f"   Valor: {sample_record['absolute_top_impression_share']}")
            else:
                print("❌ NO contiene 'absolute_top_impression_share'")
                
        return result
        
    except Exception as e:
        print(f"❌ Error en generador IA: {e}")
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_supabase_insertion(data, generator_name):
    """Probar inserción en Supabase"""
    print(f"\n🔍 Probando inserción con datos del {generator_name}...")
    
    if not data:
        print("❌ No hay datos para insertar")
        return False
        
    client = SupabaseGoogleAdsClient()
    
    try:
        # Intentar insertar solo el primer registro
        test_record = data[0].copy()
        
        # Agregar un identificador único para poder limpiar después
        test_record['campaña'] = f"TEST-{generator_name}-{pd.Timestamp.now().strftime('%H%M%S')}"
        
        result = client.insert_campaigns([test_record])
        print(f"✅ Inserción exitosa con {generator_name}")
        
        # Limpiar
        client.clear_table('google_ads_campañas')
        print("🧹 Tabla limpiada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en inserción con {generator_name}: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Comparando generadores de campañas...\n")
    
    # Probar generador específico
    campaigns_data = test_campaigns_generator()
    
    # Probar generador IA  
    ai_data = test_ai_generator()
    
    # Probar inserciones
    if campaigns_data:
        test_supabase_insertion(campaigns_data, "Campaigns Generator")
        
    if ai_data:
        test_supabase_insertion(ai_data, "AI Generator")
    
    print("\n🏁 Comparación completada")
