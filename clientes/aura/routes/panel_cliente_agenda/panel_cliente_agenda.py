"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• agenda_eventos: Eventos del calendario interno
  └ Campos clave: id(bigint), nombre_nora(varchar), titulo(text), fecha_inicio(timestamptz)
  
• tareas: Integración con módulo de tareas
  └ Campos clave: id(bigint), nombre_nora(varchar), fecha_vencimiento(timestamptz), titulo(text)
  
• cliente_empresas: Fichas de empresa para reuniones
  └ Campos clave: id(bigint), nombre_nora(varchar), nombre_empresa(text), contacto_principal(text)
  
• google_calendar_sync: Configuración de sincronización Google Calendar
  └ Campos clave: nombre_nora(varchar), calendar_id(text), access_token(text), refresh_token(text)

🔗 RELACIONES:
• agenda_eventos -> tareas via tarea_id (opcional)
• agenda_eventos -> cliente_empresas via empresa_id (opcional)
• configuracion_bot -> TODOS via nombre_nora (filtro obligatorio)

💡 VERIFICAR SCHEMAS:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('agenda_eventos'):
    campos = columnas('agenda_eventos')
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import json
import pytz
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
# BD ACTUAL: agenda_eventos, tareas, cliente_empresas, google_calendar_sync

panel_cliente_agenda_bp = Blueprint(
    "panel_cliente_agenda_bp", 
    __name__, 
    url_prefix="/panel_cliente/<nombre_nora>/agenda"
)

