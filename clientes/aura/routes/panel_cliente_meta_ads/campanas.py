# Archivo: clientes/aura/routes/panel_cliente_meta_ads/campanas.py
"""
Módulo para la gestión avanzada de campañas Meta Ads dentro del panel cliente.
Incluye funciones para plantillas, automatizaciones, auditorías, alertas, exportaciones, IA y análisis.
"""
from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta
import os
import hashlib

# Importaciones para Meta Ads SDK
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.customaudience import CustomAudience
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    print("⚠️ facebook-business SDK no está instalado. Funcionalidad de audiencias limitada.")
    FACEBOOK_SDK_AVAILABLE = False

# No necesitamos crear un blueprint separado, las rutas van en panel_cliente_meta_ads_bp

def obtener_campanas_con_filtros(nombre_nora, filtros=None):
    """
    Obtiene campañas aplicando filtros específicos
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        filtros (dict): Diccionario con filtros a aplicar
        
    Returns:
        list: Lista de campañas filtradas
    """
    try:
        # Obtener cuentas del nombre_nora
        cuentas_nora = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        if not cuentas_nora.data:
            return []
            
        cuentas_ids = [c["id_cuenta_publicitaria"] for c in cuentas_nora.data]
        
        # Consulta base para anuncios
        query = supabase.table("meta_ads_anuncios_detalle") \
            .select("*, meta_ads_cuentas!inner(nombre_cliente)") \
            .in_("id_cuenta_publicitaria", cuentas_ids)
        
        # Aplicar filtros si existen
        if filtros:
            if filtros.get('cuenta_id'):
                query = query.eq("id_cuenta_publicitaria", filtros['cuenta_id'])
            if filtros.get('fecha_inicio'):
                query = query.gte("fecha_inicio", filtros['fecha_inicio'])
            if filtros.get('fecha_fin'):
                query = query.lte("fecha_fin", filtros['fecha_fin'])
            if filtros.get('estado'):
                activo = filtros['estado'] == 'ACTIVE'
                query = query.eq("activo", activo)
        
        anuncios = query.execute()
        
        # Agrupar por campaña
        campanas_data = {}
        for anuncio in anuncios.data or []:
            campana_id = anuncio.get('campana_id')
            if not campana_id:
                continue
                
            if campana_id not in campanas_data:
                campanas_data[campana_id] = {
                    'id': campana_id,
                    'name': anuncio.get('nombre_campana', f'Campaña {campana_id}'),
                    'status': 'ACTIVE' if anuncio.get('activo') else 'PAUSED',
                    'account_name': anuncio.get('meta_ads_cuentas', {}).get('nombre_cliente', ''),
                    'account_id': anuncio.get('id_cuenta_publicitaria'),
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'ctr': 0,
                    'cpc': 0,
                    'created_time': anuncio.get('fecha_sincronizacion', ''),
                    'objetivo': 'CONVERSIONS',  # Por defecto
                    'anuncios_count': 0
                }
            
            # Sumar métricas
            campanas_data[campana_id]['spend'] += anuncio.get('importe_gastado', 0) or 0
            campanas_data[campana_id]['impressions'] += anuncio.get('impresiones', 0) or 0
            campanas_data[campana_id]['clicks'] += anuncio.get('clicks', 0) or 0
            campanas_data[campana_id]['reach'] += anuncio.get('alcance', 0) or 0
            campanas_data[campana_id]['anuncios_count'] += 1
        
        # Calcular métricas derivadas
        for campana in campanas_data.values():
            if campana['impressions'] > 0:
                campana['ctr'] = (campana['clicks'] / campana['impressions']) * 100
            if campana['clicks'] > 0:
                campana['cpc'] = campana['spend'] / campana['clicks']
        
        return list(campanas_data.values())
        
    except Exception as e:
        print(f"Error obteniendo campañas: {e}")
        return []

