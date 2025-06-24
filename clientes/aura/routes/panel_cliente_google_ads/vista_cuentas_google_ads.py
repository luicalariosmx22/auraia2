from flask import render_template, request, redirect, url_for, flash
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from .listar_cuentas import listar_cuentas_publicitarias
import os
import logging

@panel_cliente_google_ads_bp.route("/cuentas", methods=["GET", "POST"], strict_slashes=False)
def ver_cuentas_google_ads():
    nombre_nora = request.view_args.get("nombre_nora")
    mensaje = None
    cuentas_excluidas = set()
    if request.method == "POST":
        cuentas_excluidas = set(request.form.getlist("excluir"))
        mensaje = f"Se han excluido {len(cuentas_excluidas)} cuentas de la operación."
    try:
        total, cuentas = listar_cuentas_publicitarias()
        cuentas = cuentas or []
        cuentas_mostradas = [c for c in cuentas if c not in cuentas_excluidas]
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[DEV] Total cuentas encontradas: {total}")
            logging.debug(f"[DEV] Resource names: {cuentas}")
    except Exception as e:
        cuentas = []
        cuentas_mostradas = []
        mensaje = f"Error al obtener cuentas: {e}"
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.exception("[DEV] Error buscando cuentas Google Ads")
    return render_template(
        "panel_cliente_google_ads/cuentas.html",
        nombre_nora=nombre_nora,
        cuentas=cuentas,
        cuentas_excluidas=cuentas_excluidas,
        cuentas_mostradas=cuentas_mostradas,
        mensaje=mensaje
    )
