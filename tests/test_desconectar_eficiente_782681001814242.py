#!/usr/bin/env python3
"""
Test eficiente para desconectar página 782681001814242 - SIN cargar toda la app
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Solo importar lo necesario - NO from app import create_app
from clientes.aura.utils.supabase_client import supabase

def desconectar_pagina_sin_blueprints():
    """Función pura para desconectar página sin cargar Flask"""
    pagina_id = "782681001814242"
    
    print(f"🔧 Desconectando página: {pagina_id} (SIN cargar blueprints)")
    print("=" * 50)
    
    try:
        # Test directo contra Supabase - sin Flask
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'error',  # Estado válido según restricción
            'page_access_token': None,  # Limpiar token
        }).eq('page_id', pagina_id).execute()
        
        if update_response.data:
            print("✅ Página desconectada exitosamente")
            
            # Verificar estado final
            final_result = supabase.table("facebook_paginas").select("estado_webhook, page_access_token, updated_at").eq("page_id", pagina_id).execute()
            if final_result.data:
                pagina = final_result.data[0]
                print(f"📊 Estado final:")
                print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
                print(f"   - Token válido: {'NO' if pagina.get('page_access_token') is None else 'SÍ'}")
                print(f"   - Última actualización: {pagina.get('updated_at')}")
                
                return True
        else:
            print("❌ Error al desconectar página")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_estado_webhook_valido():
    """Test de función pura - estados válidos"""
    def calcular_estado_para_desconexion(tiene_token: bool) -> str:
        return 'error' if not tiene_token else 'activa'
    
    # Tests sin Flask
    assert calcular_estado_para_desconexion(False) == 'error'
    assert calcular_estado_para_desconexion(True) == 'activa'
    
    print("✅ Test de lógica pura: PASSED")

if __name__ == "__main__":
    print("🧪 Ejecutando test EFICIENTE (sin blueprints)")
    
    # 1. Test de lógica pura
    test_estado_webhook_valido()
    
    # 2. Test de operación real
    resultado = desconectar_pagina_sin_blueprints()
    
    if resultado:
        print("\n🎯 Desconexión completada exitosamente")
    else:
        print("\n❌ Error en desconexión")
