
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from clientes.aura.utils.supabase_client import supabase
import os, requests
from datetime import datetime, timedelta
from clientes.aura.utils.meta_ads import (
    obtener_reporte_campanas,
    listar_anuncios_activos,
    obtener_ads_activos_cuenta,
    listar_campañas_activas
)

panel_cliente_meta_ads_bp = Blueprint(
    "panel_cliente_meta_ads_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/meta_ads"
)

@panel_cliente_meta_ads_bp.route("/")
def panel_cliente_meta_ads(nombre_nora):
    return render_template("panel_cliente_meta_ads/index.html", nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/reportes-interno")
def vista_reportes_meta_ads_interno(nombre_nora):
    try:
        respuesta = supabase.table("meta_ads_reportes_semanales") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .order("fecha_inicio", desc=True) \
            .execute()
        reportes = respuesta.data or []
        
        # Formatear las fechas y asegurarse que los campos existen
        for reporte in reportes:
            reporte['fecha_desde_fmt'] = reporte.get('fecha_inicio', '').split('T')[0] if reporte.get('fecha_inicio') else 'N/A'
            reporte['fecha_hasta_fmt'] = reporte.get('fecha_fin', '').split('T')[0] if reporte.get('fecha_fin') else 'N/A'
            # Asegurar que todos los campos numéricos existan
            reporte['importe_gastado_campañas'] = reporte.get('importe_gastado_campañas', 0)
            reporte['facebook_importe_gastado'] = reporte.get('facebook_importe_gastado', 0)
            reporte['instagram_importe_gastado'] = reporte.get('instagram_importe_gastado', 0)
            
    except Exception as e:
        print(f"❌ Error consultando reportes: {e}")
        reportes = []
    return render_template("panel_cliente_meta_ads/reportes.html", reportes=reportes, nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/reportes/<reporte_id>")
def detalle_reporte_ads(nombre_nora, reporte_id):
    try:
        # Obtener el reporte
        res = supabase.table("meta_ads_reportes_semanales").select("*").eq("id", reporte_id).single().execute()
        reporte = res.data or {}
        
        # Obtener información de la empresa si existe empresa_id
        empresa = {}
        if reporte.get('empresa_id'):
            try:
                empresa_res = supabase.table("cliente_empresas").select("*").eq("id", reporte.get('empresa_id')).single().execute()
                empresa = empresa_res.data or {}
            except Exception as e:
                print(f"⚠️ No se pudo cargar información de empresa: {e}")
                empresa = {}
        
        # Obtener anuncios relacionados al reporte (por cuenta publicitaria y fechas)
        anuncios = []
        if reporte.get('id_cuenta_publicitaria') and reporte.get('fecha_inicio') and reporte.get('fecha_fin'):
            try:
                anuncios_res = supabase.table("meta_ads_anuncios_detalle") \
                    .select("*") \
                    .eq("id_cuenta_publicitaria", reporte.get('id_cuenta_publicitaria')) \
                    .gte("fecha_inicio", reporte.get('fecha_inicio')) \
                    .lte("fecha_fin", reporte.get('fecha_fin')) \
                    .execute()
                anuncios = anuncios_res.data or []
            except Exception as e:
                print(f"⚠️ No se pudieron cargar anuncios: {e}")
                anuncios = []
                
    except Exception as e:
        print(f"❌ Error al cargar reporte: {e}")
        reporte = {}
        empresa = {}
        anuncios = []
        
    return render_template("panel_cliente_meta_ads/detalle_reporte_ads.html", 
                         reporte=reporte, 
                         empresa=empresa, 
                         anuncios=anuncios, 
                         nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/cuentas_publicitarias")
def vista_cuentas_publicitarias(nombre_nora):
    try:
        print(f"🔍 Buscando cuentas publicitarias para {nombre_nora}")
        
        # Consulta con join para obtener información de la empresa
        resultado = supabase.table("meta_ads_cuentas") \
            .select("*, empresa:cliente_empresas(id, nombre_empresa)") \
            .eq("nombre_nora", nombre_nora) \
            .execute()
            
        print("\n🔍 Query de Supabase:")
        print(resultado)
        
        cuentas = resultado.data or []
        print(f"✅ Se encontraron {len(cuentas)} cuentas")
        print("\nDatos originales de Supabase:")
        print(resultado.data)
        
        # Enriquecer datos y validar estructura
        for cuenta in cuentas:
            if not isinstance(cuenta, dict):
                print(f"⚠️ Estructura inválida en cuenta: {cuenta}")
                continue
            
            # Procesar información de empresa vinculada
            if empresa_data := cuenta.pop('empresa', None):  # Usamos pop para eliminar y obtener el valor
                cuenta['empresa_id'] = empresa_data.get('id')
                cuenta['empresa_nombre'] = empresa_data.get('nombre_empresa')
            else:
                cuenta['empresa_id'] = None
                cuenta['empresa_nombre'] = None
        
        # Ordenar cuentas: primero las que tienen empresa (por nombre de empresa), luego las que no tienen
        cuentas = sorted(cuentas, key=lambda x: (
            0 if x['empresa_nombre'] else 1,  # Primero las que tienen empresa (0), luego las que no (1)
            x['empresa_nombre'] or 'zzzz'  # Ordenar por nombre de empresa, 'zzzz' para las que no tienen
        ))
            
        print("Cuenta encontrada: {} (ID: {}) {}".format(
                cuenta.get('nombre_cliente', 'Sin nombre'),
                cuenta.get('id_cuenta_publicitaria', 'Sin ID'),
                '- Vinculada a: ' + cuenta['empresa_nombre'] if cuenta['empresa_nombre'] else '- Sin vincular'
            ))
        
        # Ordenar cuentas: primero las que tienen empresa (por nombre de empresa), luego las que no tienen
        cuentas = sorted(cuentas, key=lambda x: (
            0 if x['empresa_nombre'] else 1,  # Primero las que tienen empresa (0), luego las que no (1)
            (x['empresa_nombre'] or '').lower()  # Ordenar por nombre de empresa en minúsculas
        ))
    
    except Exception as e:
        print(f"❌ Error al consultar cuentas publicitarias: {e}")
        cuentas = []
    
    # Debug: Imprimir estructura completa de las cuentas
    for cuenta in cuentas:
        print("\n📋 DATOS DE CUENTA:")
        print(f"ID Cuenta: {cuenta.get('id_cuenta_publicitaria')}")
        print(f"Nombre: {cuenta.get('nombre_cliente')}")
        print(f"Empresa ID: {cuenta.get('empresa_id')}")
        print(f"Empresa Nombre: {cuenta.get('empresa_nombre')}")
        print(f"Datos completos: {cuenta}")

    return render_template("panel_cliente_meta_ads/cuentas_publicitarias.html", cuentas=cuentas, nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/importar_desde_meta', methods=['POST'])
def importar_cuentas_desde_meta(nombre_nora):
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        return jsonify({'ok': False, 'msg': 'No se encontró el token de Meta.'}), 400
    
    url = f"https://graph.facebook.com/v19.0/me/adaccounts"
    params = {
        "fields": "id,account_id,name,account_status",
        "access_token": token
    }
    cuentas = []
    try:
        while url:
            resp = requests.get(url, params=params if '?' not in url else None, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            cuentas.extend(data.get('data', []))
            paging = data.get('paging', {})
            url = paging.get('next')
            params = None
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Error consultando Meta: {e}'}), 500

    existentes = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria').eq('nombre_nora', nombre_nora).execute().data or []
    existentes_ids = {c['id_cuenta_publicitaria'] for c in existentes}
    nuevas = []
    
    for acc in cuentas:
        id_publicitaria = acc.get('account_id')
        if not id_publicitaria or id_publicitaria in existentes_ids:
            continue
        data = {
            'id_cuenta_publicitaria': id_publicitaria,
            'nombre_cliente': acc.get('name', ''),
            'nombre_nora': nombre_nora,
            'conectada': True,
            'account_status': acc.get('account_status', 0)
        }
        nuevas.append(data)
    
    if nuevas:
        supabase.table('meta_ads_cuentas').insert(nuevas).execute()
    return jsonify({'ok': True, 'agregadas': len(nuevas), 'total': len(cuentas)})

@panel_cliente_meta_ads_bp.route("/campañas_activas")
def campañas_activas(nombre_nora):
    cuenta_id = request.args.get('cuenta_id')
    if cuenta_id:
        fila = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("id_cuenta_publicitaria", cuenta_id) \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute() \
            .data
    else:
        fila = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute() \
            .data

    if not fila:
        return jsonify({"error": "Cuenta no encontrada"}), 404

    try:
        campañas = listar_campañas_activas(fila["id_cuenta_publicitaria"])
        return jsonify({"campañas": campañas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_cliente_meta_ads_bp.route('/lab')
def vista_lab_meta_ads(nombre_nora):
    return render_template("panel_cliente_meta_ads/lab.html", nombre_nora=nombre_nora)
def obtener_access_token():
    """
    Obtiene el token de acceso para la API de Meta desde las variables de entorno.
    Returns:
        str: Token de acceso o None si no se encuentra.
    """
    return os.getenv('META_ACCESS_TOKEN')

# Aquí terminan las importaciones y funciones auxiliares


@panel_cliente_meta_ads_bp.route('/agregar_cuenta', methods=['POST'])
def agregar_cuenta(nombre_nora):
    nombre_cliente = request.form.get('nombre_cliente')
    tipo_plataforma = request.form.get('tipo_plataforma')
    id_cuenta_publicitaria = request.form.get('id_cuenta_publicitaria')
    activo = request.form.get('activo') == 'on'
    account_status = 1 if activo else 2
    data = {
        'nombre_cliente': nombre_cliente,
        'tipo_plataforma': tipo_plataforma,
        'id_cuenta_publicitaria': id_cuenta_publicitaria,
        'account_status': account_status,
        'activo': activo,
        'nombre_nora': nombre_nora
    }
    supabase.table('meta_ads_cuentas').insert(data).execute()
    return redirect(url_for('panel_cliente_meta_ads_bp.panel_cliente_meta_ads', nombre_nora=nombre_nora))


@panel_cliente_meta_ads_bp.route('/campanas', methods=['GET'])
def vista_campanas(nombre_nora):
    return render_template('campanas_meta_ads.html', nombre_nora=nombre_nora)



@panel_cliente_meta_ads_bp.route('/campanas_activas_meta_ads')
def campanas_activas_meta_ads(nombre_nora):
    cuenta_id = request.args.get('cuenta_id', '')
    return render_template('campanas_activas_meta_ads.html', nombre_nora=nombre_nora, cuenta_id=cuenta_id)



@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/actualizar', methods=['POST'])
def actualizar_cuentas_publicitarias(nombre_nora):
    print(f"🔄 Iniciando actualización de cuentas publicitarias para Nora: {nombre_nora}")
    from clientes.aura.utils.meta_ads import obtener_info_cuenta_ads
    from datetime import datetime
    
    # Verificar token antes de empezar
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        return jsonify({'ok': False, 'msg': 'No se encontró el token de Meta.'}), 400
    
    try:
        # DEBUGGING: Verificar qué valor exacto tiene nombre_nora
        print(f"🔍 DEBUGGING - Valor exacto de nombre_nora: '{nombre_nora}' (tipo: {type(nombre_nora)})")
        
        # PASO 1: Primero verificar TODAS las cuentas sin filtros para ver qué hay en la tabla
        print("📋 PASO 1: Verificando TODAS las cuentas en la tabla meta_ads_cuentas...")
        todas_cuentas = supabase.table('meta_ads_cuentas') \
            .select("id_cuenta_publicitaria, nombre_cliente, nombre_nora, estado_actual") \
            .execute()
        
        print(f"📊 Total de cuentas en la tabla: {len(todas_cuentas.data) if todas_cuentas.data else 0}")
        if todas_cuentas.data:
            for cuenta in todas_cuentas.data[:5]:  # Mostrar solo las primeras 5
                print(f"   - ID: {cuenta.get('id_cuenta_publicitaria')} | Cliente: {cuenta.get('nombre_cliente')} | Nora: '{cuenta.get('nombre_nora')}' | Estado: {cuenta.get('estado_actual')}")
        
        # PASO 2: Buscar cuentas que coincidan exactamente con nombre_nora
        print(f"\n📋 PASO 2: Buscando cuentas con nombre_nora = '{nombre_nora}'...")
        cuentas_nora = supabase.table('meta_ads_cuentas') \
            .select("id_cuenta_publicitaria, nombre_cliente, nombre_nora, estado_actual") \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        print(f"� Cuentas encontradas para '{nombre_nora}': {len(cuentas_nora.data) if cuentas_nora.data else 0}")
        if cuentas_nora.data:
            for cuenta in cuentas_nora.data:
                print(f"   - ID: {cuenta.get('id_cuenta_publicitaria')} | Cliente: {cuenta.get('nombre_cliente')} | Estado: {cuenta.get('estado_actual')}")
        
        # PASO 3: Ahora aplicar el filtro de estado_actual
        print(f"\n📋 PASO 3: Aplicando filtro de estado_actual...")
        # Usar consulta que incluya explícitamente NULL values
        cuentas = supabase.table('meta_ads_cuentas') \
            .select("*, empresa:cliente_empresas(id, nombre_empresa, cliente_id)") \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        # Filtrar en Python para incluir NULL y excluir 'excluida'
        if cuentas.data:
            cuentas_filtradas = [
                cuenta for cuenta in cuentas.data 
                if cuenta.get('estado_actual') != 'excluida'
            ]
            cuentas.data = cuentas_filtradas
        
        print(f"📋 Query ejecutada: nombre_nora = '{nombre_nora}' (filtrado en Python para incluir NULL y excluir 'excluida')")
        print(f"📊 Respuesta final después del filtro: {len(cuentas.data) if cuentas.data else 0} cuentas")
        if cuentas.data:
            print("📊 Primeras 5 cuentas filtradas:")
            for cuenta in cuentas.data[:5]:
                print(f"   - {cuenta.get('nombre_cliente')} (ID: {cuenta.get('id_cuenta_publicitaria')}) - Estado: {cuenta.get('estado_actual', 'NULL')}")
        print(f"📊 Respuesta final de Supabase: data=[{len(cuentas.data) if cuentas.data else 0} cuentas] count=None")
        
        if not cuentas or not cuentas.data:
            print(f"⚠️ No se encontraron cuentas activas para {nombre_nora}")
            print("📝 Verificando si hay cuentas excluidas...")
            
            # Verificar si hay cuentas excluidas
            cuentas_excluidas = supabase.table('meta_ads_cuentas') \
                .select("id_cuenta_publicitaria, nombre_cliente, estado_actual") \
                .eq('nombre_nora', nombre_nora) \
                .eq('estado_actual', 'excluida') \
                .execute()
            
            if cuentas_excluidas.data:
                print(f"🚫 Encontradas {len(cuentas_excluidas.data)} cuentas excluidas:")
                for cuenta_exc in cuentas_excluidas.data:
                    print(f"   - {cuenta_exc.get('nombre_cliente', 'Sin nombre')} (ID: {cuenta_exc.get('id_cuenta_publicitaria')}) - Estado: {cuenta_exc.get('estado_actual')}")
            
            # Verificar si hay cuentas sin estado_actual
            cuentas_sin_estado = supabase.table('meta_ads_cuentas') \
                .select("id_cuenta_publicitaria, nombre_cliente, estado_actual") \
                .eq('nombre_nora', nombre_nora) \
                .is_('estado_actual', 'null') \
                .execute()
            
            if cuentas_sin_estado.data:
                print(f"❓ Encontradas {len(cuentas_sin_estado.data)} cuentas sin estado_actual:")
                for cuenta_sin in cuentas_sin_estado.data:
                    print(f"   - {cuenta_sin.get('nombre_cliente', 'Sin nombre')} (ID: {cuenta_sin.get('id_cuenta_publicitaria')}) - Estado: NULL")
            
            return jsonify({
                'ok': False,
                'msg': f'No se encontraron cuentas activas para {nombre_nora} (excluidas las marcadas como excluidas)',
                'cuentas_excluidas': len(cuentas_excluidas.data) if cuentas_excluidas.data else 0,
                'cuentas_sin_estado': len(cuentas_sin_estado.data) if cuentas_sin_estado.data else 0
            }), 404
            
        print(f"📊 Cuentas encontradas (sin excluidas): {len(cuentas.data)}")
        for cuenta in cuentas.data:
            print(f"   ✅ {cuenta.get('nombre_cliente', 'Sin nombre')} (ID: {cuenta.get('id_cuenta_publicitaria')}) - Estado: {cuenta.get('estado_actual', 'NULL')}")
        errores = []
        cuentas_actualizadas = []
        alertas_generadas = 0
        
        for cuenta in cuentas.data:
            cuenta_id = cuenta.get('id_cuenta_publicitaria')
            if not cuenta_id:
                print(f"⚠️ Cuenta sin ID: {cuenta}")
                continue
                
            try:
                print(f"🔄 Actualizando cuenta: {cuenta_id}")
                # Obtener información actualizada de Meta
                info = obtener_info_cuenta_ads(cuenta_id)
                print(f"📥 Info obtenida de Meta API para {cuenta_id}: {info}")
                
                update_data = {
                    'nombre_cliente': info.get('nombre_cliente', cuenta['nombre_cliente']),
                    'account_status': info.get('account_status', cuenta['account_status']),
                    'ads_activos': info.get('ads_activos', cuenta.get('ads_activos')),
                    'ultima_notificacion': datetime.utcnow().isoformat()
                }
                
                # Preservar nombre si viene vacío
                if not update_data['nombre_cliente'] or update_data['nombre_cliente'].strip() == '':
                    update_data['nombre_cliente'] = cuenta['nombre_cliente'] or 'Sin nombre'
                
                print(f"📝 Datos a actualizar en Supabase para {cuenta_id}: {update_data}")
                resp_update = supabase.table('meta_ads_cuentas').update(update_data).eq('id_cuenta_publicitaria', cuenta_id).execute()
                print(f"✅ Respuesta de update Supabase para {cuenta_id}: {resp_update}")

                # Verificar si la cuenta está inactiva y crear alerta
                if info.get('account_status', 0) != 1:
                    print(f"\n🚨 DETECTADA CUENTA INACTIVA:")
                    print(f"   ID Cuenta: {cuenta_id}")
                    print(f"   Nombre: {update_data['nombre_cliente']}")
                    print(f"   Estado: {info.get('account_status', 0)}")
                    
                    empresa_data = cuenta.get('empresa') or {}
                    # Crear alerta en Supabase
                    alerta_data = {
                        'nombre': 'Cuenta publicitaria inactiva',
                        'descripcion': f'La cuenta publicitaria {update_data["nombre_cliente"]} (ID: {cuenta_id}) se encuentra inactiva',
                        'tipo': 'meta_ads',
                        'evento_origen': 'meta_ads.sync_cuentas',
                        'condiciones': {'account_status': info.get('account_status', 0)},
                        'datos': {
                            'cuenta_id': cuenta_id,
                            'nombre_cuenta': update_data['nombre_cliente'],
                            'empresa_id': empresa_data.get('id') if empresa_data else None,
                            'empresa_nombre': empresa_data.get('nombre_empresa') if empresa_data else None
                        },
                        'prioridad': 'alta',
                        'nombre_nora': nombre_nora,
                        'cliente_id': empresa_data.get('cliente_id') if empresa_data else None,
                        'activa': True,
                        'vista': False,
                        'resuelta': False
                    }
                    
                    print("\n📝 DATOS DE LA ALERTA A GENERAR:")
                    print(f"   Empresa: {empresa_data.get('nombre_empresa', 'No vinculada') if empresa_data else 'No vinculada'}")
                    print(f"   Cliente ID: {empresa_data.get('cliente_id', 'No disponible') if empresa_data else 'No disponible'}")
                    print(f"   Descripción: {alerta_data['descripcion']}")
                    
                    resultado_insercion = supabase.table('alertas').insert(alerta_data).execute()
                    alertas_generadas += 1
                    
                    print("\n✅ ALERTA GENERADA EXITOSAMENTE:")
                    print(f"   Total alertas generadas: {alertas_generadas}")
                    print(f"   Respuesta Supabase: {resultado_insercion}")
                    
                    # Enviar notificaciones automáticamente
                    try:
                        from clientes.aura.utils.notificaciones import (
                            obtener_configuracion_notificaciones_por_empresa, 
                            enviar_notificaciones_alerta
                        )
                        
                        print("\n📧 INICIANDO ENVÍO DE NOTIFICACIONES:")
                        
                        # Obtener configuración de notificaciones
                        empresa_nombre = empresa_data.get('nombre_empresa')
                        if empresa_nombre:
                            print(f"📧 Buscando configuración para empresa: {empresa_nombre}")
                            configuraciones = obtener_configuracion_notificaciones_por_empresa(empresa_nombre)
                        else:
                            print("📧 No hay empresa vinculada, usando configuración general")
                            from clientes.aura.utils.notificaciones import obtener_configuracion_notificaciones
                            configuraciones = obtener_configuracion_notificaciones(nombre_nora)
                        
                        if configuraciones:
                            print(f"📧 Encontradas {len(configuraciones)} configuraciones de notificación")
                            notificaciones_enviadas = enviar_notificaciones_alerta(alerta_data, configuraciones)
                            
                            if notificaciones_enviadas:
                                print(f"✅ Notificaciones enviadas: {', '.join(notificaciones_enviadas)}")
                            else:
                                print("⚠️ No se pudieron enviar notificaciones")
                        else:
                            print("⚠️ No se encontró configuración de notificaciones")
                            
                    except Exception as notif_error:
                        print(f"❌ Error al enviar notificaciones: {notif_error}")
                        # No fallar la función principal por error en notificaciones
                
                cuentas_actualizadas.append({
                    'id_cuenta_publicitaria': cuenta_id,
                    'ads_activos': update_data['ads_activos'],
                    'nombre_cliente': update_data['nombre_cliente']
                })
                
            except Exception as e:
                error_msg = f"Error actualizando cuenta {cuenta_id}: {str(e)}"
                print(f"❌ {error_msg}")
                errores.append({'cuenta_id': cuenta_id, 'error': error_msg})
                continue
        
        # Retornar resultado
        if errores:
            return jsonify({
                'ok': False,
                'errores': errores,
                'cuentas': cuentas_actualizadas
            }), 207
            
        return jsonify({
            'ok': True,
            'cuentas': cuentas_actualizadas,
            'total_actualizadas': len(cuentas_actualizadas),
            'alertas_generadas': alertas_generadas
        })
        
    except Exception as e:
        error_msg = f"Error general actualizando cuentas: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            'ok': False,
            'error': error_msg
        }), 500

@panel_cliente_meta_ads_bp.route('/meta_ads/anuncios_activos_json')
def anuncios_activos_json(nombre_nora):
    """
    Devuelve en JSON los anuncios ACTIVOS de la cuenta seleccionada (por cuenta_id).
    """
    from clientes.aura.utils.meta_ads import listar_anuncios_activos
    cuenta_id = request.args.get('cuenta_id')
    if not cuenta_id:
        return jsonify({"error": "Falta cuenta_id"}), 400
    try:
        anuncios = listar_anuncios_activos(cuenta_id)
        return jsonify({"anuncios": anuncios})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/vincular_empresa', methods=['GET', 'POST'])
def vincular_empresa_a_cuenta(nombre_nora, cuenta_id):
    # importaciones ya están al inicio del archivo
    # Obtener la cuenta
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute().data
    if not cuenta:
        return "Cuenta publicitaria no encontrada", 404
    # Obtener empresas disponibles para la Nora
    empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        if not empresa_id:
            return render_template('vincular_empresa_cuenta.html', cuenta=cuenta, empresas=empresas, nombre_nora=nombre_nora, error='Debes seleccionar una empresa')
        # Actualizar la cuenta con el empresa_id
        supabase.table('meta_ads_cuentas').update({'empresa_id': empresa_id}).eq('id_cuenta_publicitaria', cuenta_id).execute()
        return redirect(url_for('panel_cliente_meta_ads_bp.vista_cuentas_publicitarias', nombre_nora=nombre_nora))
    return render_template('vincular_empresa_cuenta.html', cuenta=cuenta, empresas=empresas, nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/ads_activos', methods=['GET'])
def obtener_ads_activos_endpoint(nombre_nora, cuenta_id):
    from clientes.aura.utils.meta_ads import obtener_ads_activos_cuenta
    activos = obtener_ads_activos_cuenta(cuenta_id)
    print(f"[DEBUG] Ads activos para cuenta {cuenta_id}: {activos}")  # Debug agregado
    # Actualiza el campo en Supabase
    supabase.table('meta_ads_cuentas').update({'ads_activos': activos}).eq('id_cuenta_publicitaria', cuenta_id).execute()
    return jsonify({'ok': True, 'ads_activos': activos})

@panel_cliente_meta_ads_bp.route('/cuenta/<cuenta_id>', methods=['GET'])
def ficha_cuenta_publicitaria(nombre_nora, cuenta_id):
    cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute().data
    if not cuenta:
        return redirect(url_for('panel_cliente_meta_ads_bp.vista_cuentas_publicitarias', nombre_nora=nombre_nora))
    # Enriquecer con nombre y logo de empresa si está vinculada
    empresa_id = cuenta.get('empresa_id')
    cuenta['empresa_nombre'] = None
    cuenta['empresa_logo_url'] = None
    if empresa_id:
        empresa = supabase.table('cliente_empresas').select('nombre_empresa,logo_url').eq('id', empresa_id).single().execute().data
        if empresa:
            cuenta['empresa_nombre'] = empresa.get('nombre_empresa')
            cuenta['empresa_logo_url'] = empresa.get('logo_url')
    from datetime import datetime, timedelta
    hoy = datetime.utcnow().date()
    hace_7 = hoy - timedelta(days=7)
    # Traer todos los reportes de los últimos 7 días para la cuenta
    reportes_7d = supabase.table('meta_ads_reportes_semanales') \
        .select('campana_id,conjunto_id,anuncio_id,importe_gastado') \
        .gte('fecha_fin', hace_7.isoformat()) \
        .lte('fecha_fin', hoy.isoformat()) \
        .eq('id_cuenta_publicitaria', cuenta_id) \
        .execute().data or []
    # Campañas
    campanas = supabase.table('meta_ads_campañas').select('campana_id,nombre_campana').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    campanas_dict = {}
    for row in reportes_7d:
        cid = row.get('campana_id')
        if cid:
            campanas_dict.setdefault(cid, 0)
            campanas_dict[cid] += row.get('importe_gastado', 0) or 0
    campanas_filtradas = []
    for c in campanas:
        gasto_7d = round(campanas_dict.get(c['campana_id'], 0), 2)
        if gasto_7d > 0:
            c['gasto_7d'] = gasto_7d
            campanas_filtradas.append(c)
    # Conjuntos de anuncios
    conjuntos = supabase.table('meta_ads_conjuntos_anuncios').select('conjunto_id,nombre_conjunto').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    conjuntos_dict = {}
    for row in reportes_7d:
        coid = row.get('conjunto_id')
        if coid:
            conjuntos_dict.setdefault(coid, 0)
            conjuntos_dict[coid] += row.get('importe_gastado', 0) or 0
    conjuntos_filtrados = []
    for c in conjuntos:
        gasto_7d = round(conjuntos_dict.get(c['conjunto_id'], 0), 2)
        if gasto_7d > 0:
            c['gasto_7d'] = gasto_7d
            conjuntos_filtrados.append(c)
    # Anuncios
    anuncios = supabase.table('meta_ads_anuncios_detalle').select('anuncio_id,nombre_anuncio').eq('id_cuenta_publicitaria', cuenta_id).execute().data or []
    anuncios_dict = {}
    for row in reportes_7d:
        aid = row.get('anuncio_id')
        if aid:
            anuncios_dict.setdefault(aid, 0)
            anuncios_dict[aid] += row.get('importe_gastado', 0) or 0
    anuncios_filtrados = []
    for a in anuncios:
        gasto_7d = round(anuncios_dict.get(a['anuncio_id'], 0), 2)
        if gasto_7d > 0:
            a['gasto_7d'] = gasto_7d
            anuncios_filtrados.append(a)
    return render_template(
        'meta_ads_cuenta_ficha.html',
        cuenta=cuenta,
        nombre_nora=nombre_nora,
        campanas=campanas_filtradas,
        conjuntos=conjuntos_filtrados,
        anuncios=anuncios_filtrados
    )

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/test_conexion')
def test_conexion_cuenta(nombre_nora, cuenta_id):
    """
    Prueba la conexión con la cuenta publicitaria de Meta.
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora.
        cuenta_id (str): ID de la cuenta publicitaria.
        
    Returns:
        flask.Response: Respuesta JSON con el resultado de la prueba.
    """
    try:
        # Paso 1: Verificar credenciales y token
        cuenta = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', cuenta_id).single().execute()
        if not cuenta.data:
            return jsonify({
                'ok': False,
                'paso': 'token',
                'error': 'Cuenta no encontrada en la base de datos'
            })

        access_token = obtener_access_token()
        if not access_token:
            return jsonify({
                'ok': False,
                'paso': 'token',
                'error': 'No se pudo obtener el token de acceso. Verifica la configuración de Meta.'
            })

        # Paso 2: Verificar acceso a la cuenta
        url = f"https://graph.facebook.com/v17.0/{cuenta_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', 'Error desconocido')
            return jsonify({
                'ok': False,
                'paso': 'cuenta',
                'error': f'Error al acceder a la cuenta: {error_msg}'
            })

        # Paso 3: Verificar permisos
        permisos_url = f"https://graph.facebook.com/v17.0/{cuenta_id}/assigned_users"
        permisos_response = requests.get(permisos_url, headers=headers)
        
        if permisos_response.status_code != 200:
            return jsonify({
                'ok': False,
                'paso': 'permisos',
                'error': 'No se pueden verificar los permisos de la cuenta'
            })

        # Paso 4: Verificar acceso a anuncios
        ads_url = f"https://graph.facebook.com/v17.0/{cuenta_id}/ads"
        ads_params = {
            'fields': 'status,name',
            'limit': 1000,
            'status': ['ACTIVE']
        }
        ads_response = requests.get(ads_url, headers=headers, params=ads_params)
        
        if not ads_response.ok:
            return jsonify({
                'ok': False,
                'paso': 'anuncios',
                'error': 'No se puede acceder a los anuncios de la cuenta'
            })

        # Todo OK
        ads_data = ads_response.json()
        cuenta_data = response.json()
        
        detalles = {
            'activos': len(ads_data.get('data', [])),
            'permisos': 'Completos',  # Podríamos detallar más según los permisos específicos
            'status': cuenta_data.get('status', 'UNKNOWN'),
            'id': cuenta_id
        }
        
        return jsonify({
            'ok': True,
            'detalles': detalles,
            'status': cuenta_data.get('status')
        })
            
    except Exception as e:
        print(f"❌ Error en test de conexión: {str(e)}")
        return jsonify({
            'ok': False,
            'paso': 'general',
            'error': f'Error inesperado: {str(e)}'
        })
