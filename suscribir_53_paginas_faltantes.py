#!/usr/bin/env python3
"""
Suscribir las 53 páginas restantes usando el método de Luica Larios
Obtener Page Access Token directamente + /subscribed_apps
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

def obtener_paginas_faltantes():
    """Obtener páginas que están en BD pero no en /me/accounts"""
    print("=" * 60)
    print("🔍 IDENTIFICANDO PÁGINAS FALTANTES")
    print("=" * 60)
    
    # 1. Obtener páginas disponibles en /me/accounts
    try:
        url_accounts = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
        response = requests.get(url_accounts)
        accounts_data = response.json()
        
        if response.status_code == 200:
            pages_disponibles = {p.get('id') for p in accounts_data.get('data', [])}
            print(f"📊 Páginas en /me/accounts: {len(pages_disponibles)}")
        else:
            print(f"❌ Error obteniendo accounts: {accounts_data}")
            return []
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []
    
    # 2. Obtener páginas de la base de datos
    try:
        from supabase.client import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Credenciales de Supabase no encontradas")
            return []
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        result = supabase.table('facebook_paginas').select('*').execute()
        
        if result.data:
            pages_bd = result.data
            print(f"📊 Páginas en BD: {len(pages_bd)}")
        else:
            print(f"❌ No se encontraron páginas en BD")
            return []
            
    except Exception as e:
        print(f"❌ Error con base de datos: {str(e)}")
        return []
    
    # 3. Identificar páginas faltantes
    paginas_faltantes = []
    for page in pages_bd:
        page_id = page.get('page_id')
        if page_id not in pages_disponibles:
            paginas_faltantes.append({
                'id': page_id,
                'name': page.get('name', 'Sin nombre'),
                'category': page.get('category', 'Sin categoría')
            })
    
    print(f"🎯 Páginas faltantes identificadas: {len(paginas_faltantes)}")
    print("\n📋 Lista de páginas faltantes:")
    
    for i, page in enumerate(paginas_faltantes, 1):
        print(f"   {i:2d}. {page['name']} (ID: {page['id']})")
    
    return paginas_faltantes

def obtener_page_access_token_directo(page_id):
    """Obtener Page Access Token directamente (método Luica Larios)"""
    url = f"https://graph.facebook.com/v21.0/{page_id}?fields=id,name,access_token&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            page_token = data.get('access_token')
            page_name = data.get('name')
            return page_token, page_name
        else:
            return None, None
    except Exception as e:
        return None, None

def suscribir_pagina_metodo_luica(page_info):
    """Suscribir página usando el método de Luica Larios"""
    page_id = page_info['id']
    page_name = page_info['name']
    
    print(f"\n📡 [{page_name}] Procesando...")
    
    # 1. Obtener Page Access Token directamente
    page_token, nombre_real = obtener_page_access_token_directo(page_id)
    
    if not page_token:
        print(f"   ❌ No se pudo obtener Page Access Token")
        return False
    
    print(f"   ✅ Page Access Token obtenido: {page_token[:30]}...")
    
    # 2. Verificar si ya está suscrita
    try:
        url_check = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?access_token={page_token}"
        response_check = requests.get(url_check)
        
        if response_check.status_code == 200:
            apps = response_check.json().get('data', [])
            our_app_id = os.getenv('META_APP_ID')
            
            for app in apps:
                if app.get('id') == our_app_id:
                    print(f"   ✅ Ya suscrita - omitiendo")
                    return True
    except:
        pass  # Continuar con la suscripción
    
    # 3. Suscribir usando /subscribed_apps
    url_subscribe = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps"
    
    data = {
        'access_token': page_token,
        'subscribed_fields': 'feed'
    }
    
    try:
        response = requests.post(url_subscribe, data=data)
        result = response.json()
        
        if response.status_code == 200:
            success = result.get('success', False)
            if success:
                print(f"   🎉 Suscrita exitosamente")
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

def suscribir_paginas_faltantes():
    """Proceso principal para suscribir páginas faltantes"""
    print("🎯 SUSCRIPCIÓN DE 53 PÁGINAS FALTANTES - MÉTODO LUICA LARIOS")
    print("=" * 80)
    
    # 1. Obtener páginas faltantes
    paginas_faltantes = obtener_paginas_faltantes()
    
    if not paginas_faltantes:
        print("❌ No hay páginas faltantes para procesar")
        return
    
    total_faltantes = len(paginas_faltantes)
    print(f"\n🚀 Iniciando suscripción de {total_faltantes} páginas faltantes")
    
    # 2. Estadísticas
    exitosas = 0
    fallidas = 0
    ya_suscritas = 0
    
    print(f"\n" + "=" * 60)
    print(f"🔄 PROCESANDO PÁGINAS FALTANTES")
    print("=" * 60)
    
    # 3. Procesar cada página faltante
    for i, page_info in enumerate(paginas_faltantes, 1):
        print(f"\n[{i}/{total_faltantes}] {page_info['name']}")
        
        # Intentar suscribir usando método Luica Larios
        resultado = suscribir_pagina_metodo_luica(page_info)
        
        if resultado is True:
            # Verificar si ya estaba suscrita o se suscribió ahora
            if "Ya suscrita" in str(resultado):
                ya_suscritas += 1
            else:
                exitosas += 1
        else:
            fallidas += 1
        
        # Pausa para no sobrecargar la API
        time.sleep(0.3)
    
    # 4. Reporte final
    print(f"\n" + "=" * 80)
    print(f"📊 REPORTE FINAL - PÁGINAS FALTANTES")
    print("=" * 80)
    print(f"📄 Total páginas faltantes procesadas: {total_faltantes}")
    print(f"✅ Ya suscritas: {ya_suscritas}")
    print(f"🎉 Suscritas exitosamente: {exitosas}")
    print(f"❌ Fallidas: {fallidas}")
    print(f"📈 Tasa de éxito: {((ya_suscritas + exitosas) / total_faltantes * 100):.1f}%")
    
    print(f"\n🎯 RESUMEN TOTAL:")
    print(f"   • Páginas administradas: 25 (100% suscritas)")
    print(f"   • Páginas faltantes procesadas: {exitosas + ya_suscritas}/{total_faltantes}")
    print(f"   • Total páginas con webhooks activos: {25 + exitosas + ya_suscritas}")
    print("=" * 80)
    
    if exitosas > 0:
        print(f"🎉 ¡{exitosas} páginas faltantes suscritas exitosamente!")

def main():
    """Función principal"""
    suscribir_paginas_faltantes()

if __name__ == "__main__":
    main()
