#!/usr/bin/env python3
"""
Limpieza completa de Supabase y verificación
"""
from supabase_client import SupabaseGoogleAdsClient

def force_clean_supabase():
    """Forzar limpieza completa de Supabase"""
    print("🧹 LIMPIEZA FORZADA DE SUPABASE")
    print("=" * 40)
    
    try:
        client = SupabaseGoogleAdsClient()
        
        # Limpiar usando el método normal
        result = client.clear_all_tables()
        print(f"✅ Limpieza normal: {result}")
        
        # Verificar que está limpio
        tables = ['google_ads_palabras_clave', 'google_ads_reporte_anuncios', 'google_ads_campañas']
        
        for table in tables:
            try:
                check_result = client.supabase.table(table).select('*').limit(1).execute()
                count = len(check_result.data) if check_result.data else 0
                print(f"📊 {table}: {count} registros restantes")
                
                if count > 0:
                    print(f"⚠️ {table} aún tiene datos, intentando limpieza manual...")
                    # Intentar delete más agresivo
                    try:
                        # Obtener todos los IDs y borrar uno por uno si es necesario
                        all_records = client.supabase.table(table).select('id').execute()
                        if all_records.data:
                            for record in all_records.data:
                                client.supabase.table(table).delete().eq('id', record['id']).execute()
                            print(f"✅ {table}: Limpieza manual completada")
                    except Exception as manual_error:
                        print(f"❌ Error en limpieza manual de {table}: {manual_error}")
                        
            except Exception as e:
                print(f"❌ Error verificando {table}: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza forzada: {e}")
        return False

if __name__ == "__main__":
    if force_clean_supabase():
        print("\n✅ LIMPIEZA COMPLETADA")
        print("💡 Ahora puedes subir nuevos archivos sin datos mezclados")
    else:
        print("\n❌ LIMPIEZA FALLÓ")
        print("🔧 Puede que necesites limpiar manualmente desde el panel de Supabase")
