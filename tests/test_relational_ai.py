#!/usr/bin/env python3
"""
Script de prueba para el generador de Google Ads con detección automática de relaciones jerárquicas.
"""

import pandas as pd
import os
from google_ads_sql_generator import GoogleAdsExcelAnalyzer

def create_test_data_with_relations():
    """Crea datos de prueba que incluyen relaciones jerárquicas claras"""
    
    # Datos de prueba para anuncios con relaciones jerárquicas
    ads_data = {
        'Campaign': ['SaldeJade - Search', 'SaldeJade - Search', 'SaldeJade - Display', 'SaldeJade - Display'],
        'Ad group': ['Jade Keywords', 'Jade Keywords', 'Display Audience', 'Display Audience'],
        'Headline 1': ['Compra Jade Natural', 'Jade de Calidad', 'Joyería Exclusiva', 'Jade Premium'],
        'Headline 2': ['Envío Gratis', 'Mejor Precio', 'Descuento 20%', 'Oferta Especial'],
        'Description': ['Descripción 1', 'Descripción 2', 'Descripción 3', 'Descripción 4'],
        'Final URL': ['https://salde.com/jade1', 'https://salde.com/jade2', 'https://salde.com/jade3', 'https://salde.com/jade4'],
        'Ad type': ['Responsive search ad', 'Responsive search ad', 'Responsive display ad', 'Responsive display ad'],
        'Status': ['Enabled', 'Enabled', 'Paused', 'Enabled'],
        'Impressions': [5000, 3200, 1800, 2500],
        'Clicks': [250, 160, 45, 80],
        'CTR': ['5.00%', '5.00%', '2.50%', '3.20%'],
        'Cost': [125.50, 80.20, 22.50, 40.00],
        'Conversions': [8, 5, 1, 2],
        'Cost/conv.': [15.69, 16.04, 22.50, 20.00]
    }
    
    # Datos de prueba para palabras clave con relaciones
    keywords_data = {
        'Campaign': ['SaldeJade - Search', 'SaldeJade - Search', 'SaldeJade - Search', 'SaldeJade - Search'],
        'Ad group': ['Jade Keywords', 'Jade Keywords', 'Jade Premium', 'Jade Premium'],
        'Keyword': ['jade natural', 'comprar jade', 'jade premium', 'joyería jade'],
        'Match type': ['Broad match', 'Phrase match', 'Exact match', 'Broad match'],
        'Status': ['Enabled', 'Enabled', 'Enabled', 'Paused'],
        'Final URL': ['https://salde.com/jade', 'https://salde.com/comprar', 'https://salde.com/premium', 'https://salde.com/joyeria'],
        'Impressions': [2500, 1800, 1200, 900],
        'Clicks': [125, 90, 60, 20],
        'CTR': ['5.00%', '5.00%', '5.00%', '2.22%'],
        'Cost': [62.50, 45.00, 30.00, 10.00],
        'Conversions': [4, 3, 2, 0],
        'Cost/conv.': [15.63, 15.00, 15.00, '--']
    }
    
    return ads_data, keywords_data

def test_ai_with_relations():
    """Prueba el generador con IA incluyendo detección de relaciones"""
    
    print("🧪 PRUEBA DEL GENERADOR CON IA Y RELACIONES JERÁRQUICAS")
    print("=" * 60)
    
    # Verificar API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY no configurada")
        return False
    
    # Crear datos de prueba
    ads_data, keywords_data = create_test_data_with_relations()
    
    # Test 1: Anuncios
    print("\n📺 TEST 1: ANUNCIOS CON RELACIONES")
    print("-" * 40)
    
    ads_df = pd.DataFrame(ads_data)
    test_ads_file = 'test_ads_relational.xlsx'
    ads_df.to_excel(test_ads_file, index=False)
    
    analyzer = GoogleAdsExcelAnalyzer()
    analyzer.set_table_type('anuncios')
    
    result = analyzer.process_excel_to_sql(
        excel_file=test_ads_file,
        output_file='test_ads_relational_output.sql',
        table_type='anuncios'
    )
    
    if result['success']:
        print("✅ Anuncios procesados correctamente")
        
        # Verificar que se generaron relaciones
        try:
            with open('test_ads_relational_output.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
                if 'id_campaña' in sql_content and 'id_grupo_anuncios' in sql_content:
                    print("✅ IDs relacionales detectados en el SQL")
                else:
                    print("⚠️ IDs relacionales no encontrados en el SQL")
        except Exception as e:
            print(f"❌ Error verificando SQL: {e}")
    else:
        print(f"❌ Error procesando anuncios: {result.get('error', 'Error desconocido')}")
    
    # Limpiar archivo temporal
    if os.path.exists(test_ads_file):
        os.remove(test_ads_file)
    
    # Test 2: Palabras clave
    print("\n🔑 TEST 2: PALABRAS CLAVE CON RELACIONES")
    print("-" * 40)
    
    keywords_df = pd.DataFrame(keywords_data)
    test_keywords_file = 'test_keywords_relational.xlsx'
    keywords_df.to_excel(test_keywords_file, index=False)
    
    analyzer.set_table_type('palabras_clave')
    
    result = analyzer.process_excel_to_sql(
        excel_file=test_keywords_file,
        output_file='test_keywords_relational_output.sql',
        table_type='palabras_clave'
    )
    
    if result['success']:
        print("✅ Palabras clave procesadas correctamente")
        
        # Verificar que se generaron relaciones
        try:
            with open('test_keywords_relational_output.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
                if 'id_campaña' in sql_content and 'id_grupo_anuncios' in sql_content and 'id_palabra_clave' in sql_content:
                    print("✅ IDs relacionales detectados en el SQL")
                else:
                    print("⚠️ IDs relacionales no encontrados en el SQL")
        except Exception as e:
            print(f"❌ Error verificando SQL: {e}")
    else:
        print(f"❌ Error procesando palabras clave: {result.get('error', 'Error desconocido')}")
    
    # Limpiar archivo temporal
    if os.path.exists(test_keywords_file):
        os.remove(test_keywords_file)
    
    print("\n✅ PRUEBAS COMPLETADAS")
    return True

if __name__ == "__main__":
    test_ai_with_relations()
