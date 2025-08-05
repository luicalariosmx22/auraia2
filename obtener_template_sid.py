#!/usr/bin/env python3
"""
Obtener el SID del template de Twilio para usar en las notificaciones
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Agregar el directorio raíz al path para poder importar
sys.path.append(os.getcwd())

from twilio.rest import Client

def obtener_templates():
    """Listar todos los Content Templates disponibles"""
    
    # Configuración de Twilio
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not all([twilio_sid, twilio_token]):
        print("❌ Credenciales de Twilio no configuradas")
        return
    
    client = Client(twilio_sid, twilio_token)
    
    try:
        print("📋 Obteniendo templates de Twilio...")
        
        # Listar content templates
        contents = client.content.contents.list()
        
        if not contents:
            print("❌ No se encontraron templates")
            return
        
        print(f"✅ Encontrados {len(contents)} templates:")
        print("-" * 60)
        
        for content in contents:
            print(f"📄 Nombre: {content.friendly_name}")
            print(f"   SID: {content.sid}")
            print(f"   Tipo: {content.content_type if hasattr(content, 'content_type') else 'N/A'}")
            print(f"   Estado: {content.approval_requests[0].status if content.approval_requests else 'N/A'}")
            print("-" * 60)
            
            # Si encontramos el template de alerta_sistema, guardar su SID
            if content.friendly_name == 'alerta_sistema':
                print(f"🎯 Template alerta_sistema encontrado!")
                print(f"   SID para usar en código: {content.sid}")
                return content.sid
        
    except Exception as e:
        print(f"❌ Error al obtener templates: {e}")
        return None

if __name__ == "__main__":
    sid = obtener_templates()
    if sid:
        print(f"\n🔧 Usar este SID en notificaciones.py:")
        print(f"   content_sid='{sid}'")
    else:
        print("\n⚠️ No se encontró el template alerta_sistema")
        print("   Verifica que el template esté creado y aprobado en Twilio")
