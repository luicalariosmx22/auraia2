# Archivo: clientes/aura/routes/panel_cliente_ads.py

"""
✅ RUTA: Panel Cliente Ads
Este archivo se asegura que la vista de Ads funcione bien:
- Muestra TODAS las cuentas publicitarias de la Nora.
- Permite seleccionar una cuenta y ver las campañas + métricas.
- También lista los reportes históricos.

Este archivo DEBE estar en la carpeta routes (no en modules).
"""

from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.modules.meta_ads import obtener_reporte_campanas
from clientes.aura.utils.meta_ads import listar_campañas_activas   # 🆕 añadir
# Importa el blueprint de reportes avanzados para registrar en app principal
from clientes.aura.routes.reportes_meta_ads import reportes_meta_ads_bp
from clientes.aura.routes.campanas_meta_ads import campanas_meta_ads_bp

panel_cliente_ads_bp = Blueprint(
    'panel_cliente_ads',
    __name__
)

@panel_cliente_ads_bp.route('/', methods=['GET'])
def panel_ads(nombre_nora=None):
    if nombre_nora is None:
        # Extrae nombre_nora de la ruta Flask: /panel_cliente/<nombre_nora>/meta_ads
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = ''

    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []

    cuenta_id = request.args.get('cuenta')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    cuenta_seleccionada = None
    campañas_data = []

    if cuenta_id:
        cuenta_info = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute()
        if cuenta_info.data:
            cuenta_seleccionada = cuenta_info.data
            campañas = obtener_reporte_campanas(cuenta_id, fecha_inicio, fecha_fin)
            campañas_data = campañas if campañas else []

    reportes = supabase.table('meta_ads_reportes').select('*').eq('nombre_visible', nombre_nora).order('fecha_envio', desc=True).limit(10).execute()
    reportes_data = reportes.data if reportes.data else []

    return render_template(
        'panel_cliente_ads.html',
        nombre_nora=nombre_nora,
        nombre_visible=nombre_nora,
        cuentas_ads=cuentas_ads,
        cuenta_seleccionada=cuenta_seleccionada,
        campañas=campañas_data,
        reportes=reportes_data,
        moneda="MXN",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@panel_cliente_ads_bp.route('/agregar_cuenta/<nombre_nora>', methods=['POST'])
def agregar_cuenta(nombre_nora):
    nombre_cliente = request.form.get('nombre_cliente')
    tipo_plataforma = request.form.get('tipo_plataforma')
    id_cuenta_publicitaria = request.form.get('id_cuenta_publicitaria')
    activo = request.form.get('activo') == 'on'
    account_status = 1 if activo else 2
    data = {
        'nombre_cliente': nombre_cliente,
        'tipo_plataforma': tipo_plataforma,
        'id_cuenta_publicitaria': id_cuenta_publicitaria,
        'account_status': account_status,
        'activo': activo,
        'nombre_visible': nombre_nora
    }
    supabase.table('meta_ads_cuentas').insert(data).execute()
    return panel_ads(nombre_nora)

@panel_cliente_ads_bp.route('/reportes/<nombre_nora>', methods=['GET'])
def vista_reportes(nombre_nora):
    # Aquí puedes traer los datos de cuentas y reportes si lo deseas
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    return render_template('reportes_meta_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads)

@panel_cliente_ads_bp.route('/campanas/<nombre_nora>', methods=['GET'])
def vista_campanas(nombre_nora):
    # Vista avanzada de campañas
    return render_template('campanas_meta_ads.html', nombre_nora=nombre_nora)

@panel_cliente_ads_bp.get("/panel_cliente/<nombre_nora>/ads/campañas_activas")
def campañas_activas(nombre_nora):
    """
    Devuelve en JSON las campañas ACTIVAS de la cuenta que el cliente tenga
    asignada en la tabla `meta_ads_cuentas`.
    Si se pasa ?cuenta_id=... por query string, filtra solo esa cuenta.
    """
    cuenta_id = request.args.get('cuenta_id')
    if cuenta_id:
        # Buscar solo esa cuenta
        fila = supabase.table("meta_ads_cuentas") \
                   .select("id_cuenta_publicitaria") \
                   .eq("id_cuenta_publicitaria", cuenta_id) \
                   .eq("nombre_visible", nombre_nora) \
                   .single() \
                   .execute() \
                   .data
    else:
        # Buscar la cuenta principal ligada a la Nora
        fila = supabase.table("meta_ads_cuentas") \
                   .select("id_cuenta_publicitaria") \
                   .eq("nombre_visible", nombre_nora) \
                   .single() \
                   .execute() \
                   .data

    if not fila:
        return jsonify({"error": "Cuenta no encontrada"}), 404

    cuenta_id = fila["id_cuenta_publicitaria"]

    try:
        campañas = listar_campañas_activas(cuenta_id)
        return jsonify({"campañas": campañas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_cliente_ads_bp.route('/campanas_activas_meta_ads')
def campanas_activas_meta_ads():
    nombre_nora = request.args.get('nombre_nora', '')
    cuenta_id = request.args.get('cuenta_id', '')
    return render_template('campanas_activas_meta_ads.html', nombre_nora=nombre_nora, cuenta_id=cuenta_id)

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>', methods=['GET'])
def vista_cuentas_publicitarias(nombre_nora):
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    # Enriquecer con nombre de empresa
    for cuenta in cuentas_ads:
        empresa_id = cuenta.get('empresa_id')
        cuenta['empresa_nombre'] = None
        if empresa_id:
            empresa = supabase.table('cliente_empresas').select('nombre_empresa').eq('id', empresa_id).single().execute().data
            if empresa:
                cuenta['empresa_nombre'] = empresa.get('nombre_empresa')
    return render_template('cuentas_publicitarias.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, moneda="MXN")

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/actualizar', methods=['POST'])
def actualizar_cuentas_publicitarias(nombre_nora):
    print(f"[DEBUG] Iniciando actualización de cuentas publicitarias para Nora: {nombre_nora}")
    from clientes.aura.utils.meta_ads import obtener_info_cuenta_ads
    cuentas = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    print(f"[DEBUG] Cuentas encontradas: {len(cuentas)}")
    errores = []
    cuentas_actualizadas = []
    for cuenta in cuentas:
        cuenta_id = cuenta['id_cuenta_publicitaria']
        print(f"[DEBUG] Actualizando cuenta: {cuenta_id}")
        try:
            info = obtener_info_cuenta_ads(cuenta_id)  # Debe devolver dict con los datos actualizados
            print(f"[DEBUG] Info obtenida de Meta API para {cuenta_id}: {info}")
            update_data = {
                'nombre_cliente': info.get('nombre_cliente', cuenta['nombre_cliente']),
                'account_status': info.get('account_status', cuenta['account_status']),
                'ads_activos': info.get('ads_activos', cuenta.get('ads_activos')),
            }
            # Fallback si nombre_cliente viene vacío
            if not update_data['nombre_cliente']:
                update_data['nombre_cliente'] = 'Sin nombre'
            print(f"[DEBUG] Datos a actualizar en Supabase para {cuenta_id}: {update_data}")
            resp_update = supabase.table('meta_ads_cuentas').update(update_data).eq('id_cuenta_publicitaria', cuenta_id).execute()
            print(f"[DEBUG] Respuesta de update Supabase para {cuenta_id}: {resp_update}")
            cuentas_actualizadas.append({
                'id_cuenta_publicitaria': cuenta_id,
                'ads_activos': update_data['ads_activos'],
                'nombre_cliente': update_data['nombre_cliente']
            })
        except Exception as e:
            print(f"[ERROR] Error actualizando cuenta {cuenta_id}: {e}")
            errores.append({'cuenta_id': cuenta_id, 'error': str(e)})
    if errores:
        print(f"[DEBUG] Errores encontrados: {errores}")
        return {'ok': False, 'errores': errores, 'cuentas': cuentas_actualizadas}, 207
    print("[DEBUG] Actualización de cuentas publicitarias finalizada correctamente.")
    return {'ok': True, 'cuentas': cuentas_actualizadas}

@panel_cliente_ads_bp.route('/meta_ads/anuncios_activos_json')
def anuncios_activos_json():
    """
    Devuelve en JSON los anuncios ACTIVOS de la cuenta seleccionada (por cuenta_id).
    """
    from clientes.aura.utils.meta_ads import listar_anuncios_activos
    cuenta_id = request.args.get('cuenta_id')
    if not cuenta_id:
        return jsonify({"error": "Falta cuenta_id"}), 400
    try:
        anuncios = listar_anuncios_activos(cuenta_id)
        return jsonify({"anuncios": anuncios})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/importar_desde_meta', methods=['POST'])
def importar_cuentas_desde_meta(nombre_nora):
    """
    Consulta la API de Meta con el token global y agrega todas las cuentas publicitarias asociadas al usuario,
    insertando solo las que no existan aún en Supabase para la Nora.
    """
    import os
    import requests
    from clientes.aura.utils.supabase_client import supabase
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        return jsonify({'ok': False, 'msg': 'No se encontró el token de Meta.'}), 400
    url = f"https://graph.facebook.com/v19.0/me/adaccounts"
    params = {
        "fields": "id,account_id,name,account_status",
        "access_token": token
    }
    cuentas = []
    try:
        while url:
            resp = requests.get(url, params=params if '?' not in url else None, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            cuentas.extend(data.get('data', []))
            # Paginación: si hay siguiente página, seguir
            paging = data.get('paging', {})
            url = paging.get('next')
            params = None  # Solo en la primera petición se usan params
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Error consultando Meta: {e}'}), 500
    # Buscar cuentas ya existentes para la Nora
    existentes = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria').eq('nombre_visible', nombre_nora).execute().data or []
    existentes_ids = {c['id_cuenta_publicitaria'] for c in existentes}
    nuevas = []
    for acc in cuentas:
        id_publicitaria = acc.get('account_id')
        if not id_publicitaria or id_publicitaria in existentes_ids:
            continue
        data = {
            'id_cuenta_publicitaria': id_publicitaria,
            'nombre_cliente': acc.get('name', ''),
            'nombre_visible': nombre_nora,
            'conectada': True,
            'account_status': acc.get('account_status', 0)
        }
        nuevas.append(data)
    if nuevas:
        supabase.table('meta_ads_cuentas').insert(nuevas).execute()
    return jsonify({'ok': True, 'agregadas': len(nuevas), 'total': len(cuentas)})

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/<cuenta_id>/vincular_empresa', methods=['GET', 'POST'])
def vincular_empresa_a_cuenta(nombre_nora, cuenta_id):
    from flask import render_template, request, redirect, url_for
    # Obtener la cuenta
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute().data
    if not cuenta:
        return "Cuenta publicitaria no encontrada", 404
    # Obtener empresas disponibles para la Nora
    empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        if not empresa_id:
            return render_template('vincular_empresa_cuenta.html', cuenta=cuenta, empresas=empresas, nombre_nora=nombre_nora, error='Debes seleccionar una empresa')
        # Actualizar la cuenta con el empresa_id
        supabase.table('meta_ads_cuentas').update({'empresa_id': empresa_id}).eq('id_cuenta_publicitaria', cuenta_id).execute()
        return redirect(url_for('panel_cliente_ads.vista_cuentas_publicitarias', nombre_nora=nombre_nora))
    return render_template('vincular_empresa_cuenta.html', cuenta=cuenta, empresas=empresas, nombre_nora=nombre_nora)

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/<cuenta_id>/ads_activos', methods=['GET'])
def obtener_ads_activos_endpoint(nombre_nora, cuenta_id):
    from clientes.aura.utils.meta_ads import obtener_ads_activos_cuenta
    activos = obtener_ads_activos_cuenta(cuenta_id)
    print(f"[DEBUG] Ads activos para cuenta {cuenta_id}: {activos}")  # Debug agregado
    # Actualiza el campo en Supabase
    supabase.table('meta_ads_cuentas').update({'ads_activos': activos}).eq('id_cuenta_publicitaria', cuenta_id).execute()
    return jsonify({'ok': True, 'ads_activos': activos})

@panel_cliente_ads_bp.route('/cuenta/<cuenta_id>', methods=['GET'])
def ficha_cuenta_publicitaria(cuenta_id):
    nombre_nora = request.args.get('nombre_nora') or ''
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute().data
    if not cuenta:
        return redirect(url_for('panel_cliente_ads.vista_cuentas_publicitarias', nombre_nora=nombre_nora))
    # Enriquecer con nombre y logo de empresa si está vinculada
    empresa_id = cuenta.get('empresa_id')
    cuenta['empresa_nombre'] = None
    cuenta['empresa_logo_url'] = None
    if empresa_id:
        empresa = supabase.table('cliente_empresas').select('nombre_empresa,logo_url').eq('id', empresa_id).single().execute().data
        if empresa:
            cuenta['empresa_nombre'] = empresa.get('nombre_empresa')
            cuenta['empresa_logo_url'] = empresa.get('logo_url')
    from datetime import datetime, timedelta
    hoy = datetime.utcnow().date()
    hace_7 = hoy - timedelta(days=7)
    # Traer todos los reportes de los últimos 7 días para la cuenta
    reportes_7d = supabase.table('meta_ads_reportes') \
        .select('campana_id,conjunto_id,anuncio_id,importe_gastado') \
        .gte('fecha_envio', hace_7.isoformat()) \
        .lte('fecha_envio', hoy.isoformat()) \
        .eq('id_cuenta_publicitaria', cuenta_id) \
        .execute().data or []
    # Campañas
    campanas = supabase.table('meta_ads_campañas').select('campana_id,nombre_campana').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    campanas_dict = {}
    for row in reportes_7d:
        cid = row.get('campana_id')
        if cid:
            campanas_dict.setdefault(cid, 0)
            campanas_dict[cid] += row.get('importe_gastado', 0) or 0
    campanas_filtradas = []
    for c in campanas:
        gasto_7d = round(campanas_dict.get(c['campana_id'], 0), 2)
        if gasto_7d > 0:
            c['gasto_7d'] = gasto_7d
            campanas_filtradas.append(c)
    # Conjuntos de anuncios
    conjuntos = supabase.table('meta_ads_conjuntos').select('conjunto_id,nombre_conjunto').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    conjuntos_dict = {}
    for row in reportes_7d:
        coid = row.get('conjunto_id')
        if coid:
            conjuntos_dict.setdefault(coid, 0)
            conjuntos_dict[coid] += row.get('importe_gastado', 0) or 0
    conjuntos_filtrados = []
    for c in conjuntos:
        gasto_7d = round(conjuntos_dict.get(c['conjunto_id'], 0), 2)
        if gasto_7d > 0:
            c['gasto_7d'] = gasto_7d
            conjuntos_filtrados.append(c)
    # Anuncios
    anuncios = supabase.table('meta_ads_anuncios').select('anuncio_id,nombre_anuncio').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    anuncios_dict = {}
    for row in reportes_7d:
        aid = row.get('anuncio_id')
        if aid:
            anuncios_dict.setdefault(aid, 0)
            anuncios_dict[aid] += row.get('importe_gastado', 0) or 0
    anuncios_filtrados = []
    for a in anuncios:
        gasto_7d = round(anuncios_dict.get(a['anuncio_id'], 0), 2)
        if gasto_7d > 0:
            a['gasto_7d'] = gasto_7d
            anuncios_filtrados.append(a)
    return render_template(
        'meta_ads_cuenta_ficha.html',
        cuenta=cuenta,
        nombre_nora=nombre_nora,
        campanas=campanas_filtradas,
        conjuntos=conjuntos_filtrados,
        anuncios=anuncios_filtrados
    )
