# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/usuarios_clientes.py
# 👉 Subruta para gestión de usuarios empresa dentro del módulo de TAREAS

from flask import Blueprint, request, jsonify, render_template, session
from .panel_cliente_tareas import panel_cliente_tareas_bp
from supabase import create_client
from datetime import datetime
import os
import uuid
import re

usuarios_clientes_bp = Blueprint("usuarios_clientes", __name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Función: listar_usuarios_clientes(nombre_nora)
@usuarios_clientes_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios", methods=["GET"])
def listar_usuarios_clientes(nombre_nora):
    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data
    return jsonify(usuarios)

# ✅ Función: crear_usuario_empresa(nombre_nora, data)
@usuarios_clientes_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios", methods=["POST"])
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
    existentes = supabase.table("usuarios_clientes").select("*").or_(f"correo.eq.{correo},telefono.eq.{telefono}").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data
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
        "nombre_nora": nombre_nora,
        "rol": "usuario",
        "activo": True,
        "ver_todas_tareas": data.get("ver_todas_tareas", False),
        "crear_tareas_otros": data.get("crear_tareas_otros", False),
        "reasignar_tareas": data.get("reasignar_tareas", False),
        "es_supervisor_tareas": data.get("es_supervisor_tareas", False),
        "created_at": datetime.now().isoformat()
    }

    supabase.table("usuarios_clientes").insert(nuevo).execute()
    return jsonify({"status": "creado"})

# ✅ Función: editar_usuario_empresa(usuario_id, data)
@usuarios_clientes_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios/<usuario_id>", methods=["PUT"])
def editar_usuario_empresa(nombre_nora, usuario_id):
    data = request.json
    empresa_id = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data["cliente_id"]

    if data.get("es_supervisor_tareas") is True:
        if not validar_limite_supervisores(nombre_nora, excluyendo=usuario_id):
            return jsonify({"error": "Límite de supervisores alcanzado"}), 400

    data["updated_at"] = datetime.now().isoformat()
    supabase.table("usuarios_clientes").update(data).eq("id", usuario_id).eq("nombre_nora", nombre_nora).execute()
    return jsonify({"status": "actualizado"})

# ✅ Función: eliminar_usuario_empresa(usuario_id)
@usuarios_clientes_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios/<usuario_id>", methods=["DELETE"])
def eliminar_usuario_empresa(nombre_nora, usuario_id):
    supabase.table("usuarios_clientes").update({"activo": False}).eq("id", usuario_id).execute()
    return jsonify({"status": "desactivado"})

# ✅ Función: validar_limite_supervisores(nombre_nora, excluyendo=None)
def validar_limite_supervisores(nombre_nora, excluyendo=None):
    empresa_id = supabase.table("configuracion_bot").select("cliente_id").eq("nombre_nora", nombre_nora).single().execute().data["cliente_id"]
    query = supabase.table("usuarios_clientes").select("id").eq("nombre_nora", nombre_nora).eq("es_supervisor_tareas", True).eq("activo", True)
    if excluyendo:
        query = query.neq("id", excluyendo)
    supervisores = query.execute().data
    return len(supervisores) < 3

# ✅ Listar todos los usuarios del cliente
@panel_cliente_tareas_bp.route("/usuarios/<nombre_nora>", methods=["GET"])
def listar_usuarios(nombre_nora):
    usuarios = supabase.table("usuarios_clientes").select("*") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    return jsonify(usuarios)

# ✅ Crear un nuevo usuario del equipo
@panel_cliente_tareas_bp.route("/usuarios/<nombre_nora>/crear", methods=["POST"])
def crear_usuario(nombre_nora):
    data = request.get_json()

    # Verificar duplicados por correo o teléfono
    existentes = supabase.table("usuarios_clientes").select("id").or_(
        f"correo.eq.{data['correo']},telefono.eq.{data['telefono']}"
    ).eq("nombre_nora", nombre_nora).eq("activo", True).execute().data

    if existentes:
        return jsonify({"success": False, "error": "Usuario ya existe"}), 400

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": data["nombre"],
        "correo": data["correo"],
        "telefono": data["telefono"],
        "nombre_nora": nombre_nora,
        "ver_todas_tareas": data.get("ver_todas_tareas", False),
        "crear_tareas_otros": data.get("crear_tareas_otros", False),
        "reasignar_tareas": data.get("reasignar_tareas", False),
        "es_supervisor_tareas": data.get("es_supervisor_tareas", False),
        "activo": True,
        "created_at": datetime.now().isoformat()
    }

    supabase.table("usuarios_clientes").insert(nuevo).execute()
    return jsonify({"success": True})

# ✅ Editar un usuario existente
@panel_cliente_tareas_bp.route("/usuarios/<nombre_nora>/editar/<usuario_id>", methods=["PUT"])
def editar_usuario(nombre_nora, usuario_id):
    data = request.get_json()

    campos = {
        "nombre": data.get("nombre"),
        "correo": data.get("correo"),
        "telefono": data.get("telefono"),
        "ver_todas_tareas": data.get("ver_todas_tareas", False),
        "crear_tareas_otros": data.get("crear_tareas_otros", False),
        "reasignar_tareas": data.get("reasignar_tareas", False),
        "es_supervisor_tareas": data.get("es_supervisor_tareas", False),
        "updated_at": datetime.now().isoformat()
    }

    supabase.table("usuarios_clientes").update(campos).eq("id", usuario_id).execute()
    return jsonify({"success": True})

# ✅ Eliminar usuario (soft delete)
@panel_cliente_tareas_bp.route("/usuarios/<nombre_nora>/eliminar/<usuario_id>", methods=["DELETE"])
def eliminar_usuario(nombre_nora, usuario_id):
    supabase.table("usuarios_clientes").update({
        "activo": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", usuario_id).execute()
    return jsonify({"success": True})

# ✅ Validar límite de supervisores (máx. 3)
def validar_maximo_supervisores(nombre_nora):
    supervisores = supabase.table("usuarios_clientes").select("id") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).eq("es_supervisor_tareas", True).execute().data or []
    return len(supervisores) < 3

@usuarios_clientes_bp.route("/panel_cliente/<nombre_nora>/tareas/usuarios", methods=["GET"])
def vista_usuarios(nombre_nora):
    user = session.get("user", {})
    
    usuarios = supabase.table("usuarios_clientes").select("*") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    config = {
        "max_supervisores_tareas": 3
    }

    supervisores_activos = len([u for u in usuarios if u.get("es_supervisor_tareas")])

    return render_template(
        "panel_cliente_tareas/usuarios.html",
        usuarios=usuarios,
        nombre_nora=nombre_nora,
        user=user,
        config=config,
        supervisores_activos=supervisores_activos
    )

