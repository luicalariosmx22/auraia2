# ✅ Archivo: clientes/aura/routes/panel_cliente_meta_ads/vista_sincronizacion.py
# 👉 Ruta manual para sincronizar gasto semanal de anuncios desde Meta Ads

from flask import Blueprint, request, render_template
from clientes.aura.routes.sincronizar_meta_ads import sincronizar_gasto_anuncios
import sys
import os  # ← Importar os normalmente
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../tasks')))
from clientes.aura.tasks import meta_ads_sync_all
from clientes.aura.utils.supabase_client import supabase

panel_cliente_meta_ads_sincronizacion_bp = Blueprint("panel_cliente_meta_ads_sincronizacion", __name__)

@panel_cliente_meta_ads_sincronizacion_bp.route('/panel_cliente/<nombre_nora>/meta_ads/sincronizar-gasto-manual')
def sincronizar_gasto_manual(nombre_nora):
    empresa_id = request.args.get('id_empresa')
    access_token = os.getenv("META_ACCESS_TOKEN")
    ad_account_id = os.getenv("META_AD_ACCOUNT_ID")

    if not empresa_id or not access_token or not ad_account_id:
        return "❌ Faltan parámetros o variables de entorno", 400

    sincronizar_gasto_anuncios(empresa_id, ad_account_id, access_token)
    return "✅ Sincronización de gasto completada"

