# clientes/aura/routes/debug_verificar.py

from flask import Blueprint, jsonify
import pkg_resources

debug_verificar_bp = Blueprint("debug_verificar", __name__)

@debug_verificar_bp.route("/debug/verificar", methods=["GET"])
def verificar_configuracion():
    resultado = {}

    # Verificar versión de openai
    try:
        openai_version = pkg_resources.get_distribution("openai").version
        resultado["openai"] = {
            "version": openai_version,
            "estado": "✅ Correcta" if openai_version == "0.28.1" else "❌ Incorrecta (usa 0.28.1)"
        }
    except Exception as e:
        resultado["openai"] = {
            "version": None,
            "estado": f"❌ No instalado ({str(e)})"
        }

    # Aquí puedes agregar más validaciones en el futuro...

    return jsonify(resultado)
