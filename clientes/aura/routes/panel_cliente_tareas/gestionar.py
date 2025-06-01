from datetime import datetime
from datetime import date
import uuid
import logging
import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    url_for,
    flash
)

from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.generar_codigo_tarea import generar_codigo_tarea

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar_bp", __name__)

# -------------------------------------------------------------------
# VISTA PRINCIPAL: listado de tareas (gestión)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar", methods=["GET", "POST"])
def gestionar_tareas(nombre_nora):
    if request.method == "POST":
        return crear_tarea(nombre_nora)
    return vista_gestionar_tareas(nombre_nora)

# -------------------------------------------------------------------
# VISTA RENDER: solo para GET
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/vista")
def vista_gestionar_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    if not modulo_activo_para_nora(nombre_nora, "tareas"):
        return "Módulo no activo", 403

    usuario_id = session.get("usuario_empresa_id")
    if not usuario_id:
        user = session.get("user", {})
        usuario_id = user.get("usuario_empresa_id") or user.get("id")
        if usuario_id:
            session["usuario_empresa_id"] = usuario_id

    if not usuario_id and os.getenv("FLASK_ENV") == "development":
        print("🧪 Simulación de sesión en modo local")
        usuario_id = "00000000-0000-0000-0000-000000000000"
        session["usuario_empresa_id"] = usuario_id

    permisos = {
        "es_supervisor": session.get("rol") == "supervisor"
    }

    tareas_resp = (
        supabase.table("tareas")
        .select("*")
        .eq("nombre_nora", nombre_nora)
        .eq("activo", True)
        .execute()
    )
    todas = tareas_resp.data or []

    q_busqueda  = request.args.get("busqueda", "").strip().lower()
    q_estatus   = request.args.get("estatus", "").strip()
    q_prioridad = request.args.get("prioridad", "").strip()
    q_empresa   = request.args.get("empresa_id", "").strip()
    q_asignado  = request.args.get("usuario_empresa_id", "").strip()
    q_ini       = request.args.get("fecha_ini", "").strip()
    q_fin       = request.args.get("fecha_fin", "").strip()

    tareas = todas

    def coincide(t):
        if q_busqueda and q_busqueda not in (t.get("titulo","" ).lower() + " " + t.get("descripcion", "").lower()):
            return False
        if q_estatus and t.get("estatus") != q_estatus:
            return False
        if q_prioridad and t.get("prioridad") != q_prioridad:
            return False
        if q_empresa and (t.get("empresa_id") or "") != q_empresa:
            return False
        if q_asignado and (t.get("usuario_empresa_id") or "") != q_asignado:
            return False
        if q_ini and (t.get("fecha_limite") or "") < q_ini:
            return False
        if q_fin and (t.get("fecha_limite") or "") > q_fin:
            return False
        return True

    tareas = [t for t in tareas if coincide(t)]

    filtro_tipo = request.args.get("tipo", "").strip().lower()
    if filtro_tipo == "recurrente":
        tareas = [t for t in tareas if t.get("recurrente") is True]

    for t in tareas:
        if t.get("empresa_id"):
            try:
                emp = (
                    supabase.table("cliente_empresas")
                    .select("nombre_empresa")
                    .eq("id", t["empresa_id"])
                    .limit(1)
                    .execute()
                )
                if emp.data:
                    t["empresa_nombre"] = emp.data[0]["nombre_empresa"]
            except Exception:
                t["empresa_nombre"] = ""
        if t.get("usuario_empresa_id"):
            try:
                usr = (
                    supabase.table("usuarios_clientes")
                    .select("nombre")
                    .eq("id", t["usuario_empresa_id"])
                    .limit(1)
                    .execute()
                )
                if usr.data:
                    t["asignado_nombre"] = usr.data[0]["nombre"]
            except Exception:
                t["asignado_nombre"] = ""
        if t.get("fecha_limite"):
            try:
                t["dias_restantes"] = (date.fromisoformat(t["fecha_limite"]) - date.today()).days
            except Exception:
                t["dias_restantes"] = None
        else:
            t["dias_restantes"] = None

    usuarios_resp = (
        supabase.table("usuarios_clientes")
        .select("id, nombre")
        .eq("nombre_nora", nombre_nora)
        .eq("activo", True)
        .execute()
    )
    usuarios = usuarios_resp.data or []

    empresas_resp = (
        supabase.table("cliente_empresas")
        .select("id, nombre_empresa")
        .eq("nombre_nora", nombre_nora)
        .execute()
    )
    empresas = empresas_resp.data or []

    logger = logging.getLogger(__name__)
    logger.info(f"[Tareas] Recuperadas {len(tareas)} tareas para usuario_id={usuario_id} (Nora: {nombre_nora})")

    tareas_activas     = [t for t in tareas if t.get("estatus", "").strip() != "completada"]
    tareas_completadas = [t for t in tareas if t.get("estatus", "").strip() == "completada"]

    resumen = {
        "tareas_activas": len(tareas_activas),
        "tareas_completadas": len(tareas_completadas),
        "tareas_vencidas": len([t for t in tareas_activas if t.get("dias_restantes", 0) < 0]),
        "porcentaje_cumplimiento": 0
    }
    total = resumen["tareas_activas"] + resumen["tareas_completadas"] + resumen["tareas_vencidas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    cliente_id = session.get("cliente_id")
    if cliente_id:
        alertas_data = supabase.table("alertas_ranking") \
            .select("data") \
            .eq("cliente_id", cliente_id) \
            .single() \
            .execute().data
    else:
        alertas_data = None

    alertas = alertas_data["data"] if alertas_data and "data" in alertas_data else {}

    user = session.get("user", {})
    nombre_usuario = user.get("nombre", "Usuario")
    mensaje_bienvenida = f"Hola {nombre_usuario}, aquí puedes gestionar tus tareas. Asegúrate de mantener tus pendientes actualizados para un mejor seguimiento."

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,  # <-- Agrega esta línea
        tareas=tareas,
        resumen=resumen,
        usuarios=usuarios,
        mensaje_bienvenida=mensaje_bienvenida,
        tareas_activas=tareas_activas,
        tareas_completadas=tareas_completadas,
        permisos=permisos,
        empresas=empresas,
        user={"name": session.get("name", "Usuario"), "id": usuario_id},
        modulo_activo="tareas",
        alertas=alertas
    )

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

    permisos = {
        "es_supervisor": session.get("rol") == "supervisor",
        "es_superadmin": session.get("rol") == "superadmin",
        "es_cliente": session.get("rol") == "cliente"
    }

    campos_restringidos = ["usuario_empresa_id", "empresa_id", "fecha_limite"]

    # Permitir sólo a supervisor o superadmin modificar campos restringidos
    if campo in campos_restringidos and not (permisos["es_supervisor"] or permisos["es_superadmin"]):
        return jsonify({"error": "No tienes permiso para modificar este campo"}), 403

    # Si es cliente, solo puede modificar ciertos campos
    if permisos["es_cliente"]:
        campos_permitidos_cliente = ["estatus", "titulo", "descripcion"]
        if campo not in campos_permitidos_cliente:
            return jsonify({"error": "No tienes permiso para modificar este campo"}), 403

    if campo not in [
        "titulo",
        "prioridad",
        "fecha_limite",
        "estatus",
        "usuario_empresa_id",
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
    if campo == "fecha_limite":
        try:
            datetime.strptime(valor, "%Y-%m-%d")  # Validar formato de fecha
        except ValueError:
            return jsonify({"error": "Fecha límite inválida"}), 400

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
    data = request.form.to_dict(flat=True) or request.get_json(silent=True) or {}

    titulo = data.get("titulo")
    prioridad = (data.get("prioridad") or "media").strip().lower()
    fecha_limite = data.get("fecha_limite")
    estatus = (data.get("estatus") or "pendiente").strip().lower()

    usuario_empresa_id = (data.get("usuario_empresa_id") or session.get("usuario_empresa_id") or "").strip()
    if not usuario_empresa_id or usuario_empresa_id.lower() == "none":
        return jsonify({"error": "No se puede determinar el usuario asignado"}), 400

    empresa_id = (data.get("empresa_id") or "").strip() or None

    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    if prioridad not in ("baja", "media", "alta"):
        return jsonify({"error": "Prioridad inválida"}), 400
    if estatus not in ("pendiente", "en progreso", "retrasada", "completada"):
        return jsonify({"error": "Estatus inválido"}), 400

    usr_check = supabase.table("usuarios_clientes") \
        .select("id") \
        .eq("id", usuario_empresa_id) \
        .limit(1) \
        .execute()
    if not usr_check.data:
        return jsonify({"error": "Usuario asignado inválido"}), 400

    creado_por = session.get("usuario_empresa_id") or "Nora"
    nombre_usuario = session.get("name", "NN")
    iniciales_usuario = "".join([s[0] for s in nombre_usuario.split()[:2]])

    tarea_data = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "titulo": titulo,
        "prioridad": prioridad,
        "fecha_limite": fecha_limite,
        "estatus": estatus,
        "usuario_empresa_id": usuario_empresa_id,
        "empresa_id": empresa_id,
        "codigo_tarea": generar_codigo_tarea(iniciales_usuario),
        "origen": "manual",
        "activo": True,
        "creado_por": creado_por,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        supabase.table("tareas").insert(tarea_data).execute()
        # Eliminada la inserción a tabla tareas_recurrentes para evitar error
        return jsonify({"ok": True, "tarea": tarea_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: obtener tarea por ID
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/obtener/<tarea_id>", methods=["GET"])
def obtener_tarea(nombre_nora, tarea_id):
    try:
        tarea_resp = supabase.table("tareas").select("*").eq("id", tarea_id).eq("nombre_nora", nombre_nora).limit(1).execute()
        if not tarea_resp.data:
            return jsonify({"error": "Tarea no encontrada"}), 404
        tarea = tarea_resp.data[0]

        # Agregar nombre de empresa
        tarea["empresa_nombre"] = ""
        if tarea.get("empresa_id"):
            emp_resp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", tarea["empresa_id"]).limit(1).execute()
            if emp_resp.data:
                tarea["empresa_nombre"] = emp_resp.data[0]["nombre_empresa"]

        # Agregar nombre de usuario asignado
        tarea["asignado_nombre"] = ""
        if tarea.get("usuario_empresa_id"):
            usr_resp = supabase.table("usuarios_clientes").select("nombre").eq("id", tarea["usuario_empresa_id"]).limit(1).execute()
            if usr_resp.data:
                tarea["asignado_nombre"] = usr_resp.data[0]["nombre"]

        # Asegurar descripción
        if "descripcion" not in tarea:
            tarea["descripcion"] = ""

        return jsonify(tarea)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: eliminar tarea (marcar como inactiva)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/eliminar/<tarea_id>", methods=["POST"])
def eliminar_tarea(nombre_nora, tarea_id):
    try:
        supabase.table("tareas").update({
            "activo": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", tarea_id).eq("nombre_nora", nombre_nora).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500