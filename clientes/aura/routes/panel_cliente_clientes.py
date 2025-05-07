from flask import Blueprint, render_template, session, redirect, url_for, request, flash
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

@panel_cliente_clientes_bp.route('/panel_cliente/<nombre_nora>/clientes/nuevo', methods=["GET", "POST"])
def nuevo_cliente(nombre_nora):
    if not session.get("user"):
        return redirect(url_for('login_bp.login'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    if session.get("user") and session.get("user").get("email"):
        user_email = session["user"]["email"]
    else:
        user_email = "sin_email@desconocido.com"

    if session.get("user") and session.get("user").get("name"):
        user_name = session["user"]["name"]
    else:
        user_name = "Desconocido"

    if session.get("user") and session.get("user").get("sub"):
        user_id = session["user"]["sub"]
    else:
        user_id = "sin_id"

    if request.method == "POST":
        nombre_cliente = request.form.get("nombre_cliente")
        tipo = request.form.get("tipo")
        email = request.form.get("email")
        telefono = request.form.get("telefono")

        data = {
            "nombre_nora": nombre_nora,
            "nombre_cliente": nombre_cliente,
            "tipo": tipo,
            "email": email,
            "telefono": telefono
        }

        resultado = supabase.table("clientes").insert(data).execute()

        if resultado.error:
            flash("Error al guardar el cliente", "error")
        else:
            flash("Cliente guardado correctamente", "success")
            return redirect(url_for('panel_cliente_clientes_bp.vista_clientes', nombre_nora=nombre_nora))

    return render_template('panel_cliente_clientes_nuevo.html', nombre_nora=nombre_nora, user=session.get("user"))
