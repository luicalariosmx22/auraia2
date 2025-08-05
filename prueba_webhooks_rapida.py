#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prueba corregida de registro de webhooks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

def registrar_webhook_simple():
    """Función simple corregida para registrar webhooks"""
    print("🧪 PRUEBA CORREGIDA DE WEBHOOKS META ADS")
    print("=" * 50)
    
    # Obtener token desde variables de entorno
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        print("💡 Agrega a tu .env: META_ACCESS_TOKEN=tu_token_aqui")
        return
    
    print("✅ Access token encontrado")
    
    try:
        # Importar SDK de Facebook
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        
        print("✅ Facebook Business SDK disponible")
        
        # Inicializar API
        FacebookAdsApi.init(access_token=access_token)
        print("✅ API inicializada")
        
        # Probar con una cuenta específica
        print("\n🎯 PRUEBA CON UNA CUENTA ESPECÍFICA")
        account_id = input("Ingresa el ID de cuenta (ej: 3113286718820966): ").strip()
        
        if not account_id:
            print("❌ No se ingresó ID de cuenta")
            return
        
        # Asegurarse de que tenga el formato correcto
        if account_id.startswith('act_'):
            account_id = account_id[4:]  # Quitar el prefijo si ya lo tiene
        
        formatted_account_id = f"act_{account_id}"
        
        print(f"� Probando con: {formatted_account_id}")
        
        try:
            # Crear objeto de cuenta
            cuenta = AdAccount(formatted_account_id)
            
            # Método correcto para suscribir app
            response = cuenta.create_subscribed_app()
            
            print(f"✅ Webhook registrado exitosamente!")
            print(f"📋 Respuesta: {response}")
            
        except Exception as e:
            print(f"❌ Error específico: {e}")
            
            # Intentar método alternativo
            try:
                print("🔄 Intentando método alternativo...")
                
                # Usar requests directamente con la API de Graph
                import requests
                
                url = f"https://graph.facebook.com/v19.0/{formatted_account_id}/subscribed_apps"
                headers = {'Authorization': f'Bearer {access_token}'}
                
                response = requests.post(url, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ Método alternativo exitoso!")
                    print(f"📋 Respuesta: {response.json()}")
                else:
                    print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
            except Exception as e2:
                print(f"❌ También falló método alternativo: {e2}")
                
                # Verificar si ya está suscrito
                try:
                    print("🔍 Verificando suscripciones existentes...")
                    
                    url = f"https://graph.facebook.com/v19.0/{formatted_account_id}/subscribed_apps"
                    headers = {'Authorization': f'Bearer {access_token}'}
                    
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        apps = data.get('data', [])
                        print(f"📱 Apps suscritas: {len(apps)}")
                        
                        if apps:
                            for i, app in enumerate(apps, 1):
                                print(f"   {i}. App ID: {app.get('id', 'N/A')}")
                                print(f"      Link: {app.get('link', 'N/A')}")
                            print("✅ El webhook ya podría estar registrado")
                        else:
                            print("❌ No hay apps suscritas")
                    else:
                        print(f"❌ Error verificando HTTP {response.status_code}: {response.text}")
                        
                except Exception as e3:
                    print(f"❌ Error verificando: {e3}")
        
    except ImportError:
        print("❌ Facebook Business SDK no está instalado")
        print("💡 Instala con: pip install facebook-business")
    except Exception as e:
        print(f"❌ Error general: {e}")

def main():
    """Función principal simplificada"""
    registrar_webhook_simple()
    print("\n✨ Prueba completada!")

if __name__ == "__main__":
    main()
