from flask import Blueprint, jsonify
import os
import json

chat_data_bp = Blueprint('chat_data_aura', __name__)

@chat_data_bp.route("/chat/<numero>")
def chat_historial(numero):
    ruta = f"clientes/aura/database/historial/{numero}.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            historial = json.load(f)
        nombre = historial[0]["nombre"] if historial else "Sin nombre"
        return jsonify({"nombre": nombre, "historial": historial})
    return jsonify({"nombre": "Desconocido", "historial": []})
