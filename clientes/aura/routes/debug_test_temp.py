print("✅ debug_test_temp.py cargado correctamente")

from flask import Blueprint, jsonify

debug_test_temp_bp = Blueprint("debug_test_temp_bp", __name__, url_prefix="/debug")

@debug_test_temp_bp.route("/test_temp")
def test_temp():
    return jsonify({
        "ok": True,
        "mensaje": "Este blueprint está funcionando desde rutas"
    })
