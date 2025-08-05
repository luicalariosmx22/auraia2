#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper functions para manejar webhooks de Meta Ads
"""

import logging
from datetime import datetime
from typing import Any, Optional
from clientes.aura.utils.supabase_client import supabase

logger = logging.getLogger(__name__)

def registrar_evento_supabase(objeto: str, objeto_id: str, campo: str, valor: Any, hora_evento: str) -> bool:
    """
    Registra un evento de webhook en Supabase
    
    Args:
        objeto: Tipo de objeto (account, campaign, ad, etc.)
        objeto_id: ID del objeto afectado
        campo: Campo que cambió
        valor: Nuevo valor del campo
        hora_evento: Timestamp del evento
        
    Returns:
        bool: True si se registró exitosamente
    """
    try:
        # Preparar datos para insertar
        evento_data = {
            'objeto': objeto,
            'objeto_id': str(objeto_id),
            'campo': campo,
            'valor': str(valor) if valor is not None else None,
            'hora_evento': hora_evento,
            'procesado': False,
            'creado_en': datetime.utcnow().isoformat()
        }
        
        # Insertar en tabla de eventos de webhook
        response = supabase.table('logs_webhooks_meta').insert({
            'tipo_objeto': objeto,
            'objeto_id': str(objeto_id),
            'campo': campo,
            'valor': str(valor) if valor is not None else None,
            'timestamp': hora_evento
        }).execute()
        
        if response.data:
            logger.info(f"Evento webhook registrado: {objeto} {objeto_id} - {campo}")
            
            # Si es un evento de audiencia, marcar para sincronización
            if objeto == 'audience':
                marcar_audiencia_para_sync(objeto_id)
                
            return True
        else:
            logger.error(f"Error registrando evento webhook: {response}")
            return False
            
    except Exception as e:
        logger.error(f"Error en registrar_evento_supabase: {e}")
        return False

def marcar_audiencia_para_sync(audience_id: str) -> bool:
    """
    Marca una audiencia para sincronización después de recibir webhook
    
    Args:
        audience_id: ID de la audiencia que cambió
        
    Returns:
        bool: True si se marcó exitosamente
    """
    try:
        # Actualizar timestamp de última modificación
        update_data = {
            'webhook_actualizada': datetime.utcnow().isoformat(),
            'requiere_sync': True
        }
        
        response = supabase.table('meta_ads_audiencias')\
            .update(update_data)\
            .eq('audience_id', audience_id)\
            .execute()
            
        if response.data:
            logger.info(f"Audiencia {audience_id} marcada para sincronización")
            return True
        else:
            logger.warning(f"No se encontró audiencia {audience_id} para marcar")
            return False
            
    except Exception as e:
        logger.error(f"Error marcando audiencia para sync: {e}")
        return False

def marcar_anuncio_para_sync(ad_id: str) -> bool:
    """
    Marca un anuncio para sincronización después de recibir webhook
    
    Args:
        ad_id: ID del anuncio que cambió
        
    Returns:
        bool: True si se marcó exitosamente
    """
    try:
        # Actualizar timestamp de última modificación
        update_data = {
            'fecha_ultima_actualizacion': datetime.utcnow().isoformat(),
            'activo': True  # Marcar como activo para asegurar que se sincronice
        }
        
        response = supabase.table('meta_ads_anuncios_detalle')\
            .update(update_data)\
            .eq('ad_id', ad_id)\
            .execute()
            
        if response.data:
            logger.info(f"Anuncio {ad_id} marcado para sincronización")
            return True
        else:
            logger.warning(f"No se encontró anuncio {ad_id} para marcar")
            # Si no existe, podemos crear un registro temporal para sincronizar
            try:
                nuevo_anuncio_data = {
                    'ad_id': ad_id,
                    'id_cuenta_publicitaria': 'webhook_pending',
                    'fecha_inicio': datetime.now().date().isoformat(),
                    'fecha_fin': datetime.now().date().isoformat(),
                    'publisher_platform': 'facebook',
                    'fecha_ultima_actualizacion': datetime.utcnow().isoformat(),
                    'activo': True
                }
                
                supabase.table('meta_ads_anuncios_detalle').insert(nuevo_anuncio_data).execute()
                logger.info(f"Anuncio {ad_id} creado para sincronización posterior")
                return True
            except Exception as insert_error:
                logger.error(f"Error creando registro temporal para anuncio {ad_id}: {insert_error}")
                return False
            
    except Exception as e:
        logger.error(f"Error marcando anuncio para sync: {e}")
        return False

def procesar_eventos_pendientes() -> int:
    """
    Procesa eventos de webhook pendientes y actualiza datos correspondientes
    
    Returns:
        int: Número de eventos procesados
    """
    try:
        # Obtener eventos no procesados
        response = supabase.table('meta_webhook_eventos')\
            .select('*')\
            .eq('procesado', False)\
            .order('creado_en', desc=False)\
            .limit(100)\
            .execute()
            
        eventos = response.data if response.data else []
        eventos_procesados = 0
        
        for evento in eventos:
            if procesar_evento_individual(evento):
                eventos_procesados += 1
                
        logger.info(f"Procesados {eventos_procesados} eventos de webhook")
        return eventos_procesados
        
    except Exception as e:
        logger.error(f"Error procesando eventos pendientes: {e}")
        return 0

def procesar_evento_individual(evento: dict) -> bool:
    """
    Procesa un evento individual de webhook
    
    Args:
        evento: Datos del evento
        
    Returns:
        bool: True si se procesó exitosamente
    """
    try:
        objeto = evento.get('objeto')
        objeto_id = evento.get('objeto_id')
        campo = evento.get('campo')
        
        # Procesar según tipo de objeto
        if objeto == 'audience':
            return procesar_evento_audiencia(evento)
        elif objeto == 'campaign':
            return procesar_evento_campana(evento)
        elif objeto == 'ad':
            return procesar_evento_anuncio(evento)
        elif objeto == 'account':
            return procesar_evento_cuenta(evento)
        else:
            logger.warning(f"Tipo de objeto no soportado: {objeto}")
            # Marcar como procesado aunque no hagamos nada
            marcar_evento_procesado(evento['id'])
            return True
            
    except Exception as e:
        logger.error(f"Error procesando evento individual: {e}")
        return False

def procesar_evento_audiencia(evento: dict) -> bool:
    """Procesa eventos específicos de audiencias"""
    try:
        # Aquí podrías actualizar datos específicos de la audiencia
        # Por ahora solo marcamos como procesado
        marcar_evento_procesado(evento['id'])
        return True
    except Exception as e:
        logger.error(f"Error procesando evento de audiencia: {e}")
        return False

def procesar_evento_campana(evento: dict) -> bool:
    """Procesa eventos específicos de campañas"""
    try:
        # Aquí podrías actualizar datos específicos de la campaña
        marcar_evento_procesado(evento['id'])
        return True
    except Exception as e:
        logger.error(f"Error procesando evento de campaña: {e}")
        return False

def procesar_evento_anuncio(evento: dict) -> bool:
    """
    Procesa eventos específicos de anuncios
    
    Args:
        evento: Datos del evento
        
    Returns:
        bool: True si se procesó exitosamente
    """
    try:
        objeto_id = evento.get('objeto_id')
        campo = evento.get('campo')
        valor = evento.get('valor')
        
        if not objeto_id:
            logger.warning("Evento de anuncio sin objeto_id")
            marcar_evento_procesado(evento['id'])
            return True
        
        logger.info(f"Procesando evento de anuncio {objeto_id}: {campo} = {valor}")
        
        # Marcar anuncio para sincronización
        if marcar_anuncio_para_sync(str(objeto_id)):
            logger.info(f"Anuncio {objeto_id} marcado para sincronización")
        
        # Marcar evento como procesado
        marcar_evento_procesado(evento['id'])
        return True
        
    except Exception as e:
        logger.error(f"Error procesando evento de anuncio: {e}")
        return False

def procesar_evento_cuenta(evento: dict) -> bool:
    """Procesa eventos específicos de cuentas publicitarias"""
    try:
        # Aquí podrías actualizar datos específicos de la cuenta
        marcar_evento_procesado(evento['id'])
        return True
    except Exception as e:
        logger.error(f"Error procesando evento de cuenta: {e}")
        return False

def marcar_evento_procesado(evento_id: int) -> bool:
    """
    Marca un evento como procesado
    
    Args:
        evento_id: ID del evento
        
    Returns:
        bool: True si se marcó exitosamente
    """
    try:
        response = supabase.table('meta_webhook_eventos')\
            .update({'procesado': True, 'procesado_en': datetime.utcnow().isoformat()})\
            .eq('id', evento_id)\
            .execute()
            
        return bool(response.data)
        
    except Exception as e:
        logger.error(f"Error marcando evento como procesado: {e}")
        return False

def obtener_estadisticas_webhooks() -> dict:
    """
    Obtiene estadísticas de los webhooks recibidos
    
    Returns:
        dict: Estadísticas de webhooks
    """
    try:
        # Total de eventos
        response_total = supabase.table('meta_webhook_eventos')\
            .select('id', count='exact')\
            .execute()
            
        total_eventos = response_total.count if response_total.count else 0
        
        # Eventos procesados
        response_procesados = supabase.table('meta_webhook_eventos')\
            .select('id', count='exact')\
            .eq('procesado', True)\
            .execute()
            
        eventos_procesados = response_procesados.count if response_procesados.count else 0
        
        # Eventos por tipo de objeto
        response_tipos = supabase.table('meta_webhook_eventos')\
            .select('objeto')\
            .execute()
            
        tipos = {}
        if response_tipos.data:
            for evento in response_tipos.data:
                objeto = evento.get('objeto', 'unknown')
                tipos[objeto] = tipos.get(objeto, 0) + 1
        
        return {
            'total_eventos': total_eventos,
            'eventos_procesados': eventos_procesados,
            'eventos_pendientes': total_eventos - eventos_procesados,
            'tipos_objeto': tipos,
            'ultima_actualizacion': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de webhooks: {e}")
        return {
            'total_eventos': 0,
            'eventos_procesados': 0,
            'eventos_pendientes': 0,
            'tipos_objeto': {},
            'ultima_actualizacion': datetime.utcnow().isoformat()
        }
