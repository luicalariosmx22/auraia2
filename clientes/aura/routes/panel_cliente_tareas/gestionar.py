from datetime import datetime
import uuid
import logging

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify,
)

from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.generar_codigo_tarea import generar_codigo_tarea

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar_bp", __name__)

# -------------------------------------------------------------------
# VISTA PRINCIPAL: listado de tareas (gestión)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/<nombre_nora>/tareas/gestionar")
def gestionar_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    user = session.get("user", {})
    if not user:
        return "❌ Sesión inválida", 403

    if session.get("nombre_nora") != nombre_nora:
        return "❌ No autorizado para esta Nora", 403

    tipo = "usuario_cliente"
    if session.get("is_admin"):
        if session.get("nombre_nora") == "admin":
            tipo = "admin_global"
        else:
            tipo = "cliente_admin"

    print("🧪 USUARIO LOGUEADO")
    print(f"🧪 Correo: {session.get('email')}")
    print(f"🧪 Nombre: {user.get('nombre')}")
    print(f"🧪 Tipo: {tipo}")

    usuarios = supabase.table("usuarios_clientes").select("id,nombre").eq("nombre_nora", nombre_nora).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id,nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    tareas = supabase.table("tareas").select("*").eq("activo", True).eq("nombre_nora", nombre_nora).order("fecha_limite").execute().data or []
    tareas_activas = [t for t in tareas if t["estatus"] != "completada"]
    tareas_completadas = [t for t in tareas if t["estatus"] == "completada"]

    permisos = {
        "es_supervisor": session.get("is_admin", False)
    }

    is_admin = session.get("is_admin", False)

    return render_template("panel_cliente_tareas/gestionar.html",
                           nombre_nora=nombre_nora,
                           tareas_activas=tareas_activas,
                           tareas_completadas=tareas_completadas,
                           usuarios=usuarios,
                           empresas=empresas,
                           permisos=permisos,
                           user=user,
                           is_admin=is_admin)

# -------------------------------------------------------------------
# API: actualizar campo (inline edit)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/gestionar/actualizar/<tarea_id>",
    methods=["POST"],
)
def actualizar_campo_tarea(nombre_nora, tarea_id):
    payload = request.get_json(silent=True) or {}
    campo = payload.get("campo")
    valor = payload.get("valor")

    if campo not in [
        "titulo",
        "prioridad",
        "fecha_limite",
        "estatus",
        "usuario_empresa_id",  # ← Único campo para “Asignado a”
        "empresa_id",
    ]:
        return jsonify({"error": "Campo no permitido"}), 400

    # Validaciones de valor
    if campo == "prioridad":
        valor = (valor or "").strip().lower()
        if valor not in ("alta", "media", "baja"):
            return jsonify({"error": "Prioridad inválida"}), 400
    if campo == "estatus" and valor not in [
        "pendiente",
        "en progreso",
        "retrasada",
        "completada",
    ]:
        return jsonify({"error": "Estatus inválido"}), 400

    try:
        supabase.table("tareas").update(
            {campo: valor, "updated_at": datetime.utcnow().isoformat()}
        ).eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: crear tarea nueva
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/gestionar/crear", methods=["POST"]
)
def crear_tarea(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    usuario_id = session.get("usuario_empresa_id")
    if not usuario_id:
        return jsonify({"error": "Usuario no identificado"}), 403

    payload = request.get_json(silent=True) or {}
    titulo = payload.get("titulo")
    prioridad = (payload.get("prioridad") or "media").strip().lower()
    fecha_limite = payload.get("fecha_limite")
    estatus = payload.get("estatus", "pendiente")
    # ─── Saneamos cadenas vacías para uuid de empresa ─────────────────
    raw_empresa = (payload.get("empresa_id") or "").strip()
    empresa_id = raw_empresa or None   # "" → None para permitir NULL
    # ─── Determinar si el usuario puede asignar a otros (admin o supervisor) ─
    resp_priv = supabase.table("usuarios_clientes") \
        .select("es_supervisor, es_supervisor_tareas") \
        .eq("id", usuario_id) \
        .limit(1) \
        .execute()
    fila_priv = resp_priv.data[0] if resp_priv.data else {}
    is_supervisor = session.get("is_admin") \
        or fila_priv.get("es_supervisor", False) \
        or fila_priv.get("es_supervisor_tareas", False)
    raw_usuario = (payload.get("usuario_empresa_id") or "").strip()
    if is_supervisor:
        # Admin/supervisor debe elegir un usuario asignado
        if not raw_usuario:
            return jsonify({"error": "Debe seleccionar un usuario asignado"}), 400
        usuario_empresa_id = raw_usuario
    else:
        # Usuario normal solo puede auto-asignarse
        usuario_empresa_id = usuario_id
    # ─── Validar que el usuario_empresa_id exista en usuarios_clientes ────
    usr_check = supabase.table("usuarios_clientes") \
        .select("id") \
        .eq("id", usuario_empresa_id) \
        .limit(1) \
        .execute()
    if not usr_check.data:
        return jsonify({"error": "Usuario asignado inválido"}), 400

    # -----------------------------------------------------------------
    # Prints de depuración de variables recibidas y calculadas
    # -----------------------------------------------------------------
    print("=== crear_tarea ===")
    print(f"payload: {payload}")
    print(f"titulo: {titulo}")
    print(f"prioridad: {prioridad}")
    print(f"fecha_limite: {fecha_limite}")
    print(f"estatus: {estatus}")
    print(f"raw_empresa: {raw_empresa}")
    print(f"empresa_id: {empresa_id}")
    print(f"raw_usuario: {raw_usuario}")
    print(f"usuario_empresa_id: {usuario_empresa_id}")
    print(f"usuario_id (sesión): {usuario_id}")
    print(f"is_admin: {session.get('is_admin')}")
    print(f"nombre_nora: {nombre_nora}")

    # -----------------------------------------------------------------
    # Validaciones
    # -----------------------------------------------------------------
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    if prioridad not in ("alta", "media", "baja"):
        return jsonify({"error": "Prioridad inválida"}), 400
    if estatus not in ("pendiente", "en progreso", "retrasada", "completada"):
        return jsonify({"error": "Estatus inválido"}), 400
    # empresa_id *puede* ser None → la FK admite NULL

    # -----------------------------------------------------------------
    # Crear tarea
    # -----------------------------------------------------------------
    # el nombre de sesión puede ser None → convertimos a cadena segura
    nombre_sesion = (session.get("nombre") or "").strip()
    iniciales_usuario = nombre_sesion.split(" ")[:2] if nombre_sesion else ["NN"]

    tarea_data = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "titulo": titulo,
        "prioridad": prioridad,
        "fecha_limite": fecha_limite,
        "estatus": estatus,
        "usuario_empresa_id": usuario_empresa_id,  # ↩️ única columna vigente para responsable
        # registrar quién creó la tarea
        "creado_por": session.get("usuario_empresa_id") or None,
    }
    if empresa_id:
        tarea_data["empresa_id"] = empresa_id

    tarea_data["codigo_tarea"] = generar_codigo_tarea(iniciales_usuario)

    try:
        supabase.table("tareas").insert(tarea_data).execute()
        return jsonify({"ok": True, "tarea": tarea_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500