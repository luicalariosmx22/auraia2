import pandas as pd
import os

def create_sample_excel():
    """Crea un archivo Excel de ejemplo para testing"""
    
    # Datos de ejemplo que simulan un reporte de Google Ads
    sample_data = {
        'Campaign': ['Campaña Verano 2024', 'Campaña Invierno 2024', 'Campaña Black Friday'],
        'Ad group': ['Grupo Productos A', 'Grupo Productos B', 'Grupo Ofertas'],
        'Headline 1': ['Compra Ahora', 'Mejor Precio', 'Oferta Limitada'],
        'Headline 2': ['Envío Gratis', 'Calidad Premium', 'Descuento 50%'],
        'Headline 3': ['Stock Limitado', 'Garantía Total', 'Solo Hoy'],
        'Description 1': ['Los mejores productos al mejor precio', 'Calidad garantizada con envío express', 'Ofertas increíbles por tiempo limitado'],
        'Description 2': ['No te pierdas esta oportunidad única', 'Satisfacción garantizada o devolvemos tu dinero', 'Aprovecha antes que se agoten'],
        'Final URL': ['https://tienda.com/producto1', 'https://tienda.com/producto2', 'https://tienda.com/ofertas'],
        'Path 1': ['productos', 'calidad', 'ofertas'],
        'Path 2': ['nuevos', 'premium', 'limitadas'],
        'Status': ['Enabled', 'Enabled', 'Paused'],
        'Ad state': ['Eligible', 'Eligible', 'Under review'],
        'Clicks': [150, 89, 234],
        'Impressions': [5420, 3210, 8901],
        'CTR': ['2.77%', '2.77%', '2.63%'],
        'Avg. CPC': ['$1.25', '$1.89', '$0.95'],
        'Cost': ['$187.50', '$168.21', '$222.30'],
        'Conversions': [12, 8, 19],
        'Conv. rate': ['8.00%', '8.99%', '8.12%'],
        'Cost / conv.': ['$15.63', '$21.03', '$11.70']
    }
    
    # Crear DataFrame
    df = pd.DataFrame(sample_data)
    
    # Guardar como Excel
    excel_file = 'sample_google_ads_report.xlsx'
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Archivo de ejemplo creado: {excel_file}")
    print(f"📊 Datos: {len(df)} filas, {len(df.columns)} columnas")
    print(f"🔍 Columnas: {list(df.columns)}")
    
    return excel_file

def test_simple_converter():
    """Prueba el convertidor simple"""
    print("\n🧪 TESTING CONVERTIDOR SIMPLE")
    print("=" * 40)
    
    # Crear archivo de ejemplo
    excel_file = create_sample_excel()
    
    # Importar y probar el convertidor simple
    try:
        from simple_excel_to_sql import SimpleExcelToSQL
        
        converter = SimpleExcelToSQL()
        success = converter.process_excel_simple(excel_file, "test_output_simple.sql")
        
        if success:
            print("\n✅ Test del convertidor simple: EXITOSO")
            
            # Leer primeras líneas del archivo generado
            with open("test_output_simple.sql", 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # Primeras 20 líneas
                print("\n📄 Primeras líneas del SQL generado:")
                for line in lines:
                    print(line.rstrip())
        else:
            print("\n❌ Test del convertidor simple: FALLIDO")
            
    except Exception as e:
        print(f"\n❌ Error en test simple: {str(e)}")

def test_ai_converter():
    """Prueba el convertidor con IA (requiere API key)"""
    print("\n🤖 TESTING CONVERTIDOR CON IA")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ No se encontró OPENAI_API_KEY - Saltando test de IA")
        return
    
    # Crear archivo de ejemplo
    excel_file = create_sample_excel()
    
    try:
        from google_ads_sql_generator import GoogleAdsExcelAnalyzer
        
        analyzer = GoogleAdsExcelAnalyzer()
        result = analyzer.process_excel_to_sql(excel_file, "test_output_ai.sql")
        
        if result['success']:
            print("\n✅ Test del convertidor con IA: EXITOSO")
            print(f"📊 Registros procesados: {result['total_records']}")
        else:
            print(f"\n❌ Test del convertidor con IA: FALLIDO - {result['error']}")
            
    except Exception as e:
        print(f"\n❌ Error en test IA: {str(e)}")

def main():
    """Función principal de testing"""
    print("🧪 SUITE DE PRUEBAS - GOOGLE ADS SQL GENERATOR")
    print("=" * 60)
    
    # Test 1: Convertidor simple
    test_simple_converter()
    
    # Test 2: Convertidor con IA
    test_ai_converter()
    
    print("\n🏁 TESTS COMPLETADOS")
    print("=" * 60)

if __name__ == "__main__":
    main()
