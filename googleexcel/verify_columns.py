# Verificación de columnas - Tabla Supabase vs Scripts
# Esta es la estructura exacta de tu tabla:

SUPABASE_COLUMNS = [
    'estado_anuncio',
    'url_final', 
    'titulo_1', 'pos_titulo_1',
    'titulo_2', 'pos_titulo_2',
    'titulo_3', 'pos_titulo_3',
    'titulo_4', 'pos_titulo_4',
    'titulo_5', 'pos_titulo_5',
    'titulo_6', 'pos_titulo_6',
    'titulo_7', 'pos_titulo_7',
    'titulo_8', 'pos_titulo_8',
    'titulo_9', 'pos_titulo_9',
    'titulo_10', 'pos_titulo_10',
    'titulo_11', 'pos_titulo_11',
    'titulo_12', 'pos_titulo_12',
    'titulo_13', 'pos_titulo_13',
    'titulo_14', 'pos_titulo_14',
    'titulo_15', 'pos_titulo_15',
    'descripcion_1', 'pos_desc_1',
    'descripcion_2', 'pos_desc_2',
    'descripcion_3', 'pos_desc_3',
    'descripcion_4', 'pos_desc_4',
    'ruta_1', 'ruta_2',
    'url_final_movil',
    'plantilla_seguimiento',
    'sufijo_url_final',
    'param_personalizado',
    'campaña',
    'grupo_anuncios',
    'estado',
    'motivos_estado',
    'calidad_anuncio',
    'mejoras_efectividad',
    'tipo_anuncio',
    'clics',
    'impresiones',
    'ctr',
    'codigo_moneda',
    'cpc_promedio',
    'costo',
    'porcentaje_conversion',
    'conversiones',
    'costo_por_conversion'
]

print("🔍 VERIFICACIÓN DE COLUMNAS")
print("=" * 50)
print(f"Total columnas en Supabase: {len(SUPABASE_COLUMNS)}")

# Importar y verificar los scripts
try:
    from google_ads_sql_generator import GoogleAdsExcelAnalyzer
    from simple_excel_to_sql import SimpleExcelToSQL
    
    analyzer = GoogleAdsExcelAnalyzer()
    converter = SimpleExcelToSQL()
    
    print(f"Columnas en script IA: {len(analyzer.target_columns)}")
    print(f"Columnas en script simple: {len(converter.target_columns)}")
    
    # Verificar si coinciden
    ai_match = analyzer.target_columns == SUPABASE_COLUMNS
    simple_match = converter.target_columns == SUPABASE_COLUMNS
    
    print(f"\n✅ Script IA coincide: {ai_match}")
    print(f"✅ Script simple coincide: {simple_match}")
    
    if not ai_match:
        print("\n❌ Diferencias en script IA:")
        for i, (supabase, script) in enumerate(zip(SUPABASE_COLUMNS, analyzer.target_columns)):
            if supabase != script:
                print(f"  Posición {i}: '{supabase}' vs '{script}'")
    
    if not simple_match:
        print("\n❌ Diferencias en script simple:")
        for i, (supabase, script) in enumerate(zip(SUPABASE_COLUMNS, converter.target_columns)):
            if supabase != script:
                print(f"  Posición {i}: '{supabase}' vs '{script}'")
    
    if ai_match and simple_match:
        print("\n🎉 ¡PERFECTO! Todas las columnas coinciden con tu tabla de Supabase")
        
except Exception as e:
    print(f"❌ Error verificando: {e}")
