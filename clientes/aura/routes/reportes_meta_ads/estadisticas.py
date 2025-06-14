# Archivo: clientes/aura/routes/reportes_meta_ads/estadisticas.py
from flask import Blueprint, render_template, request, jsonify, abort
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase
import os
import requests
import json
import threading

estadisticas_ads_bp = Blueprint('estadisticas_ads_bp', __name__)

# NUEVA RUTA CORRECTA PARA ESTADÍSTICAS DE META ADS
@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas', methods=['GET', 'POST'])
def vista_estadisticas_ads(nombre_nora):
    if request.method == 'POST':
        fecha_fin = datetime.utcnow().date()
        fecha_inicio = fecha_fin - timedelta(days=6)
        total = generar_reporte_semanal(fecha_inicio, fecha_fin)
        return jsonify({'ok': True, 'insertados': total})
    return render_template('reportes_meta_ads/estadisticas_ads.html', nombre_nora=nombre_nora)

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/data', methods=['GET'])
def obtener_estadisticas_data(nombre_nora):
    """
    Devuelve los reportes semanales agregados para mostrar en el frontend.
    """
    reportes = supabase.table('meta_ads_reportes_semanales').select('*').order('fecha_fin', desc=True).limit(52).execute().data or []
    return jsonify({'ok': True, 'reportes': reportes})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/sync', methods=['POST'])
def sync_anuncios_meta_ads(nombre_nora):
    """
    Endpoint para sincronizar anuncios de Meta Ads y alimentar meta_ads_anuncios_detalle (por Nora).
    """
    from datetime import datetime, timedelta
    fecha_fin = datetime.utcnow().date()
    fecha_inicio = fecha_fin - timedelta(days=6)
    try:
        resultado = sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin)
        if resultado is None:
            return jsonify({'ok': False, 'error': 'Error en sincronización, resultado vacío o None.'}), 500
        return jsonify({'ok': True, 'procesados': resultado.get("procesados", 0), 'sin_anuncios': resultado.get("sin_anuncios", [])})
    except Exception as e:
        print(f"[ERROR] Error en sincronización: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/sync_manual', methods=['GET', 'POST'])
def sync_anuncios_meta_ads_manual(nombre_nora):
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        # Puedes agregar más variables aquí
        resultado = sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin)
        return jsonify({'ok': True, 'procesados': resultado.get("procesados", 0), 'sin_anuncios': resultado.get("sin_anuncios", [])})
    return render_template('reportes_meta_ads/sync_manual.html', nombre_nora=nombre_nora)

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/eliminar_reportes', methods=['POST'])
def eliminar_reportes(nombre_nora):
    """
    Elimina todos los registros de meta_ads_reportes_semanales de forma segura.
    """
    try:
        res = supabase.table('meta_ads_reportes_semanales').delete() \
            .neq('id', '00000000-0000-0000-0000-000000000000').execute()
        # Manejo robusto del conteo de eliminados
        if hasattr(res, 'count') and res.count is not None:
            eliminados = res.count
        elif hasattr(res, 'data') and res.data is not None:
            eliminados = len(res.data)
        else:
            eliminados = 0
        return jsonify({'ok': True, 'eliminados': eliminados})
    except Exception as e:
        print(f"[ERROR] Error al eliminar reportes: {e}")
        return jsonify({'ok': False, 'error': str(e)})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/eliminar_anuncios_detalle', methods=['POST'])
def eliminar_anuncios_detalle(nombre_nora):
    """
    Elimina todos los registros de meta_ads_anuncios_detalle de forma segura.
    """
    try:
        res = supabase.table('meta_ads_anuncios_detalle').delete() \
            .neq('ad_id', '00000000-0000-0000-0000-000000000000').execute()
        if hasattr(res, 'count') and res.count is not None:
            eliminados = res.count
        elif hasattr(res, 'data') and res.data is not None:
            eliminados = len(res.data)
        else:
            eliminados = 0
        return jsonify({'ok': True, 'eliminados': eliminados})
    except Exception as e:
        print(f"[ERROR] Error al eliminar anuncios detalle: {e}")
        return jsonify({'ok': False, 'error': str(e)})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/reporte/<reporte_id>')
