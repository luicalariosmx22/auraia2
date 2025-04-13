import json
import os

RUTA_CONFIG = "clientes/aura/config/settings.json"

def cargar_settings():
    try:
        if os.path.exists(RUTA_CONFIG):
            with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar settings: {e}")
    
    return {
        "usar_ai": False,
        "usar_respuestas_automaticas": False,
        "usar_manejo_archivos": False
    }
