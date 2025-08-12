# clientes/aura/app_config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde .env si lo usas

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-fuerte")
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "aura_multinora_cookie")
    
    # 🔄 Configuración para auto-reload de templates sin reiniciar servidor
    TEMPLATES_AUTO_RELOAD = True  # ✅ Recarga templates automáticamente
    SEND_FILE_MAX_AGE_DEFAULT = 0  # ✅ No cachea archivos estáticos
    
    # 🧪 Solo en desarrollo
    if os.environ.get("ENTORNO", "local") == "local":
        DEBUG = True  # ✅ Modo debug para desarrollo
        EXPLAIN_TEMPLATE_LOADING = False  # No mostrar logs de templates (muy verboso)
    else:
        DEBUG = False  # ❌ Sin debug en producción
    
    # Agrega más configuraciones aquí
    # Ejemplo: SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")