def vista_detalle_reporte_ads(nombre_nora, reporte_id):
    """
    Vista de detalle de un reporte semanal de Meta Ads, incluyendo anuncios individuales y datos de la empresa real.
    """
    reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
    if not reporte:
        abort(404)
    anuncios = supabase.table('meta_ads_anuncios_detalle').select('ad_id,nombre_anuncio,importe_gastado,alcance,impresiones,interacciones,clicks,link_clicks,mensajes').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).eq('fecha_inicio', reporte['fecha_inicio']).eq('fecha_fin', reporte['fecha_fin']).order('importe_gastado', desc=True).limit(100).execute().data or []
    empresa = None
    if reporte.get('empresa_id'):
        empresa = supabase.table('cliente_empresas').select('*').eq('id', reporte['empresa_id']).single().execute().data
    return render_template('reportes_meta_ads/detalle_reporte_ads.html', reporte=reporte, anuncios=anuncios, empresa=empresa)

def generar_resumen_por_plataforma(anuncios):
    plataformas = {
        'facebook': {'impresiones': 0, 'alcance': 0, 'clicks': 0, 'mensajes': 0, 'importe_gastado': 0},
        'instagram': {'impresiones': 0, 'alcance': 0, 'clicks': 0, 'mensajes': 0, 'importe_gastado': 0}
    }
    for anuncio in anuncios:
        plataforma = (anuncio.get('publisher_platform') or '').lower()
        if plataforma not in plataformas:
            continue
        plataformas[plataforma]['impresiones'] += anuncio.get('impresiones') or 0
        plataformas[plataforma]['alcance'] += anuncio.get('alcance') or 0
        plataformas[plataforma]['clicks'] += anuncio.get('clicks') or 0
        plataformas[plataforma]['mensajes'] += anuncio.get('mensajes') or 0
        plataformas[plataforma]['importe_gastado'] += anuncio.get('importe_gastado') or 0
    return plataformas

