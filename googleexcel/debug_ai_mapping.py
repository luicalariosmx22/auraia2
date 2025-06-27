#!/usr/bin/env python3
"""
Debug del generador IA para ver exactamente qué está pasando con el mapeo
"""
import pandas as pd
from google_ads_sql_generator import GoogleAdsExcelAnalyzer

def debug_ai_mapping():
    """Debuggear el proceso de mapeo del generador IA"""
    print("🔍 DEBUGGING GENERADOR IA - MAPEO DE COLUMNAS")
    print("=" * 60)
    
    # Crear el mismo DataFrame que en el test anterior
    campaigns_data = {
        'Campaign': ['Test Campaign 001'],
        'Campaign type': ['Search'],
        'Campaign state': ['Enabled'],
        'Budget': [1000.0],
        'Bidding strategy': ['Target CPA'],
        'Target CPA': [50.0],
        'Impressions': [15000],
        'Clicks': [450],
        'CTR': [3.0],
        'Cost': [900.0],
        'Conversions': [18],
        'Cost/conv.': [50.0],
        'Conv. rate': [4.0],
        # Las columnas problemáticas
        'absolute_top_impression_share': [0.75],
        'search_absolute_top_impression_share': [0.80],
        'impression_share': [0.85],
        'search_impression_share': [0.88]
    }
    
    df = pd.DataFrame(campaigns_data)
    
    print(f"📊 DataFrame original:")
    print(f"   Filas: {len(df)}")
    print(f"   Columnas: {len(df.columns)}")
    print(f"   Columnas: {list(df.columns)}")
    
    # Crear generador y configurar para campañas
    analyzer = GoogleAdsExcelAnalyzer()
    analyzer.set_table_type('campaigns')
    
    print(f"\n🎯 Columnas objetivo del generador IA para campañas:")
    target_cols = analyzer.target_columns
    print(f"   Total: {len(target_cols)}")
    
    # Verificar si las columnas problemáticas están en target_columns
    problematic_cols = ['absolute_top_impression_share', 'search_absolute_top_impression_share', 'impression_share', 'search_impression_share']
    
    print(f"\n🔍 Verificando columnas problemáticas en target_columns:")
    for col in problematic_cols:
        if col in target_cols:
            print(f"   ✅ {col}: PRESENTE en target_columns")
        else:
            print(f"   ❌ {col}: NO está en target_columns")
    
    # Simular el filtrado que hace el generador
    print(f"\n🔄 Simulando filtrado para OpenAI...")
    
    # Código copiado del generador (líneas 194-204)
    if len(df.columns) > 50:
        print("   📊 Aplicando filtrado (>50 columnas)")
        essential_cols = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['campaign', 'campaña', 'cost', 'costo', 'click', 
                                      'clic', 'impression', 'impresión', 'conversion', 
                                      'conversión', 'budget', 'presupuesto', 'status', 
                                      'estado', 'type', 'tipo'])][:20]
    else:
        print("   📊 NO se aplica filtrado (<50 columnas)")
        essential_cols = list(df.columns)
    
    print(f"   Columnas después del filtrado: {len(essential_cols)}")
    print(f"   Columnas: {essential_cols}")
    
    # Verificar si las columnas problemáticas sobreviven el filtrado
    print(f"\n🔍 Verificando supervivencia de columnas problemáticas:")
    for col in problematic_cols:
        if col in essential_cols:
            print(f"   ✅ {col}: SOBREVIVE al filtrado")
        else:
            print(f"   ❌ {col}: ELIMINADA por el filtrado")
            
            # Verificar qué keyword debería detectarla
            keywords = ['campaign', 'campaña', 'cost', 'costo', 'click', 'clic', 'impression', 'impresión', 'conversion', 'conversión', 'budget', 'presupuesto', 'status', 'estado', 'type', 'tipo']
            matching_keywords = [kw for kw in keywords if kw in col.lower()]
            if matching_keywords:
                print(f"      🔍 Debería detectarse por: {matching_keywords}")
            else:
                print(f"      ⚠️ No coincide con ninguna keyword de filtrado")
    
    # Intentar el análisis real para ver qué mapea OpenAI
    print(f"\n🤖 Intentando análisis real con OpenAI...")
    try:
        analysis = analyzer.analyze_excel_structure(df)
        
        print(f"✅ Análisis exitoso")
        print(f"📋 Mapeos encontrados: {len(analysis.get('column_mapping', {}))}")
        
        column_mapping = analysis.get('column_mapping', {})
        
        print(f"\n🔍 Verificando mapeos de columnas problemáticas:")
        for col in problematic_cols:
            if col in column_mapping:
                mapped_to = column_mapping[col]
                print(f"   ✅ {col} -> {mapped_to}")
            else:
                print(f"   ❌ {col}: NO MAPEADA por OpenAI")
                
                # Buscar mapeos similares
                similar_mappings = {k: v for k, v in column_mapping.items() if 'impression' in k.lower() or 'share' in k.lower()}
                if similar_mappings:
                    print(f"      🔍 Mapeos similares encontrados: {similar_mappings}")
        
    except Exception as e:
        print(f"❌ Error en análisis de OpenAI: {e}")

if __name__ == "__main__":
    debug_ai_mapping()
    
    print("\n" + "=" * 60)
    print("💡 CONCLUSIONES:")
    print("1. Verificar si las columnas están en target_columns del generador")
    print("2. Verificar si sobreviven al filtrado de columnas esenciales")
    print("3. Verificar si OpenAI las mapea correctamente")
    print("4. Posible solución: Agregar keywords al filtrado o incluir más columnas")