def obtener_detalle_campana(campana_id, nombre_nora):
    """
    Obtiene el detalle completo de una campaña específica
    
    Args:
        campana_id (str): ID de la campaña
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        dict: Detalle de la campaña o None si no se encuentra
    """
    try:
        # Verificar que la campaña pertenece a una cuenta del nombre_nora
        cuentas_nora = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        if not cuentas_nora.data:
            return None
            
        cuentas_ids = [c["id_cuenta_publicitaria"] for c in cuentas_nora.data]
        
        # Buscar anuncios de la campaña
        anuncios = supabase.table("meta_ads_anuncios_detalle") \
            .select("*, meta_ads_cuentas!inner(nombre_cliente)") \
            .eq("campana_id", campana_id) \
            .in_("id_cuenta_publicitaria", cuentas_ids) \
            .execute()
        
        if not anuncios.data:
            return None
        
        # Construir detalle agregando datos de todos los anuncios
        primer_anuncio = anuncios.data[0]
        detalle = {
            'id': campana_id,
            'name': primer_anuncio.get('nombre_campana', f'Campaña {campana_id}'),
            'status': 'ACTIVE' if primer_anuncio.get('activo') else 'PAUSED',
            'account_name': primer_anuncio.get('meta_ads_cuentas', {}).get('nombre_cliente', ''),
            'account_id': primer_anuncio.get('id_cuenta_publicitaria'),
            'objective': 'CONVERSIONS',  # Placeholder
            'created_time': primer_anuncio.get('fecha_sincronizacion', ''),
            'spend': sum(a.get('importe_gastado', 0) or 0 for a in anuncios.data),
            'impressions': sum(a.get('impresiones', 0) or 0 for a in anuncios.data),
            'clicks': sum(a.get('clicks', 0) or 0 for a in anuncios.data),
            'reach': sum(a.get('alcance', 0) or 0 for a in anuncios.data),
            'frequency': 0,
            'ctr': 0,
            'cpc': 0,
            'cpm': 0,
            'anuncios': []
        }
        
        # Calcular métricas derivadas
        if detalle['impressions'] > 0:
            detalle['ctr'] = (detalle['clicks'] / detalle['impressions']) * 100
            detalle['cpm'] = (detalle['spend'] / detalle['impressions']) * 1000
        if detalle['clicks'] > 0:
            detalle['cpc'] = detalle['spend'] / detalle['clicks']
        if detalle['reach'] > 0:
            detalle['frequency'] = detalle['impressions'] / detalle['reach']
        
        # Agregar lista de anuncios
        for anuncio in anuncios.data:
            detalle['anuncios'].append({
                'id': anuncio.get('ad_id'),
                'name': anuncio.get('nombre_anuncio', 'Sin nombre'),
                'status': 'ACTIVE' if anuncio.get('activo') else 'PAUSED',
                'spend': anuncio.get('importe_gastado', 0) or 0,
                'impressions': anuncio.get('impresiones', 0) or 0,
                'clicks': anuncio.get('clicks', 0) or 0,
                'ctr': (anuncio.get('clicks', 0) / anuncio.get('impresiones', 1)) * 100 if anuncio.get('impresiones', 0) > 0 else 0
            })
        
        return detalle
        
    except Exception as e:
        print(f"Error obteniendo detalle de campaña {campana_id}: {e}")
        return None

def obtener_estadisticas_campanas(nombre_nora, filtros=None):
    """
    Obtiene estadísticas resumidas de las campañas
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        filtros (dict): Filtros aplicados
        
    Returns:
        dict: Estadísticas resumidas
    """
    try:
        campanas = obtener_campanas_con_filtros(nombre_nora, filtros)
        
        estadisticas = {
            'total_campanas': len(campanas),
            'campanas_activas': len([c for c in campanas if c['status'] == 'ACTIVE']),
            'campanas_pausadas': len([c for c in campanas if c['status'] == 'PAUSED']),
            'gasto_total': sum(c['spend'] for c in campanas),
            'impresiones_total': sum(c['impressions'] for c in campanas),
            'clicks_total': sum(c['clicks'] for c in campanas),
            'alcance_total': sum(c.get('reach', 0) for c in campanas),
            'ctr_promedio': 0,
            'cpc_promedio': 0
        }
        
        # Calcular promedios
        if estadisticas['impresiones_total'] > 0:
            estadisticas['ctr_promedio'] = (estadisticas['clicks_total'] / estadisticas['impresiones_total']) * 100
        
        if estadisticas['clicks_total'] > 0:
            estadisticas['cpc_promedio'] = estadisticas['gasto_total'] / estadisticas['clicks_total']
        
        return estadisticas
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'total_campanas': 0,
            'campanas_activas': 0,
            'campanas_pausadas': 0,
            'gasto_total': 0,
            'impresiones_total': 0,
            'clicks_total': 0,
            'alcance_total': 0,
            'ctr_promedio': 0,
            'cpc_promedio': 0
        }

# Funciones auxiliares para futuras implementaciones

def generar_reporte_campana(campana_id, nombre_nora, formato='json'):
    """
    Genera un reporte detallado de una campaña
    """
    # TODO: Implementar generación de reportes
    pass

def automatizar_campana(campana_id, reglas):
    """
    Aplica reglas de automatización a una campaña
    """
    # TODO: Implementar automatización
    pass

def auditar_campana(campana_id):
    """
    Realiza una auditoría de la campaña
    """
    # TODO: Implementar auditoría
    pass

# ============================================================================
# FUNCIONES PARA AUDIENCIAS META ADS
# ============================================================================

