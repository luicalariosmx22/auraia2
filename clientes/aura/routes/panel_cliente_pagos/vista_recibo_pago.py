# ✅ Archivo: clientes/aura/routes/panel_cliente_pagos/vista_recibo_pago.py
from flask import Blueprint, render_template, session, redirect, url_for, make_response
from weasyprint import HTML
from supabase import create_client
import os
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_recibo_bp = Blueprint("panel_cliente_pagos_recibo", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_recibo_bp.route("/recibo/<pago_id>")
@login_required
def ver_recibo(nombre_nora, pago_id):
    # Validar módulo activo
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    # Obtener el pago
    pago_resp = supabase.table("pagos").select("*").eq("id", pago_id).single().execute()
    pago = pago_resp.data
    if not pago: return "Pago no encontrado", 404

    # Obtener nombres
    cliente = supabase.table("clientes").select("nombre_cliente").eq("id", pago["cliente_id"]).single().execute().data
    empresa = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", pago["empresa_id"]).single().execute().data

    pago["cliente_nombre"] = cliente["nombre_cliente"] if cliente else "—"
    pago["empresa_nombre"] = empresa["nombre_empresa"] if empresa else "—"

    return render_template("panel_cliente_pagos/recibo_detalle.html", pago=pago, nombre_nora=nombre_nora)

@panel_cliente_pagos_recibo_bp.route("/recibo/<pago_id>/pdf")
@login_required
def exportar_pdf(nombre_nora, pago_id):
    # Validar módulo activo
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    # Obtener el pago
    pago_resp = supabase.table("pagos").select("*").eq("id", pago_id).single().execute()
    pago = pago_resp.data
    if not pago: return "Pago no encontrado", 404

    # Obtener nombres
    cliente = supabase.table("clientes").select("nombre_cliente").eq("id", pago["cliente_id"]).single().execute().data
    empresa = supabase.table("cliente_empresas").select("nombre_empresa").eq("id", pago["empresa_id"]).single().execute().data

    pago["cliente_nombre"] = cliente["nombre_cliente"] if cliente else "—"
    pago["empresa_nombre"] = empresa["nombre_empresa"] if empresa else "—"

    html_render = render_template("panel_cliente_pagos/recibo_detalle.html", pago=pago, nombre_nora=nombre_nora)
    pdf = HTML(string=html_render).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=recibo_{pago_id}.pdf'
    return response
