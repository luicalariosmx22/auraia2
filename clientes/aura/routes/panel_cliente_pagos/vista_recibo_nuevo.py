from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from supabase import create_client
import os
import uuid
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_nuevo_bp = Blueprint("panel_cliente_pagos_nuevo", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_nuevo_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_recibo(nombre_nora):
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa, cliente_id").eq("nombre_nora", nombre_nora).execute().data
    servicios = supabase.table("servicios").select("*").eq("nombre_nora", nombre_nora).execute().data

    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        empresa = next((e for e in empresas if e["id"] == empresa_id), None)
        cliente_id = empresa["cliente_id"] if empresa else None

        data = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "cliente_id": cliente_id,
            "empresa_id": empresa_id,
            "concepto": request.form.get("concepto", "").strip(),
            "monto": float(request.form.get("monto")),
            "fecha_vencimiento": request.form.get("fecha_vencimiento"),
            "fecha_pago": request.form.get("fecha_pago") or None,
            "estatus": request.form.get("estatus"),
            "forma_pago": request.form.get("forma_pago", "").strip() or None,
            "notas": request.form.get("notas", "").strip() or None
        }

        supabase.table("pagos").insert(data).execute()
        flash("✅ Recibo registrado correctamente", "success")
        return redirect(url_for("panel_cliente_pagos.panel_cliente_pagos", nombre_nora=nombre_nora))

    return render_template("panel_cliente_pagos/recibo_nuevo.html", empresas=empresas, servicios=servicios, nombre_nora=nombre_nora)
