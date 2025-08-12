#!/usr/bin/env python3
"""
Diagnóstico específico para la página 782681001814242 que no se puede desconectar
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from clientes.aura.utils.supabase_client import supabase

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
            print(f"   - Token válido: {'SÍ' if pagina.get('page_access_token') else 'NO'}")
            print(f"   - Estado webhook: {pagina.get('estado_webhook')}")
            print(f"   - Fecha creación: {pagina.get('created_at')}")
            print(f"   - Última actividad: {pagina.get('ultima_actividad_webhook')}")
            
            token = pagina.get('page_access_token')
        else:
            print("❌ Página NO encontrada en BD")
            return
            
    except Exception as e:
        print(f"❌ Error consultando BD: {e}")
        return
    
    # 2. Verificar logs de webhooks recientes
    print(f"\n📋 Logs de webhooks recientes:")
    try:
        logs_result = supabase.table("logs_webhooks_meta").select("*").eq("page_id", pagina_id).order("timestamp", desc=True).limit(5).execute()
        
        if logs_result.data:
            for log in logs_result.data:
                print(f"   - {log.get('timestamp')}: {log.get('field')} - {log.get('value')}")
        else:
            print("   - No hay logs recientes")
            
    except Exception as e:
        print(f"❌ Error consultando logs: {e}")
    
    # 3. Verificar subscripciones actuales en Meta
    print(f"\n🔍 Verificando subscripciones en Meta...")
    if token:
        try:
            import requests
            
            # Obtener subscripciones actuales
            url = f"https://graph.facebook.com/v18.0/{pagina_id}/subscribed_apps"
            params = {
                'access_token': token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                apps = data.get('data', [])
                print(f"📱 Apps suscritas ({len(apps)}):")
                for app in apps:
                    print(f"   - App ID: {app.get('id')}")
                    print(f"   - Nombre: {app.get('name')}")
                    print(f"   - Campos: {app.get('subscribed_fields', [])}")
            else:
                print(f"❌ Error verificando subscripciones: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error verificando Meta: {e}")
    else:
        print("❌ No hay token válido para verificar")
    
    # 4. Simular desconexión real
    print(f"\n🔧 Opciones para desconectar correctamente:")
    print("1. Actualizar estado a 'inactiva' en BD")
    print("2. Eliminar registro completamente de BD")
    print("3. Desuscribir webhook de Meta API")
    
    opcion = input("\n¿Qué opción quieres ejecutar? (1/2/3/n para ninguna): ")
    
    if opcion == "1":
        try:
            update_response = supabase.table('facebook_paginas').update({
                'estado_webhook': 'inactiva'
            }).eq('page_id', pagina_id).execute()
            print("✅ Estado actualizado a 'inactiva'")
        except Exception as e:
            print(f"❌ Error actualizando: {e}")
            
    elif opcion == "2":
        confirm = input("⚠️ ¿Estás SEGURO de eliminar el registro? (sí/no): ")
        if confirm.lower() == "sí":
            try:
                delete_response = supabase.table('facebook_paginas').delete().eq('page_id', pagina_id).execute()
                print("✅ Registro eliminado de BD")
            except Exception as e:
                print(f"❌ Error eliminando: {e}")
        else:
            print("❌ Operación cancelada")
            
    elif opcion == "3":
        if token:
            try:
                # Desuscribir de Meta
                url = f"https://graph.facebook.com/v18.0/{pagina_id}/subscribed_apps"
                data = {
                    'access_token': token,
                    'subscribed_fields': ''  # Campos vacíos = desuscribir
                }
                
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    print("✅ Webhook desuscrito de Meta")
                    # También actualizar BD
                    supabase.table('facebook_paginas').update({
                        'estado_webhook': 'inactiva'
                    }).eq('page_id', pagina_id).execute()
                    print("✅ Estado actualizado en BD")
                else:
                    print(f"❌ Error desuscribiendo: {response.status_code}")
                    print(f"   Respuesta: {response.text}")
            except Exception as e:
                print(f"❌ Error en desuscripción Meta: {e}")
        else:
            print("❌ No hay token válido")

if __name__ == "__main__":
    diagnosticar_pagina_782681001814242()
