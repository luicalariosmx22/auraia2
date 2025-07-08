from flask import Blueprint, request, jsonify
from clientes.aura.utils.supabase_client import supabase

cobranza_bp = Blueprint("cobranza", __name__)

@cobranza_bp.route("/cobranza", methods=["GET"])
def obtener_cobranza():
    """
    Recupera la lista de clientes con deudas pendientes.
    """
    try:
        response = supabase.table("cobranza").select("*").execute()
        if response.data:
            return jsonify({"success": True, "data": response.data}), 200
        return jsonify({"success": False, "message": "No hay datos de cobranza disponibles"}), 404
    except Exception as e:
        print(f"❌ Error al obtener datos de cobranza: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@cobranza_bp.route("/cobranza/<telefono>", methods=["POST"])
def registrar_pago(telefono):
    """
    Registra un pago para un cliente.
    """
    try:
        data = request.json
        monto = data.get("monto")
        if not monto:
            return jsonify({"success": False, "message": "Monto no proporcionado"}), 400

        # Actualizar el registro en la base de datos
        response = supabase.table("cobranza").update({"estado": "pagado", "monto_pagado": monto}).eq("telefono", telefono).execute()
        if response.data:
            return jsonify({"success": True, "message": "Pago registrado exitosamente"}), 200
        return jsonify({"success": False, "message": "No se pudo registrar el pago"}), 400
    except Exception as e:
        print(f"❌ Error al registrar pago: {e}")
        return jsonify({"success": False, "error": str(e)}), 500