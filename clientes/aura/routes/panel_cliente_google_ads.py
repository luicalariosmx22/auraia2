from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for
from clientes.aura.utils.supabase_client import supabase

panel_cliente_google_ads_bp = Blueprint(
    'panel_cliente_google_ads',
    __name__
)

# --- SOLO UNA DEFINICIÓN DEL BLUEPRINT Y LOS IMPORTS ---

@panel_cliente_google_ads_bp.route('/<nombre_nora>/sincronizar_anuncios_mcc', methods=['GET'])
def sincronizar_anuncios_mcc(nombre_nora):
    """
    Sincroniza y guarda en Supabase todos los anuncios con métricas reales de SOLO las cuentas que realmente están en el MCC para la Nora.
    """
    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        cuentas_mcc = service.listar_cuentas_mcc()
        cuentas_mcc = [c for c in cuentas_mcc if c.get('accesible', True)]
        total_anuncios_insertados = 0
        errores = []
        
        print(f"[INFO] 🚀 Iniciando sincronización con métricas para {len(cuentas_mcc)} cuentas")
        
        for cuenta in cuentas_mcc:
            customer_id = cuenta['customer_id']
            nombre_cliente = cuenta.get('nombre_cliente', '')
            
            # Obtener empresa_id de la base de datos
            try:
                cuenta_bd = supabase.table('google_ads_cuentas').select('empresa_id').eq('customer_id', customer_id).eq('nombre_visible', nombre_nora).single().execute().data
                empresa_id = cuenta_bd.get('empresa_id') if cuenta_bd else None
            except:
                empresa_id = None
                print(f"[WARNING] No se encontró empresa_id para cuenta {customer_id}")
            
            try:
                # Usar la nueva función con métricas reales (últimos 30 días)
                anuncios = service.obtener_anuncios_con_metricas(customer_id, periodo_dias=30)
                print(f"[DEBUG] Anuncios con métricas obtenidos para la cuenta {customer_id}: {len(anuncios)} anuncios")
                
                if not anuncios:
                    print(f"[INFO] No hay anuncios con métricas para la cuenta {customer_id}")
                    continue
                    
                for anuncio in anuncios:
                    reporte_data = {
                        'estado_anuncio': anuncio.get('estado_anuncio'),
                        'url_final': anuncio.get('url_final'),
                        'titulo_1': anuncio.get('titulo_1'),
                        'pos_titulo_1': anuncio.get('pos_titulo_1'),
                        'titulo_2': anuncio.get('titulo_2'),
                        'pos_titulo_2': anuncio.get('pos_titulo_2'),
                        'titulo_3': anuncio.get('titulo_3'),
                        'pos_titulo_3': anuncio.get('pos_titulo_3'),
                        'titulo_4': anuncio.get('titulo_4'),
                        'pos_titulo_4': anuncio.get('pos_titulo_4'),
                        'titulo_5': anuncio.get('titulo_5'),
                        'pos_titulo_5': anuncio.get('pos_titulo_5'),
                        'titulo_6': anuncio.get('titulo_6'),
                        'pos_titulo_6': anuncio.get('pos_titulo_6'),
                        'titulo_7': anuncio.get('titulo_7'),
                        'pos_titulo_7': anuncio.get('pos_titulo_7'),
                        'titulo_8': anuncio.get('titulo_8'),
                        'pos_titulo_8': anuncio.get('pos_titulo_8'),
                        'titulo_9': anuncio.get('titulo_9'),
                        'pos_titulo_9': anuncio.get('pos_titulo_9'),
                        'titulo_10': anuncio.get('titulo_10'),
                        'pos_titulo_10': anuncio.get('pos_titulo_10'),
                        'titulo_11': anuncio.get('titulo_11'),
                        'pos_titulo_11': anuncio.get('pos_titulo_11'),
                        'titulo_12': anuncio.get('titulo_12'),
                        'pos_titulo_12': anuncio.get('pos_titulo_12'),
                        'titulo_13': anuncio.get('titulo_13'),
                        'pos_titulo_13': anuncio.get('pos_titulo_13'),
                        'titulo_14': anuncio.get('titulo_14'),
                        'pos_titulo_14': anuncio.get('pos_titulo_14'),
                        'titulo_15': anuncio.get('titulo_15'),
                        'pos_titulo_15': anuncio.get('pos_titulo_15'),
                        'descripcion_1': anuncio.get('descripcion_1'),
                        'pos_desc_1': anuncio.get('pos_desc_1'),
                        'descripcion_2': anuncio.get('descripcion_2'),
                        'pos_desc_2': anuncio.get('pos_desc_2'),
                        'descripcion_3': anuncio.get('descripcion_3'),
                        'pos_desc_3': anuncio.get('pos_desc_3'),
                        'descripcion_4': anuncio.get('descripcion_4'),
                        'pos_desc_4': anuncio.get('pos_desc_4'),
                        'ruta_1': anuncio.get('ruta_1'),
                        'ruta_2': anuncio.get('ruta_2'),
                        'url_final_movil': anuncio.get('url_final_movil'),
                        'plantilla_seguimiento': anuncio.get('plantilla_seguimiento'),
                        'sufijo_url_final': anuncio.get('sufijo_url_final'),
                        'param_personalizado': anuncio.get('param_personalizado'),
                        'campaña': anuncio.get('campaña'),
                        'grupo_anuncios': anuncio.get('grupo_anuncios'),
                        'estado': anuncio.get('estado'),
                        'motivos_estado': anuncio.get('motivos_estado'),
                        'calidad_anuncio': anuncio.get('calidad_anuncio'),
                        'mejoras_efectividad': anuncio.get('mejoras_efectividad'),
                        'tipo_anuncio': anuncio.get('tipo_anuncio'),
                        'clics': anuncio.get('clics'),
                        'impresiones': anuncio.get('impresiones'),
                        'ctr': anuncio.get('ctr'),
                        'codigo_moneda': anuncio.get('codigo_moneda'),
                        'cpc_promedio': anuncio.get('cpc_promedio'),
                        'costo': anuncio.get('costo'),
                        'porcentaje_conversion': anuncio.get('porcentaje_conversion'),
                        'conversiones': anuncio.get('conversiones'),
                        'costo_por_conversion': anuncio.get('costo_por_conversion'),
                        'id_campaña': str(anuncio.get('id_campaña')) if anuncio.get('id_campaña') else None,
                        'id_grupo_anuncios': str(anuncio.get('id_grupo_anuncios')) if anuncio.get('id_grupo_anuncios') else None,
                        'id_anuncio': str(anuncio.get('id_anuncio')) if anuncio.get('id_anuncio') else None,
                        'customer_id': anuncio.get('customer_id'),  # Incluir customer_id
                        'nombre_nora': nombre_nora,
                        'empresa_id': empresa_id
                    }
                    
                    try:
                        # Usar upsert para evitar duplicados basado en id_anuncio
                        result = supabase.table('google_ads_reporte_anuncios').upsert(
                            reporte_data, 
                            on_conflict='id_anuncio'
                        ).execute()
                        
                        total_anuncios_insertados += 1
                        # Mostrar métricas para verificar datos reales
                        if anuncio.get('impresiones', 0) > 0 or anuncio.get('clics', 0) > 0:
                            print(f"[SUCCESS] ✅ Anuncio {anuncio.get('id_anuncio')} con métricas: {anuncio.get('impresiones')} imp, {anuncio.get('clics')} clics")
                        else:
                            print(f"[SUCCESS] ✅ Anuncio {anuncio.get('id_anuncio')} sin métricas (insertado)")
                            
                    except Exception as e:
                        print(f"[ERROR] Error insertando reporte anuncio {anuncio.get('id_anuncio')} de {customer_id}: {e}")
                        errores.append(f"Cuenta {customer_id} anuncio {anuncio.get('id_anuncio')}: {e}")
                        
            except Exception as e:
                print(f"[ERROR] Error obteniendo anuncios para la cuenta {customer_id}: {e}")
                errores.append(f"Cuenta {customer_id}: {e}")
                
        print(f"[INFO] 🎉 Sincronización completada: {total_anuncios_insertados} anuncios procesados")
        return jsonify({
            'ok': True, 
            'anuncios_insertados': total_anuncios_insertados, 
            'errores': errores, 
            'cuentas': len(cuentas_mcc),
            'mensaje': f'Sincronización con métricas completada: {total_anuncios_insertados} anuncios procesados'
        })
        
    except Exception as e:
        print(f"[ERROR] Error general en sincronización: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500
    """
    Sincroniza y devuelve todos los anuncios (histórico: activos e inactivos) de todas las cuentas accesibles del MCC para la Nora.
    """
    try:
        # Obtener todas las cuentas accesibles del MCC para la Nora
        cuentas = supabase.table('google_ads_cuentas').select('customer_id,nombre_cliente,accesible').eq('nombre_visible', nombre_nora).execute().data or []
        cuentas = [c for c in cuentas if c.get('accesible', True)]
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        resultados = []
        for cuenta in cuentas:
            customer_id = cuenta['customer_id']
            nombre_cliente = cuenta.get('nombre_cliente', '')
            try:
                anuncios = service.obtener_todos_los_anuncios(customer_id)
                resultados.append({
                    'customer_id': customer_id,
                    'nombre_cliente': nombre_cliente,
                    'anuncios': anuncios
                })
            except Exception as e:
                resultados.append({
                    'customer_id': customer_id,
                    'nombre_cliente': nombre_cliente,
                    'error': str(e),
                    'anuncios': []
                })
        return jsonify({'ok': True, 'resultados': resultados, 'cuentas': len(resultados)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# Archivo: clientes/aura/routes/panel_cliente_google_ads.py
from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for
from clientes.aura.utils.supabase_client import supabase

panel_cliente_google_ads_bp = Blueprint(
    'panel_cliente_google_ads',
    __name__
)

@panel_cliente_google_ads_bp.route('/<nombre_nora>/ads_json', methods=['GET'])
def obtener_todos_los_anuncios_json(nombre_nora):
    """
    Devuelve en JSON todos los anuncios (activos e inactivos) de una cuenta Google Ads usando el método obtener_todos_los_anuncios.
    Parámetros: customer_id (GET)
    """
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return jsonify({'ok': False, 'error': 'Falta customer_id'}), 400
    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        anuncios = service.obtener_todos_los_anuncios(customer_id)
        return jsonify({'ok': True, 'anuncios': anuncios})
    except Exception as e:
        print(f"[ERROR] Error obteniendo anuncios para {customer_id}: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

"""
✅ RUTA: Panel Cliente Google Ads (replicando panel_cliente_ads.py)
Este archivo maneja la vista de Google Ads de forma idéntica a Meta Ads:
- Muestra TODAS las cuentas publicitarias de Google Ads de la Nora.
- Permite vincular cuentas con empresas.
- Importa cuentas desde Google Ads API.
- Actualiza información de cuentas.
"""

from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for
from clientes.aura.utils.supabase_client import supabase

panel_cliente_google_ads_bp = Blueprint(
    'panel_cliente_google_ads',
    __name__
)

@panel_cliente_google_ads_bp.route('/<nombre_nora>/actualizar_empresa', methods=['POST'])
@panel_cliente_google_ads_bp.route('/actualizar_empresa', methods=['POST'])
def actualizar_empresa(nombre_nora=None):
    """Actualiza la empresa seleccionada para la sesión actual."""
    # Usar nombre_nora del parámetro o extraerlo de la ruta
    if nombre_nora is None:
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = ''
    
    try:
        data = request.get_json()
        empresa_id = data.get('empresa_id')
        
        if not empresa_id:
            return jsonify({'ok': False, 'error': 'empresa_id es requerido'}), 400
        
        # Aquí podrías guardar la selección en la sesión o base de datos
        # Por ahora solo devolvemos éxito
        return jsonify({'ok': True, 'empresa_id': empresa_id})
        
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@panel_cliente_google_ads_bp.route('/<nombre_nora>/', methods=['GET'])
@panel_cliente_google_ads_bp.route('/', methods=['GET'])  # Mantener compatibilidad
def panel_google_ads(nombre_nora=None):
    """Panel principal de Google Ads - vista de tarjetas con selector de empresa"""
    if nombre_nora is None:
        # Extrae nombre_nora de la ruta Flask: /panel_cliente/<nombre_nora>/google_ads
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = ''

    # Obtener empresas disponibles para la Nora
    empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    
    # Obtener empresa seleccionada (podría venir de query param o sesión)
    empresa_id = request.args.get('empresa_id')
    
    return render_template(
        'panel_cliente_google_ads/index.html',
        nombre_nora=nombre_nora,
        empresas=empresas,
        empresa_id=empresa_id
    )

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias', methods=['GET', 'POST'])
@panel_cliente_google_ads_bp.route('/cuentas', methods=['GET', 'POST'])  # Alias para compatibilidad

def vista_cuentas_publicitarias_google_ads():
    """
    Vista principal de cuentas publicitarias de Google Ads.
    Ahora SOLO muestra las cuentas que devuelve la API del MCC y que son accesibles.
    """
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''

    print(f"[DEBUG CUENTAS] Ruta accedida: {path}")
    print(f"[DEBUG CUENTAS] nombre_nora extraído: {nombre_nora}")
    print(f"[DEBUG CUENTAS] Método: {request.method}")

    # Manejar POST para asignación de empresas
    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'asignar_empresa':
            customer_id = request.form.get('customer_id')
            empresa_id = request.form.get('empresa_id')
            try:
                supabase.table('google_ads_cuentas').update({
                    'empresa_id': empresa_id
                }).eq('customer_id', customer_id).eq('nombre_visible', nombre_nora).execute()
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        # Manejar actualización de exclusiones
        excluir_ids = request.form.getlist('excluir')
        return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads'))

    # Obtener empresas disponibles
    empresas_disponibles = supabase.table('cliente_empresas').select('*').eq('nombre_nora', nombre_nora).execute().data or []

    # --- SOLO CUENTAS DEL MCC REAL ---
    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        cuentas_mcc = service.listar_cuentas_mcc()
        cuentas_mcc = [c for c in cuentas_mcc if c.get('accesible', True)]
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener cuentas del MCC: {e}")
        cuentas_mcc = []

    cuentas_procesadas = []
    for cuenta in cuentas_mcc:
        cuenta_procesada = {
            'id': cuenta.get('customer_id'),
            'name': cuenta.get('nombre_cliente', 'Sin nombre'),
            'moneda': cuenta.get('moneda', 'MXN'),
            'zona_horaria': cuenta.get('zona_horaria', 'America/Mexico_City'),
            'es_test': cuenta.get('es_test', False),
            'accesible': cuenta.get('accesible', True),
            'problema': cuenta.get('problema'),
            'resource_name': f"customers/{cuenta.get('customer_id')}",
            'empresa_asignada': None
        }
        # Buscar empresa asignada en la base de datos (si existe)
        empresa_id = cuenta.get('empresa_id')
        if empresa_id:
            empresa = next((e for e in empresas_disponibles if e['id'] == empresa_id), None)
            if empresa:
                cuenta_procesada['empresa_asignada'] = {
                    'id': empresa['id'],
                    'nombre': empresa.get('nombre_empresa', 'Sin nombre')
                }
        cuentas_procesadas.append(cuenta_procesada)

    cuentas_excluidas_ids = []
    print(f"[DEBUG CUENTAS] Cuentas procesadas (solo MCC): {len(cuentas_procesadas)}")
    print(f"[DEBUG CUENTAS] Empresas disponibles: {len(empresas_disponibles)}")
    print(f"[DEBUG CUENTAS] Rendering template: panel_cliente_google_ads/cuentas.html")

    return render_template(
        'panel_cliente_google_ads/cuentas.html',
        nombre_nora=nombre_nora,
        cuentas=cuentas_procesadas,
        cuentas_mostradas=[c for c in cuentas_procesadas if c.get('id') not in cuentas_excluidas_ids],
        cuentas_excluidas=cuentas_excluidas_ids,
        empresas_disponibles=empresas_disponibles,
        mensaje=request.args.get('mensaje')
    )

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/actualizar', methods=['POST'])
def actualizar_cuentas_publicitarias_google_ads():
    """
    Actualiza información de todas las cuentas de Google Ads desde la API.
    Replica la funcionalidad de Meta Ads.
    """
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    print(f"[DEBUG] Iniciando actualización de cuentas Google Ads para Nora: {nombre_nora}")
    
    # Importar el servicio de Google Ads
    from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
    
    # Obtener todas las cuentas de Google Ads para la Nora
    cuentas = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    print(f"[DEBUG] Cuentas encontradas: {len(cuentas)}")
    
    errores = []
    cuentas_actualizadas = []
    
    # Crear instancia del servicio de Google Ads
    try:
        service = GoogleAdsService()
        
        for cuenta in cuentas:
            customer_id = cuenta['customer_id']
            print(f"[DEBUG] Actualizando cuenta: {customer_id}")
            
            try:
                # Obtener información actualizada de la cuenta desde Google Ads API
                info_cuenta = service.obtener_info_cuenta(customer_id)
                print(f"[DEBUG] Info obtenida de Google Ads API para {customer_id}: {info_cuenta}")
                
                # Preparar datos para actualizar
                update_data = {
                    'nombre_cliente': info_cuenta.get('nombre_cliente', cuenta['nombre_cliente']),
                    'account_status': 1 if info_cuenta.get('activa', True) else 0,
                    'accesible': info_cuenta.get('accesible', True),
                    'problema': info_cuenta.get('problema'),
                    'ads_activos': info_cuenta.get('ads_activos', cuenta.get('ads_activos', 0)),
                    'moneda': info_cuenta.get('moneda', 'MXN'),
                    'zona_horaria': info_cuenta.get('zona_horaria', 'America/Mexico_City'),
                }
                
                # Fallback si nombre_cliente viene vacío
                if not update_data['nombre_cliente']:
                    update_data['nombre_cliente'] = 'Sin nombre'
                
                print(f"[DEBUG] Datos a actualizar en Supabase para {customer_id}: {update_data}")
                
                # Actualizar en Supabase
                resp_update = supabase.table('google_ads_cuentas').update(update_data).eq('customer_id', customer_id).execute()
                print(f"[DEBUG] Respuesta de update Supabase para {customer_id}: {resp_update}")
                
                cuentas_actualizadas.append({
                    'customer_id': customer_id,
                    'ads_activos': update_data['ads_activos'],
                    'nombre_cliente': update_data['nombre_cliente']
                })
                
            except Exception as e:
                print(f"[ERROR] Error actualizando cuenta {customer_id}: {e}")
                errores.append({'cuenta_id': customer_id, 'error': str(e)})
                
    except Exception as e:
        print(f"[ERROR] Error inicializando servicio de Google Ads: {e}")
        return {'ok': False, 'error': f'Error inicializando servicio: {str(e)}'}, 500
    
    if errores:
        print(f"[DEBUG] Errores encontrados: {errores}")
        return {'ok': False, 'errores': errores, 'cuentas': cuentas_actualizadas}, 207
    
    print("[DEBUG] Actualización de cuentas Google Ads finalizada correctamente.")
    return {'ok': True, 'cuentas': cuentas_actualizadas}

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/importar_desde_google_ads', methods=['POST'])
def importar_cuentas_desde_google_ads():
    """
    Consulta la API de Google Ads y agrega todas las cuentas publicitarias del MCC,
    insertando solo las que no existan aún en Supabase para la Nora.
    """
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    print(f"[DEBUG] Iniciando importación de cuentas Google Ads para Nora: {nombre_nora}")
    
    try:
        # Importar el servicio de Google Ads
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        
        # Crear instancia del servicio
        service = GoogleAdsService()
        
        # Obtener todas las cuentas del MCC
        cuentas_mcc = service.listar_cuentas_mcc()
        print(f"[DEBUG] Cuentas obtenidas del MCC: {len(cuentas_mcc)}")
        
        # Buscar cuentas ya existentes para la Nora
        existentes = supabase.table('google_ads_cuentas').select('customer_id').eq('nombre_visible', nombre_nora).execute().data or []
        existentes_ids = {c['customer_id'] for c in existentes}
        
        nuevas = []
        for cuenta in cuentas_mcc:
            customer_id = cuenta.get('customer_id')
            if not customer_id or customer_id in existentes_ids:
                continue
                
            # Construir data con manejo explícito de None values
            data = {
                'customer_id': str(customer_id),  # Asegurar que sea string
                'nombre_cliente': cuenta.get('nombre_cliente') or 'Sin nombre',
                'nombre_visible': nombre_nora,
                'conectada': True,
                'account_status': 1 if cuenta.get('activa', True) else 0,
                'accesible': cuenta.get('accesible', True),
                'ads_activos': int(cuenta.get('ads_activos', 0)),
                'moneda': cuenta.get('moneda') or 'MXN',
                'zona_horaria': cuenta.get('zona_horaria') or 'America/Mexico_City',
            }
            
            # Solo agregar problema si no es None
            problema = cuenta.get('problema')
            if problema:
                data['problema'] = str(problema)
                
            print(f"[DEBUG] Preparando inserción para customer_id: {customer_id}")
            print(f"[DEBUG] Data limpia: {data}")
            nuevas.append(data)
        
        if nuevas:
            print(f"[DEBUG] Insertando {len(nuevas)} cuentas nuevas")
            try:
                # Intentar inserción en lote primero
                result = supabase.table('google_ads_cuentas').insert(nuevas).execute()
                print(f"[DEBUG] Inserción en lote exitosa: {len(result.data)} cuentas insertadas")
            except Exception as batch_error:
                print(f"[WARNING] Error en inserción en lote: {batch_error}")
                print("[DEBUG] Intentando inserción individual...")
                
                # Si falla inserción en lote, intentar una por una
                insertadas = 0
                for i, data in enumerate(nuevas):
                    try:
                        result = supabase.table('google_ads_cuentas').insert(data).execute()
                        insertadas += 1
                        print(f"[DEBUG] Cuenta {data['customer_id']} insertada exitosamente ({i+1}/{len(nuevas)})")
                    except Exception as individual_error:
                        print(f"[ERROR] Error insertando cuenta {data['customer_id']}: {individual_error}")
                        print(f"[ERROR] Datos que causaron error: {data}")
                        
                        # Intentar inserción ultra-minimal como último recurso
                        try:
                            minimal_data = {
                                'customer_id': str(data['customer_id']),
                                'nombre_cliente': str(data['nombre_cliente']),
                                'nombre_visible': str(data['nombre_visible'])
                            }
                            result = supabase.table('google_ads_cuentas').insert(minimal_data).execute()
                            insertadas += 1
                            print(f"[DEBUG] Cuenta {data['customer_id']} insertada con datos mínimos")
                        except Exception as minimal_error:
                            print(f"[ERROR] Falló incluso inserción mínima para {data['customer_id']}: {minimal_error}")
                
                print(f"[DEBUG] Inserción individual completada: {insertadas}/{len(nuevas)} cuentas insertadas")
        
        print(f"[DEBUG] Importación completada: {len(nuevas)} cuentas agregadas de {len(cuentas_mcc)} total")
        return jsonify({'ok': True, 'agregadas': len(nuevas), 'total': len(cuentas_mcc)})
        
    except Exception as e:
        print(f"[ERROR] Error importando cuentas de Google Ads: {e}")
        return jsonify({'ok': False, 'msg': f'Error importando cuentas: {str(e)}'}), 500

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/vincular_empresa', methods=['GET', 'POST'])
def vincular_empresa_a_cuenta_google_ads():
    """
    Vincula una cuenta de Google Ads con una empresa del cliente.
    Replica exactamente la funcionalidad de Meta Ads.
    """
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    # Obtener customer_id de los parámetros de consulta
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return "Customer ID requerido", 400
    
    # Obtener la cuenta
    cuenta = supabase.table('google_ads_cuentas').select('*').eq('customer_id', customer_id).single().execute().data
    if not cuenta:
        return "Cuenta de Google Ads no encontrada", 404
    
    # Obtener empresas disponibles para la Nora
    empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    
    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        if not empresa_id:
            return render_template(
                'vincular_empresa_cuenta_google_ads.html', 
                cuenta=cuenta, 
                empresas=empresas, 
                nombre_nora=nombre_nora, 
                error='Debes seleccionar una empresa'
            )
        
        # Actualizar la cuenta con el empresa_id
        supabase.table('google_ads_cuentas').update({'empresa_id': empresa_id}).eq('customer_id', customer_id).execute()
        
        return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads', nombre_nora=nombre_nora))
    
    return render_template(
        'vincular_empresa_cuenta_google_ads.html', 
        cuenta=cuenta, 
        empresas=empresas, 
        nombre_nora=nombre_nora
    )

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/ads_activos', methods=['GET'])
def obtener_ads_activos_endpoint_google_ads():
    """
    Obtiene el número de anuncios activos para una cuenta específica.
    """
    # Obtener customer_id de los parámetros de consulta
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return jsonify({'ok': False, 'error': 'Customer ID requerido'}), 400
    
    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        
        service = GoogleAdsService()
        ads_activos = service.obtener_ads_activos_cuenta(customer_id)
        
        print(f"[DEBUG] Ads activos para cuenta Google Ads {customer_id}: {ads_activos}")
        
        # Actualizar el campo en Supabase
        supabase.table('google_ads_cuentas').update({
            'ads_activos': ads_activos
        }).eq('customer_id', customer_id).execute()
        
        return jsonify({'ok': True, 'ads_activos': ads_activos})
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo ads activos para cuenta {customer_id}: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@panel_cliente_google_ads_bp.route('/cuenta', methods=['GET'])
def ficha_cuenta_publicitaria_google_ads():
    """
    Ficha detallada de una cuenta de Google Ads.
    """
    # Obtener customer_id de los parámetros de consulta
    customer_id = request.args.get('customer_id')
    nombre_nora = request.args.get('nombre_nora') or ''
    
    if not customer_id:
        return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads'))
    
    # Si nombre_nora no viene en parámetros, extraerlo del path
    if not nombre_nora:
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = ''
    
    # Obtener información de la cuenta
    cuenta = supabase.table('google_ads_cuentas').select('*').eq('customer_id', customer_id).single().execute().data
    if not cuenta:
        return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads'))
    
    # Enriquecer con información de empresa si está vinculada
    empresa_id = cuenta.get('empresa_id')
    cuenta['empresa_nombre'] = None
    cuenta['empresa_logo_url'] = None
    if empresa_id:
        empresa = supabase.table('cliente_empresas').select('nombre_empresa,logo_url').eq('id', empresa_id).single().execute().data
        if empresa:
            cuenta['empresa_nombre'] = empresa.get('nombre_empresa')
            cuenta['empresa_logo_url'] = empresa.get('logo_url')
    
    # TODO: Aquí se pueden agregar más datos específicos de Google Ads
    # como campañas, grupos de anuncios, etc.
    
    return render_template(
        'google_ads_cuenta_ficha.html',
        cuenta=cuenta,
        nombre_nora=nombre_nora
    )

# Rutas adicionales para replicar completamente el comportamiento de Meta Ads

@panel_cliente_google_ads_bp.route('/agregar_cuenta', methods=['POST'])
def agregar_cuenta_google_ads():
    """Agregar una cuenta de Google Ads manualmente"""
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = request.form.get('nombre_nora', '')
    
    customer_id = request.form.get('customer_id')
    nombre_cliente = request.form.get('nombre_cliente')
    activo = request.form.get('activo') == 'on'
    account_status = 1 if activo else 0
    
    data = {
        'customer_id': customer_id,
        'nombre_cliente': nombre_cliente,
        'account_status': account_status,
        'conectada': True,
        'nombre_visible': nombre_nora,
        'accesible': True,
        'ads_activos': 0,
        'moneda': 'MXN',
        'zona_horaria': 'America/Mexico_City'
    }
    
    supabase.table('google_ads_cuentas').insert(data).execute()
    return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads'))

@panel_cliente_google_ads_bp.route('/google_ads/anuncios_activos_json')
def anuncios_activos_json():
    """
    Devuelve en JSON los anuncios ACTIVOS de la cuenta seleccionada (por customer_id).
    """
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return jsonify({"error": "Falta customer_id"}), 400
    
    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        # TODO: Implementar listar_anuncios_activos en el servicio
        anuncios = []  # service.listar_anuncios_activos(customer_id)
        return jsonify({"anuncios": anuncios})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_cliente_google_ads_bp.route('/reportes', methods=['GET'])
def vista_reportes_google_ads():
    """Vista de reportes de Google Ads"""
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    cuentas_ads = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    # Filtrar solo cuentas accesibles (en el MCC real)
    cuentas_ads = [c for c in cuentas_ads if c.get('accesible', True)]
    
    return render_template('panel_cliente_google_ads/reportes_google_ads.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads)

@panel_cliente_google_ads_bp.route('/campanas', methods=['GET'])
def vista_campanas_google_ads():
    """Vista avanzada de campañas de Google Ads"""
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    return render_template('panel_cliente_google_ads/campanas_google_ads.html', nombre_nora=nombre_nora)

@panel_cliente_google_ads_bp.route('/campanas_activas_google_ads')
def campanas_activas_google_ads():
    """Vista de campañas activas de Google Ads"""
    nombre_nora = request.args.get('nombre_nora', '')
    customer_id = request.args.get('customer_id', '')
    return render_template('panel_cliente_google_ads/campanas_activas_google_ads.html', nombre_nora=nombre_nora, customer_id=customer_id)

@panel_cliente_google_ads_bp.get("/panel_cliente/google_ads/campañas_activas")
def campañas_activas_api():
    """
    Devuelve en JSON las campañas ACTIVAS de la cuenta que el cliente tenga
    asignada en la tabla `google_ads_cuentas`.
    """
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    customer_id = request.args.get('customer_id')
    if customer_id:
        # Buscar solo esa cuenta
        fila = supabase.table("google_ads_cuentas") \
                   .select("customer_id") \
                   .eq("customer_id", customer_id) \
                   .eq("nombre_visible", nombre_nora) \
                   .single() \
                   .execute() \
                   .data
    else:
        # Buscar la cuenta principal ligada a la Nora
        fila = supabase.table("google_ads_cuentas") \
                   .select("customer_id") \
                   .eq("nombre_visible", nombre_nora) \
                   .single() \
                   .execute() \
                   .data

    if not fila:
        return jsonify({"error": "Cuenta no encontrada"}), 404

    customer_id = fila["customer_id"]

    try:
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        service = GoogleAdsService()
        # TODO: Implementar listar_campañas_activas en el servicio
        campañas = []  # service.listar_campañas_activas(customer_id)
        return jsonify({"campañas": campañas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_cliente_google_ads_bp.route('/reporte_google_ads', methods=['GET'])
def reporte_google_ads():
    """Vista de reportes de Google Ads - función específica para el template"""
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    cuentas_ads = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    # Filtrar solo cuentas accesibles (en el MCC real)
    cuentas_ads = [c for c in cuentas_ads if c.get('accesible', True)]
    
    return render_template('panel_cliente_google_ads/reportes.html', nombre_nora=nombre_nora, cuentas_ads=cuentas_ads)

@panel_cliente_google_ads_bp.route('/ver_cuentas_google_ads', methods=['GET', 'POST'])
def ver_cuentas_google_ads():
    """Vista de cuentas de Google Ads - función específica para el template"""
    # Extrae nombre_nora de la ruta Flask
    path = request.path
    try:
        nombre_nora = path.split('/')[2]
    except Exception:
        nombre_nora = ''
    
    mensaje = None
    
    # Manejar POST para asignar empresas o actualizar exclusiones
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'asignar_empresa':
            customer_id = request.form.get('customer_id')
            empresa_id = request.form.get('empresa_id')
            
            try:
                # Actualizar la cuenta con la empresa asignada
                supabase.table('google_ads_cuentas').update({
                    'empresa_id': empresa_id
                }).eq('customer_id', customer_id).execute()
                
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        elif 'excluir' in request.form:
            # Manejar exclusiones de cuentas
            cuentas_excluir = request.form.getlist('excluir')
            # TODO: Implementar lógica de exclusión si es necesaria
            mensaje = f"Configuración actualizada. {len(cuentas_excluir)} cuentas marcadas como excluidas."
    
    # Obtener todas las cuentas de Google Ads para la Nora (simular desde MCC)
    cuentas_desde_bd = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    
    # Convertir las cuentas de BD al formato esperado por el template
    cuentas = []
    for cuenta_bd in cuentas_desde_bd:
        # Buscar empresa asignada
        empresa_asignada = None
        if cuenta_bd.get('empresa_id'):
            empresa = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('id', cuenta_bd['empresa_id']).single().execute().data
            if empresa:
                empresa_asignada = {
                    'id': empresa['id'],
                    'nombre': empresa['nombre_empresa']
                }
        
        cuenta = {
            'id': cuenta_bd.get('customer_id', ''),
            'name': cuenta_bd.get('nombre_cliente', 'Sin nombre'),
            'resource_name': f"customers/{cuenta_bd.get('customer_id', '')}",
            'moneda': cuenta_bd.get('moneda', 'MXN'),
            'zona_horaria': cuenta_bd.get('zona_horaria', 'America/Mexico_City'),
            'accesible': cuenta_bd.get('accesible', True),
            'problema': cuenta_bd.get('problema'),
            'es_test': False,  # Determinar si es cuenta de test
            'empresa_asignada': empresa_asignada
        }
        cuentas.append(cuenta)
    
    # Si no hay cuentas en BD, intentar obtener desde el servicio de Google Ads
    if not cuentas:
        try:
            from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
            service = GoogleAdsService()
            cuentas_mcc = service.listar_cuentas_mcc()
            
            # Convertir al formato del template
            for cuenta_mcc in cuentas_mcc:
                cuenta = {
                    'id': cuenta_mcc.get('customer_id', ''),
                    'name': cuenta_mcc.get('nombre_cliente', 'Sin nombre'),
                    'resource_name': f"customers/{cuenta_mcc.get('customer_id', '')}",
                    'moneda': cuenta_mcc.get('moneda', 'MXN'),
                    'zona_horaria': cuenta_mcc.get('zona_horaria', 'America/Mexico_City'),
                    'accesible': cuenta_mcc.get('accesible', True),
                    'problema': cuenta_mcc.get('problema'),
                    'es_test': cuenta_mcc.get('es_test', False),
                    'empresa_asignada': None
                }
                cuentas.append(cuenta)
                
        except Exception as e:
            print(f"[ERROR] No se pudieron obtener cuentas del MCC: {e}")
            mensaje = "No se pudieron cargar las cuentas desde Google Ads. Verifica la configuración de la API."
    
    # Obtener empresas disponibles para asignar
    empresas_disponibles = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    
    # Simular cuentas excluidas (vacío por ahora)
    cuentas_excluidas = []
    
    # Filtrar cuentas mostradas (las que no están excluidas)
    cuentas_mostradas = [c for c in cuentas if c['id'] not in cuentas_excluidas]
    
    return render_template('panel_cliente_google_ads/cuentas.html', 
                         nombre_nora=nombre_nora, 
                         cuentas=cuentas, 
                         empresas_disponibles=empresas_disponibles,
                         cuentas_excluidas=cuentas_excluidas,
                         cuentas_mostradas=cuentas_mostradas,
                         mensaje=mensaje)

@panel_cliente_google_ads_bp.route('/<nombre_nora>/importar_cuentas_automatico', methods=['POST'])
@panel_cliente_google_ads_bp.route('/importar_cuentas_automatico', methods=['POST'])  # Mantener compatibilidad
def importar_cuentas_automatico(nombre_nora=None):
    """Importa automáticamente todas las cuentas del MCC si no existen"""
    # Usar nombre_nora del parámetro o extraerlo de la ruta
    if nombre_nora is None:
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = ''
    
    try:
        # Verificar si ya hay cuentas (pero no bloquear la importación)
        cuentas_existentes = supabase.table('google_ads_cuentas').select('customer_id').eq('nombre_visible', nombre_nora).execute().data or []
        print(f"[DEBUG] Cuentas existentes encontradas: {len(cuentas_existentes)}")
        
        # Obtener IDs de cuentas existentes para evitar duplicados
        ids_existentes = {cuenta['customer_id'] for cuenta in cuentas_existentes}
        
        # Importar desde Google Ads API
        from clientes.aura.services.google_ads_service_fixed import GoogleAdsService
        
        service = GoogleAdsService()
        cuentas_mcc = service.listar_cuentas_mcc()
        
        print(f"[DEBUG] Obtenidas {len(cuentas_mcc)} cuentas del MCC")
        
        # Debug: mostrar estructura de las primeras cuentas
        if cuentas_mcc:
            print(f"[DEBUG] Estructura de la primera cuenta: {cuentas_mcc[0]}")
            if len(cuentas_mcc) > 1:
                print(f"[DEBUG] Estructura de la segunda cuenta: {cuentas_mcc[1]}")
        
        # Insertar cuentas en la base de datos
        nuevas_cuentas = []
        cuentas_problematicas = []
        
        for i, cuenta in enumerate(cuentas_mcc):
            # Validar campos requeridos
            customer_id = cuenta.get('customer_id')
            nombre_cliente = cuenta.get('nombre_cliente') or 'Sin nombre'
            accesible = cuenta.get('accesible', True)
            
            print(f"[DEBUG] Procesando cuenta {i+1}: customer_id={customer_id}, nombre={nombre_cliente}, accesible={accesible}")
            
            # FILTRAR: Solo procesar cuentas accesibles (sin problemas)
            if not accesible:
                print(f"[INFO] Omitiendo cuenta no accesible: {customer_id} - {nombre_cliente} - {cuenta.get('problema')}")
                cuentas_problematicas.append(f"Cuenta {customer_id}: no accesible - {cuenta.get('problema')}")
                continue
            
            if not customer_id:
                print(f"[WARNING] Cuenta {i+1} sin customer_id válido, omitiendo: {cuenta}")
                cuentas_problematicas.append(f"Cuenta {i+1}: sin customer_id")
                continue
            
            # Asegurar que customer_id sea string y tenga el formato correcto
            customer_id = str(customer_id).strip()
            if not customer_id or customer_id == 'None':
                print(f"[WARNING] Cuenta {i+1} con customer_id inválido: '{customer_id}', omitiendo")
                cuentas_problematicas.append(f"Cuenta {i+1}: customer_id inválido '{customer_id}'")
                continue
            
            # Saltear si la cuenta ya existe
            if customer_id in ids_existentes:
                print(f"[DEBUG] Cuenta {customer_id} ya existe, omitiendo")
                continue
            
            # Validar que nombre_nora no sea None
            if not nombre_nora:
                print(f"[ERROR] nombre_nora es None o vacío: '{nombre_nora}'")
                raise ValueError("nombre_nora no puede ser None o vacío")
            
            # Preparar datos para inserción con validación exhaustiva
            data = {
                'customer_id': str(customer_id).strip(),
                'nombre_cliente': str(nombre_cliente).strip()[:255],  # Limitar longitud
                'nombre_visible': str(nombre_nora).strip()[:100],     # Limitar longitud
                'empresa_id': None,  # Sin empresa asignada inicialmente
                'conectada': True,
                'account_status': 1,  # Siempre activo por defecto
                'activa': True,
                'moneda': str(cuenta.get('moneda') or 'MXN')[:10],
                'zona_horaria': str(cuenta.get('zona_horaria') or 'America/Mexico_City')[:50],
                'es_test': bool(cuenta.get('es_test', False)),
                'accesible': bool(cuenta.get('accesible', True)),
                'problema': str(cuenta.get('problema'))[:255] if cuenta.get('problema') else None,
                'ads_activos': int(cuenta.get('ads_activos', 0) or 0),
                'ads_activos': int(cuenta.get('ads_activos', 0) or 0)
            }
            
            # Validar que los campos críticos no sean vacíos después del procesamiento
            campos_criticos = ['customer_id', 'nombre_cliente', 'nombre_visible']
            for campo in campos_criticos:
                if not data[campo] or data[campo].strip() == '':
                    print(f"[ERROR] Campo crítico '{campo}' está vacío después del procesamiento")
                    cuentas_problematicas.append(f"Cuenta {customer_id}: campo '{campo}' vacío")
                    break
            else:
                # Solo agregar si todos los campos críticos están OK
                nuevas_cuentas.append(data)
        
        print(f"[DEBUG] Cuentas válidas para insertar: {len(nuevas_cuentas)}")
        if cuentas_problematicas:
            print(f"[DEBUG] Cuentas problemáticas: {cuentas_problematicas}")
        
        if nuevas_cuentas:
            try:
                print(f"[DEBUG] Intentando insertar {len(nuevas_cuentas)} cuentas...")
                
                # Inserción simplificada - una por una con manejo individual de errores
                inserted_count = 0
                for i, data in enumerate(nuevas_cuentas):
                    try:
                        print(f"[DEBUG] Insertando cuenta {i+1}/{len(nuevas_cuentas)}: {data['customer_id']}")
                        
                        # Datos mínimos para asegurar inserción exitosa
                        minimal_insert = {
                            'customer_id': data['customer_id'],
                            'nombre_cliente': data['nombre_cliente'],
                            'nombre_visible': data['nombre_visible']
                        }
                        
                        # Agregar campos opcionales solo si tienen valores válidos
                        optional_fields = {
                            'empresa_id': data.get('empresa_id'),
                            'conectada': data.get('conectada', True),
                            'account_status': data.get('account_status', 1),
                            'activa': data.get('activa', True),
                            'moneda': data.get('moneda', 'MXN'),
                            'zona_horaria': data.get('zona_horaria', 'America/Mexico_City'),
                            'es_test': data.get('es_test', False),
                            'accesible': data.get('accesible', True),
                            'ads_activos': data.get('ads_activos', 0)
                        }
                        
                        # Solo agregar campos opcionales que no sean None
                        for field, value in optional_fields.items():
                            if value is not None:
                                minimal_insert[field] = value
                        
                        print(f"[DEBUG] Datos finales para inserción: {minimal_insert}")
                        
                        # Intentar inserción
                        result = supabase.table('google_ads_cuentas').insert(minimal_insert).execute()
                        print(f"[DEBUG] ✅ Cuenta {data['customer_id']} insertada exitosamente")
                        inserted_count += 1
                        
                    except Exception as insert_error:
                        error_detail = str(insert_error)
                        print(f"[ERROR] ❌ Error insertando cuenta {data['customer_id']}: {error_detail}")
                        
                        # Intentar con datos ultra-mínimos
                        try:
                            ultra_minimal = {
                                'customer_id': data['customer_id'],
                                'nombre_cliente': data['nombre_cliente'],
                                'nombre_visible': data['nombre_visible']
                            }
                            print(f"[DEBUG] Intentando inserción ultra-mínima: {ultra_minimal}")
                            supabase.table('google_ads_cuentas').insert(ultra_minimal).execute()
                            print(f"[DEBUG] ✅ Inserción ultra-mínima exitosa para {data['customer_id']}")
                            inserted_count += 1
                        except Exception as ultra_error:
                            print(f"[ERROR] ❌ Falló incluso la inserción ultra-mínima: {ultra_error}")
                            cuentas_problematicas.append(f"Error total en {data['customer_id']}: {str(ultra_error)[:50]}")
                
                print(f"[DEBUG] ✅ Proceso completado. Insertadas: {inserted_count}, Problemáticas: {len(cuentas_problematicas)}")
                
            except Exception as e:
                print(f"[ERROR] Error general en inserción: {e}")
                import traceback
                traceback.print_exc()
                raise e
        
        return jsonify({
            'ok': True,
            'mensaje': f'Importación completada: {inserted_count} nuevas cuentas de {len(cuentas_mcc)} encontradas en MCC',
            'cuentas_importadas': inserted_count,
            'cuentas_procesadas': len(nuevas_cuentas),
            'total_mcc': len(cuentas_mcc),
            'cuentas_existentes': len(ids_existentes),
            'cuentas_problematicas': len(cuentas_problematicas),
            'detalles_problemas': cuentas_problematicas[:3] if cuentas_problematicas else [],
            'resumen': f"Nuevas: {inserted_count}, Existentes: {len(ids_existentes)}, Con errores: {len(cuentas_problematicas)}"
        })
        
    except Exception as e:
        print(f"[ERROR] Error importando cuentas: {e}")
        import traceback
        traceback.print_exc()
        
        # Proporcionar información más detallada del error
        error_msg = str(e)
        if 'null value' in error_msg and 'not-null constraint' in error_msg:
            error_msg = "Error de base de datos: Campo requerido faltante. Verifica la estructura de la tabla."
        elif 'duplicate key' in error_msg:
            error_msg = "Algunas cuentas ya existen en la base de datos."
        elif 'connection' in error_msg.lower():
            error_msg = "Error de conexión con la base de datos."
        
        return jsonify({
            'ok': False,
            'error': error_msg,
            'error_detalle': str(e)[:200] + "..." if len(str(e)) > 200 else str(e)
        }), 500

@panel_cliente_google_ads_bp.route('/<nombre_nora>/test_simple_insert', methods=['POST'])
@panel_cliente_google_ads_bp.route('/test_simple_insert', methods=['POST'])
def test_simple_insert(nombre_nora=None):
    """Endpoint de prueba para insertar una cuenta con datos mínimos"""
    # Usar nombre_nora del parámetro o extraerlo de la ruta
    if nombre_nora is None:
        path = request.path
        try:
            nombre_nora = path.split('/')[2]
        except Exception:
            nombre_nora = 'aura'
    
    try:
        print(f"[DEBUG] Test simple insert para {nombre_nora}")
        
        # Datos mínimos para prueba - NUNCA incluir 'id'
        test_account = {
            'customer_id': '9999999999',
            'nombre_cliente': 'Cuenta de Prueba',
            'nombre_visible': str(nombre_nora).strip()
        }
        
        print(f"[DEBUG] Datos de prueba: {test_account}")
        
        # Verificar si ya existe
        existing = supabase.table('google_ads_cuentas').select('id').eq('customer_id', '9999999999').execute()
        
        if existing.data:
            print("[DEBUG] Cuenta de prueba ya existe, eliminando...")
            supabase.table('google_ads_cuentas').delete().eq('customer_id', '9999999999').execute()
        
        # Insertar cuenta de prueba
        print("[DEBUG] Insertando cuenta de prueba...")
        result = supabase.table('google_ads_cuentas').insert(test_account).execute()
        print(f"[DEBUG] Resultado: {result}")
        
        # Limpiar después del test
        print("[DEBUG] Limpiando cuenta de prueba...")
        supabase.table('google_ads_cuentas').delete().eq('customer_id', '9999999999').execute()
        
        return jsonify({
            'ok': True,
            'mensaje': 'Test de inserción simple exitoso',
            'datos_insertados': test_account,
            'resultado': str(result)
        })
        
    except Exception as e:
        print(f"[ERROR] Error en test simple: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'ok': False,
            'error': f'Error en test simple: {str(e)}',
            'datos_intentados': test_account if 'test_account' in locals() else 'N/A'
        }), 500

@panel_cliente_google_ads_bp.route('/<nombre_nora>/reporte/<customer_id>')
def reporte_detallado_google_ads(nombre_nora, customer_id):
    """
    Vista de reporte detallado de una cuenta de Google Ads usando datos reales de google_ads_reporte_anuncios
    """
    try:
        # Obtener datos de la cuenta
        cuenta_result = supabase.table('google_ads_cuentas').select('*').eq('customer_id', customer_id).eq('nombre_visible', nombre_nora).execute()
        if not cuenta_result.data:
            return render_template('panel_cliente_google_ads/reporte_detallado_google_ads.html', 
                                 error="Cuenta no encontrada", 
                                 nombre_nora=nombre_nora, 
                                 cuenta={'nombre_cliente': 'N/A', 'customer_id': customer_id})
        
        cuenta = cuenta_result.data[0]

        # Obtener anuncios de esta cuenta específica desde la tabla de reportes
        # Filtrar por customer_id para obtener solo los anuncios de esta cuenta
        result_cuenta = supabase.table('google_ads_reporte_anuncios').select('*').eq('nombre_nora', nombre_nora).eq('customer_id', customer_id).execute()
        anuncios = result_cuenta.data or []
        
        # Si no hay anuncios específicos de esta cuenta, intentar con empresa_id si existe
        if not anuncios and cuenta.get('empresa_id'):
            result_empresa = supabase.table('google_ads_reporte_anuncios').select('*').eq('nombre_nora', nombre_nora).eq('empresa_id', cuenta['empresa_id']).execute()
            anuncios = result_empresa.data or []
        
        if not anuncios:
            return render_template('panel_cliente_google_ads/reporte_detallado_google_ads.html', 
                                 error="No hay datos de anuncios disponibles para esta cuenta", 
                                 nombre_nora=nombre_nora, cuenta=cuenta)

        # Calcular estadísticas generales
        total_clics = 0
        total_impresiones = 0
        total_costo = 0.0
        total_conversiones = 0
        
        def convertir_numero(valor, tipo=int):
            """Convierte valores de texto a números, manejando casos especiales"""
            if not valor or valor == '' or valor == 'N/A':
                return 0
            try:
                # Remover comas y espacios
                valor_limpio = str(valor).replace(',', '').replace(' ', '').replace('%', '')
                if tipo == float:
                    return float(valor_limpio)
                else:
                    return int(float(valor_limpio))  # Convertir a float primero por si hay decimales
            except (ValueError, TypeError):
                return 0
        
        for anuncio in anuncios:
            total_clics += convertir_numero(anuncio.get('clics', 0))
            total_impresiones += convertir_numero(anuncio.get('impresiones', 0))
            total_costo += convertir_numero(anuncio.get('costo', 0), float)
            total_conversiones += convertir_numero(anuncio.get('conversiones', 0))
        
        # Calcular CTR promedio
        ctr_promedio = (total_clics / total_impresiones * 100) if total_impresiones > 0 else 0.0
        
        stats = {
            'clics': total_clics,
            'impresiones': total_impresiones,
            'ctr': round(ctr_promedio, 2),
            'costo_total': round(total_costo, 2),
            'conversiones': total_conversiones
        }

        # Top 5 campañas por impresiones
        campanas_stats = {}
        for anuncio in anuncios:
            campaña = anuncio.get('campaña', 'Sin nombre')
            if campaña not in campanas_stats:
                campanas_stats[campaña] = {
                    'nombre': campaña,
                    'impresiones': 0,
                    'clics': 0,
                    'costo': 0.0,
                    'estado': anuncio.get('estado', 'UNKNOWN')
                }
            
            campanas_stats[campaña]['impresiones'] += convertir_numero(anuncio.get('impresiones', 0))
            campanas_stats[campaña]['clics'] += convertir_numero(anuncio.get('clics', 0))
            campanas_stats[campaña]['costo'] += convertir_numero(anuncio.get('costo', 0), float)
        
        # Calcular CTR para cada campaña y ordenar por impresiones
        for campaña in campanas_stats.values():
            campaña['ctr'] = round((campaña['clics'] / campaña['impresiones'] * 100), 2) if campaña['impresiones'] > 0 else 0.0
        
        top_campanas = sorted(campanas_stats.values(), key=lambda x: x['impresiones'], reverse=True)[:5]

        # Top anuncios por rendimiento (CTR)
        top_anuncios = []
        for anuncio in anuncios:
            try:
                clics = convertir_numero(anuncio.get('clics', 0))
                impresiones = convertir_numero(anuncio.get('impresiones', 0))
                ctr = (clics / impresiones * 100) if impresiones > 0 else 0.0
                
                # Mostrar todos los anuncios, no solo los que tienen impresiones
                top_anuncios.append({
                    'id_anuncio': anuncio.get('id_anuncio', 'N/A'),
                    'titulo_1': anuncio.get('titulo_1', 'Sin título'),
                    'descripcion_1': anuncio.get('descripcion_1', 'Sin descripción'),
                    'campaña': anuncio.get('campaña', 'Sin campaña'),
                    'estado': anuncio.get('estado', 'UNKNOWN'),
                    'clics': clics,
                    'impresiones': impresiones,
                    'ctr': round(ctr, 2),
                    'costo': convertir_numero(anuncio.get('costo', 0), float)
                })
            except (ValueError, TypeError):
                continue
        
        # Ordenar por impresiones descendente primero, luego por CTR
        top_anuncios = sorted(top_anuncios, key=lambda x: (x['impresiones'], x['ctr']), reverse=True)[:10]

        print(f"[DEBUG REPORTE] Total anuncios procesados: {len(top_anuncios)}")
        for i, anuncio in enumerate(top_anuncios, 1):
            print(f"[DEBUG REPORTE] {i}. {anuncio['titulo_1']} - {anuncio['campaña']}")

        return render_template(
            'panel_cliente_google_ads/reporte_detallado_google_ads.html',
            cuenta=cuenta,
            nombre_nora=nombre_nora,
            stats=stats,
            top_campanas=top_campanas,
            top_anuncios=top_anuncios,
            total_anuncios=len(anuncios)
        )
        
    except Exception as e:
        print(f"[ERROR] Error en reporte detallado: {e}")
        return render_template('panel_cliente_google_ads/reporte_detallado_google_ads.html', 
                             error=f"Error generando reporte: {str(e)}", 
                             nombre_nora=nombre_nora,
                             cuenta={'nombre_cliente': 'N/A', 'customer_id': customer_id})
