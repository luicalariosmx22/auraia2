# ✅ Archivo: clientes/aura/routes/panel_cliente_meta_ads/sincronizar.py
# 👉 Adaptamos el flujo para validar columnas dinámicas

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import json

from clientes.aura.tasks.meta_ads_sync_all import sincronizar_todo_meta_ads
from clientes.aura.routes.panel_cliente_meta_ads.utils.validar_columnas_meta_ads import limpiar_columnas_solicitadas, obtener_breakdowns

bp = Blueprint('sincronizar_meta_ads', __name__)

@bp.route('/sincronizar-meta-ads', methods=['GET', 'POST'])
def sincronizar_meta_ads():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        cuentas = request.form.get('cuentas')
        columnas = request.form.get('columnas')  # <- Aquí recibimos las columnas desde el frontend
        
        # Procesar fechas
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except Exception as e:
            flash(f'Error en formato de fechas: {e}', 'danger')
            return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

        # Procesar cuentas
        cuentas_list = [c.strip() for c in cuentas.split(',') if c.strip()] if cuentas else []

        # ✅ AQUI INTERCEPTAMOS EL PROBLEMA Y LO LIMPIAMOS
        columnas_list = [c.strip() for c in columnas.split(',') if c.strip()] if columnas else []
        columnas_validas = limpiar_columnas_solicitadas(columnas_list)
        breakdowns = obtener_breakdowns()

        # Token de entorno
        access_token = os.environ.get('META_ACCESS_TOKEN')
        if not access_token:
            flash('No se encontró META_ACCESS_TOKEN en variables de entorno.', 'danger')
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
            flash(f'Errores en la sincronización: {errores}', 'danger')
        else:
            flash(f'Sincronización exitosa para {procesados} cuentas.', 'success')

        return redirect(url_for('sincronizar_meta_ads.sincronizar_meta_ads'))

    # Carga inicial de columnas válidas al frontend
    variables_disponibles = sorted(list(limpiar_columnas_solicitadas(None)))
    return render_template('sincronizar_meta_ads.html', variables_disponibles=variables_disponibles)
