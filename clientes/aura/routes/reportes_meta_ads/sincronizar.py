from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import json

from clientes.aura.tasks.meta_ads_sync_all import sincronizar_todo_meta_ads
from clientes.aura.routes.reportes_meta_ads.utils.validar_columnas_meta_ads import limpiar_columnas_solicitadas, obtener_breakdowns

bp = Blueprint('sincronizar_meta_ads', __name__)

@bp.route('/sincronizar-meta-ads', methods=['GET', 'POST'])
def sincronizar_meta_ads():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        cuentas = request.form.get('cuentas')
        variables = request.form.get('variables')

        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except Exception as e:
            flash(f'Error en fechas: {e}', 'danger')
            return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

        cuentas_list = [c.strip() for c in cuentas.split(',') if c.strip()] if cuentas else []

        columnas_solicitadas = []
        if variables:
            try:
                columnas_solicitadas = json.loads(variables)
            except Exception as e:
                flash(f'Variables no son JSON válido: {e}', 'danger')
                return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

        columnas_validas = limpiar_columnas_solicitadas(columnas_solicitadas)
        breakdowns = obtener_breakdowns()

        access_token = os.environ.get('META_ACCESS_TOKEN')
        if not access_token:
            flash('No se encontró META_ACCESS_TOKEN.', 'danger')
            return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

        procesados, errores = 0, []
        for cuenta_id in cuentas_list:
            try:
                sincronizar_todo_meta_ads(
                    cuenta_id,
                    access_token,
                    fecha_inicio_dt,
                    fecha_fin_dt,
                    columnas_validas,
                    breakdowns
                )
                procesados += 1
            except Exception as e:
                errores.append(f'Cuenta {cuenta_id}: {e}')
        
        if errores:
            flash(f'Errores: {errores}', 'danger')
        else:
            flash(f'Sincronización lanzada para {fecha_inicio} a {fecha_fin} en {procesados} cuentas.', 'success')

        return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

    variables_disponibles = sorted(list(limpiar_columnas_solicitadas(None)))
    return render_template('sincronizar_meta_ads.html', variables_disponibles=variables_disponibles)