@panel_cliente_agenda_bp.route("/")
def panel_cliente_agenda():
    """Dashboard principal del calendario"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    # Obtener vista por defecto (mes, semana, día)
    vista = request.args.get('vista', 'mes')
    
    return render_template(
        "panel_cliente_agenda/index.html", 
        nombre_nora=nombre_nora,
        vista=vista
    )

@panel_cliente_agenda_bp.route("/api/eventos")
def api_eventos():
    """API para obtener eventos del calendario"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        # Parámetros de fecha
        fecha_inicio = request.args.get('start')
        fecha_fin = request.args.get('end')
        
        eventos = []
        
        # 1. Eventos propios de la agenda
        if existe('agenda_eventos'):
            eventos_agenda = obtener_eventos_agenda(nombre_nora, fecha_inicio, fecha_fin)
            eventos.extend(eventos_agenda)
        
        # 2. Tareas con fecha límite
        if existe('tareas'):
            eventos_tareas = obtener_eventos_tareas(nombre_nora, fecha_inicio, fecha_fin)
            eventos.extend(eventos_tareas)
        
        # 3. Google Calendar (si está configurado)
        eventos_google = obtener_eventos_google_calendar(nombre_nora, fecha_inicio, fecha_fin)
        eventos.extend(eventos_google)
        
        return jsonify({
            'success': True,
            'eventos': eventos
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@panel_cliente_agenda_bp.route("/api/evento", methods=['POST'])
def api_crear_evento():
    """API para crear nuevo evento"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('titulo') or not data.get('fecha_inicio'):
            return jsonify({
                'success': False,
                'error': 'Título y fecha de inicio son requeridos'
            }), 400
        
        # Crear evento en BD local
        evento_creado = crear_evento_agenda(nombre_nora, data)
        
        # Sincronizar con Google Calendar si está configurado
        if esta_google_calendar_configurado(nombre_nora):
            sincronizar_evento_a_google(nombre_nora, evento_creado)
        
        return jsonify({
            'success': True,
            'evento': evento_creado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@panel_cliente_agenda_bp.route("/api/evento/<int:evento_id>", methods=['PUT'])
def api_actualizar_evento(evento_id):
    """API para actualizar evento existente"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        data = request.get_json()
        
        evento_actualizado = actualizar_evento_agenda(nombre_nora, evento_id, data)
        
        if not evento_actualizado:
            return jsonify({
                'success': False,
                'error': 'Evento no encontrado'
            }), 404
        
        # Sincronizar cambios con Google Calendar
        if esta_google_calendar_configurado(nombre_nora):
            sincronizar_evento_a_google(nombre_nora, evento_actualizado)
        
        return jsonify({
            'success': True,
            'evento': evento_actualizado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@panel_cliente_agenda_bp.route("/api/evento/<int:evento_id>", methods=['DELETE'])
def api_eliminar_evento(evento_id):
    """API para eliminar evento"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        eliminado = eliminar_evento_agenda(nombre_nora, evento_id)
        
        if not eliminado:
            return jsonify({
                'success': False,
                'error': 'Evento no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Evento eliminado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@panel_cliente_agenda_bp.route("/configuracion")
def configuracion_agenda():
    """Configuración de la agenda y Google Calendar"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    # Obtener configuración actual
    config_google = obtener_configuracion_google_calendar(nombre_nora)
    
    return render_template(
        "panel_cliente_agenda/configuracion.html",
        nombre_nora=nombre_nora,
        config_google=config_google
    )

@panel_cliente_agenda_bp.route("/sync/google")
def sync_google_calendar():
    """Sincronización con Google Calendar"""
    # Regla oficial: obtener nombre_nora desde view_args
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        # Iniciar proceso de autenticación OAuth2
        auth_url = generar_url_auth_google(nombre_nora)
        
        return redirect(auth_url)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== FUNCIONES DE NEGOCIO =====

def obtener_eventos_agenda(nombre_nora, fecha_inicio=None, fecha_fin=None):
    """Obtiene eventos de la agenda interna"""
    try:
        # Verificar si la tabla agenda_eventos existe
        if not existe('agenda_eventos'):
            print("⚠️ Tabla 'agenda_eventos' no existe, creando lista vacía")
            return []
        # Consulta base sin depender de relaciones PostgREST
        try:
            query = supabase.table('agenda_eventos') \
                .select('*') \
                .eq('nombre_nora', nombre_nora)
            if fecha_inicio:
                query = query.gte('fecha_inicio', fecha_inicio)
            if fecha_fin:
                query = query.lte('fecha_fin', fecha_fin)
            result = query.order('fecha_inicio').execute()
        except Exception as backup_error:
            print(f"❌ Error consultando agenda_eventos: {backup_error}")
            return []

        eventos = []
        empresa_ids = set()
        for evento in result.data:
            if evento.get('empresa_id'):
                empresa_ids.add(evento['empresa_id'])

        # Enriquecer con nombres de empresa en un solo query si la tabla existe
        empresas_map = {}
        if empresa_ids and existe('cliente_empresas'):
            try:
                empresas = supabase.table('cliente_empresas') \
                    .select('id, nombre_empresa') \
                    .in_('id', list(empresa_ids)) \
                    .execute()
                empresas_map = {e['id']: e.get('nombre_empresa') for e in (empresas.data or [])}
            except Exception as e_emp:
                print(f"⚠️ No se pudo enriquecer con nombres de empresa: {e_emp}")

        for evento in result.data:
            # Datos básicos del evento
            evento_data = {
                'id': evento['id'],
                'title': evento['titulo'],
                'start': evento['fecha_inicio'],
                'end': evento['fecha_fin'],
                'description': evento.get('descripcion', ''),
                'type': 'agenda',
                'color': '#3b82f6',  # Azul para eventos de agenda
                'editable': True
            }

            # Agregar empresa si está disponible
            emp_id = evento.get('empresa_id')
            if emp_id and emp_id in empresas_map:
                evento_data['empresa'] = empresas_map[emp_id]
            elif emp_id:
                evento_data['empresa'] = f"Empresa #{emp_id}"

            eventos.append(evento_data)

        print(f"✅ Obtenidos {len(eventos)} eventos de agenda para {nombre_nora}")
        return eventos
        
    except Exception as e:
        print(f"❌ Error obteniendo eventos agenda: {e}")
        return []

def obtener_eventos_tareas(nombre_nora, fecha_inicio=None, fecha_fin=None):
    """Obtiene tareas con fecha límite como eventos"""
    try:
        # Verificar si la tabla tareas existe
        if not existe('tareas'):
            print("⚠️ Tabla 'tareas' no existe, saltando eventos de tareas")
            return []
        
        # Intentar con fecha_vencimiento, si falla probar con fecha_limite
        try:
            query = supabase.table('tareas') \
                .select('id, titulo, fecha_vencimiento, prioridad') \
                .eq('nombre_nora', nombre_nora) \
                .not_.is_('fecha_vencimiento', 'null')
            
            if fecha_inicio:
                query = query.gte('fecha_vencimiento', fecha_inicio)
            if fecha_fin:
                query = query.lte('fecha_vencimiento', fecha_fin)
            
            result = query.execute()
            fecha_campo = 'fecha_vencimiento'
            
        except Exception as column_error:
            # Si fecha_vencimiento no existe, intentar con fecha_limite
            print(f"⚠️ Columna fecha_vencimiento no existe, intentando con fecha_limite: {column_error}")
            try:
                query = supabase.table('tareas') \
                    .select('id, titulo, fecha_limite, prioridad') \
                    .eq('nombre_nora', nombre_nora) \
                    .not_.is_('fecha_limite', 'null')
                
                if fecha_inicio:
                    query = query.gte('fecha_limite', fecha_inicio)
                if fecha_fin:
                    query = query.lte('fecha_limite', fecha_fin)
                
                result = query.execute()
                fecha_campo = 'fecha_limite'
                
            except Exception as backup_error:
                print(f"❌ Error con fecha_limite también: {backup_error}")
                # Último intento: obtener solo id y titulo
                query = supabase.table('tareas') \
                    .select('id, titulo, prioridad') \
                    .eq('nombre_nora', nombre_nora)
                
                result = query.execute()
                fecha_campo = None
        
        eventos = []
        for tarea in result.data:
            # Solo crear evento si tiene fecha válida
            fecha_tarea = None
            if fecha_campo and fecha_campo in tarea and tarea[fecha_campo]:
                fecha_tarea = tarea[fecha_campo]
            
            # Si no hay fecha, saltar esta tarea
            if not fecha_tarea:
                continue
            
            # Color según prioridad
            color_map = {
                'alta': '#ef4444',      # Rojo
                'media': '#f59e0b',     # Amarillo
                'baja': '#10b981'       # Verde
            }
            
            eventos.append({
                'id': f"tarea_{tarea['id']}",
                'title': f"📋 {tarea['titulo']}",
                'start': fecha_tarea,
                'end': fecha_tarea,
                'type': 'tarea',
                'tarea_id': tarea['id'],
                'color': color_map.get(tarea.get('prioridad', 'media'), '#6b7280'),
                'editable': False,
                'allDay': True
            })
        
        print(f"✅ Obtenidos {len(eventos)} eventos de tareas para {nombre_nora}")
        return eventos
        
    except Exception as e:
        print(f"❌ Error obteniendo eventos tareas: {e}")
        return []

def obtener_eventos_google_calendar(nombre_nora, fecha_inicio=None, fecha_fin=None):
    """Obtiene eventos de Google Calendar"""
    try:
        # TODO: Implementar integración con Google Calendar API
        # Por ahora retorna lista vacía
        return []
        
    except Exception as e:
        print(f"Error obteniendo eventos Google Calendar: {e}")
        return []

def crear_evento_agenda(nombre_nora, data):
    """Crea nuevo evento en la agenda"""
    try:
        # Verificar si la tabla agenda_eventos existe
        if not existe('agenda_eventos'):
            print("❌ Tabla 'agenda_eventos' no existe")
            return None
        
        # Preparar datos del evento con validaciones
        evento_data = {
            'nombre_nora': nombre_nora,
            'titulo': data['titulo'],
            'descripcion': data.get('descripcion', ''),
            'fecha_inicio': data['fecha_inicio'],
            'fecha_fin': data.get('fecha_fin', data['fecha_inicio']),
            'tipo': data.get('tipo', 'reunion'),
            'ubicacion': data.get('ubicacion', ''),
            'creado_en': datetime.now().isoformat()
        }
        
        # Validar foreign keys solo si existen
        if data.get('empresa_id') and existe('cliente_empresas'):
            # Verificar que la empresa existe
            try:
                empresa_check = supabase.table('cliente_empresas') \
                    .select('id') \
                    .eq('id', data['empresa_id']) \
                    .single() \
                    .execute()
                
                if empresa_check.data:
                    evento_data['empresa_id'] = data['empresa_id']
                else:
                    print(f"⚠️ Empresa ID {data['empresa_id']} no existe, creando evento sin empresa")
                    
            except Exception as empresa_error:
                print(f"⚠️ Error verificando empresa: {empresa_error}, creando evento sin empresa")
        
        if data.get('tarea_id') and existe('tareas'):
            # Verificar que la tarea existe
            try:
                tarea_check = supabase.table('tareas') \
                    .select('id') \
                    .eq('id', data['tarea_id']) \
                    .eq('nombre_nora', nombre_nora) \
                    .single() \
                    .execute()
                
                if tarea_check.data:
                    evento_data['tarea_id'] = data['tarea_id']
                else:
                    print(f"⚠️ Tarea ID {data['tarea_id']} no existe, creando evento sin tarea")
                    
            except Exception as tarea_error:
                print(f"⚠️ Error verificando tarea: {tarea_error}, creando evento sin tarea")
        
        # Insertar evento
        result = supabase.table('agenda_eventos') \
            .insert(evento_data) \
            .execute()
        
        if result.data:
            print(f"✅ Evento creado exitosamente: {result.data[0]['id']}")
            return result.data[0]
        else:
            print("❌ No se pudo crear el evento")
            return None
        
    except Exception as e:
        print(f"❌ Error creando evento: {e}")
        return None

def actualizar_evento_agenda(nombre_nora, evento_id, data):
    """Actualiza evento existente"""
    try:
        result = supabase.table('agenda_eventos') \
            .update(data) \
            .eq('id', evento_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error actualizando evento: {e}")
        return None

def eliminar_evento_agenda(nombre_nora, evento_id):
    """Elimina evento de la agenda"""
    try:
        result = supabase.table('agenda_eventos') \
            .delete() \
            .eq('id', evento_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        return bool(result.data)
        
    except Exception as e:
        print(f"Error eliminando evento: {e}")
        return False

def esta_google_calendar_configurado(nombre_nora):
    """Verifica si Google Calendar está configurado"""
    try:
        if not existe('google_calendar_sync'):
            return False
        
        result = supabase.table('google_calendar_sync') \
            .select('access_token') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        
        return bool(result.data and result.data.get('access_token'))
        
    except Exception as e:
        return False

def obtener_configuracion_google_calendar(nombre_nora):
    """Obtiene configuración de Google Calendar"""
    try:
        if not existe('google_calendar_sync'):
            return None
        
        result = supabase.table('google_calendar_sync') \
            .select('*') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        
        return result.data
        
    except Exception as e:
        return None

def sincronizar_evento_a_google(nombre_nora, evento):
    """Sincroniza evento con Google Calendar"""
    try:
        # TODO: Implementar sincronización con Google Calendar API
        pass
        
    except Exception as e:
        print(f"Error sincronizando con Google Calendar: {e}")

def generar_url_auth_google(nombre_nora):
    """Genera URL de autenticación OAuth2 para Google Calendar"""
    try:
        # TODO: Implementar OAuth2 flow para Google Calendar
        return f"/panel_cliente/{nombre_nora}/agenda/auth/google/callback"
        
    except Exception as e:
        print(f"Error generando URL auth Google: {e}")
        return None
