#!/usr/bin/env python3
"""
Test unitario directo - Solo prueba la lógica sin cargar Flask.

Este enfoque es el más rápido porque:
- No carga la aplicación Flask
- No registra blueprints
- Solo prueba la lógica específica
"""

import os
import sys
from datetime import datetime, timedelta

# Solo agregamos el path sin cargar la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar solo lo necesario
from clientes.aura.utils.supabase_client import supabase

def test_logica_webhook_directo():
    """Prueba solo la lógica de webhook sin cargar Flask."""
    print("🧪 Test unitario directo - Sin cargar aplicación Flask\n")
    
    page_id = "121755595885612"
    
    try:
        # Obtener datos directamente
        response = supabase.table('facebook_paginas').select('*').eq('page_id', page_id).single().execute()
        pagina = response.data
        
        # Simular la lógica de webhook (copiada de la función original)
        webhook_activo = False
        publicaciones_response = supabase.table("meta_publicaciones_webhook") \
            .select("created_time") \
            .eq("page_id", page_id) \
            .limit(5) \
            .execute()
        
        publicaciones = publicaciones_response.data if publicaciones_response.data else []
        
        if publicaciones:
            fecha_limite = datetime.now() - timedelta(days=7)
            for pub in publicaciones:
                if pub.get('created_time'):
                    try:
                        if isinstance(pub['created_time'], (int, float)):
                            fecha_pub = datetime.fromtimestamp(pub['created_time'])
                        else:
                            fecha_pub = datetime.fromisoformat(pub['created_time'].replace('Z', '+00:00'))
                        
                        if fecha_pub >= fecha_limite:
                            webhook_activo = True
                            break
                    except:
                        continue
        
        # Aplicar lógica corregida
        estado_db = pagina.get('estado_webhook', 'pausada')
        if estado_db == 'activa' or webhook_activo:
            estado_real = 'activa'
        else:
            estado_real = 'inactiva'
        
        print(f"✅ Página: {pagina['nombre_pagina']}")
        print(f"📊 Estado BD: {estado_db}")
        print(f"📈 Actividad: {webhook_activo}")
        print(f"🎯 Resultado: {estado_real}")
        
        return estado_real
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_logica_webhook_directo()