def obtener_audiencias_con_filtros(nombre_nora, filtros=None):
    """
    Obtiene audiencias aplicando filtros específicos
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        filtros (dict): Diccionario con filtros a aplicar
        
    Returns:
        list: Lista de audiencias filtradas
    """
    try:
        # Consulta base
        query = supabase.table("meta_ads_audiencias") \
            .select("*") \
            .eq("nombre_nora", nombre_nora)
        
        # Aplicar filtros si existen
        if filtros:
            if filtros.get('cuenta_id'):
                query = query.eq("ad_account_id", filtros['cuenta_id'])
            if filtros.get('tipo_audiencia'):
                query = query.eq("tipo_audiencia", filtros['tipo_audiencia'])
            if filtros.get('estado'):
                query = query.eq("estado", filtros['estado'])
            if filtros.get('origen'):
                query = query.eq("origen", filtros['origen'])
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order("creada_en", desc=True)
        
        resultado = query.execute()
        audiencias = resultado.data or []
        
        # Obtener información de las cuentas para agregar datos de empresa
        cuentas_info = {}
        if audiencias:
            # Obtener todas las cuentas únicas
            cuentas_ids = list(set([aud.get('ad_account_id') for aud in audiencias if aud.get('ad_account_id')]))
            
            if cuentas_ids:
                cuentas_query = supabase.table("meta_ads_cuentas") \
                    .select("id_cuenta_publicitaria, nombre_cliente, empresa_id, empresa:cliente_empresas(nombre_empresa)") \
                    .in_("id_cuenta_publicitaria", cuentas_ids) \
                    .execute()
                
                for cuenta in cuentas_query.data or []:
                    cuentas_info[cuenta['id_cuenta_publicitaria']] = cuenta
        
        # Enriquecer datos con información adicional
        for audiencia in audiencias:
            # Información de la empresa
            cuenta_id = audiencia.get('ad_account_id')
            if cuenta_id and cuenta_id in cuentas_info:
                cuenta = cuentas_info[cuenta_id]
                audiencia['nombre_cliente'] = cuenta.get('nombre_cliente', 'Sin cliente')
                empresa_info = cuenta.get('empresa')
                if empresa_info:
                    audiencia['nombre_empresa'] = empresa_info.get('nombre_empresa', 'Sin empresa')
                else:
                    audiencia['nombre_empresa'] = 'Sin empresa'
            else:
                audiencia['nombre_cliente'] = 'Sin cliente'
                audiencia['nombre_empresa'] = 'Sin empresa'
            
            # Formatear fecha de creación
            if audiencia.get('creada_en'):
                try:
                    fecha = datetime.fromisoformat(audiencia['creada_en'].replace('Z', '+00:00'))
                    audiencia['creada_en_fmt'] = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    audiencia['creada_en_fmt'] = 'N/A'
            else:
                audiencia['creada_en_fmt'] = 'N/A'
            
            # Formatear tamaño
            tamaño = audiencia.get('tamaño_aproximado', 0) or 0
            if tamaño >= 1000000:
                audiencia['tamaño_fmt'] = f"{tamaño/1000000:.1f}M"
            elif tamaño >= 1000:
                audiencia['tamaño_fmt'] = f"{tamaño/1000:.1f}K"
            else:
                audiencia['tamaño_fmt'] = str(tamaño)
            
            # Estado con formato visual
            estado = audiencia.get('estado', 'unknown')
            if estado == '200':
                audiencia['estado_badge'] = {'text': 'Activa', 'class': 'bg-green-100 text-green-800'}
            elif estado == '300':
                audiencia['estado_badge'] = {'text': 'Pequeña', 'class': 'bg-yellow-100 text-yellow-800'}
            elif estado == '441':
                audiencia['estado_badge'] = {'text': 'Completándose', 'class': 'bg-blue-100 text-blue-800'}
            elif estado == '450':
                audiencia['estado_badge'] = {'text': 'Desactualizada', 'class': 'bg-orange-100 text-orange-800'}
            elif estado == '433':
                audiencia['estado_badge'] = {'text': 'Error', 'class': 'bg-red-100 text-red-800'}
            else:
                audiencia['estado_badge'] = {'text': f'Estado {estado}', 'class': 'bg-gray-100 text-gray-800'}
        
        return audiencias
        
    except Exception as e:
        print(f"Error obteniendo audiencias: {e}")
        return []

