"""
🚀 FUNCIÓN OPTIMIZADA: detalle_pagina_facebook
Version optimizada para carga rápida
"""

def detalle_pagina_facebook_optimizada(page_id):
    """Detalle completo de una página específica de Facebook - ULTRA OPTIMIZADO"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        # 🚀 PASO 1: Datos básicos de la página (solo campos necesarios)
        pagina_response = supabase.table('facebook_paginas').select(
            'page_id, nombre_pagina, username, categoria, descripcion, ciudad, pais, '
            'website, telefono, email, seguidores, likes, verificada, estado_webhook, '
            'access_token_valido, ultima_sincronizacion, empresa_id, foto_perfil_url'
        ).eq('page_id', page_id).single().execute()
        
        pagina = pagina_response.data if pagina_response.data else None
        
        if not pagina:
            return "Página no encontrada", 404

        # 🚀 PASO 2: Empresa info optimizada (UN SOLO QUERY CON JOIN)
        empresa_info = None
        if pagina.get('empresa_id'):
            try:
                # Query optimizada con JOIN directo
                empresa_response = supabase.table('cliente_empresas').select(
                    'id, nombre_empresa, clientes(nombre_cliente)'
                ).eq('id', pagina['empresa_id']).single().execute()
                
                if empresa_response.data:
                    empresa_data = empresa_response.data
                    nombre_contacto = "Sin contacto"
                    if empresa_data.get('clientes') and len(empresa_data['clientes']) > 0:
                        nombre_contacto = empresa_data['clientes'][0]['nombre_cliente']
                    
                    empresa_info = {
                        'id': empresa_data['id'],
                        'nombre_empresa': empresa_data['nombre_empresa'],
                        'nombre_contacto': nombre_contacto
                    }
            except Exception as e:
                print(f"Error al obtener empresa: {e}")
                
        if empresa_info:
            pagina['cliente_vinculado'] = empresa_info

        # 🚀 PASO 3: Solo 5 publicaciones iniciales (campos mínimos)
        publicaciones_response = supabase.table('meta_publicaciones_webhook').select(
            'post_id, message, type, created_time, reactions_count, comments_count, shares_count'
        ).eq('page_id', page_id).neq('tipo_item', 'comment').neq('tipo_item', 'reaction').order('created_time', desc=True).limit(5).execute()
        
        publicaciones = []
        for pub in (publicaciones_response.data or []):
            try:
                # Formateo ultra rápido de fecha
                if pub.get('created_time') and isinstance(pub['created_time'], (int, float)):
                    fecha_formateada = datetime.fromtimestamp(pub['created_time']).strftime('%d/%m %H:%M')
                else:
                    fecha_formateada = str(pub.get('created_time', 'Sin fecha'))[:10]
                
                pub['fecha_formateada'] = fecha_formateada
                publicaciones.append(pub)
            except:
                pub['fecha_formateada'] = 'Sin fecha'
                publicaciones.append(pub)

        # 🚀 PASO 4: Solo 5 comentarios recientes (campos mínimos)
        comentarios_response = supabase.table('meta_publicaciones_webhook').select(
            'post_id, mensaje, created_time'
        ).eq('page_id', page_id).eq('tipo_item', 'comment').order('created_time', desc=True).limit(5).execute()
        
        comentarios = []
        for com in (comentarios_response.data or []):
            try:
                if com.get('created_time') and isinstance(com['created_time'], (int, float)):
                    fecha_formateada = datetime.fromtimestamp(com['created_time']).strftime('%d/%m %H:%M')
                else:
                    fecha_formateada = str(com.get('created_time', 'Sin fecha'))[:10]
                
                com['fecha_formateada'] = fecha_formateada
                comentarios.append(com)
            except:
                com['fecha_formateada'] = 'Sin fecha'
                comentarios.append(com)

        # 🚀 PASO 5: Solo 5 reacciones recientes (campos mínimos)
        reacciones_response = supabase.table('meta_publicaciones_webhook').select(
            'post_id, created_time, webhook_data'
        ).eq('page_id', page_id).eq('tipo_item', 'reaction').order('created_time', desc=True).limit(5).execute()
        
        reacciones = []
        for reac in (reacciones_response.data or []):
            try:
                if reac.get('created_time') and isinstance(reac['created_time'], (int, float)):
                    fecha_formateada = datetime.fromtimestamp(reac['created_time']).strftime('%d/%m %H:%M')
                else:
                    fecha_formateada = str(reac.get('created_time', 'Sin fecha'))[:10]
                
                reac['fecha_formateada'] = fecha_formateada
                reacciones.append(reac)
            except:
                reac['fecha_formateada'] = 'Sin fecha'
                reacciones.append(reac)

        # 🚀 PASO 6: Estado webhook simplificado
        pagina['estado_webhook_real'] = 'activa' if pagina.get('estado_webhook') == 'activa' else 'inactiva'

        # 🚀 PASO 7: Estadísticas básicas (sin cálculos complejos)
        estadisticas = {
            'total_publicaciones': len(publicaciones),
            'total_comentarios': len(comentarios), 
            'total_reacciones': len(reacciones),
            'total_shares': sum(pub.get('shares_count', 0) for pub in publicaciones),
            'promedio_reacciones': round(sum(pub.get('reactions_count', 0) for pub in publicaciones) / max(len(publicaciones), 1)),
            'promedio_comentarios': round(sum(pub.get('comments_count', 0) for pub in publicaciones) / max(len(publicaciones), 1)),
            'comentarios_webhook': len(comentarios),
            'reacciones_webhook': len(reacciones),
            'comentarios_historicos': 0,  # Se calculará vía AJAX si es necesario
            'reacciones_historicos': 0,   # Se calculará vía AJAX si es necesario
            'tipos_contenido': {}         # Se calculará vía AJAX si es necesario
        }

        # 🚀 PASO 8: Lista empresas optimizada (solo campos necesarios)
        clientes_response = supabase.table('cliente_empresas').select(
            'id, nombre_empresa, cliente_id'
        ).order('nombre_empresa').execute()
        
        clientes = []
        for empresa in (clientes_response.data or []):
            clientes.append({
                'id': empresa['id'],
                'nombre_empresa': empresa['nombre_empresa'],
                'nombre_contacto': 'Sin contacto'  # Se puede cargar vía AJAX si es necesario
            })

        return render_template(
            "panel_cliente_redes_sociales/facebook_detalle.html",
            nombre_nora=nombre_nora,
            pagina=pagina,
            publicaciones=publicaciones,
            comentarios=comentarios,
            reacciones=reacciones,
            estadisticas=estadisticas,
            clientes=clientes
        )
        
    except Exception as e:
        print(f"Error en detalle_pagina_facebook: {e}")
        return f"Error interno del servidor: {str(e)}", 500
