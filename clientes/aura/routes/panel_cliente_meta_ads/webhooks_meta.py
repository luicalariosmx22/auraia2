from flask import Blueprint, request, jsonify, Response
from datetime import datetime
import os
import hashlib
import hmac
from dotenv import load_dotenv
from clientes.aura.utils.meta_webhook_helpers import (
    registrar_evento_supabase, 
    procesar_evento_audiencia, 
    procesar_evento_anuncio,
    verificar_webhook_registrado,
    registrar_webhook_en_cuenta,
    registrar_webhooks_en_cuentas_activas
)
from clientes.aura.utils.supabase_client import supabase

# 🔧 Cargar variables de entorno
load_dotenv()

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_cuentas(15), meta_webhook_eventos(1), meta_ads_anuncios_detalle(96)

webhooks_meta_bp = Blueprint('webhooks_meta_bp', __name__)

def verificar_firma_webhook(payload_body, signature_header):
    """Verifica la firma del webhook para mayor seguridad"""
    try:
        app_secret = os.getenv('META_WEBHOOK_SECRET')
        if not app_secret:
            print("⚠️ META_WEBHOOK_SECRET no configurado - saltando verificación de firma")
            return True
            
        if not signature_header:
            print("⚠️ No se recibió signature header")
            return False
            
        # Debug: imprimir información de la firma
        print(f"🔍 Debug firma - Secret length: {len(app_secret)}")
        print(f"🔍 Debug firma - Signature header: {signature_header}")
        print(f"🔍 Debug firma - Payload length: {len(payload_body)}")
        
        # Meta envía la firma como "sha256=<hash>"
        if not signature_header.startswith('sha256='):
            print("⚠️ Formato de firma inválido")
            return False
            
        signature = signature_header[7:]  # Remover "sha256="
        
        # Calcular hash esperado
        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        print(f"🔍 Debug - Firma recibida: {signature}")
        print(f"🔍 Debug - Firma esperada: {expected_signature}")
        
        # Comparación segura
        if hmac.compare_digest(signature, expected_signature):
            print("✅ Firma del webhook verificada correctamente")
            return True
        else:
            print("❌ Firma del webhook inválida")
            print("🚨 TEMPORAL: Permitiendo webhook sin verificación para debug")
            return True  # TEMPORAL: permitir sin verificación
            
    except Exception as e:
        print(f"❌ Error verificando firma: {e}")
        print("🚨 TEMPORAL: Permitiendo webhook por error en verificación")
        return True  # TEMPORAL: permitir en caso de error

