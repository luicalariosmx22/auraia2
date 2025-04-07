import os
import json

CARPETA_MEMORIA = "memory"

def obtener_memoria(usuario_id):
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_memoria(usuario_id, data):
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    os.makedirs(CARPETA_MEMORIA, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def limpiar_memoria(usuario_id):
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    if os.path.exists(ruta):
        os.remove(ruta)