@panel_cliente_meta_ads_sincronizacion_bp.route('/sincronizar-gasto-manual', methods=["GET"])
def sincronizar_gasto_manual_short():
    ad_account_id = request.args.get('id_empresa')
    accion = request.args.get('accion')
    mensaje = None
    exito = False
    anuncios = []
    cuentas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,nombre_cliente').eq('account_status', 1).execute().data or []
    # Paginación
    page = int(request.args.get('page', 1))
    per_page = 20
    total_anuncios = 0
    # Calcular fecha_inicio y fecha_fin (últimos 7 días)
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=6)
    # No formatear aquí, pasar como date
    if ad_account_id:
        # --- NUEVO: Lista de todos los campos avanzados a mostrar ---
        advanced_fields = [
            'frequency', 'ctr', 'cpc', 'cost_per_unique_click', 'unique_clicks',
            'quality_ranking', 'engagement_rate_ranking', 'conversion_rate_ranking',
            'video_plays_at_25', 'video_plays_at_50', 'video_plays_at_75', 'video_plays_at_100',
            'video_play_actions', 'video_avg_time_watched_actions',
            'post_engagement', 'post_reactions', 'post_comments', 'post_shares',
            'cost_per_messaging_conversation_started',
            'cost_per_inline_link_click', 'cost_per_unique_inline_link_click',
            'unique_inline_link_clicks', 'unique_ctr', 'unique_impressions',
            'unique_link_clicks', 'cost_per_unique_link_click', 'cost_per_click',
            'cost_per_1k_impressions', 'cost_per_10_sec_video_view',
            'cost_per_2_sec_continuous_video_view', 'cost_per_action_type',
            'cost_per_estimated_ad_recallers', 'cost_per_outbound_click',
            'cost_per_thruplay', 'cost_per_unique_outbound_click',
            'estimated_ad_recallers', 'estimated_ad_recall_rate',
            'outbound_clicks', 'outbound_clicks_ctr', 'thruplay_rate',
            'thruplays', 'unique_outbound_clicks', 'website_ctr',
            'website_purchase_roas', 'purchase_roas'
        ]
        # --- Seleccionar todos los campos básicos y avanzados ---
        select_fields = [
            'ad_id', 'nombre_anuncio', 'importe_gastado', 'conjunto_id', 'campana_id',
            'alcance', 'impresiones', 'interacciones', 'clicks', 'link_clicks', 'inline_link_clicks', 'mensajes',
            *advanced_fields
        ]
        anuncios_query = supabase.table('meta_ads_anuncios_detalle').select(','.join(select_fields)).eq('id_cuenta_publicitaria', ad_account_id)
        total_anuncios = len(anuncios_query.execute().data or [])
        anuncios = anuncios_query.range((page-1)*per_page, page*per_page-1).execute().data or []
        todos_los_anuncios = anuncios_query.execute().data or []
        # Calcular totales para todos los campos
        def sum_field(field):
            return sum(a.get(field, 0) or 0 for a in todos_los_anuncios)
        gasto_total = sum_field('importe_gastado')
        alcance_total = sum_field('alcance')
        impresiones_total = sum_field('impresiones')
        interacciones_total = sum_field('interacciones')
        mensajes_total = sum_field('mensajes')
        clicks_total = sum_field('clicks')
        link_clicks_total = sum_field('link_clicks')
        inline_link_clicks_total = sum_field('inline_link_clicks')
        # Totales avanzados
        advanced_totals = { field: sum_field(field) for field in advanced_fields }
        # Obtener todos los conjuntos y campañas de la cuenta
        conjuntos = supabase.table('meta_ads_conjuntos_anuncios').select('conjunto_id,nombre_conjunto').eq('id_cuenta_publicitaria', ad_account_id).execute().data or []
        campañas = supabase.table('meta_ads_campañas').select('campana_id,nombre_campana').eq('id_cuenta_publicitaria', ad_account_id).execute().data or []
        conjunto_map = {c['conjunto_id']: c['nombre_conjunto'] for c in conjuntos}
        campana_map = {c['campana_id']: c['nombre_campana'] for c in campañas}
        for a in anuncios:
            a['nombre_conjunto'] = conjunto_map.get(a.get('conjunto_id'), '(sin conjunto)')
            a['nombre_campana'] = campana_map.get(a.get('campana_id'), '(sin campaña)')
            # Evitar None en los campos de ordenamiento
            if a.get('nombre_campana') is None:
                a['nombre_campana'] = 'Sin campaña'
            if a.get('nombre_conjunto') is None:
                a['nombre_conjunto'] = 'Sin conjunto'
            if a.get('nombre_anuncio') is None:
                a['nombre_anuncio'] = 'Sin nombre'
    else:
        gasto_total = 0
        alcance_total = 0
        impresiones_total = 0
        interacciones_total = 0
        mensajes_total = 0
        clicks_total = 0
        link_clicks_total = 0
        inline_link_clicks_total = 0
        # Inicializar advanced_totals aunque no haya anuncios ni advanced_fields
        if 'advanced_fields' not in locals():
            advanced_fields = []
        advanced_totals = {field: 0 for field in advanced_fields}
    if request.args and accion == 'sincronizar':
        access_token = os.getenv("META_ACCESS_TOKEN")
        if not ad_account_id or not access_token:
            mensaje = "❌ Faltan parámetros o variables de entorno"
        else:
            try:
                # Sincroniza campañas, conjuntos y anuncios (todo)
                meta_ads_sync_all.sincronizar_todo_meta_ads(ad_account_id, access_token)
                mensaje = "✅ Sincronización completa de campañas, conjuntos y anuncios"
                exito = True
                anuncios_query = supabase.table('meta_ads_anuncios_detalle').select('ad_id,nombre_anuncio,importe_gastado,conjunto_id,campana_id,alcance,impresiones,interacciones,clicks,link_clicks,inline_link_clicks,mensajes').eq('id_cuenta_publicitaria', ad_account_id)
                total_anuncios = len(anuncios_query.execute().data or [])
                anuncios = anuncios_query.range((page-1)*per_page, page*per_page-1).execute().data or []
                conjuntos = supabase.table('meta_ads_conjuntos_anuncios').select('conjunto_id,nombre_conjunto').eq('id_cuenta_publicitaria', ad_account_id).execute().data or []
                campañas = supabase.table('meta_ads_campañas').select('campana_id,nombre_campana').eq('id_cuenta_publicitaria', ad_account_id).execute().data or []
                conjunto_map = {c['conjunto_id']: c['nombre_conjunto'] for c in conjuntos}
                campana_map = {c['campana_id']: c['nombre_campana'] for c in campañas}
                for a in anuncios:
                    a['nombre_conjunto'] = conjunto_map.get(a.get('conjunto_id'), '(sin conjunto)')
                    a['nombre_campana'] = campana_map.get(a.get('campana_id'), '(sin campaña)')
                    # Evitar None en los campos de ordenamiento
                    if a.get('nombre_campana') is None:
                        a['nombre_campana'] = 'Sin campaña'
                    if a.get('nombre_conjunto') is None:
                        a['nombre_conjunto'] = 'Sin conjunto'
                    if a.get('nombre_anuncio') is None:
                        a['nombre_anuncio'] = 'Sin nombre'
            except Exception as e:
                mensaje = f"❌ Error: {str(e)}"
    total_pages = max(1, (total_anuncios + per_page - 1) // per_page)
    # --- NUEVO: Listado de errores de campos faltantes de Meta ---
    meta_field_errors = []
    # Buscar si hay errores guardados en la sesión o en la tabla (opcional: aquí solo ejemplo de variable global)
    # Si usas una variable global o log temporal, puedes pasarla aquí. Si quieres persistir, deberías guardar en una tabla.
    # Por ahora, intentaremos leer de un archivo temporal si existe (puedes adaptar a tu sistema de logging real)
    error_log_path = os.path.join(os.path.dirname(__file__), '../../meta_ads_field_errors.log')
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8') as f:
            meta_field_errors = [line.strip() for line in f if line.strip()]
    # Inicializar advanced_totals aunque no haya anuncios ni advanced_fields
    if 'advanced_fields' not in locals():
        advanced_fields = []
    if 'advanced_totals' not in locals() or not isinstance(advanced_totals, dict):
        advanced_totals = {field: 0 for field in advanced_fields}
    # Procesar video_play_actions para métricas de video_plays_at_25, _50, _75, _100
    for a in anuncios:
        vpa = a.get('video_play_actions')
        if isinstance(vpa, list):
            for item in vpa:
                if not isinstance(item, dict):
                    continue
                action_type = item.get('action_type')
                value = item.get('value', 0)
                if action_type == 'video_view' and item.get('video_view_type') == '25':
                    a['video_plays_at_25'] = value
                elif action_type == 'video_view' and item.get('video_view_type') == '50':
                    a['video_plays_at_50'] = value
                elif action_type == 'video_view' and item.get('video_view_type') == '75':
                    a['video_plays_at_75'] = value
                elif action_type == 'video_view' and item.get('video_view_type') == '100':
                    a['video_plays_at_100'] = value
        for k in ['video_plays_at_25', 'video_plays_at_50', 'video_plays_at_75', 'video_plays_at_100']:
            if k not in a:
                a[k] = 0
    advanced_totals['video_plays_at_25'] = sum(a.get('video_plays_at_25', 0) or 0 for a in anuncios)
    advanced_totals['video_plays_at_50'] = sum(a.get('video_plays_at_50', 0) or 0 for a in anuncios)
    advanced_totals['video_plays_at_75'] = sum(a.get('video_plays_at_75', 0) or 0 for a in anuncios)
    advanced_totals['video_plays_at_100'] = sum(a.get('video_plays_at_100', 0) or 0 for a in anuncios)
    return render_template(
        "reportes_meta_ads/sincronizar_gasto_manual.html",
        mensaje=mensaje,
        exito=exito,
        cuentas=cuentas,
        anuncios=anuncios,
        page=page,
        total_pages=total_pages,
        fecha_inicio=fecha_inicio,  # Pasar como date
        fecha_fin=fecha_fin,        # Pasar como date
        gasto_total=gasto_total,    # Total del gasto
        alcance_total=alcance_total,
        impresiones_total=impresiones_total,
        interacciones_total=interacciones_total,
        mensajes_total=mensajes_total,
        clicks_total=clicks_total,
        link_clicks_total=link_clicks_total,
        inline_link_clicks_total=inline_link_clicks_total,
        advanced_fields=advanced_fields,
        advanced_totals=advanced_totals,
        meta_field_errors=meta_field_errors
    )