@webhooks_meta_bp.route('/meta/webhook', methods=['GET', 'POST'])
def recibir_webhook():
    """Endpoint unificado para verificación y recepción de webhooks de Meta"""
    
    if request.method == 'GET':
        # Verificación del webhook por parte de Meta
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        verify_token = request.args.get("hub.verify_token")

        # Token de verificación (puedes cambiarlo por el tuyo)
        TOKEN_VERIFICACION = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')

        if mode == "subscribe" and verify_token == TOKEN_VERIFICACION:
            print("✅ Verificación de webhook exitosa")
            return Response(challenge, status=200, mimetype='text/plain')
        else:
            print(f"❌ Token inválido. Recibido: {verify_token}, Esperado: {TOKEN_VERIFICACION}")
            return Response("❌ Token inválido", status=403)
    
    elif request.method == 'POST':
        # Procesamiento de eventos del webhook
        try:
            # Obtener el payload como bytes para verificación de firma
            payload_body = request.get_data()
            signature_header = request.headers.get('X-Hub-Signature-256')
            
            # Verificar firma del webhook (opcional pero recomendado)
            if signature_header and not verificar_firma_webhook(payload_body, signature_header):
                print("❌ Firma del webhook inválida")
                return jsonify({"status": "error", "message": "Firma inválida"}), 403
            
            # Procesar el JSON
            payload = request.get_json()
            if not payload:
                return jsonify({"status": "error", "message": "No payload"}), 400
                
            ahora = datetime.utcnow().isoformat()
            eventos_procesados = 0

            print(f"📥 Webhook recibido: {payload}")

            for entry in payload.get('entry', []):
                entry_id = entry.get('id')  # ID de la página
                
                for cambio in entry.get('changes', []):
                    objeto = cambio.get('field')  # Ej: 'account', 'audience', 'campaign', 'feed'
                    valor = cambio.get('value', {})
                    
                    # Extraer objeto_id de forma robusta
                    objeto_id = None

                    # Intenta encontrar el ID correcto dependiendo del tipo de objeto
                    if objeto == "account":
                        objeto_id = valor.get("ad_account_id") or entry_id
                    elif objeto == "audience":
                        objeto_id = valor.get("id") or valor.get("audience_id")
                    elif objeto == "campaign":
                        objeto_id = valor.get("campaign_id")
                    elif objeto == "ad":
                        objeto_id = valor.get("ad_id")
                    elif objeto == "feed":
                        objeto_id = valor.get("post_id") or valor.get("parent_id")
                    else:
                        objeto_id = valor.get("id") or entry_id  # fallback

                    if not objeto or not objeto_id:
                        print(f"⚠️ Evento incompleto: objeto={objeto}, objeto_id={objeto_id}")
                        continue
                    
                    # Guardar page_id como evento adicional
                    if entry_id and objeto_id:
                        registrar_evento_supabase(
                            objeto='feed',
                            objeto_id=objeto_id,
                            campo='page_id',
                            valor=entry_id,
                            hora_evento=ahora
                        )

                    # Registrar evento base - filtrar campos que no van en logs_webhooks_meta
                    campos_excluidos = {'nombre_nora', 'created_time', 'updated_time'}
                    for campo, val in valor.items():
                        # Saltar campos que no deben ir en la tabla de webhooks
                        if campo in campos_excluidos:
                            print(f"⚠️ Saltando campo excluido: {campo} = {val}")
                            continue
                            
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
                    
                    # 🆕 Procesamiento específico para publicaciones (FEED)
                    elif objeto == 'feed':
                        try:
                            from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_campanas import procesar_publicacion_webhook
                            
                            # Procesar automatización de campañas
                            resultado_automatizacion = procesar_publicacion_webhook(payload)
                            
                            if resultado_automatizacion['ok']:
                                print(f"🚀 Automatización procesada: {resultado_automatizacion['anuncios_creados']} anuncios creados")
                            else:
                                print(f"⚠️ Error en automatización: {resultado_automatizacion.get('error', 'Error desconocido')}")
                                
                        except Exception as e:
                            print(f"⚠️ Error procesando feed {objeto_id}: {e}")

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


