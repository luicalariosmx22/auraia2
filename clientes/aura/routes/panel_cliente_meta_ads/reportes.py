from flask import render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp


@panel_cliente_meta_ads_bp.route("/reportes", methods=["GET"])
def vista_reportes_meta_ads(nombre_nora):
    try:
        respuesta = supabase.table("meta_ads_reportes_semanales") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("estatus", "activo") \
            .order("fecha_inicio", desc=True) \
            .execute()
        
        reportes = respuesta.data or []
        return render_template("panel_cliente_meta_ads/reportes.html", nombre_nora=nombre_nora, reportes=reportes)
    except Exception as e:
        print(f"❌ Error consultando reportes: {e}")
        return render_template("panel_cliente_meta_ads/reportes.html", nombre_nora=nombre_nora, reportes=[])

@panel_cliente_meta_ads_bp.route("/reportes/archivados", methods=["GET"])
def vista_reportes_archivados(nombre_nora):
    """Vista para mostrar reportes archivados"""
    try:
        respuesta = supabase.table("meta_ads_reportes_semanales") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("estatus", "archivado") \
            .order("fecha_inicio", desc=True) \
            .execute()
        
        reportes_archivados = respuesta.data or []
        return render_template("panel_cliente_meta_ads/reportes_archivados.html", 
                             nombre_nora=nombre_nora, 
                             reportes=reportes_archivados)
    except Exception as e:
        print(f"❌ Error consultando reportes archivados: {e}")
        return render_template("panel_cliente_meta_ads/reportes_archivados.html", 
                             nombre_nora=nombre_nora, 
                             reportes=[])

