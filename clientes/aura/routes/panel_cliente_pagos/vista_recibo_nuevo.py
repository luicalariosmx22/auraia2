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
def nuevo_recibo(nombre_nora):
    """
    Alta de un nuevo recibo.
    • Permite añadir uno o varios servicios ya registrados (buscables por nombre -o- filtrables por categoría).
    • Opcionalmente el usuario puede agregar líneas manuales (servicio, cantidad, costo).
    """
    supa = supabase

    if request.method == "POST":
        # ---------- Procesar servicios seleccionados ----------
        items = []
        ids      = request.form.getlist("servicio_id[]")
        cant     = request.form.getlist("cantidad[]")
        costos   = request.form.getlist("costo[]")
        nombres  = request.form.getlist("nombre_servicio[]")  # vienen cuando es manual

        for i in range(len(cant)):
            if not cant[i]:
                continue  # fila vacía
            item = {
                "servicio_id": ids[i] or None,
                "nombre":      nombres[i] if nombres[i] else None,
                "cantidad":    float(cant[i]),
                "costo_unit":  float(costos[i]),
            }
            items.append(item)

        total = sum(it["cantidad"] * it["costo_unit"] for it in items)

        # ---------- Insertar recibo ----------
        recibo_data = {
            "empresa_id":      request.form["empresa_id"],
            "concepto":        request.form["concepto"],
            "monto":           total,
            "fecha_vencimiento": request.form["fecha_vencimiento"],
            "fecha_pago":      request.form.get("fecha_pago") or None,
            "estatus":         request.form["estatus"],
            "forma_pago":      request.form["forma_pago"],
            "notas":           request.form.get("notas") or "",
            "items":           items,
            "nombre_nora":     nombre_nora,
        }
        result = supa.table("pagos").insert(recibo_data).execute()
        pago_id = result.data[0]["id"]

        return redirect(
            url_for(
                "panel_cliente_pagos_recibo.ver_recibo",
                nombre_nora=nombre_nora,
                pago_id=pago_id,
            )
        )

    # ---------- Vista GET ----------
    # ⚠️ Algunos proyectos tienen la tabla como `cliente_empresas`
    #    y otros simplemente `empresas`. Intentamos ambos →
    try:
        empresas = (
            supa.table("cliente_empresas")
                .select("id,nombre_empresa")
                .eq("nombre_nora", nombre_nora)
                .order("nombre_empresa")
                .execute()
                .data
        )
    except Exception:
        empresas = (
            supa.table("empresas")
                .select("id,nombre_empresa")
                .eq("nombre_nora", nombre_nora)
                .order("nombre_empresa")
                .execute()
                .data
        )
    # La tabla real trae `titulo` (no `nombre`). Normalizamos a la clave `nombre`
    servicios_raw = (
        supa.table("servicios")
            .select("id,titulo,costo,categoria")
            .eq("nombre_nora", nombre_nora)
            .execute()
            .data
    )
    servicios   = [
        {
            "id":        s["id"],
            "nombre":    s["titulo"],
            "costo":     s["costo"],
            "categoria": s.get("categoria") or "",
        }
        for s in servicios_raw
    ]
    categorias = sorted({s["categoria"] for s in servicios if s["categoria"]})

    return render_template(
        "recibo_nuevo.html",
        empresas=empresas,
        servicios=servicios,
        categorias=categorias,
        nombre_nora=nombre_nora,
    )
