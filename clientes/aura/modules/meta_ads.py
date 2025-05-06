# Archivo: clientes/aura/modules/meta_ads.py

from flask import Blueprint, render_template, jsonify
import requests
import os

meta_ads_bp = Blueprint('panel_cliente_meta_ads', __name__, template_folder='templates')

@meta_ads_bp.route('/')
def index_meta_ads():
    print("📥 [Meta Ads Module] Página principal accedida.")
    return render_template('panel_cliente_meta_ads.html')

@meta_ads_bp.route('/meta_ads/test', methods=['GET'])
def test_meta_ads():
    print("🧪 Ruta /test accedida.")
    token = os.getenv('META_ACCESS_TOKEN')
    cuenta_id = '721441716870946'  # ✅ Cuenta publicitaria ACTUALIZADA para la prueba

    url = f"https://graph.facebook.com/v19.0/{cuenta_id}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status',
        'access_token': token
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "response": response.text if 'response' in locals() else 'No response'
        })
