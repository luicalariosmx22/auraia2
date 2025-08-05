# Archivo: clientes/aura/tasks/meta_ads_sync_all.py
from clientes.aura.utils.supabase_client import supabase
import os
import requests
import json
from datetime import datetime, date, timedelta


def sincronizar_todas_las_cuentas_meta_ads(nombre_nora=None, fecha_inicio=None, fecha_fin=None):
    hoy = date.today()
    print(f"🗓️ Fecha actual del sistema: {hoy}")

    if not fecha_fin:
        fecha_fin = hoy - timedelta(days=1)
    elif isinstance(fecha_fin, str):
        fecha_fin = date.fromisoformat(fecha_fin)

    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=7)
    elif isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)

    access_token = os.getenv('META_ACCESS_TOKEN')
    if not access_token:
        return {'ok': False, 'error': 'No se encontró el token META_ACCESS_TOKEN'}

    query = supabase.table('meta_ads_cuentas') \
        .select('id_cuenta_publicitaria, nombre_cliente, nombre_nora') \
        .is_('estado_actual', 'null')
    if nombre_nora:
        query = query.eq('nombre_nora', nombre_nora)

    cuentas = query.execute()
    if not cuentas.data:
        return {'ok': False, 'error': 'No se encontraron cuentas activas'}

    resultados = {
        'ok': True,
        'cuentas_procesadas': 0,
        'cuentas_exitosas': 0,
        'errores': [],
        'cuentas_con_errores': [],
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_fin': fecha_fin.isoformat()
    }

    for cuenta in cuentas.data:
        cuenta_id = cuenta['id_cuenta_publicitaria']
        nombre_cliente = cuenta.get('nombre_cliente', 'Cliente desconocido')
        nombre_nora = cuenta.get('nombre_nora', 'Sin Nora')
        
        try:
            print(f"🔄 Procesando: {nombre_cliente} ({cuenta_id})")
            exito = sincronizar_cuenta_meta_ads_simple(
                ad_account_id=cuenta_id,
                access_token=access_token,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            if exito:
                resultados['cuentas_exitosas'] += 1
                print(f"✅ Exitosa: {nombre_cliente}")
            else:
                error_info = {
                    'cuenta_id': cuenta_id,
                    'nombre_cliente': nombre_cliente,
                    'nombre_nora': nombre_nora,
                    'error': 'Falló la sincronización sin excepción'
                }
                resultados['errores'].append(f"Falló cuenta {cuenta_id} ({nombre_cliente})")
                resultados['cuentas_con_errores'].append(error_info)
                print(f"❌ Falló: {nombre_cliente}")
        except Exception as e:
            error_info = {
                'cuenta_id': cuenta_id,
                'nombre_cliente': nombre_cliente,
                'nombre_nora': nombre_nora,
                'error': str(e)
            }
            resultados['errores'].append(f"Error en cuenta {cuenta_id} ({nombre_cliente}): {str(e)}")
            resultados['cuentas_con_errores'].append(error_info)
            print(f"💥 Error en {nombre_cliente}: {str(e)}")

        resultados['cuentas_procesadas'] += 1

    # Generar resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE SINCRONIZACIÓN META ADS")
    print("="*80)
    print(f"🗓️ Período: {fecha_inicio} → {fecha_fin}")
    print(f"📈 Cuentas procesadas: {resultados['cuentas_procesadas']}")
    print(f"✅ Cuentas exitosas: {resultados['cuentas_exitosas']}")
    print(f"❌ Cuentas con errores: {len(resultados['cuentas_con_errores'])}")
    
    if resultados['cuentas_con_errores']:
        print("\n🚨 DETALLE DE ERRORES:")
        print("-" * 50)
        for i, error_info in enumerate(resultados['cuentas_con_errores'], 1):
            print(f"{i}. {error_info['nombre_cliente']} ({error_info['cuenta_id']})")
            print(f"   Nora: {error_info['nombre_nora']}")
            print(f"   Error: {error_info['error']}")
            print()
    else:
        print("\n🎉 ¡Todas las cuentas se sincronizaron correctamente!")
    
    print("="*80)

    return resultados


def sincronizar_cuenta_meta_ads_simple(ad_account_id, access_token, fecha_inicio, fecha_fin):
    print(f"🔄 Sincronizando cuenta: {ad_account_id}")
    
    # Construir URL para insights de anuncios
    url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/insights"
    
    # Parámetros para la consulta
    params = {
        'access_token': access_token,
        'level': 'ad',
        'fields': 'ad_id,ad_name,spend,impressions,clicks,reach,frequency,cpc,cpm,ctr,actions,cost_per_action_type',
        'action_attribution_windows': ['1d_view', '7d_click'],
        'breakdowns': 'publisher_platform',
        'time_range': json.dumps({
            'since': fecha_inicio.strftime('%Y-%m-%d'),
            'until': fecha_fin.strftime('%Y-%m-%d')
        }),
        'limit': 500
    }

    print(f"📊 Obteniendo insights entre {fecha_inicio.strftime('%Y-%m-%d')} y {fecha_fin.strftime('%Y-%m-%d')}")
    
    try:
        # Realizar consulta a la API
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        insights = data.get('data', [])
        
        print(f"📊 Se obtuvieron {len(insights)} insights de la API")
        
        if not insights:
            print(f"⚠️ No se encontraron insights para la cuenta {ad_account_id}")
            # Intentar sin breakdown
            params_simple = params.copy()
            del params_simple['breakdowns']
            print("🔄 Intentando sin breakdown de plataforma...")
            
            response_simple = requests.get(url, params=params_simple, timeout=30)
            response_simple.raise_for_status()
            data_simple = response_simple.json()
            insights = data_simple.get('data', [])
            print(f"📊 Sin breakdown: {len(insights)} insights")
            
        # Debug adicional: mostrar estructura de un insight
        if insights and len(insights) > 0:
            print(f"🔍 Ejemplo de insight para debug:")
            sample_insight = insights[0]
            print(f"   Campos disponibles: {list(sample_insight.keys())}")
            if 'actions' in sample_insight:
                print(f"   Tipos de acciones: {[action.get('action_type') for action in sample_insight.get('actions', [])]}")
            
        fecha_sync = datetime.utcnow().isoformat()
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error obteniendo insights para cuenta {ad_account_id}: {error_msg}")
        
        # Diagnóstico específico del error
        if "Invalid OAuth access token" in error_msg:
            print("🔑 Problema de autenticación - token inválido o expirado")
        elif "Unsupported get request" in error_msg:
            print("🚫 Cuenta publicitaria no existe o sin permisos")
        elif "timeout" in error_msg.lower():
            print("⏱️ Timeout en la consulta - API de Meta sobrecargada")
        elif "rate limit" in error_msg.lower():
            print("🚦 Límite de tasa excedido - demasiadas consultas")
        
        return False

    # Actualizar registros existentes como inactivos
    supabase.table('meta_ads_anuncios_detalle') \
        .update({'activo': False, 'fecha_ultima_actualizacion': fecha_sync}) \
        .eq('id_cuenta_publicitaria', ad_account_id).execute()

    anuncios_procesados = 0
    anuncios_con_mensajes = 0
    for insight in insights:
        ad_id = insight.get('ad_id')
        if not ad_id:
            continue

        ad_info = obtener_info_anuncio(ad_id, access_token)
        platform = insight.get('publisher_platform', 'facebook')

        data = {
            'ad_id': ad_id,
            'nombre_anuncio': insight.get('ad_name') or ad_info.get('name'),
            'id_cuenta_publicitaria': ad_account_id,
            'publisher_platform': platform,
            'importe_gastado': float(insight.get('spend', 0)),
            'impresiones': int(insight.get('impressions', 0)),
            'clicks': int(insight.get('clicks', 0)),
            'alcance': int(insight.get('reach', 0)),
            'frequency': float(insight.get('frequency', 0)),
            'ctr': float(insight.get('ctr', 0)),
            'cpc': float(insight.get('cpc', 0)),
            'cost_per_1k_impressions': float(insight.get('cpm', 0)),
            'campana_id': ad_info.get('campaign_id'),
            'nombre_campana': ad_info.get('campaign_name'),
            'conjunto_id': ad_info.get('adset_id'),
            'nombre_conjunto': ad_info.get('adset_name'),
            'status': ad_info.get('status'),
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'fecha_sincronizacion': fecha_sync,
            'fecha_ultima_actualizacion': fecha_sync,
            'activo': True
        }

        # Extraer acciones
        actions = insight.get('actions', [])
        
        # Debug: Mostrar todas las acciones disponibles
        if actions:
            print(f"📋 Acciones disponibles para anuncio {ad_id}: {[action.get('action_type') for action in actions]}")
        
        for action in actions:
            tipo = action.get('action_type')
            valor = int(float(action.get('value', 0)))
            
            if tipo == 'link_click':
                data['link_clicks'] = valor
            elif tipo == 'post_engagement':
                data['interacciones'] = valor
            elif tipo == 'video_view':
                data['video_views'] = valor
            elif tipo in [
                'messaging_conversation_started_7d', 
                'messaging_first_reply', 
                'messaging_conversation_started',
                'onsite_conversion.messaging_conversation_started_7d',
                'onsite_conversion.messaging_first_reply',
                'onsite_conversion.total_messaging_connection'
            ]:
                data['messaging_conversations_started'] = valor
                anuncios_con_mensajes += 1
                print(f"💬 Encontrado {tipo}: {valor} mensajes para anuncio {ad_id}")
            elif tipo == 'page_engagement':
                # Sumar page_engagement a interacciones totales
                data['interacciones'] = data.get('interacciones', 0) + valor
            elif tipo == 'post_reaction':
                # Las reacciones también son interacciones
                data['interacciones'] = data.get('interacciones', 0) + valor

        supabase.table('meta_ads_anuncios_detalle').upsert(
            data,
            on_conflict='ad_id,fecha_inicio,fecha_fin,publisher_platform'
        ).execute()
        
        anuncios_procesados += 1

    print(f"✅ Sincronización COMPLETA: {anuncios_procesados} anuncios procesados")
    if anuncios_con_mensajes > 0:
        print(f"💬 Anuncios con mensajes: {anuncios_con_mensajes}")
    else:
        print("💬 Ningún anuncio generó conversaciones por mensajería en este período")
    return True


def obtener_info_anuncio(ad_id, access_token):
    """
    Obtiene información adicional del anuncio usando Graph API
    """
    try:
        url = f"https://graph.facebook.com/v19.0/{ad_id}"
        params = {
            'access_token': access_token,
            'fields': 'name,status,campaign{id,name},adset{id,name}'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        info = response.json()
        
        return {
            'name': info.get('name'),
            'status': info.get('status'),
            'campaign_id': info.get('campaign', {}).get('id'),
            'campaign_name': info.get('campaign', {}).get('name'),
            'adset_id': info.get('adset', {}).get('id'),
            'adset_name': info.get('adset', {}).get('name')
        }
    except Exception as e:
        print(f"⚠️ Error obteniendo info del anuncio {ad_id}: {str(e)}")
        return {}
