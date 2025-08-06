#!/usr/bin/env python3
"""
Análisis de la confusión Usuario vs Página
Basado en la información del Debug Token
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
ID_LUICA = "1669696123329079"  # El mismo ID que vimos en el debug

def verificar_que_es_este_id():
    """Verificar si este ID es usuario o página"""
    print("=" * 70)
    print("🔍 VERIFICANDO QUÉ TIPO DE ENTIDAD ES 1669696123329079")
    print("=" * 70)
    
    # Intentar acceder como usuario
    print("\n👤 Intentando acceder como USUARIO:")
    url_user = f"https://graph.facebook.com/v21.0/{ID_LUICA}?fields=id,name,first_name,last_name&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_user)
        user_data = response.json()
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Respuesta como USUARIO:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Nombre: {user_data.get('name')}")
            print(f"   Primer nombre: {user_data.get('first_name')}")
            print(f"   Apellido: {user_data.get('last_name')}")
        else:
            print(f"❌ Error como usuario: {user_data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Intentar acceder como página
    print("\n📄 Intentando acceder como PÁGINA:")
    url_page = f"https://graph.facebook.com/v21.0/{ID_LUICA}?fields=id,name,category,fan_count,about&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_page)
        page_data = response.json()
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Respuesta como PÁGINA:")
            print(f"   ID: {page_data.get('id')}")
            print(f"   Nombre: {page_data.get('name')}")
            print(f"   Categoría: {page_data.get('category')}")
            print(f"   Seguidores: {page_data.get('fan_count')}")
            print(f"   Acerca de: {page_data.get('about', 'No disponible')}")
        else:
            print(f"❌ Error como página: {page_data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def verificar_tipo_de_token():
    """Verificar qué tipo de token tenemos"""
    print("\n" + "=" * 70)
    print("🔑 ANALIZANDO EL TOKEN ACTUAL")
    print("=" * 70)
    
    # Verificar información del token
    url_debug = f"https://graph.facebook.com/v21.0/debug_token?input_token={META_ACCESS_TOKEN}&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_debug)
        debug_data = response.json()
        
        if response.status_code == 200:
            token_info = debug_data.get('data', {})
            print("🔍 Información del token:")
            print(f"   App ID: {token_info.get('app_id')}")
            print(f"   Tipo: {token_info.get('type')}")
            print(f"   Usuario ID: {token_info.get('user_id')}")
            print(f"   Válido: {token_info.get('is_valid')}")
            print(f"   Expira: {token_info.get('expires_at')}")
            print(f"   Scopes: {', '.join(token_info.get('scopes', []))}")
        else:
            print(f"❌ Error debug token: {debug_data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def verificar_me_endpoint():
    """Verificar qué devuelve /me"""
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO ENDPOINT /me")
    print("=" * 70)
    
    url_me = f"https://graph.facebook.com/v21.0/me?fields=id,name,first_name,last_name,email&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_me)
        me_data = response.json()
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Información de /me:")
            print(f"   ID: {me_data.get('id')}")
            print(f"   Nombre: {me_data.get('name')}")
            print(f"   Primer nombre: {me_data.get('first_name')}")
            print(f"   Apellido: {me_data.get('last_name')}")
            print(f"   Email: {me_data.get('email', 'No disponible')}")
            
            # Comparar IDs
            me_id = me_data.get('id')
            if me_id == ID_LUICA:
                print(f"🎯 ¡MATCH! El token /me tiene el mismo ID que Luica Larios")
            else:
                print(f"❓ DIFERENTE: /me ID ({me_id}) ≠ Luica Larios ID ({ID_LUICA})")
        else:
            print(f"❌ Error en /me: {me_data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def buscar_pages_del_usuario_actual():
    """Buscar páginas del usuario actual del token"""
    print("\n" + "=" * 70)
    print("📋 PÁGINAS DEL USUARIO ACTUAL DEL TOKEN")
    print("=" * 70)
    
    # Obtener ID del usuario actual
    url_me = f"https://graph.facebook.com/v21.0/me?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_me)
        me_data = response.json()
        
        if response.status_code == 200:
            current_user_id = me_data.get('id')
            current_user_name = me_data.get('name')
            
            print(f"👤 Usuario actual del token: {current_user_name} (ID: {current_user_id})")
            
            # Buscar páginas de este usuario
            url_accounts = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
            response_accounts = requests.get(url_accounts)
            accounts_data = response_accounts.json()
            
            if response_accounts.status_code == 200:
                pages = accounts_data.get('data', [])
                print(f"\n📊 Total páginas administradas por {current_user_name}: {len(pages)}")
                
                # Buscar si hay alguna página relacionada con "Luica Larios"
                luica_related = []
                for page in pages:
                    page_name = page.get('name', '').lower()
                    if 'luica' in page_name or 'larios' in page_name or page.get('id') == ID_LUICA:
                        luica_related.append(page)
                
                if luica_related:
                    print(f"\n🎯 Páginas relacionadas con Luica Larios:")
                    for page in luica_related:
                        print(f"   📄 {page.get('name')} (ID: {page.get('id')})")
                else:
                    print(f"\n❌ No se encontraron páginas relacionadas con 'Luica Larios'")
                    print(f"   Buscando en {len(pages)} páginas administradas")
            else:
                print(f"❌ Error obteniendo accounts: {accounts_data}")
        else:
            print(f"❌ Error obteniendo usuario actual: {me_data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🔍 ANÁLISIS: CONFUSIÓN USUARIO vs PÁGINA")
    print("=" * 80)
    print("Basado en el Debug Token que muestra:")
    print("- Usuario: Luica Larios")
    print("- ID: 1669696123329079")
    print("- Página: Luica Larios")
    print("=" * 80)
    
    # 1. Verificar qué tipo de entidad es este ID
    verificar_que_es_este_id()
    
    # 2. Analizar el token
    verificar_tipo_de_token()
    
    # 3. Verificar /me
    verificar_me_endpoint()
    
    # 4. Buscar páginas del usuario actual
    buscar_pages_del_usuario_actual()
    
    print("\n" + "=" * 80)
    print("💡 CONCLUSIONES POSIBLES:")
    print("1. Si /me ID = Luica Larios ID → Token de cuenta personal")
    print("2. Si /me ID ≠ Luica Larios ID → Token de otra cuenta")
    print("3. Puede ser confusión entre perfil personal y página")
    print("4. Necesitamos token de la cuenta que administra la página")
    print("=" * 80)

if __name__ == "__main__":
    main()
