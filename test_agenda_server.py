#!/usr/bin/env python3
"""
Test del módulo agenda - Servidor de desarrollo
Inicia el servidor Flask y abre el módulo agenda
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def verificar_dependencias():
    """Verifica que Flask esté instalado"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} detectado")
        return True
    except ImportError:
        print("❌ Flask no está instalado")
        print("💡 Instalar con: pip install flask")
        return False

def verificar_variables_entorno():
    """Verifica variables de entorno básicas"""
    print("🔍 Verificando variables de entorno...")
    
    variables_requeridas = [
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    faltan = []
    for var in variables_requeridas:
        if var in os.environ:
            print(f"✅ {var} configurada")
        else:
            print(f"❌ {var} no configurada")
            faltan.append(var)
    
    if faltan:
        print(f"\n⚠️  Variables faltantes: {', '.join(faltan)}")
        print("💡 Cargar desde .env.local o configurar manualmente")
        return False
    
    return True

def iniciar_servidor():
    """Inicia el servidor Flask en modo desarrollo"""
    print("🚀 Iniciando servidor Flask...")
    
    # Cambiar al directorio del proyecto
    os.chdir("C:/Users/PC/PYTHON/AuraAi2")
    
    # Configurar variables de entorno para desarrollo
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    env['MODO_DEV'] = 'True'
    
    try:
        # Iniciar servidor usando dev_start.py si existe, sino run.py
        if Path("dev_start.py").exists():
            print("📝 Usando dev_start.py...")
            proceso = subprocess.Popen(
                [sys.executable, "dev_start.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        else:
            print("📝 Usando run.py...")
            proceso = subprocess.Popen(
                [sys.executable, "run.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        return proceso
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def esperar_servidor(timeout=30):
    """Espera a que el servidor esté listo"""
    import requests
    
    print("⏳ Esperando que el servidor esté listo...")
    
    url_test = "http://localhost:5000"
    
    for i in range(timeout):
        try:
            response = requests.get(url_test, timeout=2)
            if response.status_code == 200:
                print("✅ Servidor listo!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   Esperando... {i+1}/{timeout}")
    
    print("❌ Timeout esperando servidor")
    return False

def abrir_navegador():
    """Abre el módulo agenda en el navegador"""
    url_agenda = "http://localhost:5000/panel_cliente/aura/agenda"
    
    print(f"🌐 Abriendo navegador: {url_agenda}")
    
    try:
        webbrowser.open(url_agenda)
        return True
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para probar el módulo"""
    print("\n" + "="*50)
    print("📋 INSTRUCCIONES DE TESTING")
    print("="*50)
    
    print("\n🔍 En el navegador, verificar:")
    print("✅ 1. La página carga sin errores")
    print("✅ 2. El CSS se aplica correctamente (colores, layout)")
    print("✅ 3. El calendario se muestra")
    print("✅ 4. Los botones son interactivos")
    print("✅ 5. No hay errores en la consola del navegador (F12)")
    
    print("\n🛠️ DevTools (F12):")
    print("• Pestaña 'Console' - verificar errores JavaScript")
    print("• Pestaña 'Network' - verificar que CSS/JS se cargan")
    print("• Pestaña 'Elements' - inspeccionar estilos aplicados")
    
    print("\n📂 URLs a probar:")
    print("• Panel principal: http://localhost:5000/panel_cliente/aura")
    print("• Módulo agenda: http://localhost:5000/panel_cliente/aura/agenda")
    print("• Health check: http://localhost:5000/health")
    
    print("\n⏹️ Para detener el servidor: Ctrl+C en la terminal")

def main():
    """Función principal"""
    print("🧪 TEST DEL MÓDULO AGENDA")
    print("=" * 30)
    
    # Verificaciones previas
    if not verificar_dependencias():
        return
    
    # Variables de entorno (opcional para testing básico)
    verificar_variables_entorno()
    
    print("\n🚀 Iniciando testing...")
    
    # Iniciar servidor
    proceso_servidor = iniciar_servidor()
    if not proceso_servidor:
        return
    
    try:
        # Esperar que el servidor esté listo
        if esperar_servidor():
            # Abrir navegador
            abrir_navegador()
            
            # Mostrar instrucciones
            mostrar_instrucciones()
            
            print("\n⏳ Servidor ejecutándose...")
            print("💡 Presiona Ctrl+C para detener")
            
            # Mantener servidor activo
            proceso_servidor.wait()
            
        else:
            print("❌ El servidor no respondió")
            
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo servidor...")
        
    finally:
        # Terminar proceso del servidor
        if proceso_servidor:
            proceso_servidor.terminate()
            try:
                proceso_servidor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proceso_servidor.kill()
        
        print("✅ Servidor detenido")

if __name__ == "__main__":
    # Verificar que requests está disponible
    try:
        import requests
    except ImportError:
        print("⚠️ requests no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    
    main()
