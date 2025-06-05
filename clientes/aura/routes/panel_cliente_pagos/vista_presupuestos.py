# Vista para presupuestos: solo muestra pagos con formato 'presupuesto'
from flask import Blueprint, render_template, request
from supabase import create_client
import os
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_presupuestos_bp = Blueprint("panel_cliente_pagos_presupuestos", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_presupuestos_bp.route("/panel_cliente/<nombre_nora>/pagos/presupuestos", methods=["GET"])
@login_required
def panel_cliente_pagos_presupuestos(nombre_nora):
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    pagos = supabase.table("pagos").select("*").eq("nombre_nora", nombre_nora).eq("formato", "presupuesto").order("fecha_vencimiento", desc=False).execute().data
    clientes = {
        c["id"]: c["nombre_cliente"]
        for c in supabase.table("clientes").select("id, nombre_cliente").eq("nombre_nora", nombre_nora).execute().data
    }
    empresas = {
        e["id"]: e["nombre_empresa"]
        for e in supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data
    }
    for p in pagos:
        p["cliente_nombre"] = clientes.get(p["cliente_id"], "—")
        p["empresa_nombre"] = empresas.get(p["empresa_id"], "—")

    return render_template(
        "panel_cliente_pagos/presupuestos.html",
        pagos=pagos,
        nombre_nora=nombre_nora,
        modulo_activo="pagos",
    )
