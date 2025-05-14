# clientes/aura/app_config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde .env si lo usas

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-fuerte")
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "aura_multinora_cookie")
    # Agrega más configuraciones aquí
    # Ejemplo: SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")