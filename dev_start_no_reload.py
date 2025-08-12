#!/usr/bin/env python3
"""
Iniciador de desarrollo simple - sin auto-reload en tests/
"""
from dotenv import load_dotenv
import os
import logging

# Configurar logging silencioso
logging.basicConfig(level=logging.ERROR)

# Cargar variables de entorno
modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

# Lanzar app Flask SIN debug mode
try:
    from gunicorn_patch import app, socketio

    # Si app es una tupla, extraer el primer elemento
    if isinstance(app, tuple) and len(app) >= 1:
        app_instance = app[0]
    else:
        app_instance = app

    if __name__ == '__main__':
        print("🚀 Servidor Flask - Modo desarrollo SIN auto-reload")
        print("📁 Los cambios en tests/ NO reinician el servidor")
        print("🔄 Para reiniciar: Ctrl+C y volver a ejecutar")
        print("=" * 50)
        
        # SIN debug=True para evitar auto-reload
        app_instance.run(
            debug=False,  # ✅ Sin auto-reload
            port=5000,
            host='0.0.0.0'
        )
        
except Exception as e:
    print(f"❌ Error al iniciar la aplicación: {str(e)}")
    logging.error(f"Error al iniciar la aplicación: {str(e)}", exc_info=True)
