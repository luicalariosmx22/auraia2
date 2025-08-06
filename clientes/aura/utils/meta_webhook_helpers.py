#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper functions para manejar webhooks de Meta Ads
"""

import logging
from datetime import datetime
from typing import Any, Optional
from clientes.aura.utils.supabase_client import supabase

# Importar Facebook Business SDK para registrar webhooks
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False
    logging.warning("⚠️ Facebook Business SDK no disponible. Instala con: pip install facebook-business")

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
            'timestamp': hora_evento,
            'procesado': False,
            'procesado_en': None
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
        response = supabase.table('logs_webhooks_meta')\
            .select('*')\
            .eq('procesado', False)\
            .order('timestamp', desc=False)\
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
        objeto = evento.get('tipo_objeto')  # Cambiado de 'objeto' a 'tipo_objeto'
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
        response = supabase.table('logs_webhooks_meta')\
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
        # Obtener todos los eventos
        response_eventos = supabase.table('logs_webhooks_meta')\
            .select('tipo_objeto, procesado')\
            .execute()
            
        eventos = response_eventos.data if response_eventos.data else []
        total_eventos = len(eventos)
        
        # Eventos procesados
        eventos_procesados = len([e for e in eventos if e.get('procesado', False)])
        
        # Eventos por tipo de objeto
        tipos = {}
        for evento in eventos:
            objeto = evento.get('tipo_objeto', 'unknown')
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

def registrar_webhook_en_cuenta(ad_account_id: str, access_token: str) -> dict:
    """
    Registra la app actual en una cuenta publicitaria para recibir eventos del webhook.
    
    Args:
        ad_account_id: ID de la cuenta publicitaria (ej: 'act_1234567890' o '1234567890')
        access_token: Token de acceso con permisos suficientes
        
    Returns:
        dict: Resultado de la operación
    """
    if not FACEBOOK_SDK_AVAILABLE:
        error_msg = "Facebook Business SDK no disponible. Instala con: pip install facebook-business"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    
    try:
        # Asegurar que el ID tenga el formato correcto (sin duplicar act_)
        if ad_account_id.startswith('act_'):
            clean_id = ad_account_id[4:]  # Remover 'act_' del inicio
        else:
            clean_id = ad_account_id
        
        formatted_account_id = f"act_{clean_id}"
        
        print(f"🔗 Registrando webhook para cuenta: {formatted_account_id}")
        
        # Inicializar la API de Facebook
        FacebookAdsApi.init(access_token=access_token)
        
        # Crear objeto de cuenta publicitaria
        cuenta = AdAccount(formatted_account_id)
        
        # Usar el método correcto del SDK
        respuesta = cuenta.create_subscribed_app()
        
        print(f"✅ Cuenta {formatted_account_id} registrada correctamente.")
        logger.info(f"Webhook registrado exitosamente para cuenta {formatted_account_id}")
        
        return {
            'success': True,
            'account_id': formatted_account_id,
            'response': str(respuesta),
            'message': f'Webhook registrado exitosamente para {formatted_account_id}'
        }
        
    except Exception as e:
        formatted_account_id = formatted_account_id if 'formatted_account_id' in locals() else ad_account_id
        error_msg = f"Error registrando webhook en {formatted_account_id}: {e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return {
            'success': False,
            'account_id': formatted_account_id,
            'error': str(e)
        }
        return {'error': str(e), 'account_id': formatted_account_id, 'success': False}

def registrar_webhooks_en_cuentas_activas(access_token: str) -> list:
    """
    Recorre todas las cuentas activas (no excluidas) y suscribe la app al webhook.
    
    Args:
        access_token: Token de acceso con permisos suficientes
        
    Returns:
        list: Lista de resultados para cada cuenta
    """
    print("📡 Registrando webhooks en cuentas activas...")
    logger.info("Iniciando registro masivo de webhooks en cuentas activas")
    
    try:
        # Obtener TODAS las cuentas y filtrar localmente (evitar problemas con NULL)
        resultado = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, estado_actual") \
            .execute()

        # Filtrar localmente: incluir NULL y todo excepto 'excluida'
        todas_cuentas = resultado.data or []
        cuentas = [
            cuenta for cuenta in todas_cuentas 
            if cuenta.get('estado_actual') != 'excluida'
        ]
        print(f"🔍 Se encontraron {len(cuentas)} cuentas activas")
        logger.info(f"Encontradas {len(cuentas)} cuentas activas para registrar webhooks")

        resultados = []
        
        for cuenta in cuentas:
            # El id_cuenta_publicitaria de la base de datos ya contiene solo números
            account_id = cuenta['id_cuenta_publicitaria']  # No agregar act_ aquí
            resultado = registrar_webhook_en_cuenta(account_id, access_token)
            
            # Agregar información adicional al resultado
            resultado_completo = {
                'account_id': f"act_{account_id}",  # Formato completo para mostrar
                'original_id': cuenta['id_cuenta_publicitaria'],
                'resultado': resultado,
                'success': resultado.get('success', 'error' not in resultado)
            }
            
            resultados.append(resultado_completo)
            
            # Pausa pequeña entre registros para evitar rate limiting
            import time
            time.sleep(0.5)
        
        exitosos = len([r for r in resultados if r['success']])
        fallidos = len(resultados) - exitosos
        
        print(f"📊 Registro completado: {exitosos} exitosos, {fallidos} fallidos")
        logger.info(f"Registro masivo completado: {exitosos} exitosos, {fallidos} fallidos")
        
        return resultados
        
    except Exception as e:
        error_msg = f"Error en registro masivo de webhooks: {e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return [{'error': str(e), 'success': False}]

def verificar_webhook_registrado(ad_account_id: str, access_token: str) -> dict:
    """
    Verifica si el webhook está registrado en una cuenta publicitaria.
    
    Args:
        ad_account_id: ID de la cuenta publicitaria
        access_token: Token de acceso
        
    Returns:
        dict: Estado del registro del webhook
    """
    if not FACEBOOK_SDK_AVAILABLE:
        return {'error': 'Facebook Business SDK no disponible', 'registered': False}
    
    try:
        # Asegurar que el ID tenga el formato correcto (sin duplicar act_)
        if ad_account_id.startswith('act_'):
            clean_id = ad_account_id[4:]  # Remover 'act_' del inicio
        else:
            clean_id = ad_account_id
        
        formatted_account_id = f"act_{clean_id}"
        
        print(f"🔍 Verificando webhook para cuenta: {formatted_account_id}")
        
        # Usar requests directamente para hacer la llamada a la API
        import requests
        
        url = f"https://graph.facebook.com/v19.0/{formatted_account_id}/subscribed_apps"
        params = {
            'access_token': access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            apps_suscritas = response_data.get('data', [])
            esta_registrado = len(apps_suscritas) > 0
            
            print(f"✅ Cuenta {formatted_account_id}: {'Registrada' if esta_registrado else 'No registrada'}")
            logger.info(f"Verificación webhook {formatted_account_id}: {'registrado' if esta_registrado else 'no registrado'}")
            
            return {
                'account_id': formatted_account_id,
                'registered': esta_registrado,
                'subscribed_apps': apps_suscritas,
                'success': True
            }
        else:
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get('error', {}).get('message', error_data.get('message', 'Error desconocido'))
                else:
                    error_msg = str(error_data)
            except:
                error_msg = response.text or 'Error desconocido'
            
            print(f"❌ Error HTTP {response.status_code}: {error_msg}")
            logger.error(f"Error verificando webhook {formatted_account_id}: HTTP {response.status_code} - {error_msg}")
            
            return {
                'account_id': formatted_account_id,
                'registered': False,
                'error': error_msg,
                'success': False,
                'status_code': response.status_code
            }
        
    except Exception as e:
        formatted_account_id = formatted_account_id if 'formatted_account_id' in locals() else ad_account_id
        error_msg = f"Error verificando webhook en {formatted_account_id}: {e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return {
            'account_id': formatted_account_id,
            'registered': False,
            'error': str(e),
            'success': False
        }
