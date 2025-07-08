# ✅ Archivo: clientes/aura/routes/debug/debug_verificar_tareas.py
# 👉 Ruta para validar el estado del módulo de TAREAS en Nora (Multi-Nora)

from flask import Blueprint, render_template, request
from supabase import create_client
from datetime import datetime
import os

debug_verificar_tareas_bp = Blueprint("debug_verificar_tareas", __name__, template_folder="../../templates/debug")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@debug_verificar_tareas_bp.route("/debug/verificar_tareas")
def verificar_tareas():
    nombre_nora = request.args.get("nombre_nora")
    if not nombre_nora:
        return "❌ Falta el parámetro ?nombre_nora", 400

    resultado = []

    # 1. Módulo activado
    config = supabase.table("configuracion_bot").select("modulos, modulo_tareas_activo, tareas_recurrentes, alertas_whatsapp, reporte_meta_ads, cliente_id").eq("nombre_nora", nombre_nora).single().execute().data
    mod_activo = config.get("modulo_tareas_activo", False)
    resultado.append({
        "nombre": "Módulo de tareas activado",
        "estado": "🟢 OK" if mod_activo else "🔴 Faltante",
        "comentario": "Revisar campo modulo_tareas_activo en configuracion_bot"
    })

    # 2. Usuarios empresa registrados
    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).execute().data
    resultado.append({
        "nombre": "Usuarios empresa registrados",
        "estado": "🟢 OK" if usuarios else "🔴 Faltante",
        "comentario": f"{len(usuarios)} usuarios encontrados" if usuarios else "No hay usuarios vinculados"
    })

    # 3. Tareas activas
    tareas = supabase.table("tareas").select("*").eq("cliente_id", config.get("cliente_id")).eq("activo", True).execute().data
    resultado.append({
        "nombre": "Tareas activas registradas",
        "estado": "🟢 OK" if tareas else "🟡 Incompleto",
        "comentario": f"{len(tareas)} tareas activas"
    })

    # 4. Códigos generados correctamente
    codigos_ok = [t for t in tareas if "-" in t["codigo_tarea"] and len(t["codigo_tarea"].split("-")) == 3]
    resultado.append({
        "nombre": "Códigos de tarea válidos",
        "estado": "🟢 OK" if len(codigos_ok) == len(tareas) else "🟡 Parcial",
        "comentario": f"{len(codigos_ok)} de {len(tareas)} tareas tienen código válido"
    })

    # 5. Supervisores activos
    supervisores = [u for u in usuarios if u.get("es_supervisor_tareas")]
    resultado.append({
        "nombre": "Supervisores activos",
        "estado": "🟢 OK" if len(supervisores) <= 3 else "⚠️ Exceso",
        "comentario": f"{len(supervisores)} supervisores activos"
    })

    # 6. Automatizaciones
    resultado.append({
        "nombre": "Recordatorios por WhatsApp",
        "estado": "🟢 OK" if config.get("alertas_whatsapp") else "🟡 Inactivo",
        "comentario": "Ver campo alertas_whatsapp en configuracion_bot"
    })
    resultado.append({
        "nombre": "Tareas recurrentes activadas",
        "estado": "🟢 OK" if config.get("tareas_recurrentes") else "🟡 Inactivo",
        "comentario": "Ver campo tareas_recurrentes en configuracion_bot"
    })

    # 7. Tareas sin asignar
    sin_asignar = [t for t in tareas if not t.get("usuario_empresa_id")]
    resultado.append({
        "nombre": "Tareas sin asignar",
        "estado": "🔴 Faltante" if sin_asignar else "🟢 OK",
        "comentario": f"{len(sin_asignar)} tareas sin usuario asignado"
    })

    # 8. Tareas vencidas
    hoy = datetime.now().date()
    vencidas = [t for t in tareas if t["fecha_limite"] and t["fecha_limite"] < hoy.isoformat() and t["estatus"] != "completada"]
    resultado.append({
        "nombre": "Tareas vencidas sin completar",
        "estado": "🟡 Hay vencidas" if vencidas else "🟢 OK",
        "comentario": f"{len(vencidas)} tareas vencidas"
    })

    # 9. Plantillas activas
    plantillas = supabase.table("plantillas_tareas").select("id").eq("cliente_id", config.get("cliente_id")).eq("activo", True).execute().data
    resultado.append({
        "nombre": "Plantillas de tareas activas",
        "estado": "🟢 OK" if plantillas else "🟡 Ninguna",
        "comentario": f"{len(plantillas)} plantillas activas"
    })

    return render_template("debug/verificar_tareas.html", nombre_nora=nombre_nora, resultado=resultado)
