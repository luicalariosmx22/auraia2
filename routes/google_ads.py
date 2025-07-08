#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rutas para la gestión de Google Ads en el panel de administración.
Incluye endpoints para actualizar datos y obtener reportes.
"""

from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime
from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
from actualizar_google_ads_cuentas import actualizar_cuenta, actualizar_todas_las_cuentas, actualizar_ultimos_7_dias

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
google_ads_bp = Blueprint('google_ads', __name__, url_prefix='/api/google-ads')

@google_ads_bp.route('/listar-cuentas', methods=['GET'])
def listar_cuentas():
    """Endpoint para listar todas las cuentas de Google Ads accesibles"""
    try:
        service = GoogleAdsService()
        total, cuentas = service.listar_cuentas_accesibles()
        
        return jsonify({
            "success": True,
            "total": total,
            "cuentas": cuentas
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error listando cuentas de Google Ads: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@google_ads_bp.route('/actualizar-datos', methods=['POST'])
def actualizar_datos():
    """
    Endpoint para actualizar datos de Google Ads en Supabase
    
    Parámetros (JSON):
    - customer_id: (opcional) ID de cuenta específica para actualizar
    - incluir_mcc: (opcional) Si es true, incluye la cuenta MCC principal
    - incluir_anuncios: (opcional) Si es true, actualiza también los anuncios
    """
    try:
        # Obtener parámetros
        data = request.get_json() or {}
        customer_id = data.get('customer_id')
        incluir_mcc = data.get('incluir_mcc', False)
        incluir_anuncios = data.get('incluir_anuncios', False)
        
        # Registrar inicio de la operación
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"🚀 Iniciando actualización de datos de Google Ads: {timestamp}")
        
        if customer_id:
            # Actualizar una cuenta específica
            logger.info(f"🎯 Actualizando cuenta específica: {customer_id}")
            service = GoogleAdsService()
            total, cuentas = service.listar_cuentas_accesibles()
            
            for cuenta in cuentas:
                if cuenta["id"] == customer_id and cuenta.get("accesible", False):
                    resultado = actualizar_cuenta(customer_id, cuenta["nombre"], incluir_anuncios)
                    return jsonify({
                        "success": True,
                        "mensaje": f"Datos de cuenta {customer_id} actualizados correctamente",
                        "resultado": resultado
                    }), 200
            
            return jsonify({
                "success": False,
                "error": f"No se encontró la cuenta {customer_id} o no es accesible"
            }), 404
        
        else:
            # Actualizar todas las cuentas
            logger.info(f"📊 Actualizando todas las cuentas")
            resultados = actualizar_todas_las_cuentas(not incluir_mcc, incluir_anuncios)
            
            return jsonify({
                "success": True,
                "mensaje": f"Actualización de datos completada para {resultados['cuentas_procesadas']} cuentas",
                "resultado": resultados
            }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en actualización de datos de Google Ads: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@google_ads_bp.route('/estadisticas/<string:customer_id>', methods=['GET'])
def obtener_estadisticas(customer_id):
    """Endpoint para obtener estadísticas de una cuenta específica"""
    try:
        dias = request.args.get('dias', 30, type=int)
        
        service = GoogleAdsService()
        estadisticas = service.obtener_estadisticas_cuenta(customer_id, dias)
        
        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "estadisticas": estadisticas
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de cuenta {customer_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@google_ads_bp.route('/actualizar-ultimos-7-dias', methods=['POST'])
def actualizar_ultimos_7_dias_endpoint():
    """
    Endpoint para actualizar datos de Google Ads de los últimos 7 días
    Este endpoint está diseñado específicamente para ser llamado desde un botón en el frontend
    
    Parámetros (JSON):
    - incluir_mcc: (opcional) Si es true, incluye la cuenta MCC principal (default: false)
    - incluir_anuncios: (opcional) Si es true, actualiza también los anuncios (default: true)
    """
    try:
        # Obtener parámetros
        data = request.get_json() or {}
        incluir_mcc = data.get('incluir_mcc', False)
        incluir_anuncios = data.get('incluir_anuncios', True)  # Por defecto incluimos anuncios
        
        # Registrar inicio de la operación
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"🚀 Iniciando actualización de últimos 7 días de Google Ads: {timestamp}")
        
        # Actualizar datos de los últimos 7 días
        resultados = actualizar_ultimos_7_dias(not incluir_mcc, incluir_anuncios)
        
        return jsonify({
            "success": True,
            "mensaje": f"Actualización de datos de los últimos 7 días completada para {resultados.get('cuentas_procesadas', 0)} cuentas",
            "resultado": resultados
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en actualización de últimos 7 días de Google Ads: {e}")
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(error_traceback)
        
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": error_traceback
        }), 500
