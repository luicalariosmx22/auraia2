from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from supabase import create_client
import os
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_servicios_bp = Blueprint("panel_cliente_pagos_servicios", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_servicios_bp.route("/", methods=["GET"])
@login_required
def servicios_lista(nombre_nora):
    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).limit(1).execute()
    modulos = config.data[0]["modulos"] if config.data else []
    if "pagos" not in modulos:
        return "Módulo de pagos no disponible para esta Nora", 403

    servicios = supabase.table("servicios").select("*").eq("nombre_nora", nombre_nora).execute().data
    return render_template("panel_cliente_pagos/servicios.html", servicios=servicios, nombre_nora=nombre_nora)

@panel_cliente_pagos_servicios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_servicio(nombre_nora):
    if request.method == "POST":
        data = {
            "nombre_nora": nombre_nora,
            "categoria": request.form.get("categoria", "").strip() or None,
            "titulo": request.form.get("titulo", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip() or None,
            "costo": float(request.form.get("costo", 0)),
            "tipo": request.form.get("tipo")
        }

        if not data["titulo"] or not data["tipo"]:
            flash("❌ El título y el tipo son obligatorios", "error")
            return redirect(request.url)

        supabase.table("servicios").insert(data).execute()
        flash("✅ Servicio registrado correctamente", "success")
        return redirect(url_for("panel_cliente_pagos_servicios.servicios_lista", nombre_nora=nombre_nora))

    return render_template("panel_cliente_pagos/servicios_nuevo.html", nombre_nora=nombre_nora)
