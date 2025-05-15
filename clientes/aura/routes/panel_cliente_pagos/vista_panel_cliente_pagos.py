# ✅ Archivo: clientes/aura/routes/panel_cliente_pagos/vista_panel_cliente_pagos.py
# 👉 Código corregido: solo una ruta definida, sin duplicados

from flask import Blueprint, render_template, request, redirect, session
from supabase import create_client
import os
import json

panel_cliente_pagos_bp = Blueprint("panel_cliente_pagos", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_bp.route("/", methods=["GET"])
def panel_cliente_pagos(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    # Validar si el módulo está activo en configuracion_bot
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    # Cargar datos base
    pagos = supabase.table("pagos").select("*").eq("nombre_nora", nombre_nora).order("fecha_vencimiento", desc=False).execute().data
    clientes = {
        c["id"]: c["nombre"]
        for c in supabase.table("clientes").select("id, nombre").eq("nombre_nora", nombre_nora).execute().data
    }
    empresas = {
        e["id"]: e["nombre"]
        for e in supabase.table("empresas").select("id, nombre").eq("nombre_nora", nombre_nora).execute().data
    }

    for p in pagos:
        p["cliente_nombre"] = clientes.get(p["cliente_id"], "—")
        p["empresa_nombre"] = empresas.get(p["empresa_id"], "—")

    return render_template("panel_cliente_pagos/index.html", pagos=pagos, nombre_nora=nombre_nora)