@panel_cliente_meta_ads_bp.route("/reportes/archivar", methods=["POST"])
def archivar_reporte(nombre_nora):
    """Archiva un reporte específico"""
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Actualizar estatus a archivado
        resultado = supabase.table('meta_ads_reportes_semanales') \
            .update({'estatus': 'archivado'}) \
            .eq('id', reporte_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        if resultado.data:
            return jsonify({'ok': True, 'message': 'Reporte archivado exitosamente'})
        else:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
            
    except Exception as e:
        print(f"❌ Error archivando reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@panel_cliente_meta_ads_bp.route("/reportes/restaurar", methods=["POST"])
def restaurar_reporte(nombre_nora):
    """Restaura un reporte archivado"""
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Actualizar estatus a activo
        resultado = supabase.table('meta_ads_reportes_semanales') \
            .update({'estatus': 'activo'}) \
            .eq('id', reporte_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        if resultado.data:
            return jsonify({'ok': True, 'message': 'Reporte restaurado exitosamente'})
        else:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
            
    except Exception as e:
        print(f"❌ Error restaurando reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@panel_cliente_meta_ads_bp.route('/sincronizar_completo', methods=['POST'])
def sincronizar_completo_meta_ads(nombre_nora):
    """
    Endpoint para probar la sincronización completa de Meta Ads
    """
    from clientes.aura.tasks.meta_ads_sync_all import sincronizar_todas_las_cuentas_meta_ads
    from datetime import date, timedelta
    
    try:
        # Obtener parámetros del request
        datos = request.json if request.json else {}
        dias_atras = int(datos.get('dias', datos.get('dias_atras', 7)))
        
        # Calcular fechas
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=dias_atras)
        
        print(f"🔄 Iniciando sincronización completa (todas las cuentas activas)")
        print(f"📅 Rango: {fecha_inicio} a {fecha_fin} ({dias_atras} días)")
        
        # Ejecutar sincronización para TODAS las cuentas activas (no solo las de nombre_nora)
        resultado = sincronizar_todas_las_cuentas_meta_ads(
            nombre_nora=None,  # Buscar todas las cuentas, no solo las de esta nora
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': f'Error en sincronización: {str(e)}'
        }), 500

@panel_cliente_meta_ads_bp.route('/sincronizar_test', methods=['GET'])
def test_sincronizacion_meta_ads(nombre_nora):
    """
    Vista para probar la sincronización con diferentes rangos de tiempo
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Sincronización Meta Ads - {nombre_nora}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select {{ width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }}
            button {{ background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #005a87; }}
            .result {{ margin-top: 20px; padding: 15px; border-radius: 4px; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .loading {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔄 Test Sincronización Meta Ads</h1>
            <p><strong>Nora:</strong> {nombre_nora}</p>
            
            <div class="form-group">
                <label for="dias_atras">Días hacia atrás:</label>
                <select id="dias_atras">
                    <option value="1">1 día (solo hoy)</option>
                    <option value="3">3 días</option>
                    <option value="7" selected>7 días (1 semana)</option>
                    <option value="14">14 días (2 semanas)</option>
                    <option value="30">30 días (1 mes)</option>
                </select>
            </div>
            
            <button onclick="ejecutarSincronizacion()">🚀 Ejecutar Sincronización</button>
            <button onclick="actualizarEstados()" style="margin-left: 10px; background: #28a745;">🔄 Actualizar Estados (NULL → activas)</button>
            
            <div id="resultado"></div>
        </div>
        
        <script>
            function ejecutarSincronizacion() {{
                const diasAtras = document.getElementById('dias_atras').value;
                const resultado = document.getElementById('resultado');
                
                resultado.innerHTML = '<div class="result loading">⏳ Ejecutando sincronización... Esto puede tomar varios minutos.</div>';
                
                fetch('/panel_cliente/{nombre_nora}/meta_ads/sincronizar_completo', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        dias_atras: parseInt(diasAtras)
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.ok) {{
                        resultado.innerHTML = `
                            <div class="result success">
                                <h3>✅ Sincronización Exitosa</h3>
                                <p><strong>Cuentas procesadas:</strong> ${{data.cuentas_procesadas}}</p>
                                <p><strong>Cuentas exitosas:</strong> ${{data.cuentas_exitosas}}</p>
                                <p><strong>Errores:</strong> ${{data.errores.length}}</p>
                                <p><strong>Período:</strong> ${{data.fecha_inicio}} a ${{data.fecha_fin}}</p>
                                ${{data.errores.length > 0 ? '<p><strong>Errores:</strong> ' + JSON.stringify(data.errores, null, 2) + '</p>' : ''}}
                            </div>
                        `;
                    }} else {{
                        resultado.innerHTML = `
                            <div class="result error">
                                <h3>❌ Error en Sincronización</h3>
                                <p>${{data.error}}</p>
                            </div>
                        `;
                    }}
                }})
                .catch(error => {{
                    resultado.innerHTML = `
                        <div class="result error">
                            <h3>❌ Error de Conexión</h3>
                            <p>${{error.message}}</p>
                        </div>
                    `;
                }});
            }}
            
            function actualizarEstados() {{
                const resultado = document.getElementById('resultado');
                
                resultado.innerHTML = '<div class="result loading">⏳ Actualizando estados de cuentas...</div>';
                
                fetch('/panel_cliente/{nombre_nora}/meta_ads/actualizar_estados_cuentas', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.ok) {{
                        resultado.innerHTML = `
                            <div class="result success">
                                <h3>✅ Estados Actualizados</h3>
                                <p>${{data.message}}</p>
                                <p><strong>Cuentas actualizadas:</strong> ${{data.cuentas_actualizadas}}</p>
                            </div>
                        `;
                    }} else {{
                        resultado.innerHTML = `
                            <div class="result error">
                                <h3>❌ Error al Actualizar Estados</h3>
                                <p>${{data.error}}</p>
                            </div>
                        `;
                    }}
                }})
                .catch(error => {{
                    resultado.innerHTML = `
                        <div class="result error">
                            <h3>❌ Error de Conexión</h3>
                            <p>${{error.message}}</p>
                        </div>
                    `;
                }});
            }}
        </script>
    </body>
    </html>
    """
    
@panel_cliente_meta_ads_bp.route('/actualizar_estados_cuentas', methods=['POST'])
def actualizar_estados_cuentas_meta_ads(nombre_nora):
    """
    Actualiza todas las cuentas con estado_actual NULL a 'activas'
    """
    try:
        # Actualizar todas las cuentas con estado_actual NULL
        resultado = supabase.table('meta_ads_cuentas') \
            .update({'estado_actual': 'activas'}) \
            .is_('estado_actual', 'null') \
            .execute()
        
        cuentas_actualizadas = len(resultado.data) if resultado.data else 0
        
        return jsonify({
            'ok': True,
            'message': f'Se actualizaron {cuentas_actualizadas} cuentas de NULL a "activas"',
            'cuentas_actualizadas': cuentas_actualizadas
        })
        
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': f'Error al actualizar estados: {str(e)}'
        }), 500
    
