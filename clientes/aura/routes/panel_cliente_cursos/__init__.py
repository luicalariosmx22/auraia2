# ✅ Archivo: clientes/aura/routes/panel_cliente_cursos/__init__.py
# 👉 Módulo CURSOS para gestión de cursos y programas educativos

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import uuid

# Crear el blueprint principal del módulo
panel_cliente_cursos_bp = Blueprint(
    'panel_cliente_cursos',
    __name__,
    template_folder='../../templates/panel_cliente_cursos'
)

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos')
def index_cursos(nombre_nora):
    """Vista principal del módulo de cursos"""
    try:
        # Obtener cursos de la base de datos
        cursos_response = supabase.table('cursos').select('*').eq('nombre_nora', nombre_nora).execute()
        cursos = cursos_response.data if cursos_response.data else []
        
        # Estadísticas básicas
        total_cursos = len(cursos)
        cursos_activos = len([c for c in cursos if c.get('activo', True)])
        estudiantes_total = sum([c.get('estudiantes_inscritos', 0) for c in cursos])
        
        return render_template(
            'panel_cliente_cursos/index.html',
            nombre_nora=nombre_nora,
            cursos=cursos,
            total_cursos=total_cursos,
            cursos_activos=cursos_activos,
            estudiantes_total=estudiantes_total
        )
    except Exception as e:
        print(f"Error en index_cursos: {e}")
        return render_template(
            'panel_cliente_cursos/index.html',
            nombre_nora=nombre_nora,
            cursos=[],
            total_cursos=0,
            cursos_activos=0,
            estudiantes_total=0,
            error="Error al cargar los cursos"
        )

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/nuevo', methods=['GET', 'POST'])
def nuevo_curso(nombre_nora):
    """Crear nuevo curso"""
    if request.method == 'POST':
        try:
            # Recoger datos del formulario
            datos_curso = {
                'id': str(uuid.uuid4()),
                'nombre_nora': nombre_nora,
                'titulo': request.form.get('titulo'),
                'descripcion': request.form.get('descripcion'),
                'categoria': request.form.get('categoria'),
                'nivel': request.form.get('nivel'),
                'duracion_horas': int(request.form.get('duracion_horas', 0)),
                'precio': float(request.form.get('precio', 0)),
                'precio_pronto_pago': float(request.form.get('precio_pronto_pago', 0)),
                'modalidad': request.form.get('modalidad'),
                'fecha_inicio': request.form.get('fecha_inicio'),
                'fecha_fin': request.form.get('fecha_fin'),
                'instructor': request.form.get('instructor'),
                'max_estudiantes': int(request.form.get('max_estudiantes', 0)),
                'direccion': request.form.get('direccion', ''),
                'google_maps_link': request.form.get('google_maps_link', ''),
                'horario_lunes': request.form.get('horario_lunes', ''),
                'horario_martes': request.form.get('horario_martes', ''),
                'horario_miercoles': request.form.get('horario_miercoles', ''),
                'horario_jueves': request.form.get('horario_jueves', ''),
                'horario_viernes': request.form.get('horario_viernes', ''),
                'horario_sabado': request.form.get('horario_sabado', ''),
                'horario_domingo': request.form.get('horario_domingo', ''),
                'estudiantes_inscritos': 0,
                'activo': 'activo' in request.form,
                'fecha_creacion': datetime.now().isoformat(),
                'contenido_detalle': request.form.get('contenido_detalle', ''),
                'requisitos': request.form.get('requisitos', ''),
                'objetivos': request.form.get('objetivos', '')
            }
            
            # Insertar en base de datos
            response = supabase.table('cursos').insert(datos_curso).execute()
            
            if response.data:
                flash('Curso creado exitosamente', 'success')
                return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))
            else:
                flash('Error al crear el curso', 'error')
                
        except Exception as e:
            print(f"Error al crear curso: {e}")
            flash('Error al crear el curso', 'error')
    
    return render_template('panel_cliente_cursos/nuevo_curso.html', nombre_nora=nombre_nora)

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/<curso_id>')
def detalle_curso(nombre_nora, curso_id):
    """Ver detalle de un curso específico"""
    try:
        # Obtener curso
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if not curso_response.data:
            flash('Curso no encontrado', 'error')
            return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))
        
        curso = curso_response.data[0]
        
        # Obtener estudiantes inscritos (si existe tabla de inscripciones)
        estudiantes_response = supabase.table('curso_inscripciones').select('*, estudiante:estudiantes(*)').eq('curso_id', curso_id).execute()
        estudiantes = estudiantes_response.data if estudiantes_response.data else []
        
        return render_template(
            'panel_cliente_cursos/detalle_curso.html',
            nombre_nora=nombre_nora,
            curso=curso,
            estudiantes=estudiantes
        )
        
    except Exception as e:
        print(f"Error en detalle_curso: {e}")
        flash('Error al cargar el curso', 'error')
        return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/<curso_id>/editar', methods=['GET', 'POST'])
