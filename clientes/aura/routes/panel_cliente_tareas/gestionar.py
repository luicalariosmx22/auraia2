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
        per_page = int(request.args.get("per_page", 15))  # Cambiado a 15 por página
    except Exception:
        page = 1
        per_page = 15
    offset = (page - 1) * per_page
    # --- Consulta eficiente a Supabase ---
    query = supabase.table("tareas").select("*", count="exact").eq("nombre_nora", nombre_nora).eq("activo", True).neq("estatus", "completada")
    if q["empresa_id"]:
        query = query.eq("empresa_id", q["empresa_id"])
    if q["usuario_empresa_id"]:
        query = query.eq("usuario_empresa_id", q["usuario_empresa_id"])
    # --- NO usar lógica combinada en la query ---
    # if not q["usuario_empresa_id"]:
    #     query = query.or_("asignada_a_empresa.is.true,usuario_empresa_id.is.not.null")
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
    # Ordenar por fecha_limite más cercana a más lejana (sin usar nulls_last, para compatibilidad)
    query = query.order("fecha_limite", desc=False)
    # Paginación
    query = query.range(offset, offset + per_page - 1)
    res = query.execute()
    tareas_activas = res.data or []
    total_registros = res.count or 0
    total_pages = (total_registros + per_page - 1) // per_page if per_page else 1

    # --- Filtrar en memoria si no se filtra por usuario_empresa_id ---
    if not q["usuario_empresa_id"]:
        tareas_activas = [
            t for t in tareas_activas
            if (t.get("asignada_a_empresa") is True) or (t.get("usuario_empresa_id"))
        ]
    total_activas = len(tareas_activas)
    total_pages = (total_activas + per_page - 1) // per_page

    # --- Filtro de búsqueda por texto (en memoria, si aplica) ---
    if q["busqueda"]:
        tareas_activas = [t for t in tareas_activas if q["busqueda"] in (t.get("titulo", "").lower() + " " + t.get("descripcion", "").lower())]
        total_registros = len(tareas_activas)
        total_pages = (total_registros + per_page - 1) // per_page if per_page else 1

    # --- Marcar recurrentes y enriquecer tareas ---
    tareas_recurrentes_resp = supabase.table("tareas_recurrentes").select("tarea_id").execute()
    tarea_ids_recurrentes = set(r["tarea_id"] for r in (tareas_recurrentes_resp.data or []))
    # Enriquecer tareas: mostrar si está asignada a empresa
    for t in tareas_activas:
        t["is_recurrente"] = t.get("id") in tarea_ids_recurrentes
        t["asignada_a_empresa"] = t.get("asignada_a_empresa", False)
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
        # Enriquecer subtareas con info de asignación a empresa
        for s in t["subtareas"]:
            if s.get("asignada_a_empresa"):
                s["asignado_nombre"] = "(Empresa)"
            elif s.get("usuario_empresa_id"):
                try:
                    usr = supabase.table("usuarios_clientes").select("nombre").eq("id", s["usuario_empresa_id"]).limit(1).execute()
                    s["asignado_nombre"] = usr.data[0]["nombre"] if usr.data else ""
                except Exception:
                    s["asignado_nombre"] = ""
            else:
                s["asignado_nombre"] = ""

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

    # --- Obtener reports de Meta para la empresa (si aplica) ---
    meta_reports = []
    if q["empresa_id"]:
        try:
            meta_reports = supabase.table("meta_ads_reportes").select("*").eq("empresa_id", q["empresa_id"]).order("fecha", desc=True).execute().data or []
        except Exception as e:
            print(f"Error al obtener reports de Meta: {e}")

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
        total_activas=total_registros,
        orden=orden,
        meta_reports=meta_reports,
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

    # Permitir actualizar asignada_a_empresa
    if campo == "asignada_a_empresa":
        valor_bool = valor in (True, "true", "on", 1, "1")
        update_data = {"asignada_a_empresa": valor_bool, "usuario_empresa_id": None if valor_bool else payload.get("usuario_empresa_id"), "updated_at": datetime.utcnow().isoformat()}
        try:
            supabase.table("tareas").update(update_data).eq("id", tarea_id).execute()
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # Solo permitir ciertos campos
    if campo not in [
        "titulo",
        "prioridad",
        "fecha_limite",
        "estatus",
        "usuario_empresa_id",  # ← Único campo para “Asignado a”
        "empresa_id",
        # "tarea_padre_id",      # ← Eliminado porque no existe en la tabla
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
    # update_data = {campo: valor, "updated_at": datetime.utcnow().isoformat()}
    update_data = {campo: valor, "updated_at": datetime.utcnow().isoformat()}
    # if campo == "tarea_padre_id" and (valor is None or valor == ""):
    #     update_data["tarea_padre_id"] = None

    # --- Lógica especial: mover tarea a completadas y marcar como inactiva ---
    # Si se marca como completada, mover a tabla de tareas completadas y marcar como inactiva
    if campo == "estatus" and valor == "completada":
        # Obtener la tarea actual
        tarea_resp = supabase.table("tareas").select("*").eq("id", tarea_id).limit(1).execute()
        if not tarea_resp.data:
            return jsonify({"error": "Tarea no encontrada"}), 404
        tarea = tarea_resp.data[0]
        # Marcar como inactiva
        supabase.table("tareas").update({"activo": False, "estatus": "completada", "updated_at": datetime.utcnow().isoformat()}).eq("id", tarea_id).execute()
        # Insertar en tabla de tareas completadas (crear si no existe)
        try:
            supabase.table("tareas_completadas").insert({
                **tarea,
                "id": tarea_id,
                "estatus": "completada",
                "activo": False,
                "updated_at": datetime.utcnow().isoformat(),
                # "completada_en": datetime.utcnow().isoformat(),  # Eliminado porque no existe la columna
            }).execute()
        except Exception as e:
            import traceback
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: obtener tarea por ID
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/obtener/<tarea_id>", methods=["GET"])
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/eliminar/<tarea_id>", methods=["POST"])
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/completadas_json", methods=["GET"])
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/<tarea_id>/subtareas", methods=["GET"])
def api_subtareas(nombre_nora, tarea_id):
    res = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_id).eq("activo", True).order("created_at", desc=False).execute()
    subtareas = res.data or []
    return jsonify(subtareas)

