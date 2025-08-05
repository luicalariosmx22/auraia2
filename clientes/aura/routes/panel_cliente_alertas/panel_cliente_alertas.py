
from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.notificaciones import enviar_notificaciones_alerta, obtener_configuracion_notificaciones, obtener_configuracion_notificaciones_por_empresa

panel_cliente_alertas_bp = Blueprint("panel_cliente_alertas_bp", __name__)

@panel_cliente_alertas_bp.route("/")
def panel_cliente_alertas():
    # Obtener nombre_nora desde la URL path
    from flask import request
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener alertas activas para esta Nora
        alertas_response = supabase.table("alertas") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activa", True) \
            .order("creado_en", desc=True) \
            .execute()
        
        # Filtrar alertas ignoradas (las que tienen "IGNORADA:" en la columna acciones)
        alertas = [a for a in (alertas_response.data or []) 
                  if not (a.get('acciones', '') and 'IGNORADA:' in a.get('acciones', ''))]
        
        # Separar alertas por estado
        alertas_nuevas = [a for a in alertas if not a.get('vista', False)]
        alertas_vistas = [a for a in alertas if a.get('vista', False) and not a.get('resuelta', False)]
        alertas_resueltas = [a for a in alertas if a.get('resuelta', False)]
        
        # Agrupar alertas por tipo
        alertas_por_tipo = {}
        for alerta in alertas:
            tipo = alerta.get('tipo', 'general')
            if tipo not in alertas_por_tipo:
                alertas_por_tipo[tipo] = {
                    'nuevas': [],
                    'vistas': [], 
                    'resueltas': [],
                    'total': 0
                }
            
            # Clasificar por estado
            if alerta.get('resuelta', False):
                alertas_por_tipo[tipo]['resueltas'].append(alerta)
            elif alerta.get('vista', False):
                alertas_por_tipo[tipo]['vistas'].append(alerta)
            else:
                alertas_por_tipo[tipo]['nuevas'].append(alerta)
            
            alertas_por_tipo[tipo]['total'] += 1
        
        # Estadísticas
        stats = {
            'total': len(alertas),
            'nuevas': len(alertas_nuevas),
            'vistas': len(alertas_vistas),
            'resueltas': len(alertas_resueltas),
            'alta_prioridad': len([a for a in alertas if a.get('prioridad') == 'alta']),
            'por_tipo': {tipo: data['total'] for tipo, data in alertas_por_tipo.items()}
        }
        
        print(f"📊 Alertas para {nombre_nora}: {stats}")
        print(f"🏷️ Tipos de alertas encontrados: {list(alertas_por_tipo.keys())}")
        
    except Exception as e:
        print(f"❌ Error al obtener alertas: {e}")
        alertas_nuevas = []
        alertas_vistas = []
        alertas_resueltas = []
        alertas_por_tipo = {}
        stats = {'total': 0, 'nuevas': 0, 'vistas': 0, 'resueltas': 0, 'alta_prioridad': 0, 'por_tipo': {}}
    
    return render_template(
        "panel_cliente_alertas/index.html", 
        nombre_nora=nombre_nora,
        alertas_nuevas=alertas_nuevas,
        alertas_vistas=alertas_vistas,
        alertas_resueltas=alertas_resueltas,
        alertas_por_tipo=alertas_por_tipo,
        stats=stats
    )

