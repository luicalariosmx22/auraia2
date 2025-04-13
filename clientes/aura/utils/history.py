import os
import json
from datetime import datetime

HISTORIAL_DIR = "clientes/aura/database/historial"

def guardar_en_historial(numero, mensaje, origen, nombre):
    if not os.path.exists(HISTORIAL_DIR):
        os.makedirs(HISTORIAL_DIR)

    archivo_historial = os.path.join(HISTORIAL_DIR, f"{numero}.json")

    nuevo_mensaje = {
        "mensaje": mensaje,
        "origen": origen,
        "nombre": nombre,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        if os.path.exists(archivo_historial):
            with open(archivo_historial, "r", encoding="utf-8") as f:
                historial = json.load(f)
        else:
            historial = []

        historial.append(nuevo_mensaje)

        with open(archivo_historial, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error al guardar historial: {e}")
