#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para suscribir webhooks en todas las páginas de Facebook
Similar al sistema de Meta Ads pero para Facebook Pages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from datetime import datetime
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# Cargar variables de entorno
load_dotenv()

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN en las variables de entorno")
        print("💡 Configura tu token con:")
        print("   export META_ACCESS_TOKEN='tu_token_aqui'")
        return None
    
    return access_token

def obtener_webhook_url():
    """Obtiene la URL del webhook desde variables de entorno"""
    webhook_url = os.getenv('META_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ No se encontró META_WEBHOOK_URL en las variables de entorno")
        print("💡 Ejemplo: META_WEBHOOK_URL='https://tu-dominio.com/meta/webhook'")
        return None
    
    return webhook_url

def obtener_verify_token():
    """Obtiene el verify token desde variables de entorno"""
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    if not verify_token:
        print("❌ No se encontró META_WEBHOOK_VERIFY_TOKEN en las variables de entorno")
        print("💡 Ejemplo: META_WEBHOOK_VERIFY_TOKEN='tu_verify_token_secreto'")
        return None
    
    return verify_token

def obtener_page_access_token(page_id, user_access_token):
    """
    Obtiene el Page Access Token para una página específica
    
    Args:
        page_id (str): ID de la página de Facebook
        user_access_token (str): User Access Token
        
    Returns:
        str: Page Access Token o None si hay error
    """
    try:
        url = f"https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': user_access_token,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            # Buscar la página específica
            for page in pages:
                if page.get('id') == page_id:
                    return page.get('access_token')
            
            print(f"⚠️ No se encontró Page Access Token para página {page_id}")
            return None
        else:
            print(f"❌ Error obteniendo Page Access Token: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo Page Access Token para {page_id}: {e}")
        return None

def suscribir_webhook_pagina(page_id, user_access_token, webhook_url, verify_token):
    """
    Suscribe webhook para una página específica de Facebook
    
    Args:
        page_id (str): ID de la página de Facebook
        user_access_token (str): User Access Token de Meta
        webhook_url (str): URL del webhook endpoint
        verify_token (str): Token de verificación
        
    Returns:
        dict: Resultado de la suscripción
    """
    try:
        print(f"📡 Suscribiendo webhook para página: {page_id}")
        
        # Primero obtener el Page Access Token
        page_access_token = obtener_page_access_token(page_id, user_access_token)
        
        if not page_access_token:
            return {
                'success': False,
                'page_id': page_id,
                'error': 'No se pudo obtener Page Access Token'
            }
        
        print(f"✅ Page Access Token obtenido para página {page_id}")
        
        # URL para suscribir webhook en la página
        url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        
        # Datos de la suscripción - usando campos básicos que no requieren permisos especiales
        # Empezamos con campos básicos que deberían funcionar con los permisos actuales
        data = {
            'access_token': page_access_token,
            'subscribed_fields': 'feed'  # Empezar solo con feed que es el más básico
        }
        
        # Realizar la suscripción
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print(f"✅ Webhook suscrito exitosamente para página {page_id}")
                return {
                    'success': True,
                    'page_id': page_id,
                    'message': 'Webhook suscrito correctamente'
                }
            else:
                print(f"⚠️ Respuesta inesperada para página {page_id}: {result}")
                return {
                    'success': False,
                    'page_id': page_id,
                    'error': 'Respuesta inesperada de la API'
                }
        else:
            try:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
                if isinstance(error_data, dict) and 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_msg = error_data['error'].get('message', response.text)
                    else:
                        error_msg = str(error_data['error'])
                else:
                    error_msg = response.text
            except:
                error_msg = response.text
            
            print(f"❌ Error suscribiendo webhook para página {page_id}: {response.status_code}")
            print(f"   Detalles: {error_data}")
            return {
                'success': False,
                'page_id': page_id,
                'error': f"HTTP {response.status_code}: {error_msg}"
            }
            
    except requests.exceptions.Timeout:
        error_msg = f"Timeout suscribiendo webhook para página {page_id}"
        print(f"⏰ {error_msg}")
        return {
            'success': False,
            'page_id': page_id,
            'error': 'Timeout en la solicitud'
        }
    except Exception as e:
        error_msg = f"Error inesperado suscribiendo webhook para página {page_id}: {e}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'page_id': page_id,
            'error': str(e)
        }

