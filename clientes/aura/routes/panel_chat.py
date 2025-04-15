from flask import Blueprint, render_template, request, jsonify
import os, json, datetime

panel_chat_bp = Blueprint("panel_chat_aura", __name__)

def leer_historial(nombre_nora, numero):
    ruta = f"clientes/{nombre_nora}/database/historial/{numero}.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_historial(nombre_nora, numero, mensajes):
    ruta = f"clientes/{nombre_nora}/database/historial/{numero}.json"
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)

def leer_contactos():
    with open("clientes/aura/database/contactos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_contactos(data):
    with open("clientes/aura/database/contactos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    contactos = leer_contactos()
    historial_path = f"clientes/{nombre_nora}/database/historial"
    lista = []
    for c in contactos:
        ruta = os.path.join(historial_path, f"{c['numero']}.json")
        mensajes = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                mensajes = json.load(f)
        lista.append({**c, "mensajes": mensajes})
    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

@panel_chat_bp.route("/api/chat/<numero>")
def api_chat(numero):
    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["numero"] == numero), {})
    historial = leer_historial("aura", numero)
    return jsonify({
        "contacto": contacto,
        "mensajes": historial
    })

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    data = request.json
    numero = data["numero"]
    texto = data["mensaje"]
    nombre_nora = data["nombre_nora"]

    historial = leer_historial(nombre_nora, numero)
    historial.append({
        "origen": "usuario",
        "texto": texto,
        "hora": datetime.datetime.now().strftime("%H:%M")
    })

    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["numero"] == numero), {})
    if contacto.get("ia_activada"):
        respuesta = f"Respuesta IA a: {texto}"
        historial.append({
            "origen": "nora",
            "texto": respuesta,
            "hora": datetime.datetime.now().strftime("%H:%M")
        })

    guardar_historial(nombre_nora, numero, historial)
    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<numero>", methods=["POST"])
def api_toggle_ia(numero):
    contactos = leer_contactos()
    for c in contactos:
        if c["numero"] == numero:
            c["ia_activada"] = not c.get("ia_activada", True)
    guardar_contactos(contactos)
    return jsonify({"success": True})