def obtener_detalle_audiencia(audience_id, nombre_nora):
    """
    Obtiene el detalle completo de una audiencia específica
    
    Args:
        audience_id (str): ID de la audiencia
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        dict: Detalle de la audiencia o None si no se encuentra
    """
    try:
        # Buscar audiencia en base de datos
        resultado = supabase.table("meta_ads_audiencias") \
            .select("*") \
            .eq("audience_id", audience_id) \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()
        
        if resultado.data:
            audiencia = resultado.data
            
            # Obtener información de la empresa
            cuenta_id = audiencia.get('ad_account_id')
            if cuenta_id:
                cuenta_query = supabase.table("meta_ads_cuentas") \
                    .select("nombre_cliente, empresa_id, empresa:cliente_empresas(nombre_empresa)") \
                    .eq("id_cuenta_publicitaria", cuenta_id) \
                    .single() \
                    .execute()
                
                if cuenta_query.data:
                    cuenta = cuenta_query.data
                    audiencia['nombre_cliente'] = cuenta.get('nombre_cliente', 'Sin cliente')
                    empresa_info = cuenta.get('empresa')
                    if empresa_info:
                        audiencia['nombre_empresa'] = empresa_info.get('nombre_empresa', 'Sin empresa')
                    else:
                        audiencia['nombre_empresa'] = 'Sin empresa'
                else:
                    audiencia['nombre_cliente'] = 'Sin cliente'
                    audiencia['nombre_empresa'] = 'Sin empresa'
            else:
                audiencia['nombre_cliente'] = 'Sin cliente'
                audiencia['nombre_empresa'] = 'Sin empresa'
            
            # Formatear fecha de creación
            if audiencia.get('creada_en'):
                try:
                    fecha = datetime.fromisoformat(audiencia['creada_en'].replace('Z', '+00:00'))
                    audiencia['creada_en_fmt'] = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    audiencia['creada_en_fmt'] = 'N/A'
            else:
                audiencia['creada_en_fmt'] = 'N/A'
            
            # Formatear tamaño
            tamaño = audiencia.get('tamaño_aproximado', 0) or 0
            if tamaño >= 1000000:
                audiencia['tamaño_fmt'] = f"{tamaño/1000000:.1f}M"
            elif tamaño >= 1000:
                audiencia['tamaño_fmt'] = f"{tamaño/1000:.1f}K"
            else:
                audiencia['tamaño_fmt'] = str(tamaño)
            
            # Estado con formato visual
            estado = audiencia.get('estado', 'unknown').upper()
            if estado == 'ACTIVE':
                audiencia['estado_badge'] = {'text': 'Activa', 'class': 'bg-green-100 text-green-800'}
            elif estado == 'PAUSED':
                audiencia['estado_badge'] = {'text': 'Pausada', 'class': 'bg-yellow-100 text-yellow-800'}
            elif estado == 'DELETED':
                audiencia['estado_badge'] = {'text': 'Eliminada', 'class': 'bg-red-100 text-red-800'}
            else:
                audiencia['estado_badge'] = {'text': 'Desconocido', 'class': 'bg-gray-100 text-gray-800'}
            
            return audiencia
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo detalle de audiencia: {e}")
        return None

def obtener_estadisticas_audiencias(nombre_nora, filtros=None):
    """
    Obtiene estadísticas resumidas de las audiencias
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        filtros (dict): Filtros aplicados
        
    Returns:
        dict: Estadísticas resumidas
    """
    try:
        audiencias = obtener_audiencias_con_filtros(nombre_nora, filtros)
        
        estadisticas = {
            'total_audiencias': len(audiencias),
            'audiencias_activas': len([a for a in audiencias if a.get('estado', '').upper() == 'ACTIVE']),
            'audiencias_pausadas': len([a for a in audiencias if a.get('estado', '').upper() == 'PAUSED']),
            'audiencias_eliminadas': len([a for a in audiencias if a.get('estado', '').upper() == 'DELETED']),
            'tamaño_total': sum(a.get('tamaño_aproximado', 0) or 0 for a in audiencias),
            'tipos_audiencia': {},
            'origenes': {},
            'promedio_tamaño': 0
        }
        
        # Calcular distribución por tipos
        for audiencia in audiencias:
            tipo = audiencia.get('tipo_audiencia', 'Sin tipo')
            estadisticas['tipos_audiencia'][tipo] = estadisticas['tipos_audiencia'].get(tipo, 0) + 1
            
            origen = audiencia.get('origen', 'Sin origen')
            estadisticas['origenes'][origen] = estadisticas['origenes'].get(origen, 0) + 1
        
        # Calcular promedio de tamaño
        if estadisticas['total_audiencias'] > 0:
            estadisticas['promedio_tamaño'] = estadisticas['tamaño_total'] / estadisticas['total_audiencias']
        
        return estadisticas
        
    except Exception as e:
        print(f"Error obteniendo estadísticas de audiencias: {e}")
        return {
            'total_audiencias': 0,
            'audiencias_activas': 0,
            'audiencias_pausadas': 0,
            'audiencias_eliminadas': 0,
            'tamaño_total': 0,
            'tipos_audiencia': {},
            'origenes': {},
            'promedio_tamaño': 0
        }

