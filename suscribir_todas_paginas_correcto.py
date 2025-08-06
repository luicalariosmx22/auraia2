#!/usr/bin/env python3
"""
Suscribir todas las páginas faltantes usando el método correcto
POST /{PAGE_ID}/subscribed_apps
"""

import os
import requests
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
WEBHOOK_URL = os.getenv('META_WEBHOOK_URL')

def obtener_paginas_disponibles():
    """Obtener lista de páginas administradas disponibles"""
    print("=" * 60)
    print("📋 OBTENIENDO PÁGINAS DISPONIBLES")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            print(f"📊 Total páginas disponibles: {len(pages)}")
            
            paginas_info = []
            for page in pages:
                page_info = {
                    'id': page.get('id'),
                    'name': page.get('name'),
                    'category': page.get('category', 'Sin categoría'),
                    'access_token': page.get('access_token')
                }
                paginas_info.append(page_info)
                print(f"   📄 {page_info['name']} (ID: {page_info['id']})")
            
            return paginas_info
        else:
            print(f"❌ Error obteniendo páginas: {data}")
            return []
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def obtener_paginas_base_datos():
    """Obtener páginas de la base de datos"""
    print("\n" + "=" * 60)
    print("💾 OBTENIENDO PÁGINAS DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        from supabase.client import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Credenciales de Supabase no encontradas")
            return []
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Obtener todas las páginas de la base de datos
        result = supabase.table('facebook_paginas').select('*').execute()
        
        if result.data:
            print(f"📊 Total páginas en BD: {len(result.data)}")
            return result.data
        else:
            print(f"❌ No se encontraron páginas en BD")
            return []
            
    except Exception as e:
        print(f"❌ Error con base de datos: {str(e)}")
        return []

def verificar_aplicacion_suscrita(page_id, page_token):
    """Verificar si la aplicación ya está suscrita a una página"""
    url = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?access_token={page_token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            apps = data.get('data', [])
            our_app_id = os.getenv('META_APP_ID')
            
            for app in apps:
                if app.get('id') == our_app_id:
                    return True
            return False
        else:
            return False
    except Exception as e:
        return False

def suscribir_pagina_webhook(page_info):
    """Suscribir webhook para una página específica"""
    page_id = page_info['id']
    page_name = page_info['name']
    page_token = page_info['access_token']
    
    print(f"\n📡 Suscribiendo: {page_name} (ID: {page_id})")
    
    if not page_token:
        print(f"   ❌ Sin Page Access Token")
        return False
    
    # Verificar si ya está suscrita
    if verificar_aplicacion_suscrita(page_id, page_token):
        print(f"   ✅ Ya suscrita - omitiendo")
        return True
    
    # URL correcta para suscripción
    url = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps"
    
    # Datos para la suscripción
    data = {
        'access_token': page_token,
        'subscribed_fields': 'feed'
    }
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        
        if response.status_code == 200:
            success = result.get('success', False)
            if success:
                print(f"   ✅ Suscrita exitosamente")
                return True
            else:
                print(f"   ❌ Falló: {result}")
                return False
        else:
            print(f"   ❌ Error: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def actualizar_estado_bd(page_id, estado):
    """Actualizar estado de página en base de datos"""
    try:
        from supabase.client import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Verificar si existe columna webhook_estado
        try:
            result = supabase.table('facebook_paginas').update({
                'webhook_estado': estado
            }).eq('page_id', page_id).execute()
            return True
        except:
            # Si no existe la columna, intentar con otro campo o crear
            print(f"   ℹ️ Columna webhook_estado no existe - usando método alternativo")
            return False
            
    except Exception as e:
        return False

def suscribir_todas_las_paginas():
    """Proceso principal para suscribir todas las páginas"""
    print("🎯 SUSCRIPCIÓN MASIVA DE PÁGINAS - MÉTODO CORRECTO")
    print("=" * 80)
    
    # 1. Obtener páginas disponibles
    paginas_disponibles = obtener_paginas_disponibles()
    
    if not paginas_disponibles:
        print("❌ No hay páginas disponibles. Abortando.")
        return
    
    # 2. Obtener páginas de BD para referencia
    paginas_bd = obtener_paginas_base_datos()
    
    # 3. Crear mapeo de páginas BD por ID
    bd_mapping = {p.get('page_id'): p for p in paginas_bd}
    
    # 4. Estadísticas
    total_paginas = len(paginas_disponibles)
    exitosas = 0
    fallidas = 0
    ya_suscritas = 0
    
    print(f"\n" + "=" * 60)
    print(f"🚀 INICIANDO SUSCRIPCIÓN MASIVA")
    print(f"📊 Total páginas a procesar: {total_paginas}")
    print("=" * 60)
    
    # 5. Procesar cada página
    for i, page_info in enumerate(paginas_disponibles, 1):
        page_id = page_info['id']
        page_name = page_info['name']
        
        print(f"\n[{i}/{total_paginas}] Procesando: {page_name}")
        
        # Verificar si ya está suscrita antes de intentar
        if verificar_aplicacion_suscrita(page_id, page_info['access_token']):
            print(f"   ✅ Ya suscrita")
            ya_suscritas += 1
            
            # Actualizar BD si es posible
            actualizar_estado_bd(page_id, 'activa')
            continue
        
        # Intentar suscribir
        exito = suscribir_pagina_webhook(page_info)
        
        if exito:
            exitosas += 1
            # Actualizar BD
            actualizar_estado_bd(page_id, 'activa')
        else:
            fallidas += 1
            # Actualizar BD como fallida
            actualizar_estado_bd(page_id, 'error')
        
        # Pausa pequeña para no sobrecargar la API
        time.sleep(0.5)
    
    # 6. Reporte final
    print(f"\n" + "=" * 80)
    print(f"📊 REPORTE FINAL DE SUSCRIPCIÓN MASIVA")
    print("=" * 80)
    print(f"📄 Total páginas procesadas: {total_paginas}")
    print(f"✅ Ya suscritas previamente: {ya_suscritas}")
    print(f"🎉 Suscritas exitosamente: {exitosas}")
    print(f"❌ Fallidas: {fallidas}")
    print(f"📈 Tasa de éxito: {((ya_suscritas + exitosas) / total_paginas * 100):.1f}%")
    print(f"🔔 Total páginas con webhooks activos: {ya_suscritas + exitosas}")
    print("=" * 80)
    
    if exitosas > 0:
        print(f"🎯 ¡{exitosas} páginas nuevas suscritas exitosamente!")
    
    if fallidas > 0:
        print(f"⚠️ {fallidas} páginas fallaron - posibles problemas de permisos")

def main():
    """Función principal"""
    suscribir_todas_las_paginas()

if __name__ == "__main__":
    main()
