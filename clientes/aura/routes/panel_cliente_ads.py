# Archivo: clientes/aura/routes/panel_cliente_ads.py

"""
✅ RUTA: Panel Cliente Ads
Este archivo se asegura que la vista de Ads funcione bien:
- Muestra TODAS las cuentas publicitarias de la Nora.
- Permite seleccionar una cuenta y ver las campañas + métricas.
- También lista los reportes históricos.

Este archivo DEBE estar en la carpeta routes (no en modules).
"""

from flask import Blueprint, render_template, request
from clientes.aura.utils.supabase import supabase
from clientes.aura.modules.meta_ads import obtener_reporte_campanas

panel_cliente_ads_bp = Blueprint('panel_cliente_ads', __name__)

@panel_cliente_ads_bp.route('/panel_cliente/ads/<nombre_nora>', methods=['GET'])
def panel_ads(nombre_nora):
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
