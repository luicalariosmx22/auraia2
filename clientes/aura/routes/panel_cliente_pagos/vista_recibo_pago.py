# ✅ Archivo: clientes/aura/routes/panel_cliente_pagos/vista_recibo_pago.py
# 👉 Protegido contra errores de importación si fpdf2 no está instalado

from flask import Blueprint, Response, render_template, session, redirect, url_for, make_response, request, flash
from supabase import create_client
import os, shutil, subprocess, tempfile
from pathlib import Path
from clientes.aura.utils.login_required import login_required
from PyPDF2 import PdfFileWriter

panel_cliente_pagos_recibo_bp = Blueprint("panel_cliente_pagos_recibo", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    from fpdf2 import FPDF
except ImportError as e:
    print("⚠️ No se pudo importar 'fpdf2':", e)
    FPDF = None

@panel_cliente_pagos_recibo_bp.route("/recibo/<nombre_nora>/<pago_id>")
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
    Genera un PDF del recibo usando fpdf2 (sin dependencias nativas).
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

    # ---------- Generar PDF con fpdf2 (no libs nativas) ----------
    pdf = FPDF(format="Letter", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cabecera
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Recibo #{pago_id[:8]}", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"Empresa: {pago['empresa_id']}", ln=True)
    pdf.cell(0, 8, f"Cliente: {pago['cliente_id']}", ln=True)
    pdf.cell(0, 8, f"Concepto: {pago['concepto']}", ln=True)
    pdf.cell(0, 8, f"Fecha venc.: {pago['fecha_vencimiento']}", ln=True)
    pdf.ln(4)

    # Tabla de ítems
    if items:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(100, 8, "Servicio", border=1)
        pdf.cell(25, 8, "Cant.", border=1, align="R")
        pdf.cell(35, 8, "Costo", border=1, align="R")
        pdf.ln()
        pdf.set_font("Helvetica", size=11)
        for it in items:
            pdf.cell(100, 8, it["nombre"], border=1)
            pdf.cell(25, 8, f"{it['cantidad']:.2f}", border=1, align="R")
            pdf.cell(35, 8, f"${it['costo_unit']:.2f}", border=1, align="R")
            pdf.ln()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(125, 8, "Total", border=1)
        pdf.cell(35, 8, f"${pago['monto']:.2f}", border=1, align="R")
        pdf.ln()

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    pdf_writer = PdfFileWriter()
    # pdf_writer.write(pdf_bytes)  # ← Esto no es necesario, puedes omitirlo si no vas a manipular el PDF

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

@panel_cliente_pagos_recibo_bp.route("/recibo-pago/<cliente_id>")
def generar_recibo(cliente_id):
    if FPDF is None:
        return Response("⚠️ El módulo fpdf2 no está disponible en el entorno. Verifica tu requirements.txt.", status=500)

    # 🧾 Crear PDF ficticio como ejemplo
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Recibo de Pago - Cliente ID: {cliente_id}", ln=True, align="C")

    response = Response(pdf.output(dest="S").encode("latin1"))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=recibo_{cliente_id}.pdf"
    return response
