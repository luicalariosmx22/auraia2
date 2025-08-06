import os
import requests
from dotenv import load_dotenv

load_dotenv()

user_token = os.getenv('META_ACCESS_TOKEN')
print(f"User Token encontrado: {'✅' if user_token else '❌'}")

if user_token:
    try:
        # 1. Obtener las páginas y sus tokens
        url = f"https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': user_token,
            'fields': 'id,name,access_token,tasks'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            print(f"\n📋 PÁGINAS ENCONTRADAS: {len(pages)}")
            
            if pages:
                # Tomar la primera página como ejemplo
                primera_pagina = pages[0]
                page_id = primera_pagina.get('id')
                page_name = primera_pagina.get('name')
                page_token = primera_pagina.get('access_token')
                
                print(f"\n🔍 ANÁLISIS DE LA PRIMERA PÁGINA:")
                print(f"   Nombre: {page_name}")
                print(f"   ID: {page_id}")
                print(f"   Tareas: {primera_pagina.get('tasks', [])}")
                print(f"   Tiene Page Token: {'✅' if page_token else '❌'}")
                
                if page_token:
                    # 2. Verificar permisos del Page Token
                    print(f"\n🔍 VERIFICANDO PERMISOS DEL PAGE TOKEN...")
                    perm_url = f"https://graph.facebook.com/v19.0/me/permissions"
                    perm_response = requests.get(perm_url, params={'access_token': page_token}, timeout=10)
                    
                    if perm_response.status_code == 200:
                        permisos = perm_response.json().get('data', [])
                        print(f"   Permisos del Page Token: {len(permisos)}")
                        
                        necesarios = ['pages_manage_metadata', 'pages_messaging']
                        for permiso in necesarios:
                            tiene = any(p['permission'] == permiso and p['status'] == 'granted' for p in permisos)
                            status = '✅' if tiene else '❌'
                            print(f"   {status} {permiso}")
                            
                    else:
                        print(f"   ❌ Error verificando permisos del Page Token: {perm_response.status_code}")
                        
                    # 3. Intentar suscribir webhook SIN campos específicos (solo la app)
                    print(f"\n🧪 PROBANDO SUSCRIPCIÓN BÁSICA (sin campos)...")
                    webhook_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
                    webhook_data = {
                        'access_token': page_token
                        # NO incluir subscribed_fields
                    }
                    
                    webhook_response = requests.post(webhook_url, data=webhook_data, timeout=10)
                    print(f"   Status: {webhook_response.status_code}")
                    
                    if webhook_response.status_code == 200:
                        result = webhook_response.json()
                        print(f"   ✅ Suscripción básica exitosa: {result}")
                    else:
                        print(f"   ❌ Error en suscripción básica: {webhook_response.text}")
                        
            else:
                print("❌ No se encontraron páginas")
        else:
            print(f"❌ Error obteniendo páginas: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No se encontró token de usuario")
