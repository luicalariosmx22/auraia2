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
    # Si usas FormData, recoge de request.form:
    data = request.form.to_dict(flat=True) or request.get_json(silent=True) or {}
    titulo = data.get("titulo")
    prioridad = (data.get("prioridad") or "media").strip().lower()
    fecha_limite = data.get("fecha_limite")
    rrule      = data.get("rrule")      # <-- nuevo
    dtstart    = data.get("dtstart")    # <-- nuevo
    until      = data.get("until")      # <-- nuevo
    count      = data.get("count")      # <-- nuevo
    estatus = (data.get("estatus") or "pendiente").strip().lower()
    # 🔧 Fallback a usuario de sesión si no viene en el form
    usuario_empresa_id = (data.get("usuario_empresa_id") or session.get("usuario_empresa_id") or "").strip()
    if not usuario_empresa_id:
        return jsonify({"error": "usuario_empresa_id es obligatorio"}), 400
    raw_empresa = (data.get("empresa_id") or "").strip()
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
      # campos recurrentes:
      "rrule": rrule or None,
      "dtstart": dtstart or None,
      "until": until or None,
      "count": int(count) if count else None,
    }
    if empresa_id is not None:
        tarea_data["empresa_id"] = empresa_id

    try:
        # insertar tarea principal
        supabase.table("tareas").insert(tarea_data).execute()
        # si viene recurrencia, grabar en tareas_recurrentes
        if data.get("rrule_type"):
            recurrente = {
                "tarea_id": tarea_data["id"],
                "dtstart":  data.get("fecha_inicio"),
                "rrule":    data.get("rrule_type"),
                "until":    data.get("fecha_fin") or None,
                "count":    int(data.get("count")) if data.get("count") else None,
            }
            supabase.table("tareas_recurrentes").insert(recurrente).execute()
        return jsonify({"ok": True, "tarea": tarea_data})
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