"""
Script para probar la inserción después de agregar las columnas de campañas
"""

from supabase_client import SupabaseGoogleAdsClient

def test_insertion_after_fix():
    """Prueba la inserción después de agregar las columnas faltantes"""
    
    print("🧪 PROBANDO INSERCIÓN DESPUÉS DE AGREGAR COLUMNAS")
    print("=" * 50)
    
    try:
        client = SupabaseGoogleAdsClient()
        
        # Intentar la inserción completa
        result = client.insert_all_data(
            'demo_campaigns.sql', 
            'demo_ads.sql', 
            'demo_keywords.sql', 
            clear_tables=True
        )
        
        if result['success']:
            print("✅ ¡ÉXITO! La inserción funcionó perfectamente")
            print(f"📊 Total insertado: {result['total_inserted']} registros")
            print(f"📈 Campañas: {result['results']['campaigns']['inserted_count']}")
            print(f"📺 Anuncios: {result['results']['ads']['inserted_count']}")
            print(f"🔑 Palabras clave: {result['results']['keywords']['inserted_count']}")
        else:
            print("❌ La inserción falló:")
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_insertion_after_fix()
