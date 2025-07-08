#!/usr/bin/env python3
"""
Debug más profundo del generador IA - verificar configuración exacta
"""
from google_ads_sql_generator import GoogleAdsExcelAnalyzer

def deep_debug_ai_generator():
    """Debug profundo del generador IA"""
    print("🔬 DEBUG PROFUNDO DEL GENERADOR IA")
    print("=" * 50)
    
    analyzer = GoogleAdsExcelAnalyzer()
    
    # Verificar configuración inicial
    print(f"📊 Configuración inicial:")
    print(f"   table_type: {analyzer.table_type}")
    print(f"   target_columns (primeras 10): {analyzer.target_columns[:10]}")
    print(f"   target_columns total: {len(analyzer.target_columns)}")
    
    # Configurar para campañas
    print(f"\n🎯 Configurando para 'campaigns'...")
    analyzer.set_table_type('campaigns')
    
    print(f"   table_type después: {analyzer.table_type}")
    print(f"   target_columns total después: {len(analyzer.target_columns)}")
    
    # Verificar si las columnas problemáticas están ahora
    problematic_cols = [
        'absolute_top_impression_share', 
        'search_absolute_top_impression_share', 
        'search_impression_share',
        'costo_por_conversion'  # Esta también está causando problemas
    ]
    
    print(f"\n🔍 Verificando columnas problemáticas:")
    for col in problematic_cols:
        if col in analyzer.target_columns:
            index = analyzer.target_columns.index(col)
            print(f"   ✅ {col}: PRESENTE (índice {index})")
        else:
            print(f"   ❌ {col}: NO PRESENTE")
    
    # Verificar qué tipo de columnas está usando
    print(f"\n📋 Verificando qué lista de columnas se está usando:")
    print(f"   analyzer.target_columns es analyzer.anuncios_columns: {analyzer.target_columns is analyzer.anuncios_columns}")
    print(f"   analyzer.target_columns es analyzer.campaigns_columns: {analyzer.target_columns is analyzer.campaigns_columns}")
    print(f"   analyzer.target_columns es analyzer.keywords_columns: {analyzer.target_columns is analyzer.keywords_columns}")
    
    # Verificar configuración de set_table_type
    print(f"\n🔄 Verificando método set_table_type:")
    print(f"   Llamando analyzer.set_table_type('campañas')...")
    analyzer.set_table_type('campañas')
    print(f"   table_type: {analyzer.table_type}")
    print(f"   target_columns total: {len(analyzer.target_columns)}")
    print(f"   Es campaigns_columns: {analyzer.target_columns is analyzer.campaigns_columns}")
    
    # Verificar campaigns_columns directamente
    print(f"\n📊 Verificando campaigns_columns directamente:")
    print(f"   campaigns_columns total: {len(analyzer.campaigns_columns)}")
    
    for col in problematic_cols:
        if col in analyzer.campaigns_columns:
            index = analyzer.campaigns_columns.index(col)
            print(f"   ✅ {col}: PRESENTE en campaigns_columns (índice {index})")
        else:
            print(f"   ❌ {col}: NO PRESENTE en campaigns_columns")
    
    # Buscar columnas similares
    print(f"\n🔍 Buscando columnas similares en campaigns_columns:")
    impression_cols = [col for col in analyzer.campaigns_columns if 'impression' in col.lower()]
    share_cols = [col for col in analyzer.campaigns_columns if 'share' in col.lower()]
    conversion_cols = [col for col in analyzer.campaigns_columns if 'conversion' in col.lower()]
    
    print(f"   Columnas con 'impression': {impression_cols}")
    print(f"   Columnas con 'share': {share_cols}")
    print(f"   Columnas con 'conversion': {conversion_cols}")

if __name__ == "__main__":
    deep_debug_ai_generator()
    
    print("\n" + "=" * 50)
    print("💡 PRÓXIMOS PASOS:")
    print("1. Si las columnas están presentes, el problema puede ser en el mapeo de OpenAI")
    print("2. Si las columnas no están, hay que agregarlas a campaigns_columns")
    print("3. Si el table_type no se configura bien, hay que revisar set_table_type")
