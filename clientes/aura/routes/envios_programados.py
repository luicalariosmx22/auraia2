from flask import Blueprint, render_template, request, jsonify
import json
import os
from datetime import datetime

envios_programados_bp = Blueprint("envios_programados", __name__)

CONTACTOS_PATH = "clientes/aura/database/contactos.json"
ENVIOS_PATH = "clientes/aura/database/envios_programados.json"

@envios_programados_bp.route("/panel/envios-programados")
def vista_envios():
    return render_template("panel_envios_programados.html")

@envios_programados_bp.route("/api/contactos")
def api_contactos():
    with open(CONTACTOS_PATH, "r", encoding="utf-8") as f:
        contactos = json.load(f)
    return jsonify(contactos)

@envios_programados_bp.route("/api/programar-envio-masivo", methods=["POST"])
def programar_envio_masivo():
    data = request.json
    mensaje = data.get("mensaje")
    fecha = data.get("fecha")
    hora = data.get("hora")
    destinatarios = data.get("destinatarios", [])

    if not mensaje or not fecha or not hora or not destinatarios:
        return jsonify({"error": "Datos incompletos"}), 400

    if not os.path.exists(ENVIOS_PATH):
        with open(ENVIOS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    with open(ENVIOS_PATH, "r", encoding="utf-8") as f:
        existentes = json.load(f)

    for numero in destinatarios:
        existentes.append({
            "numero": numero,
            "mensaje": mensaje,
            "fecha": fecha,
            "hora": hora,
            "programado_por": "admin",
            "estado": "pendiente",
            "creado_en": datetime.now().isoformat()
        })

    with open(ENVIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(existentes, f, ensure_ascii=False, indent=2)

    return jsonify({"ok": True})