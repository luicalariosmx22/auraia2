"""
Script para procesar archivos demo y probar la inserción en Supabase
"""

import os
from google_ads_sql_generator import GoogleAdsExcelAnalyzer
from campaigns_generator import CampaignsExcelToSQL  
from keywords_generator import KeywordsExcelToSQL
from supabase_client import SupabaseGoogleAdsClient

def process_and_insert_demo():
    """Procesa archivos demo y los inserta en Supabase"""
    
    print("🎯 PROCESANDO ARCHIVOS DEMO PARA SUPABASE")
    print("=" * 50)
    
    # Verificar que existen los archivos demo
    demo_files = ['demo_campaigns.xlsx', 'demo_ads.xlsx', 'demo_keywords.xlsx']
    for file in demo_files:
        if not os.path.exists(file):
            print(f"❌ Error: {file} no existe. Ejecuta create_demo_files.py primero")
            return
    
    # 1. Procesar campañas
    print("📈 Procesando campañas...")
    campaigns_gen = CampaignsExcelToSQL()
    campaigns_success = campaigns_gen.process_excel_to_sql('demo_campaigns.xlsx', 'demo_campaigns.sql')
    print(f"✅ Resultado campañas: {'success' if campaigns_success else 'error'}")
    
    # 2. Procesar anuncios
    print("📺 Procesando anuncios...")
    ads_gen = GoogleAdsExcelAnalyzer()
    ads_success = ads_gen.process_excel_to_sql('demo_ads.xlsx', 'demo_ads.sql', table_type='anuncios')
    print(f"✅ Resultado anuncios: {'success' if ads_success else 'error'}")
    
    # 3. Procesar palabras clave
    print("🔑 Procesando palabras clave...")
    keywords_gen = KeywordsExcelToSQL()
    keywords_success = keywords_gen.process_excel_to_sql('demo_keywords.xlsx', 'demo_keywords.sql')
    print(f"✅ Resultado keywords: {'success' if keywords_success else 'error'}")
    
    # 4. Verificar que se generaron los SQL
    sql_files = ['demo_campaigns.sql', 'demo_ads.sql', 'demo_keywords.sql']
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            print(f"✅ {sql_file} generado correctamente")
        else:
            print(f"❌ {sql_file} no se generó")
            return
    
    # 5. Insertar en Supabase
    print("\n🚀 INSERTANDO EN SUPABASE...")
    try:
        client = SupabaseGoogleAdsClient()
        result = client.insert_all_data(
            'demo_campaigns.sql', 
            'demo_ads.sql', 
            'demo_keywords.sql', 
            clear_tables=True
        )
        
        if result['success']:
            print(f"✅ Inserción exitosa: {result['message']}")
        else:
            print(f"❌ Error en inserción: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error durante la inserción: {str(e)}")

if __name__ == "__main__":
    process_and_insert_demo()
