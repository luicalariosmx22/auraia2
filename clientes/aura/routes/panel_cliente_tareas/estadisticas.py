# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/estadisticas.py
# 👉 Corrige todas las rutas y filtros a nombre_nora (no cliente_id)

from flask import jsonify, request, Blueprint
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime, timedelta
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

estadisticas_bp = Blueprint(
    "estadisticas", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

# ✅ Resumen general para dashboards
@panel_cliente_tareas_bp.route("/estadisticas/resumen/<nombre_nora>", methods=["GET"])
def obtener_resumen_general(nombre_nora):
    solo_usuario = request.args.get("solo_usuario")  # opcional

    consulta = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True)
    if solo_usuario:
        consulta = consulta.eq("usuario_empresa_id", solo_usuario)

    tareas = consulta.execute().data or []

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
    nombre_nora = data["nombre_nora"]
    inicio = data.get("fecha_inicio")
    fin = data.get("fecha_fin")

    filtros = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True)
    if inicio and fin:
        filtros = filtros.gte("fecha_limite", inicio).lte("fecha_limite", fin)

    tareas = filtros.execute().data or []
    return jsonify(tareas)

# ✅ Ranking: usuarios con más tareas completadas
@panel_cliente_tareas_bp.route("/estadisticas/completadas/<nombre_nora>", methods=["GET"])
def ranking_completadas(nombre_nora):
    tareas = supabase.table("tareas").select("*") \
        .eq("nombre_nora", nombre_nora).eq("estatus", "completada").eq("activo", True).execute().data or []

    ranking = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        ranking[uid] = ranking.get(uid, 0) + 1

    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ranking)

# ✅ Ranking: usuarios con más tareas vencidas
@panel_cliente_tareas_bp.route("/estadisticas/vencidas/<nombre_nora>", methods=["GET"])
def ranking_vencidas(nombre_nora):
    tareas = supabase.table("tareas").select("*") \
        .eq("nombre_nora", nombre_nora).in_("estatus", ["vencida", "atrasada"]).eq("activo", True).execute().data or []

    ranking = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        ranking[uid] = ranking.get(uid, 0) + 1

    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ranking)

# ✅ Usuarios más activos
@panel_cliente_tareas_bp.route("/estadisticas/activos/<nombre_nora>", methods=["GET"])
def usuarios_mas_activos(nombre_nora):
    tareas = supabase.table("tareas").select("*") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    conteo = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        conteo[uid] = conteo.get(uid, 0) + 1

    sorted_usuarios = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_usuarios)

# ❌ Eliminar función obsoleta (no se usa en frontend ni backend)
# @panel_cliente_tareas_bp.route("/dashboard/<nombre_nora>", methods=["GET"])
# def obtener_dashboard(nombre_nora):
#     try:
#         resumen = {
#             "tareas_activas": 0,
#             "tareas_completadas": 0,
#             "tareas_vencidas": 0,
#             "porcentaje_cumplimiento": 0
#         }
#         tareas = supabase.table("tareas").select("estatus, updated_at, fecha_limite") \
#             .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
#         for t in tareas:
#             estatus = t.get("estatus")
#             if estatus == "completada":
#                 resumen["tareas_completadas"] += 1
#             elif estatus in ["retrasada", "vencida"]:
#                 resumen["tareas_vencidas"] += 1
#             else:
#                 resumen["tareas_activas"] += 1
#         total = resumen["tareas_activas"] + resumen["tareas_completadas"] + resumen["tareas_vencidas"]
#         if total > 0:
#             resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)
#         alertas_data = supabase.table("alertas_ranking").select("data") \
#             .eq("cliente_id", nombre_nora).single().execute().data
#         alertas = alertas_data["data"] if alertas_data and "data" in alertas_data else {}
#         return jsonify({"resumen": resumen, "alertas": alertas})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@estadisticas_bp.route("/panel_cliente/<nombre_nora>/estadisticas/prueba", methods=["GET"])
def prueba_estadisticas(nombre_nora):
    return f"Vista de prueba ESTADÍSTICAS para {nombre_nora}"

# ✅ Utilidad para estadísticas centralizadas
def calcular_estadisticas_tareas(nombre_nora):
    tareas_resp = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    tareas = tareas_resp.data or []

    usuarios_resp = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).execute()
    usuarios = {u["id"]: u["nombre"] for u in usuarios_resp.data or []}

    empresas_resp = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute()
    empresas = {e["id"]: e["nombre_empresa"] for e in empresas_resp.data or []}

    resumen = {
        "tareas_activas": len([t for t in tareas if t["estatus"] not in ["completada"]]),
        "tareas_completadas": len([t for t in tareas if t["estatus"] == "completada"]),
        "tareas_vencidas": len([t for t in tareas if t["estatus"] in ["vencida", "atrasada"]]),
        "porcentaje_cumplimiento": 0
    }
    total = resumen["tareas_activas"] + resumen["tareas_completadas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    return resumen, usuarios, empresas
