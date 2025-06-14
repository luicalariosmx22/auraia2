from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
from clientes.aura.tasks.meta_ads_sync_all import sincronizar_todo_meta_ads

bp = Blueprint('sincronizar_meta_ads', __name__)

@bp.route('/sincronizar-meta-ads', methods=['GET', 'POST'])
def sincronizar_meta_ads():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        cuentas = request.form.get('cuentas')
        variables = request.form.get('variables')
        # Procesar fechas
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except Exception as e:
            flash(f'Error en formato de fechas: {e}', 'danger')
            return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))
        # Procesar cuentas
        cuentas_list = [c.strip() for c in cuentas.split(',') if c.strip()] if cuentas else []
        # Procesar variables adicionales (JSON opcional)
        import json
        variables_dict = {}
        if variables:
            try:
                variables_dict = json.loads(variables)
            except Exception as e:
                flash(f'Variables adicionales no son JSON válido: {e}', 'danger')
                return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))
        # Token de entorno
        access_token = os.environ.get('META_ACCESS_TOKEN')
        if not access_token:
            flash('No se encontró META_ACCESS_TOKEN en variables de entorno.', 'danger')
            return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))
        # Lógica real de sincronización
        procesados = 0
        errores = []
        for cuenta_id in cuentas_list:
            try:
                sincronizar_todo_meta_ads(cuenta_id, access_token)
                procesados += 1
            except Exception as e:
                errores.append(f'Cuenta {cuenta_id}: {e}')
        if errores:
            flash(f'Errores en la sincronización: {errores}', 'danger')
        else:
            flash(f'Sincronización lanzada para {fecha_inicio} a {fecha_fin} en {procesados} cuentas.', 'success')
        return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))
    # Variables disponibles para sincronizar (puedes ajustar esta lista)
    variables_disponibles = ['impresiones', 'clics', 'mensajes', 'importe_gastado']
    return render_template('sincronizar_meta_ads.html', variables_disponibles=variables_disponibles)
