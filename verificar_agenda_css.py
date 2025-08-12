#!/usr/bin/env python3
"""
Verificador del módulo agenda - CSS y JavaScript
Verifica que los archivos estáticos se cargan correctamente
"""

import os
import sys
from pathlib import Path

def verificar_archivos_estaticos():
    """Verifica que los archivos CSS y JS existen y tienen contenido"""
    print("🔍 Verificando archivos estáticos del módulo agenda...")
    
    base_path = Path("C:/Users/PC/PYTHON/AuraAi2")
    
    # Archivos a verificar
    archivos = [
        "static/css/modulos/agenda/main.css",
        "static/js/modulos/agenda/main.js",
        "clientes/aura/templates/panel_cliente_agenda/index.html",
        "clientes/aura/routes/panel_cliente_agenda/panel_cliente_agenda.py"
    ]
    
    for archivo in archivos:
        ruta_completa = base_path / archivo
        
        if ruta_completa.exists():
            tamaño = ruta_completa.stat().st_size
            print(f"✅ {archivo} - {tamaño} bytes")
            
            # Verificar contenido específico
            if archivo.endswith('.css'):
                verificar_css(ruta_completa)
            elif archivo.endswith('.js'):
                verificar_js(ruta_completa)
            elif archivo.endswith('.html'):
                verificar_template(ruta_completa)
                
        else:
            print(f"❌ {archivo} - NO EXISTE")

def verificar_css(ruta_css):
    """Verifica contenido del CSS"""
    try:
        with open(ruta_css, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar elementos clave del CSS
        elementos_clave = [
            '.agenda-container',
            '.calendario-grid',
            '.evento-modal',
            '@media (max-width: 768px)',
            'var(--agenda-primary'
        ]
        
        for elemento in elementos_clave:
            if elemento in contenido:
                print(f"    ✅ Contiene: {elemento}")
            else:
                print(f"    ❌ Falta: {elemento}")
                
    except Exception as e:
        print(f"    ❌ Error leyendo CSS: {e}")

def verificar_js(ruta_js):
    """Verifica contenido del JavaScript"""
    try:
        with open(ruta_js, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar elementos clave del JS
        elementos_clave = [
            'class AgendaCalendar',
            'window.AgendaConfig',
            'FullCalendar',
            'GoogleCalendarIntegration',
            'DOMContentLoaded'
        ]
        
        for elemento in elementos_clave:
            if elemento in contenido:
                print(f"    ✅ Contiene: {elemento}")
            else:
                print(f"    ❌ Falta: {elemento}")
                
    except Exception as e:
        print(f"    ❌ Error leyendo JS: {e}")

def verificar_template(ruta_template):
    """Verifica que el template use archivos externos"""
    try:
        with open(ruta_template, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que use archivos externos
        verificaciones = [
            ("url_for('static'", "Usa url_for para archivos estáticos"),
            ("main.css", "Referencia al CSS externo"),
            ("main.js", "Referencia al JS externo"),
            ("AGENDA_CONFIG", "Configuración JavaScript presente")
        ]
        
        for buscar, descripcion in verificaciones:
            if buscar in contenido:
                print(f"    ✅ {descripcion}")
            else:
                print(f"    ❌ {descripcion}")
                
        # Verificar que NO use CSS/JS inline
        problemas_inline = [
            ("<style>", "CSS inline detectado"),
            ("style=\"", "Estilos inline detectados"),
            ("<script>document.", "JavaScript inline detectado")
        ]
        
        for buscar, problema in problemas_inline:
            if buscar in contenido:
                print(f"    ⚠️  {problema}")
                
    except Exception as e:
        print(f"    ❌ Error leyendo template: {e}")

def verificar_estructura_carpetas():
    """Verifica que la estructura de carpetas sea correcta"""
    print("\n🗂️  Verificando estructura de carpetas...")
    
    base_path = Path("C:/Users/PC/PYTHON/AuraAi2")
    
    carpetas_requeridas = [
        "static",
        "static/css",
        "static/css/modulos",
        "static/css/modulos/agenda",
        "static/js",
        "static/js/modulos", 
        "static/js/modulos/agenda",
        "clientes/aura/templates/panel_cliente_agenda",
        "clientes/aura/routes/panel_cliente_agenda"
    ]
    
    for carpeta in carpetas_requeridas:
        ruta_carpeta = base_path / carpeta
        if ruta_carpeta.exists() and ruta_carpeta.is_dir():
            print(f"✅ {carpeta}/")
        else:
            print(f"❌ {carpeta}/ - NO EXISTE")

def verificar_blueprint():
    """Verifica configuración del blueprint"""
    print("\n🔧 Verificando configuración del blueprint...")
    
    try:
        # Simular importación
        blueprint_path = Path("C:/Users/PC/PYTHON/AuraAi2/clientes/aura/routes/panel_cliente_agenda/panel_cliente_agenda.py")
        
        if not blueprint_path.exists():
            print("❌ Archivo del blueprint no existe")
            return
        
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar configuración del blueprint
        verificaciones = [
            ("static_folder='../../static'", "Carpeta static configurada"),
            ("static_url_path='/static'", "URL path static configurado"),
            ("panel_cliente_agenda_bp", "Blueprint definido"),
            ("url_prefix=", "URL prefix configurado")
        ]
        
        for buscar, descripcion in verificaciones:
            if buscar in contenido:
                print(f"✅ {descripcion}")
            else:
                print(f"❌ {descripcion}")
                
    except Exception as e:
        print(f"❌ Error verificando blueprint: {e}")

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICADOR DEL MÓDULO AGENDA")
    print("=" * 50)
    
    verificar_estructura_carpetas()
    verificar_archivos_estaticos()
    verificar_blueprint()
    
    print("\n" + "=" * 50)
    print("✅ Verificación completada")
    print("\n💡 Pasos siguientes:")
    print("1. Iniciar el servidor Flask")
    print("2. Visitar: http://localhost:5000/panel_cliente/aura/agenda")
    print("3. Verificar que CSS se carga correctamente en DevTools")
    print("4. Comprobar que JavaScript funciona (calendario interactivo)")

if __name__ == "__main__":
    main()
