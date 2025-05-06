# Archivo: clientes/aura/routes/panel_cliente_meta_ads.py

"""
✅ RUTA: Panel Cliente Meta Ads
Este módulo permite al cliente:
- Ver su cuenta publicitaria y estado.
- Ver las campañas activas + métricas.
- Revisar el historial de reportes enviados.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from clientes.aura.utils.supabase_utils import get_supabase_client
from clientes.aura.modules.meta_ads import obtener_reporte_campanas, obtener_historial_reportes

panel_cliente_meta_ads_bp = Blueprint('panel_cliente_meta_ads', __name__)

@panel_cliente_meta_ads_bp.route('/panel_cliente/meta_ads/<nombre_nora>', methods=['GET'])
def panel_meta_ads(nombre_nora):
    supabase = get_supabase_client()
    # Obtener datos de la cuenta publicitaria
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('nombre_nora', nombre_nora).single().execute()
    cuenta_data = cuenta.data if cuenta.data else None

    # Obtener histórico de reportes enviados
    reportes = supabase.table('meta_ads_reportes').select('*').eq('nombre_nora', nombre_nora).order('fecha_envio', desc=True).execute()
    reportes_data = reportes.data if reportes.data else []

    # Consultar campañas si la cuenta está conectada
    campañas_data = []
    if cuenta_data and cuenta_data.get('id_cuenta_publicitaria') and cuenta_data.get('conectada') == True:
        campañas = obtener_reporte_campanas(
            cuenta_data['id_cuenta_publicitaria']
        )
        campañas_data = campañas if campañas else []

    return render_template(
        'panel_cliente_meta_ads.html',
        nombre_nora=nombre_nora,
        cuenta=cuenta_data,
        campañas=campañas_data,
        reportes=reportes_data
    )
