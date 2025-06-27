#!/usr/bin/env python3
"""
🧪 Script de prueba rápida para verificar el funcionamiento del panel
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rutas_js():
    """Probar que los archivos JavaScript existan y tengan contenido"""
    print("🔍 Verificando archivos JavaScript...")
    
    js_folder = os.path.join('clientes', 'aura', 'static', 'js')
    archivos = [
        'panel-entrenamiento-core.js',
        'ui-utils.js', 
        'conocimiento-manager.js',
        'form-handlers.js'
    ]
    
    for archivo in archivos:
        path = os.path.join(js_folder, archivo)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar funciones específicas
            funciones_esperadas = {
                'ui-utils.js': ['scrollToSection', 'toggleExamples'],
                'panel-entrenamiento-core.js': ['PANEL_CONFIG'],
                'conocimiento-manager.js': ['cargarConocimiento'],
                'form-handlers.js': ['initializeFormHandlers']
            }
            
            print(f"✅ {archivo} ({len(contenido)} chars)")
            
            if archivo in funciones_esperadas:
                for funcion in funciones_esperadas[archivo]:
                    if funcion in contenido:
                        print(f"   ✅ {funcion} encontrada")
                    else:
                        print(f"   ❌ {funcion} NO encontrada")
        else:
            print(f"❌ {archivo} NO EXISTE")
    
    print()

def crear_test_servidor():
    """Crear un test simple para probar el servidor"""
    test_content = '''
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
try:
    from gunicorn_patch import app
    print("✅ App importada correctamente")
    
    # Probar una ruta simple
    with app.test_client() as client:
        # Probar ruta de diagnóstico
        response = client.get('/diagnostico/test-nora')
        print(f"📊 Diagnóstico response: {response.status_code}")
        
        # Probar ruta de archivo JS
        response = client.get('/static/js/ui-utils.js')
        print(f"📄 ui-utils.js response: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if 'scrollToSection' in content:
                print("✅ scrollToSection encontrada en ui-utils.js")
            else:
                print("❌ scrollToSection NO encontrada en ui-utils.js")
        
        # Probar endpoint de entrenamiento sin auth
        response = client.get('/entrenar/test-nora')
        print(f"🎯 Panel entrenamiento response: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error importando app: {e}")
    '''
    
    with open('test_servidor.py', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ test_servidor.py creado")

def main():
    print("🧪 VERIFICADOR RÁPIDO DEL PANEL DE ENTRENAMIENTO")
    print("=" * 60)
    
    test_rutas_js()
    crear_test_servidor()
    
    print("📋 Para probar:")
    print("1. python test_servidor.py")
    print("2. Acceder a http://localhost:5000/diagnostico/test-nora")
    print("3. Verificar la consola del navegador")

if __name__ == "__main__":
    main()
