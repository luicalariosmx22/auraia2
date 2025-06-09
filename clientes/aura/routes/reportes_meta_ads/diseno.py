from . import reportes_meta_ads_bp
from flask import render_template, request
from clientes.aura.utils.supabase_client import supabase

@reportes_meta_ads_bp.route('/diseno_reporte', methods=['GET', 'POST'])
def vista_diseno_reporte(nombre_nora=None):
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora')
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_nora', nombre_nora).execute().data or []
    disenos_raw = supabase.table('meta_ads_disenos_reportes').select('*').eq('nombre_nora', nombre_nora).execute().data or []
    disenos = []
    for d in disenos_raw:
        d = dict(d)
        if isinstance(d.get('variables'), str):
            import json
            try:
                d['variables'] = json.loads(d['variables'])
            except Exception:
                d['variables'] = [d['variables']]
        elif d.get('variables') is None:
            d['variables'] = []
        disenos.append(d)
    variables_raw = supabase.table('meta_variables').select('*').eq('tipo', 'ads').execute().data or []
    variables_disponibles = []
    for v in variables_raw:
        endpoints = supabase.table('meta_endpoints').select('*').eq('variable_id', v['id']).execute().data or []
        v['endpoints'] = endpoints
        variables_disponibles.append(v)
    return render_template('reportes_meta_ads/diseno_reporte_meta_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, disenos=disenos, variables_disponibles=variables_disponibles)
