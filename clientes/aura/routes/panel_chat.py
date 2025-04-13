print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint, render_template, request
import os
import json

panel_chat_bp = Blueprint('panel_chat_aura', __name__)

@panel_chat_bp.route("/panel/chat/<nombre_nora>", methods=["GET"])
def panel_chat(nombre_nora):
    historial_dir = f"clientes/{nombre_nora}/database/historial"
    contactos = []

    if os.path.exists(historial_dir):
        for archivo in os.listdir(historial_dir):
            if archivo.endswith(".json"):
                ruta = os.path.join(historial_dir, archivo)
                with open(ruta, "r", encoding="utf-8") as f:
                    mensajes = json.load(f)
                    if mensajes:
                        ultimo = mensajes[-1]
                        contactos.append({
                            "numero": archivo.replace(".json", ""),
                            "nombre": ultimo.get("ProfileName", archivo.replace(".json", "")),
                            "mensajes": mensajes
                        })

    return render_template(
        "panel_chat.html",
        contactos=contactos,
        nombre_nora=nombre_nora
    )
