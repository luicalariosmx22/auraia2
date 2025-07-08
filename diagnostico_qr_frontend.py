#!/usr/bin/env python3
"""
Diagnóstico específico del QR - Frontend
Verifica por qué el QR no aparece en el navegador
"""

import requests
import json
from datetime import datetime

def test_qr_frontend():
    """Probar todo el flujo del QR hasta el frontend"""
    print("🔍 DIAGNÓSTICO QR FRONTEND")
    print("="*50)
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    # 1. Verificar CDN QRCode.js
    print("\n1️⃣ VERIFICANDO BIBLIOTECA QRCODE.JS")
    try:
        qr_js_urls = [
            'https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js',
            'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js',
            'https://unpkg.com/qrcode@1.5.3/build/qrcode.min.js'
        ]
        
        for url in qr_js_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {url} - OK ({len(response.content)} bytes)")
                else:
                    print(f"❌ {url} - Error {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
                
    except Exception as e:
        print(f"❌ Error verificando CDN: {e}")
    
    # 2. Probar generación de QR real
    print("\n2️⃣ PROBANDO GENERACIÓN DE QR REAL")
    try:
        # Inicializar sesión
        print("🚀 Iniciando sesión...")
        init_response = requests.post(f'{backend_url}/init_session', timeout=15)
        print(f"   Status: {init_response.status_code}")
        
        if init_response.status_code == 200:
            print("   ✅ Sesión iniciada (pero sin endpoint HTTP)")
        else:
            print("   ⚠️ Endpoint HTTP no disponible (esperado)")
            
        # Intentar obtener QR via HTTP (sabemos que no funciona)
        print("\n📱 Intentando obtener QR via HTTP...")
        qr_response = requests.get(f'{backend_url}/qr', timeout=10)
        print(f"   Status: {qr_response.status_code}")
        
        if qr_response.status_code == 200:
            try:
                qr_data = qr_response.json()
                print(f"   ✅ QR obtenido: {json.dumps(qr_data, indent=2)}")
                return qr_data.get('qr_data')
            except:
                print("   ⚠️ Respuesta no es JSON")
        else:
            print("   ❌ QR no disponible via HTTP (esperado)")
            
    except Exception as e:
        print(f"❌ Error probando QR: {e}")
    
    # 3. Verificar WebSocket (simulado)
    print("\n3️⃣ VERIFICANDO WEBSOCKET")
    try:
        import sys
        sys.path.append('/mnt/c/Users/PC/PYTHON/Auraai2')
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        
        client = WhatsAppWebSocketClient()
        print("✅ Cliente WebSocket creado")
        
        # Verificar conectividad
        if client.connect():
            print("✅ Conectado al WebSocket")
            
            # Simular obtención de QR
            if client.init_session():
                print("✅ Sesión iniciada")
                
                import time
                time.sleep(3)
                
                qr = client.get_qr_code()
                if qr:
                    print(f"✅ QR obtenido: {len(qr)} caracteres")
                    print(f"📱 Tipo: {type(qr)}")
                    print(f"📱 Inicio: {qr[:50]}...")
                    
                    # Verificar si es Base64
                    if qr.startswith('data:image/'):
                        print("✅ QR es Base64 válido")
                        return qr
                    else:
                        print("⚠️ QR no es Base64")
                else:
                    print("❌ No se obtuvo QR")
            else:
                print("❌ Error iniciando sesión")
                
            client.disconnect()
        else:
            print("❌ Error conectando WebSocket")
            
    except Exception as e:
        print(f"❌ Error con WebSocket: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def generate_test_qr():
    """Generar QR de prueba para verificar el frontend"""
    print("\n4️⃣ GENERANDO QR DE PRUEBA")
    
    # QR de prueba (texto simple)
    test_qr_text = "https://wa.me/qr/TEST123456789"
    
    try:
        # Intentar generar QR usando qrcode Python
        import qrcode
        from io import BytesIO
        import base64
        
        # Crear QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(test_qr_text)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a Base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        qr_data_url = f"data:image/png;base64,{img_base64}"
        
        print(f"✅ QR de prueba generado: {len(qr_data_url)} caracteres")
        print(f"📱 Inicio: {qr_data_url[:50]}...")
        
        return qr_data_url
        
    except ImportError:
        print("❌ Biblioteca 'qrcode' no instalada")
        print("💡 Instalando qrcode...")
        
        import subprocess
        try:
            subprocess.run(['pip', 'install', 'qrcode[pil]'], check=True)
            print("✅ qrcode instalado")
            return generate_test_qr()  # Reintentar
        except:
            print("❌ Error instalando qrcode")
            
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
    
    return None

def create_test_html():
    """Crear HTML de prueba para verificar QR"""
    print("\n5️⃣ CREANDO HTML DE PRUEBA")
    
    qr_data = generate_test_qr()
    if not qr_data:
        qr_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test QR WhatsApp</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js"></script>
</head>
<body>
    <h1>🧪 Test QR WhatsApp Web</h1>
    
    <h2>1. QR desde Base64 (directo)</h2>
    <img id="qr-base64" src="{qr_data}" style="border: 1px solid #ccc;">
    
    <h2>2. QR desde QRCode.js</h2>
    <canvas id="qr-canvas" style="border: 1px solid #ccc;"></canvas>
    
    <h2>3. QR desde texto</h2>
    <div id="qr-text-container"></div>
    
    <script>
        console.log('🔧 Iniciando test QR...');
        
        // Test 1: Base64 directo
        const base64Img = document.getElementById('qr-base64');
        if (base64Img.src) {{
            console.log('✅ QR Base64 cargado');
        }} else {{
            console.log('❌ QR Base64 no cargado');
        }}
        
        // Test 2: QRCode.js
        if (typeof QRCode !== 'undefined') {{
            console.log('✅ QRCode.js disponible');
            
            const canvas = document.getElementById('qr-canvas');
            QRCode.toCanvas(canvas, 'https://wa.me/qr/TEST123456789', function (error) {{
                if (error) {{
                    console.log('❌ Error QRCode.js:', error);
                }} else {{
                    console.log('✅ QR generado con QRCode.js');
                }}
            }});
        }} else {{
            console.log('❌ QRCode.js no disponible');
        }}
        
        // Test 3: QR desde texto
        const textContainer = document.getElementById('qr-text-container');
        if (typeof QRCode !== 'undefined') {{
            QRCode.toCanvas(textContainer, 'https://wa.me/qr/TEST123456789', {{
                width: 200,
                height: 200
            }}, function (error) {{
                if (error) {{
                    console.log('❌ Error QR texto:', error);
                }} else {{
                    console.log('✅ QR texto generado');
                }}
            }});
        }}
        
        // Test del QR real (simulado)
        const realQR = '{qr_data}';
        console.log('📱 QR real disponible:', realQR.length, 'caracteres');
        
        // Simular función displayQR
        function testDisplayQR(qrData) {{
            console.log('🔧 testDisplayQR llamada');
            
            if (!qrData) {{
                console.log('❌ No hay datos QR');
                return;
            }}
            
            // Crear elemento para mostrar QR
            const testDiv = document.createElement('div');
            testDiv.innerHTML = '<h2>4. Test displayQR</h2>';
            
            if (qrData.startsWith('data:image/')) {{
                // Es Base64
                const img = document.createElement('img');
                img.src = qrData;
                img.style.border = '1px solid #ccc';
                testDiv.appendChild(img);
                console.log('✅ QR Base64 mostrado');
            }} else {{
                // Es texto, usar QRCode.js
                const canvas = document.createElement('canvas');
                canvas.style.border = '1px solid #ccc';
                testDiv.appendChild(canvas);
                
                QRCode.toCanvas(canvas, qrData, function (error) {{
                    if (error) {{
                        console.log('❌ Error QR texto:', error);
                    }} else {{
                        console.log('✅ QR texto mostrado');
                    }}
                }});
            }}
            
            document.body.appendChild(testDiv);
        }}
        
        // Ejecutar test
        testDisplayQR(realQR);
        
        console.log('🎉 Test QR completado');
    </script>
</body>
</html>
"""
    
    # Guardar HTML
    with open('/mnt/c/Users/PC/PYTHON/Auraai2/test_qr.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ HTML de prueba creado: test_qr.html")
    print("💡 Abre este archivo en el navegador para probar QR")
    print("📁 Archivo: /mnt/c/Users/PC/PYTHON/Auraai2/test_qr.html")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO QR FRONTEND")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Probar backend
    qr_data = test_qr_frontend()
    
    # Generar QR de prueba
    test_qr = generate_test_qr()
    
    # Crear HTML de prueba
    create_test_html()
    
    print("\n" + "="*60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("="*60)
    
    if qr_data:
        print("✅ QR se genera correctamente en backend")
        print(f"📱 Tamaño: {len(qr_data)} caracteres")
        print(f"📱 Tipo: {'Base64' if qr_data.startswith('data:') else 'Texto'}")
    else:
        print("❌ QR no se genera en backend")
    
    if test_qr:
        print("✅ QR de prueba generado correctamente")
    else:
        print("❌ Error generando QR de prueba")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Abre test_qr.html en el navegador")
    print("2. Verifica la consola del navegador (F12)")
    print("3. Verifica que se muestren los QR")
    print("4. Si funciona, el problema está en NORA")
    print("5. Si no funciona, el problema está en el navegador")

if __name__ == "__main__":
    main()
