from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from supabase import create_client
import os
import uuid
from clientes.aura.utils.login_required import login_required

panel_cliente_pagos_nuevo_bp = Blueprint("panel_cliente_pagos_nuevo", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_cliente_pagos_nuevo_bp.route("/panel_cliente/<nombre_nora>/pagos/nuevo", methods=["GET", "POST"])
@panel_cliente_pagos_nuevo_bp.route("/panel_cliente/<nombre_nora>/pagos/editar/<pago_id>", methods=["GET", "POST"])
@login_required
def nuevo_recibo(nombre_nora, pago_id=None):
    """
    Alta de un nuevo recibo.
    • Permite añadir uno o varios servicios ya registrados (buscables por nombre -o- filtrables por categoría).
    • Opcionalmente el usuario puede agregar líneas manuales (servicio, cantidad, costo).
    """
    supa = supabase

    if request.method == "POST":
        # ⬇️ si viene hidden pago_id es edición
        pago_id = request.form.get("pago_id") or pago_id
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

        # ---------- Resuelve cliente_id según la empresa seleccionada ----------
        empresa_id  = request.form["empresa_id"]
        empresa_row = (
            supa.table("cliente_empresas")
                .select("cliente_id")
                .eq("id", empresa_id)
                .single()
                .execute()
                .data
        )
        cliente_id = empresa_row["cliente_id"] if empresa_row and empresa_row.get("cliente_id") else None
        if not cliente_id:
            flash("No se pudo determinar el cliente para la empresa seleccionada.", "error")
            return redirect(request.url)

        # ---------- Insertar recibo ----------
        recibo_data = {
            "empresa_id":   empresa_id,
            "cliente_id":   cliente_id,
            "concepto":     request.form["concepto"],
            "monto":           total,
            "fecha_vencimiento": request.form["fecha_vencimiento"],
            "fecha_pago":      request.form.get("fecha_pago") or None,
            "estatus":         request.form["estatus"],
            "forma_pago_id":   request.form["forma_pago_id"],
            "notas":           request.form.get("notas") or "",
            "nombre_nora":     nombre_nora,
            "tipo":            request.form.get("tipo") or "recibo",  # default a 'recibo' si no viene
        }
        if pago_id:
            # Update recibo existente
            supa.table("pagos").update(recibo_data).eq("id", pago_id).execute()
            supa.table("pagos_items").delete().eq("pago_id", pago_id).execute()
        else:
            # Nuevo recibo
            result = supa.table("pagos").insert(recibo_data).execute()
            if not result.data or not result.data[0].get("id"):
                flash("No se pudo guardar el recibo. Intenta de nuevo.", "error")
                return redirect(request.url)
            pago_id = result.data[0]["id"]

        # ---------- Insertar cada ítem en pagos_items ----------
        for it in items:
            supa.table("pagos_items").insert({
                "pago_id":     pago_id,
                "servicio_id": it["servicio_id"],
                "nombre":      it["nombre"],
                "cantidad":    it["cantidad"],
                "costo_unit":  it["costo_unit"],
            }).execute()

        # Redirigir SIEMPRE al listado de recibos tras guardar
        return redirect(url_for("panel_cliente_pagos.panel_cliente_pagos", nombre_nora=nombre_nora))

    # ---------- Vista GET ----------
    pago = None
    items_existentes = []
    if pago_id:
        pago  = supa.table("pagos").select("*").eq("id", pago_id).single().execute().data
        items_existentes = supa.table("pagos_items").select("servicio_id,nombre,cantidad,costo_unit").eq("pago_id", pago_id).execute().data

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
    # Formas de pago (catálogo)
    formas_pago = (
        supa.table("catalogo_formas_pago")
            .select("id,nombre")
            .order("nombre")
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

    # El HTML vive ahora en panel_cliente_pagos/recibo_nuevo.html
    return render_template(
        "panel_cliente_pagos/recibo_nuevo.html",
        empresas=empresas,
        servicios=servicios,
        pago=pago,
        items_existentes=items_existentes,
        formas_pago=formas_pago,
        categorias=categorias,
        nombre_nora=nombre_nora,
    )
