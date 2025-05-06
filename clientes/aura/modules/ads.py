from flask import Blueprint, render_template, jsonify, session, flash
from clientes.aura.utils.supabase import supabase  # ✅ Correct import
from flask import current_app
import requests

ads_bp = Blueprint('ads_bp', __name__, template_folder='templates')

# ✅ Ruta dinámica para cada Nora AI
@ads_bp.route('/panel_cliente/<nombre_nora>/ads')
def panel_cliente_ads(nombre_nora):
    print(f"📥 [Ads Module] Página principal accedida para Nora: {nombre_nora}")

    # Obtener la Nora actual desde la ruta dinámica
    session['nombre_nora'] = nombre_nora
    print(f"👤 Nora cargada: {nombre_nora}")

    # Variables para almacenar datos
    cuentas = []
    campañas_por_cuenta = []
    reportes = []

    try:
        # ✅ Obtener todas las cuentas publicitarias asociadas al nombre_nora
        cuentas_response = supabase.table('meta_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute()
        cuentas = cuentas_response.data if cuentas_response.data else []
        print(f"📊 Total de cuentas obtenidas: {len(cuentas)}")

        # ✅ Consultar campañas para cada cuenta conectada
        for cuenta in cuentas:
            campañas = []
            if cuenta.get('conectada') and cuenta.get('id_cuenta_publicitaria'):
                url = f"https://graph.facebook.com/v19.0/{cuenta['id_cuenta_publicitaria']}/campaigns"
                params = {
                    'fields': 'id,name,status,effective_status,daily_budget,insights{impressions,clicks,reach,spend,objective}',
                    'access_token': cuenta['access_token']  # 🔑 Usa el token propio de la cuenta
                }
                response = requests.get(url, params=params)
                print(f"🟢 [Meta API] URL consultada: {response.url}")
                try:
                    response.raise_for_status()
                    data_json = response.json()
                    print(f"🟢 [Meta API] Respuesta completa: {data_json}")
                    campañas = data_json.get('data', [])
                except Exception as e:
                    print(f"❌ [Meta API] Error: {str(e)}")
                    print(f"🔴 Respuesta de error: {response.text}")
            
            campañas_por_cuenta.append({
                'cuenta': cuenta,
                'campañas': campañas
            })

        # ✅ Obtener reportes históricos desde Supabase
        reportes_response = supabase.table('meta_ads_reportes').select('*').eq('nombre_visible', nombre_nora).order('fecha_envio', desc=True).limit(10).execute()
        reportes = reportes_response.data if reportes_response.data else []
        print(f"📄 Reportes históricos encontrados: {len(reportes)}")

    except Exception as e:
        current_app.logger.error(f"[Ads Module] Error al cargar datos: {str(e)}")
        flash("⚠️ Hubo un error al cargar los datos. Por favor, revisa los logs.", "warning")

    return render_template(
        'panel_cliente_ads.html',
        nombre_nora=nombre_nora,
        cuentas=cuentas,
        campañas_por_cuenta=campañas_por_cuenta,
        reportes=reportes
    )

# ✅ Ruta de prueba dinámica
@ads_bp.route('/panel_cliente/<nombre_nora>/ads/test')
def test_ads(nombre_nora):
    print(f"🧪 [Ads Module] Test route accedida para Nora: {nombre_nora}")
    return jsonify({"mensaje": f"Test exitoso para Nora: {nombre_nora} ✅"})
