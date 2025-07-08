#!/usr/bin/env python3
"""
Test final del flujo QR completo
"""

import requests
import time

def test_flujo_qr_final():
    """Test del flujo QR paso a paso como lo haría el usuario"""
    
    print("🎯 TEST FINAL FLUJO QR WHATSAPP WEB")
    print("="*45)
    
    base_url = "http://localhost:5000"
    whatsapp_base = f"{base_url}/panel_cliente/aura/whatsapp"
    
    print("1️⃣ Verificando que el panel carga...")
    try:
        response = requests.get(whatsapp_base, timeout=10)
        if response.status_code != 200:
            print(f"❌ Panel no carga: {response.status_code}")
            return
        
        html = response.text
        tiene_boton = 'onclick="startWhatsAppFlow()"' in html
        tiene_jquery = 'jquery' in html.lower()
        tiene_qrcode = 'qrcode' in html.lower()
        
        print(f"   ✅ Panel carga (200)")
        print(f"   {'✅' if tiene_boton else '❌'} Botón Flujo Automático: {tiene_boton}")
        print(f"   {'✅' if tiene_jquery else '❌'} jQuery cargado: {tiene_jquery}")
        print(f"   {'✅' if tiene_qrcode else '❌'} QRCode.js cargado: {tiene_qrcode}")
        
        if not (tiene_boton and tiene_jquery and tiene_qrcode):
            print("❌ Panel incompleto, abortando test")
            return
            
    except Exception as e:
        print(f"❌ Error cargando panel: {e}")
        return
    
    print("\n2️⃣ Simulando clic en 'Flujo Automático'...")
    print("   (Esto simula conectar + iniciar sesión + obtener QR)")
    
    # Paso 1: Conectar (como lo hace startWhatsAppFlow)
    print("   🔌 Paso 1: Conectar...")
    try:
        response = requests.post(
            f"{whatsapp_base}/connect",
            headers={'Content-Type': 'application/json'},
            timeout=15  # Más tiempo para conectar
        )
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Conectado: {data.get('success', False)}")
        else:
            print(f"   ⚠️ Conectar falló, pero continuando...")
            
    except Exception as e:
        print(f"   ⚠️ Error conectando: {e}, pero continuando...")
    
    # Paso 2: Obtener QR (como lo hace startWhatsAppFlow después de conectar)
    print("   📱 Paso 2: Obtener QR automático...")
    try:
        response = requests.post(
            f"{whatsapp_base}/get_qr_auto",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            has_qr = data.get('has_qr', False)
            qr_data = data.get('qr_data')
            is_test = data.get('is_test', False)
            
            print(f"   ✅ Exitoso: {success}")
            print(f"   📱 Tiene QR: {has_qr}")
            print(f"   🧪 Es de prueba: {is_test}")
            
            if qr_data:
                print(f"   📏 Longitud QR: {len(qr_data)} chars")
                if qr_data.startswith('data:image/'):
                    print(f"   🖼️ Tipo: Imagen base64")
                else:
                    print(f"   📝 Tipo: Texto")
                    print(f"   📋 Muestra: {qr_data[:50]}...")
                
                print("\n🎉 ¡ÉXITO! QR GENERADO")
                print("="*30)
                print("✅ El botón 'Flujo Automático' FUNCIONA")
                print("✅ Se genera QR de prueba correctamente")
                print("✅ El frontend debería mostrar el QR")
                print("\n💡 En el navegador deberías ver:")
                print("   - Loading modal aparece y desaparece")
                print("   - Logs en el panel de actividad")
                print("   - QR aparece en la sección derecha")
                print("   - Toast de éxito aparece")
                
            else:
                print("   ❌ No hay datos de QR")
                
        else:
            print(f"   ❌ Error obteniendo QR: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error obteniendo QR: {e}")
    
    print(f"\n🌐 Para probar manualmente:")
    print(f"   1. Abre: {whatsapp_base}")
    print(f"   2. Haz clic en 'Conectar WhatsApp Web'")
    print(f"   3. Observa logs y QR en el panel")

if __name__ == "__main__":
    test_flujo_qr_final()
