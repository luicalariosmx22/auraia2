#!/usr/bin/env python3
"""
Test para desconectar correctamente la página 782681001814242
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from clientes.aura.utils.supabase_client import supabase

def desconectar_pagina_782681001814242():
    pagina_id = "782681001814242"
    
    print(f"🔧 Desconectando página: {pagina_id}")
    print("=" * 50)
    
    try:
        # Actualizar estado - usar 'error' para páginas desconectadas
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'error',
            'page_access_token': None,  # Limpiar token
            'updated_at': 'now()'
        }).eq('page_id', pagina_id).execute()
        
        if update_response.data:
            print("✅ Página desconectada exitosamente")
            print(f"   - Estado: error")
            print(f"   - Token: eliminado")
            print(f"   - Actualizada: ahora")
            
            # Verificar estado final
            final_result = supabase.table("facebook_paginas").select("*").eq("page_id", pagina_id).execute()
            if final_result.data:
                pagina = final_result.data[0]
                print(f"\n📊 Estado final:")
                print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
                print(f"   - Token válido: {'SÍ' if pagina.get('page_access_token') else 'NO'}")
                print(f"   - Última actualización: {pagina.get('updated_at')}")
            
        else:
            print("❌ Error al desconectar página")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    desconectar_pagina_782681001814242()
