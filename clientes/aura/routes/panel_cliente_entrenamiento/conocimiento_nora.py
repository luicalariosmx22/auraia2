# ✅ Archivo: clientes/aura/routes/panel_cliente_entrenamiento/conocimiento_nora.py
# 👉 Endpoints para manejar bloques de conocimiento manual de Nora desde el panel del cliente

from flask import Blueprint, request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_conocimiento_bp = Blueprint("panel_cliente_conocimiento", __name__)

# 📥 Obtener bloques de conocimiento activos
@panel_cliente_conocimiento_bp.route("/panel/cliente/<cliente_id>/nora/<nombre_nora>/entrenar/bloques", methods=["GET"])
def obtener_conocimiento_nora(cliente_id, nombre_nora):
    try:
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("cliente_id", cliente_id) \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ➕ Agregar nuevo bloque
@panel_cliente_conocimiento_bp.route("/panel/cliente/<cliente_id>/nora/<nombre_nora>/entrenar/bloques", methods=["POST"])
def agregar_conocimiento_nora(cliente_id, nombre_nora):
    try:
        body = request.get_json()
        contenido = body.get("contenido", "").strip()
        etiquetas = body.get("etiquetas", [])
        prioridad = bool(body.get("prioridad", False))

        if not contenido or len(contenido) > 500:
            return jsonify({"success": False, "message": "Contenido inválido"}), 400

        nuevo = {
            "id": str(uuid.uuid4()),
            "cliente_id": cliente_id,
            "nombre_nora": nombre_nora,
            "contenido": contenido,
            "etiquetas": etiquetas,
            "origen": "manual",
            "prioridad": prioridad,
            "activo": True,
            "fecha_creacion": datetime.utcnow().isoformat()
        }

        res = supabase.table("conocimiento_nora").insert(nuevo).execute()
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 🗑️ Eliminar bloque
@panel_cliente_conocimiento_bp.route("/panel/cliente/<cliente_id>/nora/<nombre_nora>/entrenar/bloques/<id_bloque>", methods=["DELETE"])
def eliminar_conocimiento_nora(cliente_id, nombre_nora, id_bloque):
    try:
        res = supabase.table("conocimiento_nora") \
            .update({"activo": False}) \
            .eq("id", id_bloque) \
            .eq("cliente_id", cliente_id) \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 📝 Editar bloque existente
@panel_cliente_conocimiento_bp.route("/panel/cliente/<cliente_id>/nora/<nombre_nora>/entrenar/bloques/<id_bloque>", methods=["PUT"])
def editar_conocimiento_nora(cliente_id, nombre_nora, id_bloque):
    try:
        body = request.get_json()
        contenido = body.get("contenido", "").strip()
        etiquetas = body.get("etiquetas", [])
        prioridad = bool(body.get("prioridad", False))

        if not contenido or len(contenido) > 500:
            return jsonify({"success": False, "message": "Contenido inválido"}), 400

        actualizado = {
            "contenido": contenido,
            "etiquetas": etiquetas,
            "prioridad": prioridad,
            "fecha_modificacion": datetime.utcnow().isoformat()
        }

        res = supabase.table("conocimiento_nora") \
            .update(actualizado) \
            .eq("id", id_bloque) \
            .eq("cliente_id", cliente_id) \
            .eq("nombre_nora", nombre_nora) \
            .eq("activo", True) \
            .execute()
        
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
