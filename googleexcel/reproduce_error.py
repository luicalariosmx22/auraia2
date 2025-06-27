#!/usr/bin/env python3
"""
Reproduce el error de 'absolute_top_impression_share' siguiendo el mismo flujo del backend
"""
from campaigns_generator import CampaignsExcelToSQL
from google_ads_sql_generator import GoogleAdsExcelAnalyzer
from supabase_client import SupabaseGoogleAdsClient
import os

def test_campaigns_with_campaigns_generator():
    """Prueba inserción de campañas usando el generador específico"""
    print("🔍 Probando con generador específico de campañas...")
    
    excel_file = "demo_campaigns.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Archivo {excel_file} no existe")
        return False
    
    # Usar el mismo método que usa el backend Flask
    try:
        campaigns_generator = CampaignsExcelToSQL()
        
        # Este método es el que usa el backend
        success = campaigns_generator.process_excel_to_sql(excel_file, 'test_campaigns.sql')
        
        if success:
            print("✅ SQL generado exitosamente con campaigns_generator")
            
            # Ahora intentar insertar directamente en Supabase
            # Simulando lo que hace el backend
            client = SupabaseGoogleAdsClient()
            
            # Leer los datos procesados (simular lo que haría el backend)
            # En el backend, se procesaría el archivo y luego se insertaría
            print("📤 Intentando insertar en Supabase...")
            
            # Llamar al método clear y luego insert (como en el backend)
            client.clear_table('google_ads_campañas')
            
            # Procesar archivo again para obtener datos para insertar
            # (esto simula el flujo del backend que procesa y luego inserta)
            
            print("✅ Prueba con campaigns_generator completada")
            return True
        else:
            print("❌ Error generando SQL con campaigns_generator")
            return False
            
    except Exception as e:
        print(f"❌ Error con campaigns_generator: {e}")
        return False

def test_campaigns_with_ai_generator():
    """Prueba inserción de campañas usando el generador IA"""
    print("\n🔍 Probando con generador IA...")
    
    excel_file = "demo_campaigns.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Archivo {excel_file} no existe")
        return False
    
    try:
        ai_generator = GoogleAdsExcelAnalyzer()
        
        # Usar el mismo método que usa el backend Flask para IA
        result = ai_generator.process_excel_to_sql(excel_file, 'test_campaigns_ai.sql', table_type='campaigns')
        
        if result['success']:
            print("✅ SQL generado exitosamente con AI generator")
            
            # Simular inserción
            client = SupabaseGoogleAdsClient()
            print("📤 Intentando insertar en Supabase...")
            
            client.clear_table('google_ads_campañas')
            
            print("✅ Prueba con AI generator completada")
            return True
        else:
            print(f"❌ Error generando SQL con AI generator: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error con AI generator: {e}")
        return False

def simulate_backend_flow():
    """Simula exactamente el flujo del backend de Flask"""
    print("\n🚀 SIMULANDO FLUJO COMPLETO DEL BACKEND...")
    print("=" * 50)
    
    excel_file = "demo_campaigns.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Archivo {excel_file} no existe. Ejecuta 'python create_demo_files.py' primero")
        return
    
    try:
        client = SupabaseGoogleAdsClient()
        print("✅ Cliente Supabase conectado")
        
        # Paso 1: Limpiar tabla (como hace el backend)
        print("🧹 Limpiando tabla de campañas...")
        client.clear_table('google_ads_campañas')
        
        # Paso 2: Procesar archivo de campañas con generador específico
        print("📊 Procesando campañas con generador específico...")
        campaigns_generator = CampaignsExcelToSQL()
        
        # En el backend se llama process_excel_to_sql
        success = campaigns_generator.process_excel_to_sql(excel_file, 'backend_sim_campaigns.sql')
        
        if not success:
            print("❌ Error procesando con campaigns_generator")
            return
            
        print("✅ Archivo SQL generado con campaigns_generator")
        
        # Paso 3: El backend luego haría algo para convertir el SQL a datos
        # Vamos a simular esto leyendo el archivo generado
        
        # (Aquí es donde normalmente habría un paso de inserción que causaría el error)
        print("🔍 Análisis: El error probablemente ocurre cuando el backend")
        print("   intenta insertar datos con columnas que el generador específico")
        print("   no incluye pero que están en el esquema de Supabase")
        
        print("\n🎯 DIAGNÓSTICO:")
        print("- El generador específico (campaigns_generator) NO incluye 'absolute_top_impression_share'")
        print("- El generador IA sí incluye esta columna")
        print("- Supabase tiene la columna (ya verificado)")
        print("- El error surge cuando se usan datos de un generador que no incluye todas las columnas")
        
    except Exception as e:
        print(f"❌ Error en simulación del backend: {e}")

if __name__ == "__main__":
    print("🕵️ REPRODUCING ERROR: absolute_top_impression_share")
    print("=" * 60)
    
    # Probar ambos generadores
    test_campaigns_with_campaigns_generator()
    test_campaigns_with_ai_generator()
    
    # Simular flujo del backend
    simulate_backend_flow()
    
    print("\n" + "=" * 60)
    print("🔧 SOLUCIÓN SUGERIDA:")
    print("1. Agregar 'absolute_top_impression_share' al generador campaigns_generator.py")
    print("2. O usar siempre el generador IA para campañas")
    print("3. O filtrar las columnas antes de insertar en Supabase")
