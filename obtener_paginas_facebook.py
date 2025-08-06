#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para obtener todas las páginas de Facebook que administras
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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
    
    # URL de la API de Meta para obtener páginas
    url = "https://graph.facebook.com/v19.0/me/accounts"
    
    params = {
        'access_token': access_token,
        'fields': 'id,name,category,category_list,access_token,tasks,fan_count,followers_count,link,verification_status,is_verified,username,website',
        'limit': 100  # Meta permite hasta 100 por página
    }
    
    todas_las_paginas = []
    
    try:
        while url:
            print(f"📡 Consultando API: {url.split('?')[0]}...")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                paginas = data.get('data', [])
                todas_las_paginas.extend(paginas)
                
                print(f"✅ Obtenidas {len(paginas)} páginas en esta consulta")
                
                # Verificar si hay más páginas (paginación)
                paging = data.get('paging', {})
                url = paging.get('next')
                params = None  # Los parámetros ya están en la URL next
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                break
        
        return todas_las_paginas
        
    except Exception as e:
        print(f"❌ Error obteniendo páginas: {e}")
        return []

def mostrar_paginas(paginas):
    """Muestra información detallada de las páginas"""
    if not paginas:
        print("❌ No se encontraron páginas")
        return
    
    print(f"\n📋 PÁGINAS DE FACEBOOK ENCONTRADAS: {len(paginas)}")
    print("=" * 80)
    
    for i, pagina in enumerate(paginas, 1):
        print(f"\n{i}. 📄 {pagina.get('name', 'Sin nombre')}")
        print(f"   🆔 ID: {pagina.get('id')}")
        print(f"   🏷️ Categoría: {pagina.get('category', 'Sin categoría')}")
        
        # Información adicional
        fan_count = pagina.get('fan_count', 'N/A')
        followers_count = pagina.get('followers_count', 'N/A')
        print(f"   👥 Fans: {fan_count} | Seguidores: {followers_count}")
        
        # Verificación
        is_verified = pagina.get('is_verified', False)
        verification_status = pagina.get('verification_status', 'N/A')
        print(f"   ✅ Verificada: {is_verified} | Estado: {verification_status}")
        
        # Enlaces
        link = pagina.get('link', 'N/A')
        website = pagina.get('website', 'N/A')
        username = pagina.get('username', 'N/A')
        print(f"   🔗 Link: {link}")
        print(f"   🌐 Website: {website}")
        print(f"   📱 Username: @{username}")
        
        # Permisos/tareas que tienes en la página
        tasks = pagina.get('tasks', [])
        if tasks:
            print(f"   🔑 Permisos: {', '.join(tasks)}")
        
        # Categorías adicionales
        category_list = pagina.get('category_list', [])
        if category_list:
            categorias = [cat.get('name', '') for cat in category_list]
            print(f"   🏷️ Categorías: {', '.join(categorias)}")

def guardar_en_supabase(paginas):
    """Guarda las páginas en Supabase (opcional)"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from clientes.aura.utils.supabase_client import supabase
        
        print(f"\n💾 ¿Deseas guardar las {len(paginas)} páginas en Supabase? (s/N): ", end="")
        respuesta = input().strip().lower()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            # Crear tabla si no existe
            tabla_sql = """
            CREATE TABLE IF NOT EXISTS facebook_paginas (
                id VARCHAR PRIMARY KEY,
                nombre VARCHAR,
                categoria VARCHAR,
                access_token VARCHAR,
                fan_count INTEGER,
                followers_count INTEGER,
                link VARCHAR,
                website VARCHAR,
                username VARCHAR,
                is_verified BOOLEAN,
                verification_status VARCHAR,
                permisos TEXT[],
                creado_en TIMESTAMP DEFAULT NOW(),
                actualizado_en TIMESTAMP DEFAULT NOW()
            );
            """
            print("📋 Creando tabla facebook_paginas...")
            
            for pagina in paginas:
                datos_pagina = {
                    'id': pagina.get('id'),
                    'nombre': pagina.get('name'),
                    'categoria': pagina.get('category'),
                    'access_token': pagina.get('access_token'),
                    'fan_count': pagina.get('fan_count'),
                    'followers_count': pagina.get('followers_count'),
                    'link': pagina.get('link'),
                    'website': pagina.get('website'),
                    'username': pagina.get('username'),
                    'is_verified': pagina.get('is_verified', False),
                    'verification_status': pagina.get('verification_status'),
                    'permisos': pagina.get('tasks', [])
                }
                
                # Insertar o actualizar
                result = supabase.table('facebook_paginas').upsert(datos_pagina).execute()
                print(f"✅ Guardada: {pagina.get('name')}")
            
            print(f"✅ {len(paginas)} páginas guardadas en Supabase")
        else:
            print("❌ No se guardaron las páginas")
            
    except Exception as e:
        print(f"❌ Error guardando en Supabase: {e}")

def exportar_a_csv(paginas):
    """Exporta las páginas a un archivo CSV"""
    try:
        import csv
        from datetime import datetime
        
        filename = f"facebook_paginas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'nombre', 'categoria', 'fan_count', 'followers_count',
                'link', 'website', 'username', 'is_verified', 'verification_status',
                'permisos'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for pagina in paginas:
                row = {
                    'id': pagina.get('id'),
                    'nombre': pagina.get('name'),
                    'categoria': pagina.get('category'),
                    'fan_count': pagina.get('fan_count'),
                    'followers_count': pagina.get('followers_count'),
                    'link': pagina.get('link'),
                    'website': pagina.get('website'),
                    'username': pagina.get('username'),
                    'is_verified': pagina.get('is_verified'),
                    'verification_status': pagina.get('verification_status'),
                    'permisos': ', '.join(pagina.get('tasks', []))
                }
                writer.writerow(row)
        
        print(f"📄 Páginas exportadas a: {filename}")
        
    except Exception as e:
        print(f"❌ Error exportando CSV: {e}")

def main():
    """Función principal"""
    print("🚀 OBTENER PÁGINAS DE FACEBOOK")
    print("=" * 50)
    
    # Obtener access token
    access_token = obtener_access_token()
    if not access_token:
        return
    
    print("✅ Access token configurado")
    
    # Obtener páginas
    paginas = obtener_paginas_facebook(access_token)
    
    if paginas:
        # Mostrar páginas
        mostrar_paginas(paginas)
        
        # Opciones adicionales
        print("\n" + "=" * 50)
        print("📋 OPCIONES ADICIONALES:")
        print("1. 💾 Guardar en Supabase")
        print("2. 📄 Exportar a CSV")
        print("3. ❌ Salir")
        
        while True:
            try:
                opcion = input("\nSelecciona una opción (1-3): ").strip()
                
                if opcion == '1':
                    guardar_en_supabase(paginas)
                    break
                elif opcion == '2':
                    exportar_a_csv(paginas)
                    break
                elif opcion == '3':
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción no válida. Selecciona 1-3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Operación cancelada")
                break
    else:
        print("❌ No se pudieron obtener las páginas")

if __name__ == "__main__":
    main()
