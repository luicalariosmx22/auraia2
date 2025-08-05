INSERT INTO "public"."funciones_automatizables" ("id", "modulo", "nombre_funcion", "descripcion", "parametros", "docstring", "es_automatizable", "activa", "categoria", "ejemplo_uso", "creado_en", "actualizado_en", "envia_notificacion", "codigo_fuente", "linea_inicio", "ruta_modulo_python", "tipo_archivo", "archivo_origen", "ruta_completa", "metodo_deteccion") VALUES ('0160a4d9-001c-47a8-8431-ecf457300cdf', 'meta_ads', 'vista_reportes_meta_ads', 'Función vista_reportes_meta_ads', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"reportes.py","funcion":"vista_reportes_meta_ads","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:29.634069+00', '2025-08-01 15:13:51.038625+00', 'false', 'def vista_reportes_meta_ads(nombre_nora):
    try:
        respuesta = supabase.table("meta_ads_reportes_semanales") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .order("fecha_desde", desc=True) \
            .execute()
        
        reportes = respuesta.data or []
        return render_template("panel_cliente_meta_ads/reportes.html", nombre_nora=nombre_nora, reportes=reportes)
    except Exception as e:
        print(f"❌ Error consultando reportes: {e}")
        return render_template("panel_cliente_meta_ads/reportes.html", nombre_nora=nombre_nora, reportes=[])
    
@panel_cliente_meta_ads_bp.route('/prereportes/eliminar', methods=['POST'])', '7', 'clientes.aura.routes.panel_cliente_meta_ads.reportes', 'python', 'reportes.py', 'clientes/aura/routes/panel_cliente_meta_ads\reportes.py', 'escaneo_directo'), ('06cb16be-b108-4c1f-8c5d-2bbe8d93a32b', 'meta_ads', 'descargar_reporte_semanal_panel', 'Devuelve todos los datos de un reporte semanal por UUID en formato JSON', '{"uuid":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Devuelve todos los datos de un reporte semanal por UUID en formato JSON', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"descargas.py","funcion":"descargar_reporte_semanal_panel","parametros":{"uuid":"ejemplo_uuid"}}', '2025-08-01 14:27:20.60754+00', '2025-08-01 15:13:43.433452+00', 'false', 'def descargar_reporte_semanal_panel(uuid):
    """Devuelve todos los datos de un reporte semanal por UUID en formato JSON"""
    try:
        reporte = supabase.table('meta_ads_reportes_semanales')\
            .select('*')\
            .eq('uuid', uuid)\
            .execute().data

        if not reporte:
            todos_reportes = supabase.table('meta_ads_reportes_semanales')\
                .select('uuid')\
                .execute().data
            print(f"[DEBUG] UUID {uuid} no encontrado. Reportes disponibles: {todos_reportes}")
            return jsonify({'error': 'Reporte no encontrado'}), 404

        return jsonify({
            'ok': True,
            'reporte': reporte[0] if reporte else None
        })
    except Exception as e:
        print(f"Error al obtener reporte {uuid}: {str(e)}")
        return jsonify({
            'error': 'Error interno al obtener el reporte',
            'details': str(e)
        }), 500
', '7', 'clientes.aura.routes.panel_cliente_meta_ads.descargas', 'python', 'descargas.py', 'clientes/aura/routes/panel_cliente_meta_ads\descargas.py', 'escaneo_directo'), ('1e3d8a27-37a7-4d80-9d5e-9e8566308058', 'meta_ads', 'vista_estadisticas_ads', 'Vista principal para estadísticas de Meta Ads', '{}', 'Vista principal para estadísticas de Meta Ads', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"estadisticas.py","funcion":"vista_estadisticas_ads","parametros":{}}', '2025-08-01 14:27:21.003861+00', '2025-08-01 15:13:43.808728+00', 'false', 'def vista_estadisticas_ads():
    """Vista principal para estadísticas de Meta Ads"""
    if request.method == 'POST':
        fecha_fin = datetime.utcnow().date()
        fecha_inicio = fecha_fin - timedelta(days=6)
        # Aquí debes obtener el ID de la cuenta publicitaria, por ejemplo desde el request o una variable
        cuenta_id = request.form.get('cuenta_id') or request.args.get('cuenta_id')
        if not cuenta_id:
            return jsonify({'ok': False, 'error': 'Falta cuenta_id'}), 400
        campañas = obtener_reporte_campanas(cuenta_id, str(fecha_inicio), str(fecha_fin))
        return jsonify({'ok': True, 'campañas': campañas})
    return render_template('panel_cliente_meta_ads/estadisticas_ads.html')
', '18', 'clientes.aura.routes.panel_cliente_meta_ads.estadisticas', 'python', 'estadisticas.py', 'clientes/aura/routes/panel_cliente_meta_ads\estadisticas.py', 'escaneo_directo'), ('2985dc4a-a7ed-483a-a4ab-a3f6a72c3562', 'meta_ads', 'obtener_fields_para_meta', 'Convierte nombres de columnas locales a campos de la API de Meta.', '{"columnas":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Convierte nombres de columnas locales a campos de la API de Meta.', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"columnas_meta_ads.py","funcion":"obtener_fields_para_meta","parametros":{"columnas":"ejemplo_columnas"}}', '2025-08-01 14:27:34.205403+00', '2025-08-01 15:13:55.207282+00', 'false', 'def obtener_fields_para_meta(columnas):
    """Convierte nombres de columnas locales a campos de la API de Meta."""
    fields = []
    for col in columnas:
        if col in MAPEO_COLUMNAS_META_ADS:
            fields.append(MAPEO_COLUMNAS_META_ADS[col])
    # Campos obligatorios para identificación
    fields.extend(['ad_id', 'adset_id', 'campaign_id'])
    return list(set(fields))  # Eliminar duplicados
', '24', 'clientes.aura.routes.panel_cliente_meta_ads.utils.columnas_meta_ads', 'python', 'columnas_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\utils\columnas_meta_ads.py', 'escaneo_directo'), ('29c2b190-be59-4056-91f5-195fbc6f8a9e', 'meta_ads', 'vista_sincronizacion_semanal', 'Función vista_sincronizacion_semanal', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"sincronizador.py","funcion":"vista_sincronizacion_semanal","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:30.422768+00', '2025-08-01 15:13:51.651736+00', 'false', 'def vista_sincronizacion_semanal(nombre_nora):
    try:
        sincronizar_reportes_semanales()
        flash("✅ Reportes sincronizados correctamente.", "success")
    except Exception as e:
        flash(f"❌ Error al sincronizar: {str(e)}", "danger")
    return redirect(url_for("panel_cliente_meta_ads_bp.panel_cliente_meta_ads", nombre_nora=nombre_nora))
', '7', 'clientes.aura.routes.panel_cliente_meta_ads.sincronizador', 'python', 'sincronizador.py', 'clientes/aura/routes/panel_cliente_meta_ads\sincronizador.py', 'escaneo_directo'), ('396da7b9-a9ee-41eb-971b-0939535917bc', 'meta_ads', 'ficha_cuenta_publicitaria', 'Función ficha_cuenta_publicitaria', '{"cuenta_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"ficha_cuenta_publicitaria","parametros":{"cuenta_id":"ejemplo_cuenta_id","nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:28.855921+00', '2025-08-01 15:13:50.364402+00', 'false', 'def ficha_cuenta_publicitaria(nombre_nora, cuenta_id):
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

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/test_conexion')', '419', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('443c7351-7eb0-45db-a6cc-d0aadc942d48', 'meta_ads', 'actualizar_cuentas_publicitarias', 'Función actualizar_cuentas_publicitarias', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'sincronizacion', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"actualizar_cuentas_publicitarias","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:27.081519+00', '2025-08-01 15:13:49.021895+00', 'false', 'def actualizar_cuentas_publicitarias(nombre_nora):
    print(f"🔄 Iniciando actualización de cuentas publicitarias para Nora: {nombre_nora}")
    from clientes.aura.utils.meta_ads import obtener_info_cuenta_ads
    from datetime import datetime
    
    # Verificar token antes de empezar
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        return jsonify({'ok': False, 'msg': 'No se encontró el token de Meta.'}), 400
    
    try:
        # Obtener cuentas con información de empresas
        cuentas = supabase.table('meta_ads_cuentas') \
            .select("*, empresa:cliente_empresas(id, nombre_empresa, cliente_id)") \
            .eq('nombre_visible', nombre_nora) \
            .execute()
        
        if not cuentas or not cuentas.data:
            return jsonify({
                'ok': False,
                'msg': f'No se encontraron cuentas para {nombre_nora}'
            }), 404
            
        print(f"📊 Cuentas encontradas: {len(cuentas.data)}")
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

@panel_cliente_meta_ads_bp.route('/meta_ads/anuncios_activos_json')', '243', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('46b1563c-cd8e-4ede-954d-748d9ef7185f', 'meta_ads', 'importar_cuentas_desde_meta', 'Función importar_cuentas_desde_meta', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"importar_cuentas_desde_meta","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:24.053183+00', '2025-08-01 15:13:46.409192+00', 'false', 'def importar_cuentas_desde_meta(nombre_nora):
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

    existentes = supabase.table('meta_ads_cuentas').select('id_cuenta_publicitaria').eq('nombre_visible', nombre_nora).execute().data or []
    existentes_ids = {c['id_cuenta_publicitaria'] for c in existentes}
    nuevas = []
    
    for acc in cuentas:
        id_publicitaria = acc.get('account_id')
        if not id_publicitaria or id_publicitaria in existentes_ids:
            continue
        data = {
            'id_cuenta_publicitaria': id_publicitaria,
            'nombre_cliente': acc.get('name', ''),
            'nombre_visible': nombre_nora,
            'conectada': True,
            'account_status': acc.get('account_status', 0)
        }
        nuevas.append(data)
    
    if nuevas:
        supabase.table('meta_ads_cuentas').insert(nuevas).execute()
    return jsonify({'ok': True, 'agregadas': len(nuevas), 'total': len(cuentas)})

@panel_cliente_meta_ads_bp.route("/campañas_activas")', '124', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('51911d15-10bb-4079-97d0-c2fd978c1d8d', 'meta_ads', 'campañas_activas', 'Función campañas_activas', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"campañas_activas","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:24.513578+00', '2025-08-01 15:13:46.766223+00', 'false', 'def campañas_activas(nombre_nora):
    cuenta_id = request.args.get('cuenta_id')
    if cuenta_id:
        fila = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("id_cuenta_publicitaria", cuenta_id) \
            .eq("nombre_visible", nombre_nora) \
            .single() \
            .execute() \
            .data
    else:
        fila = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria") \
            .eq("nombre_visible", nombre_nora) \
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

@panel_cliente_meta_ads_bp.route('/lab')', '169', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('55dfc8cc-3a7b-4326-b1bc-5600c51ede16', 'meta_ads', 'obtener_breakdowns', 'Función obtener_breakdowns', '{}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"validar_columnas_meta_ads.py","funcion":"obtener_breakdowns","parametros":{}}', '2025-08-01 14:27:34.67088+00', '2025-08-01 15:13:56.275342+00', 'false', 'def obtener_breakdowns():
    return list(BREAKDOWNS_VALIDOS)
', '19', 'clientes.aura.routes.panel_cliente_meta_ads.utils.validar_columnas_meta_ads', 'python', 'validar_columnas_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\utils\validar_columnas_meta_ads.py', 'escaneo_directo'), ('5a771849-1648-46f3-9ec9-09b7b2380af8', 'meta_ads', 'obtener_estado', 'Función obtener_estado', '{}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"vista_sincronizacion.py","funcion":"obtener_estado","parametros":{}}', '2025-08-01 14:27:33.013332+00', '2025-08-01 15:13:53.966479+00', 'false', 'def obtener_estado():
    try:
        ultima_sync = supabase.table('meta_ads_sync_log').select('*').order('created_at', desc=True).limit(1).execute()
        if ultima_sync.data:
            return jsonify({
                'ok': True,
                'estado': ultima_sync.data[0].get('estado', 'desconocido'),
                'ultima_actualizacion': ultima_sync.data[0].get('created_at')
            })
    except Exception as e:
        print(f"Error al obtener estado: {e}")
    return jsonify({'ok': False, 'error': 'No se pudo obtener el estado'})

@vista_sincronizacion_bp.route('/ultimas_sincronizaciones')', '12', 'clientes.aura.routes.panel_cliente_meta_ads.vista_sincronizacion', 'python', 'vista_sincronizacion.py', 'clientes/aura/routes/panel_cliente_meta_ads\vista_sincronizacion.py', 'escaneo_directo'), ('63661742-5599-47ea-a4d5-cc6faca8ef41', 'meta_ads', 'obtener_ads_activos_endpoint', 'Función obtener_ads_activos_endpoint', '{"cuenta_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"obtener_ads_activos_endpoint","parametros":{"cuenta_id":"ejemplo_cuenta_id","nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:28.395671+00', '2025-08-01 15:13:50.06532+00', 'false', 'def obtener_ads_activos_endpoint(nombre_nora, cuenta_id):
    from clientes.aura.utils.meta_ads import obtener_ads_activos_cuenta
    activos = obtener_ads_activos_cuenta(cuenta_id)
    print(f"[DEBUG] Ads activos para cuenta {cuenta_id}: {activos}")  # Debug agregado
    # Actualiza el campo en Supabase
    supabase.table('meta_ads_cuentas').update({'ads_activos': activos}).eq('id_cuenta_publicitaria', cuenta_id).execute()
    return jsonify({'ok': True, 'ads_activos': activos})

@panel_cliente_meta_ads_bp.route('/cuenta/<cuenta_id>', methods=['GET'])', '410', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('744b1fbd-47e0-4fd3-9045-e4061f074e6b', 'meta_ads', 'vista_campanas', 'Función vista_campanas', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"vista_campanas","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:26.167452+00', '2025-08-01 15:13:48.246537+00', 'false', 'def vista_campanas(nombre_nora):
    return render_template('campanas_meta_ads.html', nombre_nora=nombre_nora)



@panel_cliente_meta_ads_bp.route('/campanas_activas_meta_ads')', '230', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('792551f4-516e-49ef-b144-5d254666d87e', 'meta_ads', 'vincular_empresa_a_cuenta', 'Función vincular_empresa_a_cuenta', '{"cuenta_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"vincular_empresa_a_cuenta","parametros":{"cuenta_id":"ejemplo_cuenta_id","nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:27.976593+00', '2025-08-01 15:13:49.707222+00', 'false', 'def vincular_empresa_a_cuenta(nombre_nora, cuenta_id):
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

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/ads_activos', methods=['GET'])', '392', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('7f348f8d-8ace-4b30-b9da-5d0ebc1bc411', 'meta_ads', 'panel_cliente_meta_ads', 'Función panel_cliente_meta_ads', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"panel_cliente_meta_ads","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:22.334778+00', '2025-08-01 15:13:44.942411+00', 'false', 'def panel_cliente_meta_ads(nombre_nora):
    return render_template("panel_cliente_meta_ads/index.html", nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/reportes-interno")', '20', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('84f16377-528b-42a4-ad8b-24d2ec700c87', 'meta_ads', 'anuncios_activos_json', 'Devuelve en JSON los anuncios ACTIVOS de la cuenta seleccionada (por cuenta_id).', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Devuelve en JSON los anuncios ACTIVOS de la cuenta seleccionada (por cuenta_id).', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"anuncios_activos_json","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:27.578513+00', '2025-08-01 15:13:49.407346+00', 'false', 'def anuncios_activos_json(nombre_nora):
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



@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/<cuenta_id>/vincular_empresa', methods=['GET', 'POST'])', '375', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('893a817f-5844-4e17-ab7c-0dd6e16734f6', 'meta_ads', 'vista_sincronizacion', 'Función vista_sincronizacion', '{}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"vista_sincronizacion.py","funcion":"vista_sincronizacion","parametros":{}}', '2025-08-01 14:27:32.555032+00', '2025-08-01 15:13:53.609133+00', 'false', 'def vista_sincronizacion():
    return render_template('panel_cliente_meta_ads/vista_sincronizacion.html')

@vista_sincronizacion_bp.route('/obtener_estado')', '8', 'clientes.aura.routes.panel_cliente_meta_ads.vista_sincronizacion', 'python', 'vista_sincronizacion.py', 'clientes/aura/routes/panel_cliente_meta_ads\vista_sincronizacion.py', 'escaneo_directo'), ('8ce6fdfd-c444-4415-a7eb-e8d4e81376d7', 'meta_ads', 'ultimas_sincronizaciones', 'Función ultimas_sincronizaciones', '{}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"vista_sincronizacion.py","funcion":"ultimas_sincronizaciones","parametros":{}}', '2025-08-01 14:27:33.413377+00', '2025-08-01 15:13:54.381274+00', 'false', 'def ultimas_sincronizaciones():
    try:
        syncs = supabase.table('meta_ads_sync_log').select('*').order('created_at', desc=True).limit(10).execute()
        return jsonify({'ok': True, 'sincronizaciones': syncs.data})
    except Exception as e:
        print(f"Error al obtener sincronizaciones: {e}")
        return jsonify({'ok': False, 'error': str(e)})
', '26', 'clientes.aura.routes.panel_cliente_meta_ads.vista_sincronizacion', 'python', 'vista_sincronizacion.py', 'clientes/aura/routes/panel_cliente_meta_ads\vista_sincronizacion.py', 'escaneo_directo'), ('8dd182a5-b035-442d-a148-3ead90ebcd52', 'meta_ads', 'obtener_nombres_batch', 'Obtiene nombres de múltiples objetos usando batch requests', '{"tipo":{"tipo":"Any","requerido":false,"valor_defecto":"''campaign''"},"batch_size":{"tipo":"Any","requerido":false,"valor_defecto":"50"},"object_ids":{"tipo":"Any","requerido":true,"valor_defecto":null},"access_token":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Obtiene nombres de múltiples objetos usando batch requests', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"helpers.py","funcion":"obtener_nombres_batch","parametros":{"object_ids":"ejemplo_object_ids","access_token":"ejemplo_access_token"}}', '2025-08-01 14:27:21.872599+00', '2025-08-01 15:13:44.580014+00', 'false', 'def obtener_nombres_batch(object_ids, access_token, tipo='campaign', batch_size=50):
    """
    Obtiene nombres de múltiples objetos usando batch requests
    """
    if not object_ids:
        return {}
    
    nombres = {}
    import requests
    import time
    
    for i in range(0, len(object_ids), batch_size):
        batch = object_ids[i:i + batch_size]
        fields = 'id,name' if tipo == 'campaign' else 'id,name'
        
        try:
            ids_str = ','.join(batch)
            url = f"https://graph.facebook.com/v19.0/?ids={ids_str}&fields={fields}&access_token={access_token}"
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                for id_, info in data.items():
                    nombres[id_] = info.get('name', f"{tipo} {id_}")
            else:
                print(f"Error {r.status_code} obteniendo nombres batch: {r.text}")
                
        except Exception as e:
            print(f"Error en batch request: {e}")
            continue
            
        time.sleep(1)  # Pausa entre batches
        
    return nombres
', '16', 'clientes.aura.routes.panel_cliente_meta_ads.helpers', 'python', 'helpers.py', 'clientes/aura/routes/panel_cliente_meta_ads\helpers.py', 'escaneo_directo'), ('91fd6459-d871-4e27-ac96-7877ee2b202f', 'meta_ads', 'vista_cuentas_publicitarias', 'Función vista_cuentas_publicitarias', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"vista_cuentas_publicitarias","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:23.64217+00', '2025-08-01 15:13:46.044347+00', 'false', 'def vista_cuentas_publicitarias(nombre_nora):
    try:
        print(f"🔍 Buscando cuentas publicitarias para {nombre_nora}")
        
        # Consulta con join para obtener información de la empresa
        resultado = supabase.table("meta_ads_cuentas") \
            .select("*, empresa:cliente_empresas(id, nombre_empresa)") \
            .eq("nombre_visible", nombre_nora) \
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

@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/importar_desde_meta', methods=['POST'])', '58', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('966058ac-843b-4600-b4fb-717e83908bd4', 'meta_ads', 'campanas_activas_meta_ads', 'Función campanas_activas_meta_ads', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"campanas_activas_meta_ads","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:26.62595+00', '2025-08-01 15:13:48.609242+00', 'false', 'def campanas_activas_meta_ads(nombre_nora):
    cuenta_id = request.args.get('cuenta_id', '')
    return render_template('campanas_activas_meta_ads.html', nombre_nora=nombre_nora, cuenta_id=cuenta_id)



@panel_cliente_meta_ads_bp.route('/cuentas_publicitarias/actualizar', methods=['POST'])', '236', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('a7f11e13-d5fe-4e7c-9682-8b6fcce6971d', 'meta_ads', 'test_conexion_cuenta', 'Prueba la conexión con la cuenta publicitaria de Meta.', '{"cuenta_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Prueba la conexión con la cuenta publicitaria de Meta.
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora.
        cuenta_id (str): ID de la cuenta publicitaria.
        
    Returns:
        flask.Response: Respuesta JSON con el resultado de la prueba.', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"test_conexion_cuenta","parametros":{"cuenta_id":"ejemplo_cuenta_id","nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:29.311005+00', '2025-08-01 15:13:50.720712+00', 'false', 'def test_conexion_cuenta(nombre_nora, cuenta_id):
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
', '494', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('b0567e6e-1de2-43f6-99ff-dd57f8e029b8', 'meta_ads', 'vista_lab_meta_ads', 'Función vista_lab_meta_ads', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"vista_lab_meta_ads","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:24.915706+00', '2025-08-01 15:13:47.13455+00', 'false', 'def vista_lab_meta_ads(nombre_nora):
    return render_template("panel_cliente_meta_ads/lab.html", nombre_nora=nombre_nora)', '197', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('b4edce35-f5d6-4d4e-98fa-02e04b1cb9ea', 'meta_ads', 'detalle_reporte_ads', 'Función detalle_reporte_ads', '{"reporte_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"detalle_reporte_ads","parametros":{"reporte_id":"ejemplo_reporte_id","nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:23.256307+00', '2025-08-01 15:13:45.680055+00', 'false', 'def detalle_reporte_ads(nombre_nora, reporte_id):
    try:
        res = supabase.table("meta_ads_reportes_semanales").select("*").eq("id", reporte_id).single().execute()
        reporte = res.data or {}
    except Exception as e:
        print(f"❌ Error al cargar reporte: {e}")
        reporte = {}
    return render_template("panel_cliente_meta_ads/detalle_reporte_ads.html", reporte=reporte, nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/cuentas_publicitarias")', '48', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('c5f84147-038e-44c0-8ddb-df700ab9f3e1', 'meta_ads', 'agregar_cuenta', 'Función agregar_cuenta', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"agregar_cuenta","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:25.840202+00', '2025-08-01 15:13:47.937965+00', 'false', 'def agregar_cuenta(nombre_nora):
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
        'nombre_visible': nombre_nora
    }
    supabase.table('meta_ads_cuentas').insert(data).execute()
    return redirect(url_for('panel_cliente_meta_ads_bp.panel_cliente_meta_ads', nombre_nora=nombre_nora))


@panel_cliente_meta_ads_bp.route('/campanas', methods=['GET'])', '211', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('cd081bfd-db4f-4465-9c32-d69c24a7d170', 'meta_ads', 'ver_reporte_meta_ads', 'Vista de detalle de un reporte de Meta Ads', '{"uuid":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Vista de detalle de un reporte de Meta Ads', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"vistas.py","funcion":"ver_reporte_meta_ads","parametros":{"uuid":"ejemplo_uuid"}}', '2025-08-01 14:27:31.605589+00', '2025-08-01 15:13:52.895656+00', 'false', 'def ver_reporte_meta_ads(uuid):
    """Vista de detalle de un reporte de Meta Ads"""
    try:
        reporte = supabase.table('meta_ads_reportes_semanales')\
            .select('*')\
            .eq('id', uuid)\
            .single()\
            .execute()\
            .data

        print("Datos del reporte:", reporte)  # Para debug

        if not reporte:
            return jsonify({
                'error': 'Reporte no encontrado'
            }), 404

        return render_template('panel_cliente_meta_ads/detalle_reporte.html', 
                            reporte=reporte)

    except Exception as e:
        print(f"Error al obtener reporte: {e}")
        return jsonify({
            'error': f'Error al obtener reporte: {str(e)}'
        }), 500

@panel_cliente_meta_ads_bp.route("/dashboard", methods=["GET"])', '6', 'clientes.aura.routes.panel_cliente_meta_ads.vistas', 'python', 'vistas.py', 'clientes/aura/routes/panel_cliente_meta_ads\vistas.py', 'escaneo_directo'), ('cd395037-a906-4b6d-95ae-b6b04eec91e4', 'meta_ads', 'sincronizar_reportes_semanales', 'Función sincronizar_reportes_semanales', '{}', '', 'true', 'true', 'sincronizacion', '{"modulo":"meta_ads","archivo":"sincronizador_semanal.py","funcion":"sincronizar_reportes_semanales","parametros":{}}', '2025-08-01 14:27:31.212146+00', '2025-08-01 15:13:52.504496+00', 'false', 'def sincronizar_reportes_semanales():
    fecha_inicio, fecha_fin = obtener_rango_semana_actual()
    print(f"📆 Sincronizando semana del {fecha_inicio} al {fecha_fin}")

    # Obtener datos de anuncios
    anuncios_res = supabase.table("meta_ads_anuncios_detalle").select("*").gte("fecha_inicio", fecha_inicio).lte("fecha_fin", fecha_fin).execute()
    anuncios = anuncios_res.data
    if not anuncios:
        print("⚠️ No hay datos de anuncios para esta semana.")
        return

    # Agrupar por empresa_id y cuenta
    agrupados = {}
    for a in anuncios:
        clave = (a["empresa_id"], a["id_cuenta_publicitaria"])
        if clave not in agrupados:
            agrupados[clave] = []
        agrupados[clave].append(a)

    # Insertar reportes por cuenta
    registros = []
    for (empresa_id, cuenta_id), items in agrupados.items():
        reporte = {
            "id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
            "id_cuenta_publicitaria": cuenta_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_campañas": len(set([x["campaign_id"] for x in items if x.get("campaign_id")])),
            "importe_gastado_anuncios": sum([x.get("spend", 0) for x in items]),
            "impresiones": sum([x.get("impressions", 0) for x in items]),
            "alcance": sum([x.get("reach", 0) for x in items]),
            "clicks": sum([x.get("clicks", 0) for x in items]),
            "link_clicks": sum([x.get("link_clicks", 0) for x in items]),
            "mensajes": sum([x.get("messaging_conversations_started", 0) for x in items]),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Verifica si ya existe
        existente = supabase.table("meta_ads_reportes_semanales") \
            .select("id") \
            .eq("empresa_id", empresa_id) \
            .eq("id_cuenta_publicitaria", cuenta_id) \
            .eq("fecha_inicio", fecha_inicio) \
            .eq("fecha_fin", fecha_fin) \
            .execute()

        if not existente.data:
            registros.append(reporte)

    if registros:
        supabase.table("meta_ads_reportes_semanales").insert(registros).execute()
        print(f"✅ Se insertaron {len(registros)} reportes semanales.")
    else:
        print("ℹ️ No se insertaron registros. Ya existen para esta semana.")
', '13', 'clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal', 'python', 'sincronizador_semanal.py', 'clientes/aura/routes/panel_cliente_meta_ads\sincronizador_semanal.py', 'escaneo_directo'), ('cda3b5e0-7bee-4444-ac3f-bb221edc5ae1', 'meta_ads', 'obtener_rango_semana_actual', 'Función obtener_rango_semana_actual', '{}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"sincronizador_semanal.py","funcion":"obtener_rango_semana_actual","parametros":{}}', '2025-08-01 14:27:30.819911+00', '2025-08-01 15:13:52.074555+00', 'false', 'def obtener_rango_semana_actual():
    hoy = datetime.utcnow().date()
    fin = hoy - timedelta(days=hoy.weekday() + 1)
    inicio = fin - timedelta(days=6)
    return inicio.isoformat(), fin.isoformat()
', '7', 'clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal', 'python', 'sincronizador_semanal.py', 'clientes/aura/routes/panel_cliente_meta_ads\sincronizador_semanal.py', 'escaneo_directo'), ('cdf5f4fd-7d58-4ecd-8f5d-18040f5b8363', 'meta_ads', 'eliminar_prereporte', 'Elimina un prereporte guardado en Supabase usando su ID.', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Elimina un prereporte guardado en Supabase usando su ID.', 'true', 'true', 'mantenimiento', '{"modulo":"meta_ads","archivo":"reportes.py","funcion":"eliminar_prereporte","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:30.02862+00', '2025-08-01 15:13:51.336705+00', 'false', 'def eliminar_prereporte(nombre_nora):
    """
    Elimina un prereporte guardado en Supabase usando su ID.
    """
    reporte_id = request.json.get("id") or request.form.get("id")
    if not reporte_id:
        return jsonify({"ok": False, "error": "Falta ID de prereporte"}), 400
    try:
        supabase.table("meta_ads_reportes_semanales").delete().eq("id", reporte_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al eliminar prereporte: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
', '22', 'clientes.aura.routes.panel_cliente_meta_ads.reportes', 'python', 'reportes.py', 'clientes/aura/routes/panel_cliente_meta_ads\reportes.py', 'escaneo_directo'), ('ce9edda3-f920-4beb-b3f9-2baf589855fe', 'meta_ads', 'vista_reportes_meta_ads_interno', 'Función vista_reportes_meta_ads_interno', '{"nombre_nora":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"vista_reportes_meta_ads_interno","parametros":{"nombre_nora":"ejemplo_nombre_nora"}}', '2025-08-01 14:27:22.863399+00', '2025-08-01 15:13:45.352147+00', 'false', 'def vista_reportes_meta_ads_interno(nombre_nora):
    try:
        respuesta = supabase.table("meta_ads_reportes_semanales") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .order("fecha_desde", desc=True) \
            .execute()
        reportes = respuesta.data or []
        
        # Formatear las fechas y asegurarse que los campos existen
        for reporte in reportes:
            reporte['fecha_desde_fmt'] = reporte.get('fecha_desde', '').split('T')[0] if reporte.get('fecha_desde') else 'N/A'
            reporte['fecha_hasta_fmt'] = reporte.get('fecha_hasta', '').split('T')[0] if reporte.get('fecha_hasta') else 'N/A'
            # Asegurar que todos los campos numéricos existan
            reporte['importe_gastado_campañas'] = reporte.get('importe_gastado_campañas', 0)
            reporte['facebook_importe_gastado'] = reporte.get('facebook_importe_gastado', 0)
            reporte['instagram_importe_gastado'] = reporte.get('instagram_importe_gastado', 0)
            
    except Exception as e:
        print(f"❌ Error consultando reportes: {e}")
        reportes = []
    return render_template("panel_cliente_meta_ads/reportes.html", reportes=reportes, nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/reportes/<reporte_id>")', '24', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('d09e3eaf-0bed-4ab4-85ce-8dc83006bc56', 'meta_ads', 'obtener_columnas_tabla', 'Obtiene las columnas disponibles para una tabla dada', '{"tabla":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Obtiene las columnas disponibles para una tabla dada', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"helpers.py","funcion":"obtener_columnas_tabla","parametros":{"tabla":"ejemplo_tabla"}}', '2025-08-01 14:27:21.473568+00', '2025-08-01 15:13:44.165343+00', 'false', 'def obtener_columnas_tabla(tabla):
    """
    Obtiene las columnas disponibles para una tabla dada
    """
    try:
        columnas = supabase.table(tabla).select('*').limit(1).execute()
        if columnas.data:
            return list(columnas.data[0].keys())
        return []
    except Exception as e:
        print(f"Error al obtener columnas de {tabla}: {e}")
        return []
', '3', 'clientes.aura.routes.panel_cliente_meta_ads.helpers', 'python', 'helpers.py', 'clientes/aura/routes/panel_cliente_meta_ads\helpers.py', 'escaneo_directo'), ('d7af016a-f11c-4050-8117-0ad82ea2b26a', 'meta_ads', 'sincronizar_gasto_anuncios', 'Función para sincronizar gastos de anuncios de Meta Ads', '{"empresa_id":{"tipo":"Any","requerido":true,"valor_defecto":null},"access_token":{"tipo":"Any","requerido":true,"valor_defecto":null},"ad_account_id":{"tipo":"Any","requerido":true,"valor_defecto":null}}', 'Función para sincronizar gastos de anuncios de Meta Ads', 'true', 'true', 'sincronizacion', '{"modulo":"meta_ads","funcion":"sincronizar_gasto_anuncios","parametros":{"empresa_id":"ejemplo_empresa_id","access_token":"ejemplo_access_token","ad_account_id":"ejemplo_ad_account_id"}}', '2025-08-01 14:02:07.802489+00', '2025-08-01 15:13:56.69764+00', 'false', null, null, null, 'python', null, null, 'importacion'), ('dac801c0-3079-44ea-bbc6-4e4915264000', 'meta_ads', 'guardar_config_reportes', 'Guarda la configuración de reportes', '{}', 'Guarda la configuración de reportes', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"automatizaciones.py","funcion":"guardar_config_reportes","parametros":{}}', '2025-08-01 14:27:20.20944+00', '2025-08-01 15:13:43.012737+00', 'false', 'def guardar_config_reportes():
    """Guarda la configuración de reportes"""
    try:
        # TODO: Implementar lógica de guardado de configuración
        flash('Configuración guardada exitosamente', 'success')
        return ('', 204)
    except Exception as e:
        flash(f'Error al guardar configuración: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500
', '5', 'clientes.aura.routes.panel_cliente_meta_ads.automatizaciones', 'python', 'automatizaciones.py', 'clientes/aura/routes/panel_cliente_meta_ads\automatizaciones.py', 'escaneo_directo'), ('e25d3e04-41c7-45d0-9375-7d78167df370', 'meta_ads', 'vista_meta_ads', 'Vista del dashboard de Meta Ads.', '{}', 'Vista del dashboard de Meta Ads.', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"vistas.py","funcion":"vista_meta_ads","parametros":{}}', '2025-08-01 14:27:32.056557+00', '2025-08-01 15:13:53.252491+00', 'false', 'def vista_meta_ads():
    """
    Vista del dashboard de Meta Ads.
    """
    try:
        # Obtener estadísticas básicas
        stats = {
            "total_reportes": supabase.table("meta_ads_reportes_semanales").select("count").execute().count,
            "ultima_actualizacion": supabase.table("meta_ads_reportes_semanales")
                .select("created_at")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
                .data[0]["created_at"] if supabase.table("meta_ads_reportes_semanales").select("count").execute().count > 0 else None
        }
        
        return render_template(
            "panel_cliente_meta_ads/dashboard.html",
            stats=stats,
            titulo="Dashboard Meta Ads"
        )
        
    except Exception as e:
        print(f"❌ Error en vista principal Meta Ads: {e}")
        return render_template(
            "panel_cliente_meta_ads/index.html",
            error=f"Error al cargar datos: {str(e)}",
            titulo="Dashboard Meta Ads"
        )
', '33', 'clientes.aura.routes.panel_cliente_meta_ads.vistas', 'python', 'vistas.py', 'clientes/aura/routes/panel_cliente_meta_ads\vistas.py', 'escaneo_directo'), ('e38aea9a-24b3-44ff-ae82-2f4517dd8369', 'meta_ads', 'obtener_access_token', 'Obtiene el token de acceso para la API de Meta desde las variables de entorno.', '{}', 'Obtiene el token de acceso para la API de Meta desde las variables de entorno.
    Returns:
        str: Token de acceso o None si no se encuentra.', 'true', 'true', 'general', '{"modulo":"meta_ads","archivo":"panel_cliente_meta_ads.py","funcion":"obtener_access_token","parametros":{}}', '2025-08-01 14:27:25.376981+00', '2025-08-01 15:13:47.536399+00', 'false', 'def obtener_access_token():
    """
    Obtiene el token de acceso para la API de Meta desde las variables de entorno.
    Returns:
        str: Token de acceso o None si no se encuentra.
    """
    return os.getenv('META_ACCESS_TOKEN')

# Aquí terminan las importaciones y funciones auxiliares


@panel_cliente_meta_ads_bp.route('/agregar_cuenta', methods=['POST'])', '199', 'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads', 'python', 'panel_cliente_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\panel_cliente_meta_ads.py', 'escaneo_directo'), ('f7e0517a-3666-41df-91f0-f3fee3ad8472', 'meta_ads', 'limpiar_columnas_solicitadas', 'Función limpiar_columnas_solicitadas', '{"columnas_solicitadas":{"tipo":"Any","requerido":true,"valor_defecto":null}}', '', 'true', 'true', 'mantenimiento', '{"modulo":"meta_ads","archivo":"validar_columnas_meta_ads.py","funcion":"limpiar_columnas_solicitadas","parametros":{"columnas_solicitadas":"ejemplo_columnas_solicitadas"}}', '2025-08-01 14:27:33.81206+00', '2025-08-01 15:13:55.918638+00', 'false', 'def limpiar_columnas_solicitadas(columnas_solicitadas):
    if not columnas_solicitadas:
        return list(COLUMNAS_VALIDAS_META_ADS)
    columnas_limpias = []
    for col in columnas_solicitadas:
        if col in COLUMNAS_VALIDAS_META_ADS:
            columnas_limpias.append(col)
    return columnas_limpias
', '10', 'clientes.aura.routes.panel_cliente_meta_ads.utils.validar_columnas_meta_ads', 'python', 'validar_columnas_meta_ads.py', 'clientes/aura/routes/panel_cliente_meta_ads\utils\validar_columnas_meta_ads.py', 'escaneo_directo');