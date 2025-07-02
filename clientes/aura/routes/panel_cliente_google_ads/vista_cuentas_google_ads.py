from flask import render_template, request, redirect, url_for, flash, jsonify
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.services.google_ads_service import google_ads_service
from clientes.aura.services.google_ads_empresa_service_mejorado import google_ads_empresa_service_mejorado
import os
import logging

@panel_cliente_google_ads_bp.route("/cuentas", methods=["GET", "POST"], strict_slashes=False)
def ver_cuentas_google_ads(nombre_nora):
    mensaje = None
    cuentas_excluidas = set()
    
    if request.method == "POST":
        # Verificar si es una petición AJAX para asignar empresa
        if request.form.get('accion') == 'asignar_empresa':
            customer_id = request.form.get('customer_id')
            empresa_id = request.form.get('empresa_id')
            
            if not customer_id or not empresa_id:
                return jsonify({'success': False, 'error': 'Faltan parámetros'})
            
            # Realizar la asignación con el nombre_nora correcto
            if google_ads_empresa_service_mejorado.asociar_cuenta_empresa(customer_id, empresa_id, nombre_nora):
                return jsonify({'success': True, 'message': 'Empresa asignada correctamente'})
            else:
                return jsonify({'success': False, 'error': 'Error al asignar empresa'})
        
        # Manejo original de exclusiones
        cuentas_excluidas = set(request.form.getlist("excluir"))
        mensaje = f"Se han excluido {len(cuentas_excluidas)} cuentas de la operación."
    
    try:
        # Usar el nuevo servicio de Google Ads para obtener TODAS las cuentas del MCC
        total, cuentas_raw = google_ads_service.listar_cuentas_accesibles()
        
        # Obtener empresas disponibles para el selector
        empresas_disponibles = google_ads_empresa_service_mejorado.obtener_empresas_disponibles(nombre_nora)
        
        # Procesar cuentas para la visualización
        cuentas_procesadas = []
        cuentas_mostradas = []
        
        for cuenta in cuentas_raw:
            # Obtener información de empresa asociada
            empresa_asociada = google_ads_empresa_service_mejorado.obtener_empresa_por_cuenta(cuenta['id'])
            
            # Crear estructura consistente para la plantilla
            cuenta_procesada = {
                'id': cuenta['id'],
                'data': cuenta,  # Datos completos de la cuenta
                'resource_name': cuenta['id'],
                'name': cuenta['nombre'],
                'display_name': f"{cuenta['nombre']} ({cuenta['id']})",
                'moneda': cuenta.get('moneda', 'N/A'),
                'zona_horaria': cuenta.get('zona_horaria', 'N/A'),
                'es_test': cuenta.get('es_test', False),
                'accesible': cuenta.get('accesible', True),
                'problema': cuenta.get('problema', None),
                'empresa_asignada': empresa_asociada
            }
            
            cuentas_procesadas.append(cuenta_procesada)
            
            # Solo agregar a mostradas si no está excluida
            if cuenta['id'] not in cuentas_excluidas:
                cuentas_mostradas.append(cuenta_procesada)
        
        # Logging para desarrollo
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[DEV] Total cuentas MCC encontradas: {total}")
            logging.debug(f"[DEV] Cuentas procesadas: {len(cuentas_procesadas)}")
            logging.debug(f"[DEV] Cuentas excluidas: {cuentas_excluidas}")
            logging.debug(f"[DEV] Cuentas mostradas: {len(cuentas_mostradas)}")
            logging.debug(f"[DEV] Nombres cuentas: {[c['name'] for c in cuentas_procesadas]}")
        
        if total > 0:
            mensaje = f"✅ Se encontraron {total} cuentas en el MCC (My Client Center)"
        else:
            mensaje = "⚠️ No se encontraron cuentas en el MCC"
            
    except Exception as e:
        cuentas_procesadas = []
        cuentas_mostradas = []
        empresas_disponibles = []
        mensaje = f"❌ Error al obtener cuentas del MCC: {str(e)}"
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.exception("[DEV] Error obteniendo cuentas del MCC")
    
    return render_template(
        "panel_cliente_google_ads/cuentas.html",
        nombre_nora=nombre_nora,
        cuentas=cuentas_procesadas,
        cuentas_excluidas=cuentas_excluidas,
        cuentas_mostradas=cuentas_mostradas,
        empresas_disponibles=empresas_disponibles,
        mensaje=mensaje
    )
