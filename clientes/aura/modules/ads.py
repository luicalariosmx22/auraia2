from flask import Blueprint, render_template, jsonify, session
from clientes.aura.utils.supabase import supabase  # ✅ Correct import

ads_bp = Blueprint('ads_bp', __name__, template_folder='templates')

@ads_bp.route('/panel_cliente/ads/')
def index_ads():
    print("📥 [Ads Module] Página principal accedida.")

    # Obtener la Nora actual desde la sesión (o por defecto 'aura')
    nombre_nora = session.get("nombre_nora", "aura")
    print(f"👤 Nora cargada: {nombre_nora}")

    # 1️⃣ Obtener la cuenta publicitaria desde Supabase
    cuenta_response = supabase.table('meta_ads_cuentas').select('*').eq('nombre_nora', nombre_nora).limit(1).execute()
    cuenta = cuenta_response.data[0] if cuenta_response.data else None
    print(f"📊 Cuenta obtenida: {cuenta['nombre_cliente'] if cuenta else '❌ No encontrada'}")

    # 2️⃣ Obtener las campañas (si existe cuenta)
    campañas = []
    if cuenta:
        campañas_response = supabase.table('meta_ads_campañas').select('*').eq('cuenta_id', cuenta['id']).execute()
        campañas = campañas_response.data if campañas_response.data else []
        print(f"📢 Campañas encontradas: {len(campañas)}")

    # 3️⃣ Obtener los reportes históricos
    reportes_response = supabase.table('meta_ads_reportes').select('*').eq('cuenta_id', cuenta['id']).order('fecha_envio', desc=True).limit(10).execute() if cuenta else None
    reportes = reportes_response.data if reportes_response and reportes_response.data else []
    print(f"📄 Reportes encontrados: {len(reportes)}")

    return render_template(
        'panel_cliente_ads.html',  # ✅ Updated template
        nombre_nora=nombre_nora,
        cuenta=cuenta,
        campañas=campañas,
        reportes=reportes
    )

@ads_bp.route('/panel_cliente/ads/test')
def test_ads():
    print("🧪 [Ads Module] Test route accedida.")
    return jsonify({"mensaje": "Test exitoso ✅"})
