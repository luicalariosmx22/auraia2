# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_automatizaciones(11), meta_publicaciones_webhook(7), meta_anuncios_automatizados(10)

"""
Rutas para el panel de automatización de campañas
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from functools import wraps
from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_campanas import (
    obtener_automatizaciones,
    crear_automatizacion,
    actualizar_automatizacion,
    eliminar_automatizacion,
    obtener_estadisticas_automatizaciones,
    obtener_historial_anuncios_automatizados
)
from clientes.aura.utils.supabase_client import supabase

# Decorador simple para login (temporal)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Por ahora permitir todas las requests
        # Aquí puedes agregar tu lógica de autenticación
        return f(*args, **kwargs)
    return decorated_function

automatizacion_routes_bp = Blueprint(
    "automatizacion_routes_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/automatizacion_campanas"
)

def obtener_nombre_nora_desde_url():
    """Función para obtener nombre_nora desde la URL"""
    return request.view_args.get('nombre_nora', 'aura') if request.view_args else 'aura'

@automatizacion_routes_bp.route("/")
def panel_automatizacion(nombre_nora):
    """Página principal del panel de automatización"""
    try:
        # Obtener automatizaciones
        automatizaciones = obtener_automatizaciones(nombre_nora)
        
        # Obtener estadísticas
        estadisticas = obtener_estadisticas_automatizaciones(nombre_nora)
        
        # Obtener historial reciente
        historial = obtener_historial_anuncios_automatizados(nombre_nora, limite=10)
        
        # Obtener cuentas de Meta Ads disponibles
        cuentas_meta = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, nombre_cliente, empresa_id") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        return render_template(
            'panel_cliente_meta_ads/automatizacion.html',
            automatizaciones=automatizaciones,
            estadisticas=estadisticas,
            historial=historial,
            cuentas_meta=cuentas_meta.data or [],
            nombre_nora=nombre_nora
        )
    except Exception as e:
        print(f"Error en panel_automatizacion: {e}")
        return redirect(url_for('panel_cliente_meta_ads_bp.meta_ads_dashboard'))

@automatizacion_routes_bp.route('/automatizacion/crear', methods=['GET', 'POST'])
@login_required
def crear_automatizacion_view():
    """Crear nueva automatización"""
    nombre_nora = obtener_nombre_nora()
    
    if request.method == 'POST':
        try:
            datos = request.get_json()
            
            resultado = crear_automatizacion(nombre_nora, datos)
            
            if resultado['ok']:
                return jsonify({
                    'success': True,
                    'message': resultado['message'],
                    'automatizacion_id': resultado['automatizacion_id']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': resultado['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creando automatización: {str(e)}'
            }), 500
    
    # GET - Mostrar formulario
    try:
        # Obtener cuentas de Meta Ads
        cuentas_meta = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, nombre_cliente") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        # Obtener plantillas disponibles
        plantillas = supabase.table("meta_plantillas_anuncios") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activa", True) \
            .execute()
        
        return render_template(
            'panel_cliente_meta_ads/crear_automatizacion.html',
            cuentas_meta=cuentas_meta.data or [],
            plantillas=plantillas.data or [],
            nombre_nora=nombre_nora
        )
    except Exception as e:
        print(f"Error en crear_automatizacion_view: {e}")
        return redirect(url_for('automatizacion_routes_bp.panel_automatizacion'))

@automatizacion_routes_bp.route('/automatizacion/<int:automatizacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_automatizacion_view(automatizacion_id):
    """Editar automatización existente"""
    nombre_nora = obtener_nombre_nora()
    
    if request.method == 'POST':
        try:
            datos = request.get_json()
            
            resultado = actualizar_automatizacion(automatizacion_id, nombre_nora, datos)
            
            if resultado['ok']:
                return jsonify({
                    'success': True,
                    'message': resultado['message']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': resultado['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error actualizando automatización: {str(e)}'
            }), 500
    
    # GET - Mostrar formulario con datos existentes
    try:
        # Obtener automatización
        automatizacion = supabase.table("meta_ads_automatizaciones") \
            .select("*") \
            .eq("id", automatizacion_id) \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()
        
        if not automatizacion.data:
            return redirect(url_for('automatizacion_routes_bp.panel_automatizacion'))
        
        # Obtener cuentas y plantillas
        cuentas_meta = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, nombre_cliente") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        plantillas = supabase.table("meta_plantillas_anuncios") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activa", True) \
            .execute()
        
        return render_template(
            'panel_cliente_meta_ads/editar_automatizacion.html',
            automatizacion=automatizacion.data,
            cuentas_meta=cuentas_meta.data or [],
            plantillas=plantillas.data or [],
            nombre_nora=nombre_nora
        )
    except Exception as e:
        print(f"Error en editar_automatizacion_view: {e}")
        return redirect(url_for('automatizacion_routes_bp.panel_automatizacion'))

@automatizacion_routes_bp.route('/automatizacion/<int:automatizacion_id>/eliminar', methods=['DELETE'])
@login_required
def eliminar_automatizacion_view(automatizacion_id):
    """Eliminar automatización"""
    try:
        nombre_nora = obtener_nombre_nora()
        
        resultado = eliminar_automatizacion(automatizacion_id, nombre_nora)
        
        if resultado['ok']:
            return jsonify({
                'success': True,
                'message': resultado['message']
            })
        else:
            return jsonify({
                'success': False,
                'message': resultado['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error eliminando automatización: {str(e)}'
        }), 500

@automatizacion_routes_bp.route('/automatizacion/<int:automatizacion_id>/toggle', methods=['POST'])
@login_required
def toggle_automatizacion(automatizacion_id):
    """Activar/desactivar automatización"""
    try:
        nombre_nora = obtener_nombre_nora()
        datos = request.get_json()
        
        activa = datos.get('activa', False)
        
        resultado = actualizar_automatizacion(automatizacion_id, nombre_nora, {'activa': activa})
        
        if resultado['ok']:
            return jsonify({
                'success': True,
                'message': f'Automatización {"activada" if activa else "desactivada"} exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': resultado['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cambiando estado: {str(e)}'
        }), 500

@automatizacion_routes_bp.route('/automatizacion/historial')
@login_required
def historial_anuncios():
    """Página de historial de anuncios automatizados"""
    try:
        nombre_nora = obtener_nombre_nora()
        
        # Parámetros de paginación
        pagina = int(request.args.get('pagina', 1))
        limite = int(request.args.get('limite', 25))
        offset = (pagina - 1) * limite
        
        # Obtener historial completo
        historial = obtener_historial_anuncios_automatizados(nombre_nora, limite=limite)
        
        # Obtener estadísticas
        estadisticas = obtener_estadisticas_automatizaciones(nombre_nora)
        
        return render_template(
            'panel_cliente_meta_ads/historial_automatizacion.html',
            historial=historial,
            estadisticas=estadisticas,
            nombre_nora=nombre_nora,
            pagina_actual=pagina,
            limite=limite
        )
    except Exception as e:
        print(f"Error en historial_anuncios: {e}")
        return redirect(url_for('automatizacion_routes_bp.panel_automatizacion'))

@automatizacion_routes_bp.route('/api/automatizacion/estadisticas')
@login_required
def api_estadisticas_automatizacion():
    """API para obtener estadísticas de automatización"""
    try:
        nombre_nora = obtener_nombre_nora()
        estadisticas = obtener_estadisticas_automatizaciones(nombre_nora)
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }), 500

@automatizacion_routes_bp.route('/api/automatizacion/cuentas_meta')
@login_required
def api_cuentas_meta():
    """API para obtener cuentas de Meta Ads disponibles"""
    try:
        nombre_nora = obtener_nombre_nora()
        
        cuentas = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, nombre_cliente, empresa_id") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        return jsonify({
            'success': True,
            'cuentas': cuentas.data or []
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo cuentas: {str(e)}'
        }), 500

@automatizacion_routes_bp.route('/api/automatizacion/probar_webhook', methods=['POST'])
@login_required
def probar_webhook():
    """API para probar el procesamiento de webhook con datos simulados"""
    try:
        datos = request.get_json()
        
        # Datos de prueba para webhook
        webhook_test = {
            "entry": [
                {
                    "id": datos.get('page_id', '123456789'),
                    "changes": [
                        {
                            "field": "feed",
                            "value": {
                                "from": {
                                    "id": "user123",
                                    "name": "Usuario Prueba"
                                },
                                "item": "post",
                                "post_id": f"test_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                "verb": "add",
                                "created_time": int(datetime.now().timestamp()),
                                "message": datos.get('mensaje_prueba', "Esta es una publicación de prueba para automatización #test #promocion"),
                                "is_hidden": False
                            }
                        }
                    ],
                    "time": int(datetime.now().timestamp())
                }
            ],
            "object": "page"
        }
        
        # Procesar webhook de prueba
        from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_campanas import procesar_publicacion_webhook
        
        resultado = procesar_publicacion_webhook(webhook_test)
        
        return jsonify({
            'success': True,
            'resultado': resultado,
            'webhook_test': webhook_test
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error probando webhook: {str(e)}'
        }), 500
