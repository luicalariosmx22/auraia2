# -*- coding: utf-8 -*-
"""
Vista para gestionar la asociación de cuentas de Google Ads con empresas
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.services.google_ads_service import google_ads_service
from clientes.aura.services.google_ads_empresa_service import google_ads_empresa_service
import logging

@panel_cliente_google_ads_bp.route("/asociar-empresas", methods=["GET", "POST"], strict_slashes=False)
def asociar_cuentas_empresas(nombre_nora):
    """
    Página para asociar cuentas de Google Ads con empresas
    """
    mensaje = None
    tipo_mensaje = "info"
    
    try:
        # Obtener cuentas de Google Ads
        total_cuentas, cuentas_google_ads = google_ads_service.listar_cuentas_accesibles()
        
        # Obtener empresas disponibles
        empresas = google_ads_empresa_service.obtener_empresas_disponibles(nombre_nora)
        
        # Obtener resumen de asociaciones actuales
        resumen = google_ads_empresa_service.obtener_resumen_asociaciones(nombre_nora)
        
        if request.method == "POST":
            accion = request.form.get("accion")
            
            if accion == "asociar_automatica":
                # Asociación automática basada en nombres
                resultado = google_ads_empresa_service.asociar_cuentas_automaticamente(
                    nombre_nora, cuentas_google_ads
                )
                
                if resultado["asociadas"] > 0:
                    mensaje = f"✅ Se asociaron {resultado['asociadas']} cuentas de {resultado['total']} disponibles"
                    tipo_mensaje = "success"
                else:
                    mensaje = "⚠️ No se pudieron asociar cuentas automáticamente"
                    tipo_mensaje = "warning"
                
                if resultado["errores"]:
                    mensaje += f" ({len(resultado['errores'])} errores)"
                
            elif accion == "asociar_manual":
                # Asociación manual
                customer_id = request.form.get("customer_id")
                empresa_id = request.form.get("empresa_id")
                
                if customer_id and empresa_id:
                    # Buscar información de la cuenta
                    cuenta_info = next((c for c in cuentas_google_ads if c['id'] == customer_id), None)
                    
                    if cuenta_info:
                        if google_ads_empresa_service.asociar_cuenta_con_empresa(
                            customer_id, empresa_id, cuenta_info['nombre'], cuenta_info
                        ):
                            mensaje = f"✅ Cuenta {cuenta_info['nombre']} asociada correctamente"
                            tipo_mensaje = "success"
                        else:
                            mensaje = "❌ Error al asociar la cuenta"
                            tipo_mensaje = "error"
                    else:
                        mensaje = "❌ Cuenta no encontrada"
                        tipo_mensaje = "error"
                else:
                    mensaje = "❌ Faltan datos para la asociación manual"
                    tipo_mensaje = "error"
            
            elif accion == "desasociar":
                # Desasociar cuenta
                customer_id = request.form.get("customer_id")
                empresa_id = request.form.get("empresa_id")
                
                if customer_id and empresa_id:
                    if google_ads_empresa_service.desasociar_cuenta(customer_id, empresa_id):
                        mensaje = "✅ Cuenta desasociada correctamente"
                        tipo_mensaje = "success"
                    else:
                        mensaje = "❌ Error al desasociar la cuenta"
                        tipo_mensaje = "error"
                else:
                    mensaje = "❌ Faltan datos para desasociar"
                    tipo_mensaje = "error"
            
            # Recargar resumen después de cambios
            if accion in ["asociar_automatica", "asociar_manual", "desasociar"]:
                resumen = google_ads_empresa_service.obtener_resumen_asociaciones(nombre_nora)
        
        # Identificar cuentas no asociadas
        cuentas_asociadas_ids = set()
        for empresa_detalle in resumen.get("detalle_empresas", []):
            for cuenta in empresa_detalle["cuentas"]:
                cuentas_asociadas_ids.add(cuenta["customer_id"])
        
        cuentas_no_asociadas = [
            cuenta for cuenta in cuentas_google_ads 
            if cuenta['id'] not in cuentas_asociadas_ids
        ]
        
    except Exception as e:
        mensaje = f"❌ Error al obtener información: {str(e)}"
        tipo_mensaje = "error"
        cuentas_google_ads = []
        empresas = []
        resumen = {"error": str(e)}
        cuentas_no_asociadas = []
        
        logging.exception(f"Error en asociar_cuentas_empresas para {nombre_nora}")
    
    return render_template(
        "panel_cliente_google_ads/asociar_empresas.html",
        nombre_nora=nombre_nora,
        cuentas_google_ads=cuentas_google_ads,
        empresas=empresas,
        resumen=resumen,
        cuentas_no_asociadas=cuentas_no_asociadas,
        mensaje=mensaje,
        tipo_mensaje=tipo_mensaje
    )

@panel_cliente_google_ads_bp.route("/api/asociaciones/<nombre_nora>", methods=["GET"])
def api_obtener_asociaciones(nombre_nora):
    """
    API para obtener asociaciones de cuentas con empresas
    """
    try:
        resumen = google_ads_empresa_service.obtener_resumen_asociaciones(nombre_nora)
        return jsonify({"success": True, "data": resumen})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@panel_cliente_google_ads_bp.route("/api/asociar", methods=["POST"])
def api_asociar_cuenta():
    """
    API para asociar una cuenta con una empresa
    """
    try:
        data = request.get_json()
        customer_id = data.get("customer_id")
        empresa_id = data.get("empresa_id")
        nombre_cuenta = data.get("nombre_cuenta")
        cuenta_info = data.get("cuenta_info", {})
        
        if not all([customer_id, empresa_id, nombre_cuenta]):
            return jsonify({"success": False, "error": "Faltan parámetros requeridos"}), 400
        
        resultado = google_ads_empresa_service.asociar_cuenta_con_empresa(
            customer_id, empresa_id, nombre_cuenta, cuenta_info
        )
        
        if resultado:
            return jsonify({"success": True, "message": "Cuenta asociada correctamente"})
        else:
            return jsonify({"success": False, "error": "Error al asociar cuenta"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