def generar_reporte_semanal(fecha_inicio, fecha_fin):
    """
    Genera y guarda el resumen semanal de Meta Ads basado en los datos de la tabla meta_ads_anuncios_detalle.
    """
    print(f"[INFO] Iniciando generación de reporte semanal: {fecha_inicio} a {fecha_fin}")

    # 1. Traer todos los anuncios de la semana
    try:
        anuncios = supabase.table('meta_ads_anuncios_detalle') \
            .select('*') \
            .gte('fecha_inicio', fecha_inicio.isoformat()) \
            .lte('fecha_fin', fecha_fin.isoformat()) \
            .execute().data or []
        print(f"[INFO] Anuncios recuperados: {len(anuncios)}")
    except Exception as e:
        print(f"[ERROR] Error al recuperar anuncios: {e}")
        return 0

    if not anuncios:
        print("[INFO] No hay anuncios para reportar en este periodo.")
        return 0

    # --- Evitar duplicados por publisher_platform y cuenta: agrupar por ad_id, publisher_platform, id_cuenta_publicitaria ---
    anuncios_por_ad = {}
    for a in anuncios:
        ad_key = (a['ad_id'], a.get('publisher_platform', ''), a.get('id_cuenta_publicitaria', ''))
        if ad_key not in anuncios_por_ad:
            anuncios_por_ad[ad_key] = a.copy()
        else:
            anuncios_por_ad[ad_key]['importe_gastado'] += a.get('importe_gastado', 0) or 0
            anuncios_por_ad[ad_key]['impresiones'] += a.get('impresiones', 0) or 0
            anuncios_por_ad[ad_key]['alcance'] += a.get('alcance', 0) or 0
            anuncios_por_ad[ad_key]['clicks'] += a.get('clicks', 0) or 0
            anuncios_por_ad[ad_key]['mensajes'] += a.get('mensajes', 0) or 0
            anuncios_por_ad[ad_key]['link_clicks'] = anuncios_por_ad[ad_key].get('link_clicks', 0) + (a.get('link_clicks', 0) or 0)
            anuncios_por_ad[ad_key]['interacciones'] = anuncios_por_ad[ad_key].get('interacciones', 0) + (a.get('interacciones', 0) or 0)
            anuncios_por_ad[ad_key]['video_plays'] = anuncios_por_ad[ad_key].get('video_plays', 0) + (a.get('video_plays', 0) or 0)
            anuncios_por_ad[ad_key]['reproducciones_video_3s'] = anuncios_por_ad[ad_key].get('reproducciones_video_3s', 0) + (a.get('reproducciones_video_3s', 0) or 0)
            # Agrega aquí cualquier otro campo acumulable necesario
    anuncios = list(anuncios_por_ad.values())

    # 1b. Traer mapeo de cuentas → empresa_id y nombre
    cuentas_map = {}
    try:
        cuentas_rows = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,empresa_id,nombre_cliente').execute().data or []
        print(f"[INFO] Cuentas recuperadas: {len(cuentas_rows)}")
    except Exception as e:
        print(f"[ERROR] Error al recuperar cuentas: {e}")
        cuentas_rows = []
    for row in cuentas_rows:
        if row.get('id_cuenta_publicitaria'):
            cuentas_map[row['id_cuenta_publicitaria']] = {
                'empresa_id': row.get('empresa_id'),
                'empresa_nombre': row.get('nombre_cliente')
            }

    # 2. Agrupar por (empresa_id, id_cuenta_publicitaria)
    cuentas = {}

    for a in anuncios:
        cuenta_id = str(a.get('id_cuenta_publicitaria')) if a.get('id_cuenta_publicitaria') is not None else ''
        empresa_id = a.get('empresa_id')
        empresa_nombre = a.get('empresa_nombre')  # <-- Usar el del anuncio si existe
        if not empresa_id or not empresa_nombre:
            cuenta_info = cuentas_map.get(cuenta_id, {})
            if not empresa_id:
                empresa_id = cuenta_info.get('empresa_id')
            if not empresa_nombre:
                empresa_nombre = cuenta_info.get('empresa_nombre')
        if not cuenta_id or not empresa_id:
            print(f"[WARN] Anuncio sin cuenta_id o empresa_id: {a}")
            continue

        key = (empresa_id, cuenta_id)
        if key not in cuentas:
            cuentas[key] = {
                'empresa_id': empresa_id,
                'empresa_nombre': empresa_nombre,
                'id_cuenta_publicitaria': cuenta_id,
                'fecha_inicio': fecha_inicio.isoformat(),
                'fecha_fin': fecha_fin.isoformat(),
                'campanas': set(),
                'conjuntos': set(),
                'anuncios': set(),
                'importe_gastado': 0,
                'impresiones': 0,
                'alcance': 0,
                'clicks': 0,
                'link_clicks': 0,
                'mensajes': 0,
                'interacciones': 0,
                'video_plays': 0,
                'reproducciones_video_3s': 0,
                'delivery_activos': 0,
                'delivery_inactivos': 0
            }

    # Sumar solo los anuncios de la cuenta correspondiente
    for key, c in cuentas.items():
        cuenta_id_actual = str(c['id_cuenta_publicitaria'])
        for a in anuncios:
            if str(a.get('id_cuenta_publicitaria')) != cuenta_id_actual:
                continue
            # Agrupación
            if a.get('campana_id'):
                c['campanas'].add(a.get('campana_id'))
            if a.get('conjunto_id'):
                c['conjuntos'].add(a.get('conjunto_id'))
            if a.get('ad_id'):
                c['anuncios'].add(a.get('ad_id'))
            # Sumas (conversión segura a float)
            try:
                importe_gastado = float(a.get('importe_gastado', 0) or 0)
            except Exception:
                importe_gastado = 0
            c['importe_gastado'] += importe_gastado
            c['impresiones'] += int(a.get('impresiones', 0) or 0)
            c['alcance'] += int(a.get('alcance', 0) or 0)
            c['clicks'] += int(a.get('clicks', 0) or 0)
            c['link_clicks'] += int(a.get('link_clicks', 0) or 0)
            c['mensajes'] += int(a.get('mensajes', 0) or 0)
            c['interacciones'] += int(a.get('interacciones', 0) or 0)
            c['video_plays'] += int(a.get('video_plays', 0) or 0)
            c['reproducciones_video_3s'] += int(a.get('reproducciones_video_3s', 0) or 0)
            delivery = (a.get('delivery') or '').lower()
            if delivery == 'active':
                c['delivery_activos'] += 1
            elif delivery:
                c['delivery_inactivos'] += 1

    # 3. Insertar resumen semanal por cuenta (con plataformas)
    inserts = []
    for c in cuentas.values():
        # Filtrar anuncios solo de la cuenta actual
        anuncios_cuenta = [a for a in anuncios if a.get('id_cuenta_publicitaria') == c['id_cuenta_publicitaria']]
        resumen_plataformas = generar_resumen_por_plataforma(anuncios_cuenta)
        inserts.append({
            'empresa_id': c['empresa_id'],
            'empresa_nombre': c['empresa_nombre'],
            'id_cuenta_publicitaria': c['id_cuenta_publicitaria'],
            'fecha_inicio': c['fecha_inicio'],
            'fecha_fin': c['fecha_fin'],
            'total_campañas': len(c['campanas']),
            'importe_gastado_campañas': round(c['importe_gastado'], 2),
            'total_conjuntos': len(c['conjuntos']),
            'importe_gastado_conjuntos': round(c['importe_gastado'], 2),
            'total_anuncios': len(c['anuncios']),
            'importe_gastado_anuncios': round(c['importe_gastado'], 2),
            'impresiones': c['impresiones'],
            'alcance': c['alcance'],
            'clicks': c['clicks'],
            'link_clicks': c['link_clicks'],
            'mensajes': c['mensajes'],
            'interacciones': c['interacciones'],
            'video_plays': c['video_plays'],
            'reproducciones_video_3s': c['reproducciones_video_3s'],
            'delivery_activos': c['delivery_activos'],
            'delivery_inactivos': c['delivery_inactivos'],
            'facebook_impresiones': resumen_plataformas['facebook']['impresiones'],
            'facebook_alcance': resumen_plataformas['facebook']['alcance'],
            'facebook_clicks': resumen_plataformas['facebook']['clicks'],
            'facebook_mensajes': resumen_plataformas['facebook']['mensajes'],
            'facebook_importe_gastado': round(resumen_plataformas['facebook']['importe_gastado'], 2),
            'instagram_impresiones': resumen_plataformas['instagram']['impresiones'],
            'instagram_alcance': resumen_plataformas['instagram']['alcance'],
            'instagram_clicks': resumen_plataformas['instagram']['clicks'],
            'instagram_mensajes': resumen_plataformas['instagram']['mensajes'],
            'instagram_importe_gastado': round(resumen_plataformas['instagram']['importe_gastado'], 2),
            'created_at': datetime.utcnow().isoformat()
        })

    print(f"[INFO] Registros a insertar: {len(inserts)}")

    if inserts:
        try:
            supabase.table('meta_ads_reportes_semanales').insert(inserts).execute()
            print("[INFO] Inserción exitosa en meta_ads_reportes_semanales.")
        except Exception as e:
            print(f"[ERROR] Error al insertar en meta_ads_reportes_semanales: {e}")
    else:
        print("[INFO] No hay registros para insertar.")

    # Ejecutar actualización de empresa_nombre en reportes (solo una vez por ejecución)
    try:
        from clientes.aura.scripts.actualizar_empresa_nombre_reportes import actualizar_empresa_nombre_en_reportes
        # Modificación: el script ahora filtra correctamente nulos y vacíos
        def actualizar_empresa_nombre_en_reportes_patch():
            # Nulos
            reportes_null = supabase.table('meta_ads_reportes_semanales') \
                .select('id, id_cuenta_publicitaria') \
                .is_('empresa_nombre', 'null') \
                .limit(500).execute().data or []
            # Vacíos
            reportes_empty = supabase.table('meta_ads_reportes_semanales') \
                .select('id, id_cuenta_publicitaria') \
                .eq('empresa_nombre', '') \
                .limit(500).execute().data or []
            reportes = reportes_null + reportes_empty
            print(f"🔎 Reportes a actualizar: {len(reportes)}")
            actualizados = 0
            for reporte in reportes:
                cuenta_id = reporte.get('id_cuenta_publicitaria')
                if not cuenta_id:
                    continue
                cuenta = supabase.table('meta_ads_cuentas') \
                    .select('nombre_cliente') \
                    .eq('id_cuenta_publicitaria', cuenta_id) \
                    .single().execute().data
                if cuenta and cuenta.get('nombre_cliente'):
                    supabase.table('meta_ads_reportes_semanales') \
                        .update({'empresa_nombre': cuenta['nombre_cliente']}) \
                        .eq('id', reporte['id']).execute()
                    print(f"✅ Actualizado reporte ID {reporte['id']} con empresa {cuenta['nombre_cliente']}")
                    actualizados += 1
            print(f"🎯 Total actualizados: {actualizados}")
        actualizar_empresa_nombre_en_reportes_patch()
        print("[INFO] Actualización de empresa_nombre en reportes ejecutada.")
    except Exception as e:
        print(f"[WARN] No se pudo actualizar empresa_nombre en reportes: {e}")

    # Ejecutar reparación de reportes sin empresa_nombre (solo una vez por ejecución)
    try:
        print("[INFO] Reparando registros faltantes de empresa_nombre...")
        reportes = supabase.table('meta_ads_reportes_semanales') \
            .select('id, id_cuenta_publicitaria') \
            .is_('empresa_nombre', 'null') \
            .limit(500) \
            .execute().data or []

        if not reportes:
            print("[INFO] No hay registros pendientes por reparar.")
        else:
            cuentas_rows = supabase.table('meta_ads_cuentas') \
                .select('id_cuenta_publicitaria, nombre_cliente') \
                .execute().data or []
            cuentas_map = {row['id_cuenta_publicitaria']: row['nombre_cliente'] for row in cuentas_rows}
            for rep in reportes:
                cuenta_id = rep['id_cuenta_publicitaria']
                empresa_nombre = cuentas_map.get(cuenta_id)
                if empresa_nombre:
                    supabase.table('meta_ads_reportes_semanales') \
                        .update({'empresa_nombre': empresa_nombre}) \
                        .eq('id', rep['id']).execute()
                    print(f"[OK] Actualizado reporte {rep['id']} -> {empresa_nombre}")
    except Exception as e:
        print(f"[ERROR] Reparación fallida: {e}")

    return len(inserts)

