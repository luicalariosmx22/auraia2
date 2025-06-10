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
from clientes.aura.utils.permisos_tareas import puede_crear_para_otros, es_supervisor, obtener_rol_tareas

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar_bp", __name__)

# -------------------------------------------------------------------
# VISTA PRINCIPAL: listado de tareas (gestión)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar", methods=["GET", "POST"])
def gestionar_tareas(nombre_nora):
    if request.method == "POST":
        print("✅ Recibido POST a crear_tarea()")
        print("🔎 Datos recibidos:", request.get_json(silent=True) or request.form.to_dict())
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

    rol_tareas = obtener_rol_tareas(usuario_id, nombre_nora)
    permisos = {
        "es_supervisor": rol_tareas == "supervisor",
        "crear_para_otros": puede_crear_para_otros(usuario_id, nombre_nora),
        "es_admin": session.get("is_admin", False),
        "es_super_admin": session.get("is_super_admin", False),
        "rol_tareas": rol_tareas
    }

    rol_demo = request.args.get("rol_demo")
    if permisos.get("es_super_admin") and rol_demo:
        if rol_demo == "usuario":
            permisos["es_supervisor"] = False
            permisos["es_admin"] = False
            permisos["rol_tareas"] = "usuario"
        elif rol_demo == "supervisor":
            permisos["es_supervisor"] = True
            permisos["es_admin"] = False
            permisos["rol_tareas"] = "supervisor"
        elif rol_demo == "admin":
            permisos["es_supervisor"] = False
            permisos["es_admin"] = True
            permisos["rol_tareas"] = "admin"
        elif rol_demo == "super_admin":
            permisos["es_supervisor"] = False
            permisos["es_admin"] = False
            permisos["es_super_admin"] = True
            permisos["rol_tareas"] = "super_admin"
    # --- Fin lógica demo roles ---

    # --- Filtros y paginación ---
    q = {
        "busqueda": request.args.get("busqueda", "").strip().lower(),
        "estatus": request.args.get("estatus", "").strip(),
        "prioridad": request.args.get("prioridad", "").strip(),
        "empresa_id": request.args.get("empresa_id", "").strip(),
        "usuario_empresa_id": request.args.get("usuario_empresa_id", "").strip(),
        "fecha_ini": request.args.get("fecha_ini", "").strip(),
        "fecha_fin": request.args.get("fecha_fin", "").strip()
    }
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except Exception:
        page = 1
        per_page = 10
    offset = (page - 1) * per_page
    # --- Consulta eficiente a Supabase ---
    query = supabase.table("tareas").select("*", count="exact").eq("nombre_nora", nombre_nora).eq("activo", True)
    if q["empresa_id"]:
        query = query.eq("empresa_id", q["empresa_id"])
    if q["usuario_empresa_id"]:
        query = query.eq("usuario_empresa_id", q["usuario_empresa_id"])
    if q["estatus"]:
        query = query.eq("estatus", q["estatus"])
    if q["prioridad"]:
        query = query.eq("prioridad", q["prioridad"])
    if q["fecha_ini"]:
        query = query.gte("fecha_limite", q["fecha_ini"])
    if q["fecha_fin"]:
        query = query.lte("fecha_limite", q["fecha_fin"])
    # Ordenamiento
    orden = request.args.get("orden", "desc")
    if orden == "asc":
        query = query.order("created_at", desc=False)
    else:
        query = query.order("created_at", desc=True)
    # Paginación
    query = query.range(offset, offset + per_page - 1)
    res = query.execute()
    tareas_activas = res.data or []
    total_activas = res.count or 0
    total_pages = (total_activas + per_page - 1) // per_page

    # --- Filtro de búsqueda por texto (en memoria, si aplica) ---
    if q["busqueda"]:
        tareas_activas = [t for t in tareas_activas if q["busqueda"] in (t.get("titulo", "").lower() + " " + t.get("descripcion", "").lower())]
        total_activas = len(tareas_activas)
        total_pages = (total_activas + per_page - 1) // per_page

    # --- Marcar recurrentes y enriquecer tareas ---
    tareas_recurrentes_resp = supabase.table("tareas_recurrentes").select("tarea_id").execute()
    tarea_ids_recurrentes = set(r["tarea_id"] for r in (tareas_recurrentes_resp.data or []))
    for t in tareas_activas:
        t["is_recurrente"] = t.get("id") in tarea_ids_recurrentes
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
    tarea_ids = [t["id"] for t in tareas_activas]
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
    for t in tareas_activas:
        t["comentarios_count"] = conteos.get(t["id"], 0)

    usuarios = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    logger = logging.getLogger(__name__)
    logger.info(f"[Tareas] Recuperadas {len(tareas_activas)} tareas para usuario_id={usuario_id} (Nora: {nombre_nora})")

    # --- SUBTAREAS: lógica para obtener subtareas de una tarea principal ---
    def obtener_subtareas(tarea_padre_id):
        res = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_padre_id).eq("activo", True).order("created_at", desc=False).execute()
        return res.data or []
    for t in tareas_activas:
        t["subtareas"] = obtener_subtareas(t["id"])

    resumen = {
        "tareas_activas": total_activas,
        "tareas_completadas": 0,  # Si necesitas, haz otra consulta paginada para completadas
        "tareas_vencidas": len([t for t in tareas_activas if (t.get("dias_restantes") or 0) < 0]),
        "porcentaje_cumplimiento": 0
    }
    total = resumen["tareas_activas"] + resumen["tareas_completadas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    nombre_usuario = session.get("user", {}).get("nombre", "Usuario")
    mensaje_bienvenida = f"Hola {nombre_usuario}, aquí puedes gestionar tus tareas. Asegúrate de mantener tus pendientes actualizados para un mejor seguimiento."

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas=[],  # ya no se usa
        resumen=resumen,
        usuarios=usuarios,
        mensaje_bienvenida=mensaje_bienvenida,
        tareas_activas=tareas_activas,
        tareas_completadas=[],  # si quieres, haz paginación igual
        permisos=permisos,
        empresas=empresas,
        user={"name": session.get("name", "Usuario"), "id": usuario_id},
        modulo_activo="tareas",
        alertas={},
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total_activas=total_activas,
        orden=orden,
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

    # Permitir actualizar tarea_padre_id
    if campo not in [
        "titulo",
        "prioridad",
        "fecha_limite",
        "estatus",
        "usuario_empresa_id",  # ← Único campo para “Asignado a”
        "empresa_id",
        "tarea_padre_id",      # ← Permitir cambiar tarea padre
        "descripcion",         # ← Permitir editar descripción
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
    if campo == "descripcion":
        if not isinstance(valor, str):
            return jsonify({"error": "Descripción inválida"}), 400
        valor = valor.strip()
        if len(valor) > 2000:
            return jsonify({"error": "La descripción es demasiado larga (máx 2000 caracteres)"}), 400

    # Si se cambia tarea_padre_id, permitir None para volver a tarea principal
    update_data = {campo: valor, "updated_at": datetime.utcnow().isoformat()}
    if campo == "tarea_padre_id" and (valor is None or valor == ""):
        update_data["tarea_padre_id"] = None

    try:
        supabase.table("tareas").update(update_data).eq("id", tarea_id).execute()
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

# -------------------------------------------------------------------
# API: obtener subtareas de una tarea principal
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/<tarea_id>/subtareas", methods=["GET"])
def api_subtareas(nombre_nora, tarea_id):
    res = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_id).eq("activo", True).order("created_at", desc=False).execute()
    subtareas = res.data or []
    return jsonify(subtareas)

# -------------------------------------------------------------------
# API: actualizar campo de subtarea (inline edit)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/subtareas/actualizar/<subtarea_id>",
    methods=["POST"],
)
def actualizar_campo_subtarea(nombre_nora, subtarea_id):
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
            datetime.strptime(valor, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Fecha inválida"}), 400

    # Si se marca como completada, mover a tabla de subtareas completadas
    if campo == "estatus" and valor == "completada":
        # Obtener la subtarea actual
        res = supabase.table("subtareas").select("*").eq("id", subtarea_id).limit(1).execute()
        if not res.data:
            return jsonify({"error": "Subtarea no encontrada"}), 404
        subtarea = res.data[0]
        # Marcar como inactiva
        supabase.table("subtareas").update({"activo": False, "updated_at": datetime.utcnow().isoformat()}).eq("id", subtarea_id).execute()
        # Insertar en tabla de subtareas completadas (crear si no existe)
        try:
            supabase.table("subtareas_completadas").insert({
                **subtarea,
                "id": subtarea_id,
                "estatus": "completada",
                "activo": False,
                "updated_at": datetime.utcnow().isoformat(),
                "completada_en": datetime.utcnow().isoformat(),
            }).execute()
        except Exception:
            pass
        return jsonify({"ok": True, "completada": True})

    # Edición normal
    try:
        supabase.table("subtareas").update(
            {campo: valor, "updated_at": datetime.utcnow().isoformat()}
        ).eq("id", subtarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: obtener subtarea por ID (para modal)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/subtareas/obtener/<subtarea_id>", methods=["GET"])
def obtener_subtarea(nombre_nora, subtarea_id):
    try:
        res = supabase.table("subtareas").select("*").eq("id", subtarea_id).limit(1).execute()
        if not res.data:
            return jsonify({"error": "Subtarea no encontrada"}), 404
        s = res.data[0]
        s["descripcion"] = s.get("descripcion", "")

        # Agregar nombre de empresa si aplica
        if s.get("empresa_id"):
            empresa = supabase.table("cliente_empresas") \
                .select("nombre_empresa") \
                .eq("id", s["empresa_id"]) \
                .limit(1).execute()
            if empresa.data:
                s["empresa_nombre"] = empresa.data[0]["nombre_empresa"]

        # Agregar nombre del usuario asignado si aplica
        if s.get("usuario_empresa_id"):
            asignado = supabase.table("usuarios_clientes") \
                .select("nombre") \
                .eq("id", s["usuario_empresa_id"]) \
                .limit(1).execute()
            if asignado.data:
                s["asignado_nombre"] = asignado.data[0]["nombre"]

        # Agregar info de tarea padre si aplica
        if s.get("tarea_padre_id"):
            tarea_padre = supabase.table("tareas").select("id, titulo, empresa_id").eq("id", s["tarea_padre_id"]).limit(1).execute()
            if tarea_padre.data:
                padre = tarea_padre.data[0]
                empresa_nombre = None
                if padre.get("empresa_id"):
                    emp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", padre["empresa_id"]).limit(1).execute()
                    if emp.data:
                        empresa_nombre = emp.data[0]["nombre_empresa"]
                s["tarea_padre"] = {
                    "id": padre["id"],
                    "titulo": padre["titulo"],
                    "empresa_nombre": empresa_nombre
                }
        return jsonify(s)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: obtener tarea para el modal de edición
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/obtener_modal/<tarea_id>", methods=["GET"])
def obtener_tarea_modal(nombre_nora, tarea_id):
    try:
        # Obtener la tarea actual
        tarea_resp = supabase.table("tareas").select("*") \
            .eq("id", tarea_id).eq("nombre_nora", nombre_nora).limit(1).execute()
        if not tarea_resp.data:
            return jsonify({"error": "Tarea no encontrada"}), 404
        tarea = tarea_resp.data[0]
        tarea["descripcion"] = tarea.get("descripcion", "")

        # Obtener tarea padre si es subtarea
        tarea_padre = None
        if tarea.get("tarea_padre_id"):
            padre_resp = supabase.table("tareas").select("id, titulo, empresa_id").eq("id", tarea["tarea_padre_id"]).limit(1).execute()
            if padre_resp.data:
                tarea_padre = padre_resp.data[0]
                if tarea_padre.get("empresa_id"):
                    emp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", tarea_padre["empresa_id"]).limit(1).execute()
                    if emp.data:
                        tarea_padre["empresa_nombre"] = emp.data[0]["nombre_empresa"]

        # Obtener todas las tareas principales (excluyendo la actual y sus descendientes)
        tareas_principales_resp = supabase.table("tareas").select("id, titulo, empresa_id").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
        tareas_principales_raw = [t for t in (tareas_principales_resp.data or []) if t["id"] != tarea_id]
        # 1. Obtener todos los empresa_id únicos (ignorando None/vacíos)
        empresa_ids = list({t["empresa_id"] for t in tareas_principales_raw if t.get("empresa_id")})
        empresas_map = {}
        if empresa_ids:
            # 2. Obtener todas las empresas de un solo query
            empresas_resp = supabase.table("cliente_empresas").select("id, nombre_empresa").in_("id", empresa_ids).execute()
            empresas_map = {e["id"]: e["nombre_empresa"] for e in (empresas_resp.data or [])}
        # 3. Asignar nombre de empresa a cada tarea principal usando el mapeo
        tareas_principales = []
        for t in tareas_principales_raw:
            if t.get("empresa_id") and t["empresa_id"] in empresas_map:
                t["empresa_nombre"] = empresas_map[t["empresa_id"]]
            tareas_principales.append(t)

        # Subtareas
        subtareas = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_id).eq("activo", True).order("created_at", desc=False).execute().data or []
        for s in subtareas:
            if s.get("empresa_id"):
                emp = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", s["empresa_id"]).limit(1).execute()
                if emp.data:
                    s["empresa_nombre"] = emp.data[0]["nombre_empresa"]

        return jsonify({
            "tarea": tarea,
            "tarea_padre": tarea_padre,
            "tareas_principales": tareas_principales,
            "subtareas": subtareas
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: crear tarea (versión robusta y moderna)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/crear", methods=["POST"])
def crear_tarea(nombre_nora):
    data = request.get_json(silent=True) or request.form.to_dict(flat=True) or {}

    usuario_empresa_id = (data.get("usuario_empresa_id") or "").strip()
    titulo = (data.get("titulo") or "").strip()
    if not usuario_empresa_id:
        return jsonify({"error": "usuario_empresa_id es obligatorio"}), 400
    if not titulo:
        return jsonify({"error": "titulo es obligatorio"}), 400

    def sanea_uuid(val):
        return val.strip() or None if isinstance(val, str) else val

    # 🧠 Generar un código de tarea único
    import re
    fecha = datetime.now().strftime("%d%m%y")
    iniciales = ''.join(filter(str.isalnum, (data.get("iniciales_usuario", "NN")).upper()))[:3]
    base_codigo = f"{iniciales}-{fecha}"
    while True:
        max_codigo = supabase.table("tareas") \
            .select("codigo_tarea") \
            .ilike("codigo_tarea", f"{base_codigo}-%") \
            .order("codigo_tarea", desc=True) \
            .limit(1) \
            .execute()
        if max_codigo.data:
            last = max_codigo.data[0]["codigo_tarea"]
            m = re.match(rf"{base_codigo}-(\d+)", last)
            correlativo = int(m.group(1)) + 1 if m else 1
        else:
            correlativo = 1
        codigo_generado = f"{base_codigo}-{str(correlativo).zfill(3)}"
        existe_codigo = supabase.table("tareas").select("id").eq("codigo_tarea", codigo_generado).execute()
        if not existe_codigo.data:
            break

    nueva = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": codigo_generado,
        "titulo": titulo,
        "descripcion": data.get("descripcion") or "",
        "fecha_limite": data.get("fecha_limite") or None,
        "prioridad": (data.get("prioridad") or "media").strip().lower(),
        "estatus": data.get("estatus", "pendiente"),
        "usuario_empresa_id": usuario_empresa_id,
        "empresa_id": sanea_uuid(data.get("empresa_id", "")),
        "origen": data.get("origen", "manual"),
        "creado_por": sanea_uuid(data.get("creado_por") or usuario_empresa_id),
        "activo": True,
        "nombre_nora": data.get("nombre_nora"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    # ❌ Evitar duplicados por título en el día
    hoy = datetime.now().strftime("%Y-%m-%d")
    existe = supabase.table("tareas").select("id").eq("usuario_empresa_id", usuario_empresa_id) \
        .eq("titulo", titulo).gte("created_at", f"{hoy}T00:00:00").lte("created_at", f"{hoy}T23:59:59").execute()
    if existe.data:
        print("⚠️ Ya existe una tarea igual hoy, no se inserta duplicado.")
        return jsonify({"ok": True, "id": existe.data[0]["id"], "duplicada": True}), 200

    try:
        # 1️⃣ Insertar tarea base
        result = supabase.table("tareas").insert(nueva).execute()

        # 2️⃣ Si es recurrente, insertarla también en tareas_recurrentes
        es_recurrente = str(data.get("is_recurrente", "")).lower() in ("1", "true", "on", "yes")
        if es_recurrente:
            dtstart_val = data.get("dtstart")
            rrule_val   = data.get("rrule") or ""
            until_val   = data.get("until") or None
            count_val   = data.get("count") or None
            if dtstart_val and rrule_val:
                rec_payload = {
                    "id":        str(uuid.uuid4()),
                    "tarea_id":  nueva["id"],
                    "dtstart":   f"{dtstart_val}T00:00:00",
                    "rrule":     rrule_val,
                    "until":     f"{until_val}T23:59:59" if until_val else None,
                    "count":     int(count_val) if count_val else None,
                    "active":    True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                supabase.table("tareas_recurrentes").insert(rec_payload).execute()

        return jsonify({"ok": True, "tarea": nueva}), 200
    except Exception as e:
        print("❌ Error insertando tarea:", e)
        return jsonify({"error": str(e)}), 500