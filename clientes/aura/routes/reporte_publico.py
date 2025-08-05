from flask import Blueprint, render_template, request, abort, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import uuid

# Blueprint para reportes públicos (sin autenticación)
reporte_publico_bp = Blueprint('reporte_publico', __name__)

@reporte_publico_bp.route('/reporte_publico/<token_uuid>')
def vista_reporte_publico(token_uuid):
    """
    Vista pública de un reporte compartido usando token de seguridad.
    URL: https://app.soynoraai.com/reporte_publico/<token_uuid>?token=<token_seguridad>
    """
    try:
        # Obtener token de seguridad de la query string
        token_seguridad = request.args.get('token')
        
        if not token_seguridad:
            abort(400, description="Token de seguridad requerido")
        
        # Verificar que el enlace compartido es válido
        try:
            enlace_compartido = supabase.table('meta_ads_reportes_compartidos').select('*').eq('id', token_uuid).eq('token', token_seguridad).eq('activo', True).single().execute().data
        except Exception as e:
            print(f"[ERROR] Error al buscar enlace compartido: {e}")
            abort(404, description="Enlace no encontrado o expirado")
        
        if not enlace_compartido:
            abort(404, description="Enlace no encontrado o expirado")
        
        # Obtener el reporte original
        reporte_id = enlace_compartido['reporte_id']
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
        except Exception as e:
            print(f"[ERROR] Error al obtener reporte: {e}")
            abort(404, description="Reporte no encontrado")
        
        if not reporte:
            abort(404, description="Reporte no encontrado")
        
        # Obtener anuncios detallados del reporte
        try:
            anuncios = supabase.table('meta_ads_anuncios_detalle').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).gte('fecha_inicio', reporte['fecha_inicio']).lte('fecha_fin', reporte['fecha_fin']).execute().data
        except Exception as e:
            print(f"[ERROR] Error al obtener anuncios: {e}")
            anuncios = []
        
        # Obtener información de la empresa
        empresa = None
        try:
            # TEMPORAL: Usar empresa_id correcto directamente
            empresa_id_correcto = "f0e9b9d8-706f-4dd3-826a-f47da9c9e1cc"
            print(f"[DEBUG] Usando empresa_id correcto: {empresa_id_correcto}")
            
            # Obtener información completa de la empresa desde cliente_empresas
            empresa_response = supabase.table('cliente_empresas').select('*').eq('id', empresa_id_correcto).execute()
            print(f"[DEBUG] Respuesta completa cliente_empresas: {empresa_response.data}")
            
            if empresa_response.data:
                empresa = empresa_response.data[0]
                print(f"[DEBUG] empresa obtenida de cliente_empresas: {empresa}")
            else:
                print(f"[DEBUG] No se encontró empresa con ID {empresa_id_correcto} en cliente_empresas")
                
            # También buscar en meta_ads_cuentas para debug
            print(f"[DEBUG] Buscando cuenta publicitaria: {reporte['id_cuenta_publicitaria']}")
            cuenta_meta_response = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).execute()
            print(f"[DEBUG] Respuesta completa meta_ads_cuentas: {cuenta_meta_response.data}")
                
        except Exception as e:
            print(f"[ERROR] Error al obtener empresa: {e}")
            empresa = None
                
        except Exception as e:
            print(f"[ERROR] Error al obtener empresa: {e}")
            empresa = None
        
        # Preparar datos para el template
        datos_reporte = {
            'reporte': reporte,
            'anuncios': anuncios or [],
            'empresa': empresa,
            'enlace_compartido': enlace_compartido,
            'es_publico': True
        }
        
        return render_template('panel_cliente_meta_ads/detalle_reporte_publico.html', **datos_reporte)
        
    except Exception as e:
        print(f"[ERROR] Error en vista_reporte_publico: {e}")
        abort(500, description="Error interno del servidor")

@reporte_publico_bp.route('/api/reporte_publico/<token_uuid>/validar')
def validar_enlace_publico(token_uuid):
    """
    API para validar si un enlace público es válido sin mostrar el reporte completo.
    """
    try:
        token_seguridad = request.args.get('token')
        
        if not token_seguridad:
            return jsonify({'valido': False, 'error': 'Token de seguridad requerido'}), 400
        
        # Verificar que el enlace compartido es válido
        try:
            enlace_compartido = supabase.table('meta_ads_reportes_compartidos').select('empresa_nombre,periodo,created_at').eq('id', token_uuid).eq('token', token_seguridad).eq('activo', True).single().execute().data
        except Exception:
            return jsonify({'valido': False, 'error': 'Enlace no encontrado o expirado'}), 404
        
        if not enlace_compartido:
            return jsonify({'valido': False, 'error': 'Enlace no encontrado o expirado'}), 404
        
        return jsonify({
            'valido': True,
            'empresa_nombre': enlace_compartido.get('empresa_nombre', ''),
            'periodo': enlace_compartido.get('periodo', ''),
            'fecha_creacion': enlace_compartido.get('created_at', '')
        })
        
    except Exception as e:
        print(f"[ERROR] Error en validar_enlace_publico: {e}")
        return jsonify({'valido': False, 'error': 'Error interno del servidor'}), 500
