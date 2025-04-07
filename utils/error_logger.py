import os
import json
from datetime import datetime

# Archivos de log
JSON_LOG_FILE = "logs_errores.json"
TXT_LOG_FILE = os.path.join("logs", "error_log.txt")

# Asegurar carpeta de logs
os.makedirs("logs", exist_ok=True)

def registrar_error(origen, mensaje, tipo="general", detalles=None):
    timestamp = datetime.now().isoformat()

    # Estructura común
    error_data = {
        "timestamp": timestamp,
        "origen": origen,
        "tipo": tipo,
        "mensaje": mensaje
    }

    if detalles:
        error_data["detalles"] = detalles

    # Guardar en JSON para el panel
    try:
        if os.path.exists(JSON_LOG_FILE):
            with open(JSON_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
    except json.JSONDecodeError:
        logs = []

    logs.append(error_data)

    with open(JSON_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    # Guardar en texto plano para debug humano
    with open(TXT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {origen} ({tipo}): {mensaje}\n")
        if detalles:
            f.write(f"  Detalles: {detalles}\n")
