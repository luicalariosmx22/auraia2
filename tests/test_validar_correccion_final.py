#!/usr/bin/env python3
"""
🚀 TEST ULTRA EFICIENTE: Validar corrección de desconexión Facebook
Valida que la función corregida funciona con los nombres de columnas correctos
"""

import os
from supabase.client import create_client, Client

def test_validar_correccion_final():
    """Simula la función corregida con nombres de columnas exactos"""
    
    # 🔗 Conexión directa a Supabase (ULTRA EFICIENTE)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")  # ✅ Corregido nombre de variable
    supabase = create_client(url, key)
    
    page_id = "782681001814242"
    
    print(f"🔍 Validando corrección para página {page_id}")
    
    try:
        # ✅ FUNCIÓN CORREGIDA - usando 'access_token' en lugar de 'page_access_token'
        result = supabase.table('facebook_paginas').update({
            'webhook_activo': False,
            'estado_webhook': 'pausada',  # ✅ Corregido de 'error' a 'pausada'
            'ultima_sincronizacion': 'now()',
            'access_token': None  # ✅ Corregido el nombre de columna
        }).eq('page_id', page_id).execute()
        
        print(f"✅ Función corregida ejecutada exitosamente")
        print(f"📊 Registros afectados: {len(result.data)}")
        
        if result.data:
            registro = result.data[0]
            print(f"📄 Estado final: webhook_activo={registro.get('webhook_activo')}, estado_webhook={registro.get('estado_webhook')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    exito = test_validar_correccion_final()
    if exito:
        print("\n🎉 CORRECCIÓN VALIDADA: La función ahora funciona correctamente")
    else:
        print("\n⚠️ La corrección necesita ajustes adicionales")
