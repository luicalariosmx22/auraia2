from flask import Blueprint, render_template, request, session
from clientes.aura.utils.supabase_client import supabase

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar", __name__)

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar", methods=["GET"])
def gestionar_tareas(nombre_nora):
    user = session.get("user", {})
    cliente_id = user.get("cliente_id", "")
    empresa_id = user.get("empresa_id", "")

    tareas = supabase.table("tareas")\
        .select("*")\
        .eq("nombre_nora", nombre_nora)\
        .eq("activo", True)\
        .order("created_at", desc=True)\
        .execute().data or []

    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    return render_template("panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas=tareas,
        usuarios=usuarios,
        empresas=empresas,
        cliente_id=cliente_id,
        empresa_id=empresa_id,
        user=user
    )