# -------------------------------------------------------------------
# API: actualizar campo de subtarea (inline edit)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/gestionar/subtareas/actualizar/<subtarea_id>",
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
        "asignada_a_empresa",  # Permitir edición inline de asignada_a_empresa
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
    if campo == "asignada_a_empresa":
        valor = valor in (True, "true", "1", 1, "on")
        # Si se asigna a empresa, usuario_empresa_id debe ser None
        if valor:
            supabase.table("subtareas").update({"usuario_empresa_id": None}).eq("id", subtarea_id).execute()

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
                # "completada_en": datetime.utcnow().isoformat(),  # Eliminado porque no existe la columna
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/subtareas/obtener/<subtarea_id>", methods=["GET"])
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
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/obtener_modal/<tarea_id>", methods=["GET"])
def obtener_tarea_modal(nombre_nora, tarea_id):
    try:
        print(f"[obtener_tarea_modal] nombre_nora={nombre_nora}, tarea_id={tarea_id}")
        # Obtener la tarea actual
        tarea_resp = supabase.table("tareas").select("*") \
            .eq("id", tarea_id).eq("nombre_nora", nombre_nora).limit(1).execute()
        if not tarea_resp.data:
            print(f"[obtener_tarea_modal] Tarea no encontrada para id={tarea_id}, nombre_nora={nombre_nora}")
            return jsonify({"error": "Tarea no encontrada"}), 404
        tarea = tarea_resp.data[0]
        tarea["descripcion"] = tarea.get("descripcion", "")

        # No buscar tarea_padre_id si no existe la columna
        tarea_padre = None
        # --- Si en el futuro se agrega tarea_padre_id, aquí va la lógica ---

        # Obtener todas las tareas principales (excluyendo la actual)
        tareas_principales_resp = supabase.table("tareas").select("id, titulo, empresa_id").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
        tareas_principales_raw = [t for t in (tareas_principales_resp.data or []) if t["id"] != tarea_id]

        # Subtareas
        subtareas = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_id).eq("activo", True).order("created_at", desc=False).execute().data or []
        # --- TAREAS DISPONIBLES PARA CONVERTIR EN SUBTAREA ---
        subtareas_ids = set([s["id"] for s in subtareas])
        tareas_disponibles_resp = supabase.table("tareas").select("id, titulo, empresa_id").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
        # --- OPTIMIZACIÓN: obtener todos los empresa_id únicos de una vez ---
        empresa_ids = set()
        for t in tareas_principales_raw:
            if t.get("empresa_id"): empresa_ids.add(t["empresa_id"])
        for s in subtareas:
            if s.get("empresa_id"): empresa_ids.add(s["empresa_id"])
        for t in (tareas_disponibles_resp.data or []):
            if t.get("empresa_id"): empresa_ids.add(t["empresa_id"])
        empresas_map = {}
        if empresa_ids:
            empresas_resp = supabase.table("cliente_empresas").select("id, nombre_empresa").in_("id", list(empresa_ids)).execute()
            empresas_map = {e["id"]: e["nombre_empresa"] for e in (empresas_resp.data or [])}

        # Tareas principales
        tareas_principales = []
        for t in tareas_principales_raw:
            if t.get("empresa_id") and t["empresa_id"] in empresas_map:
                t["empresa_nombre"] = empresas_map[t["empresa_id"]]
            tareas_principales.append(t)

        # Subtareas
        for s in subtareas:
            if s.get("empresa_id") and s["empresa_id"] in empresas_map:
                s["empresa_nombre"] = empresas_map[s["empresa_id"]]

        # Tareas disponibles para subtarea
        tareas_disponibles = []
        for t in (tareas_disponibles_resp.data or []):
            if t["id"] == tarea["id"]:
                continue
            if t["id"] in subtareas_ids:
                continue
            if t.get("empresa_id") and t["empresa_id"] in empresas_map:
                t["empresa_nombre"] = empresas_map[t["empresa_id"]]
            tareas_disponibles.append(t)

        print(f"[obtener_tarea_modal] OK: tarea_id={tarea_id}, subtareas={len(subtareas)}")
        return jsonify({
            "tarea": tarea,
            "tarea_padre": tarea_padre,
            "tareas_principales": tareas_principales,
            "subtareas": subtareas,
            "tareas_disponibles_para_subtarea": tareas_disponibles
        })
    except Exception as e:
        print(f"[obtener_tarea_modal][ERROR] {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: crear tarea (versión robusta y moderna)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/crear", methods=["POST"])
