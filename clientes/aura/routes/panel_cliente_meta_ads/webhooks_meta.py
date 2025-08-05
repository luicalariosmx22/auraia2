from flask import Blueprint, request, jsonify
from datetime import datetime
from clientes.aura.utils.meta_webhook_helpers import registrar_evento_supabase, procesar_evento_audiencia, procesar_evento_anuncio

webhooks_meta_bp = Blueprint('webhooks_meta_bp', __name__)

@webhooks_meta_bp.route('/meta/webhook', methods=['GET'])
def verificar_token():
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == 'nora123':
        return challenge, 200
    return 'Token inválido', 403

@webhooks_meta_bp.route('/meta/webhook', methods=['POST'])
def recibir_webhook():
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "error", "message": "No payload"}), 400
            
        ahora = datetime.utcnow().isoformat()
        eventos_procesados = 0

        print(f"📥 Webhook recibido: {payload}")

        for entry in payload.get('entry', []):
            for cambio in entry.get('changes', []):
                objeto = cambio.get('field')  # Ej: 'account', 'audience', 'campaign'
                valor = cambio.get('value', {})
                objeto_id = valor.get('ad_account_id') or valor.get('campaign_id') or valor.get('ad_id') or valor.get('id')

                if not objeto or not objeto_id:
                    print(f"⚠️ Evento incompleto: objeto={objeto}, objeto_id={objeto_id}")
                    continue

                # Registrar evento base
                for campo, val in valor.items():
                    if registrar_evento_supabase(
                        objeto=objeto,
                        objeto_id=objeto_id,
                        campo=campo,
                        valor=val,
                        hora_evento=ahora
                    ):
                        eventos_procesados += 1

                # Procesamiento específico para audiencias
                if objeto == 'audience':
                    try:
                        procesar_evento_audiencia(objeto_id)
                        print(f"🎯 Evento de audiencia procesado: {objeto_id}")
                    except Exception as e:
                        print(f"⚠️ Error procesando audiencia {objeto_id}: {e}")
                
                # Procesamiento específico para anuncios
                elif objeto in ['ad', 'adset', 'campaign']:
                    try:
                        # Crear evento para procesar
                        evento_anuncio = {
                            'id': f"webhook_{objeto_id}_{ahora}",
                            'objeto_id': objeto_id,
                            'campo': 'webhook_update',
                            'valor': objeto,
                            'hora_evento': ahora
                        }
                        
                        procesar_evento_anuncio(evento_anuncio)
                        print(f"📢 Evento de anuncio procesado: {objeto_id}")
                    except Exception as e:
                        print(f"⚠️ Error procesando anuncio {objeto_id}: {e}")

        return jsonify({
            "status": "recibido",
            "eventos_procesados": eventos_procesados
        }), 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
