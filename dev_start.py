# ✅ Archivo: dev_start.py
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# 🔇 Configurar logging antes de cualquier otra importación
logging.basicConfig(level=logging.ERROR)  # Solo errores críticos

# Configurar handler para archivo de log
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'werkzeug_patch.log'),
    maxBytes=1024*1024,
    backupCount=3
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Agregar handler al logger raíz
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

# Verificar y crear carpeta de parches si no existe
patches_dir = os.path.join(os.path.dirname(__file__), 'patches')
if not os.path.exists(patches_dir):
    try:
        os.makedirs(patches_dir, exist_ok=True)
        print(f"✅ Carpeta de parches creada en {patches_dir}")
    except Exception as e:
        print(f"❌ Error al crear carpeta de parches: {str(e)}")

# 🔧 Aplicar parches antes de importar otras bibliotecas
try:
    # Agregar la ruta del proyecto al path de Python si es necesario
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Verificar si existe el módulo de parches
    patches_module_path = os.path.join(patches_dir, 'werkzeug_patches.py')
    if not os.path.exists(patches_module_path):
        # Crear el módulo de parches si no existe
        print(f"⚠️ Módulo de parches no encontrado, creando en {patches_module_path}")
        from pathlib import Path
        
        # Definir el contenido del módulo de parches
        patches_content = """
# filepath: c:\\Users\\PC\\PYTHON\\AuraAi2\\patches\\werkzeug_patches.py
\"\"\"
Parches para solucionar problemas de compatibilidad con Werkzeug y Flask-Session.
\"\"\"
import logging

logger = logging.getLogger(__name__)

def apply_patches():
    \"\"\"
    Aplica todos los parches necesarios a Werkzeug y Flask-Session.
    \"\"\"
    # Patch para el problema de cookies en bytes
    patch_werkzeug_dump_cookie()
    
    # Patch para la verificación de patrones en bytes
    patch_werkzeug_cookie_quote_check()
    
    # Patch para Flask-Session
    patch_flask_session()
    
    logger.info("✅ Parches aplicados correctamente")

def patch_werkzeug_dump_cookie():
    \"\"\"
    Reemplaza werkzeug.http.dump_cookie para manejar valores en bytes.
    \"\"\"
    import werkzeug.http
    original_dump_cookie = werkzeug.http.dump_cookie
    
    def patched_dump_cookie(key, value=None, *args, **kwargs):
        \"\"\"
        Versión modificada de dump_cookie que maneja valores de tipo bytes.
        \"\"\"
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except UnicodeDecodeError:
                value = value.hex()
        
        return original_dump_cookie(key, value, *args, **kwargs)
    
    werkzeug.http.dump_cookie = patched_dump_cookie
    logger.info("✅ Patch werkzeug.http.dump_cookie aplicado")

def patch_werkzeug_cookie_quote_check():
    \"\"\"
    Modifica la verificación de patrón en werkzeug.http para aceptar bytes.
    \"\"\"
    import werkzeug.http
    
    # Monkeypatching para la verificación de valores en dump_cookie
    original_method = werkzeug.http._cookie_no_quote_re.fullmatch
    
    def safe_fullmatch(self, value):
        \"\"\"Verificación segura que maneja bytes.\"\"\"
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except UnicodeDecodeError:
                return None
        return original_method(value)
    
    # Aplicar el monkeypatch
    werkzeug.http._cookie_no_quote_re.fullmatch = lambda value: safe_fullmatch(werkzeug.http._cookie_no_quote_re, value)
    logger.info("✅ Patch para verificación de patrón en cookies aplicado")

def patch_flask_session():
    \"\"\"
    Modifica Flask-Session para evitar problemas con IDs de sesión en bytes.
    \"\"\"
    try:
        from flask_session import sessions
        
        # Guardar la implementación original
        original_save_session = sessions.SessionInterface.save_session
        
        def safe_save_session(self, app, session, response):
            \"\"\"
            Versión segura de save_session que maneja IDs de sesión en bytes.
            \"\"\"
            # Si hay un ID de sesión en bytes, convertirlo a string
            if hasattr(session, 'sid') and isinstance(session.sid, bytes):
                try:
                    session.sid = session.sid.decode('utf-8')
                except UnicodeDecodeError:
                    session.sid = session.sid.hex()
            
            # Llamar a la implementación original
            return original_save_session(self, app, session, response)
        
        # Aplicar el parche
        sessions.SessionInterface.save_session = safe_save_session
        logger.info("✅ Patch para Flask-Session aplicado")
    except ImportError:
        logger.warning("⚠️ No se pudo importar flask_session, omitiendo parche")
        """
        
        # Escribir el contenido al archivo
        with open(patches_module_path, 'w', encoding='utf-8') as f:
            f.write(patches_content)
        
        print(f"✅ Módulo de parches creado en {patches_module_path}")
    
    # Importar y aplicar los parches de Werkzeug
    from patches.werkzeug_patches import apply_patches
    apply_patches()
    
    print("✅ Parches aplicados correctamente")
except Exception as e:
    print(f"❌ Error al aplicar parches: {str(e)}")
    logging.error(f"Error al aplicar parches: {str(e)}", exc_info=True)

# 🧪 Silenciar logs de archivos estáticos (como CSS)
werkzeug_logger = logging.getLogger('werkzeug')
class StaticFilter(logging.Filter):
    def filter(self, record):
        return not (
            "/static/" in record.getMessage()
        )
werkzeug_logger.addFilter(StaticFilter())
werkzeug_logger.setLevel(logging.ERROR)  # Solo errores

# 🔧 Silenciar logs ruidosos de librerías internas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("facebook_business").setLevel(logging.WARNING)

# Cargar variables de entorno
modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

# Lanzar app Flask
try:
    from gunicorn_patch import app, socketio

    # Si app es una tupla (de la versión anterior), extraer el primer elemento
    if isinstance(app, tuple) and len(app) >= 1:
        app_instance = app[0]
    else:
        app_instance = app

    # Usar la instancia correcta de la aplicación
    if __name__ == '__main__':
        # Añadir esto antes de app.run() para depuración:
        print("🔍 Rutas registradas:")
        for rule in app_instance.url_map.iter_rules():
            print(f"  • {rule.endpoint} -> {rule}")
        
        app_instance.run(debug=True, port=5000)
except Exception as e:
    print(f"❌ Error al iniciar la aplicación: {str(e)}")
    logging.error(f"Error al iniciar la aplicación: {str(e)}", exc_info=True)
    
    # Si falla todo, iniciar una aplicación Flask mínima para diagnóstico
    from flask import Flask, session
    
    test_app = Flask(__name__)
    test_app.secret_key = 'dev-key-for-testing'
    