@panel_cliente_meta_ads_bp.route('/prereportes/eliminar', methods=['POST'])
def eliminar_prereporte(nombre_nora):
    """
    Elimina un prereporte guardado en Supabase usando su ID.
    """
    reporte_id = (request.json.get("id") if request.json else None) or request.form.get("id")
    if not reporte_id:
        return jsonify({"ok": False, "error": "Falta ID de prereporte"}), 400
    try:
        supabase.table("meta_ads_reportes_semanales").delete().eq("id", reporte_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al eliminar prereporte: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@panel_cliente_meta_ads_bp.route('/compartir_reporte', methods=['POST'])
def compartir_reporte_meta_ads(nombre_nora):
    """
    Genera un link público para compartir un reporte específico con clientes.
    """
    import uuid
    import secrets
    from datetime import datetime
    
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        empresa_nombre = data.get('empresa_nombre', '')
        periodo = data.get('periodo', '')
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Verificar que el reporte existe y está activo
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).eq('estatus', 'activo').single().execute().data
        except Exception as e:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        if not reporte:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        # Generar token único para compartir
        token_uuid = str(uuid.uuid4())
        token_seguridad = secrets.token_hex(16)
        
        # Construir URL pública
        base_url = "https://app.soynoraai.com"
        url_publico = f"{base_url}/panel_cliente/{nombre_nora}/meta_ads/reporte_publico/{token_uuid}?token={token_seguridad}"
        
        # Guardar registro de compartir en base de datos
        try:
            supabase.table('meta_ads_reportes_compartidos').insert({
                'id': token_uuid,
                'reporte_id': reporte_id,
                'token': token_seguridad,
                'empresa_nombre': empresa_nombre,
                'periodo': periodo,
                'compartido_por': nombre_nora,
                'created_at': datetime.utcnow().isoformat(),
                'activo': True
            }).execute()
        except Exception as e:
            print(f"[WARN] No se pudo guardar registro de compartir: {e}")
        
        return jsonify({
            'ok': True, 
            'url_publico': url_publico,
            'token': token_seguridad,
            'reporte_id': reporte_id,
            'token_uuid': token_uuid
        })
        
    except Exception as e:
        print(f"[ERROR] Error al compartir reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@panel_cliente_meta_ads_bp.route('/reporte_publico/<token_uuid>')
def vista_reporte_publico(nombre_nora, token_uuid):
    """
    Vista pública de un reporte compartido usando token de seguridad.
    URL: https://app.soynoraai.com/panel_cliente/{nombre_nora}/meta_ads/reporte_publico/{token_uuid}?token={token_seguridad}
    """
    from flask import abort
    
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
        print(f"[DEBUG] Buscando reporte con ID: {reporte_id}")
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).eq('estatus', 'activo').single().execute().data
            print(f"[DEBUG] Reporte encontrado: {reporte}")
        except Exception as e:
            print(f"[ERROR] Error al obtener reporte: {e}")
            abort(404, description="Reporte no encontrado")
        
        if not reporte:
            abort(404, description="Reporte no encontrado")
        
        # Obtener anuncios detallados del reporte
        print(f"[DEBUG] Buscando anuncios para cuenta: {reporte['id_cuenta_publicitaria']}, fechas: {reporte['fecha_inicio']} - {reporte['fecha_fin']}")
        try:
            anuncios = supabase.table('meta_ads_anuncios_detalle').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).gte('fecha_inicio', reporte['fecha_inicio']).lte('fecha_fin', reporte['fecha_fin']).execute().data
            print(f"[DEBUG] Anuncios encontrados: {len(anuncios) if anuncios else 0}")
            if anuncios:
                print(f"[DEBUG] Primer anuncio: {anuncios[0]}")
        except Exception as e:
            print(f"[ERROR] Error al obtener anuncios: {e}")
            anuncios = []
        
        # Obtener información de la empresa
        try:
            empresa = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).single().execute().data
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


@panel_cliente_meta_ads_bp.route('/api/reporte_publico/<token_uuid>/validar')
def validar_enlace_publico(nombre_nora, token_uuid):
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
