# Archivo: clientes/aura/routes/reportes_meta_ads.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.meta_ads import listar_campañas_activas
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

reportes_meta_ads_bp = Blueprint('reportes_meta_ads', __name__)

# Todas las rutas asumen que el blueprint se registra con url_prefix=f"/panel_cliente/<nombre_nora>/meta_ads"

@reportes_meta_ads_bp.route('/reportes', methods=['GET', 'POST'])
def vista_reportes_meta_ads(nombre_nora=None):
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora') or request.args.get('nombre_nora')
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    # Carga de reportes históricos
    reportes = supabase.table('meta_ads_reportes').select('*').eq('nombre_visible', nombre_nora).order('fecha_envio', desc=True).limit(30).execute().data or []
    if request.method == 'POST' and 'archivo_reporte' in request.files:
        archivo = request.files['archivo_reporte']
        if archivo.filename:
            # Aquí puedes procesar el archivo y guardar el reporte manual
            flash('Reporte subido correctamente (lógica pendiente de implementar)', 'success')
            # TODO: Procesar archivo y guardar en meta_ads_reportes
            return redirect(url_for('reportes_meta_ads.vista_reportes_meta_ads', nombre_nora=nombre_nora))
    return render_template('reportes_meta_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, reportes=reportes)

@reportes_meta_ads_bp.route('/diseno_reporte', methods=['GET', 'POST'])
def vista_diseno_reporte(nombre_nora=None):
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora')
    print("DEBUG nombre_nora:", nombre_nora)
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_nora', nombre_nora).execute().data or []
    disenos_raw = supabase.table('meta_ads_disenos_reportes').select('*').eq('nombre_nora', nombre_nora).execute().data or []
    print("DEBUG disenos_raw:", disenos_raw)
    disenos = []
    for d in disenos_raw:
        d = dict(d)
        # Si variables es string, conviértelo a lista
        if isinstance(d.get('variables'), str):
            import json
            try:
                d['variables'] = json.loads(d['variables'])
            except Exception:
                d['variables'] = [d['variables']]
        elif d.get('variables') is None:
            d['variables'] = []
        disenos.append(d)
    print("DEBUG disenos procesados:", disenos)
    # Obtener variables tipo 'ads' y sus endpoints
    variables_raw = supabase.table('meta_variables').select('*').eq('tipo', 'ads').execute().data or []
    variables_disponibles = []
    for v in variables_raw:
        endpoints = supabase.table('meta_endpoints').select('*').eq('variable_id', v['id']).execute().data or []
        v['endpoints'] = endpoints
        variables_disponibles.append(v)
    return render_template('diseno_reporte_meta_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, disenos=disenos, variables_disponibles=variables_disponibles)

# Endpoint para guardar automatizaciones, variables, empresas, etc. (dummy)
@reportes_meta_ads_bp.route('/reportes/config', methods=['POST'])
def guardar_config_reportes():
    # Aquí recibes y guardas la configuración de automatizaciones, variables, empresas, etc.
    # request.form o request.json
    flash('Configuración guardada (lógica pendiente de implementar)', 'success')
    return ('', 204)

@reportes_meta_ads_bp.route('/diseno_reporte/guardar', methods=['POST'])
def guardar_diseno_reporte(nombre_nora=None):
    import json
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora')
    data = request.get_json(force=True) if request.is_json else request.form
    nombre_diseno = data.get('nombre_diseno')
    variables = data.get('variables')
    header_color = data.get('header_color', '#2563eb')
    bg_color = data.get('bg_color', '#f1f5f9')
    empresa_id = data.get('empresa_id')
    if not nombre_diseno or not variables:
        return {'ok': False, 'msg': 'Faltan datos'}, 400
    # Si variables viene como string, conviértelo a lista
    if isinstance(variables, str):
        try:
            variables = json.loads(variables)
        except Exception:
            variables = [variables]
    insert_data = {
        'nombre_nora': nombre_nora,
        'nombre_diseno': nombre_diseno,
        'variables': variables,
        'header_color': header_color,
        'bg_color': bg_color
    }
    if empresa_id:
        insert_data['empresa_id'] = empresa_id
    res = supabase.table('meta_ads_disenos_reportes').insert(insert_data).execute()
    if hasattr(res, 'data') and res.data:
        return {'ok': True, 'msg': 'Diseño guardado'}, 200
    elif isinstance(res, dict) and res.get('data'):
        return {'ok': True, 'msg': 'Diseño guardado'}, 200
    else:
        return {'ok': False, 'msg': f'Error al guardar: {getattr(res, "error", res)}'}, 500

@reportes_meta_ads_bp.route('/diseno_reporte/asignar', methods=['POST'])
def asignar_diseno_empresa():
    # nombre_nora = request.view_args.get('nombre_nora')  # Si lo necesitas
    data = request.json or request.form
    # Aquí deberías guardar la relación diseño <-> empresa/cuenta
    # Campos esperados: empresa_id, diseno_id
    # Lógica real pendiente de implementar
    return {'ok': True, 'msg': 'Diseño asignado (dummy)'}, 200

@reportes_meta_ads_bp.route('/diseno_reporte/base', methods=['GET'])
def diseno_reporte_base():
    # Base de diseño de reporte por default
    base_diseno = {
        'nombre_diseno': 'Base estándar',
        'variables': ['Impresiones', 'Clicks', 'Alcance', 'Costo por resultado', 'Frecuencia', 'Objetivo'],
        'header_color': '#2563eb',
        'bg_color': '#f1f5f9',
        'empresa_id': None
    }
    return base_diseno, 200

@reportes_meta_ads_bp.route('/reportes/data_empresa/<empresa_id>', methods=['GET'])
def data_empresa_para_reporte(empresa_id):
    nombre_nora = request.view_args.get('nombre_nora')
    # Devuelve info relevante de la empresa/cuenta para usar en el reporte
    empresa = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', empresa_id).single().execute().data
    if not empresa:
        return {'error': 'Empresa/cuenta no encontrada'}, 404
    # Puedes filtrar los campos que quieras mostrar en el reporte
    data = {
        'nombre_cliente': empresa.get('nombre_cliente'),
        'tipo_plataforma': empresa.get('tipo_plataforma'),
        'id_cuenta_publicitaria': empresa.get('id_cuenta_publicitaria'),
        'activo': empresa.get('activo'),
        'account_status': empresa.get('account_status'),
        # Agrega más campos relevantes aquí
    }
    return data, 200

@reportes_meta_ads_bp.route('/diseno_reporte/eliminar', methods=['POST'])
def eliminar_diseno_reporte(nombre_nora=None):
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora')
    data = request.get_json(force=True) if request.is_json else request.form
    diseno_id = data.get('diseno_id')
    if not diseno_id:
        return {'ok': False, 'msg': 'Falta diseno_id'}, 400
    try:
        res = supabase.table('meta_ads_disenos_reportes').delete().eq('id', diseno_id).execute()
        if hasattr(res, 'data') and res.data:
            return {'ok': True, 'msg': 'Diseño eliminado'}, 200
        elif isinstance(res, dict) and res.get('data'):
            return {'ok': True, 'msg': 'Diseño eliminado'}, 200
        else:
            return {'ok': False, 'msg': f'No se eliminó: {getattr(res, "error", res)}'}, 500
    except Exception as e:
        return {'ok': False, 'msg': f'Error: {str(e)}'}, 500

@reportes_meta_ads_bp.route('/api/cuentas_publicitarias', methods=['GET'])
def api_cuentas_publicitarias():
    nombre_nora = request.view_args.get('nombre_nora') or request.args.get('nombre_nora')
    if not nombre_nora:
        # Intentar obtener de sesión, cabecera o fallback
        nombre_nora = request.headers.get('X-Nombre-Nora')
    if not nombre_nora:
        return jsonify([])
    cuentas = supabase.table('meta_ads_cuentas').select('id, id_cuenta_publicitaria, nombre_cliente').eq('nombre_nora', nombre_nora).execute().data or []
    # Formato: id, nombre
    cuentas_fmt = [
        {'id': c.get('id') or c.get('id_cuenta_publicitaria'), 'nombre': c.get('nombre_cliente') or c.get('id_cuenta_publicitaria')} for c in cuentas
    ]
    return jsonify(cuentas_fmt)

@reportes_meta_ads_bp.route('/api/disenos/<diseno_id>/asignar_cuentas', methods=['POST'])
def api_asignar_cuentas_a_diseno(diseno_id):
    nombre_nora = request.view_args.get('nombre_nora') or request.args.get('nombre_nora')
    data = request.get_json(force=True) if request.is_json else request.form
    cuentas = data.get('cuentas')
    if isinstance(cuentas, str):
        import json
        try:
            cuentas = json.loads(cuentas)
        except Exception:
            cuentas = [cuentas]
    if not isinstance(cuentas, list):
        return jsonify({'ok': False, 'msg': 'Formato de cuentas inválido'}), 400
    # Guardar en campo cuentas_publicitarias (tipo lista/JSON)
    try:
        res = supabase.table('meta_ads_disenos_reportes').update({'cuentas_publicitarias': cuentas}).eq('id', diseno_id).execute()
        if hasattr(res, 'data') and res.data:
            return jsonify({'ok': True, 'msg': 'Cuentas asignadas'}), 200
        elif isinstance(res, dict) and res.get('data'):
            return jsonify({'ok': True, 'msg': 'Cuentas asignadas'}), 200
        else:
            return jsonify({'ok': False, 'msg': f'No se asignó: {getattr(res, "error", res)}'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Error: {str(e)}'}), 500

@reportes_meta_ads_bp.route('/campanas_activas', methods=['GET'])
def campanas_activas_meta_ads_vista(nombre_nora):
    cuenta_id = request.args.get('cuenta_id', '')
    return render_template('campanas_activas_meta_ads.html', nombre_nora=nombre_nora, cuenta_id=cuenta_id)

@reportes_meta_ads_bp.route('/campanas_activas_json', methods=['GET'])
def campanas_activas_meta_ads_json(nombre_nora):
    from clientes.aura.utils.supabase_client import supabase
    import requests, os
    cuenta_id = request.args.get('cuenta_id', '')
    since = request.args.get('since')
    until = request.args.get('until')
    if not cuenta_id:
        return jsonify({'ok': False, 'msg': 'Falta cuenta_id'}), 400
    # Buscar access_token de la cuenta SOLO si existe el campo
    # Si no existe, simplemente no lo uses
    try:
        # Si hay rango de fechas, consulta insights para cada campaña
        API_VER = "v19.0"
        TOKEN = os.getenv("META_ACCESS_TOKEN")
        BASE_URL = f"https://graph.facebook.com/{API_VER}"
        # 1. Obtener campañas activas
        url_camp = f"{BASE_URL}/act_{cuenta_id}/campaigns"
        params_camp = {
            "fields": "id,name,objective,effective_status,status",
            "limit": 50,
            "access_token": TOKEN
        }
        res = requests.get(url_camp, params=params_camp, timeout=30)
        res.raise_for_status()
        campanas = res.json().get("data", [])
        # 2. Para cada campaña, obtener el gasto en el rango si se pide
        if since and until:
            for c in campanas:
                url_insights = f"{BASE_URL}/{c['id']}/insights"
                params_insights = {
                    "fields": "campaign_id,campaign_name,spend",
                    "level": "campaign",
                    "time_range[since]": since,
                    "time_range[until]": until,
                    "access_token": TOKEN
                }
                r = requests.get(url_insights, params=params_insights, timeout=20)
                try:
                    r.raise_for_status()
                    data = r.json().get('data', [])
                    if data and 'spend' in data[0]:
                        c['insights'] = {"spend": data[0]['spend']}
                except Exception:
                    c['insights'] = {"spend": "0.00"}
        return jsonify({'ok': True, 'campanas': campanas}), 200
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Error: {str(e)}'}), 500

@reportes_meta_ads_bp.route('/cuenta_publicitaria_json', methods=['GET'])
def cuenta_publicitaria_json(nombre_nora):
    from clientes.aura.utils.supabase_client import supabase
    cuenta_id = request.args.get('cuenta_id', '')
    if not cuenta_id:
        return jsonify({'ok': False, 'msg': 'Falta cuenta_id'}), 400
    try:
        res = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).eq('nombre_nora', nombre_nora).limit(1).execute()
        if res.data and len(res.data) > 0:
            return jsonify({'ok': True, 'cuenta': res.data[0]})
        else:
            return jsonify({'ok': False, 'msg': 'No encontrada'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Error: {str(e)}'}), 500

@reportes_meta_ads_bp.route('/meta_ads_lab', methods=['GET'])
def meta_ads_lab(nombre_nora):
    # Determinar si el usuario es admin o super_admin
    es_admin = False
    from flask import session
    # Cambiar la lógica para usar session['is_admin']
    if session.get('is_admin'):
        es_admin = True
    return render_template('meta_ads_lab.html', nombre_nora=nombre_nora, es_admin=es_admin)

@reportes_meta_ads_bp.route('/meta_ads_lab_api', methods=['POST'])
def meta_ads_lab_api(nombre_nora):
    from clientes.aura.utils.meta_ads import _request
    data = request.get_json(force=True)
    edge = data.get('edge')
    params = data.get('params', {})
    try:
        result = _request(edge, params)
        return jsonify({'ok': True, 'result': result})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})

@reportes_meta_ads_bp.route('/meta_token_status', methods=['GET'])
def meta_token_status(nombre_nora=None):
    from clientes.aura.utils.meta_ads import get_token_status
    status = get_token_status()
    return jsonify(status)

@reportes_meta_ads_bp.route('/meta_token_debug', methods=['GET'])
def meta_token_debug(nombre_nora=None):
    import os
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        return {'defined': False, 'msg': 'META_ACCESS_TOKEN no definido'}
    return {
        'defined': True,
        'start': token[:6],
        'end': token[-6:],
        'length': len(token),
        'token': token  # ⚠️ Solo para debug temporal, eliminar después
    }

@reportes_meta_ads_bp.route('/meta_ai_qa', methods=['POST'])
def meta_ai_qa():
    """
    Endpoint para preguntas a la IA sobre variables Meta. Consulta la tabla meta_variables en Supabase y responde usando OpenAI, usando la lógica de handle_ai.
    """
    question = request.json.get('question', '').strip()
    if not question:
        return {'ok': False, 'msg': 'Pregunta vacía'}, 400
    # 1. Leer todas las variables de la tabla meta_variables
    try:
        variables = supabase.table('meta_variables').select('*').execute().data or []
    except Exception as e:
        return {'ok': False, 'msg': f'Error leyendo Supabase: {e}'}, 500
    # 2. Construir base de conocimiento para la IA
    base_conocimiento = []
    for v in variables:
        nombre = v.get('nombre', '')
        descripcion = v.get('descripcion', '')
        valor = v.get('valor', '')
        base_conocimiento.append({
            "contenido": f"Variable: {nombre}\nDescripción: {descripcion}\nValor actual: {valor}"
        })
    # 3. Usar manejar_respuesta_ai para obtener la respuesta
    respuesta, _ = manejar_respuesta_ai(
        mensaje_usuario=question,
        numero_nora=None,
        historial=None,
        prompt="Eres un experto en Meta Ads. Responde usando solo la información de las variables proporcionadas. Si la pregunta es sobre cómo armar una consulta, sugiere el edge y los parámetros adecuados.",
        base_conocimiento=base_conocimiento
    )
    return {'ok': True, 'answer': respuesta}

@reportes_meta_ads_bp.route('/meta_variables_import', methods=['POST'])
def meta_variables_import():
    """
    Endpoint para importar variables/permisos de Meta desde un link (ej: https://developers.facebook.com/docs/permissions#permissions).
    Recibe un link, extrae los permisos y descripciones, y los inserta en la tabla meta_variables.
    """
    import requests
    from bs4 import BeautifulSoup
    url = request.json.get('url', '').strip()
    if not url:
        return {'ok': False, 'msg': 'Falta el link'}, 400
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return {'ok': False, 'msg': f'Error al descargar la página: {resp.status_code}'}, 400
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Busca los permisos en <dl> (definición de lista)
        dl = soup.find('dl')
        if not dl:
            return {'ok': False, 'msg': 'No se encontró la lista de permisos (<dl>) en la página.'}, 400
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        if not dts or not dds or len(dts) != len(dds):
            return {'ok': False, 'msg': 'No se encontraron pares de permisos y descripciones.'}, 400
        variables = []
        for dt, dd in zip(dts, dds):
            nombre = dt.get_text(strip=True)
            descripcion = dd.get_text(strip=True)
            variables.append({
                'nombre': nombre,
                'descripcion': descripcion,
                'tipo': 'permission'
            })
        # Inserta en Supabase
        for var in variables:
            supabase.table('meta_variables').upsert(var, on_conflict=['nombre']).execute()
        return {'ok': True, 'msg': f'{len(variables)} variables importadas.'}
    except Exception as e:
        return {'ok': False, 'msg': f'Error: {e}'}, 500

@reportes_meta_ads_bp.route('/meta_variables_import_pdf', methods=['POST'])
def meta_variables_import_pdf():
    """
    Endpoint para importar variables/permisos de Meta desde un archivo PDF subido.
    Extrae los permisos y descripciones del PDF y los inserta en la tabla meta_variables.
    """
    import io
    import PyPDF2
    from flask import request
    file = request.files.get('pdf')
    if not file:
        return {'ok': False, 'msg': 'Falta el archivo PDF'}, 400
    try:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        # Busca líneas con formato: permiso\ndescripción\npermiso\ndescripción...
        import re
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        variables = []
        i = 0
        while i < len(lines) - 1:
            nombre = lines[i]
            descripcion = lines[i+1]
            # Heurística: el nombre del permiso suele ser una sola palabra sin espacios y en minúsculas
            if re.match(r'^[a-z_\.]+$', nombre) and len(descripcion) > 5:
                variables.append({'nombre': nombre, 'descripcion': descripcion, 'tipo': 'permission'})
                i += 2
            else:
                i += 1
        for var in variables:
            supabase.table('meta_variables').upsert(var, on_conflict=['nombre']).execute()
        return {'ok': True, 'msg': f'{len(variables)} variables importadas del PDF.'}
    except Exception as e:
        return {'ok': False, 'msg': f'Error: {e}'}, 500

@reportes_meta_ads_bp.route('/generate_meta_ads_report', methods=['POST'])
def generate_meta_ads_report():
    """
    Genera un reporte HTML de Meta Ads para una cuenta/campaña específica.
    Espera en el body: cuenta_id, variables (lista), rango de fechas opcional.
    Devuelve HTML listo para mostrar o descargar.
    """
    import datetime
    data = request.get_json(force=True)
    cuenta_id = data.get('cuenta_id')
    variables = data.get('variables', [])
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    if not cuenta_id or not variables:
        return {'ok': False, 'msg': 'Faltan cuenta_id o variables'}, 400

    # Obtener datos de la cuenta
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute().data
    if not cuenta:
        return {'ok': False, 'msg': 'Cuenta no encontrada'}, 404

    # Obtener campañas activas (o todas si se requiere)
    from clientes.aura.utils.meta_ads import listar_campañas_activas
    campañas = listar_campañas_activas(cuenta_id.replace('act_',''))

    # Filtrar por fechas si se proveen
    if fecha_inicio and fecha_fin:
        fi = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ff = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
        def en_rango(c):
            # Suponemos que hay un campo 'start_time' y 'stop_time' en la campaña
            try:
                st = datetime.datetime.strptime(c.get('start_time','1970-01-01'), '%Y-%m-%dT%H:%M:%S%z')
                et = datetime.datetime.strptime(c.get('stop_time','2100-01-01'), '%Y-%m-%dT%H:%M:%S%z')
                return st.date() <= ff.date() and et.date() >= fi.date()
            except Exception:
                return True
        campañas = [c for c in campañas if en_rango(c)]

    # Construir tabla HTML
    table_headers = ''.join(f'<th>{v}</th>' for v in variables)
    table_rows = ''
    for camp in campañas:
        row = ''
        for v in variables:
            val = camp.get(v.lower(), '')
            # Si la variable es insights, buscar dentro
            if not val and 'insights' in camp and v.lower() in camp['insights']:
                val = camp['insights'][v.lower()]
            row += f'<td>{val}</td>'
        table_rows += f'<tr>{row}</tr>'

    html = f'''
    <div class="p-6 bg-white rounded-xl shadow">
      <h2 class="text-2xl font-bold mb-4 text-blue-900">Reporte de Meta Ads</h2>
      <p class="mb-2"><b>Cliente:</b> {cuenta.get('nombre_cliente','')}</p>
      <p class="mb-2"><b>Cuenta:</b> {cuenta_id}</p>
      <table class="min-w-full border mt-4">
        <thead class="bg-blue-100">
          <tr>{table_headers}</tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
    '''
    return {'ok': True, 'html': html}
