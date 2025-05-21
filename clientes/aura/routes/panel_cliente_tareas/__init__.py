from flask import Blueprint, render_template, session
from clientes.aura.utils.supabase_client import supabase

panel_cliente_tareas_bp = Blueprint(
    "panel_cliente_tareas",
    __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@panel_cliente_tareas_bp.route("/")
def vista_tareas_index():
    nombre_nora = session.get("nombre_nora", "aura")
    user = session.get("user", {})
    cliente_id = user.get("cliente_id", "")
    empresa_id = user.get("empresa_id", "")

    tareas_activas = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

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
        resumen=resumen,
        alertas={},
        reportes_whatsapp=[],
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        nombre_nora=nombre_nora,
        user=user,
        config={}
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
