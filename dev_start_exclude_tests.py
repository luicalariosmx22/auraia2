#!/usr/bin/env python3
"""
Servidor de desarrollo con auto-reload que excluye tests/
Versión simplificada usando Flask nativo
"""
from dotenv import load_dotenv
import os
import logging
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Configurar logging silencioso
logging.basicConfig(level=logging.ERROR)

# Cargar variables de entorno
modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

def should_reload_file(filename):
    """Determina si un archivo debe causar reload"""
    
    # Excluir carpetas específicas
    exclude_patterns = [
        'tests/',
        '__pycache__/',
        '.git/',
        'logs/',
        'node_modules/',
        '.vscode/',
        'patches/',
        'flask_session/',
        '.pytest_cache/'
    ]
    
    # Verificar patrones de exclusión
    for pattern in exclude_patterns:
        if pattern in filename:
            return False
    
    # Solo archivos importantes
    valid_extensions = ['.py', '.html', '.js', '.css', '.json', '.yaml', '.yml']
    return any(filename.endswith(ext) for ext in valid_extensions)

try:
    from gunicorn_patch import app, socketio

    # Si app es una tupla, extraer el primer elemento
    if isinstance(app, tuple) and len(app) >= 1:
        app_instance = app[0]
    else:
        app_instance = app

    if __name__ == '__main__':
        print("🚀 Servidor Flask - Auto-reload INTELIGENTE")
        print("✅ Auto-reload activado para archivos importantes")
        print("❌ Tests/ y archivos temporales NO reinician el servidor")
        print("=" * 55)
        
        # Auto-reload inteligente usando werkzeug
        run_simple(
            hostname='0.0.0.0',
            port=5000,
            application=app_instance,
            use_debugger=True,
            use_reloader=True,
            reloader_type='stat',  # Tipo de reloader más estable
            extra_files=[],  # Archivos adicionales a monitorear
            exclude_patterns=['*/tests/*', '*/__pycache__/*', '*/logs/*']  # Patrones a excluir
        )
        
except Exception as e:
    print(f"❌ Error al iniciar la aplicación: {str(e)}")
    logging.error(f"Error al iniciar la aplicación: {str(e)}", exc_info=True)
