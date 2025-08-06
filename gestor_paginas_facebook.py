#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para obtener todas las páginas de Facebook que administras
y almacenarlas en Supabase para usar con webhooks
"""

import sys
import os
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN en las variables de entorno")
        print("💡 Configura tu token con:")
        print("   export META_ACCESS_TOKEN='tu_token_aqui'")
        print("   # O en Windows:")
        print("   set META_ACCESS_TOKEN=tu_token_aqui")
        return None
    
    return access_token

def obtener_paginas_facebook(access_token):
    """Obtiene todas las páginas de Facebook que administras"""
    print("🔍 Obteniendo páginas de Facebook...")
    
    # Primero probar con campos básicos
    print("🧪 Probando permisos disponibles...")
    
    # URL para obtener páginas que administras
    url = "https://graph.facebook.com/v19.0/me/accounts"
    
    # Campos básicos que siempre deberían funcionar
    campos_basicos = 'id,name,category,fan_count,is_published,picture'
    
    # Campos que requieren permisos adicionales
    campos_avanzados = 'username,about,website,phone,emails,location,cover,verification_status'
    
    # Probar primero con campos básicos
    params_basicos = {
        'access_token': access_token,
        'fields': campos_basicos,
        'limit': 5  # Solo 5 para probar
    }
    
    try:
        print("📡 Probando campos básicos...")
        response = requests.get(url, params=params_basicos)
        if response.status_code == 200:
            print("✅ Campos básicos: OK")
            campos_disponibles = campos_basicos
        else:
            print(f"❌ Error con campos básicos: {response.status_code}")
            return []
        
        # Probar campos avanzados uno por uno
        print("🔍 Probando campos avanzados...")
        campos_extras = []
        
        for campo in campos_avanzados.split(','):
            test_params = {
                'access_token': access_token,
                'fields': f'id,{campo}',
                'limit': 1
            }
            
            test_response = requests.get(url, params=test_params)
            if test_response.status_code == 200:
                print(f"✅ {campo}: Disponible")
                campos_extras.append(campo)
            else:
                print(f"❌ {campo}: No disponible")
        
        # Combinar campos disponibles
        if campos_extras:
            campos_disponibles = f"{campos_basicos},{','.join(campos_extras)}"
        
        print(f"🎯 Campos finales a usar: {campos_disponibles}")
        
    except Exception as e:
        print(f"⚠️ Error probando permisos: {e}")
        campos_disponibles = campos_basicos
    
    # Ahora obtener todas las páginas con los campos disponibles
    params = {
        'access_token': access_token,
        'fields': campos_disponibles,
        'limit': 100  # Máximo por página
    }
    
    todas_paginas = []
    
    try:
        while url:
            print(f"📡 Consultando: {url}")
            response = requests.get(url, params=params if 'accounts' in url else None)
            
            if response.status_code != 200:
                print(f"❌ Error en API: {response.status_code}")
                print(f"Respuesta: {response.text}")
                break
            
            data = response.json()
            
            if 'data' not in data:
                print("❌ No se encontraron páginas en la respuesta")
                break
            
            paginas = data['data']
            todas_paginas.extend(paginas)
            
            print(f"📄 Encontradas {len(paginas)} páginas en esta consulta")
            
            # Verificar si hay más páginas
            url = data.get('paging', {}).get('next')
            params = None  # Los parámetros van en la URL next
        
        print(f"✅ Total páginas encontradas: {len(todas_paginas)}")
        return todas_paginas
        
    except Exception as e:
        print(f"❌ Error obteniendo páginas: {e}")
        return []

def procesar_pagina(pagina_data):
    """Procesa los datos de una página para insertarla en Supabase"""
    
    # Información básica (siempre disponible)
    page_id = pagina_data.get('id')
    nombre = pagina_data.get('name', 'Sin nombre')
    categoria = pagina_data.get('category', 'Sin categoría')
    seguidores = pagina_data.get('fan_count', 0)
    activa = pagina_data.get('is_published', True)
    
    # Información opcional (depende de permisos)
    username = pagina_data.get('username')
    descripcion = pagina_data.get('about')
    website = pagina_data.get('website')
    telefono = pagina_data.get('phone')
    
    # Email (puede ser array)
    emails = pagina_data.get('emails', [])
    email = emails[0] if emails and len(emails) > 0 else None
    
    # Ubicación (puede ser objeto complejo)
    location = pagina_data.get('location', {})
    if isinstance(location, dict):
        direccion = location.get('street')
        ciudad = location.get('city') 
        pais = location.get('country')
    else:
        direccion = ciudad = pais = None
    
    # Imágenes
    picture_data = pagina_data.get('picture', {})
    if isinstance(picture_data, dict) and 'data' in picture_data:
        foto_perfil_url = picture_data.get('data', {}).get('url')
    else:
        foto_perfil_url = None
    
    cover_data = pagina_data.get('cover', {})
    if isinstance(cover_data, dict):
        foto_portada_url = cover_data.get('source')
    else:
        foto_portada_url = None
    
    # Estado de verificación
    verification_status = pagina_data.get('verification_status')
    verificada = verification_status == 'blue_verified' if verification_status else False
    
    # Datos procesados con valores seguros
    datos_pagina = {
        'page_id': page_id,
        'nombre_pagina': nombre,
        'categoria': categoria,
        'seguidores': seguidores,
        'likes': seguidores,  # Facebook usa fan_count para ambos
        'activa': activa,
        'estado_webhook': 'activa',  # Por defecto activa
        'access_token_valido': True,
        'ultima_sincronizacion': datetime.utcnow().isoformat()
    }
    
    # Agregar campos opcionales solo si están disponibles
    if username:
        datos_pagina['username'] = username
    if descripcion:
        datos_pagina['descripcion'] = descripcion
    if website:
        datos_pagina['website'] = website
    if telefono:
        datos_pagina['telefono'] = telefono
    if email:
        datos_pagina['email'] = email
    if direccion:
        datos_pagina['direccion'] = direccion
    if ciudad:
        datos_pagina['ciudad'] = ciudad
    if pais:
        datos_pagina['pais'] = pais
    if foto_perfil_url:
        datos_pagina['foto_perfil_url'] = foto_perfil_url
    if foto_portada_url:
        datos_pagina['foto_portada_url'] = foto_portada_url
    if verification_status:
        datos_pagina['verificada'] = verificada
    
    return datos_pagina

def guardar_paginas_supabase(paginas_procesadas):
    """Guarda las páginas en Supabase"""
    print(f"\n💾 Guardando {len(paginas_procesadas)} páginas en Supabase...")
    
    if not existe('facebook_paginas'):
        print("❌ La tabla 'facebook_paginas' no existe")
        print("💡 Ejecuta primero: psql -f sql/crear_tabla_facebook_paginas.sql")
        return False
    
    insertadas = 0
    actualizadas = 0
    errores = 0
    
    for pagina in paginas_procesadas:
        try:
            page_id = pagina['page_id']
            
            # Verificar si ya existe
            resultado_busqueda = supabase.table('facebook_paginas').select('page_id').eq('page_id', page_id).execute()
            
            if resultado_busqueda.data:
                # Actualizar existente
                resultado = supabase.table('facebook_paginas').update(pagina).eq('page_id', page_id).execute()
                if resultado.data:
                    actualizadas += 1
                    print(f"🔄 Actualizada: {pagina['nombre_pagina']} ({page_id})")
                else:
                    errores += 1
                    print(f"❌ Error actualizando: {pagina['nombre_pagina']}")
            else:
                # Insertar nueva
                resultado = supabase.table('facebook_paginas').insert(pagina).execute()
                if resultado.data:
                    insertadas += 1
                    print(f"✅ Insertada: {pagina['nombre_pagina']} ({page_id})")
                else:
                    errores += 1
                    print(f"❌ Error insertando: {pagina['nombre_pagina']}")
                    
        except Exception as e:
            errores += 1
            print(f"❌ Error procesando {pagina.get('nombre_pagina', 'Página desconocida')}: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Insertadas: {insertadas}")
    print(f"   🔄 Actualizadas: {actualizadas}")
    print(f"   ❌ Errores: {errores}")
    
    return True

def mostrar_paginas_guardadas():
    """Muestra las páginas guardadas en Supabase"""
    print("\n📋 PÁGINAS GUARDADAS EN SUPABASE:")
    print("-" * 60)
    
    try:
        resultado = supabase.table('facebook_paginas').select('page_id, nombre_pagina, categoria, seguidores, estado_webhook, activa').order('nombre_pagina').execute()
        
        if not resultado.data:
            print("❌ No se encontraron páginas guardadas")
            return
        
        for i, pagina in enumerate(resultado.data, 1):
            estado_emoji = "✅" if pagina['activa'] else "❌"
            webhook_emoji = {"activa": "🟢", "pausada": "🟡", "excluida": "🔴"}.get(pagina['estado_webhook'], "⚪")
            
            print(f"{i:2d}. {estado_emoji} {pagina['nombre_pagina']}")
            print(f"     🆔 ID: {pagina['page_id']}")
            print(f"     📂 Categoría: {pagina.get('categoria', 'N/A')}")
            print(f"     👥 Seguidores: {pagina.get('seguidores', 0):,}")
            print(f"     {webhook_emoji} Webhook: {pagina['estado_webhook']}")
            print()
            
    except Exception as e:
        print(f"❌ Error obteniendo páginas: {e}")

def menu_principal():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("🏢 GESTOR DE PÁGINAS DE FACEBOOK")
    print("="*60)
    print("1. 📡 Obtener páginas de Facebook y guardar en BD")
    print("2. 📋 Ver páginas guardadas en BD")
    print("3. 🔧 Cambiar estado de webhook de una página")
    print("4. 📊 Estadísticas de páginas")
    print("5. ❌ Salir")
    print("="*60)

def cambiar_estado_pagina():
    """Permite cambiar el estado de webhook de una página"""
    print("\n🔧 CAMBIAR ESTADO DE WEBHOOK")
    print("-" * 40)
    
    try:
        # Mostrar páginas disponibles
        resultado = supabase.table('facebook_paginas').select('page_id, nombre_pagina, estado_webhook').order('nombre_pagina').execute()
        
        if not resultado.data:
            print("❌ No hay páginas registradas")
            return
        
        print("\nPáginas disponibles:")
        for i, pagina in enumerate(resultado.data, 1):
            estado_emoji = {"activa": "🟢", "pausada": "🟡", "excluida": "🔴"}.get(pagina['estado_webhook'], "⚪")
            print(f"{i}. {estado_emoji} {pagina['nombre_pagina']} ({pagina['page_id']})")
        
        # Seleccionar página
        try:
            seleccion = int(input(f"\nSelecciona una página (1-{len(resultado.data)}): ")) - 1
            if seleccion < 0 or seleccion >= len(resultado.data):
                print("❌ Selección inválida")
                return
            
            pagina_seleccionada = resultado.data[seleccion]
            
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            return
        
        # Mostrar opciones de estado
        print(f"\nEstados disponibles para: {pagina_seleccionada['nombre_pagina']}")
        print("1. 🟢 activa - Recibe webhooks normalmente")
        print("2. 🟡 pausada - Temporalmente sin webhooks")
        print("3. 🔴 excluida - Permanentemente excluida")
        
        try:
            estado_seleccion = int(input("Selecciona nuevo estado (1-3): "))
            estados = {1: 'activa', 2: 'pausada', 3: 'excluida'}
            
            if estado_seleccion not in estados:
                print("❌ Selección inválida")
                return
            
            nuevo_estado = estados[estado_seleccion]
            
            # Actualizar en BD
            resultado_update = supabase.table('facebook_paginas').update({
                'estado_webhook': nuevo_estado,
                'actualizado_en': datetime.utcnow().isoformat()
            }).eq('page_id', pagina_seleccionada['page_id']).execute()
            
            if resultado_update.data:
                emoji = {"activa": "🟢", "pausada": "🟡", "excluida": "🔴"}[nuevo_estado]
                print(f"✅ Estado actualizado: {pagina_seleccionada['nombre_pagina']} → {emoji} {nuevo_estado}")
            else:
                print("❌ Error actualizando estado")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_estadisticas():
    """Muestra estadísticas de las páginas"""
    print("\n📊 ESTADÍSTICAS DE PÁGINAS")
    print("-" * 40)
    
    try:
        resultado = supabase.table('facebook_paginas').select('estado_webhook, activa, seguidores, verificada').execute()
        
        if not resultado.data:
            print("❌ No hay páginas registradas")
            return
        
        total = len(resultado.data)
        activas = len([p for p in resultado.data if p['activa']])
        inactivas = total - activas
        
        # Estados de webhook
        estados_webhook = {}
        for pagina in resultado.data:
            estado = pagina['estado_webhook']
            estados_webhook[estado] = estados_webhook.get(estado, 0) + 1
        
        # Verificadas
        verificadas = len([p for p in resultado.data if p['verificada']])
        
        # Seguidores totales
        seguidores_total = sum(p.get('seguidores', 0) for p in resultado.data)
        
        print(f"📈 Total páginas: {total}")
        print(f"✅ Activas: {activas}")
        print(f"❌ Inactivas: {inactivas}")
        print(f"🔵 Verificadas: {verificadas}")
        print(f"👥 Seguidores totales: {seguidores_total:,}")
        
        print(f"\n🎯 Estados de webhook:")
        for estado, cantidad in estados_webhook.items():
            emoji = {"activa": "🟢", "pausada": "🟡", "excluida": "🔴"}.get(estado, "⚪")
            print(f"   {emoji} {estado}: {cantidad}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando gestor de páginas de Facebook...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener access token
    access_token = obtener_access_token()
    if not access_token:
        return
    
    print("✅ Access token configurado")
    
    while True:
        menu_principal()
        
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                # Obtener y guardar páginas
                paginas = obtener_paginas_facebook(access_token)
                if paginas:
                    paginas_procesadas = [procesar_pagina(p) for p in paginas]
                    guardar_paginas_supabase(paginas_procesadas)
                    mostrar_paginas_guardadas()
                else:
                    print("❌ No se pudieron obtener páginas")
                    
            elif opcion == '2':
                mostrar_paginas_guardadas()
                
            elif opcion == '3':
                cambiar_estado_pagina()
                
            elif opcion == '4':
                mostrar_estadisticas()
                
            elif opcion == '5':
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Por favor selecciona 1-5.")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
