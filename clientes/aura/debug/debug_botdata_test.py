# clientes/aura/debug/debug_botdata_test.py

from flask import Blueprint, jsonify
import json
import os

# ✅ Prefijo correcto para que funcione con /debug/test_botdata
debug_test_bp = Blueprint("debug_test_botdata", __name__, url_prefix="/debug")

@debug_test_bp.route("/test_botdata")
def test_botdata():
    ruta = "clientes/aura/database/bot_data.json"
    
    if not os.path.exists(ruta):
        return jsonify({
            "ok": False,
            "error": "El archivo bot_data.json no existe en la ruta esperada."
        })

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({
            "ok": True,
            "mensaje": "Archivo cargado correctamente.",
            "claves_disponibles": list(data.keys())
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })
