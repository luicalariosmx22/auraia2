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
from clientes.aura.utils.permisos import obtener_permisos
from clientes.aura.utils.permisos_tareas import puede_crear_para_otros

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

    usuario_id = session.get("usuario_empresa_id") or session.get("user", {}).get("usuario_empresa_id") or session.get("user", {}).get("id")
    if usuario_id:
        session["usuario_empresa_id"] = usuario_id

    if not usuario_id and os.getenv("FLASK_ENV") == "development":
        print("🧪 Simulación de sesión en modo local")
        usuario_id = "00000000-0000-0000-0000-000000000000"
        session["usuario_empresa_id"] = usuario_id

    # 👇 Lógica de permisos personalizada
    permisos = {
        "es_supervisor": session.get("es_supervisor", False),
        "crear_para_otros": puede_crear_para_otros(usuario_id, nombre_nora),
        "es_admin": session.get("is_admin", False),
        "es_super_admin": session.get("is_super_admin", False)
    }

    tareas_resp = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    todas = tareas_resp.data or []

    # --- Lógica para marcar tareas recurrentes ---
    tareas_recurrentes_resp = supabase.table("tareas_recurrentes").select("tarea_id").execute()
    tarea_ids_recurrentes = set(r["tarea_id"] for r in (tareas_recurrentes_resp.data or []))
    for t in todas:
        if t.get("id") in tarea_ids_recurrentes:
            t["is_recurrente"] = True
        else:
            t["is_recurrente"] = False
    # --- Fin lógica recurrente ---

    q = {
        "busqueda": request.args.get("busqueda", "").strip().lower(),
        "estatus": request.args.get("estatus", "").strip(),
        "prioridad": request.args.get("prioridad", "").strip(),
        "empresa_id": request.args.get("empresa_id", "").strip(),
        "usuario_empresa_id": request.args.get("usuario_empresa_id", "").strip(),
        "fecha_ini": request.args.get("fecha_ini", "").strip(),
        "fecha_fin": request.args.get("fecha_fin", "").strip()
    }

    def coincide(t):
        if q["busqueda"] and q["busqueda"] not in (t.get("titulo", "").lower() + " " + t.get("descripcion", "").lower()):
            return False
        if q["estatus"] and t.get("estatus") != q["estatus"]:
            return False
        if q["prioridad"] and t.get("prioridad") != q["prioridad"]:
            return False
        if q["empresa_id"] and (t.get("empresa_id") or "") != q["empresa_id"]:
            return False
        if q["usuario_empresa_id"] and (t.get("usuario_empresa_id") or "") != q["usuario_empresa_id"]:
            return False
        if q["fecha_ini"] and (t.get("fecha_limite") or "") < q["fecha_ini"]:
            return False
        if q["fecha_fin"] and (t.get("fecha_limite") or "") > q["fecha_fin"]:
            return False
        return True

    tareas = [t for t in todas if coincide(t)]

    if request.args.get("tipo", "").strip().lower() == "recurrente":
        tareas = [t for t in tareas if t.get("recurrente") is True]

    for t in tareas:
        if t.get("empresa_id"):
            try:
                emp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", t["empresa_id"]).limit(1).execute()
                t["empresa_nombre"] = emp.data[0]["nombre_empresa"] if emp.data else ""
            except Exception:
                t["empresa_nombre"] = ""
        if t.get("usuario_empresa_id"):
            try:
                usr = supabase.table("usuarios_clientes").select("nombre").eq("id", t["usuario_empresa_id"]).limit(1).execute()
                t["asignado_nombre"] = usr.data[0]["nombre"] if usr.data else ""
            except Exception:
                t["asignado_nombre"] = ""
        try:
            fecha = t.get("fecha_limite")
            t["dias_restantes"] = (date.fromisoformat(fecha) - date.today()).days if fecha else None
        except Exception:
            t["dias_restantes"] = None

    # --- Conteo de comentarios por tarea para distintivo 💬 ---
    tarea_ids = [t["id"] for t in tareas]
    if tarea_ids:
        comentarios_agregados = (
            supabase.table("tarea_comentarios")
            .select("tarea_id", "id", count="exact")
            .in_("tarea_id", tarea_ids)
            .execute()
        )
        conteos = {}
        for c in comentarios_agregados.data:
            tid = c["tarea_id"]
            conteos[tid] = conteos.get(tid, 0) + 1
        for t in tareas:
            t["comentarios_count"] = conteos.get(t["id"], 0)
    else:
        for t in tareas:
            t["comentarios_count"] = 0
    # --- Fin conteo comentarios ---
    
    usuarios = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    logger = logging.getLogger(__name__)
    logger.info(f"[Tareas] Recuperadas {len(tareas)} tareas para usuario_id={usuario_id} (Nora: {nombre_nora})")

    tareas_activas = [t for t in tareas if t.get("estatus", "").strip() != "completada"]
    tareas_completadas = [t for t in tareas if t.get("estatus", "").strip() == "completada"]
    tareas_vencidas = [t for t in tareas_activas if (t.get("dias_restantes") or 0) < 0]

    resumen = {
        "tareas_activas": len(tareas_activas),
        "tareas_completadas": len(tareas_completadas),
        "tareas_vencidas": len(tareas_vencidas),
        "porcentaje_cumplimiento": 0
    }
    total = sum(resumen.values())
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    cliente_id = session.get("cliente_id")
    alertas_data = supabase.table("alertas_ranking").select("data").eq("cliente_id", cliente_id).single().execute().data if cliente_id else None
    alertas = alertas_data["data"] if alertas_data and "data" in alertas_data else {}

    nombre_usuario = session.get("user", {}).get("nombre", "Usuario")
    mensaje_bienvenida = f"Hola {nombre_usuario}, aquí puedes gestionar tus tareas. Asegúrate de mantener tus pendientes actualizados para un mejor seguimiento."

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
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
    data = request.form.to_dict(flat=True) or request.get_json(silent=True) or {}

    print("👤 usuario_empresa_id recibido:", data.get("usuario_empresa_id"))

    titulo = data.get("titulo")
    prioridad = (data.get("prioridad") or "media").strip().lower()
    fecha_limite = data.get("fecha_limite")
    estatus = (data.get("estatus") or "pendiente").strip().lower()

    usuario_empresa_id = (data.get("usuario_empresa_id") or session.get("usuario_empresa_id") or "").strip()
    if not usuario_empresa_id or usuario_empresa_id.strip() in ["", "none", "None"]:
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
        "titulo": titulo.strip(),
        "prioridad": prioridad.strip().lower() if prioridad else "media",
        "fecha_limite": fecha_limite.strip() or None,
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
        tarea = supabase.table("tareas").select("*") \
            .eq("id", tarea_id).eq("nombre_nora", nombre_nora).limit(1).execute()
        if not tarea.data:
            return jsonify({"error": "Tarea no encontrada"}), 404
        t = tarea.data[0]
        t["descripcion"] = t.get("descripcion", "")

        # Agregar nombre de empresa si aplica
        if t.get("empresa_id"):
            empresa = supabase.table("cliente_empresas") \
                .select("nombre_empresa") \
                .eq("id", t["empresa_id"]) \
                .limit(1).execute()
            if empresa.data:
                t["empresa_nombre"] = empresa.data[0]["nombre_empresa"]

        # Agregar nombre del usuario asignado si aplica
        if t.get("usuario_empresa_id"):
            asignado = supabase.table("usuarios_clientes") \
                .select("nombre") \
                .eq("id", t["usuario_empresa_id"]) \
                .limit(1).execute()
            if asignado.data:
                t["asignado_nombre"] = asignado.data[0]["nombre"]

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

