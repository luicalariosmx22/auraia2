from . import reportes_meta_ads_bp
from flask import render_template, request, redirect, url_for, flash
from clientes.aura.utils.supabase_client import supabase

@reportes_meta_ads_bp.route('/reportes', methods=['GET', 'POST'])
def vista_reportes_meta_ads(nombre_nora=None):
    if nombre_nora is None:
        nombre_nora = request.args.get('nombre_nora')
    cuentas_ads = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    reportes = supabase.table('meta_ads_reportes').select('*').eq('nombre_visible', nombre_nora).order('fecha_envio', desc=True).limit(30).execute().data or []
    if request.method == 'POST' and 'archivo_reporte' in request.files:
        archivo = request.files['archivo_reporte']
        if archivo.filename:
            flash('Reporte subido correctamente (lógica pendiente de implementar)', 'success')
            return redirect(url_for('reportes_meta_ads.vista_reportes_meta_ads', nombre_nora=nombre_nora))
    return render_template('reportes_meta_ads/reportes_meta_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads, reportes=reportes)
