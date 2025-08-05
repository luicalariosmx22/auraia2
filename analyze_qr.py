#!/usr/bin/env python3
"""
Script para analizar el QR generado y verificar si es válido
"""

import requests
import json
import base64
import io
from PIL import Image
import qrcode
import pyzbar.pyzbar as pyzbar

def analyze_qr_response():
    """Analizar la respuesta del QR del backend"""
    print("🔍 ANÁLISIS DEL QR GENERADO")
    print("=" * 50)
    
    # 1. Obtener QR del endpoint
    print("1️⃣ Obteniendo QR del endpoint...")
    try:
        response = requests.get("http://localhost:5000/panel_cliente/aura/whatsapp/qr")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta obtenida: {data.get('success', False)}")
            
            qr_data = data.get('qr_data', '')
            print(f"📱 QR Data tipo: {type(qr_data)}")
            print(f"📱 QR Data longitud: {len(qr_data)}")
            print(f"📱 QR Data inicio: {qr_data[:100]}...")
            
            # 2. Analizar el formato del QR
            print("\n2️⃣ Analizando formato del QR...")
            if qr_data.startswith('data:image/png;base64,'):
                print("✅ QR es imagen PNG en base64")
                
                # Decodificar la imagen
                base64_data = qr_data.split(',')[1]
                image_data = base64.b64decode(base64_data)
                
                # Guardar imagen para análisis
                with open('qr_test.png', 'wb') as f:
                    f.write(image_data)
                print("💾 QR guardado como qr_test.png")
                
                # Cargar imagen con PIL
                image = Image.open(io.BytesIO(image_data))
                print(f"🖼️ Imagen: {image.size}px, modo: {image.mode}")
                
                # 3. Intentar decodificar el QR
                print("\n3️⃣ Decodificando contenido del QR...")
                try:
                    decoded_objects = pyzbar.decode(image)
                    if decoded_objects:
                        for obj in decoded_objects:
                            qr_content = obj.data.decode('utf-8')
                            print(f"✅ QR decodificado exitosamente")
                            print(f"📄 Contenido: {qr_content[:200]}...")
                            
                            # 4. Verificar si es formato WhatsApp Web
                            print("\n4️⃣ Verificando formato WhatsApp Web...")
                            if validate_whatsapp_qr(qr_content):
                                print("✅ QR es válido para WhatsApp Web")
                            else:
                                print("❌ QR NO es válido para WhatsApp Web")
                                print("💡 Formato esperado: 1@...,.../...,+...")
                    else:
                        print("❌ No se pudo decodificar el QR")
                except Exception as e:
                    print(f"❌ Error decodificando QR: {e}")
                    
            elif qr_data.startswith('1@'):
                print("📱 QR es texto plano (formato WhatsApp Web)")
                print(f"📄 Contenido: {qr_data[:200]}...")
                
                if validate_whatsapp_qr(qr_data):
                    print("✅ QR texto es válido para WhatsApp Web")
                else:
                    print("❌ QR texto NO es válido para WhatsApp Web")
            else:
                print("❓ QR en formato desconocido")
                
        else:
            print(f"❌ Error obteniendo QR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def validate_whatsapp_qr(qr_content):
    """Validar si el QR tiene formato de WhatsApp Web"""
    try:
        # Formato típico: 1@XXX,YYY,ZZZ==,+PHONE
        if not qr_content.startswith('1@'):
            return False
            
        parts = qr_content.split(',')
        if len(parts) < 3:
            return False
            
        # Verificar que tenga los componentes básicos
        session_part = parts[0]  # 1@XXX
        ref_part = parts[1]      # YYY
        key_part = parts[2]      # ZZZ==
        
        # Verificaciones básicas
        if not session_part.startswith('1@'):
            return False
            
        if len(ref_part) < 10:
            return False
            
        if not key_part.endswith('=='):
            return False
            
        return True
        
    except Exception:
        return False

def test_qr_generation():
    """Probar generación de QR válido"""
    print("\n🧪 PRUEBA DE GENERACIÓN DE QR VÁLIDO")
    print("=" * 50)
    
    # Generar QR válido de prueba
    valid_qr = "1@9jKF8WzJ2nMLrtc1qGPKqg==,wA3kDTZouRaQfGH5qvZYGrBdDl8jLZHNYhKQKmJJyCI=,T6zXEAoIcFcMvNkPqTa4cg==,+5491234567890"
    
    print(f"📱 QR válido de prueba: {valid_qr}")
    print(f"✅ Validación: {validate_whatsapp_qr(valid_qr)}")
    
    # Generar imagen QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(valid_qr)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_valid_test.png")
    print("💾 QR válido guardado como qr_valid_test.png")

def check_backend_qr():
    """Verificar QR directamente del backend Railway"""
    print("\n🌐 VERIFICANDO QR DESDE BACKEND RAILWAY")
    print("=" * 50)
    
    # Probar conexión WebSocket directa para obtener QR
    import socketio
    import time
    
    try:
        sio = socketio.Client()
        qr_received = None
        
        @sio.event
        def connect():
            print("✅ Conectado al backend Railway")
            sio.emit('get_qr', {})
        
        @sio.event
        def qr_code(data):
            nonlocal qr_received
            qr_received = data
            print(f"📱 QR recibido del backend: {data}")
        
        print("🔗 Conectando al backend Railway...")
        sio.connect("https://whatsapp-server-production-8f61.up.railway.app")
        
        # Esperar respuesta
        time.sleep(5)
        
        if qr_received:
            qr_data = qr_received.get('qr_data', '')
            if qr_data.startswith('data:image/png;base64,'):
                print("✅ QR del backend es imagen PNG")
                
                # Decodificar y analizar
                base64_data = qr_data.split(',')[1]
                image_data = base64.b64decode(base64_data)
                
                with open('qr_backend_direct.png', 'wb') as f:
                    f.write(image_data)
                print("💾 QR del backend guardado como qr_backend_direct.png")
                
                # Intentar decodificar
                image = Image.open(io.BytesIO(image_data))
                decoded_objects = pyzbar.decode(image)
                
                if decoded_objects:
                    for obj in decoded_objects:
                        content = obj.data.decode('utf-8')
                        print(f"📄 Contenido QR del backend: {content[:200]}...")
                        print(f"✅ Válido para WhatsApp: {validate_whatsapp_qr(content)}")
                else:
                    print("❌ No se pudo decodificar QR del backend")
        else:
            print("❌ No se recibió QR del backend")
            
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Error probando backend: {e}")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        from PIL import Image
        import pyzbar.pyzbar as pyzbar
        import qrcode
        print("✅ Dependencias disponibles")
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("💡 Instalar con: pip install pillow pyzbar-py qrcode[pil]")
        exit(1)
    
    analyze_qr_response()
    test_qr_generation()
    check_backend_qr()
