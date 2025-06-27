"""
Script para probar la limpieza robusta de tablas en Supabase
"""

import sys
import os
from supabase_client import SupabaseGoogleAdsClient
from create_demo_files import create_demo_files

def test_robust_cleanup():
    """Prueba completa de la limpieza robusta"""
    
    print("🧪 PRUEBA DE LIMPIEZA ROBUSTA DE TABLAS")
    print("=" * 50)
    
    try:
        # 1. Inicializar cliente
        print("\n1️⃣ Inicializando cliente de Supabase...")
        client = SupabaseGoogleAdsClient()
        
        # 2. Probar conexión
        print("\n2️⃣ Probando conexión...")
        connection_test = client.test_connection()
        print(f"Conexión: {'✅ OK' if connection_test['success'] else '❌ FAIL'}")
        if not connection_test['success']:
            print(f"Error: {connection_test['error']}")
            return False
        
        # 3. Crear datos de prueba si no existen
        print("\n3️⃣ Verificando si hay datos en las tablas...")
        
        # Verificar campañas
        campaigns_count = client.supabase.table('google_ads_campañas').select('*', count='exact').execute()
        print(f"📊 Campañas actuales: {campaigns_count.count if hasattr(campaigns_count, 'count') else 'N/A'}")
        
        # Verificar anuncios  
        ads_count = client.supabase.table('google_ads_reporte_anuncios').select('*', count='exact').execute()
        print(f"📊 Anuncios actuales: {ads_count.count if hasattr(ads_count, 'count') else 'N/A'}")
        
        # Verificar keywords
        keywords_count = client.supabase.table('google_ads_palabras_clave').select('*', count='exact').execute()
        print(f"📊 Keywords actuales: {keywords_count.count if hasattr(keywords_count, 'count') else 'N/A'}")
        
        # Si no hay datos, crear algunos para probar la limpieza
        total_records = (campaigns_count.count or 0) + (ads_count.count or 0) + (keywords_count.count or 0)
        
        if total_records == 0:
            print("\n📦 No hay datos. Creando datos de prueba...")
            create_demo_files()
            
            # Insertar datos demo
            from test_demo_insertion import main as insert_demo
            insert_demo()
            
            print("✅ Datos de prueba creados e insertados")
        
        # 4. Verificar nuevamente las tablas antes de limpieza
        print("\n4️⃣ Estado de tablas ANTES de limpieza:")
        
        campaigns_count = client.supabase.table('google_ads_campañas').select('*', count='exact').execute()
        ads_count = client.supabase.table('google_ads_reporte_anuncios').select('*', count='exact').execute()
        keywords_count = client.supabase.table('google_ads_palabras_clave').select('*', count='exact').execute()
        
        print(f"📊 Campañas: {campaigns_count.count if hasattr(campaigns_count, 'count') else 'N/A'}")
        print(f"📊 Anuncios: {ads_count.count if hasattr(ads_count, 'count') else 'N/A'}")
        print(f"📊 Keywords: {keywords_count.count if hasattr(keywords_count, 'count') else 'N/A'}")
        
        # 5. Ejecutar limpieza robusta
        print("\n5️⃣ Ejecutando limpieza robusta...")
        cleanup_result = client.clear_all_tables()
        
        print(f"Resultado de limpieza: {'✅ OK' if cleanup_result['success'] else '❌ FAIL'}")
        if cleanup_result['success']:
            print("📊 Registros eliminados por tabla:")
            for table, count in cleanup_result['deleted_counts'].items():
                print(f"  - {table}: {count}")
        else:
            print(f"❌ Error: {cleanup_result['error']}")
            return False
        
        # 6. Verificar que las tablas están realmente vacías
        print("\n6️⃣ Verificando que las tablas están vacías...")
        
        campaigns_count_after = client.supabase.table('google_ads_campañas').select('*', count='exact').execute()
        ads_count_after = client.supabase.table('google_ads_reporte_anuncios').select('*', count='exact').execute()
        keywords_count_after = client.supabase.table('google_ads_palabras_clave').select('*', count='exact').execute()
        
        print(f"📊 Campañas después: {campaigns_count_after.count if hasattr(campaigns_count_after, 'count') else 'N/A'}")
        print(f"📊 Anuncios después: {ads_count_after.count if hasattr(ads_count_after, 'count') else 'N/A'}")
        print(f"📊 Keywords después: {keywords_count_after.count if hasattr(keywords_count_after, 'count') else 'N/A'}")
        
        # 7. Validar resultado
        final_total = (campaigns_count_after.count or 0) + (ads_count_after.count or 0) + (keywords_count_after.count or 0)
        
        if final_total == 0:
            print("\n✅ PRUEBA EXITOSA: Todas las tablas están completamente vacías")
            return True
        else:
            print(f"\n❌ PRUEBA FALLIDA: Quedan {final_total} registros en total")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
        return False

def test_edge_cases():
    """Prueba casos especiales de limpieza"""
    
    print("\n🔍 PRUEBA DE CASOS ESPECIALES")
    print("=" * 40)
    
    try:
        client = SupabaseGoogleAdsClient()
        
        # Probar limpieza cuando las tablas ya están vacías
        print("\n🧹 Probando limpieza de tablas ya vacías...")
        cleanup_result = client.clear_all_tables()
        
        if cleanup_result['success']:
            print("✅ Limpieza de tablas vacías: OK")
            for table, count in cleanup_result['deleted_counts'].items():
                print(f"  - {table}: {count} registros")
        else:
            print(f"❌ Error: {cleanup_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en casos especiales: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE LIMPIEZA ROBUSTA")
    
    # Prueba principal
    test1_success = test_robust_cleanup()
    
    # Prueba de casos especiales
    test2_success = test_edge_cases()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS:")
    print(f"  - Limpieza robusta: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"  - Casos especiales: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - La limpieza robusta funciona correctamente")
        sys.exit(0)
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON - Revisar implementación")
        sys.exit(1)