# -------------------------------------------------------------------
# API: obtener tareas completadas (JSON para lazy-load)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/completadas_json", methods=["GET"])
def tareas_completadas_json(nombre_nora):
    if not session.get("email"):
        return jsonify({"error": "No autenticado"}), 401
    if not modulo_activo_para_nora(nombre_nora, "tareas"):
        return jsonify({"error": "Módulo no activo"}), 403

    # Paginación
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except Exception:
        limit = 50
        offset = 0

    # Obtener tareas completadas, ordenadas por fecha de actualización descendente
    tareas_resp = supabase.table("tareas").select("*") \
        .eq("nombre_nora", nombre_nora) \
        .eq("activo", True) \
        .eq("estatus", "completada") \
        .order("updated_at", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    tareas = tareas_resp.data or []

    # Marcar tareas recurrentes
    tareas_recurrentes_resp = supabase.table("tareas_recurrentes").select("tarea_id").execute()
    tarea_ids_recurrentes = set(r["tarea_id"] for r in (tareas_recurrentes_resp.data or []))
    for t in tareas:
        t["is_recurrente"] = t.get("id") in tarea_ids_recurrentes

    # Agregar nombre de empresa y usuario asignado
    for t in tareas:
        t["empresa"] = ""
        if t.get("empresa_id"):
            try:
                emp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", t["empresa_id"]).limit(1).execute()
                t["empresa"] = emp.data[0]["nombre_empresa"] if emp.data else ""
            except Exception:
                t["empresa"] = ""
        t["asignado_a"] = ""
        if t.get("usuario_empresa_id"):
            try:
                usr = supabase.table("usuarios_clientes").select("nombre").eq("id", t["usuario_empresa_id"]).limit(1).execute()
                t["asignado_a"] = usr.data[0]["nombre"] if usr.data else ""
            except Exception:
                t["asignado_a"] = ""
        try:
            fecha = t.get("fecha_limite")
            t["dias_restantes"] = (date.fromisoformat(fecha) - date.today()).days if fecha else None
        except Exception:
            t["dias_restantes"] = None

    # Conteo de comentarios por tarea
    tarea_ids = [t["id"] for t in tareas]
    conteos = {}
    if tarea_ids:
        comentarios_agregados = (
            supabase.table("tarea_comentarios")
            .select("tarea_id", "id", count="exact")
            .in_("tarea_id", tarea_ids)
            .execute()
        )
        for c in comentarios_agregados.data:
            tid = c["tarea_id"]
            conteos[tid] = conteos.get(tid, 0) + 1
    for t in tareas:
        t["comentarios_count"] = conteos.get(t["id"], 0)

    tareas_json = [
        {
            "id": t["id"],
            "titulo": t.get("titulo", ""),
            "prioridad": t.get("prioridad", ""),
            "dias_restantes": t.get("dias_restantes"),
            "estatus": t.get("estatus", ""),
            "asignado_a": t.get("asignado_a", ""),
            "empresa": t.get("empresa", ""),
            "comentarios_count": t.get("comentarios_count", 0),
            "recurrente": t.get("recurrente", False),
            "is_recurrente": t.get("is_recurrente", False)
        }
        for t in tareas
    ]
    return jsonify(tareas_json)