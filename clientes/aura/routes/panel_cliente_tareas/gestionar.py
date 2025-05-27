from datetime import datetime
import uuid

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
    # Filtrado de tareas según permisos
    # -----------------------------------------------------------------
    if permisos.get("ver_todas_tareas") or permisos.get("es_supervisor") or not usuario_id:
        tareas_resp = (
            supabase.table("tareas")
            .select("*")
            .eq("nombre_nora", nombre_nora)
            .eq("activo", True)
            .execute()
        )
    else:
        # 👉 Mostrar tareas creadas POR el usuario *o* asignadas A él (sin usar .or_)
        tareas_lista = []

        # Tareas creadas por el usuario
        try:
            resp_creadas = (
                supabase.table("tareas")
                .select("*")
                .eq("nombre_nora", nombre_nora)
                .eq("activo", True)
                .eq("usuario_empresa_id", usuario_id)
                .execute()
            )
            if resp_creadas.data:
                tareas_lista.extend(resp_creadas.data)
        except Exception:
            pass

        # Tareas asignadas al usuario
        try:
            resp_asignadas = (
                supabase.table("tareas")
                .select("*")
                .eq("nombre_nora", nombre_nora)
                .eq("activo", True)
                .eq("asignado_a", usuario_id)
                .execute()
            )
            if resp_asignadas.data:
                tareas_lista.extend(resp_asignadas.data)
        except Exception:
            pass

        # Deduplicar por ID
        tareas_resp = type("Obj", (object,), {"data": list({t["id"]: t for t in tareas_lista}.values())})()
    tareas = tareas_resp.data or []

    # Cargar info de empresa y asignado
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
        if t.get("asignado_a"):
            try:
                usr = (
                    supabase.table("usuarios_clientes")
                    .select("nombre")
                    .eq("id", t["asignado_a"])
                    .limit(1)
                    .execute()
                )
                if usr.data:
                    t["asignado_nombre"] = usr.data[0]["nombre"]
            except Exception:
                t["asignado_nombre"] = ""

    # -----------------------------------------------------------------
    # Listas auxiliares para dropdowns
    # -----------------------------------------------------------------
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

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas=tareas,
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
        "usuario_empresa_id",
        "empresa_id",
    ]:
        return jsonify({"error": "Campo no permitido"}), 400

    # Validaciones de valor
    if campo == "prioridad" and valor not in ["alta", "media", "baja"]:
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
    prioridad = payload.get("prioridad", "media")
    fecha_limite = payload.get("fecha_limite")
    estatus = payload.get("estatus", "pendiente")
    empresa_id = payload.get("empresa_id")
    usuario_empresa_id = payload.get("usuario_empresa_id", usuario_id)

    # -----------------------------------------------------------------
    # Validaciones
    # -----------------------------------------------------------------
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    if prioridad not in ["alta", "media", "baja"]:
        return jsonify({"error": "Prioridad inválida"}), 400
    if estatus not in ["pendiente", "en progreso", "retrasada", "completada"]:
        return jsonify({"error": "Estatus inválido"}), 400
    if not empresa_id:
        return jsonify({"error": "La empresa es obligatoria"}), 400

    # -----------------------------------------------------------------
    # Crear tarea
    # -----------------------------------------------------------------
    iniciales_usuario = (
        session.get("nombre")
        .strip()
        .split(" ")
    )[:2]  # Tomar hasta 2 palabras del nombre

    tarea_data = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "titulo": titulo,
        "prioridad": prioridad,
        "fecha_limite": fecha_limite,
        "estatus": estatus,
        "empresa_id": empresa_id,
        "usuario_empresa_id": usuario_empresa_id,
        "asignado_a": usuario_empresa_id,  # ✅ rellenamos también asignado_a para compatibilidad futura
    }
    tarea_data["codigo_tarea"] = generar_codigo_tarea(iniciales_usuario)

    try:
        supabase.table("tareas").insert(tarea_data).execute()
        return jsonify({"ok": True, "tarea": tarea_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500