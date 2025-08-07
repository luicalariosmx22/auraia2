#!/usr/bin/env python3
"""
Script para verificar y aclarar las variables de Meta
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 VERIFICACIÓN DE VARIABLES META")
print("=" * 50)

app_secret = os.getenv('META_APP_SECRET')
webhook_secret = os.getenv('META_WEBHOOK_SECRET')  
access_token = os.getenv('META_ACCESS_TOKEN')
app_id = os.getenv('META_APP_ID')
verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')

print(f"📱 META_APP_ID: {app_id if app_id else '❌ No configurado'}")
print(f"🔐 META_APP_SECRET: {app_secret[:10] + '...' if app_secret else '❌ No configurado'}")
print(f"🔑 META_WEBHOOK_SECRET: {webhook_secret}")
print(f"🎟️ META_WEBHOOK_VERIFY_TOKEN: {verify_token}")
print(f"🔗 META_ACCESS_TOKEN: {access_token[:20] + '...' if access_token else '❌ No configurado'}")

print(f"\n🧮 LONGITUDES:")
print(f"   App Secret: {len(app_secret) if app_secret else 0} caracteres")
print(f"   Webhook Secret: {len(webhook_secret) if webhook_secret else 0} caracteres")
print(f"   Access Token: {len(access_token) if access_token else 0} caracteres")

print(f"\n📝 ARCHIVOS .env ENCONTRADOS:")
env_files = ['.env', '.env.local', '.env.railway']
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"   ✅ {env_file}")
        # Leer META_WEBHOOK_SECRET de cada archivo
        with open(env_file, 'r') as f:
            content = f.read()
            if 'META_WEBHOOK_SECRET=' in content:
                for line in content.split('\n'):
                    if line.startswith('META_WEBHOOK_SECRET='):
                        secret_in_file = line.split('=', 1)[1]
                        print(f"      SECRET: {secret_in_file}")
    else:
        print(f"   ❌ {env_file}")

print(f"\n💡 DIAGNÓSTICO:")
print("-" * 30)
if webhook_secret:
    print(f"✅ META_WEBHOOK_SECRET está configurado: '{webhook_secret}'")
    print(f"📏 Longitud: {len(webhook_secret)} caracteres")
    
    if len(webhook_secret) < 8:
        print("⚠️ PROBLEMA: El secret es muy corto, debería tener al menos 8 caracteres")
    
    if webhook_secret == '1002ivimyH!':
        print("🔍 Estás usando el secret por defecto")
else:
    print("❌ META_WEBHOOK_SECRET no está configurado")

print(f"\n📋 PASOS PARA CORREGIR:")
print("1. Ve a https://developers.facebook.com/apps/")
print("2. Selecciona tu app > Webhooks")
print("3. Verifica cuál es el 'Webhook Secret' configurado")
print("4. Asegúrate de que coincida exactamente con META_WEBHOOK_SECRET")
