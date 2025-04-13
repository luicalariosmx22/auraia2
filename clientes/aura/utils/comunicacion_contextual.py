import os
import json
from datetime import datetime, timedelta

HISTORIAL_DIR = "clientes/aura/database/historial"

def cargar_historial(numero):
    ruta = os.path.join(HISTORIAL_DIR, f"{numero}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def ya_saludo(historial):
    for mensaje in historial:
        if mensaje["origen"] == "bot" and "hola" in mensaje["mensaje"].lower():
            return True
    return False

def tiempo_ultima_interaccion(historial):
    if not historial:
        return None
    ultimo = historial[-1]
    try:
        hora = datetime.strptime(ultimo["hora"], "%Y-%m-%d %H:%M:%S")
        return hora
    except Exception:
        return None

def debe_saludar(numero):
    historial = cargar_historial(numero)
    return not ya_saludo(historial)

def debe_preguntar_si_hay_duda(numero):
    historial = cargar_historial(numero)
    ultima_hora = tiempo_ultima_interaccion(historial)

    if not ultima_hora:
        return False

    ahora = datetime.now()
    diferencia = ahora - ultima_hora

    if diferencia > timedelta(hours=1):
        return True
    return False
