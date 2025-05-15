# ✅ Archivo: clientes/aura/routes/panel_cliente_pagos/vista_recibo_pago.py
import pdfkit
from flask import Blueprint, render_template, session, redirect, url_for, make_response, request, flash
from supabase import create_client
import os, shutil, subprocess, tempfile
from pathlib import Path
from clientes.aura.utils.login_required import login_required
from weasyprint import HTML

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
    """
    Genera un PDF del recibo usando WeasyPrint (solo-Python, sin wkhtmltopdf).
    """
    pago = (
        supabase.table("pagos")
            .select("*")
            .eq("id", pago_id)
            .single()
            .execute()
            .data
    )
    if not pago:
        flash("Recibo no encontrado", "error")
        return redirect(url_for(".ver_recibo", nombre_nora=nombre_nora, pago_id=pago_id))

    items = (
        supabase.table("pagos_items")
            .select("nombre,cantidad,costo_unit,servicio_id")
            .eq("pago_id", pago_id)
            .execute()
            .data
    )

    # Renderizamos HTML en string
    html = render_template(
        "panel_cliente_pagos/recibo_pdf.html",
        pago=pago,
        items=items,
        nombre_nora=nombre_nora,
    )

    # ---------- Generar PDF con WeasyPrint (solo-Python, sin wkhtmltopdf) ----------
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        HTML(string=html, base_url=request.host_url).write_pdf(tmp_pdf.name)
        pdf_bytes = tmp_pdf.read()
        tmp_path = tmp_pdf.name
    # limpiamos
    shutil.safe_remove = getattr(shutil, "safe_remove", lambda p: os.remove(p) if os.path.exists(p) else None)
    shutil.safe_remove(tmp_path)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="recibo_{pago_id[:8]}.pdf"'
    return response

# ---------- Enviar por correo ----------
@panel_cliente_pagos_recibo_bp.route("/recibo/<pago_id>/correo")
@login_required
def enviar_correo(nombre_nora, pago_id):
    # Stub: envía un link al correo registrado del cliente
    pago = supabase.table("pagos").select("cliente_id, concepto").eq("id", pago_id).single().execute().data
    cliente = supabase.table("clientes").select("correo, nombre_cliente").eq("id", pago["cliente_id"]).single().execute().data
    if not cliente or not cliente.get("correo"):
        flash("⚠️ El cliente no tiene correo registrado", "warning")
        return redirect(url_for(".ver_recibo", nombre_nora=nombre_nora, pago_id=pago_id))

    # Aquí conectarías con tu servicio de e-mail (SendGrid, Mailgun, etc.)
    # send_email(to=cliente["correo"], subject="Tu recibo", body="Adjunto…")

    flash("✅ Recibo enviado por correo", "success")
    return redirect(url_for(".ver_recibo", nombre_nora=nombre_nora, pago_id=pago_id))

# ---------- Enviar por WhatsApp ----------
@panel_cliente_pagos_recibo_bp.route("/recibo/<pago_id>/whatsapp")
@login_required
def enviar_whatsapp(nombre_nora, pago_id):
    # Stub: envía un mensaje con link al PDF usando tu integración de WhatsApp
    pago = supabase.table("pagos").select("cliente_id").eq("id", pago_id).single().execute().data
    cliente = supabase.table("contactos").select("telefono").eq("id", pago["cliente_id"]).single().execute().data
    if not cliente:
        flash("⚠️ El cliente no tiene teléfono registrado", "warning")
        return redirect(url_for(".ver_recibo", nombre_nora=nombre_nora, pago_id=pago_id))

    pdf_link = url_for(".exportar_pdf", nombre_nora=nombre_nora, pago_id=pago_id, _external=True)
    # send_whatsapp(to=cliente["telefono"], message=f"Tu recibo: {pdf_link}")

    flash("✅ Recibo enviado por WhatsApp", "success")
    return redirect(url_for(".ver_recibo", nombre_nora=nombre_nora, pago_id=pago_id))

# ---------- Editar recibo (redirección al formulario) ----------
@panel_cliente_pagos_recibo_bp.route("/recibo/<pago_id>/editar")
@login_required
def editar_recibo(nombre_nora, pago_id):
    return redirect(url_for("panel_cliente_pagos_nuevo.nuevo_recibo", nombre_nora=nombre_nora, pago_id=pago_id))
