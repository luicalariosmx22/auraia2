# 📁 Archivo: clientes/aura/routes/debug.py

from flask import Blueprint, request
from clientes.aura.utils.debug_integracion import revisar_todo
import os
import json

HISTORIAL_DIR = "clientes/aura/database/historial"

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/verificar", methods=["GET"])
def debug_verificacion():
    resultado = revisar_todo()
    return f"<pre>{resultado}</pre>"


@debug_bp.route("/debug/reset/historial", methods=["GET"])
def reset_historial():
    numero = request.args.get("numero")
    if not numero:
        return "⚠️ Debes proporcionar un número en el parámetro ?numero=XXXXXXXX"

    archivo = os.path.join(HISTORIAL_DIR, f"{numero}.json")
    if os.path.exists(archivo):
        os.remove(archivo)
        return f"✅ Historial del número {numero} eliminado."
    return f"⚠️ No se encontró historial para el número {numero}."


@debug_bp.route("/debug/info", methods=["GET"])
def info_contacto():
    numero = request.args.get("numero")
    if not numero:
        return "⚠️ Debes proporcionar un número en el parámetro ?numero=XXXXXXXX"

    archivo = os.path.join(HISTORIAL_DIR, f"{numero}.json")
    if not os.path.exists(archivo):
        return f"❌ No se encontró historial para el número {numero}."

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            historial = json.load(f)
        salida = f"🧾 Historial de {numero} (últimos 5 mensajes):\n\n"
        for msg in historial[-5:]:
            salida += f"[{msg['hora']}] {msg['origen']}: {msg['mensaje']}\n"
        return f"<pre>{salida}</pre>"
    except Exception as e:
        return f"❌ Error al leer historial: {e}"
