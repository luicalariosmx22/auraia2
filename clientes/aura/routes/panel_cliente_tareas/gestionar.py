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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar")
def vista_gestionar_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    if not modulo_activo_para_nora(nombre_nora, "tareas"):
        return "Módulo no activo", 403

    # -----------------------------------------------------------------
    # Permisos del usuario actual
    # -----------------------------------------------------------------
    usuario_id = session.get("usuario_empresa_id")
    # Permisos por defecto
    permisos = {
        "ver_todas_tareas": False,
        "reasignar_tareas": False,
        "es_supervisor": False,
    }
    if usuario_id:
        try:
            resp = (
                supabase.table("usuarios_clientes")
                .select(
                    "ver_todas_tareas, reasignar_tareas, "
                    "es_supervisor, es_supervisor_tareas"
                )
                .eq("id", usuario_id)
                .limit(1)  # evita PGRST116 cuando no hay filas
                .execute()
            )
            if resp.data:
                fila = resp.data[0]
                permisos.update(
                    {
                        "ver_todas_tareas": fila.get("ver_todas_tareas", False),
                        "reasignar_tareas": fila.get("reasignar_tareas", False),
                        "es_supervisor": fila.get("es_supervisor", False)
                        or fila.get("es_supervisor_tareas", False),
                    }
                )
        except Exception:
            # Si falla la consulta, conservamos los permisos mínimos
            pass

    # -----------------------------------------------------------------
    # 🔓 Asegurar visibilidad total para administradores globales
    # -----------------------------------------------------------------
    if session.get("is_admin"):
        permisos["ver_todas_tareas"] = True
        permisos["es_supervisor"] = True

    # -----------------------------------------------------------------
    # Traemos todas las tareas activas de la Nora
    # -----------------------------------------------------------------
    tareas_resp = (
        supabase.table("tareas")
        .select("*")
        .eq("nombre_nora", nombre_nora)
        .eq("activo", True)
        .execute()
    )
    todas = tareas_resp.data or []

    # -----------------------------------------------------------------
    # Filtros recibidos por querystring
    # -----------------------------------------------------------------
    q_busqueda  = request.args.get("busqueda", "").strip().lower()
    q_estatus   = request.args.get("estatus", "").strip()
    q_prioridad = request.args.get("prioridad", "").strip()
    q_empresa   = request.args.get("empresa_id", "").strip()
    q_asignado  = request.args.get("usuario_empresa_id", "").strip()
    q_ini       = request.args.get("fecha_ini", "").strip()
    q_fin       = request.args.get("fecha_fin", "").strip()

    # -----------------------------------------------------------------
    # Filtrado base según permisos (propias / todas)
    # -----------------------------------------------------------------
    if permisos.get("ver_todas_tareas") or permisos.get("es_supervisor") or not usuario_id:
        tareas = todas
    else:
        tareas = [t for t in todas if t.get("usuario_empresa_id") == usuario_id]

    # -----------------------------------------------------------------
    # Filtros avanzados
    # -----------------------------------------------------------------
    def coincide(t):
        # ya no excluimos aquí; las tareas completadas se mostrarán en su bloque aparte
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

    # -------------------------------------------------------------
    # Cargar info de empresa y asignado para cada tarea
    # -------------------------------------------------------------
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

        # 💡 la tabla ya NO tiene asignado_a; usamos usuario_empresa_id
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

    # -------------------------------------------------------------
    # Listas auxiliares para dropdowns
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # LOG de depuración
    # -------------------------------------------------------------
    logger = logging.getLogger(__name__)
    logger.info(
        f"[Tareas] Recuperadas {len(tareas)} tareas para usuario_id={usuario_id} "
        f"(Nora: {nombre_nora})"
    )
    # Para un detalle completo descomenta:
    # logger.debug("Detalles tareas: %s", tareas)

    # -----------------------------------------------------------------
    # Separar tareas por estatus para mostrar dos tablas
    # -----------------------------------------------------------------
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
        modulo_activo="tareas",
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
    empresa_id = payload.get("empresa_id") or None  # "" → None
    usuario_empresa_id = payload.get("usuario_empresa_id", usuario_id)

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
        "empresa_id": empresa_id,
        "usuario_empresa_id": usuario_empresa_id,  # ↩️ única columna vigente para responsable
    }
    tarea_data["codigo_tarea"] = generar_codigo_tarea(iniciales_usuario)

    try:
        supabase.table("tareas").insert(tarea_data).execute()
        return jsonify({"ok": True, "tarea": tarea_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500