def sincronizar_audiencias_desde_meta(nombre_nora, ad_account_id=None):
    """
    Sincroniza audiencias desde la API de Meta Ads
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        ad_account_id (str, optional): ID de cuenta específica, None para todas
        
    Returns:
        dict: Resultado de la sincronización
    """
    try:
        import requests
        
        print(f"🔍 Iniciando sincronización de audiencias para {nombre_nora}")
        print(f"📋 Cuenta específica: {ad_account_id}")
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("❌ Token de acceso no encontrado")
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        print(f"✅ Token de acceso encontrado: {access_token[:20]}...")
        
        # Obtener cuentas a sincronizar
        if ad_account_id:
            cuentas = [{'id_cuenta_publicitaria': ad_account_id}]
            print(f"🎯 Usando cuenta específica: {ad_account_id}")
        else:
            print(f"🔍 Buscando cuentas para {nombre_nora}")
            resultado_cuentas = supabase.table("meta_ads_cuentas") \
                .select("id_cuenta_publicitaria") \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            cuentas = resultado_cuentas.data or []
            print(f"📊 Cuentas encontradas: {len(cuentas)}")
            for cuenta in cuentas:
                print(f"   - {cuenta['id_cuenta_publicitaria']}")
        
        audiencias_sincronizadas = 0
        errores = []
        
        for cuenta in cuentas:
            cuenta_id = cuenta['id_cuenta_publicitaria']
            print(f"\n🔄 Procesando cuenta: {cuenta_id}")
            
            try:
                # Consultar audiencias desde Meta API Graph
                url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/customaudiences"
                params = {
                    'access_token': access_token,
                    'fields': 'id,name,description,subtype,delivery_status,operation_status,data_source,time_created',  # Sin approximate_count
                    'limit': 1000
                }
                
                print(f"🌐 URL de API: {url}")
                print(f"📄 Parámetros: {params}")
                
                response = requests.get(url, params=params, timeout=30)
                print(f"📡 Respuesta HTTP: {response.status_code}")
                
                # Si no es exitoso, obtener detalles del error
                if response.status_code != 200:
                    print(f"❌ Error HTTP {response.status_code}")
                    print(f"📄 Respuesta completa: {response.text}")
                    
                    try:
                        error_data = response.json()
                        print(f"🔍 Error JSON: {error_data}")
                        
                        # Analizar el tipo de error específico
                        if 'error' in error_data:
                            error_info = error_data['error']
                            error_code = error_info.get('code', 'unknown')
                            error_message = error_info.get('message', 'Sin mensaje')
                            error_type = error_info.get('type', 'unknown')
                            
                            print(f"🚨 Código de error: {error_code}")
                            print(f"📝 Mensaje: {error_message}")
                            print(f"🏷️ Tipo: {error_type}")
                            
                            # Errores comunes y sus soluciones
                            if error_code == 190:
                                error_msg = f"Token inválido para cuenta {cuenta_id}: {error_message}"
                            elif error_code == 200:
                                error_msg = f"Permisos insuficientes para cuenta {cuenta_id}: {error_message}"
                            elif error_code == 100:
                                error_msg = f"Parámetro inválido para cuenta {cuenta_id}: {error_message}"
                            elif error_code == 803:
                                error_msg = f"Sin acceso a audiencias para cuenta {cuenta_id}: {error_message}"
                            else:
                                error_msg = f"Error {error_code} en cuenta {cuenta_id}: {error_message}"
                                
                            errores.append(error_msg)
                    except:
                        # Si no se puede parsear como JSON
                        errores.append(f"Error {response.status_code} en cuenta {cuenta_id}: {response.text[:200]}")
                    
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                print(f"📥 Datos recibidos: {data}")
                
                audiencias_meta = data.get('data', [])
                print(f"👥 Audiencias encontradas en Meta: {len(audiencias_meta)}")
                
                for i, audiencia_meta in enumerate(audiencias_meta):
                    print(f"\n  🔸 Procesando audiencia {i+1}/{len(audiencias_meta)}")
                    print(f"     ID: {audiencia_meta.get('id')}")
                    print(f"     Nombre: {audiencia_meta.get('name', 'Sin nombre')}")
                    
                    # Mapear datos de Meta a nuestro esquema
                    data_source = audiencia_meta.get('data_source', {})
                    delivery_status = audiencia_meta.get('delivery_status', {})
                    
                    # Extraer el código de estado si es un dict, sino usar el valor directamente
                    estado_final = 'UNKNOWN'
                    if isinstance(delivery_status, dict):
                        estado_final = str(delivery_status.get('code', 'UNKNOWN'))
                    elif delivery_status:
                        estado_final = str(delivery_status).upper()
                    
                    # Convertir timestamp Unix a formato ISO para PostgreSQL
                    from datetime import datetime
                    time_created = audiencia_meta.get('time_created')
                    created_at_iso = None
                    if time_created:
                        try:
                            created_at_iso = datetime.fromtimestamp(int(time_created)).isoformat()
                        except (ValueError, TypeError):
                            created_at_iso = None
                    
                    audiencia_data = {
                        'ad_account_id': cuenta_id,
                        'nombre_nora': nombre_nora,
                        'audience_id': audiencia_meta.get('id'),
                        'nombre_audiencia': audiencia_meta.get('name', 'Sin nombre'),
                        'tipo_audiencia': audiencia_meta.get('subtype', 'CUSTOM').lower(),
                        'tamaño_aproximado': None,  # No disponible en la API
                        'origen': data_source.get('type', 'unknown') if isinstance(data_source, dict) else 'unknown',
                        'creada_en': created_at_iso,
                        'estado': estado_final
                    }
                    
                    print(f"     📝 Datos mapeados: {audiencia_data}")
                    
                    # Insertar o actualizar en Supabase
                    try:
                        # Primero verificar si ya existe
                        resultado_existente = supabase.table('meta_ads_audiencias').select('id').eq('audience_id', audiencia_data['audience_id']).execute()
                        
                        if resultado_existente.data:
                            # Si existe, actualizar
                            resultado = supabase.table('meta_ads_audiencias').update(audiencia_data).eq('audience_id', audiencia_data['audience_id']).execute()
                            print(f"     ✅ Audiencia actualizada: {audiencia_data['audience_id']}")
                        else:
                            # Si no existe, insertar
                            resultado = supabase.table('meta_ads_audiencias').insert(audiencia_data).execute()
                            print(f"     ✅ Audiencia insertada: {audiencia_data['audience_id']}")
                        
                        audiencias_sincronizadas += 1
                    except Exception as e:
                        error_msg = f"Error guardando audiencia {audiencia_meta.get('id')}: {str(e)}"
                        print(f"     ❌ {error_msg}")
                        errores.append(error_msg)
                
            except Exception as e:
                error_msg = f"Error sincronizando cuenta {cuenta_id}: {str(e)}"
                print(f"❌ {error_msg}")
                errores.append(error_msg)
                continue
        
        resultado = {
            'ok': True,
            'audiencias_sincronizadas': audiencias_sincronizadas,
            'errores': errores,
            'total_errores': len(errores)
        }
        
        print(f"\n✅ Sincronización completada:")
        print(f"   📊 Audiencias sincronizadas: {audiencias_sincronizadas}")
        print(f"   ❌ Errores: {len(errores)}")
        if errores:
            for error in errores:
                print(f"      - {error}")
        
        # Si no se pudieron sincronizar audiencias personalizadas, intentar con audiencias guardadas
        if audiencias_sincronizadas == 0 and len(errores) > 0:
            print(f"\n🔄 Intentando sincronizar audiencias guardadas (saved_audiences)...")
            resultado_alternativo = sincronizar_saved_audiences_desde_meta(nombre_nora, ad_account_id)
            
            if resultado_alternativo['audiencias_sincronizadas'] > 0:
                print(f"✅ Se encontraron {resultado_alternativo['audiencias_sincronizadas']} audiencias guardadas")
                resultado['audiencias_sincronizadas'] = resultado_alternativo['audiencias_sincronizadas']
                resultado['errores'].extend(resultado_alternativo.get('errores', []))
        
        return resultado
        
    except Exception as e:
        error_msg = f'Error general: {str(e)}'
        print(f"💥 {error_msg}")
        return {'ok': False, 'error': error_msg}

