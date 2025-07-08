#!/usr/bin/env python3
"""
Probar el flujo completo con archivos limpios
"""
from supabase_client import SupabaseGoogleAdsClient
import os

def test_clean_workflow():
    """Probar el flujo completo con archivos demo limpios"""
    print("🧪 PROBANDO FLUJO COMPLETO CON ARCHIVOS LIMPIOS")
    print("=" * 50)
    
    # Verificar que los archivos demo existen
    demo_files = {
        'campaigns': 'demo_campaigns.xlsx',
        'ads': 'demo_ads.xlsx', 
        'keywords': 'demo_keywords.xlsx'
    }
    
    missing_files = []
    for file_type, filename in demo_files.items():
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        print("💡 Ejecuta 'python create_demo_files.py' primero")
        return False
    
    print("✅ Todos los archivos demo están disponibles")
    
    try:
        # Procesar archivos con los generadores específicos
        from campaigns_generator import CampaignsExcelToSQL
        from keywords_generator import KeywordsExcelToSQL
        
        print("\n📊 PASO 1: Procesando campañas...")
        campaigns_gen = CampaignsExcelToSQL()
        campaigns_success = campaigns_gen.process_excel_to_sql('demo_campaigns.xlsx', 'clean_campaigns.sql')
        
        if not campaigns_success:
            print("❌ Error procesando campañas")
            return False
        print("✅ Campañas procesadas")
        
        print("\n🔑 PASO 2: Procesando palabras clave...")
        keywords_gen = KeywordsExcelToSQL()
        keywords_success = keywords_gen.process_excel_to_sql('demo_keywords.xlsx', 'clean_keywords.sql')
        
        if not keywords_success:
            print("❌ Error procesando keywords")
            return False
        print("✅ Keywords procesadas")
        
        # Verificar contenido de keywords
        print(f"\n🔍 VERIFICANDO CONTENIDO DE KEYWORDS...")
        client = SupabaseGoogleAdsClient()
        keywords_data = client._parse_sql_file('clean_keywords.sql')
        
        print(f"📊 Keywords parseadas: {len(keywords_data)}")
        
        if keywords_data:
            print(f"🔍 Primeras 5 palabras clave:")
            for i, record in enumerate(keywords_data[:5]):
                kw = record.get('palabra_clave', 'N/A')
                estado = record.get('estado', 'N/A')
                campaña = record.get('campaña', 'N/A')
                print(f"   {i+1}. '{kw}' | Estado: {estado} | Campaña: {campaña}")
                
            # Verificar si hay palabras problemáticas
            problematic_keywords = [
                kw for kw in keywords_data 
                if kw.get('palabra_clave', '').lower() in ['habilitado', 'enabled', 'estado de palabras clave', 'palabra clave']
            ]
            
            if problematic_keywords:
                print(f"⚠️ PROBLEMA: {len(problematic_keywords)} palabras clave problemáticas encontradas")
                for prob in problematic_keywords:
                    print(f"   - '{prob.get('palabra_clave')}'")
            else:
                print("✅ No se encontraron palabras clave problemáticas")
        
        print(f"\n📤 PASO 3: Insertando en Supabase...")
        
        # Limpiar Supabase primero
        client.clear_all_tables()
        
        # Usar solo keywords y campaigns (simplificado para debug)
        result = client.insert_all_data(
            campaigns_file='clean_campaigns.sql',
            ads_file='demo_ads.sql',  # Usar archivo existente
            keywords_file='clean_keywords.sql',
            clear_tables=False  # Ya limpiamos arriba
        )
        
        if result['success']:
            print("✅ INSERCIÓN EXITOSA")
            
            # Verificar datos insertados
            print(f"\n🔍 VERIFICANDO DATOS EN SUPABASE...")
            
            # Verificar keywords
            keywords_check = client.supabase.table('google_ads_palabras_clave').select('palabra_clave, estado, campaña').limit(10).execute()
            
            if keywords_check.data:
                print(f"📊 Keywords en Supabase: {len(keywords_check.data)}")
                for i, record in enumerate(keywords_check.data[:5]):
                    kw = record.get('palabra_clave', 'N/A')
                    estado = record.get('estado', 'N/A')
                    campaña = record.get('campaña', 'N/A')
                    print(f"   {i+1}. '{kw}' | Estado: {estado} | Campaña: {campaña}")
                    
                # Verificar palabras problemáticas en Supabase
                problematic_in_db = [
                    record for record in keywords_check.data
                    if record.get('palabra_clave', '').lower() in ['habilitado', 'enabled', 'estado de palabras clave']
                ]
                
                if problematic_in_db:
                    print(f"❌ AÚN HAY PROBLEMAS: {len(problematic_in_db)} palabras problemáticas en Supabase")
                    return False
                else:
                    print("✅ ÉXITO: No hay palabras problemáticas en Supabase")
                    return True
            else:
                print("❌ No hay keywords en Supabase")
                return False
        else:
            print(f"❌ Error en inserción: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_clean_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PRUEBA EXITOSA: El problema de keywords está solucionado")
        print("✅ Ahora puedes subir archivos reales sin problemas")
    else:
        print("❌ PRUEBA FALLÓ: El problema persiste")
        print("🔧 Necesita más investigación en el generador de keywords")
