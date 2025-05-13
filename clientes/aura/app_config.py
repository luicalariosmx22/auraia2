# clientes/aura/app_config.py
import os
from dotenv import load_dotenv

load_dotenv() # Carga variables desde .env si lo usas

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "una-clave-secreta-muy-fuerte")
    SESSION_TYPE = "filesystem"
    # Agrega más configuraciones aquí
    # Ejemplo: SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")