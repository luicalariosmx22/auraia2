# ✅ Archivo: clientes/aura/routes/panel_cliente_pagos/vista_recibo_pago.py
from flask import Blueprint, render_template, abort, session, redirect
from supabase import create_client
from clientes.aura.utils.login_required import login_required
import os
import json

vista_recibo_pago_bp = Blueprint("panel_cliente_pagos_recibo", __name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@vista_recibo_pago_bp.route("/<pago_id>/recibo", methods=["GET"])
@login_required
def ver_recibo_pago(nombre_nora, pago_id):
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    pago_resp = supabase.table("pagos").select("*").eq("id", pago_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    if not pago_resp.data:
        return abort(404)

    pago = pago_resp.data[0]
    cliente = supabase.table("clientes").select("nombre").eq("id", pago["cliente_id"]).limit(1).execute().data[0]
    empresa = supabase.table("empresas").select("nombre, direccion, ciudad").eq("id", pago["empresa_id"]).limit(1).execute().data[0]

    return render_template("panel_cliente_pagos/recibo.html", pago=pago, cliente=cliente, empresa=empresa, nombre_nora=nombre_nora)
