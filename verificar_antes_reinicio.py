#!/usr/bin/env python3
"""
Verificación pre-reinicio de NORA
Verifica que todos los archivos estén en su lugar
"""

import os
import sys

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print("🔍 VERIFICACIÓN PRE-REINICIO")
    print("="*40)
    
    archivos_criticos = [
        # Blueprint WebSocket
        "clientes/aura/routes/panel_cliente_whatsapp_web/panel_cliente_whatsapp_websocket.py",
        
        # Cliente WebSocket
        "clientes/aura/utils/whatsapp_websocket_client.py",
        
        # Registro dinámico
        "clientes/aura/registro/registro_dinamico.py",
        
        # Template
        "clientes/aura/templates/panel_cliente_whatsapp_web.html",
        
        # App principal (run.py es el archivo real)
        "run.py"
    ]
    
    todos_ok = True
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO EXISTE")
            todos_ok = False
    
    print("\n🔍 VERIFICANDO CONTENIDO CRÍTICO")
    print("="*40)
    
    # Verificar registro dinámico
    try:
        with open("clientes/aura/registro/registro_dinamico.py", "r") as f:
            contenido = f.read()
            if "panel_cliente_whatsapp_websocket" in contenido:
                print("✅ Registro dinámico apunta al blueprint WebSocket")
            else:
                print("❌ Registro dinámico NO apunta al blueprint WebSocket")
                todos_ok = False
    except Exception as e:
        print(f"❌ Error leyendo registro dinámico: {e}")
        todos_ok = False
    
    # Verificar blueprint WebSocket
    try:
        with open("clientes/aura/routes/panel_cliente_whatsapp_web/panel_cliente_whatsapp_websocket.py", "r") as f:
            contenido = f.read()
            if "panel_cliente_whatsapp_web_bp" in contenido:
                print("✅ Blueprint WebSocket tiene nombre correcto")
            else:
                print("❌ Blueprint WebSocket NO tiene nombre correcto")
                todos_ok = False
    except Exception as e:
        print(f"❌ Error leyendo blueprint WebSocket: {e}")
        todos_ok = False
    
    # Verificar template
    try:
        with open("clientes/aura/templates/panel_cliente_whatsapp_web.html", "r") as f:
            contenido = f.read()
            if "cdnjs.cloudflare.com" in contenido and "qrcode" in contenido:
                print("✅ Template tiene QRCode.js correcto")
            else:
                print("❌ Template NO tiene QRCode.js correcto")
                todos_ok = False
    except Exception as e:
        print(f"❌ Error leyendo template: {e}")
        todos_ok = False
    
    print("\n" + "="*40)
    if todos_ok:
        print("✅ VERIFICACIÓN EXITOSA - Todo está en orden")
        print("🚀 Puedes reiniciar NORA con confianza")
        return True
    else:
        print("❌ VERIFICACIÓN FALLÓ - Hay problemas")
        print("🔧 Corrige los errores antes de reiniciar")
        return False

def mostrar_instrucciones():
    """Mostrar instrucciones de uso"""
    print("\n📋 INSTRUCCIONES:")
    print("1. Si la verificación pasó, ejecuta:")
    print("   ./restart_nora_whatsapp.sh")
    print("\n2. Después accede a:")
    print("   http://localhost:5000/panel_cliente/aura/whatsapp")
    print("\n3. Haz clic en 'Flujo Automático' para obtener QR")

if __name__ == "__main__":
    # Cambiar al directorio correcto
    os.chdir("/mnt/c/Users/PC/PYTHON/Auraai2")
    
    if verificar_archivos():
        mostrar_instrucciones()
        sys.exit(0)
    else:
        print("\n❌ No reinicies NORA hasta corregir los problemas")
        sys.exit(1)
