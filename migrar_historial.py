import os
import json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

HISTORIAL_PATH = "clientes/aura/database/historial"

def cargar_archivos_historial():
    archivos = []
    if not os.path.exists(HISTORIAL_PATH):
        print(f"❌ No se encontró la carpeta {HISTORIAL_PATH}")
        return archivos

    for archivo in os.listdir(HISTORIAL_PATH):
        if archivo.endswith(".json"):
            ruta = os.path.join(HISTORIAL_PATH, archivo)
            telefono = archivo.replace(".json", "")
            archivos.append((telefono, ruta))

    return archivos

def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al leer {ruta}: {e}")
        return []

def preparar_registros(telefono, mensajes):
    registros