def editar_curso(nombre_nora, curso_id):
    """Editar curso existente"""
    try:
        # Obtener curso actual
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if not curso_response.data:
            flash('Curso no encontrado', 'error')
            return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))
        
        curso = curso_response.data[0]
        
        if request.method == 'POST':
            # Actualizar datos del curso
            datos_actualizacion = {
                'titulo': request.form.get('titulo'),
                'descripcion': request.form.get('descripcion'),
                'categoria': request.form.get('categoria'),
                'nivel': request.form.get('nivel'),
                'duracion_horas': int(request.form.get('duracion_horas', 0)),
                'precio': float(request.form.get('precio', 0)),
                'precio_pronto_pago': float(request.form.get('precio_pronto_pago', 0)),
                'modalidad': request.form.get('modalidad'),
                'fecha_inicio': request.form.get('fecha_inicio'),
                'fecha_fin': request.form.get('fecha_fin'),
                'instructor': request.form.get('instructor'),
                'max_estudiantes': int(request.form.get('max_estudiantes', 0)),
                'direccion': request.form.get('direccion', ''),
                'google_maps_link': request.form.get('google_maps_link', ''),
                'horario_lunes': request.form.get('horario_lunes', ''),
                'horario_martes': request.form.get('horario_martes', ''),
                'horario_miercoles': request.form.get('horario_miercoles', ''),
                'horario_jueves': request.form.get('horario_jueves', ''),
                'horario_viernes': request.form.get('horario_viernes', ''),
                'horario_sabado': request.form.get('horario_sabado', ''),
                'horario_domingo': request.form.get('horario_domingo', ''),
                'activo': 'activo' in request.form,
                'contenido_detalle': request.form.get('contenido_detalle', ''),
                'requisitos': request.form.get('requisitos', ''),
                'objetivos': request.form.get('objetivos', ''),
                'fecha_actualizacion': datetime.now().isoformat()
            }
            
            response = supabase.table('cursos').update(datos_actualizacion).eq('id', curso_id).execute()
            
            if response.data:
                flash('Curso actualizado exitosamente', 'success')
                return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))
            else:
                flash('Error al actualizar el curso', 'error')
        
        return render_template('panel_cliente_cursos/editar_curso.html', nombre_nora=nombre_nora, curso=curso)
        
    except Exception as e:
        print(f"Error en editar_curso: {e}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/<curso_id>/eliminar', methods=['POST'])
def eliminar_curso(nombre_nora, curso_id):
    """Eliminar curso"""
    try:
        response = supabase.table('cursos').delete().eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if response.data:
            flash('Curso eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el curso', 'error')
            
    except Exception as e:
        print(f"Error al eliminar curso: {e}")
        flash('Error al eliminar el curso', 'error')
    
    return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/estudiantes')
def gestionar_estudiantes(nombre_nora):
    """Gestionar estudiantes de todos los cursos"""
    try:
        # Obtener todos los estudiantes inscritos en cursos de esta nora
        estudiantes_response = supabase.table('curso_inscripciones')\
            .select('*, curso:cursos(*), estudiante:estudiantes(*)')\
            .eq('cursos.nombre_nora', nombre_nora)\
            .execute()
        
        estudiantes = estudiantes_response.data if estudiantes_response.data else []
        
        return render_template(
            'panel_cliente_cursos/estudiantes.html',
            nombre_nora=nombre_nora,
            estudiantes=estudiantes
        )
        
    except Exception as e:
        print(f"Error en gestionar_estudiantes: {e}")
        return render_template(
            'panel_cliente_cursos/estudiantes.html',
            nombre_nora=nombre_nora,
            estudiantes=[],
            error="Error al cargar estudiantes"
        )

# Endpoint para obtener datos para gráficos y estadísticas
@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/api/estadisticas')
def api_estadisticas(nombre_nora):
    """API endpoint para estadísticas de cursos"""
    try:
        # Obtener cursos con estadísticas
        cursos_response = supabase.table('cursos').select('*').eq('nombre_nora', nombre_nora).execute()
        cursos = cursos_response.data if cursos_response.data else []
        
        # Calcular estadísticas
        estadisticas = {
            'cursos_por_categoria': {},
            'cursos_por_modalidad': {},
            'estudiantes_por_curso': {},
            'ingresos_por_curso': {},
            'total_ingresos': 0
        }
        
        for curso in cursos:
            # Por categoría
            cat = curso.get('categoria', 'Sin categoría')
            estadisticas['cursos_por_categoria'][cat] = estadisticas['cursos_por_categoria'].get(cat, 0) + 1
            
            # Por modalidad
            mod = curso.get('modalidad', 'No definida')
            estadisticas['cursos_por_modalidad'][mod] = estadisticas['cursos_por_modalidad'].get(mod, 0) + 1
            
            # Estudiantes por curso
            estadisticas['estudiantes_por_curso'][curso['titulo']] = curso.get('estudiantes_inscritos', 0)
            
            # Ingresos por curso
            ingresos = curso.get('estudiantes_inscritos', 0) * curso.get('precio', 0)
            estadisticas['ingresos_por_curso'][curso['titulo']] = ingresos
            estadisticas['total_ingresos'] += ingresos
        
        return jsonify(estadisticas)
        
    except Exception as e:
        print(f"Error en api_estadisticas: {e}")
        return jsonify({'error': str(e)}), 500

# ===== GESTIÓN DE ESTUDIANTES E INSCRIPCIONES =====

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/<curso_id>/inscribir', methods=['GET', 'POST'])
def inscribir_estudiante(nombre_nora, curso_id):
    """Inscribir nuevo estudiante a un curso"""
    try:
        # Verificar que el curso existe
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        if not curso_response.data:
            flash('Curso no encontrado', 'error')
            return redirect(url_for('panel_cliente_cursos.index_cursos', nombre_nora=nombre_nora))
        
        curso = curso_response.data[0]
        
        if request.method == 'POST':
            # Datos del estudiante
            datos_estudiante = {
                'id': str(uuid.uuid4()),
                'nombre_nora': nombre_nora,
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'email': request.form.get('email'),
                'telefono': request.form.get('telefono', ''),
                'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
                'nivel_educativo': request.form.get('nivel_educativo', ''),
                'experiencia_previa': request.form.get('experiencia_previa', ''),
                'fecha_registro': datetime.now().isoformat(),
                'activo': True
            }
            
            # Verificar si el estudiante ya existe por email
            estudiante_existente = supabase.table('estudiantes').select('*').eq('email', datos_estudiante['email']).eq('nombre_nora', nombre_nora).execute()
            
            if estudiante_existente.data:
                estudiante_id = estudiante_existente.data[0]['id']
                flash('Estudiante ya registrado, procediendo con la inscripción', 'info')
            else:
                # Crear nuevo estudiante
                response_estudiante = supabase.table('estudiantes').insert(datos_estudiante).execute()
                if not response_estudiante.data:
                    flash('Error al registrar estudiante', 'error')
                    return render_template('panel_cliente_cursos/inscribir_estudiante.html', nombre_nora=nombre_nora, curso=curso)
                estudiante_id = response_estudiante.data[0]['id']
            
            # Verificar si ya está inscrito en este curso
            inscripcion_existente = supabase.table('curso_inscripciones').select('*').eq('curso_id', curso_id).eq('estudiante_id', estudiante_id).execute()
            
            if inscripcion_existente.data:
                flash('El estudiante ya está inscrito en este curso', 'warning')
                return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))
            
            # Verificar capacidad del curso
            if curso['estudiantes_inscritos'] >= curso['max_estudiantes']:
                flash('El curso ha alcanzado su capacidad máxima', 'warning')
                return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))
            
            # Crear inscripción
            datos_inscripcion = {
                'id': str(uuid.uuid4()),
                'curso_id': curso_id,
                'estudiante_id': estudiante_id,
                'fecha_inscripcion': datetime.now().isoformat(),
                'estado': 'inscrito',
                'fecha_pago': request.form.get('fecha_pago', ''),
                'monto_pagado': float(request.form.get('monto_pagado', curso['precio'])),
                'metodo_pago': request.form.get('metodo_pago', ''),
                'notas': request.form.get('notas', '')
            }
            
            response_inscripcion = supabase.table('curso_inscripciones').insert(datos_inscripcion).execute()
            
            if response_inscripcion.data:
                # Actualizar contador de estudiantes en el curso
                nuevo_contador = curso['estudiantes_inscritos'] + 1
                supabase.table('cursos').update({'estudiantes_inscritos': nuevo_contador}).eq('id', curso_id).execute()
                
                flash('Estudiante inscrito exitosamente', 'success')
                return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))
            else:
                flash('Error al inscribir estudiante', 'error')
        
        return render_template('panel_cliente_cursos/inscribir_estudiante.html', nombre_nora=nombre_nora, curso=curso)
        
    except Exception as e:
        print(f"Error en inscribir_estudiante: {e}")
        flash('Error al procesar la inscripción', 'error')
        return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/<curso_id>/estudiante/<inscripcion_id>/cancelar', methods=['POST'])
