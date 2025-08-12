#!/usr/bin/env python3
"""
Test ULTRA eficiente - Solo Supabase directo, SIN imports de la app
"""
from supabase.client import create_client, Client

def test_desconectar_directo():
    """Test directo a Supabase sin pasar por la aplicación"""
    
    # Variables hardcodeadas para test rápido
    url = "https://sylqljdiiyhtgtrghwjk.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q"
    
    supabase: Client = create_client(url, key)
    
    pagina_id = "782681001814242"
    print(f"🔧 Desconectando página: {pagina_id} (DIRECTO - SIN BLUEPRINTS)")
    print("=" * 60)
    
    try:
        # Primero verificar estructura de la tabla
        print("📋 Verificando estructura de la tabla...")
        current_result = supabase.table("facebook_paginas").select("*").eq("page_id", pagina_id).limit(1).execute()
        
        if current_result.data:
            pagina_actual = current_result.data[0]
            print(f"📊 Estado ANTES:")
            print(f"   - Nombre: {pagina_actual.get('nombre_pagina')}")
            print(f"   - Estado webhook: {pagina_actual.get('estado_webhook')}")
            print(f"   - Total columnas: {len(pagina_actual.keys())}")
            
            # Mostrar algunas columnas clave
            columnas_token = [k for k in pagina_actual.keys() if 'token' in k.lower()]
            if columnas_token:
                print(f"   - Columnas con 'token': {columnas_token}")
        
        # Actualización directa - usar 'pausada' que ya sabemos que funciona
        print(f"\n🔧 Actualizando estado a 'pausada' (valor seguro)...")
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'pausada'
        }).eq('page_id', pagina_id).execute()
        
        if update_response.data:
            print(f"✅ Página desconectada exitosamente")
            
            # Verificar resultado
            final_result = supabase.table("facebook_paginas").select("estado_webhook, nombre_pagina").eq("page_id", pagina_id).execute()
            if final_result.data:
                pagina = final_result.data[0]
                print(f"📊 Estado DESPUÉS:")
                print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
                print(f"   - Nombre: {pagina.get('nombre_pagina')}")
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
    print("⚡ Tiempo de carga: INSTANTÁNEO")
    print()
    
    resultado = test_desconectar_directo()
    
    if resultado:
        print("\n🎯 ¡Desconexión completada! Página marcada como 'error'")
        print("💡 Ahora debería aparecer como desconectada en el frontend")
    else:
        print("\n❌ Error en la operación")
