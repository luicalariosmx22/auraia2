# Archivo: clientes/aura/routes/panel_cliente_ads.py

"""
✅ RUTA: Panel Cliente Ads
Este archivo se asegura que la vista de Ads funcione bien:
- Muestra TODAS las cuentas publicitarias de la Nora.
- Permite seleccionar una cuenta y ver las campañas + métricas.
- También lista los reportes históricos.

Este archivo DEBE estar en la carpeta routes (no en modules).
"""

from flask import Blueprint, render_template, request, current_app, jsonify
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
    return render_template('cuentas_publicitarias.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, moneda="MXN")

@panel_cliente_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/actualizar', methods=['POST'])
def actualizar_cuentas_publicitarias(nombre_nora):
    """
    Actualiza la información de las cuentas publicitarias activas desde la API de Meta Ads y sincroniza en Supabase.
    """
    from clientes.aura.utils.meta_ads import obtener_info_cuenta_ads
    cuentas = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    errores = []
    for cuenta in cuentas:
        cuenta_id = cuenta['id_cuenta_publicitaria']
        try:
            info = obtener_info_cuenta_ads(cuenta_id)  # Debe devolver dict con los datos actualizados
            update_data = {
                'nombre_cliente': info.get('nombre_cliente', cuenta['nombre_cliente']),
                'account_status': info.get('account_status', cuenta['account_status']),
                'ads_activos': info.get('ads_activos', cuenta.get('ads_activos')),
            }
            supabase.table('meta_ads_cuentas').update(update_data).eq('id_cuenta_publicitaria', cuenta_id).execute()
        except Exception as e:
            errores.append({'cuenta_id': cuenta_id, 'error': str(e)})
    if errores:
        return {'ok': False, 'errores': errores}, 207
    return {'ok': True}

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
