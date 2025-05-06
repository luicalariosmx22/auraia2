# Archivo: clientes/aura/tasks/meta_ads_reporter.py

"""
✅ TAREA PROGRAMADA: Reporte Semanal Meta Ads
Consulta semanalmente los datos y envía reporte automático por WhatsApp.
"""

import requests
from flask import current_app
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_utils import get_supabase_client
from clientes.aura.utils.whatsapp_utils import enviar_mensaje_whatsapp  # ⚠️ Usa la función que tengas para enviar WhatsApp

ACCESS_TOKEN_GLOBAL = 'TU_ACCESS_TOKEN_GLOBAL'  # ⚠️ Cargar desde la DB más adelante

def generar_reporte_mensaje(cuenta, resumen, mejor_anuncio):
    semana_actual = datetime.now()
    semana_inicio = (semana_actual - timedelta(days=7)).strftime('%d de %B')
    semana_fin = semana_actual.strftime('%d de %B de %Y')

    mensaje = (
        f"📊 REPORTE SEMANAL DE CAMPAÑA 📊\n"
        f"📅 Semana del {semana_inicio} al {semana_fin}\n\n"
        f"👤 Cliente: {cuenta['nombre_cliente']}\n"
        f"📢 Anuncios Activos: {resumen['anuncios_activos']}\n\n"
        f"📌 Resultados Clave:\n"
        f"💬 Conversaciones iniciadas: {resumen['conversaciones']}\n"
        f"👀 Alcance total: {resumen['alcance']} personas\n"
        f"📢 Impresiones: {resumen['impresiones']}\n"
        f"💰 Costo por conversación: ${resumen['costo_por_conversacion']} MXN\n"
        f"💳 Gasto total: ${resumen['gasto_total']} MXN\n\n"
        f"🏆Mejor Anuncio:\n"
        f"📝 \"{mejor_anuncio}\"\n"
        f"(Mayor número de resultados esta semana)"
    )
    return mensaje

def consultar_metricas(cuenta_id_meta):
    url = f"https://graph.facebook.com/v19.0/{cuenta_id_meta}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status,insights{impressions,clicks,reach,spend,objective,conversations}',
        'access_token': ACCESS_TOKEN_GLOBAL
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        campañas = response.json().get('data', [])
        return campañas
    except Exception as e:
        current_app.logger.error(f"[Meta Ads Reporter] Error al obtener métricas: {str(e)}")
        return []

def enviar_reporte_semanal():
    supabase = get_supabase_client()
    cuentas = supabase.table('meta_ads_cuentas').select('*').eq('conectada', True).execute()

    if not cuentas.data:
        current_app.logger.info("[Meta Ads Reporter] No hay cuentas conectadas.")
        return

    for cuenta in cuentas.data:
        campañas = consultar_metricas(cuenta['id_cuenta_publicitaria'])

        if not campañas:
            current_app.logger.info(f"[Meta Ads Reporter] No se encontraron campañas para {cuenta['nombre_cliente']}")
            continue

        total_conversaciones = 0
        total_alcance = 0
        total_impresiones = 0
        total_gasto = 0
        mejor_anuncio = None
        max_resultados = 0

        for c in campañas:
            insights = c.get('insights', {})
            conversaciones = int(insights.get('conversations', 0)) if insights else 0
            alcance = int(insights.get('reach', 0)) if insights else 0
            impresiones = int(insights.get('impressions', 0)) if insights else 0
            gasto = float(insights.get('spend', 0)) if insights else 0

            total_conversaciones += conversaciones
            total_alcance += alcance
            total_impresiones += impresiones
            total_gasto += gasto

            if conversaciones > max_resultados:
                max_resultados = conversaciones
                mejor_anuncio = c['name']

        costo_por_conversacion = round(total_gasto / total_conversaciones, 2) if total_conversaciones > 0 else 0

        resumen = {
            'anuncios_activos': len(campañas),
            'conversaciones': total_conversaciones,
            'alcance': total_alcance,
            'impresiones': total_impresiones,
            'costo_por_conversacion': costo_por_conversacion,
            'gasto_total': round(total_gasto, 2)
        }

        mensaje = generar_reporte_mensaje(cuenta, resumen, mejor_anuncio if mejor_anuncio else "No disponible")

        receptores = supabase.table('meta_ads_receptores').select('*').eq('cuenta_id', cuenta['id']).eq('activo', True).execute()
        numeros = [r['numero_telefono'] for r in receptores.data] if receptores.data else []

        for numero in numeros:
            enviar_mensaje_whatsapp(numero, mensaje)

        supabase.table('meta_ads_reportes').insert({
            'cuenta_id': cuenta['id'],
            'mensaje': mensaje,
            'numeros_destino': numeros,
            'estado_envio': 'Exitoso'
        }).execute()

        current_app.logger.info(f"[Meta Ads Reporter] Reporte enviado para {cuenta['nombre_cliente']}")