def verificar_webhook_pagina(page_id, user_access_token):
    """
    Verifica si una página tiene webhooks suscritos
    
    Args:
        page_id (str): ID de la página de Facebook
        user_access_token (str): User Access Token de Meta
        
    Returns:
        bool: True si tiene webhooks suscritos
    """
    try:
        # Obtener Page Access Token
        page_access_token = obtener_page_access_token(page_id, user_access_token)
        
        if not page_access_token:
            print(f"⚠️ No se pudo obtener Page Access Token para verificar página {page_id}")
            return False
        
        url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        
        params = {
            'access_token': page_access_token  # Usar Page Access Token
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            apps = data.get('data', [])
            
            # Verificar si nuestra app está en la lista
            app_id = os.getenv('META_APP_ID')
            if app_id:
                for app in apps:
                    if app.get('id') == app_id:
                        return True
            
            # Si no hay APP_ID configurado, asumir que está suscrito si hay apps
            return len(apps) > 0
        else:
            print(f"⚠️ Error verificando webhook para página {page_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando webhook para página {page_id}: {e}")
        return False

def obtener_paginas_facebook():
    """
    Obtiene todas las páginas de Facebook desde la base de datos
    
    Returns:
        list: Lista de páginas de Facebook
    """
    try:
        print("🔍 Obteniendo páginas de Facebook desde base de datos...")
        
        # Obtener todas las páginas activas
        resultado = supabase.table('facebook_paginas').select('page_id, nombre_pagina, estado_webhook, activa').eq('activa', True).execute()
        
        if not resultado.data:
            print("❌ No se encontraron páginas de Facebook en la base de datos")
            return []
        
        paginas = resultado.data
        print(f"✅ Se encontraron {len(paginas)} páginas activas")
        
        return paginas
        
    except Exception as e:
        print(f"❌ Error obteniendo páginas de Facebook: {e}")
        return []

def actualizar_estado_webhook_pagina(page_id, webhook_suscrito):
    """
    Actualiza el estado del webhook de una página en la base de datos
    
    Args:
        page_id (str): ID de la página
        webhook_suscrito (bool): Si el webhook está suscrito
    """
    try:
        estado = 'activa' if webhook_suscrito else 'pausada'
        
        resultado = supabase.table('facebook_paginas').update({
            'estado_webhook': estado,
            'actualizado_en': datetime.utcnow().isoformat()
        }).eq('page_id', page_id).execute()
        
        if resultado.data:
            print(f"✅ Estado actualizado para página {page_id}: {estado}")
        else:
            print(f"⚠️ No se pudo actualizar estado para página {page_id}")
            
    except Exception as e:
        print(f"❌ Error actualizando estado para página {page_id}: {e}")

def suscribir_webhooks_masivo():
    """
    Suscribe webhooks en todas las páginas de Facebook activas
    
    Returns:
        dict: Estadísticas del proceso
    """
    print("🚀 SUSCRIPCIÓN MASIVA DE WEBHOOKS PARA FACEBOOK PAGES")
    print("=" * 60)
    
    # Verificar tokens y configuración
    access_token = obtener_access_token()
    if not access_token:
        return {'error': 'Access token no configurado'}
    
    webhook_url = obtener_webhook_url()
    if not webhook_url:
        return {'error': 'Webhook URL no configurada'}
    
    verify_token = obtener_verify_token()
    if not verify_token:
        return {'error': 'Verify token no configurado'}
    
    print(f"✅ Access token configurado")
    print(f"✅ Webhook URL: {webhook_url}")
    print(f"✅ Verify token configurado")
    
    # Obtener páginas
    paginas = obtener_paginas_facebook()
    if not paginas:
        return {'error': 'No se encontraron páginas para procesar'}
    
    # Filtrar páginas que no requieren suscripción
    paginas_a_suscribir = [p for p in paginas if p.get('estado_webhook') != 'excluida']
    
    print(f"\n📊 Páginas a procesar: {len(paginas_a_suscribir)}")
    print(f"📊 Páginas excluidas: {len(paginas) - len(paginas_a_suscribir)}")
    
    # Estadísticas
    exitosos = 0
    fallidos = 0
    ya_suscritos = 0
    resultados = []
    
    print(f"\n🔄 Procesando páginas...")
    
    for i, pagina in enumerate(paginas_a_suscribir, 1):
        page_id = pagina['page_id']
        nombre_pagina = pagina['nombre_pagina']
        
        print(f"\n[{i}/{len(paginas_a_suscribir)}] Procesando: {nombre_pagina}")
        print(f"   📋 Page ID: {page_id}")
        
        # Verificar si ya está suscrito
        ya_suscrito = verificar_webhook_pagina(page_id, access_token)
        
        if ya_suscrito:
            print(f"   ✅ Ya tiene webhook suscrito")
            ya_suscritos += 1
            actualizar_estado_webhook_pagina(page_id, True)
            continue
        
        # Suscribir webhook
        resultado = suscribir_webhook_pagina(page_id, access_token, webhook_url, verify_token)
        resultados.append(resultado)
        
        if resultado['success']:
            exitosos += 1
            actualizar_estado_webhook_pagina(page_id, True)
            print(f"   ✅ Suscripción exitosa")
        else:
            fallidos += 1
            actualizar_estado_webhook_pagina(page_id, False)
            print(f"   ❌ Error: {resultado['error']}")
    
    # Resumen final
    print(f"\n" + "=" * 60)
    print(f"📊 RESUMEN DE SUSCRIPCIÓN MASIVA")
    print(f"=" * 60)
    print(f"✅ Exitosos: {exitosos}")
    print(f"🔄 Ya suscritos: {ya_suscritos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📋 Total procesadas: {len(paginas_a_suscribir)}")
    print(f"⏱️ Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'exitosos': exitosos,
        'ya_suscritos': ya_suscritos,
        'fallidos': fallidos,
        'total': len(paginas_a_suscribir),
        'resultados': resultados
    }

def verificar_estado_todas_paginas():
    """
    Verifica el estado de webhooks en todas las páginas
    
    Returns:
        dict: Estado de todas las páginas
    """
    print("🔍 VERIFICACIÓN DE ESTADO DE WEBHOOKS")
    print("=" * 50)
    
    access_token = obtener_access_token()
    if not access_token:
        return {'error': 'Access token no configurado'}
    
    paginas = obtener_paginas_facebook()
    if not paginas:
        return {'error': 'No se encontraron páginas'}
    
    print(f"📋 Verificando {len(paginas)} páginas...")
    
    suscritas = 0
    no_suscritas = 0
    errores = 0
    
    for pagina in paginas:
        page_id = pagina['page_id']
        nombre_pagina = pagina['nombre_pagina']
        
        print(f"\n🔍 {nombre_pagina} ({page_id})")
        
        try:
            suscrito = verificar_webhook_pagina(page_id, access_token)
            
            if suscrito:
                print(f"   ✅ Webhook suscrito")
                suscritas += 1
                actualizar_estado_webhook_pagina(page_id, True)
            else:
                print(f"   ❌ Webhook NO suscrito")
                no_suscritas += 1
                actualizar_estado_webhook_pagina(page_id, False)
                
        except Exception as e:
            print(f"   ⚠️ Error verificando: {e}")
            errores += 1
    
    print(f"\n" + "=" * 50)
    print(f"📊 RESUMEN DE VERIFICACIÓN")
    print(f"=" * 50)
    print(f"✅ Suscritas: {suscritas}")
    print(f"❌ No suscritas: {no_suscritas}")
    print(f"⚠️ Errores: {errores}")
    print(f"📋 Total: {len(paginas)}")
    
    return {
        'suscritas': suscritas,
        'no_suscritas': no_suscritas,
        'errores': errores,
        'total': len(paginas)
    }

def suscribir_pagina_especifica():
    """
    Suscribe webhook en una página específica (modo interactivo)
    """
    print("📡 SUSCRIPCIÓN DE WEBHOOK EN PÁGINA ESPECÍFICA")
    print("=" * 50)
    
    access_token = obtener_access_token()
    if not access_token:
        return
    
    webhook_url = obtener_webhook_url()
    if not webhook_url:
        return
    
    verify_token = obtener_verify_token()
    if not verify_token:
        return
    
    # Mostrar páginas disponibles
    paginas = obtener_paginas_facebook()
    if not paginas:
        return
    
    print(f"\n📋 Páginas disponibles:")
    for i, pagina in enumerate(paginas, 1):
        estado = "🟢" if pagina.get('estado_webhook') == 'activa' else "🔴" if pagina.get('estado_webhook') == 'pausada' else "🟡"
        print(f"{i:2d}. {estado} {pagina['nombre_pagina']} (ID: {pagina['page_id']})")
    
    try:
        seleccion = input(f"\nSelecciona una página (1-{len(paginas)}) o 'q' para salir: ").strip()
        
        if seleccion.lower() == 'q':
            return
        
        indice = int(seleccion) - 1
        if 0 <= indice < len(paginas):
            pagina = paginas[indice]
            page_id = pagina['page_id']
            nombre_pagina = pagina['nombre_pagina']
            
            print(f"\n🎯 Suscribiendo webhook para: {nombre_pagina}")
            
            resultado = suscribir_webhook_pagina(page_id, access_token, webhook_url, verify_token)
            
            if resultado['success']:
                print(f"✅ ¡Webhook suscrito exitosamente!")
                actualizar_estado_webhook_pagina(page_id, True)
            else:
                print(f"❌ Error: {resultado['error']}")
                actualizar_estado_webhook_pagina(page_id, False)
        else:
            print("❌ Selección inválida")
            
    except ValueError:
        print("❌ Por favor ingresa un número válido")
    except KeyboardInterrupt:
        print("\n👋 Operación cancelada")

def menu_principal():
    """Muestra el menú principal de opciones"""
    print("\n" + "="*60)
    print("📡 GESTIÓN DE WEBHOOKS PARA FACEBOOK PAGES")
    print("="*60)
    print("1. 🚀 Suscribir webhooks en TODAS las páginas")
    print("2. 🔍 Verificar estado de todas las páginas")
    print("3. 📡 Suscribir webhook en página específica")
    print("4. 📊 Ver estadísticas de páginas")
    print("5. ❌ Salir")
    print("="*60)

def mostrar_estadisticas():
    """Muestra estadísticas de las páginas"""
    print("📊 ESTADÍSTICAS DE FACEBOOK PAGES")
    print("=" * 40)
    
    try:
        # Estadísticas generales
        total = supabase.table('facebook_paginas').select('*').execute()
        activas = supabase.table('facebook_paginas').select('*').eq('activa', True).execute()
        webhook_activo = supabase.table('facebook_paginas').select('*').eq('estado_webhook', 'activa').execute()
        webhook_pausado = supabase.table('facebook_paginas').select('*').eq('estado_webhook', 'pausada').execute()
        webhook_excluido = supabase.table('facebook_paginas').select('*').eq('estado_webhook', 'excluida').execute()
        
        print(f"📋 Total páginas: {len(total.data)}")
        print(f"✅ Páginas activas: {len(activas.data)}")
        print(f"🟢 Webhooks activos: {len(webhook_activo.data)}")
        print(f"🔴 Webhooks pausados: {len(webhook_pausado.data)}")
        print(f"⚫ Webhooks excluidos: {len(webhook_excluido.data)}")
        
        # Top páginas por seguidores
        print(f"\n🏆 TOP 10 PÁGINAS POR SEGUIDORES:")
        top_paginas = supabase.table('facebook_paginas').select('nombre_pagina, seguidores').order('seguidores', desc=True).limit(10).execute()
        
        for i, pagina in enumerate(top_paginas.data, 1):
            seguidores = pagina.get('seguidores', 0)
            nombre = pagina.get('nombre_pagina', 'Sin nombre')
            print(f"{i:2d}. {nombre:<40} {seguidores:>10,} seguidores")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando gestor de webhooks para Facebook Pages...")
    
    while True:
        menu_principal()
        
        try:
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                print("\n🚀 Iniciando suscripción masiva...")
                resultado = suscribir_webhooks_masivo()
                
                if 'error' in resultado:
                    print(f"❌ Error: {resultado['error']}")
                else:
                    print(f"\n✅ Proceso completado exitosamente!")
                
                input("\nPresiona Enter para continuar...")
                
            elif opcion == '2':
                print("\n🔍 Verificando estado de páginas...")
                resultado = verificar_estado_todas_paginas()
                
                if 'error' in resultado:
                    print(f"❌ Error: {resultado['error']}")
                    
                input("\nPresiona Enter para continuar...")
                
            elif opcion == '3':
                suscribir_pagina_especifica()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == '4':
                mostrar_estadisticas()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("\n❌ Opción no válida. Por favor selecciona 1-5.")
                input("Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