# Variable global para controlar la sincronización
sync_stop_flag = threading.Event()

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/parar_sincronizacion', methods=['POST'])
def parar_sincronizacion(nombre_nora):
    """
    Permite parar la sincronización manualmente.
    """
    global sync_stop_flag
    sync_stop_flag.set()
    return jsonify({'ok': True, 'msg': 'Sincronización detenida.'})

# Modifica la función de sincronización para checar el flag:
def sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin):
    global sync_stop_flag
    sync_stop_flag.clear()  # Reset al inicio
    """
    Sincroniza anuncios de Meta Ads para todas las cuentas activas y alimenta la tabla meta_ads_anuncios_detalle en Supabase.
    Solo inserta/actualiza anuncios con spend > 0 en el periodo.
    Devuelve un dict con el total procesado y un listado de cuentas sin anuncios.
    """
    print(f"[SYNC] Iniciando sincronización de anuncios Meta Ads: {fecha_inicio} a {fecha_fin}")
    access_token = os.environ.get('META_ACCESS_TOKEN')
    if not access_token:
        print("[ERROR] No se encontró META_ACCESS_TOKEN en variables de entorno.")
        return {"procesados": 0, "sin_anuncios": []}
    cuentas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,empresa_id,nombre_cliente').execute().data or []
    print(f"[SYNC] Cuentas publicitarias encontradas: {len(cuentas)}")
    total_procesados = 0
    cuentas_sin_anuncios = []
    for cuenta in cuentas:
        if sync_stop_flag.is_set():
            print('[SYNC] Sincronización detenida por el usuario.')
            break
        cuenta_id = cuenta.get('id_cuenta_publicitaria')
        empresa_id = cuenta.get('empresa_id')
        nombre_cliente = cuenta.get('nombre_cliente')
        if not cuenta_id or not empresa_id:
            print(f"[WARN] Cuenta sin id o empresa_id: {cuenta}")
            continue
        print(f"[SYNC] Procesando cuenta: {cuenta_id}")
        url_base = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/insights"
        fields_a = [
            'ad_id', 'ad_name',
            'adset_id', 'adset_name',
            'campaign_id', 'campaign_name',
            'impressions', 'reach', 'frequency',
            'spend', 'clicks', 'unique_clicks',
            'ctr', 'cpc', 'unique_ctr',
            'quality_ranking', 'engagement_rate_ranking', 'conversion_rate_ranking',
            'date_start', 'date_stop',
            'account_id', 'account_name'
        ]
        params_a = {
            'level': 'ad',
            'fields': ','.join(fields_a),
            'breakdowns': 'publisher_platform',  # <-- Ajuste crítico para obtener la plataforma
            'time_range': json.dumps({
                'since': fecha_inicio.isoformat(),
                'until': fecha_fin.isoformat()
            }),
            'limit': 100,
            'access_token': access_token
        }
        params_b = {
            'level': 'ad',
            'fields': 'ad_id,actions',
            'action_breakdowns': 'action_type',
            'time_range': json.dumps({
                'since': fecha_inicio.isoformat(),
                'until': fecha_fin.isoformat()
            }),
            'limit': 100,
            'access_token': access_token
        }
        def fetch_all(url, params):
            results = []
            next_url = url
            next_params = params.copy()
            while next_url:
                r = requests.get(next_url, params=next_params)
                if r.status_code != 200:
                    print(f"[ERROR] Meta API error {r.status_code}: {r.text}")
                    try:
                        error_data = r.json().get("error", {})
                        if error_data.get("code") == 200:
                            print(f"[SYNC][WARN] Sin permisos suficientes para la cuenta. Saltando cuenta actual.")
                            return []
                    except Exception:
                        pass
                    raise Exception(f"Meta API error {r.status_code}: {r.text}")
                data = r.json()
                results.extend(data.get('data', []))
                paging = data.get('paging', {})
                next_url = paging.get('next')
                next_params = {}
            return results
        datos_a = fetch_all(url_base, params_a)
        datos_b = fetch_all(url_base, params_b)
        print(f"[SYNC] Anuncios encontrados (A): {len(datos_a)} | (B): {len(datos_b)}")
        if not datos_a:
            cuentas_sin_anuncios.append({
                "id_cuenta_publicitaria": cuenta_id,
                "empresa_id": empresa_id,
                "nombre_cliente": nombre_cliente
            })
        anuncios = {}
        for a in datos_a:
            ad_id = a.get('ad_id')
            platform = a.get('publisher_platform', '').lower()
            if not ad_id or not platform:
                continue
            key = f"{ad_id}__{platform}"
            anuncios[key] = {**a, 'publisher_platform': platform}
        # --- Actions agregadas y mapeo robusto
        # Definir mapeo de action_type a campo en registro
        action_map = {
            'post_reaction': 'post_reactions',
            'comment': 'comments',
            'share': 'shares',
            'post_engagement': 'post_engagement',
            'page_engagement': 'page_engagement',
            'link_click': 'link_clicks',
            'video_view': 'video_plays',
            'onsite_conversion.messaging_conversation_started_7d': 'mensajes',
            'onsite_conversion.post_save': 'saves'
        }
        # Inicializar métricas de actions en cada anuncio
        for ad in anuncios.values():
            for campo in action_map.values():
                ad[campo] = 0
        for b in datos_b:
            ad_id = b.get('ad_id')
            platform = b.get('publisher_platform', '').lower()
            key = f"{ad_id}__{platform}"
            if not ad_id or not platform or key not in anuncios:
                continue
            actions = b.get('actions', [])
            for act in actions:
                tipo = act.get('action_type')
                valor = act.get('value')
                if tipo and valor is not None and tipo in action_map:
                    campo_tabla = action_map[tipo]
                    try:
                        valor = int(valor)
                    except:
                        valor = float(valor) if valor else 0
                    anuncios[key][campo_tabla] += valor
        # --- Inserción/Upsert robusto con on_conflict --- hola mundo
        for ad_id, ad in anuncios.items():
            print(f"[DEBUG] Procesando anuncio: ad_id={ad_id}, ad={ad}")
            try:
                spend = float(ad.get('spend', 0) or 0)
            except Exception:
                spend = 0
            if spend <= 0:
                print(f"[DEBUG] Anuncio {ad_id} omitido por gasto 0")
                continue  # Solo anuncios con gasto positivo

            # Validar que cuenta_id no sea None o vacío
            print(f"[DEBUG] cuenta_id antes de validación: {cuenta_id}")
            if not cuenta_id:
                print(f"[ERROR] id_cuenta_publicitaria es None o vacío para el anuncio {ad_id}. Se omite este registro. ad={ad}")
                continue

            registro = {
                'ad_id': str(ad_id),
                'nombre_anuncio': ad.get('ad_name'),
                'conjunto_id': ad.get('adset_id'),
                'nombre_conjunto': ad.get('adset_name'),
                'campana_id': ad.get('campaign_id'),
                'nombre_campana': ad.get('campaign_name'),
                'id_cuenta_publicitaria': str(cuenta_id),
                'importe_gastado': spend,
                'impresiones': int(ad.get('impressions', 0) or 0),
                'alcance': int(ad.get('reach', 0) or 0),
                'clicks': int(ad.get('clicks', 0) or 0),
                'unique_clicks': int(ad.get('unique_clicks', 0) or 0),
                'ctr': float(ad.get('ctr', 0) or 0),
                'cpc': float(ad.get('cpc', 0) or 0),
                'unique_ctr': float(ad.get('unique_ctr', 0) or 0),
                'quality_ranking': ad.get('quality_ranking'),
                'engagement_rate_ranking': ad.get('engagement_rate_ranking'),
                'conversion_rate_ranking': ad.get('conversion_rate_ranking'),
                'post_reactions': ad.get('post_reactions', 0),
                'comments': ad.get('comments', 0),
                'shares': ad.get('shares', 0),
                'post_engagement': ad.get('post_engagement', 0),
                'page_engagement': ad.get('page_engagement', 0),
                'link_clicks': ad.get('link_clicks', 0),
                'video_plays': ad.get('video_plays', 0),
                'mensajes': ad.get('mensajes', 0),
                'publisher_platform': str(ad.get('publisher_platform')) if ad.get('publisher_platform') is not None else '',
                'saves': ad.get('saves', 0),
                'fecha_inicio': fecha_inicio.isoformat() if hasattr(fecha_inicio, 'isoformat') else str(fecha_inicio),
                'fecha_fin': fecha_fin.isoformat() if hasattr(fecha_fin, 'isoformat') else str(fecha_fin),
            }

            print(f"[DEBUG] Registro a upsert: {registro}")

            # Depuración: imprime los valores clave antes del upsert
            print('DEBUG registro upsert:', {
                'ad_id': registro.get('ad_id'),
                'fecha_inicio': registro.get('fecha_inicio'),
                'fecha_fin': registro.get('fecha_fin'),
                'publisher_platform': registro.get('publisher_platform'),
                'id_cuenta_publicitaria': registro.get('id_cuenta_publicitaria')
            })

            try:
                supabase.table('meta_ads_anuncios_detalle') \
                    .upsert(
                        registro,
                        on_conflict="ad_id,fecha_inicio,fecha_fin,publisher_platform"
                    ) \
                    .execute()
                print(f"[SYNC] Insertado/Actualizado anuncio {ad_id} ({ad.get('publisher_platform')})")
            except Exception as e:
                print(f"[ERROR] Error al insertar/actualizar anuncio {ad_id} ({ad.get('publisher_platform')}): {e}")
                print(f"[ERROR][EXTRA] Registro problemático: {registro}")
                return  # Detener toda la sincronización al primer error
    print(f"[SYNC] Total anuncios procesados: {total_procesados}")
    return {"procesados": total_procesados, "sin_anuncios": cuentas_sin_anuncios}

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/cuentas_json', methods=['GET'])
def cuentas_publicitarias_json(nombre_nora):
    """
    Devuelve todas las cuentas publicitarias (id y nombre_cliente) para el modal de sincronización.
    """
    cuentas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,nombre_cliente').execute().data or []
    return jsonify({'ok': True, 'cuentas': cuentas})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/variables_json', methods=['GET'])
def variables_anuncios_detalle_json(nombre_nora):
    """
    Devuelve los campos/variables de la tabla meta_ads_anuncios_detalle para mostrar en el modal.
    """
    from clientes.aura.routes.reportes_meta_ads.mapeo_manual import obtener_columnas_tabla
    from clientes.aura.utils.supabase_client import supabase as sb
    columnas = obtener_columnas_tabla(sb, 'meta_ads_anuncios_detalle')
    return jsonify({'ok': True, 'variables': columnas})
