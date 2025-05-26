from flask import Blueprint
from flask import render_template, session, request
from clientes.aura.utils.supabase_client import supabase

panel_cliente_tareas_bp = Blueprint(
    "panel_cliente_tareas",  # este nombre debe ser único
    __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@panel_cliente_tareas_bp.route("/", endpoint="index_tareas")
def vista_tareas_index():
    nombre_nora = request.path.split("/")[2]

    user = session.get("user", {})
    cliente_id = user.get("cliente_id", "")
    empresa_id = user.get("empresa_id", "")

    tareas_activas = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    filtro_empresa_id = request.args.get("empresa_id")
    filtro_estatus = request.args.get("estatus")
    filtro_prioridad = request.args.get("prioridad")

    if filtro_empresa_id:
        tareas_activas = [t for t in tareas_activas if t.get("empresa_id") == filtro_empresa_id]

    if filtro_estatus:
        tareas_activas = [t for t in tareas_activas if t.get("estatus") == filtro_estatus]

    if filtro_prioridad:
        tareas_activas = [t for t in tareas_activas if t.get("prioridad") == filtro_prioridad]

    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    empresas = supabase.table("cliente_empresas")\
        .select("id, nombre_empresa")\
        .eq("nombre_nora", nombre_nora)\
        .eq("activo", True)\
        .execute().data or []

    empresas_dict = {e["id"]: e["nombre_empresa"] for e in empresas}

    resumen = {
        "tareas_activas": len([t for t in tareas_activas if t["estatus"] == "pendiente"]),
        "tareas_completadas": len([t for t in tareas_activas if t["estatus"] == "completada"]),
        "tareas_vencidas": len([t for t in tareas_activas if t["estatus"] in ["vencida", "atrasada"]]),
        "porcentaje_cumplimiento": 0
    }

    total = resumen["tareas_activas"] + resumen["tareas_completadas"] + resumen["tareas_vencidas"]
    if total > 0:
        resumen["porcentaje_cumplimiento"] = round((resumen["tareas_completadas"] / total) * 100, 1)

    return render_template("panel_cliente_tareas/index.html",
        tareas_activas=tareas_activas,
        usuarios=usuarios,
        empresas=empresas,
        empresas_dict=empresas_dict,
        resumen=resumen,
        alertas={},
        reportes_whatsapp=[],
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        nombre_nora=nombre_nora,
        user=user,
        config={},
        modulo_activo="tareas"  # ✅ ESTA ES LA CLAVE
    )

# Importa los submódulos que registran rutas en este blueprint
from . import (
    tareas_crud,
    plantillas,
    whatsapp,
    usuarios_clientes,
    estadisticas,
    automatizaciones,
    verificar
)
