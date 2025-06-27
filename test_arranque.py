#!/usr/bin/env python3
"""
Script simple para probar que el servidor arranca sin errores
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Probar que todos los imports funcionen"""
    try:
        print("🔧 Probando imports...")
        
        # Probar import del cliente_nora
        from clientes.aura.routes.cliente_nora import cliente_nora_bp
        print("✅ cliente_nora_bp importado correctamente")
        
        # Probar import de la app
        from gunicorn_patch import app
        print("✅ App importada correctamente")
        
        # Probar que el servidor se pueda inicializar
        with app.test_client() as client:
            print("✅ Test client creado correctamente")
        
        print("🎉 ¡Todos los imports funcionan correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Probar rutas específicas"""
    try:
        from gunicorn_patch import app
        
        with app.test_client() as client:
            print("🔧 Probando rutas...")
            
            # Probar ruta de diagnóstico
            response = client.get('/diagnostico/test-nora')
            print(f"📊 /diagnostico/test-nora: {response.status_code}")
            
            # Probar ruta de archivo JS
            response = client.get('/static/js/ui-utils.js')
            print(f"📄 /static/js/ui-utils.js: {response.status_code}")
            
            # Probar ruta de entrenamiento sin auth
            response = client.get('/entrenar/test-nora')
            print(f"🎯 /entrenar/test-nora: {response.status_code}")
            
        print("✅ Todas las rutas responden correctamente")
        
    except Exception as e:
        print(f"❌ Error probando rutas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 PRUEBA DE ARRANQUE DEL SERVIDOR")
    print("=" * 50)
    
    if test_import():
        print("\n" + "=" * 50)
        test_routes()
        
        print("\n" + "=" * 50)
        print("✅ Servidor listo para arrancar")
        print("📝 Para iniciar: python dev_start.py")
        print("🌐 Luego visita: http://localhost:5000/entrenar/test-nora")
    else:
        print("\n❌ Hay problemas con los imports")