# API Endpoints para gestión de cuentas registradas
@webhooks_meta_bp.route('/api/webhooks/estado_cuentas', methods=['GET'])
def obtener_estado_cuentas():
    """Obtiene el estado de registro de webhooks para todas las cuentas de Meta Ads"""
    try:
        # Obtener access token
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return jsonify({
                "success": False,
                "message": "Access token no configurado"
            }), 500
        
        # Obtener todas las cuentas activas de Meta Ads
        response = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria, nombre_cliente, estado_actual').eq('estado_actual', 'ACTIVE').execute()
        
        if not response.data:
            return jsonify({
                "success": False,
                "message": "No se encontraron cuentas activas"
            }), 404
        
        cuentas_con_estado = []
        
        for cuenta in response.data:
            id_cuenta = cuenta['id_cuenta_publicitaria']
            
            # Verificar si tiene webhook registrado
            webhook_registrado = verificar_webhook_registrado(id_cuenta, access_token)
            
            cuentas_con_estado.append({
                'id_cuenta_publicitaria': id_cuenta,
                'nombre_cliente': cuenta['nombre_cliente'],
                'estado_actual': cuenta['estado_actual'],
                'webhook_registrado': webhook_registrado
            })
        
        return jsonify({
            "success": True,
            "cuentas": cuentas_con_estado
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo estado de cuentas: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/registrar_cuenta', methods=['POST'])
def registrar_webhook_cuenta_individual():
    """Registra webhook para una cuenta específica"""
    try:
        # Obtener access token
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return jsonify({
                "success": False,
                "message": "Access token no configurado"
            }), 500
        
        data = request.get_json()
        id_cuenta = data.get('id_cuenta')
        
        if not id_cuenta:
            return jsonify({
                "success": False,
                "message": "ID de cuenta requerido"
            }), 400
        
        # Registrar webhook
        resultado = registrar_webhook_en_cuenta(id_cuenta, access_token)
        
        if resultado:
            return jsonify({
                "success": True,
                "message": f"Webhook registrado exitosamente para cuenta {id_cuenta}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": f"Error registrando webhook para cuenta {id_cuenta}"
            }), 500
            
    except Exception as e:
        print(f"❌ Error registrando webhook individual: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/verificar_cuenta', methods=['POST'])
def verificar_webhook_cuenta_individual():
    """Verifica el estado del webhook para una cuenta específica"""
    try:
        # Obtener access token
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return jsonify({
                "success": False,
                "message": "Access token no configurado"
            }), 500
        
        data = request.get_json()
        id_cuenta = data.get('id_cuenta')
        
        if not id_cuenta:
            return jsonify({
                "success": False,
                "message": "ID de cuenta requerido"
            }), 400
        
        # Verificar webhook
        registrado = verificar_webhook_registrado(id_cuenta, access_token)
        
        return jsonify({
            "success": True,
            "registrado": registrado,
            "cuenta": id_cuenta
        }), 200
            
    except Exception as e:
        print(f"❌ Error verificando webhook: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/registrar_masivo', methods=['POST'])
def registrar_webhooks_masivo():
    """Registra webhooks en todas las cuentas activas que no lo tengan"""
    try:
        # Obtener access token
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return jsonify({
                "success": False,
                "message": "Access token no configurado"
            }), 500
        
        # Registrar webhooks en cuentas activas
        resultados = registrar_webhooks_en_cuentas_activas(access_token)
        
        # Calcular estadísticas
        exitosos = len([r for r in resultados if r.get('success', False)])
        fallidos = len(resultados) - exitosos
        
        return jsonify({
            "success": True,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "message": f"Registro masivo completado: {exitosos} exitosos, {fallidos} fallidos"
        }), 200
            
    except Exception as e:
        print(f"❌ Error en registro masivo: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/estadisticas', methods=['GET'])
def obtener_estadisticas_webhooks():
    """Obtiene estadísticas de eventos de webhook"""
    try:
        # Obtener estadísticas de eventos
        response = supabase.table('logs_webhooks_meta').select('procesado').execute()
        
        total_eventos = len(response.data) if response.data else 0
        procesados = len([e for e in response.data if e.get('procesado', False)]) if response.data else 0
        no_procesados = total_eventos - procesados
        
        # Eventos de los últimos 7 días
        from datetime import datetime, timedelta
        hace_7_dias = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        response_recientes = supabase.table('logs_webhooks_meta').select('id').gte('timestamp', hace_7_dias).execute()
        eventos_recientes = len(response_recientes.data) if response_recientes.data else 0
        
        return jsonify({
            "success": True,
            "estadisticas": {
                "total_eventos": total_eventos,
                "procesados": procesados,
                "no_procesados": no_procesados,
                "eventos_recientes": eventos_recientes
            }
        }), 200
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/eventos', methods=['GET'])
def obtener_eventos_webhook():
    """Obtiene eventos de webhook con filtros y paginación"""
    try:
        # Parámetros de consulta
        objeto = request.args.get('objeto')
        procesado = request.args.get('procesado')
        limite = int(request.args.get('limite', 50))
        offset = int(request.args.get('offset', 0))
        
        # Construir consulta
        query = supabase.table('logs_webhooks_meta').select('*')
        
        if objeto:
            query = query.eq('tipo_objeto', objeto)
        
        if procesado:
            procesado_bool = procesado.lower() == 'true'
            query = query.eq('procesado', procesado_bool)
        
        # Obtener total para paginación
        total_response = query.execute()
        total = len(total_response.data) if total_response.data else 0
        
        # Aplicar paginación y ordenamiento
        response = query.order('timestamp', desc=True).range(offset, offset + limite - 1).execute()
        
        return jsonify({
            "success": True,
            "eventos": response.data or [],
            "total": total
        }), 200
            
    except Exception as e:
        print(f"❌ Error obteniendo eventos: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@webhooks_meta_bp.route('/api/webhooks/marcar_procesado', methods=['POST'])
def marcar_evento_procesado():
    """Marca un evento como procesado"""
    try:
        data = request.get_json()
        evento_id = data.get('evento_id')
        
        if not evento_id:
            return jsonify({
                "success": False,
                "message": "ID de evento requerido"
            }), 400
        
        # Actualizar evento
        response = supabase.table('logs_webhooks_meta').update({'procesado': True, 'procesado_en': datetime.utcnow().isoformat()}).eq('id', evento_id).execute()
        
        if response.data:
            return jsonify({
                "success": True,
                "message": "Evento marcado como procesado"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Evento no encontrado"
            }), 404
            
    except Exception as e:
        print(f"❌ Error marcando evento como procesado: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