def sincronizar_saved_audiences_desde_meta(nombre_nora, ad_account_id=None):
    """
    Sincroniza audiencias guardadas (saved audiences) desde la API de Meta Ads
    Como alternativa a las audiencias personalizadas
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        ad_account_id (str, optional): ID de cuenta específica, None para todas
        
    Returns:
        dict: Resultado de la sincronización
    """
    try:
        import requests
        
        print(f"🔍 Iniciando sincronización de audiencias guardadas para {nombre_nora}")
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # Obtener cuentas a sincronizar
        if ad_account_id:
            cuentas = [{'id_cuenta_publicitaria': ad_account_id}]
        else:
            resultado_cuentas = supabase.table("meta_ads_cuentas") \
                .select("id_cuenta_publicitaria") \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            cuentas = resultado_cuentas.data or []
        
        audiencias_sincronizadas = 0
        errores = []
        
        for cuenta in cuentas:
            cuenta_id = cuenta['id_cuenta_publicitaria']
            print(f"\n🔄 Procesando saved audiences para cuenta: {cuenta_id}")
            
            try:
                # Consultar audiencias guardadas desde Meta API Graph
                url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/saved_audiences"
                params = {
                    'access_token': access_token,
                    'fields': 'id,name,description,time_created',  # Quitamos approximate_count
                    'limit': 1000
                }
                
                response = requests.get(url, params=params, timeout=30)
                print(f"📡 Respuesta HTTP: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Error HTTP {response.status_code}: {response.text}")
                    errores.append(f"Error accediendo a saved audiences de cuenta {cuenta_id}: {response.status_code}")
                    continue
                
                data = response.json()
                audiencias_guardadas = data.get('data', [])
                print(f"💾 Audiencias guardadas encontradas: {len(audiencias_guardadas)}")
                
                for audiencia in audiencias_guardadas:
                    print(f"  📁 Procesando: {audiencia.get('name', 'Sin nombre')}")
                    
                    # Mapear datos de saved audience a nuestro esquema
                    # Convertir timestamp Unix a formato ISO para PostgreSQL
                    from datetime import datetime
                    time_created = audiencia.get('time_created')
                    created_at_iso = None
                    if time_created:
                        try:
                            # time_created puede venir como string en formato ISO o como timestamp
                            if 'T' in str(time_created):
                                created_at_iso = time_created  # Ya está en formato ISO
                            else:
                                created_at_iso = datetime.fromtimestamp(int(time_created)).isoformat()
                        except (ValueError, TypeError):
                            created_at_iso = None
                    
                    audiencia_data = {
                        'ad_account_id': cuenta_id,
                        'nombre_nora': nombre_nora,
                        'audience_id': f"saved_{audiencia.get('id')}",  # Prefijo para distinguir
                        'nombre_audiencia': audiencia.get('name', 'Sin nombre'),
                        'tipo_audiencia': 'saved',
                        'tamaño_aproximado': None,  # No disponible para saved audiences
                        'origen': 'saved_audience',
                        'creada_en': created_at_iso,
                        'estado': 'ACTIVE'  # Las saved audiences suelen estar activas
                    }
                    
                    try:
                        # Primero verificar si ya existe
                        resultado_existente = supabase.table('meta_ads_audiencias').select('id').eq('audience_id', audiencia_data['audience_id']).execute()
                        
                        if resultado_existente.data:
                            # Si existe, actualizar
                            resultado = supabase.table('meta_ads_audiencias').update(audiencia_data).eq('audience_id', audiencia_data['audience_id']).execute()
                            print(f"     ✅ Saved audience actualizada: {audiencia_data['audience_id']}")
                        else:
                            # Si no existe, insertar
                            resultado = supabase.table('meta_ads_audiencias').insert(audiencia_data).execute()
                            print(f"     ✅ Saved audience insertada: {audiencia_data['audience_id']}")
                            
                        audiencias_sincronizadas += 1
                    except Exception as e:
                        error_msg = f"Error insertando saved audience {audiencia.get('id')}: {str(e)}"
                        errores.append(error_msg)
                
            except Exception as e:
                error_msg = f"Error sincronizando saved audiences de cuenta {cuenta_id}: {str(e)}"
                errores.append(error_msg)
        
        return {
            'ok': True,
            'audiencias_sincronizadas': audiencias_sincronizadas,
            'errores': errores,
            'total_errores': len(errores)
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error general en saved audiences: {str(e)}'}

def crear_audiencia_personalizada(nombre_nora, ad_account_id, datos_audiencia):
    """
    Crea una audiencia personalizada vía Graph API de Meta
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        ad_account_id (str): ID de la cuenta publicitaria
        datos_audiencia (dict): Datos para crear la audiencia
        
    Returns:
        dict: Resultado de la creación
    """
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # URL para crear audiencia
        url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/customaudiences"
        
        # Parámetros para crear la audiencia
        params = {
            'access_token': access_token,
            'name': datos_audiencia.get('name', 'Audiencia sin nombre'),
            'subtype': datos_audiencia.get('subtype', 'CUSTOM'),
            'description': datos_audiencia.get('description', ''),
            'customer_file_source': 'USER_PROVIDED_ONLY'
        }
        
        # Para audiencias lookalike
        if datos_audiencia.get('subtype') == 'LOOKALIKE':
            params.update({
                'origin_audience_id': datos_audiencia.get('origin_audience_id'),
                'lookalike_spec': {
                    'country': datos_audiencia.get('country', 'MX'),
                    'ratio': datos_audiencia.get('ratio', 0.01)
                }
            })
        
        # Crear la audiencia
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        audience_id = result.get('id')
        
        if not audience_id:
            return {'ok': False, 'error': 'No se pudo obtener ID de audiencia creada'}
        
        # Guardar en nuestra base de datos
        audiencia_data = {
            'ad_account_id': ad_account_id,
            'nombre_nora': nombre_nora,
            'audience_id': audience_id,
            'nombre_audiencia': params['name'],
            'tipo_audiencia': params['subtype'].lower(),
            'tamaño_aproximado': 0,  # Inicialmente 0
            'origen': 'user_created',
            'creada_en': datetime.utcnow().isoformat(),
            'estado': 'ACTIVE'
        }
        
        supabase.table('meta_ads_audiencias').insert(audiencia_data).execute()
        
        return {
            'ok': True,
            'audience_id': audience_id,
            'message': f'Audiencia "{params["name"]}" creada exitosamente'
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error creando audiencia: {str(e)}'}

def agregar_usuarios_a_audiencia(audience_id, usuarios, tipo_schema='email'):
    """
    Agrega usuarios a una audiencia personalizada
    
    Args:
        audience_id (str): ID de la audiencia
        usuarios (list): Lista de usuarios (emails, teléfonos, etc.)
        tipo_schema (str): Tipo de dato ('email', 'phone', 'madid', etc.)
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        if not FACEBOOK_SDK_AVAILABLE:
            return {'ok': False, 'error': 'SDK de Facebook no está disponible'}
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # Inicializar la API
        FacebookAdsApi.init(access_token=access_token)
        
        # Crear objeto CustomAudience
        audiencia = CustomAudience(audience_id)
        
        # Hashear los datos si es necesario
        usuarios_hasheados = []
        for usuario in usuarios:
            if tipo_schema == 'email':
                # Hashear email en SHA256
                hash_obj = hashlib.sha256(usuario.lower().strip().encode())
                usuarios_hasheados.append(hash_obj.hexdigest())
            elif tipo_schema == 'phone':
                # Para teléfonos, normalizar y hashear
                telefono_limpio = ''.join(filter(str.isdigit, usuario))
                hash_obj = hashlib.sha256(telefono_limpio.encode())
                usuarios_hasheados.append(hash_obj.hexdigest())
            else:
                usuarios_hasheados.append(usuario)
        
        # Usar el schema correcto del SDK
        schema = ['EMAIL_SHA256'] if tipo_schema == 'email' else ['PHONE_SHA256']
        
        # Agregar usuarios a la audiencia
        audiencia.add_users(
            schema=schema,
            users=usuarios_hasheados
        )
        
        return {
            'ok': True,
            'usuarios_agregados': len(usuarios_hasheados),
            'message': f'Se agregaron {len(usuarios_hasheados)} usuarios a la audiencia'
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error agregando usuarios: {str(e)}'}

def eliminar_audiencia(audience_id, nombre_nora):
    """
    Elimina una audiencia personalizada
    
    Args:
        audience_id (str): ID de la audiencia
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        if not FACEBOOK_SDK_AVAILABLE:
            return {'ok': False, 'error': 'SDK de Facebook no está disponible'}
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # Inicializar la API
        FacebookAdsApi.init(access_token=access_token)
        
        # Eliminar de Meta
        audiencia = CustomAudience(audience_id)
        audiencia.api_delete()
        
        # Eliminar de nuestra base de datos
        supabase.table('meta_ads_audiencias') \
            .delete() \
            .eq('audience_id', audience_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        return {
            'ok': True,
            'message': 'Audiencia eliminada exitosamente'
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error eliminando audiencia: {str(e)}'}

def actualizar_audiencia(audience_id, nombre_nora, datos_actualizacion):
    """
    Actualiza los datos de una audiencia
    
    Args:
        audience_id (str): ID de la audiencia
        nombre_nora (str): Nombre de la instancia Nora
        datos_actualizacion (dict): Datos a actualizar
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        if not FACEBOOK_SDK_AVAILABLE:
            return {'ok': False, 'error': 'SDK de Facebook no está disponible'}
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # Inicializar la API
        FacebookAdsApi.init(access_token=access_token)
        
        # Actualizar en Meta
        audiencia = CustomAudience(audience_id)
        params_meta = {}
        
        if 'name' in datos_actualizacion:
            params_meta['name'] = datos_actualizacion['name']
        if 'description' in datos_actualizacion:
            params_meta['description'] = datos_actualizacion['description']
        
        if params_meta:
            audiencia.api_update(params=params_meta)
        
        # Actualizar en nuestra base de datos
        update_data = {}
        if 'name' in datos_actualizacion:
            update_data['nombre_audiencia'] = datos_actualizacion['name']
        
        if update_data:
            supabase.table('meta_ads_audiencias') \
                .update(update_data) \
                .eq('audience_id', audience_id) \
                .eq('nombre_nora', nombre_nora) \
                .execute()
        
        return {
            'ok': True,
            'message': 'Audiencia actualizada exitosamente'
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error actualizando audiencia: {str(e)}'}

def crear_audiencia_lookalike(nombre_nora, ad_account_id, origen_audience_id, nombre, pais='MX', ratio=0.01):
    """
    Crea una audiencia lookalike basada en una audiencia existente
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        ad_account_id (str): ID de la cuenta publicitaria
        origen_audience_id (str): ID de la audiencia origen
        nombre (str): Nombre para la nueva audiencia
        pais (str): Código del país (ej: 'MX', 'US')
        ratio (float): Ratio de similitud (0.01 = 1%, 0.10 = 10%)
        
    Returns:
        dict: Resultado de la operación
    """
    datos_audiencia = {
        'name': nombre,
        'subtype': 'LOOKALIKE',
        'origin_audience_id': origen_audience_id,
        'country': pais,
        'ratio': ratio
    }
    
    return crear_audiencia_personalizada(nombre_nora, ad_account_id, datos_audiencia)