def cancelar_inscripcion(nombre_nora, curso_id, inscripcion_id):
    """Cancelar inscripción de un estudiante"""
    try:
        # Verificar que la inscripción existe
        inscripcion_response = supabase.table('curso_inscripciones').select('*').eq('id', inscripcion_id).execute()
        
        if not inscripcion_response.data:
            flash('Inscripción no encontrada', 'error')
        else:
            # Actualizar estado de la inscripción
            response = supabase.table('curso_inscripciones').update({
                'estado': 'cancelado',
                'fecha_cancelacion': datetime.now().isoformat()
            }).eq('id', inscripcion_id).execute()
            
            if response.data:
                # Actualizar contador de estudiantes en el curso
                curso_response = supabase.table('cursos').select('estudiantes_inscritos').eq('id', curso_id).execute()
                if curso_response.data:
                    nuevo_contador = max(0, curso_response.data[0]['estudiantes_inscritos'] - 1)
                    supabase.table('cursos').update({'estudiantes_inscritos': nuevo_contador}).eq('id', curso_id).execute()
                
                flash('Inscripción cancelada exitosamente', 'success')
            else:
                flash('Error al cancelar inscripción', 'error')
    
    except Exception as e:
        print(f"Error en cancelar_inscripcion: {e}")
        flash('Error al cancelar inscripción', 'error')
    
    return redirect(url_for('panel_cliente_cursos.detalle_curso', nombre_nora=nombre_nora, curso_id=curso_id))

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/estudiantes')
def listar_estudiantes(nombre_nora):
    """Listar todos los estudiantes registrados"""
    try:
        estudiantes_response = supabase.table('estudiantes').select('*').eq('nombre_nora', nombre_nora).execute()
        estudiantes = estudiantes_response.data if estudiantes_response.data else []
        
        # Obtener inscripciones para cada estudiante
        for estudiante in estudiantes:
            inscripciones_response = supabase.table('curso_inscripciones')\
                .select('*, curso:cursos(titulo)')\
                .eq('estudiante_id', estudiante['id'])\
                .execute()
            estudiante['inscripciones'] = inscripciones_response.data if inscripciones_response.data else []
        
        return render_template(
            'panel_cliente_cursos/estudiantes.html',
            nombre_nora=nombre_nora,
            estudiantes=estudiantes
        )
        
    except Exception as e:
        print(f"Error en listar_estudiantes: {e}")
        return render_template(
            'panel_cliente_cursos/estudiantes.html',
            nombre_nora=nombre_nora,
            estudiantes=[],
            error="Error al cargar estudiantes"
        )

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/estudiante/<estudiante_id>')
def detalle_estudiante(nombre_nora, estudiante_id):
    """Ver detalle de un estudiante específico"""
    try:
        # Obtener estudiante
        estudiante_response = supabase.table('estudiantes').select('*').eq('id', estudiante_id).eq('nombre_nora', nombre_nora).execute()
        
        if not estudiante_response.data:
            flash('Estudiante no encontrado', 'error')
            return redirect(url_for('panel_cliente_cursos.listar_estudiantes', nombre_nora=nombre_nora))
        
        estudiante = estudiante_response.data[0]
        
        # Obtener inscripciones del estudiante
        inscripciones_response = supabase.table('curso_inscripciones')\
            .select('*, curso:cursos(*)')\
            .eq('estudiante_id', estudiante_id)\
            .execute()
        inscripciones = inscripciones_response.data if inscripciones_response.data else []
        
        return render_template(
            'panel_cliente_cursos/detalle_estudiante.html',
            nombre_nora=nombre_nora,
            estudiante=estudiante,
            inscripciones=inscripciones
        )
        
    except Exception as e:
        print(f"Error en detalle_estudiante: {e}")
        flash('Error al cargar el estudiante', 'error')
        return redirect(url_for('panel_cliente_cursos.listar_estudiantes', nombre_nora=nombre_nora))

