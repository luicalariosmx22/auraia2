from flask import jsonify, request
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime, timedelta
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Resumen general para dashboards
@panel_cliente_tareas_bp.route("/estadisticas/resumen/<nombre_nora>", methods=["GET"])
def obtener_resumen_general(nombre_nora):
    tareas = supabase.table("tareas").select("*") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    resumen = {
        "tareas_activas": len([t for t in tareas if t["estatus"] == "pendiente"]),
        "tareas_completadas": len([t for t in tareas if t["estatus"] == "completada"]),
        "tareas_vencidas": len([t for t in tareas if t["estatus"] in ["vencida", "atrasada"]]),
        "porcentaje_cumplimiento": 0
    }

    total = resumen["tareas_activas"] + resumen["tareas_completadas"] + resumen["tareas_vencidas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    return jsonify(resumen)

# ✅ Obtener tareas por estado en un rango de fechas
@panel_cliente_tareas_bp.route("/estadisticas/estado", methods=["POST"])
def obtener_tareas_por_estado():
    data = request.get_json()
    cliente_id = data["cliente_id"]
    inicio = data.get("fecha_inicio")
    fin = data.get("fecha_fin")

    filtros = supabase.table("tareas").select("*").eq("cliente_id", cliente_id).eq("activo", True)
    if inicio and fin:
        filtros = filtros.gte("fecha_limite", inicio).lte("fecha_limite", fin)

    tareas = filtros.execute().data or []
    return jsonify(tareas)

# ✅ Ranking: usuarios con más tareas completadas
@panel_cliente_tareas_bp.route("/estadisticas/completadas/<cliente_id>", methods=["GET"])
def ranking_completadas(cliente_id):
    tareas = supabase.table("tareas").select("*").eq("cliente_id", cliente_id).eq("estatus", "completada").eq("activo", True).execute().data or []
    ranking = {}

    for t in tareas:
        uid = t["usuario_empresa_id"]
        ranking[uid] = ranking.get(uid, 0) + 1

    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ranking)

# ✅ Ranking: usuarios con más tareas vencidas
@panel_cliente_tareas_bp.route("/estadisticas/vencidas/<cliente_id>", methods=["GET"])
def ranking_vencidas(cliente_id):
    tareas = supabase.table("tareas").select("*") \
        .eq("cliente_id", cliente_id).in_("estatus", ["vencida", "atrasada"]).eq("activo", True).execute().data or []

    ranking = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        ranking[uid] = ranking.get(uid, 0) + 1

    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ranking)

# ✅ Usuarios más activos
@panel_cliente_tareas_bp.route("/estadisticas/activos/<cliente_id>", methods=["GET"])
def usuarios_mas_activos(cliente_id):
    tareas = supabase.table("tareas").select("*").eq("cliente_id", cliente_id).eq("activo", True).execute().data or []

    conteo = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        conteo[uid] = conteo.get(uid, 0) + 1

    sorted_usuarios = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_usuarios)

@panel_cliente_tareas_bp.route("/estadisticas/kpis", methods=["GET"])
def obtener_kpis():
    # TODO: lógica para generar resumen de estadísticas
    return jsonify({"total": 0})