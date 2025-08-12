#!/usr/bin/env python3
"""
Test ULTRA eficiente - Solo Supabase directo, SIN imports de la app
"""
import os
from supabase.client import create_client, Client

#!/usr/bin/env python3
"""
Test ULTRA eficiente - Solo Supabase directo, SIN imports de la app
"""
import os
from supabase.client import create_client, Client

def test_desconectar_directo():
    """Test directo a Supabase sin pasar por la aplicación"""
    
    # Variables hardcodeadas para test rápido
    url = "https://sylqljdiiyhtgtrghwjk.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q"
    
    supabase: Client = create_client(url, key)
    
    pagina_id = "782681001814242"
    print(f"🔧 Desconectando página: {pagina_id} (DIRECTO)")
    print("=" * 50)
    
    try:
        # Primero verificar estado actual
        current_result = supabase.table("facebook_paginas").select("estado_webhook, page_access_token, nombre_pagina").eq("page_id", pagina_id).execute()
        if current_result.data:
            pagina_actual = current_result.data[0]
            print(f"� Estado ANTES:")
            print(f"   - Nombre: {pagina_actual.get('nombre_pagina')}")
            print(f"   - Estado webhook: {pagina_actual.get('estado_webhook')}")
            print(f"   - Token: {'presente' if pagina_actual.get('page_access_token') else 'ausente'}")
        
        # Actualización directa sin Flask
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'error',
            'page_access_token': None,
        }).eq('page_id', pagina_id).execute()
        
        if update_response.data:
            print(f"\n✅ Página desconectada exitosamente")
            
            # Verificar resultado
            final_result = supabase.table("facebook_paginas").select("estado_webhook, page_access_token").eq("page_id", pagina_id).execute()
            if final_result.data:
                pagina = final_result.data[0]
                print(f"📊 Estado DESPUÉS:")
                print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
                print(f"   - Token: {'presente' if pagina.get('page_access_token') else 'ausente'}")
                return True
        else:
            print("❌ No se actualizó ningún registro")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test ULTRA EFICIENTE - Solo Supabase")
    print("📝 SIN blueprints, SIN Flask, SIN aplicación")
    print()
    
    resultado = test_desconectar_directo()
    
    if resultado:
        print("\n🎯 ¡Desconexión completada!")
    else:
        print("\n❌ Error en la operación")
