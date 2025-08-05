from flask import request, jsonify, Blueprint
from .panel_cliente_tareas import panel_cliente_tareas_bp
from supabase import create_client
from datetime import datetime
from pytz import timezone
import uuid
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
zona = timezone("America/Hermosillo")

automatizaciones_bp = Blueprint(
    "automatizaciones", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

# ✅ Crear una tarea recurrente
@panel_cliente_tareas_bp.route("/automatizaciones/crear", methods=["POST"])
def crear_tarea_recurrente():
    data = request.get_json()
    nueva = {
        "id": str(uuid.uuid4()),
        "cliente_id": data["cliente_id"],
        "empresa_id": data["empresa_id"],
        "titulo": data["titulo"],
        "descripcion": data.get("descripcion", ""),
        "prioridad": data.get("prioridad", "media"),
        "frecuencia": data.get("frecuencia", "semanal"),
        "dia_ejecucion": data.get("dia_ejecucion", "lunes"),
        "asignado_a": data["asignado_a"],
        "usuario_empresa_id": data["asignado_a"],
        "creado_por": data.get("creado_por"),
        "nombre_nora": data.get("nombre_nora"),
        "activo": True,
        "created_at": datetime.now(zona).isoformat(),
        "updated_at": datetime.now(zona).isoformat()
    }
    supabase.table("tareas_recurrentes").insert(nueva).execute()
    return jsonify({"success": True})

# ✅ Listar tareas recurrentes activas por cliente
def obtener_tareas_recurrentes_activas(cliente_id):
    tareas = supabase.table("tareas_recurrentes").select("*") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data
    return tareas

# ✅ Ejecutar la recurrencia diaria (crear nuevas tareas)
@panel_cliente_tareas_bp.route("/automatizaciones/ejecutar", methods=["POST"])
def ejecutar_recurrencia_diaria():
    hoy = datetime.now(zona)
    dia = hoy.strftime("%A").lower()

    clientes = supabase.table("configuracion_bot").select("cliente_id, nombre_nora") \
        .eq("modulo_tareas_activo", True).execute().data

    creadas = []

    for cliente in clientes:
        tareas = obtener_tareas_recurrentes_activas(cliente["cliente_id"])
        tareas_hoy = [t for t in tareas if t["dia_ejecucion"] == dia]

        for t in tareas_hoy:
            fecha_str = hoy.strftime("%d%m%y")
            iniciales = ''.join(filter(str.isalnum, t["titulo"][:2].upper()))
            codigo_base = f"{iniciales}-{fecha_str}"
            count = supabase.table("tareas").select("id") \
                .ilike("codigo_tarea", f"{codigo_base}-%").execute().data
            correlativo = len(count) + 1
            codigo = f"{codigo_base}-{str(correlativo).zfill(3)}"

            nueva_tarea = {
                "id": str(uuid.uuid4()),
                "codigo_tarea": codigo,
                "titulo": t["titulo"],
                "descripcion": t["descripcion"],
                "fecha_limite": hoy.strftime("%Y-%m-%d"),
                "prioridad": t["prioridad"],
                "estatus": "pendiente",
                "usuario_empresa_id": t["usuario_empresa_id"],
                "asignado_a": t["usuario_empresa_id"],
                "empresa_id": t["empresa_id"],
                "cliente_id": cliente["cliente_id"],
                "origen": "recurrente",
                "creado_por": t["creado_por"],
                "nombre_nora": cliente["nombre_nora"],
                "activo": True,
                "created_at": hoy.isoformat(),
                "updated_at": hoy.isoformat()
            }

            supabase.table("tareas").insert(nueva_tarea).execute()
            creadas.append(codigo)

    return jsonify({"success": True, "creadas": creadas})

# ✅ Eliminar o desactivar una tarea recurrente
@panel_cliente_tareas_bp.route("/automatizaciones/eliminar/<recurrente_id>", methods=["DELETE"])
def eliminar_tarea_recurrente(recurrente_id):
    supabase.table("tareas_recurrentes").update({"activo": False, "updated_at": datetime.now(zona).isoformat()}) \
        .eq("id", recurrente_id).execute()
    return jsonify({"success": True})

@panel_cliente_tareas_bp.route("/automatizaciones/guardar", methods=["POST"])
def guardar_preferencias_automatizaciones():
    data = request.get_json()
    nombre_nora = data.get("nombre_nora")
    if not nombre_nora:
        return jsonify({"success": False, "error": "nombre_nora requerido"}), 400

    # Actualiza la tabla configuracion_bot para la Nora correspondiente
    update_data = {
        "alertas_whatsapp": data.get("alertas_whatsapp", False),
        "tareas_recurrentes": data.get("tareas_recurrentes", False),
        "reporte_meta_ads": data.get("reporte_meta_ads", False),
        "tareas_sugeridas_modulos": data.get("tareas_sugeridas_modulos", False),
        "updated_at": datetime.now(zona).isoformat()
    }
    supabase.table("configuracion_bot").update(update_data).eq("nombre_nora", nombre_nora).execute()
    return jsonify({"success": True})

@panel_cliente_tareas_bp.route("/automatizaciones/<nombre_nora>/guardar", methods=["PUT"])
def guardar_automatizaciones(nombre_nora):
    data = request.json
    response = supabase.table("configuracion_bot")\
        .update({ "modulos_disponibles": data })\
        .eq("nombre_nora", nombre_nora)\
        .execute()
    return jsonify({"ok": True})

@automatizaciones_bp.route("/panel_cliente/<nombre_nora>/automatizaciones/prueba", methods=["GET"])
def prueba_automatizaciones(nombre_nora):
    return f"Vista de prueba AUTOMATIZACIONES para {nombre_nora}"