#!/usr/bin/env python3
"""
Diagnostico JavaScript del panel WhatsApp Web
"""

import requests
import re

def test_javascript_panel():
    """Test del JavaScript del panel"""
    
    print("🔧 DIAGNÓSTICO JAVASCRIPT PANEL WHATSAPP")
    print("="*50)
    
    base_url = "http://localhost:5000"
    whatsapp_url = f"{base_url}/panel_cliente/aura/whatsapp"
    
    print("📡 Obteniendo HTML del panel...")
    
    try:
        response = requests.get(whatsapp_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            return
        
        html = response.text
        print(f"✅ HTML obtenido ({len(html)} chars)")
        
        # Verificar dependencias JavaScript
        dependencias = [
            ('jQuery', r'jquery'),
            ('Bootstrap', r'bootstrap'),
            ('Toastr', r'toastr'),
            ('QRCode.js', r'qrcode'),
            ('FontAwesome', r'fontawesome|fas fa-')
        ]
        
        print("\n📚 Verificando dependencias JavaScript:")
        for nombre, patron in dependencias:
            if re.search(patron, html, re.IGNORECASE):
                print(f"   ✅ {nombre} encontrado")
            else:
                print(f"   ❌ {nombre} NO encontrado")
        
        # Verificar funciones JavaScript específicas
        funciones = [
            'startWhatsAppFlow',
            'refreshQR',
            'displayQR',
            'connectToBackend',
            'addLog'
        ]
        
        print("\n🔧 Verificando funciones JavaScript:")
        for funcion in funciones:
            if f"function {funcion}" in html:
                print(f"   ✅ {funcion}() definida")
            else:
                print(f"   ❌ {funcion}() NO encontrada")
        
        # Verificar variables del template
        variables = [
            ('nombreNora', r'const nombreNora = "([^"]+)"'),
            ('backendUrl', r'const backendUrl = "([^"]+)"')
        ]
        
        print("\n📋 Verificando variables del template:")
        for nombre, patron in variables:
            match = re.search(patron, html)
            if match:
                valor = match.group(1)
                print(f"   ✅ {nombre} = '{valor}'")
            else:
                print(f"   ❌ {nombre} NO definida")
        
        # Verificar elementos DOM críticos
        elementos = [
            ('btn btn-success btn-lg', 'Botón Flujo Automático'),
            ('id="qr-container"', 'Contenedor QR'),
            ('id="activity-logs"', 'Contenedor Logs'),
            ('onclick="startWhatsAppFlow()"', 'Event Handler Flujo Automático')
        ]
        
        print("\n🎯 Verificando elementos DOM:")
        for selector, descripcion in elementos:
            if selector in html:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ❌ {descripcion} NO encontrado")
        
        # Buscar posibles errores en el template
        print("\n🔍 Buscando posibles errores:")
        
        # Variables sin interpolar
        sin_interpolar = re.findall(r'\{\{\s*(\w+)\s*\}\}', html)
        if sin_interpolar:
            print(f"   ⚠️ Variables sin interpolar: {sin_interpolar}")
        else:
            print(f"   ✅ Todas las variables interpoladas correctamente")
        
        # Errores de sintaxis JavaScript comunes
        errores_js = [
            (r'function\s+\w+\([^)]*\)\s*{[^}]*$', 'Función sin cerrar'),
            (r'\.then\([^)]*$', 'Promise sin cerrar'),
            (r'console\.log\([^)]*$', 'Console.log sin cerrar')
        ]
        
        for patron, descripcion in errores_js:
            if re.search(patron, html, re.MULTILINE):
                print(f"   ⚠️ Posible error: {descripcion}")
        
        print("\n📄 Verificando estructura del HTML...")
        
        # Verificar que el template se extiende correctamente
        if '{% extends' in html:
            print("   ⚠️ Template no procesado - contiene tags Django/Jinja")
        elif '<html' in html and '</html>' in html:
            print("   ✅ HTML completo renderizado")
        else:
            print("   ❌ HTML incompleto")
        
        # Verificar scripts al final
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        print(f"   📝 Scripts encontrados: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            if 'startWhatsAppFlow' in script:
                print(f"   ✅ Script {i+1}: Contiene lógica principal")
            elif script.strip().startswith('http'):
                print(f"   📚 Script {i+1}: Biblioteca externa")
            elif len(script.strip()) > 100:
                print(f"   🔧 Script {i+1}: Código personalizado ({len(script)} chars)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_javascript_panel()
