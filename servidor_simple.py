#!/usr/bin/env python3
"""
🚀 Servidor de desarrollo simple (sin gunicorn/gevent)
Usar cuando dev_start.py falla por dependencias
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar la aplicación Flask principal
    from run import app
    
    if __name__ == "__main__":
        print("🚀 Iniciando servidor de desarrollo simple...")
        print("📍 Servidor: http://localhost:5000")
        print("🔧 Panel de entrenamiento: http://localhost:5000/admin/nora/aura/entrenar")
        print("⏹️ Presiona Ctrl+C para detener")
        print("-" * 60)
        
        # Iniciar servidor Flask en modo debug
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
except ImportError as e:
    print(f"❌ Error importando la aplicación: {e}")
    print("💡 Verifica que run.py existe y está configurado correctamente")
    
except Exception as e:
    print(f"❌ Error iniciando servidor: {e}")
    print(f"Tipo de error: {type(e).__name__}")
