#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar permisos del token de Meta
y qué se puede hacer con el token actual
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_permisos_token():
    """Verifica los permisos del token actual"""
    print("🔍 VERIFICACIÓN DE PERMISOS DEL TOKEN META")
    print("=" * 50)
    
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN en las variables de entorno")
        return
    
    try:
        # Verificar permisos del token
        url = 'https://graph.facebook.com/v19.0/me/permissions'
        response = requests.get(url, params={'access_token': token}, timeout=10)
        
        if response.status_code == 200:
            permisos = response.json().get('data', [])
            
            print(f"📋 PERMISOS ACTUALES DEL TOKEN:")
            print("-" * 30)
            
            permisos_concedidos = []
            permisos_denegados = []
            
            for permiso in permisos:
                if permiso['status'] == 'granted':
                    permisos_concedidos.append(permiso['permission'])
                    print(f"✅ {permiso['permission']}")
                else:
                    permisos_denegados.append(permiso['permission'])
                    print(f"❌ {permiso['permission']} - {permiso['status']}")
            
            print(f"\n🔍 PERMISOS NECESARIOS PARA WEBHOOKS:")
            print("-" * 35)
            
            permisos_webhook = [
                'pages_manage_metadata',  # Para feed, mention, videos, website
                'pages_messaging',        # Para messages, message_reads, messaging_referrals
                'pages_show_list',        # Para listar páginas
                'pages_read_engagement'   # Para leer engagement
            ]
            
            for permiso in permisos_webhook:
                tiene = permiso in permisos_concedidos
                status = '✅' if tiene else '❌'
                descripcion = {
                    'pages_manage_metadata': 'Gestionar metadatos de páginas (feed, mention, videos, website)',
                    'pages_messaging': 'Mensajería de páginas (messages, message_reads, messaging_referrals)',
                    'pages_show_list': 'Listar páginas administradas',
                    'pages_read_engagement': 'Leer engagement de páginas'
                }.get(permiso, permiso)
                
                print(f"{status} {permiso}")
                print(f"   {descripcion}")
            
            # Resumen
            permisos_ok = sum(1 for p in permisos_webhook if p in permisos_concedidos)
            print(f"\n📊 RESUMEN:")
            print(f"✅ Permisos concedidos: {len(permisos_concedidos)}")
            print(f"❌ Permisos denegados: {len(permisos_denegados)}")
            print(f"🎯 Permisos para webhooks: {permisos_ok}/{len(permisos_webhook)}")
            
            if permisos_ok == len(permisos_webhook):
                print(f"\n🎉 ¡TIENES TODOS LOS PERMISOS NECESARIOS!")
                print(f"   Puedes suscribir webhooks sin problemas")
            else:
                print(f"\n⚠️ FALTAN PERMISOS PARA WEBHOOKS")
                faltantes = [p for p in permisos_webhook if p not in permisos_concedidos]
                print(f"   Permisos faltantes: {', '.join(faltantes)}")
                print(f"   Necesitas renovar el token con más permisos")
            
            return permisos_concedidos
            
        else:
            print(f"❌ Error verificando permisos: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def verificar_acceso_paginas():
    """Verifica a qué páginas tienes acceso"""
    print(f"\n🔍 VERIFICACIÓN DE ACCESO A PÁGINAS")
    print("=" * 40)
    
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    try:
        url = 'https://graph.facebook.com/v19.0/me/accounts'
        params = {
            'access_token': token,
            'fields': 'id,name,access_token,tasks'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            print(f"📋 PÁGINAS ACCESIBLES: {len(pages)}")
            print("-" * 25)
            
            if not pages:
                print("❌ No tienes acceso a ninguna página")
                print("   Verifica que tu token tenga permisos de páginas")
                return
            
            for i, page in enumerate(pages[:5], 1):  # Mostrar solo las primeras 5
                print(f"{i}. {page.get('name', 'Sin nombre')}")
                print(f"   ID: {page.get('id')}")
                print(f"   Tareas: {', '.join(page.get('tasks', []))}")
                print(f"   Tiene Page Token: {'✅' if page.get('access_token') else '❌'}")
                print()
            
            if len(pages) > 5:
                print(f"... y {len(pages) - 5} páginas más")
            
            return pages
            
        else:
            print(f"❌ Error obteniendo páginas: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def verificar_configuracion_app():
    """Verifica la configuración de la aplicación"""
    print(f"\n🔍 VERIFICACIÓN DE CONFIGURACIÓN DE LA APP")
    print("=" * 45)
    
    app_id = os.getenv('META_APP_ID')
    token = os.getenv('META_ACCESS_TOKEN')
    webhook_url = os.getenv('META_WEBHOOK_URL')
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    print(f"📱 App ID: {'✅' if app_id else '❌'} {app_id if app_id else 'No configurado'}")
    print(f"🔑 Access Token: {'✅' if token else '❌'} {'Configurado' if token else 'No configurado'}")
    print(f"🌐 Webhook URL: {'✅' if webhook_url else '❌'} {webhook_url if webhook_url else 'No configurado'}")
    print(f"🔐 Verify Token: {'✅' if verify_token else '❌'} {'Configurado' if verify_token else 'No configurado'}")
    
    if token and app_id:
        try:
            # Verificar información de la app
            url = f'https://graph.facebook.com/v19.0/{app_id}'
            response = requests.get(url, params={'access_token': token}, timeout=10)
            
            if response.status_code == 200:
                app_info = response.json()
                print(f"\n📱 INFORMACIÓN DE LA APP:")
                print(f"   Nombre: {app_info.get('name', 'N/A')}")
                print(f"   ID: {app_info.get('id', 'N/A')}")
                print(f"   Categoría: {app_info.get('category', 'N/A')}")
            else:
                print(f"\n❌ No se pudo obtener info de la app: {response.status_code}")
                
        except Exception as e:
            print(f"\n❌ Error verificando app: {e}")

def verificar_campos_disponibles():
    """Verifica qué campos están disponibles en la app"""
    print(f"\n🔍 CAMPOS DISPONIBLES PARA WEBHOOKS")
    print("=" * 35)
    
    # Campos que tienes configurados según tu lista
    campos_configurados = [
        'feed', 'group_feed', 'mention', 'message_reads', 
        'messages', 'messaging_referrals', 'videos', 'website'
    ]
    
    print(f"📋 CAMPOS CONFIGURADOS EN TU APP:")
    for campo in campos_configurados:
        print(f"✅ {campo}")
    
    print(f"\n🎯 CAMPOS RECOMENDADOS PARA PÁGINAS:")
    campos_recomendados = [
        'feed',               # Publicaciones
        'mention',            # Menciones  
        'messages',           # Mensajes privados
        'message_reads',      # Lecturas de mensajes
        'messaging_referrals' # Referencias de mensajería
    ]
    
    for campo in campos_recomendados:
        disponible = campo in campos_configurados
        status = '✅' if disponible else '❌'
        print(f"{status} {campo}")

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO COMPLETO DE PERMISOS META")
    print("=" * 50)
    
    # 1. Verificar permisos del token
    permisos = verificar_permisos_token()
    
    # 2. Verificar acceso a páginas
    if permisos:
        paginas = verificar_acceso_paginas()
    
    # 3. Verificar configuración de la app
    verificar_configuracion_app()
    
    # 4. Verificar campos disponibles
    verificar_campos_disponibles()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 DIAGNÓSTICO COMPLETADO")
    print(f"=" * 50)

if __name__ == "__main__":
    main()
