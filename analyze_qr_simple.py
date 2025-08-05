#!/usr/bin/env python3
"""
Script simplificado para analizar el QR generado
"""

import requests
import json
import base64
import io
from PIL import Image
import qrcode

def analyze_qr_simple():
    """Analizar QR de forma simplificada"""
    print("🔍 ANÁLISIS SIMPLIFICADO DEL QR")
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
            
            # 2. Analizar formato
            print("\n2️⃣ Analizando formato...")
            if qr_data.startswith('data:image/png;base64,'):
                print("✅ QR es imagen PNG en base64")
                
                # Decodificar imagen
                base64_data = qr_data.split(',')[1]
                image_data = base64.b64decode(base64_data)
                
                # Guardar imagen
                with open('qr_analysis.png', 'wb') as f:
                    f.write(image_data)
                print("💾 QR guardado como qr_analysis.png")
                
                # Verificar imagen
                image = Image.open(io.BytesIO(image_data))
                print(f"🖼️ Imagen: {image.size}px, modo: {image.mode}")
                
                # 3. Verificar si es un QR válido visualmente
                print("\n3️⃣ Verificación visual...")
                if image.size[0] > 200 and image.size[1] > 200:
                    print("✅ Tamaño de imagen adecuado para QR")
                else:
                    print("⚠️ Imagen pequeña, puede no ser QR válido")
                    
            elif qr_data.startswith('1@'):
                print("📱 QR es texto plano")
                print(f"📄 Contenido: {qr_data}")
                
                # Verificar formato WhatsApp
                if validate_whatsapp_format(qr_data):
                    print("✅ Formato WhatsApp Web válido")
                else:
                    print("❌ Formato WhatsApp Web inválido")
                    
            else:
                print("❓ Formato desconocido")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def validate_whatsapp_format(qr_content):
    """Validar formato de WhatsApp Web"""
    try:
        # Formato: 1@XXX,YYY,ZZZ==,+PHONE
        if not qr_content.startswith('1@'):
            print("❌ No comienza con '1@'")
            return False
            
        parts = qr_content.split(',')
        print(f"📋 Partes del QR: {len(parts)}")
        
        if len(parts) < 3:
            print("❌ Muy pocas partes (necesita al menos 3)")
            return False
            
        # Verificar cada parte
        session_part = parts[0]  # 1@XXX
        ref_part = parts[1]      # YYY  
        key_part = parts[2]      # ZZZ==
        
        print(f"   - Sesión: {session_part[:20]}...")
        print(f"   - Referencia: {ref_part[:20]}...")
        print(f"   - Clave: {key_part[:20]}...")
        
        if not session_part.startswith('1@'):
            print("❌ Parte de sesión inválida")
            return False
            
        if len(ref_part) < 10:
            print("❌ Referencia muy corta")
            return False
            
        if len(key_part) < 10:
            print("❌ Clave muy corta")
            return False
            
        print("✅ Formato básico parece correcto")
        return True
        
    except Exception as e:
        print(f"❌ Error validando: {e}")
        return False

def check_backend_direct():
    """Verificar backend directamente"""
    print("\n🌐 VERIFICANDO BACKEND RAILWAY DIRECTO")
    print("=" * 50)
    
    try:
        import socketio
        import time
        
        sio = socketio.Client()
        qr_received = None
        
        @sio.event
        def connect():
            print("✅ Conectado al backend")
            sio.emit('get_qr', {})
        
        @sio.event
        def qr_code(data):
            nonlocal qr_received
            qr_received = data
            print(f"📱 QR recibido: {data.get('message', 'Sin mensaje')}")
        
        print("🔗 Conectando...")
        sio.connect("https://whatsapp-server-production-8f61.up.railway.app")
        
        time.sleep(5)
        
        if qr_received:
            qr_data = qr_received.get('qr_data', '')
            if qr_data:
                print(f"📱 QR directo longitud: {len(qr_data)}")
                print(f"📱 QR directo inicio: {qr_data[:50]}...")
                
                if qr_data.startswith('data:image/png;base64,'):
                    print("✅ Backend genera imagen PNG válida")
                    
                    # Guardar imagen del backend
                    base64_data = qr_data.split(',')[1]
                    image_data = base64.b64decode(base64_data)
                    
                    with open('qr_backend_direct.png', 'wb') as f:
                        f.write(image_data)
                    print("💾 QR del backend guardado como qr_backend_direct.png")
                    
                    # Verificar tamaño
                    image = Image.open(io.BytesIO(image_data))
                    print(f"🖼️ Imagen del backend: {image.size}px")
                    
                    return True
                else:
                    print("❌ Backend no genera imagen válida")
                    return False
            else:
                print("❌ No hay datos de QR")
                return False
        else:
            print("❌ No se recibió QR del backend")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_valid_whatsapp_qr():
    """Crear un QR válido de WhatsApp para prueba"""
    print("\n🧪 CREANDO QR VÁLIDO DE PRUEBA")
    print("=" * 50)
    
    # Formato real de WhatsApp Web
    valid_content = "1@9jKF8WzJ2nMLrtc1qGPKqg==,wA3kDTZouRaQfGH5qvZYGrBdDl8jLZHNYhKQKmJJyCI=,T6zXEAoIcFcMvNkPqTa4cg==,+5491234567890"
    
    print(f"📄 Contenido válido: {valid_content}")
    print(f"✅ Validación: {validate_whatsapp_format(valid_content)}")
    
    # Crear QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(valid_content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_valid_example.png")
    print("💾 QR válido guardado como qr_valid_example.png")
    
    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    print(f"📱 Base64 longitud: {len(img_str)}")
    print("✅ QR válido creado exitosamente")
    
    return f"data:image/png;base64,{img_str}"

if __name__ == "__main__":
    analyze_qr_simple()
    
    # Verificar backend directo
    backend_ok = check_backend_direct()
    
    # Crear QR válido de ejemplo
    valid_qr = create_valid_whatsapp_qr()
    
    print("\n" + "=" * 50)
    print("🏁 RESUMEN DEL ANÁLISIS")
    print(f"Backend genera QR: {'✅ SÍ' if backend_ok else '❌ NO'}")
    print(f"QR válido creado: {'✅ SÍ' if valid_qr else '❌ NO'}")
    
    if not backend_ok:
        print("\n💡 RECOMENDACIONES:")
        print("1. El backend puede no estar generando QR reales")
        print("2. Railway puede no tener Chrome instalado")
        print("3. El QR puede ser simulado/dummy")
        print("4. Verificar logs del backend para más detalles")
