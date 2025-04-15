from flask import Blueprint, render_template, request, jsonify, session
import json
import os
from datetime import datetime

envios_programados_bp = Blueprint("envios_programados", __name__)

CONTACTOS_PATH = "clientes/aura/database/contactos.json"
ENVIOS_PATH = "clientes/aura/database/envios_programados.json"

@envios_programados_bp.route("/panel/envios-programados")
@envios_programados_bp.route("/panel/envios-programados/<estado>")
def vista_envios(estado=None):
        return render_template("panel_envios_programados.html", estado=estado)

@envios_programados_bp.route("/api/contactos")
def api_contactos():
    with open(CONTACTOS_PATH, "r", encoding="utf-8") as f:
        contactos = json.load(f)
    return jsonify(contactos)

@envios_programados_bp.route("/api/envios-programados")
def api_envios_programados():
    estado_filtro = request.args.get("estado")
    if os.path.exists(ENVIOS_PATH):
        with open(ENVIOS_PATH, "r", encoding="utf-8") as f:
            todos = json.load(f)
            if estado_filtro:
                filtrados = [e for e in todos if e.get("estado") == estado_filtro]
                return jsonify(filtrados)
            return jsonify(todos)
    return jsonify([])

@envios_programados_bp.route("/api/programar-envio-masivo", methods=["POST"])
def programar_envio_masivo():
    data = request.json
    mensaje = data.get("mensaje")
    fecha = data.get("fecha")
    hora = data.get("hora")
    destinatarios = data.get("destinatarios", [])

    errores = []
    if not mensaje:
        errores.append("Falta el mensaje.")
    if not fecha:
        errores.append("Falta la fecha.")
    if not hora:
        errores.append("Falta la hora.")
    if not destinatarios:
        errores.append("No se seleccionaron destinatarios.")

    if errores:
        return jsonify({"error": "Datos incompletos", "detalles": errores}), 400

    if not os.path.exists(ENVIOS_PATH):
        with open(ENVIOS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    with open(ENVIOS_PATH, "r", encoding="utf-8") as f:
        existentes = json.load(f)

    programado_por = session.get("user", {}).get("email", "admin")

    for numero in destinatarios:
        existentes.append({
            "numero": numero,
            "mensaje": mensaje,
            "fecha": fecha,
            "hora": hora,
            "programado_por": programado_por,
            "estado": "pendiente",
            "creado_en": datetime.now().isoformat()
        })

    with open(ENVIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(existentes, f, ensure_ascii=False, indent=2)

    return jsonify({"ok": True})

@envios_programados_bp.route("/api/cancelar-envio", methods=["POST"])
def cancelar_envio():
    data = request.json
    numero = data.get("numero")
    fecha = data.get("fecha")
    hora = data.get("hora")

    if not all([numero, fecha, hora]):
        return jsonify({"error": "Faltan datos para cancelar el envío."}), 400

    if not os.path.exists(ENVIOS_PATH):
        return jsonify({"error": "No hay archivo de envíos."}), 404

    with open(ENVIOS_PATH, "r", encoding="utf-8") as f:
        envios = json.load(f)

    nuevos = [e for e in envios if not (e["numero"] == numero and e["fecha"] == fecha and e["hora"] == hora)]

    with open(ENVIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(nuevos, f, ensure_ascii=False, indent=2)

    return jsonify({"ok": True})
