from flask import jsonify, request, Blueprint
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

verificar_bp = Blueprint(
    "verificar", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@verificar_bp.route("/panel_cliente/<nombre_nora>/verificar/prueba", methods=["GET"])
def prueba_verificar(nombre_nora):
    return f"Vista de prueba VERIFICAR para {nombre_nora}"

# ✅ Verificar estado del módulo de tareas
@panel_cliente_tareas_bp.route("/verificar/<nombre_nora>", methods=["GET"])
def verificar_modulo(nombre_nora):
    verificaciones = {}

    # Verificar tareas creadas
    tareas = supabase.table("tareas").select("id, usuario_empresa_id, codigo_tarea, estatus").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    tareas_asignadas = [t for t in tareas if t.get("usuario_empresa_id")]
    tareas_codificadas = [t for t in tareas if t.get("codigo_tarea")]

    verificaciones["tareas_creadas"] = {"estado": "🟢" if tareas else "🔴", "comentario": f"{len(tareas)} tareas registradas"}
    verificaciones["tareas_asignadas"] = {"estado": "🟢" if len(tareas_asignadas) == len(tareas) else "🟡", "comentario": f"{len(tareas_asignadas)} asignadas"}
    verificaciones["codigos_generados"] = {"estado": "🟢" if len(tareas_codificadas) == len(tareas) else "🟡", "comentario": f"{len(tareas_codificadas)} con código"}

    # Plantillas activas
    plantillas = supabase.table("plantillas_tareas").select("id").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    verificaciones["plantillas"] = {"estado": "🟢" if plantillas else "🟡", "comentario": f"{len(plantillas)} plantillas activas"}

    # Supervisores activos
    supervisores = supabase.table("usuarios_clientes").select("id").eq("nombre_nora", nombre_nora).eq("activo", True).eq("es_supervisor_tareas", True).execute().data or []
    estado = "🟢" if 1 <= len(supervisores) <= 3 else "🔴" if len(supervisores) > 3 else "🟡"
    verificaciones["supervisores"] = {"estado": estado, "comentario": f"{len(supervisores)} supervisores activos"}

    # Automatizaciones activas
    config = supabase.table("configuracion_bot").select("alertas_whatsapp, tareas_recurrentes, reporte_semanal").eq("nombre_nora", nombre_nora).single().execute().data
    for campo in ["alertas_whatsapp", "tareas_recurrentes", "reporte_semanal"]:
        valor = config.get(campo)
        estado = "🟢" if valor else "🔴"
        verificaciones[campo] = {"estado": estado, "comentario": "Activo" if valor else "Desactivado"}

    return jsonify({"verificaciones": verificaciones})


# ✅ Reparar errores comunes
@panel_cliente_tareas_bp.route("/verificar/reparar/<nombre_nora>", methods=["POST"])
def reparar_modulo(nombre_nora):
    log = []

    # 1. Generar código para tareas sin código
    tareas_sin_codigo = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).is_("codigo_tarea", "is.null").execute().data or []
    for t in tareas_sin_codigo:
        nuevo_codigo = f"FIX-{datetime.now().strftime('%d%m%y')}-{str(t['id'])[:4]}"
        supabase.table("tareas").update({"codigo_tarea": nuevo_codigo, "updated_at": datetime.now().isoformat()}).eq("id", t["id"]).execute()
        log.append(f"🛠 Se generó código para tarea {t['id']} → {nuevo_codigo}")

    # 2. Desactivar tareas sin asignación válida
    tareas_sin_usuario = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).is_("usuario_empresa_id", "is.null").execute().data or []
    for t in tareas_sin_usuario:
        supabase.table("tareas").update({"activo": False, "updated_at": datetime.now().isoformat()}).eq("id", t["id"]).execute()
        log.append(f"🚫 Tarea {t['codigo_tarea']} desactivada por falta de asignación")

    # 3. Limitar supervisores a 3
    supervisores = supabase.table("usuarios_clientes").select("id").eq("nombre_nora", nombre_nora).eq("activo", True).eq("es_supervisor_tareas", True).execute().data or []
    if len(supervisores) > 3:
        for s in supervisores[3:]:
            supabase.table("usuarios_clientes").update({"es_supervisor_tareas": False}).eq("id", s["id"]).execute()
            log.append(f"🔧 Se removió permiso de supervisor a {s['id']}")

    # 4. Crear supervisor default si no hay ninguno
    if len(supervisores) == 0:
        usuarios = supabase.table("usuarios_clientes").select("id").eq("nombre_nora", nombre_nora).eq("activo", True).limit(1).execute().data
        if usuarios:
            supabase.table("usuarios_clientes").update({"es_supervisor_tareas": True}).eq("id", usuarios[0]["id"]).execute()
            log.append(f"✅ Usuario {usuarios[0]['id']} asignado como supervisor por defecto")

    # 5. Activar automatizaciones por defecto si están apagadas
    campos_auto = {
        "alertas_whatsapp": True,
        "tareas_recurrentes": True,
        "reporte_semanal": True
    }

    for campo, valor in campos_auto.items():
        supabase.table("configuracion_bot").update({campo: valor}).eq("nombre_nora", nombre_nora).execute()
        log.append(f"⚙️ Automatización '{campo}' activada")

    return jsonify({"reparado": True, "log": log})