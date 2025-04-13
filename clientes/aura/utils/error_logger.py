import json
from datetime import datetime

RUTA_LOG = "clientes/aura/database/logs_errores.json"

def registrar_error(origen, mensaje_error):
    error = {
        "origen": origen,
        "mensaje": mensaje_error,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(RUTA_LOG, "r", encoding="utf-8") as f:
            errores = json.load(f)
    except:
        errores = []

    errores.append(error)

    with open(RUTA_LOG, "w", encoding="utf-8") as f:
        json.dump(errores, f, indent=2, ensure_ascii=False)
