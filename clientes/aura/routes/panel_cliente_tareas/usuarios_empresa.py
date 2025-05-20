# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/usuarios_empresa.py
# 👉 Subruta para gestión de usuarios empresa dentro del módulo de TAREAS

from flask import Blueprint, request, jsonify
from supabase import create_client
from datetime import datetime
import os
import uuid
import re

usuarios_empresa_bp = Blueprint("usuarios_empresa", __name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Función: listar_usuarios_empresa(nombre_nora)
@usuarios_empresa_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios", methods=["GET"])
def listar_usuarios_empresa(nombre_nora):
    config = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data
    empresa_id = config.get("cliente_id")
    usuarios = supabase.table("usuarios_empresa").select("*").eq("empresa_id", empresa_id).eq("activo", True).execute().data
    return jsonify(usuarios)

# ✅ Función: crear_usuario_empresa(nombre_nora, data)
@usuarios_empresa_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios", methods=["POST"])
def crear_usuario_empresa(nombre_nora):
    data = request.json
    nombre = data.get("nombre")
    correo = data.get("correo", "").lower()
    telefono = data.get("telefono", "")
    if not nombre or not correo or not telefono:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Validar formato
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return jsonify({"error": "Correo inválido"}), 400
    if not re.match(r"^\+?\d{10,15}$", telefono):
        return jsonify({"error": "Teléfono inválido"}), 400

    # Config
    config = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data
    empresa_id = config.get("cliente_id")

    # Verificar duplicados
    existentes = supabase.table("usuarios_empresa").select("*").or_(f"correo.eq.{correo},telefono.eq.{telefono}").eq("empresa_id", empresa_id).eq("activo", True).execute().data
    if existentes:
        return jsonify({"error": "Ya existe un usuario con ese correo o teléfono"}), 400

    # Validar supervisores
    if data.get("es_supervisor_tareas") and not validar_limite_supervisores(nombre_nora):
        return jsonify({"error": "Máximo de 3 supervisores activos alcanzado"}), 400

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "empresa_id": empresa_id,
        "rol": "usuario",
        "activo": True,
        "ver_todas_tareas": data.get("ver_todas_tareas", False),
        "crear_tareas_otros": data.get("crear_tareas_otros", False),
        "reasignar_tareas": data.get("reasignar_tareas", False),
        "es_supervisor_tareas": data.get("es_supervisor_tareas", False),
        "created_at": datetime.now().isoformat()
    }

    supabase.table("usuarios_empresa").insert(nuevo).execute()
    return jsonify({"status": "creado"})

# ✅ Función: editar_usuario_empresa(usuario_id, data)
@usuarios_empresa_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios/<usuario_id>", methods=["PUT"])
def editar_usuario_empresa(nombre_nora, usuario_id):
    data = request.json
    empresa_id = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data["cliente_id"]

    if data.get("es_supervisor_tareas") is True:
        if not validar_limite_supervisores(nombre_nora, excluyendo=usuario_id):
            return jsonify({"error": "Límite de supervisores alcanzado"}), 400

    data["updated_at"] = datetime.now().isoformat()
    supabase.table("usuarios_empresa").update(data).eq("id", usuario_id).eq("empresa_id", empresa_id).execute()
    return jsonify({"status": "actualizado"})

# ✅ Función: eliminar_usuario_empresa(usuario_id)
@usuarios_empresa_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios/<usuario_id>", methods=["DELETE"])
def eliminar_usuario_empresa(nombre_nora, usuario_id):
    supabase.table("usuarios_empresa").update({"activo": False}).eq("id", usuario_id).execute()
    return jsonify({"status": "desactivado"})

# ✅ Función: validar_limite_supervisores(nombre_nora, excluyendo=None)
def validar_limite_supervisores(nombre_nora, excluyendo=None):
    empresa_id = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data["cliente_id"]
    query = supabase.table("usuarios_empresa").select("id").eq("empresa_id", empresa_id).eq("es_supervisor_tareas", True).eq("activo", True)
    if excluyendo:
        query = query.neq("id", excluyendo)
    supervisores = query.execute().data
    return len(supervisores) < 3
