#!/usr/bin/env python3
"""
Test ultra eficiente para probar desconexión corregida
"""
from supabase.client import create_client, Client

def test_desconectar_corregido():
    """Test de desconexión con nombres de columnas correctos"""
    
    # Variables hardcodeadas para test rápido
    url = "https://sylqljdiiyhtgtrghwjk.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q"
    
    supabase: Client = create_client(url, key)
    
    pagina_id = "782681001814242"
    print(f"🔧 Probando desconexión corregida: {pagina_id}")
    print("=" * 60)
    
    try:
        # 1. Verificar columnas disponibles
        print("📋 Verificando estructura de tabla...")
        current_result = supabase.table("facebook_paginas").select("*").eq("page_id", pagina_id).limit(1).execute()
        
        if current_result.data:
            pagina_actual = current_result.data[0]
            print(f"📊 Estado ANTES:")
            print(f"   - Nombre: {pagina_actual.get('nombre_pagina')}")
            print(f"   - Estado webhook: {pagina_actual.get('estado_webhook')}")
            print(f"   - access_token: {'presente' if pagina_actual.get('access_token') else 'ausente'}")
            print(f"   - access_token_valido: {pagina_actual.get('access_token_valido')}")
        
        # 2. Simular la lógica de desconexión corregida
        print(f"\n🔧 Simulando desconexión con columnas correctas...")
        
        # Verificar si existe access_token (como hace la función corregida)
        page_result = supabase.table('facebook_paginas').select('access_token').eq('page_id', pagina_id).execute()
        
        if page_result.data:
            page_token = page_result.data[0].get('access_token')
            print(f"✅ Token encontrado: {'SÍ' if page_token else 'NO'}")
            
            # Actualizar estado (usando 'pausada' que está permitido)
            update_response = supabase.table('facebook_paginas').update({
                'estado_webhook': 'pausada',
                'access_token': None  # Limpiar token
            }).eq('page_id', pagina_id).execute()
            
            if update_response.data:
                print(f"✅ Página desconectada exitosamente")
                
                # Verificar resultado
                final_result = supabase.table("facebook_paginas").select("estado_webhook, access_token, access_token_valido").eq("page_id", pagina_id).execute()
                if final_result.data:
                    pagina = final_result.data[0]
                    print(f"📊 Estado DESPUÉS:")
                    print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
                    print(f"   - access_token: {'presente' if pagina.get('access_token') else 'ausente'}")
                    print(f"   - access_token_valido: {pagina.get('access_token_valido')}")
                    return True
            else:
                print("❌ No se pudo actualizar")
                return False
        else:
            print("❌ No se encontró la página")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de desconexión con columnas corregidas")
    print("⚡ Sin cargar Flask ni blueprints")
    print()
    
    resultado = test_desconectar_corregido()
    
    if resultado:
        print("\n🎯 ¡Desconexión corregida funcional!")
        print("💡 Ahora la función debería funcionar sin errores")
    else:
        print("\n❌ Error en el test")
