import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
print(f"Token encontrado: {'✅' if token else '❌'}")

if token:
    try:
        url = 'https://graph.facebook.com/v19.0/me/permissions'
        response = requests.get(url, params={'access_token': token})
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            permisos = data.get('data', [])
            
            print(f"\n📋 PERMISOS ENCONTRADOS ({len(permisos)}):")
            for p in permisos:
                status = '✅' if p['status'] == 'granted' else '❌'
                print(f"{status} {p['permission']}")
                
            # Verificar permisos específicos para webhooks
            necesarios = ['pages_manage_metadata', 'pages_messaging']
            print(f"\n🎯 PERMISOS PARA WEBHOOKS:")
            for permiso in necesarios:
                tiene = any(p['permission'] == permiso and p['status'] == 'granted' for p in permisos)
                status = '✅' if tiene else '❌'
                print(f"{status} {permiso}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No se encontró token")
