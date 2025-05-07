from flask import Blueprint, render_template, session, redirect, url_for
from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase

panel_cliente_clientes_bp = Blueprint('panel_cliente_clientes_bp', __name__)

@panel_cliente_clientes_bp.route('/panel_cliente/<nombre_nora>/clientes')
def vista_clientes(nombre_nora):
    if not session.get("user"):
        return redirect(url_for('login_bp.login'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    # Obtener todos los clientes de esta Nora
    clientes_data = supabase.table("clientes").select("*").eq("nombre_nora", nombre_nora).execute()
    clientes = clientes_data.data if clientes_data.data else []

    for cliente in clientes:
        # Empresas asociadas a este cliente
        empresas_data = supabase.table("cliente_empresas") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("cliente_id", cliente["id"]) \
            .execute()
        cliente["empresas"] = empresas_data.data if empresas_data.data else []

        # Cuentas publicitarias asociadas
        ads_data = supabase.table("meta_ads_cuentas") \
            .select("*") \
            .eq("cliente_id", cliente["id"]) \
            .execute()
        cliente["ads_cuentas"] = ads_data.data if ads_data.data else []

    return render_template('panel_cliente_clientes.html', nombre_nora=nombre_nora, clientes=clientes, user=session.get("user"))

@panel_cliente_clientes_bp.route('/panel_cliente/<nombre_nora>/clientes/nuevo', methods=["GET"])
def nuevo_cliente(nombre_nora):
    if not session.get("user"):
        return redirect(url_for('login_bp.login'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    return render_template('panel_cliente_clientes_nuevo.html', nombre_nora=nombre_nora, user=session.get("user"))
