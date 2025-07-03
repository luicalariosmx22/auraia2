# Archivo: clientes/aura/routes/reportes_meta_ads/estadisticas.py
from flask import Blueprint, render_template, request, jsonify, abort
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase
import os
import requests
import json
import threading

from clientes.aura.routes.reportes_meta_ads.utils.columnas_meta_ads import (
    limpiar_columnas_solicitadas, obtener_fields_para_meta, obtener_breakdowns, MAPEO_COLUMNAS_META_ADS
)

estadisticas_ads_bp = Blueprint('estadisticas_ads_bp', __name__)

# NUEVA RUTA CORRECTA PARA ESTADÍSTICAS DE META ADS
@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas', methods=['GET', 'POST'])
def vista_estadisticas_ads(nombre_nora):
    if request.method == 'POST':
        fecha_fin = datetime.utcnow().date()
        fecha_inicio = fecha_fin - timedelta(days=6)
        total = generar_reporte_meta_ads(fecha_inicio, fecha_fin)
        return jsonify({'ok': True, 'insertados': total})
    return render_template('reportes_meta_ads/estadisticas_ads.html', nombre_nora=nombre_nora)

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/data', methods=['GET'])
def obtener_estadisticas_data(nombre_nora):
    """
    Devuelve los reportes semanales agregados para mostrar en el frontend.
    """
    reportes = supabase.table('meta_ads_reportes_semanales').select('*').order('fecha_fin', desc=True).limit(52).execute().data or []
    print(f"[DEBUG] Reportes obtenidos: {len(reportes)}")
    if reportes:
        print(f"[DEBUG] Primer reporte: empresa_nombre='{reportes[0].get('empresa_nombre')}', empresa_id='{reportes[0].get('empresa_id')}'")
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
    """
    Sincronización manual desde el modal: recibe fechas y columnas desde el formulario.
    Al finalizar, genera el reporte semanal para ese rango de fechas.
    """
    from datetime import datetime
    try:
        fecha_inicio_str = request.form.get('fecha_inicio')
        fecha_fin_str = request.form.get('fecha_fin')
        columnas_str = request.form.get('columnas')
        columnas = [c.strip() for c in columnas_str.split(',') if c.strip()] if columnas_str else None
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
        resultado = sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin, columnas=columnas)
        # Generar el reporte semanal para ese rango
        total_reportes = generar_reporte_meta_ads(fecha_inicio, fecha_fin)
        return jsonify({'ok': True, 'procesados': resultado["procesados"], 'sin_anuncios': resultado["sin_anuncios"], 'reportes_generados': total_reportes})
    except Exception as e:
        print(f"[ERROR] Error en sincronización manual: {e}")
        return jsonify({'ok': False, 'error': str(e)})

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
    Elimina TODOS los registros de meta_ads_anuncios_detalle de forma segura (sin filtro).
    """
    try:
        # Supabase requiere un WHERE, así que usamos un filtro que siempre es verdadero
        res = supabase.table('meta_ads_anuncios_detalle').delete().neq('id', 0).execute()
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
    print(f"[DEBUG] Filtro solo por id_cuenta_publicitaria={reporte['id_cuenta_publicitaria']}")
    anuncios = supabase.table('meta_ads_anuncios_detalle')\
        .select('*')\
        .eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria'])\
        .order('importe_gastado', desc=True)\
        .limit(1000).execute().data or []
    print(f"[DEBUG] Anuncios recuperados: {len(anuncios)}")
    if anuncios:
        print(f"[DEBUG] Primer anuncio: {anuncios[0]}")
        fechas_inicio = [a['fecha_inicio'] for a in anuncios if a.get('fecha_inicio')]
        fechas_fin = [a['fecha_fin'] for a in anuncios if a.get('fecha_fin')]
        fecha_inicio_anuncios = min(fechas_inicio) if fechas_inicio else None
        fecha_fin_anuncios = max(fechas_fin) if fechas_fin else None
    else:
        fecha_inicio_anuncios = None
        fecha_fin_anuncios = None
    empresa = None
    if reporte.get('empresa_id'):
        empresa = supabase.table('cliente_empresas').select('*').eq('id', reporte['empresa_id']).single().execute().data
    return render_template('reportes_meta_ads/detalle_reporte_ads.html', reporte=reporte, anuncios=anuncios, empresa=empresa, fecha_inicio_anuncios=fecha_inicio_anuncios, fecha_fin_anuncios=fecha_fin_anuncios)

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

def generar_reporte_meta_ads(fecha_inicio, fecha_fin):
    """
    Genera y guarda el resumen de Meta Ads basado en los datos de la tabla meta_ads_anuncios_detalle para cualquier rango de fechas.
    """
    print(f"[INFO] Iniciando generación de reporte Meta Ads: {fecha_inicio} a {fecha_fin}")

    # 1. Traer todos los anuncios del rango
    print(f"[DEBUG] Recuperando TODOS los anuncios de la tabla sin filtrar por fecha.")
    try:
        anuncios = supabase.table('meta_ads_anuncios_detalle') \
            .select('*') \
            .execute().data or []
        print(f"[INFO] Anuncios recuperados: {len(anuncios)}")
        if anuncios:
            print(f"[DEBUG] Primer anuncio recuperado: {anuncios[0]}")
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
        anuncios_por_ad[ad_key] = a.copy()
    anuncios = list(anuncios_por_ad.values())

    # 1b. Traer mapeo de cuentas → empresa_id y nombre
    cuentas_map = {}
    empresas_map = {}  # Nuevo: mapeo de empresa_id → nombre_empresa real
    try:
        cuentas_rows = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,empresa_id,nombre_cliente').execute().data or []
        print(f"[INFO] Cuentas recuperadas: {len(cuentas_rows)}")
        
        # Obtener nombres reales de empresas
        empresas_rows = supabase.table('cliente_empresas').select('id,nombre_empresa').execute().data or []
        print(f"[INFO] Empresas recuperadas: {len(empresas_rows)}")
        for emp in empresas_rows:
            if emp.get('id'):
                empresas_map[emp['id']] = emp.get('nombre_empresa', 'Sin nombre')
        
    except Exception as e:
        print(f"[ERROR] Error al recuperar cuentas/empresas: {e}")
        cuentas_rows = []
        
    for row in cuentas_rows:
        if row.get('id_cuenta_publicitaria'):
            empresa_id = row.get('empresa_id')
            nombre_empresa_real = empresas_map.get(empresa_id, row.get('nombre_cliente', 'Sin empresa'))
            cuentas_map[row['id_cuenta_publicitaria']] = {
                'empresa_id': empresa_id,
                'empresa_nombre': nombre_empresa_real  # Ahora usa el nombre real de la empresa
            }

    # 2. Agrupar por (empresa_id, id_cuenta_publicitaria)
    cuentas = {}
    for a in anuncios:
        cuenta_id = str(a.get('id_cuenta_publicitaria')) if a.get('id_cuenta_publicitaria') is not None else ''
        empresa_id = a.get('empresa_id')
        empresa_nombre = a.get('empresa_nombre')
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
                'delivery_activos': 0,
                'delivery_inactivos': 0
            }
    for key, c in cuentas.items():
        cuenta_id_actual = str(c['id_cuenta_publicitaria'])
        for a in anuncios:
            if str(a.get('id_cuenta_publicitaria')) != cuenta_id_actual:
                continue
            if a.get('campana_id'):
                c['campanas'].add(a.get('campana_id'))
            if a.get('conjunto_id'):
                c['conjuntos'].add(a.get('conjunto_id'))
            if a.get('ad_id'):
                c['anuncios'].add(a.get('ad_id'))
            c['importe_gastado'] += safe_float(a.get('importe_gastado'))
            c['impresiones'] += safe_int(a.get('impresiones'))
            c['alcance'] += safe_int(a.get('alcance'))
            c['clicks'] += safe_int(a.get('clicks'))
            c['link_clicks'] += safe_int(a.get('link_clicks'))
            c['mensajes'] += safe_int(a.get('mensajes'))
            c['interacciones'] += safe_int(a.get('interacciones'))
            c['video_plays'] += safe_int(a.get('video_plays'))
            delivery = (a.get('delivery') or '').lower()
            if delivery == 'active':
                c['delivery_activos'] += 1
            elif delivery:
                c['delivery_inactivos'] += 1
    inserts = []
    for c in cuentas.values():
        anuncios_cuenta = [a for a in anuncios if a.get('id_cuenta_publicitaria') == c['id_cuenta_publicitaria']]
        resumen_plataformas = generar_resumen_por_plataforma(anuncios_cuenta)
        insert_obj = {
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
        }
        print(f"[DEBUG] Insert a report: {insert_obj}")
        inserts.append(insert_obj)
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
        def actualizar_empresa_nombre_en_reportes_patch():
            reportes_null = supabase.table('meta_ads_reportes_semanales') \
                .select('id, id_cuenta_publicitaria') \
                .is_('empresa_nombre', 'null') \
                .limit(500).execute().data or []
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
def sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin, columnas=None):
    global sync_stop_flag
    sync_stop_flag.clear()
    
    print(f"[SYNC] Iniciando sincronización de anuncios Meta Ads: {fecha_inicio} a {fecha_fin}")
    access_token = os.environ.get('META_ACCESS_TOKEN')
    if not access_token:
        print("[ERROR] No se encontró META_ACCESS_TOKEN.")
        return {"procesados": 0, "sin_anuncios": []}

    cuentas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,empresa_id,nombre_cliente,estado_actual').execute().data or []
    cuentas = [c for c in cuentas if c.get('estado_actual') != 'excluida']
    print(f"[SYNC] Cuentas publicitarias encontradas (no excluidas): {len(cuentas)}")

    total_procesados = 0
    cuentas_sin_anuncios = []

    for idx_cuenta, cuenta in enumerate(cuentas):
        if sync_stop_flag.is_set():
            print('[SYNC] Sincronización detenida por el usuario.')
            break

        cuenta_id = cuenta.get('id_cuenta_publicitaria')
        empresa_id = cuenta.get('empresa_id')
        nombre_cliente = cuenta.get('nombre_cliente')
        if not cuenta_id or not empresa_id:
            print(f"[WARN] Cuenta sin id o empresa_id: {cuenta}")
            continue

        print(f"[SYNC] Procesando cuenta {idx_cuenta + 1}/{len(cuentas)}: {cuenta_id} ({nombre_cliente})")

        # --- Obtener columnas válidas y fields finales ---
        columnas_validas = limpiar_columnas_solicitadas(columnas)
        fields_para_meta = obtener_fields_para_meta(columnas_validas)
        breakdowns = obtener_breakdowns()

        params_a = {
            'level': 'ad',
            'fields': ','.join(fields_para_meta),
            'breakdowns': ','.join(breakdowns),
            'time_range': json.dumps({
                'since': fecha_inicio.isoformat(),
                'until': fecha_fin.isoformat()
            }),
            'limit': 1000,  # Aumentar el límite para menos requests
            'access_token': access_token
        }

        url_base = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/insights"

        def fetch_all(url, params):
            results = []
            next_url = url
            next_params = params.copy()
            request_count = 0
            max_requests = 20  # Límite máximo de requests por cuenta
            timeout_retries = 0
            max_timeout_retries = 3
            
            while next_url and request_count < max_requests:
                request_count += 1
                if request_count % 5 == 0:
                    print(f"[SYNC] Petición {request_count}/{max_requests} para cuenta {cuenta_id}...")
                
                try:
                    r = requests.get(next_url, params=next_params, timeout=15)  # Timeout reducido
                    if r.status_code != 200:
                        print(f"[ERROR] Meta API error {r.status_code}: {r.text}")
                        if r.status_code == 429:  # Rate limit
                            print(f"[WARN] Rate limit alcanzado, esperando 30 segundos...")
                            import time
                            time.sleep(30)
                            continue
                        raise Exception(f"Meta API error {r.status_code}: {r.text}")
                    data = r.json()
                    batch_data = data.get('data', [])
                    results.extend(batch_data)
                    print(f"[SYNC] Obtenidos {len(batch_data)} registros en esta petición (total: {len(results)})")
                    
                    paging = data.get('paging', {})
                    next_url = paging.get('next')
                    next_params = {}
                    
                    # Reset timeout retries on success
                    timeout_retries = 0
                    
                    # Pequeña pausa para ser respetuosos con la API
                    if next_url:
                        import time
                        time.sleep(0.5)  # Pausa aumentada
                        
                except requests.exceptions.Timeout:
                    timeout_retries += 1
                    if timeout_retries > max_timeout_retries:
                        print(f"[ERROR] Demasiados timeouts ({timeout_retries}), saltando cuenta {cuenta_id}")
                        break
                    print(f"[WARN] Timeout en petición {request_count} (intento {timeout_retries}/{max_timeout_retries}), reintentando...")
                    import time
                    time.sleep(5)
                    continue
                except Exception as e:
                    print(f"[ERROR] Error en petición {request_count}: {e}")
                    # En caso de error, saltar a la siguiente cuenta
                    break
                    
            if request_count >= max_requests:
                print(f"[WARN] Límite de requests alcanzado para cuenta {cuenta_id}")
                    
            return results

        datos_a = fetch_all(url_base, params_a)
        print(f"[SYNC] Anuncios encontrados (A): {len(datos_a)}")
        if not datos_a:
            cuentas_sin_anuncios.append({
                "id_cuenta_publicitaria": cuenta_id,
                "empresa_id": empresa_id,
                "nombre_cliente": nombre_cliente
            })
            continue

        # Optimización: si hay demasiados anuncios, procesar solo los primeros para evitar cuelgues
        if len(datos_a) > 100:
            print(f"[WARN] Cuenta {cuenta_id} tiene {len(datos_a)} anuncios, limitando a 100 para evitar timeout")
            datos_a = datos_a[:100]

        print(f"[SYNC] Preparando segunda consulta para actions...")
        # 2do request para actions
        params_b = {
            'level': 'ad',
            'fields': 'ad_id,actions',
            'action_breakdowns': 'action_type',
            'time_range': json.dumps({
                'since': fecha_inicio.isoformat(),
                'until': fecha_fin.isoformat()
            }),
            'limit': 1000,  # Aumentar el límite para menos requests
            'access_token': access_token
        }
        print(f"[SYNC] Iniciando segunda consulta para actions...")
        try:
            datos_b = fetch_all(url_base, params_b)
            print(f"[SYNC] Actions encontradas (B): {len(datos_b)}")
        except Exception as e:
            print(f"[WARN] Error en segunda consulta para cuenta {cuenta_id}: {e}")
            print(f"[WARN] Continuando sin actions para esta cuenta...")
            datos_b = []

        print(f"[SYNC] Inicializando campos de actions...")
        # Inicializar campos de actions en datos_a
        for ad in datos_a:
            ad_id = ad.get('ad_id')
            ad['mensajes'] = 0
            ad['interacciones'] = 0
            ad['post_reactions'] = 0
            ad['comments'] = 0
            ad['shares'] = 0

        action_map = {
            'onsite_conversion.messaging_conversation_started_7d': 'mensajes',
            'messaging_conversations_started': 'mensajes',
            'post_engagement': 'interacciones',
            'post_reaction': 'post_reactions',
            'comment': 'comments',
            'share': 'shares'
        }
        
        print(f"[SYNC] Enlazando actions de datos_b sobre datos_a...")
        # Enlazar actions de datos_b sobre datos_a
        for b in datos_b:
            ad_id = b.get('ad_id')
            actions = b.get('actions', [])
            ad_match = next((a for a in datos_a if a.get('ad_id') == ad_id), None)
            if not ad_match:
                continue
            for act in actions:
                tipo = act.get('action_type')
                valor = act.get('value')
                if tipo and valor is not None and tipo in action_map:
                    campo_local = action_map[tipo]
                    try:
                        valor = int(valor)
                    except:
                        valor = 0
                    ad_match[campo_local] += valor

        # Optimización avanzada: Usar batch requests para obtener nombres
        print(f"[SYNC] Recopilando IDs únicos para optimización...")
        adset_ids = set()
        campaign_ids = set();
        for ad in datos_a:
            if ad.get('adset_id'):
                adset_ids.add(ad.get('adset_id'))
            if ad.get('campaign_id'):
                campaign_ids.add(ad.get('campaign_id'))
        
        # Cache para nombres para evitar llamadas duplicadas
        nombres_cache = {}
        
        # Obtener nombres usando batch requests más eficientes
        if campaign_ids:
            print(f"[SYNC] Obteniendo nombres de {len(campaign_ids)} campañas...")
            nombres_campanas = obtener_nombres_batch(list(campaign_ids), access_token, tipo='campaign')
            for campaign_id, nombre in nombres_campanas.items():
                nombres_cache[f"campaign_{campaign_id}"] = nombre
        
        if adset_ids:
            print(f"[SYNC] Obteniendo nombres de {len(adset_ids)} conjuntos...")
            nombres_conjuntos = obtener_nombres_batch(list(adset_ids), access_token, tipo='adset')
            for adset_id, nombre in nombres_conjuntos.items():
                nombres_cache[f"adset_{adset_id}"] = nombre

        print(f"[SYNC] Procesando {len(datos_a)} anuncios para inserción...")
        
        # Procesar anuncios en lotes para mejor rendimiento
        batch_size = 100
        batch_inserts = []
        
        for idx, ad in enumerate(datos_a):
            if sync_stop_flag.is_set():
                print('[SYNC] Sincronización detenida por el usuario.')
                break
                
            # Mostrar progreso cada 50 anuncios
            if idx % 50 == 0 and idx > 0:
                print(f"[SYNC] Progreso: {idx}/{len(datos_a)} anuncios procesados")
            
            try:
                registro = {}

                for col in columnas_validas:
                    campo_api = obtener_fields_para_meta([col])[0]
                    registro[col] = ad.get(campo_api)

                registro['id_cuenta_publicitaria'] = str(cuenta_id)
                registro['fecha_inicio'] = fecha_inicio.isoformat()
                registro['fecha_fin'] = fecha_fin.isoformat()
                registro['publisher_platform'] = ad.get('publisher_platform') or 'unknown'
                # Enriquecimiento de actions
                registro['mensajes'] = ad.get('mensajes') or 0
                registro['interacciones'] = ad.get('interacciones') or 0
                registro['post_reactions'] = ad.get('post_reactions') or 0
                registro['comments'] = ad.get('comments') or 0
                registro['shares'] = ad.get('shares') or 0
                # Enriquecimiento de nombres usando cache
                adset_id = ad.get('adset_id')
                campaign_id = ad.get('campaign_id')
                registro['nombre_conjunto'] = nombres_cache.get(f"adset_{adset_id}", f"Conjunto {adset_id}")
                registro['nombre_campana'] = nombres_cache.get(f"campaign_{campaign_id}", f"Campaña {campaign_id}")

                batch_inserts.append(registro)
                
                # Insertar en lotes para mejor rendimiento
                if len(batch_inserts) >= batch_size:
                    try:
                        supabase.table('meta_ads_anuncios_detalle') \
                            .upsert(
                                batch_inserts,
                                on_conflict="ad_id,fecha_inicio,fecha_fin,publisher_platform"
                            ) \
                            .execute()
                        total_procesados += len(batch_inserts)
                        print(f"[SYNC] Lote de {len(batch_inserts)} anuncios insertado exitosamente")
                        batch_inserts = []
                    except Exception as e:
                        print(f"[ERROR] Error al insertar lote de anuncios: {e}")
                        # Fallback: insertar uno por uno
                        for reg in batch_inserts:
                            try:
                                supabase.table('meta_ads_anuncios_detalle') \
                                    .upsert(
                                        reg,
                                        on_conflict="ad_id,fecha_inicio,fecha_fin,publisher_platform"
                                    ) \
                                    .execute()
                                total_procesados += 1
                            except Exception as e2:
                                print(f"[ERROR] Error al insertar anuncio individual {reg.get('ad_id')}: {e2}")
                        batch_inserts = []

            except Exception as e:
                print(f"[ERROR] Error al procesar anuncio {ad.get('ad_id')}: {e}")

        # Insertar el último lote si queda algo
        if batch_inserts:
            try:
                supabase.table('meta_ads_anuncios_detalle') \
                    .upsert(
                        batch_inserts,
                        on_conflict="ad_id,fecha_inicio,fecha_fin,publisher_platform"
                    ) \
                    .execute()
                total_procesados += len(batch_inserts)
                print(f"[SYNC] Último lote de {len(batch_inserts)} anuncios insertado exitosamente")
            except Exception as e:
                print(f"[ERROR] Error al insertar último lote: {e}")
                # Fallback: insertar uno por uno
                for reg in batch_inserts:
                    try:
                        supabase.table('meta_ads_anuncios_detalle') \
                            .upsert(
                                reg,
                                on_conflict="ad_id,fecha_inicio,fecha_fin,publisher_platform"
                            ) \
                            .execute()
                        total_procesados += 1
                    except Exception as e2:
                        print(f"[ERROR] Error al insertar anuncio individual {reg.get('ad_id')}: {e2}")
        
        print(f"[SYNC] Cuenta {cuenta_id} completada: {total_procesados} anuncios procesados")
        
        # Limpieza de memoria para cuentas grandes
        del datos_a, datos_b, nombres_cache
        import gc
        gc.collect()

    print(f"[SYNC] Total anuncios procesados: {total_procesados}")
    return {"procesados": total_procesados, "sin_anuncios": cuentas_sin_anuncios}

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/cuentas_json', methods=['GET'])
def cuentas_publicitarias_json(nombre_nora):
    """
    Devuelve todas las cuentas publicitarias (id y nombre_cliente) para el modal de sincronización.
    """
    cuentas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria,nombre_cliente,estado_actual').execute().data or []
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

@estadisticas_ads_bp.route('/estadisticas/columnas_detalle', methods=['GET'])
def obtener_columnas_anuncios_detalle():
    """
    Devuelve las columnas disponibles en meta_ads_anuncios_detalle para configurar sincronización.
    """
    columnas_estaticas = [
        'importe_gastado', 'impresiones', 'alcance', 'clicks', 'link_clicks', 'unique_clicks',
        'ctr', 'cpc', 'unique_ctr', 'post_reactions', 'comments', 'shares', 'video_plays',
        'mensajes', 'publisher_platform'
    ]
    return jsonify({'ok': True, 'columnas': columnas_estaticas})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/columnas_disponibles', methods=['GET'])
def columnas_disponibles_meta_ads(nombre_nora):
    """
    Devuelve las columnas válidas para sincronizar, incluyendo campos fijos y breakdowns.
    """
    columnas = list(MAPEO_COLUMNAS_META_ADS.keys())
    columnas += ['fecha_inicio', 'fecha_fin', 'publisher_platform']  # Campos fijos siempre necesarios
    return jsonify({'ok': True, 'columnas': columnas})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/excluir_cuentas', methods=['POST'])
def excluir_cuentas_publicitarias(nombre_nora):
    """
    Marca como 'excluida' en estado_actual las cuentas seleccionadas y limpia el campo en las demás.
    """
    data = request.get_json()
    cuentas_excluir = data.get('cuentas_excluir', '')
    ids_excluir = [c for c in cuentas_excluir.split(',') if c]
    # Primero, poner estado_actual = 'excluida' a las seleccionadas
    if ids_excluir:
        supabase.table('meta_ads_cuentas').update({'estado_actual': 'excluida'}).in_('id_cuenta_publicitaria', ids_excluir).execute()
        # Obtener todos los IDs de cuentas
        todas = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria').execute().data or []
        ids_todas = [c['id_cuenta_publicitaria'] for c in todas]
        ids_no_excluir = [c for c in ids_todas if c not in ids_excluir]
        if ids_no_excluir:
            supabase.table('meta_ads_cuentas').update({'estado_actual': None}).in_('id_cuenta_publicitaria', ids_no_excluir).execute()
    else:
        # Si no hay exclusiones, limpiar todas
        supabase.table('meta_ads_cuentas').update({'estado_actual': None}).execute()
    return jsonify({'ok': True, 'excluidas': ids_excluir})

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/sincronizacion_manual', methods=['GET'])
def vista_sincronizacion_manual(nombre_nora):
    """
    Página dedicada para la sincronización manual de Meta Ads.
    """
    return render_template('reportes_meta_ads/sincronizacion_manual.html', nombre_nora=nombre_nora)

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/insertar_anuncio_prueba', methods=['POST'])
def insertar_anuncio_prueba(nombre_nora):
    """
    Inserta un anuncio de prueba en meta_ads_anuncios_detalle para validar el flujo de reportes.
    """
    from datetime import datetime
    hoy = datetime.utcnow().date()
    anuncio = {
        'ad_id': 'TEST123',
        'nombre_anuncio': 'Anuncio Prueba',
        'conjunto_id': 'SET1',
        'nombre_conjunto': 'Conjunto Prueba',
        'campana_id': 'CAMP1',
        'nombre_campana': 'Campaña Prueba',
        'id_cuenta_publicitaria': 'CUENTA_PRUEBA',
        'importe_gastado': 100.0,
        'impresiones': 1000,
        'alcance': 800,
        'clicks': 50,
        'unique_clicks': 40,
        'ctr': 5.0,
        'cpc': 2.0,
        'unique_ctr': 4.0,
        'quality_ranking': 'HIGH',
        'engagement_rate_ranking': 'AVERAGE',
        'conversion_rate_ranking': 'LOW',
        'post_reactions': 10,
        'comments': 2,
        'shares': 1,
        'post_engagement': 5,
        'page_engagement': 3,
        'link_clicks': 20,
        'video_plays': 15,
        'mensajes': 4,
        'publisher_platform': 'facebook',
        'saves': 0,
        'fecha_inicio': hoy.isoformat(),
        'fecha_fin': hoy.isoformat(),
    }
    try:
        supabase.table('meta_ads_anuncios_detalle').insert(anuncio).execute()
        return jsonify({'ok': True, 'msg': 'Anuncio de prueba insertado', 'anuncio': anuncio})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

def safe_int(value):
    try:
        return int(value or 0)
    except:
        return 0

def safe_float(value):
    try:
        return float(value or 0)
    except:
        return 0.0

def obtener_nombres_batch(object_ids, access_token, tipo='campaign', batch_size=50):
    """
    Obtiene nombres de múltiples objetos (campañas/conjuntos) usando batch requests
    para mejorar significativamente el rendimiento.
    """
    if not object_ids:
        return {}
    
    nombres = {}
    
    # Procesar en lotes para evitar límites de la API
    for i in range(0, len(object_ids), batch_size):
        batch = object_ids[i:i + batch_size]
        print(f"[SYNC] Procesando lote {i//batch_size + 1} de {tipo}s: {len(batch)} elementos")
        
        try:
            # Preparar requests para el batch
            batch_requests = []
            for idx, object_id in enumerate(batch):
                batch_requests.append({
                    "method": "GET",
                    "relative_url": f"{object_id}?fields=name"
                })
            
            # Hacer el batch request
            batch_url = "https://graph.facebook.com/v19.0/"
            batch_params = {
                "access_token": access_token,
                "batch": json.dumps(batch_requests)
            }
            
            import time
            max_retries = 3
            
            for attempt in range(max_retries + 1):
                try:
                    response = requests.post(batch_url, data=batch_params, timeout=10)  # Timeout reducido
                    
                    if response.status_code == 200:
                        batch_response = response.json()
                        
                        # Procesar respuestas del batch
                        for idx, resp in enumerate(batch_response):
                            object_id = batch[idx]
                            if resp.get('code') == 200:
                                try:
                                    body_data = json.loads(resp.get('body', '{}'))
                                    nombre = body_data.get('name', f"{tipo.title()} {object_id}")
                                    nombres[object_id] = nombre
                                except:
                                    nombres[object_id] = f"{tipo.title()} {object_id}"
                            else:
                                # Error individual en el objeto
                                nombres[object_id] = f"{tipo.title()} {object_id}"
                        break
                        
                    elif response.status_code == 429:  # Rate limit
                        if attempt < max_retries:
                            wait_time = min(5, 2 ** attempt)  # Máximo 5 segundos de espera
                            print(f"[WARN] Rate limit en batch {tipo}, esperando {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"[WARN] Rate limit persistente en batch {tipo}, usando nombres genéricos")
                            # Usar nombres genéricos para todo el batch
                            for object_id in batch:
                                nombres[object_id] = f"{tipo.title()} {object_id}"
                            break
                    else:
                        print(f"[WARN] Error {response.status_code} en batch {tipo}: {response.text}")
                        # Fallback: nombres por defecto
                        for object_id in batch:
                            nombres[object_id] = f"{tipo.title()} {object_id}"
                        break
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries:
                        print(f"[WARN] Timeout en batch {tipo}, reintentando...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"[WARN] Timeout persistente en batch {tipo}, usando nombres genéricos")
                        for object_id in batch:
                            nombres[object_id] = f"{tipo.title()} {object_id}"
                        break
                        
                except Exception as e:
                    if attempt < max_retries:
                        print(f"[WARN] Error en batch {tipo}: {e}, reintentando...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"[ERROR] Error persistente en batch {tipo}: {e}")
                        for object_id in batch:
                            nombres[object_id] = f"{tipo.title()} {object_id}"
                        break
        
        except Exception as e:
            print(f"[ERROR] Error crítico en batch {tipo}: {e}")
            # Fallback para todo el lote
            for object_id in batch:
                nombres[object_id] = f"{tipo.title()} {object_id}"
        
        # Pequeña pausa entre lotes para ser respetuosos con la API
        if i + batch_size < len(object_ids):
            time.sleep(0.5)
    
    print(f"[SYNC] Obtenidos {len(nombres)} nombres de {tipo}s exitosamente")
    return nombres

def obtener_nombre_de_id(object_id, access_token, tipo='campaign'):
    if not object_id:
        return None
    
    try:
        base_url = f"https://graph.facebook.com/v19.0/{object_id}"
        params = {
            'fields': 'name',
            'access_token': access_token
        }
        
        # Agregar timeout y reintentos
        import time
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                r = requests.get(base_url, params=params, timeout=10)  # Timeout de 10 segundos
                if r.status_code == 200:
                    data = r.json()
                    return data.get('name')
                elif r.status_code == 429:  # Rate limit
                    if attempt < max_retries:
                        print(f"[WARN] Rate limit alcanzado para {tipo} {object_id}, reintentando en 2s...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"[WARN] Rate limit persistente para {tipo} {object_id}")
                        return f"{tipo.title()} {object_id}"
                else:
                    print(f"[WARN] Error {r.status_code} obteniendo nombre de {tipo}: {object_id}")
                    return f"{tipo.title()} {object_id}"
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    print(f"[WARN] Timeout obteniendo {tipo} {object_id}, reintentando...")
                    time.sleep(1)
                    continue
                else:
                    print(f"[WARN] Timeout persistente para {tipo} {object_id}")
                    return f"{tipo.title()} {object_id}"
            except Exception as e:
                if attempt < max_retries:
                    print(f"[WARN] Error {e} obteniendo {tipo} {object_id}, reintentando...")
                    time.sleep(1)
                    continue
                else:
                    print(f"[WARN] Error persistente obteniendo {tipo} {object_id}: {e}")
                    return f"{tipo.title()} {object_id}"
        
        return f"{tipo.title()} {object_id}"
        
    except Exception as e:
        print(f"[ERROR] Error crítico obteniendo nombre de {tipo} {object_id}: {e}")
        return f"{tipo.title()} {object_id}"

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/compartir_reporte', methods=['POST'])
def compartir_reporte(nombre_nora):
    """
    Genera un link público para compartir un reporte específico con clientes.
    """
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        empresa_nombre = data.get('empresa_nombre', '')
        periodo = data.get('periodo', '')
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Verificar que el reporte existe
        reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
        if not reporte:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        # Generar token único para compartir
        import uuid
        import hashlib
        token = hashlib.sha256(f"{reporte_id}_{uuid.uuid4()}".encode()).hexdigest()[:32]
        
        # Guardar el token en una tabla de links compartidos (o usar el ID directamente por simplicidad)
        # Por ahora, usaremos el reporte_id directamente en la URL
        
        # Construir URL pública
        from flask import request as flask_request
        base_url = f"{flask_request.scheme}://{flask_request.host}"
        url_publico = f"{base_url}/reporte_publico/{reporte_id}?token={token}"
        
        # Opcional: Guardar el registro del share en base de datos
        try:
            supabase.table('meta_ads_reportes_compartidos').insert({
                'reporte_id': reporte_id,
                'token': token,
                'empresa_nombre': empresa_nombre,
                'periodo': periodo,
                'compartido_por': nombre_nora,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"[WARN] No se pudo guardar registro de compartir: {e}")
        
        return jsonify({
            'ok': True, 
            'url_publico': url_publico,
            'token': token,
            'reporte_id': reporte_id
        })
        
    except Exception as e:
        print(f"[ERROR] Error al compartir reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/descargar_reporte', methods=['POST'])
def descargar_reporte(nombre_nora):
    """
    Genera y descarga un reporte específico en formato Excel.
    """
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        formato = data.get('formato', 'excel')
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Obtener datos del reporte
        reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
        if not reporte:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        # Obtener anuncios detallados del mismo período y cuenta
        anuncios = supabase.table('meta_ads_anuncios_detalle') \
            .select('*') \
            .eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']) \
            .eq('fecha_inicio', reporte['fecha_inicio']) \
            .eq('fecha_fin', reporte['fecha_fin']) \
            .execute().data or []
        
        if formato == 'excel':
            # Generar archivo Excel
            import io
            import pandas as pd
            
            # Crear DataFrames
            df_resumen = pd.DataFrame([reporte])
            df_anuncios = pd.DataFrame(anuncios) if anuncios else pd.DataFrame()
            
            # Crear archivo Excel en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                if not df_anuncios.empty:
                    df_anuncios.to_excel(writer, sheet_name='Anuncios Detalle', index=False)
            
            output.seek(0)
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename=Meta_Ads_Reporte_{reporte_id}.xlsx'
                }
            )
        else:
            return jsonify({'ok': False, 'error': 'Formato no soportado'}), 400
            
    except Exception as e:
        print(f"[ERROR] Error al descargar reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@estadisticas_ads_bp.route('/panel_cliente/<nombre_nora>/meta_ads/estadisticas/actualizar_nombres_empresas', methods=['POST'])
def actualizar_nombres_empresas(nombre_nora):
    """
    Actualiza todos los reportes existentes para que tengan el nombre real de la empresa
    en lugar del nombre_cliente de la cuenta publicitaria.
    """
    try:
        print("🔄 Iniciando actualización de nombres de empresas en reportes...")
        
        # 1. Obtener todos los reportes
        reportes = supabase.table('meta_ads_reportes_semanales').select('*').execute().data or []
        print(f"📊 Reportes encontrados: {len(reportes)}")
        
        if not reportes:
            return jsonify({'ok': True, 'message': 'No hay reportes para actualizar', 'actualizados': 0})
        
        # 2. Obtener mapeo de empresas
        empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').execute().data or []
        empresas_map = {emp['id']: emp['nombre_empresa'] for emp in empresas}
        print(f"🏢 Empresas encontradas: {len(empresas)}")
        
        # 3. Actualizar cada reporte
        actualizados = 0
        errores = 0
        
        for reporte in reportes:
            reporte_id = reporte.get('id')
            empresa_id = reporte.get('empresa_id')
            empresa_nombre_actual = reporte.get('empresa_nombre', '')
            
            if not empresa_id:
                print(f"⚠️ Reporte {reporte_id}: Sin empresa_id")
                continue
                
            nombre_empresa_real = empresas_map.get(empresa_id)
            if not nombre_empresa_real:
                print(f"⚠️ Reporte {reporte_id}: Empresa ID {empresa_id} no encontrada")
                continue
                
            # Solo actualizar si el nombre es diferente
            if empresa_nombre_actual != nombre_empresa_real:
                try:
                    supabase.table('meta_ads_reportes_semanales').update({
                        'empresa_nombre': nombre_empresa_real
                    }).eq('id', reporte_id).execute()
                    
                    print(f"✅ Reporte {reporte_id}: '{empresa_nombre_actual}' → '{nombre_empresa_real}'")
                    actualizados += 1
                except Exception as e:
                    print(f"❌ Error al actualizar reporte {reporte_id}: {e}")
                    errores += 1
        
        print(f"📈 Resumen: Reportes actualizados: {actualizados}, Errores: {errores}")
        
        if actualizados > 0:
            return jsonify({
                'ok': True, 
                'message': f'Actualización completada. {actualizados} reportes actualizados.',
                'actualizados': actualizados,
                'errores': errores
            })
        else:
            return jsonify({
                'ok': True, 
                'message': 'No se requirieron actualizaciones. Los reportes ya tienen los nombres correctos.',
                'actualizados': 0,
                'errores': errores
            })
            
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500
