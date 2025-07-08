# Archivo: clientes/aura/tasks/meta_ads_reporter.py

"""
✅ TAREA PROGRAMADA: Reporte Semanal Meta Ads
Consulta semanalmente los datos y envía reporte automático por WhatsApp.
"""

import requests
from flask import current_app
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.whatsapp_utils import enviar_mensaje_whatsapp  # ⚠️ Usa la función que tengas para enviar WhatsApp
import os

ACCESS_TOKEN_GLOBAL = os.getenv("META_ACCESS_TOKEN")  # ✅ Load from environment

print("🚀 [Meta Ads Reporter] Módulo cargado correctamente.")

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
    print(f"🌐 Consultando métricas para: {cuenta_id_meta}")
    url = f"https://graph.facebook.com/v19.0/{cuenta_id_meta}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status,insights{impressions,clicks,reach,spend,objective,conversations}',
        'access_token': ACCESS_TOKEN_GLOBAL
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        campañas = response.json().get('data', [])
        print(f"✅ Campañas encontradas: {len(campañas)}")
        return campañas
    except Exception as e:
        current_app.logger.error(f"[Meta Ads Reporter] Error al obtener métricas: {str(e)}")
        return []

def enviar_reporte_meta_ads():
    print("📤 [Meta Ads Reporter] Ejecutando enviar_reporte_meta_ads...")
    cuentas = supabase.table('meta_ads_cuentas').select('*').eq('conectada', True).execute()
    print(f"🔍 Cuentas conectadas: {len(cuentas.data) if cuentas.data else 0}")

    if not cuentas.data:
        current_app.logger.info("[Meta Ads Reporter] No hay cuentas conectadas.")
        return

    for cuenta in cuentas.data:
        print(f"➡️ Procesando cuenta: {cuenta['nombre_cliente']}")
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
            print(f"📲 Enviando WhatsApp a: {numero}")
            enviar_mensaje_whatsapp(numero, mensaje)

        # El guardado de reportes automáticos SÍ debe seguir insertando en meta_ads_reportes
        # No modificar aquí, solo asegurarse que la carga manual no use esta lógica
        supabase.table('meta_ads_reportes').insert({
            'cuenta_id': cuenta['id'],
            'mensaje': mensaje,
            'numeros_destino': numeros,
            'estado_envio': 'Exitoso'
        }).execute()

        current_app.logger.info(f"[Meta Ads Reporter] Reporte enviado para {cuenta['nombre_cliente']}")
