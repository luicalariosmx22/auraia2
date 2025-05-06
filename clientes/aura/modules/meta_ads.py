# Archivo: clientes/aura/modules/meta_ads.py

from flask import Blueprint, render_template, session, redirect, url_for, current_app
from clientes.aura.utils.supabase import supabase
import requests
from datetime import datetime

ads_bp = Blueprint('ads_bp', __name__, url_prefix='/panel_cliente')

ACCESS_TOKEN_GLOBAL = 'TU_ACCESS_TOKEN_GLOBAL'  # ✅ Replace or load from .env in the future

@ads_bp.route('/<nombre_nora>/ads')
def panel_ads(nombre_nora):
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login'))

    # 🔎 Fetch the account associated with this Nora
    cuenta_resp = supabase.table('meta_ads_cuentas').select('*').eq('nombre_nora', nombre_nora).single().execute()
    cuenta = cuenta_resp.data if cuenta_resp.data else None

    campañas = []
    if cuenta and cuenta['conectada']:
        cuenta_id_meta = cuenta['id_cuenta_publicitaria']

        url = f"https://graph.facebook.com/v19.0/{cuenta_id_meta}/campaigns"
        params = {
            'fields': 'id,name,status,effective_status,daily_budget,insights{impressions,clicks,reach,spend,objective}',
            'access_token': ACCESS_TOKEN_GLOBAL
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            campañas = response.json().get('data', [])
            current_app.logger.info(f"[Meta Ads] Loaded {len(campañas)} campaigns for {nombre_nora}")

            # ✅ Update last synchronization
            supabase.table('meta_ads_cuentas').update({'ultima_sincron': datetime.utcnow()}).eq('id', cuenta['id']).execute()

        except Exception as e:
            current_app.logger.error(f"[Meta Ads] Error fetching campaigns: {str(e)}")

    # 📄 Load historical reports
    reportes_resp = supabase.table('meta_ads_reportes').select('*').eq('cuenta_id', cuenta['id'] if cuenta else -1).order('fecha_envio', desc=True).execute()
    reportes = reportes_resp.data if reportes_resp.data else []

    return render_template(
        'panel_cliente_ads.html',
        nombre_nora=nombre_nora,
        cuenta=cuenta,
        campañas=campañas,
        reportes=reportes
    )
