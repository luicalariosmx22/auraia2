from datetime import datetime
from datetime import date
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar")
def vista_gestionar_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    if not modulo_activo_para_nora(nombre_nora, "tareas"):
        return "Módulo no activo", 403

    usuario_id = session.get("usuario_empresa_id")
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
        if q_busqueda and q_busqueda not in (t.get("titulo","").lower() + " " + t.get("descripcion","").lower()):
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
        # 🚨 Agregar esta línea para calcular días restantes
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
    logger.info(
        f"[Tareas] Recuperadas {len(tareas)} tareas para usuario_id={usuario_id} (Nora: {nombre_nora})"
    )

    tareas_activas     = [t for t in tareas if t.get("estatus", "").strip() != "completada"]
    tareas_completadas = [t for t in tareas if t.get("estatus", "").strip() == "completada"]

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas_activas=tareas_activas,
        tareas_completadas=tareas_completadas,
        permisos=permisos,
        usuarios=usuarios,
        empresas=empresas,
        user={"name": session.get("name", "Usuario"), "id": usuario_id},
        modulo_activo="tareas"
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
    form = request.form.to_dict()
    titulo = (form.get("titulo") or "").strip()
    prioridad = (form.get("prioridad") or "media").strip().lower()
    fecha_limite = form.get("fecha_limite")
    estatus = (form.get("estatus") or "pendiente").strip().lower()
    usuario_empresa_id = (form.get("usuario_empresa_id") or "").strip()
    raw_empresa = (form.get("empresa_id") or "").strip()
    empresa_id = raw_empresa if raw_empresa else None

    # Validaciones mínimas
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    if prioridad not in ("baja", "media", "alta"):
        return jsonify({"error": "Prioridad inválida"}), 400
    if estatus not in ("pendiente", "en progreso", "retrasada", "completada"):
        return jsonify({"error": "Estatus inválido"}), 400
    if not usuario_empresa_id or usuario_empresa_id.lower() == "none":
        usuario_empresa_id = session.get("usuario_empresa_id") or None
    if not usuario_empresa_id:
        return jsonify({"error": "No se puede determinar el usuario asignado"}), 400

    # Normalizar campos UUID vacíos a None
    if empresa_id == "":
        empresa_id = None
    if usuario_empresa_id == "":
        usuario_empresa_id = None

    # Validar existencia del usuario asignado
    usr_check = supabase.table("usuarios_clientes") \
        .select("id") \
        .eq("id", usuario_empresa_id) \
        .limit(1) \
        .execute()
    if not usr_check.data:
        return jsonify({"error": "Usuario asignado inválido"}), 400

    creado_por = session.get("usuario_empresa_id") or "Nora"
    nombre_usuario = session.get("name", "NN")
    iniciales_usuario = nombre_usuario.split(" ")[:2]

    tarea_data = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "titulo": titulo,
        "prioridad": prioridad,
        "fecha_limite": fecha_limite,
        "estatus": estatus,
        "usuario_empresa_id": usuario_empresa_id,
        "creado_por": creado_por,
        "codigo_tarea": generar_codigo_tarea(iniciales_usuario),
    }
    if empresa_id is not None:
        tarea_data["empresa_id"] = empresa_id

    try:
        supabase.table("tareas").insert(tarea_data).execute()

        # Guardar configuración de recurrencia si aplica
        if form.get("recurrente") == "true":
            rrule = (form.get("rrule") or "").strip()
            dtstart = form.get("dtstart") or fecha_limite  # fallback si no lo envían
            until = form.get("until") or None
            count = form.get("count") or None

            if not rrule or not dtstart:
                return jsonify({"error": "RRULE y fecha inicio requeridas"}), 400

            try:
                count = int(count)
            except (ValueError, TypeError):
                count = None

            tarea_recurrente = {
                "id": str(uuid.uuid4()),
                "tarea_id": tarea_data["id"],
                "dtstart": dtstart,
                "rrule": rrule,
                "until": until,
                "count": count,
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            try:
                supabase.table("tareas_recurrentes").insert(tarea_recurrente).execute()
            except Exception as e:
                return jsonify({"ok": True, "warning": f"Tarea creada pero falló guardar la recurrencia: {e}"}), 200

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: obtener tarea por ID
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/obtener/<tarea_id>", methods=["GET"])
def obtener_tarea(nombre_nora, tarea_id):
    try:
        tarea = supabase.table("tareas").select("*") \
            .eq("id", tarea_id).eq("nombre_nora", nombre_nora).limit(1).execute()
        if not tarea.data:
            return jsonify({"error": "Tarea no encontrada"}), 404
        # Aseguramos que descripcion esté presente (aunque sea vacío)
        t = tarea.data[0]
        if "descripcion" not in t:
            t["descripcion"] = ""
        return jsonify(t)
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