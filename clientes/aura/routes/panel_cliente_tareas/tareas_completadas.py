from flask import Blueprint, render_template, request, session
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase

panel_tareas_completadas_bp = Blueprint(
    "panel_tareas_completadas_bp", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@panel_tareas_completadas_bp.route("/panel_cliente/<nombre_nora>/tareas/completadas", methods=["GET"])
def vista_tareas_completadas(nombre_nora):
    # Filtros de fechas
    fecha_fin = request.args.get("fecha_fin")
    fecha_inicio = request.args.get("fecha_inicio")
    if not fecha_fin:
        fecha_fin = datetime.utcnow().date()
    else:
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=7)
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()

    # Otros filtros (puedes expandir según tus necesidades)
    # usuario_id = request.args.get("usuario_id")
    # empresa_id = request.args.get("empresa_id")

    # Consulta tareas completadas en el rango
    tareas = supabase.table("tareas_completadas") \
        .select("*") \
        .eq("nombre_nora", nombre_nora) \
        .gte("updated_at", fecha_inicio.strftime("%Y-%m-%d")) \
        .lte("updated_at", fecha_fin.strftime("%Y-%m-%d")) \
        .order("updated_at", desc=True) \
        .execute().data or []

    # Cargar usuarios y empresas para los filtros y la tabla
    usuarios = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    return render_template(
        "panel_cliente_tareas/tareas_completadas.html",
        tareas=tareas,
        usuarios=usuarios,
        empresas=empresas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        nombre_nora=nombre_nora
    )