def crear_tarea(nombre_nora):
    data = request.get_json(silent=True) or request.form.to_dict(flat=True) or {}

    # --- Si es SUBTAREA ---
    if data.get("tarea_padre_id"):
        required = ["titulo", "empresa_id", "tarea_padre_id", "creado_por"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing)}"}), 400
        # Permitir subtarea asignada a empresa (sin usuario)
        asignada_a_empresa = data.get("asignada_a_empresa") in (True, "true", "1", 1, "on")
        usuario_empresa_id = data.get("usuario_empresa_id") if not asignada_a_empresa else None
        nueva_subtarea = {
            "id": str(uuid.uuid4()),
            "titulo": data["titulo"],
            "descripcion": data.get("descripcion", ""),
            "prioridad": (data.get("prioridad") or "media").strip().lower(),
            "estatus": data.get("estatus", "pendiente"),
            "fecha_limite": data.get("fecha_limite") or None,
            "usuario_empresa_id": usuario_empresa_id,
            "empresa_id": data["empresa_id"],
            "tarea_padre_id": data["tarea_padre_id"],
            "creado_por": data["creado_por"],
            "asignada_a_empresa": asignada_a_empresa,
            "activo": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        try:
            print(f"[crear_tarea][SUBTAREA] Payload a insertar: {nueva_subtarea}")
            result = supabase.table("subtareas").insert(nueva_subtarea).execute()
            print(f"[crear_tarea][SUBTAREA] Resultado insert: {result}")
            if hasattr(result, 'error') and result.error:
                print(f"[crear_tarea][SUBTAREA][ERROR] {result.error}")
                return jsonify({"error": str(result.error)}), 500
            if not result.data:
                print(f"[crear_tarea][SUBTAREA][ERROR] Insert vacío: {result}")
                return jsonify({"error": "No se insertó la subtarea (respuesta vacía de Supabase)", "supabase_result": str(result)}), 500
            return jsonify({"ok": True, "subtarea": nueva_subtarea}), 200
        except Exception as e:
            print("❌ Error insertando subtarea:", e)
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    # --- TAREA NORMAL (principal) ---
    asignar_a_empresa = data.get("asignar_a_empresa") in (True, "true", "on", 1, "1")
    usuario_empresa_id = (data.get("usuario_empresa_id") or "").strip() if not asignar_a_empresa else None
    titulo = (data.get("titulo") or "").strip()
    if not asignar_a_empresa and not usuario_empresa_id:
        return jsonify({"error": "usuario_empresa_id es obligatorio si no se asigna a empresa"}), 400
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
        "estatus": (data.get("estatus") or "pendiente").strip().lower(),
        "usuario_empresa_id": usuario_empresa_id,
        "empresa_id": sanea_uuid(data.get("empresa_id", "")),
        "asignada_a_empresa": asignar_a_empresa,
        "origen": data.get("origen", "manual"),
        "creado_por": sanea_uuid(data.get("creado_por") or usuario_empresa_id),
        "activo": True,
        "nombre_nora": nombre_nora,  # <-- asegurar que se envía correctamente
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    print(f"[crear_tarea][TAREA] Payload a insertar: {nueva}")
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
        print(f"[crear_tarea][TAREA] Resultado insert: {result}")
        if hasattr(result, 'error') and result.error:
            print(f"[crear_tarea][TAREA][ERROR] {result.error}")
            return jsonify({"error": str(result.error)}), 500
        if not result.data:
            print(f"[crear_tarea][TAREA][ERROR] Insert vacío: {result}")
            return jsonify({"error": "No se insertó la tarea (respuesta vacía de Supabase)", "supabase_result": str(result)}), 500
        return jsonify({"ok": True, "tarea": nueva}), 200
    except Exception as e:
        print("❌ Error insertando tarea:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: convertir tarea existente en subtarea
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/convertir_en_subtarea", methods=["POST"])
def convertir_en_subtarea(nombre_nora):
    data = request.get_json(silent=True) or {}
    tarea_id = data.get("tarea_id")
    tarea_padre_id = data.get("tarea_padre_id")
    if not tarea_id or not tarea_padre_id:
        return jsonify({"error": "Faltan parámetros obligatorios"}), 400
    print(f"[convertir_en_subtarea] Recibido: tarea_id={tarea_id}, tarea_padre_id={tarea_padre_id}")
    # Obtener la tarea a convertir
    tarea_resp = supabase.table("tareas").select("*").eq("id", tarea_id).limit(1).execute()
    if not tarea_resp.data:
        print(f"[convertir_en_subtarea] Tarea no encontrada: {tarea_id}")
        return jsonify({"error": "Tarea no encontrada"}), 404
    tarea = tarea_resp.data[0]
    print(f"[convertir_en_subtarea] Datos tarea a convertir: {tarea}")
    # Crear subtarea con los datos de la tarea (sin lógica de recurrencia)
    creado_por_val = tarea.get("creado_por") or "LL"
    nueva_subtarea = {
        "id": str(uuid.uuid4()),
        "titulo": tarea["titulo"],
        "descripcion": tarea.get("descripcion", ""),
        "prioridad": tarea.get("prioridad", "media"),
        "fecha_limite": tarea.get("fecha_limite"),
        "estatus": tarea.get("estatus", "pendiente"),
        "usuario_empresa_id": tarea.get("usuario_empresa_id"),
        "empresa_id": tarea.get("empresa_id"),
        "tarea_padre_id": tarea_padre_id,
        "creado_por": creado_por_val,
        "activo": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    print(f"[convertir_en_subtarea] Insertando nueva subtarea: {nueva_subtarea}")
    try:
        # Insertar la subtarea primero
        supabase.table("subtareas").insert(nueva_subtarea).execute()
        print(f"[convertir_en_subtarea] Subtarea insertada OK. Eliminando tarea original...")
        # Eliminar la tarea original
        supabase.table("tareas").delete().eq("id", tarea_id).execute()
        print(f"[convertir_en_subtarea] Tarea original eliminada.")
        return jsonify({"ok": True, "subtarea": nueva_subtarea})
    except Exception as e:
        import traceback
        print(f"[convertir_en_subtarea][ERROR] {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500