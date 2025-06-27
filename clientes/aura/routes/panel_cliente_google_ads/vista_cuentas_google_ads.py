from flask import render_template, request, redirect, url_for, flash
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from .listar_cuentas import listar_cuentas_publicitarias
import os
import logging

@panel_cliente_google_ads_bp.route("/cuentas", methods=["GET", "POST"], strict_slashes=False)
def ver_cuentas_google_ads(nombre_nora):
    mensaje = None
    cuentas_excluidas = set()
    if request.method == "POST":
        cuentas_excluidas = set(request.form.getlist("excluir"))
        mensaje = f"Se han excluido {len(cuentas_excluidas)} cuentas de la operación."
    try:
        total, cuentas = listar_cuentas_publicitarias()
        cuentas = cuentas or []
        
        # Procesar cuentas para extraer IDs y crear estructura consistente
        cuentas_procesadas = []
        cuentas_mostradas = []
        
        for cuenta in cuentas:
            # Extraer ID de la cuenta
            cuenta_id = cuenta.get('resource_name') or cuenta.get('id') or str(cuenta)
            
            # Crear estructura consistente con ID
            cuenta_procesada = {
                'id': cuenta_id,
                'data': cuenta,  # Datos originales
                'resource_name': cuenta.get('resource_name', cuenta_id),
                'name': cuenta.get('name', cuenta_id),
                'display_name': cuenta.get('name', cuenta_id) or cuenta_id
            }
            
            cuentas_procesadas.append(cuenta_procesada)
            
            # Solo agregar a mostradas si no está excluida
            if cuenta_id not in cuentas_excluidas:
                cuentas_mostradas.append(cuenta_procesada)
        
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[DEV] Total cuentas encontradas: {total}")
            logging.debug(f"[DEV] Cuentas procesadas: {len(cuentas_procesadas)}")
            logging.debug(f"[DEV] Cuentas excluidas: {cuentas_excluidas}")
            logging.debug(f"[DEV] Cuentas mostradas: {len(cuentas_mostradas)}")
    except Exception as e:
        cuentas_procesadas = []
        cuentas_mostradas = []
        mensaje = f"Error al obtener cuentas: {e}"
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.exception("[DEV] Error buscando cuentas Google Ads")
    
    return render_template(
        "panel_cliente_google_ads/cuentas.html",
        nombre_nora=nombre_nora,
        cuentas=cuentas_procesadas,  # Usar cuentas procesadas con IDs
        cuentas_excluidas=cuentas_excluidas,
        cuentas_mostradas=cuentas_mostradas,
        mensaje=mensaje
    )