@panel_cliente_alertas_bp.route("/marcar_vista/<alerta_id>", methods=['POST'])
def marcar_alerta_vista(alerta_id):
    """Marcar una alerta como vista"""
    try:
        supabase.table("alertas") \
            .update({"vista": True}) \
            .eq("id", alerta_id) \
            .execute()
        
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al marcar alerta como vista: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_alertas_bp.route("/resolver/<alerta_id>", methods=['POST'])
def resolver_alerta(alerta_id):
    """Marcar una alerta como resuelta"""
    try:
        from datetime import datetime
        
        supabase.table("alertas") \
            .update({
                "resuelta": True,
                "vista": True,
                "resuelta_en": datetime.utcnow().isoformat()
            }) \
            .eq("id", alerta_id) \
            .execute()
        
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al resolver alerta: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_alertas_bp.route("/ignorar/<alerta_id>", methods=['POST'])
def ignorar_alerta(alerta_id):
    """Ignorar una alerta (marcarla como ignorada para que no vuelva a aparecer)"""
    try:
        from datetime import datetime
        
        # Obtener la alerta actual para preservar acciones existentes
        alerta_actual = supabase.table("alertas") \
            .select("acciones") \
            .eq("id", alerta_id) \
            .single() \
            .execute()
        
        acciones_existentes = alerta_actual.data.get('acciones', '') if alerta_actual.data else ''
        nueva_accion = f"IGNORADA:{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        # Combinar acciones existentes con la nueva
        acciones_actualizadas = f"{acciones_existentes}|{nueva_accion}" if acciones_existentes else nueva_accion
        
        # Marcar como inactiva y agregar la acción de ignorar
        supabase.table("alertas") \
            .update({
                "activa": False,
                "acciones": acciones_actualizadas
            }) \
            .eq("id", alerta_id) \
            .execute()
        
        print(f"✅ Alerta {alerta_id} ignorada correctamente - Acciones: {acciones_actualizadas}")
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al ignorar alerta: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_alertas_bp.route("/notificar/<alerta_id>", methods=['POST'])
def notificar_alerta(alerta_id):
    """Enviar notificación por email/SMS de una alerta específica"""
    try:
        # Obtener la alerta
        alerta_response = supabase.table("alertas") \
            .select("*") \
            .eq("id", alerta_id) \
            .single() \
            .execute()
        
        if not alerta_response.data:
            return jsonify({"ok": False, "error": "Alerta no encontrada"}), 404
        
        alerta_data = alerta_response.data
        
        # Extraer el nombre de la empresa desde los datos de la alerta
        empresa_nombre = None
        if alerta_data.get('datos') and isinstance(alerta_data['datos'], dict):
            empresa_nombre = alerta_data['datos'].get('empresa_nombre')
        
        if not empresa_nombre:
            empresa_nombre = alerta_data.get('empresa_nombre')
        
        if not empresa_nombre:
            return jsonify({
                "ok": False, 
                "error": "No se pudo identificar la empresa para esta alerta"
            }), 400
        
        print(f"🏢 Enviando notificación para empresa: {empresa_nombre}")
        
        # Obtener configuración de notificaciones por empresa
        config_notificaciones = obtener_configuracion_notificaciones_por_empresa(empresa_nombre)
        
        if not config_notificaciones:
            return jsonify({
                "ok": False, 
                "error": f"No se encontró configuración de notificaciones para la empresa '{empresa_nombre}'"
            }), 400
        
        # Enviar notificaciones
        notificaciones_enviadas = enviar_notificaciones_alerta(alerta_data, config_notificaciones)
        
        if notificaciones_enviadas:
            # Registrar la notificación en las acciones de la alerta
            from datetime import datetime
            alerta_actual = supabase.table("alertas") \
                .select("acciones") \
                .eq("id", alerta_id) \
                .single() \
                .execute()
            
            acciones_existentes = alerta_actual.data.get('acciones', '') if alerta_actual.data else ''
            nueva_accion = f"NOTIFICADO:{','.join(notificaciones_enviadas)}:{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            acciones_actualizadas = f"{acciones_existentes}|{nueva_accion}" if acciones_existentes else nueva_accion
            
            supabase.table("alertas") \
                .update({"acciones": acciones_actualizadas}) \
                .eq("id", alerta_id) \
                .execute()
            
            return jsonify({
                "ok": True, 
                "notificaciones_enviadas": notificaciones_enviadas,
                "mensaje": f"Notificaciones enviadas a {empresa_nombre}: {', '.join(notificaciones_enviadas)}"
            })
        else:
            return jsonify({
                "ok": False, 
                "error": f"No se pudo enviar ninguna notificación para {empresa_nombre}. Verifica la configuración."
            }), 400
        
    except Exception as e:
        print(f"❌ Error al enviar notificación: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_alertas_bp.route("/eliminar/<alerta_id>", methods=['POST'])
def eliminar_alerta(alerta_id):
    """Eliminar una alerta (marcar como inactiva)"""
    try:
        supabase.table("alertas") \
            .update({"activa": False}) \
            .eq("id", alerta_id) \
            .execute()
        
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al eliminar alerta: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
