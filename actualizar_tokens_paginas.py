#!/usr/bin/env python3
"""
Script para actualizar/poblar los tokens de acceso de las páginas de Facebook.

Este script:
1. Obtiene todas las páginas activas sin token o con token inválido
2. Usa el token principal de Meta para obtener tokens específicos de página
3. Actualiza la tabla facebook_paginas con los nuevos tokens

Uso:
    python actualizar_tokens_paginas.py
"""

import os
import sys
import requests
import json
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def obtener_token_principal():
    """Obtiene el token principal de Meta desde las variables de entorno."""
    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        print("❌ ERROR: No se encontró META_ACCESS_TOKEN en las variables de entorno")
        return None
    return token

def obtener_paginas_sin_token():
    """Obtiene todas las páginas activas que no tienen token o tienen token inválido."""
    try:
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, access_token, access_token_valido") \
            .eq("activa", True) \
            .execute()
        
        paginas_sin_token = []
        for pagina in response.data or []:
            # Página sin token o con token marcado como inválido
            if not pagina.get('access_token') or not pagina.get('access_token_valido', True):
                paginas_sin_token.append(pagina)
        
        print(f"✅ Encontradas {len(paginas_sin_token)} páginas que necesitan token")
        return paginas_sin_token
        
    except Exception as e:
        print(f"❌ ERROR obteniendo páginas sin token: {str(e)}")
        return []

def obtener_token_pagina_desde_meta(page_id, token_principal):
    """
    Obtiene el token específico de una página usando el token principal.
    
    Args:
        page_id (str): ID de la página
        token_principal (str): Token principal de la aplicación Meta
        
    Returns:
        str: Token de la página o None si hay error
    """
    try:
        print(f"🔍 Obteniendo token para página {page_id}...")
        
        # Primero verificar que tenemos acceso a la página
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'access_token': token_principal,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            page_token = data.get('access_token')
            page_name = data.get('name', 'Sin nombre')
            
            if page_token:
                print(f"✅ Token obtenido para página '{page_name}' ({page_id})")
                return page_token
            else:
                print(f"⚠️ No se pudo obtener token para página '{page_name}' ({page_id})")
                return None
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Error obteniendo token para página {page_id}: {response.status_code}")
            print(f"   Detalles: {error_data}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR obteniendo token para página {page_id}: {str(e)}")
        return None

def actualizar_token_en_bd(page_id, token):
    """
    Actualiza el token de una página en la base de datos.
    
    Args:
        page_id (str): ID de la página
        token (str): Token de acceso de la página
    """
    try:
        response = supabase.table("facebook_paginas") \
            .update({
                "access_token": token,
                "access_token_valido": True,
                "actualizado_en": datetime.now().isoformat(),
                "ultima_sincronizacion": datetime.now().isoformat()
            }) \
            .eq("page_id", page_id) \
            .execute()
        
        print(f"✅ Token actualizado en BD para página {page_id}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR actualizando token en BD para página {page_id}: {str(e)}")
        return False

def validar_token_pagina(page_id, token):
    """
    Valida que el token de página funciona correctamente.
    
    Args:
        page_id (str): ID de la página
        token (str): Token de acceso de la página
        
    Returns:
        bool: True si el token es válido
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'access_token': token,
            'fields': 'id,name'
        }
        
        response = requests.get(url, params=params, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ ERROR validando token para página {page_id}: {str(e)}")
        return False

def main():
    """Función principal del script."""
    print("🚀 Iniciando actualización de tokens de páginas de Facebook...")
    
    # Obtener token principal
    token_principal = obtener_token_principal()
    if not token_principal:
        return
    
    print(f"✅ Token principal encontrado")
    
    # Obtener páginas que necesitan token
    paginas_sin_token = obtener_paginas_sin_token()
    if not paginas_sin_token:
        print("✅ Todas las páginas activas ya tienen tokens válidos")
        return
    
    # Procesar cada página
    exitosos = 0
    fallidos = 0
    
    for pagina in paginas_sin_token:
        page_id = pagina['page_id']
        nombre_pagina = pagina.get('nombre_pagina', 'Sin nombre')
        
        print(f"\n📄 Procesando página '{nombre_pagina}' ({page_id})...")
        
        # Obtener token de la página
        page_token = obtener_token_pagina_desde_meta(page_id, token_principal)
        
        if page_token:
            # Validar que el token funciona
            if validar_token_pagina(page_id, page_token):
                # Actualizar en base de datos
                if actualizar_token_en_bd(page_id, page_token):
                    exitosos += 1
                    print(f"✅ Página '{nombre_pagina}' actualizada exitosamente")
                else:
                    fallidos += 1
                    print(f"❌ Error actualizando página '{nombre_pagina}' en BD")
            else:
                fallidos += 1
                print(f"❌ Token obtenido para '{nombre_pagina}' no es válido")
        else:
            fallidos += 1
            print(f"❌ No se pudo obtener token para página '{nombre_pagina}'")
    
    # Resumen final
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Exitosos: {exitosos}")
    print(f"   ❌ Fallidos: {fallidos}")
    print(f"   📄 Total procesados: {len(paginas_sin_token)}")
    
    if exitosos > 0:
        print(f"\n🎉 Se actualizaron {exitosos} páginas con nuevos tokens")
    
    print("🏁 Proceso completado")

if __name__ == "__main__":
    main()
