#!/usr/bin/env python3
"""
Test para diagnosticar por qué no se puede desconectar la página 782681001814242
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.meta_webhook_helpers import desuscribir_webhook_pagina

def diagnosticar_pagina_782681001814242():
    pagina_id = "782681001814242"
    
    print(f"🔍 Diagnosticando página: {pagina_id}")
    print("=" * 50)
    
    # 1. Verificar estado en BD
    try:
        result = supabase.table("facebook_paginas").select("*").eq("page_id", pagina_id).execute()
        
        if result.data:
            pagina = result.data[0]
            print(f"📊 Estado en BD:")
            print(f"   - Página ID: {pagina.get('page_id')}")
            print(f"   - Nombre: {pagina.get('nombre_pagina', 'N/A')}")
            print(f"   - Token válido: {bool(pagina.get('page_access_token'))}")
            print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
            print(f"   - Fecha creación: {pagina.get('created_at')}")
            print(f"   - Última actividad: {pagina.get('ultima_actividad_webhook')}")
        else:
            print("❌ Página NO encontrada en BD")
            return
            
    except Exception as e:
        print(f"❌ Error consultando BD: {e}")
        return
    
    # 2. Intentar desuscribir webhook
    print(f"\n🔧 Intentando desuscribir webhook...")
    try:
        resultado = desuscribir_webhook_pagina(pagina_id, pagina.get('page_access_token'))
        print(f"✅ Resultado desuscripción: {resultado}")
    except Exception as e:
        print(f"❌ Error en desuscripción: {e}")
    
    # 3. Verificar estado después
    print(f"\n🔍 Verificando estado después de desuscripción...")
    try:
        result_after = supabase.table("facebook_paginas").select("*").eq("page_id", pagina_id).execute()
        if result_after.data:
            pagina_after = result_after.data[0]
            print(f"📊 Estado después:")
            print(f"   - Estado webhook: {pagina_after.get('estado_webhook')}")
            print(f"   - Última actualización: {pagina_after.get('updated_at')}")
        
    except Exception as e:
        print(f"❌ Error verificando estado después: {e}")

if __name__ == "__main__":
    diagnosticar_pagina_782681001814242()
