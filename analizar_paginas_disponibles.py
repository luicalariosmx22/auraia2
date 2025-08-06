#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para analizar cuáles páginas funcionan vs cuáles fallan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

load_dotenv()

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    return os.getenv('META_ACCESS_TOKEN')

def obtener_paginas_disponibles_token():
    """Obtiene las páginas disponibles con el token actual"""
    access_token = obtener_access_token()
    if not access_token:
        return []
    
    try:
        url = "https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            return [p['id'] for p in pages if p.get('access_token')]
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo páginas: {e}")
        return []

def obtener_paginas_base_datos():
    """Obtiene todas las páginas de la base de datos"""
    try:
        resultado = supabase.table('facebook_paginas').select('page_id, nombre_pagina, estado_webhook').eq('activa', True).execute()
        return resultado.data
    except Exception as e:
        print(f"❌ Error obteniendo páginas de BD: {e}")
        return []

def main():
    """Función principal para analizar diferencias"""
    print("🔍 ANÁLISIS DE PÁGINAS: DISPONIBLES vs BASE DE DATOS")
    print("=" * 70)
    
    # Obtener páginas disponibles con el token
    paginas_token = obtener_paginas_disponibles_token()
    print(f"✅ Páginas disponibles con el token: {len(paginas_token)}")
    
    # Obtener páginas de la base de datos
    paginas_bd = obtener_paginas_base_datos()
    print(f"📋 Páginas en base de datos: {len(paginas_bd)}")
    
    # Crear sets para comparación
    set_token = set(paginas_token)
    set_bd = set([p['page_id'] for p in paginas_bd])
    
    # Páginas que FUNCIONAN (están en ambos)
    funcionan = set_token.intersection(set_bd)
    
    # Páginas que FALLAN (están en BD pero NO en token)
    fallan = set_bd - set_token
    
    print(f"\n📊 RESULTADOS:")
    print(f"✅ Páginas que FUNCIONAN: {len(funcionan)}")
    print(f"❌ Páginas que FALLAN: {len(fallan)}")
    
    # Mostrar páginas que funcionan
    print(f"\n🟢 PÁGINAS QUE FUNCIONAN ({len(funcionan)}):")
    for page_id in sorted(funcionan):
        # Buscar nombre en BD
        for p in paginas_bd:
            if p['page_id'] == page_id:
                estado = p.get('estado_webhook', 'desconocido')
                emoji = "✅" if estado == 'activa' else "🔄" if estado == 'pausada' else "❓"
                print(f"  {emoji} {p['nombre_pagina']} (ID: {page_id})")
                break
    
    # Mostrar páginas que fallan
    print(f"\n🔴 PÁGINAS QUE FALLAN ({len(fallan)}):")
    for page_id in sorted(fallan):
        # Buscar nombre en BD
        for p in paginas_bd:
            if p['page_id'] == page_id:
                print(f"  ❌ {p['nombre_pagina']} (ID: {page_id})")
                break
    
    print(f"\n💡 RESUMEN:")
    print(f"  • De {len(paginas_bd)} páginas en total, {len(funcionan)} pueden usar webhooks")
    print(f"  • {len(fallan)} páginas no están disponibles con el token actual")
    print(f"  • Tasa de éxito: {(len(funcionan)/len(paginas_bd)*100):.1f}%")

if __name__ == "__main__":
    main()
