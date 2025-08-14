# ✅ Archivo: clientes/aura/routes/panel_cliente_bienes_raices/social.py
# 👉 Endpoint para publicar/colar en cola de redes sociales
from flask import Blueprint, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from .crud import TABLE_SOCIAL_QUEUE, generar_copy_social
from .crud import _sb as _sb_crud, _base_query as _baseq

br_social_bp = Blueprint("br_social_bp", __name__)

@br_social_bp.route("/publicar/<prop_id>", methods=["POST"])
def publicar_en_redes(nombre_nora, prop_id):
    try:
        # Carga propiedad
        res = _baseq(nombre_nora).eq("id", prop_id).limit(1).execute()
        prop = (res.data or [None])[0]
        if not prop:
            return jsonify({"success": False, "message": "Propiedad no encontrada"}), 404

        payload = request.get_json(silent=True) or {}
        plataformas = payload.get("plataformas", ["facebook", "instagram"])
        imagenes = payload.get("imagenes", [])
        copy = payload.get("copy") or generar_copy_social(prop)

        _sb = supabase
        _sb.table(TABLE_SOCIAL_QUEUE).insert({
            "propiedad_id": prop_id,
            "plataformas": plataformas,
            "estado": "pendiente",
            "payload": {"copy": copy, "imagenes": imagenes}
        }).execute()

        return jsonify({"success": True, "en_cola": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
