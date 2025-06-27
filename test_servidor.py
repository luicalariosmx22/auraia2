
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
    