# ===== ENDPOINTS API ADICIONALES =====

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/api/buscar_estudiante')
def api_buscar_estudiante(nombre_nora):
    """Buscar estudiante por email o nombre para inscripción rápida"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
        
        # Buscar por email o nombre
        estudiantes_response = supabase.table('estudiantes')\
            .select('*')\
            .eq('nombre_nora', nombre_nora)\
            .or_(f'email.ilike.%{query}%,nombre.ilike.%{query}%,apellido.ilike.%{query}%')\
            .limit(10)\
            .execute()
        
        estudiantes = estudiantes_response.data if estudiantes_response.data else []
        
        return jsonify([{
            'id': est['id'],
            'nombre': f"{est['nombre']} {est['apellido']}",
            'email': est['email'],
            'telefono': est.get('telefono', '')
        } for est in estudiantes])
        
    except Exception as e:
        print(f"Error en api_buscar_estudiante: {e}")
        return jsonify([])

@panel_cliente_cursos_bp.route('/panel_cliente/<nombre_nora>/cursos/api/duplicar/<curso_id>', methods=['POST'])
def api_duplicar_curso(nombre_nora, curso_id):
    """Duplicar un curso existente"""
    try:
        # Obtener curso original
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if not curso_response.data:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        curso_original = curso_response.data[0]
        
        # Crear nuevo curso duplicado
        nuevo_curso = curso_original.copy()
        nuevo_curso['id'] = str(uuid.uuid4())
        nuevo_curso['titulo'] = f"{curso_original['titulo']} (Copia)"
        nuevo_curso['estudiantes_inscritos'] = 0
        nuevo_curso['fecha_creacion'] = datetime.now().isoformat()
        nuevo_curso['fecha_actualizacion'] = datetime.now().isoformat()
        
        # Limpiar campos de fechas si es necesario
        if 'fecha_inicio' in nuevo_curso:
            nuevo_curso['fecha_inicio'] = ''
        if 'fecha_fin' in nuevo_curso:
            nuevo_curso['fecha_fin'] = ''
        
        response = supabase.table('cursos').insert(nuevo_curso).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'message': 'Curso duplicado exitosamente',
                'nuevo_curso_id': response.data[0]['id']
            })
        else:
            return jsonify({'error': 'Error al duplicar curso'}), 500
            
    except Exception as e:
        print(f"Error en api_duplicar_curso: {e}")
        return jsonify({'error': str(e)}), 500

# ===== RUTAS PÚBLICAS PARA AUTO-REGISTRO =====

@panel_cliente_cursos_bp.route('/registro-publico/<nombre_nora>/curso/<curso_id>', methods=['GET', 'POST'])
def auto_registro_publico(nombre_nora, curso_id):
    """Página pública para que estudiantes se auto-registren en un curso"""
    try:
        # Obtener información del curso
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if not curso_response.data:
            return render_template('panel_cliente_cursos/error_publico.html', 
                                 error="Curso no encontrado o no disponible")
        
        curso = curso_response.data[0]
        
        # Verificar si el curso está activo
        if not curso.get('activo', True):
            return render_template('panel_cliente_cursos/error_publico.html', 
                                 error="Este curso no está disponible para registro")
        
        # Verificar capacidad
        if curso.get('estudiantes_inscritos', 0) >= curso.get('max_estudiantes', 999):
            return render_template('panel_cliente_cursos/error_publico.html', 
                                 error="Este curso ha alcanzado su capacidad máxima")
        
        if request.method == 'POST':
            # Procesar registro
            try:
                # Datos del estudiante
                datos_estudiante = {
                    'id': str(uuid.uuid4()),
                    'nombre_nora': nombre_nora,
                    'nombre': request.form.get('nombre'),
                    'apellido': request.form.get('apellido'),
                    'email': request.form.get('email'),
                    'telefono': request.form.get('telefono', ''),
                    'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
                    'nivel_educativo': request.form.get('nivel_educativo', ''),
                    'experiencia_previa': request.form.get('experiencia_previa', ''),
                    'proyecto_empresa': request.form.get('proyecto_empresa', ''),
                    'red_social': request.form.get('red_social', ''),
                    'fecha_registro': datetime.now().isoformat(),
                    'activo': True
                }
                
                # Verificar si el estudiante ya existe por email
                estudiante_existente = supabase.table('estudiantes').select('*').eq('email', datos_estudiante['email']).eq('nombre_nora', nombre_nora).execute()
                
                if estudiante_existente.data:
                    estudiante_id = estudiante_existente.data[0]['id']
                    
                    # Verificar si ya está registrado en este curso
                    inscripcion_existente = supabase.table('curso_inscripciones').select('*').eq('curso_id', curso_id).eq('estudiante_id', estudiante_id).execute()
                    
                    if inscripcion_existente.data:
                        return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                             curso=curso, 
                                             resultado="warning",
                                             mensaje="Ya estás registrado en este curso")
                else:
                    # Crear nuevo estudiante
                    response_estudiante = supabase.table('estudiantes').insert(datos_estudiante).execute()
                    if not response_estudiante.data:
                        return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                             curso=curso, 
                                             resultado="error",
                                             mensaje="Error al registrar tus datos")
                    estudiante_id = response_estudiante.data[0]['id']
                
                # Verificar capacidad nuevamente
                curso_actualizado = supabase.table('cursos').select('*').eq('id', curso_id).execute()
                if curso_actualizado.data[0]['estudiantes_inscritos'] >= curso_actualizado.data[0]['max_estudiantes']:
                    return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                         curso=curso, 
                                         resultado="error",
                                         mensaje="El curso ha alcanzado su capacidad máxima")
                
                # Determinar precio según tipo de pago seleccionado
                tipo_pago = request.form.get('tipo_pago', 'regular')
                if tipo_pago == 'pronto_pago' and curso.get('precio_pronto_pago'):
                    precio_aplicado = curso['precio_pronto_pago']
                    notas_pago = 'Registro con precio de pronto pago (48 horas)'
                else:
                    precio_aplicado = curso.get('precio', 0)
                    notas_pago = 'Registro con precio regular'
                
                # Crear inscripción
                datos_inscripcion = {
                    'id': str(uuid.uuid4()),
                    'curso_id': curso_id,
                    'estudiante_id': estudiante_id,
                    'fecha_inscripcion': datetime.now().isoformat(),
                    'estado': 'inscrito',
                    'monto_pagado': precio_aplicado,
                    'metodo_pago': f'Pronto Pago' if tipo_pago == 'pronto_pago' else 'Regular',
                    'notas': f'Registro realizado por auto-registro público - {notas_pago}'
                }
                
                response_inscripcion = supabase.table('curso_inscripciones').insert(datos_inscripcion).execute()
                
                if response_inscripcion.data:
                    # Actualizar contador de estudiantes en el curso
                    nuevo_contador = curso_actualizado.data[0]['estudiantes_inscritos'] + 1
                    supabase.table('cursos').update({'estudiantes_inscritos': nuevo_contador}).eq('id', curso_id).execute()
                    
                    return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                         curso=curso, 
                                         resultado="success",
                                         mensaje="¡Registro exitoso! Te hemos registrado en el curso")
                else:
                    return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                         curso=curso, 
                                         resultado="error",
                                         mensaje="Error al procesar el registro")
                                         
            except Exception as e:
                print(f"Error en auto_registro_publico POST: {e}")
                return render_template('panel_cliente_cursos/auto_registro_resultado.html', 
                                     curso=curso, 
                                     resultado="error",
                                     mensaje="Error interno del sistema")
        
        # Mostrar formulario de registro
        return render_template('panel_cliente_cursos/auto_registro_publico.html', curso=curso, nombre_nora=nombre_nora)
        
    except Exception as e:
        print(f"Error en auto_registro_publico: {e}")
        return render_template('panel_cliente_cursos/error_publico.html', 
                             error="Error interno del sistema")

@panel_cliente_cursos_bp.route('/info-curso-publico/<nombre_nora>/curso/<curso_id>')
def info_curso_publico(nombre_nora, curso_id):
    """Vista pública con información del curso (sin necesidad de login)"""
    try:
        # Obtener información del curso
        curso_response = supabase.table('cursos').select('*').eq('id', curso_id).eq('nombre_nora', nombre_nora).execute()
        
        if not curso_response.data:
            return render_template('panel_cliente_cursos/error_publico.html', 
                                 error="Curso no encontrado")
        
        curso = curso_response.data[0]
        
        # Obtener estadísticas básicas (sin datos sensibles)
        estadisticas = {
            'estudiantes_inscritos': curso.get('estudiantes_inscritos', 0),
            'capacidad_maxima': curso.get('max_estudiantes', 0),
            'disponibilidad': curso.get('max_estudiantes', 0) - curso.get('estudiantes_inscritos', 0),
            'esta_disponible': curso.get('estudiantes_inscritos', 0) < curso.get('max_estudiantes', 999) and curso.get('activo', True)
        }
        
        return render_template('panel_cliente_cursos/info_curso_publico.html', 
                             curso=curso, 
                             nombre_nora=nombre_nora,
                             estadisticas=estadisticas)
        
    except Exception as e:
        print(f"Error en info_curso_publico: {e}")
        return render_template('panel_cliente_cursos/error_publico.html', 
                             error="Error al cargar información del curso")
