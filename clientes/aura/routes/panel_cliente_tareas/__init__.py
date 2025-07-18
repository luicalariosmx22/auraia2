# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/__init__.py
# 👉 Corrige los imports y registra solo los blueprints existentes

from flask import Blueprint, render_template, request, session
from clientes.aura.utils.supabase_client import supabase
from .gestionar import panel_tareas_gestionar_bp
from .recurrentes import panel_tareas_recurrentes_bp
from .tareas_crud import panel_tareas_crud_bp
from .plantillas import plantillas_bp
from .whatsapp import whatsapp_bp
from .usuarios_clientes import usuarios_clientes_bp
from .estadisticas import estadisticas_bp
from .automatizaciones import automatizaciones_bp
from .verificar import verificar_bp
from clientes.aura.routes.panel_cliente_tareas.utils.alertas_y_ranking import actualizar_estadisticas_alertas, obtener_datos_alertas_y_ranking
from supabase import create_client, Client
import os
from datetime import datetime
from flask import request, jsonify
import uuid
import re

panel_cliente_tareas_bp = Blueprint(
    "panel_cliente_tareas",
    __name__,
    template_folder="../../templates/panel_cliente_tareas"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cambia la ruta para que acepte el parámetro nombre_nora explícitamente y funcione con el url_prefix dinámico
@panel_cliente_tareas_bp.route("/", endpoint="index_tareas")
def vista_tareas_index():
    nombre_nora = request.view_args.get("nombre_nora")
    if not nombre_nora:
        match = re.search(r"/panel_cliente/([^/]+)/tareas", request.path)
        if match:
            nombre_nora = match.group(1)
    print(f"🔵 nombre_nora recibido: {nombre_nora}")
    user = session.get("user", {})
    cliente_id = user.get("cliente_id", "")
    empresa_id = user.get("empresa_id", "")
    print(f"🔵 user: {user}, cliente_id: {cliente_id}, empresa_id: {empresa_id}")

    # ⬇️ Agrega esto antes de render_template
    usuario_empresa_id = user.get("usuario_empresa_id", "")
    is_admin = session.get("is_admin", False)
    permisos = {
        "es_supervisor": user.get("rol") == "supervisor",
        "es_superadmin": user.get("rol") == "superadmin",
        "es_admin": is_admin,
        "crear_para_otros": True  # los admin siempre pueden
    }

    # Obtener tareas
    tareas = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).execute().data or []
    tareas_activas = [t for t in tareas if t["estatus"] != "completada"]
    print(f"🔵 tareas_activas iniciales: {len(tareas_activas)}")

    filtro_empresa_id = request.args.get("empresa_id")
    filtro_estatus = request.args.get("estatus")
    filtro_prioridad = request.args.get("prioridad")
    print(f"🔵 Filtros: empresa_id={filtro_empresa_id}, estatus={filtro_estatus}, prioridad={filtro_prioridad}")

    if filtro_empresa_id:
        tareas_activas = [t for t in tareas_activas if t.get("empresa_id") == filtro_empresa_id]
        print(f"🔵 tareas_activas tras filtro_empresa_id: {len(tareas_activas)}")

    if filtro_estatus:
        tareas_activas = [t for t in tareas_activas if t.get("estatus") == filtro_estatus]
        print(f"🔵 tareas_activas tras filtro_estatus: {len(tareas_activas)}")

    if filtro_prioridad:
        tareas_activas = [t for t in tareas_activas if t.get("prioridad") == filtro_prioridad]
        print(f"🔵 tareas_activas tras filtro_prioridad: {len(tareas_activas)}")

    # ⚠️ Obtener usuarios activos del cliente
    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    print(f"🔵 usuarios encontrados: {len(usuarios)}")

    # Calcular supervisores activos para el template de permisos
    supervisores_activos = len([u for u in usuarios if u.get("es_supervisor_tareas")])

    # ⚠️ Obtener alertas y ranking
    alertas, ranking, usuario_peor, empresa_mas = obtener_datos_alertas_y_ranking(nombre_nora, tareas, usuarios)

    # Resumen
    resumen = {
        "tareas_activas": len([t for t in tareas if t["estatus"] != "completada"]),
        "tareas_completadas": len([t for t in tareas if t["estatus"] == "completada"]),
        "tareas_vencidas": len([t for t in tareas if t["estatus"] in ["vencida", "atrasada"]]),
        "porcentaje_cumplimiento": 0
    }
    total = resumen["tareas_activas"] + resumen["tareas_completadas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)
    print(f"🔵 resumen: {resumen}")

    empresas = supabase.table("cliente_empresas")\
        .select("id, nombre_empresa")\
        .eq("nombre_nora", nombre_nora)\
        .eq("activo", True)\
        .execute().data or []

    empresas_dict = {e["id"]: e["nombre_empresa"] for e in empresas}
    reportes_whatsapp = []
    config = {}

    return render_template("panel_cliente_tareas/index.html",
        tareas_activas=tareas,
        usuarios=usuarios,
        supervisores_activos=supervisores_activos,
        empresas=empresas,
        empresas_dict=empresas_dict,
        resumen=resumen,
        alertas=alertas,
        reportes_whatsapp=reportes_whatsapp,
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        nombre_nora=nombre_nora,
        user=user,
        config=config,
        modulo_activo="tareas",
        permisos=permisos,
        usuario_empresa_id=usuario_empresa_id
    )

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/actualizar_completa/<tarea_id>", methods=["POST"])
def actualizar_tarea_completa(nombre_nora, tarea_id):
    data = request.get_json(silent=True) or {}
    
    campos_requeridos = [
        "titulo", "descripcion", "prioridad", "estatus",
        "fecha_limite", "usuario_empresa_id", "empresa_id"
    ]

    faltantes = [campo for campo in campos_requeridos if campo not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos: {', '.join(faltantes)}"}), 400

    # Validación opcional de campos
    if data["prioridad"] not in ["baja", "media", "alta"]:
        return jsonify({"error": "Prioridad inválida"}), 400
    if data["estatus"] not in ["pendiente", "en progreso", "retrasada", "completada"]:
        return jsonify({"error": "Estatus inválido"}), 400
    try:
        datetime.strptime(data["fecha_limite"], "%Y-%m-%d")
    except Exception:
        return jsonify({"error": "Fecha límite inválida"}), 400

    try:
        # 1️⃣ Actualiza la tarea base
        supabase.table("tareas").update({
            "titulo": data["titulo"],
            "descripcion": data["descripcion"],
            "prioridad": data["prioridad"],
            "estatus": data["estatus"],
            "fecha_limite": data["fecha_limite"],
            "usuario_empresa_id": data["usuario_empresa_id"],
            "empresa_id": data["empresa_id"],
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", tarea_id).eq("nombre_nora", nombre_nora).execute()

        # ────────────────────────────────────────────────────────────────
        # 📌 AQUÍ se crea/actualiza/desactiva la regla recurrente cuando se
        #    guarda el modal “Ver / Editar tarea”. 
        #    • Si no existe regla → insert into tareas_recurrentes
        #    • Si
        # ────────────────────────────────────────────────────────────────
        is_recurrente = str(data.get("is_recurrente", "")).lower() in ("1", "true", "on", "yes")

        # Busca si ya existe una regla para esta tarea
        rec_res = (
            supabase.table("tareas_recurrentes")
            .select("id")
            .eq("tarea_id", tarea_id)
            .execute()
        )

        # Compatibilidad con ambos SDKs: res.data o lista directa
        rec_rows = rec_res if isinstance(rec_res, list) else getattr(rec_res, "data", [])
        rec_id = rec_rows[0]["id"] if rec_rows else None

        if is_recurrente:
            dtstart = data.get("dtstart")
            rrule   = data.get("rrule")
            until   = data.get("until") or None
            count   = data.get("count") or None

            if dtstart and rrule:
                payload = {
                    "dtstart": f"{dtstart}T00:00:00",
                    "rrule":   rrule.upper(),
                    "until":   f"{until}T23:59:59" if until else None,
                    "count":   int(count) if (count or "").isdigit() else None,
                    "active":  True,
                    "updated_at": datetime.utcnow().isoformat()
                }

                if rec_id:
                    # Actualiza la regla existente
                    supabase.table("tareas_recurrentes").update(payload).eq("id", rec_id).execute()
                else:
                    # Crea nueva regla
                    payload.update({
                        "id": str(uuid.uuid4()),
                        "tarea_id": tarea_id,
                        "created_at": datetime.utcnow().isoformat()
                    })
                    supabase.table("tareas_recurrentes").insert(payload).execute()
        else:
            # Si se desmarcó la casilla, desactiva la regla existente
            if rec_id:
                supabase.table("tareas_recurrentes")\
                    .update({"active": False, "updated_at": datetime.utcnow().isoformat()})\
                    .eq("id", rec_id).execute()

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Import forzado: asegura que las rutas se registren aunque el bloque multiple no se ejecute
import clientes.aura.routes.panel_cliente_tareas.tareas_crud

# Importación obligatoria para que se registren correctamente las rutas del CRUD y submódulos
from . import (
    tareas_crud,
    gestionar,
    plantillas,
    whatsapp,
    usuarios_clientes,
    estadisticas,
    automatizaciones,
    verificar,
    recurrentes
)

# Registrar blueprints locales
def register_tareas_blueprints(app):
    # Eliminado el registro estático para evitar conflicto con el registro dinámico
    # app.register_blueprint(panel_cliente_tareas_bp, url_prefix="/panel_cliente")
    app.register_blueprint(panel_tareas_gestionar_bp)
    app.register_blueprint(panel_tareas_crud_bp)
    app.register_blueprint(panel_tareas_recurrentes_bp)
    app.register_blueprint(plantillas_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(usuarios_clientes_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(automatizaciones_bp)
    app.register_blueprint(verificar_bp)
