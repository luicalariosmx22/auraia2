print("✅ debug_mensaje_hola.py cargado correctamente")

from flask import Blueprint, jsonify
import os
import json

debug_mensaje_hola_bp = Blueprint("debug_mensaje_hola", __name__, url_prefix="/debug")

@debug_mensaje_hola_bp.route("/mensaje_hola")
def verificar_mensaje_hola():
    ruta = "clientes/aura/database/bot_data.json"

    if not os.path.exists(ruta):
        print("❌ El archivo bot_data.json no existe")
        return jsonify({"ok": False, "error": "El archivo bot_data.json no existe"})

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("❌ Error al leer bot_data.json:", str(e))
        return jsonify({"ok": False, "error": f"Error al leer bot_data.json: {str(e)}"})

    if "hola" not in data:
        print("❌ Clave 'hola' no encontrada en bot_data.json")
        return jsonify({"ok": False, "error": "La clave 'hola' no fue encontrada en bot_data.json"})

    print("✅ bot_data.json cargado correctamente con clave 'hola'")
    return jsonify({
        "ok": True,
        "mensaje": "bot_data.json contiene la clave 'hola'",
        "respuesta": data["hola"]
    })
