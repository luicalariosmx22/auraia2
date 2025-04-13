import os
import json

# Carpeta donde se guardará la memoria de cada número
CARPETA_MEMORIA = "memory"

def obtener_memoria(usuario_id):
    """
    Devuelve un diccionario con la memoria del usuario si existe.
    """
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_memoria(usuario_id, data):
    """
    Guarda un nuevo estado de memoria para el usuario.
    """
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    os.makedirs(CARPETA_MEMORIA, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def limpiar_memoria(usuario_id):
    """
    Elimina el archivo de memoria si ya no se necesita.
    """
    ruta = os.path.join(CARPETA_MEMORIA, f"{usuario_id}.json")
    if os.path.exists(ruta):
        os.remove(ruta)
