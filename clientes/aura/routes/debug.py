from flask import Blueprint
from clientes.aura.utils.debug_integracion import revisar_todo

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/verificar", methods=["GET"])
def debug_verificacion():
    resultado = revisar_todo()
    return f"<pre>{resultado}</pre>"
