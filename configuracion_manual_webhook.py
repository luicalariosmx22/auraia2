#!/usr/bin/env python3
"""
Guía para configurar webhook manualmente desde Facebook Developer Console
Ya que la API tiene restricciones, vamos a hacerlo manualmente
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_APP_ID = os.getenv('META_APP_ID')
WEBHOOK_URL = os.getenv('META_WEBHOOK_URL')
WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
LUICA_PAGE_TOKEN = "EAAPJAAprGjgBPCW28xufZC72i8ZBx0Uketfrexpch7lNZB9igZCw5f5itJwpAhNIlvHitZAupkTKjkakIrOZB3mn0MzH3WqguwcqlQH53qyZBKSN94BPPVGEBYia8A5Soq9TS3MuQlNqEY5U6YggNJj5hx9ZCTKJotpNFoVdlZCoPrZCyUhMZA3nuGhWVIxkUhfGXBUYpZA6"

def mostrar_configuracion_manual():
    """Mostrar la configuración manual paso a paso"""
    print("🛠️ CONFIGURACIÓN MANUAL DE WEBHOOK EN FACEBOOK DEVELOPER CONSOLE")
    print("=" * 80)
    
    print("\n📱 INFORMACIÓN DE TU APLICACIÓN:")
    print(f"   App ID: {META_APP_ID}")
    print(f"   Webhook URL: {WEBHOOK_URL}")
    print(f"   Verify Token: {WEBHOOK_VERIFY_TOKEN}")
    
    print("\n🔗 PASOS PARA CONFIGURAR MANUALMENTE:")
    print("=" * 50)
    
    print("\n1️⃣ ACCEDE A FACEBOOK DEVELOPER CONSOLE:")
    print("   🌐 https://developers.facebook.com/apps/")
    print(f"   📱 Selecciona tu aplicación (ID: {META_APP_ID})")
    
    print("\n2️⃣ NAVEGA A WEBHOOKS:")
    print("   📋 Productos > Webhooks")
    print("   O directo: https://developers.facebook.com/apps/{}/webhooks/".format(META_APP_ID))
    
    print("\n3️⃣ CONFIGURA EL WEBHOOK:")
    print("   📡 Callback URL:", WEBHOOK_URL)
    print("   🔐 Verify Token:", WEBHOOK_VERIFY_TOKEN)
    print("   📋 Subscription Fields: feed")
    
    print("\n4️⃣ SUSCRIBE LA PÁGINA:")
    print("   👤 En la sección 'Page'")
    print("   🔗 Hacer clic en 'Subscribe to this object'")
    print("   📄 Buscar y seleccionar: Luica Larios")
    print("   ✅ Suscribir a los campos: feed")
    
    print("\n5️⃣ VERIFICAR SUSCRIPCIÓN:")
    print("   📊 Deberías ver 'Luica Larios' en la lista de páginas suscritas")
    print("   ✅ Estado: Active")
    
    print("\n" + "=" * 80)

def verificar_webhook_endpoint():
    """Verificar que nuestro endpoint esté funcionando"""
    print("\n🔍 VERIFICACIÓN DEL ENDPOINT WEBHOOK")
    print("=" * 50)
    
    import requests
    
    # Simular verificación de Facebook
    params = {
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge_123',
        'hub.verify_token': WEBHOOK_VERIFY_TOKEN
    }
    
    try:
        print(f"🌐 Probando endpoint: {WEBHOOK_URL}")
        print(f"🔐 Con verify token: {WEBHOOK_VERIFY_TOKEN}")
        
        response = requests.get(WEBHOOK_URL, params=params)
        
        print(f"\n📊 Resultado:")
        print(f"   Status: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        
        if response.status_code == 200 and response.text == 'test_challenge_123':
            print("✅ ¡Endpoint funcionando correctamente!")
        else:
            print("❌ Endpoint no responde correctamente")
            print("💡 Asegúrate de que tu servidor esté corriendo")
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {str(e)}")

def mostrar_codigo_verificacion():
    """Mostrar el código de verificación para el webhook"""
    print("\n📝 CÓDIGO DE VERIFICACIÓN DEL WEBHOOK")
    print("=" * 50)
    
    print("""
Asegúrate de que tu servidor tenga este código para manejar la verificación:

```python
@app.route('/meta/webhook', methods=['GET'])
def webhook_verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == 'nora123':
        return challenge
    else:
        return 'Forbidden', 403

@app.route('/meta/webhook', methods=['POST'])
def webhook_receive():
    data = request.get_json()
    
    # Procesar eventos de Facebook Pages
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            page_id = entry.get('id')
            changes = entry.get('changes', [])
            
            for change in changes:
                if change.get('field') == 'feed':
                    # Nuevo post en la página
                    print(f"Nuevo evento en página {page_id}")
    
    return 'EVENT_RECEIVED', 200
```
""")

def actualizar_base_datos_manual():
    """Función para actualizar manualmente la base de datos después de configurar"""
    print("\n💾 ACTUALIZACIÓN MANUAL DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        from supabase.client import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Credenciales de Supabase no encontradas")
            return
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Actualizar estado de la página Luica Larios
        result = supabase.table('facebook_paginas').update({
            'webhook_estado': 'activa'
        }).eq('page_id', '1669696123329079').execute()
        
        if result.data:
            print("✅ Estado actualizado en base de datos:")
            print("   Página: Luica Larios")
            print("   Estado: activa")
            print("   ID: 1669696123329079")
        else:
            print("❌ Error actualizando base de datos")
            
    except Exception as e:
        print(f"❌ Error con base de datos: {str(e)}")

def main():
    """Función principal"""
    mostrar_configuracion_manual()
    verificar_webhook_endpoint()
    mostrar_codigo_verificacion()
    
    print("\n🎯 DESPUÉS DE CONFIGURAR MANUALMENTE:")
    print("Ejecuta esta función para actualizar la base de datos:")
    actualizar_base_datos_manual()
    
    print("\n" + "=" * 80)
    print("📞 RESUMEN:")
    print("1. Configura el webhook manualmente en Facebook Developer Console")
    print("2. Suscribe la página 'Luica Larios' al campo 'feed'")
    print("3. Verifica que el endpoint responda correctamente")
    print("4. La base de datos se actualizará automáticamente")
    print("=" * 80)

if __name__ == "__main__":
    main()
