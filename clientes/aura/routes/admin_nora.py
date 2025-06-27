print("✅ admin_nora.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid
from clientes.aura.middlewares.verificar_login import admin_login_required

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_nora_bp = Blueprint("admin_nora", __name__)

# ==============================================================================
# 🗂️ RUTAS ESTÁTICAS PARA ARCHIVOS JAVASCRIPT
# ==============================================================================

@admin_nora_bp.route("/admin/nora/static/js/<filename>")
def static_js(filename):
    """Servir archivos JavaScript estáticos para el panel de admin"""
    try:
        js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')
        return send_from_directory(js_path, filename)
    except Exception as e:
        print(f"❌ Error sirviendo archivo JS {filename}: {e}")
        return f"Error cargando {filename}", 404

# ==============================================================================

# 👉 Agrega soporte para /nora/editar?nombre=... redireccionando a la ruta con <nombre_nora>
@admin_nora_bp.route("/admin/nora/editar", methods=["GET"])
def redireccionar_editar_nora():
    nombre = request.args.get("nombre")
    if not nombre:
        return "❌ Parámetro 'nombre' requerido", 400
    return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre))

@admin_nora_bp.route("/admin/nora/<nombre_nora>/editar", methods=["GET", "POST"])
def editar_nora(nombre_nora):
    # Consultar módulos disponibles desde la tabla en Supabase
    try:
        response_modulos = supabase.table("modulos_disponibles").select("nombre").execute()
        modulos_disponibles = [m["nombre"] for m in response_modulos.data] if response_modulos.data else []
    except Exception as e:
        print(f"❌ Error al obtener módulos disponibles: {e}")
        modulos_disponibles = []

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        nuevos_modulos = request.form.getlist("modulos")

        if not nuevo_nombre:
            flash("❌ Debes ingresar un nombre para la Nora", "error")
            return redirect(request.url)

        if not nuevos_modulos:
            flash("❌ Debes seleccionar al menos un módulo", "error")
            return redirect(request.url)

        # Actualizar configuración en Supabase
        try:
            config["nombre_visible"] = nuevo_nombre
            config["modulos"] = nuevos_modulos
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        print(f"📝 Nora '{nombre_nora}' actualizada:")
        print(f"    ➤ Nombre visible: {nuevo_nombre}")
        print(f"    ➤ Módulos activos: {', '.join(nuevos_modulos)}")

        flash("✅ Configuración actualizada correctamente", "success")
        return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre_nora))

    return render_template(
        "admin_nora_editar.html",
        nombre_nora=nombre_nora,
        config=config,
        modulos_disponibles=modulos_disponibles
    )

# 👉 Soporte directo para /nora/editar?nombre=aura sin redirección
@admin_nora_bp.route("/editar", methods=["GET", "POST"])
def editar_nora_desde_query():
    nombre_nora = request.args.get("nombre")
    if not nombre_nora:
        return "❌ Parámetro 'nombre' requerido", 400

    # Consultar módulos disponibles desde la tabla en Supabase
    try:
        response_modulos = supabase.table("modulos_disponibles").select("nombre").execute()
        modulos_disponibles = [m["nombre"] for m in response_modulos.data] if response_modulos.data else []
    except Exception as e:
        print(f"❌ Error al obtener módulos disponibles: {e}")
        modulos_disponibles = []

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        nuevos_modulos = request.form.getlist("modulos")

        if not nuevo_nombre:
            flash("❌ Debes ingresar un nombre para la Nora", "error")
            return redirect(request.url)

        if not nuevos_modulos:
            flash("❌ Debes seleccionar al menos un módulo", "error")
            return redirect(request.url)

        try:
            config["nombre_visible"] = nuevo_nombre
            config["modulos"] = nuevos_modulos
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        flash("✅ Configuración actualizada correctamente", "success")
        return redirect(request.url)

    return render_template(
        "admin_nora_editar.html",
        nombre_nora=nombre_nora,
        config=config,
        modulos_disponibles=modulos_disponibles
    )

@admin_nora_bp.route("/admin/nora/nueva", methods=["GET", "POST"])
def crear_nora():
    try:
        response_modulos = supabase.table("modulos_disponibles").select("nombre").execute()
        modulos_disponibles = [m["nombre"] for m in response_modulos.data] if response_modulos.data else []
    except Exception as e:
        print(f"❌ Error al obtener módulos disponibles: {e}")
        modulos_disponibles = []

    if request.method == "POST":
        nombre_interno = request.form.get("nombre_interno", "").strip().lower().replace(" ", "").replace("_", "")
        nombre_visible = request.form.get("nombre_visible", "").strip()
        modulos = request.form.getlist("modulos")

        if not nombre_interno or not nombre_visible:
            flash("❌ Debes completar ambos campos", "error")
            return redirect(request.url)

        # Verificar si ya existe en Supabase
        try:
            response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_interno).execute()
            if response.data:
                flash("❌ Ya existe una Nora con ese nombre interno", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al verificar existencia de Nora: {str(e)}")
            flash("❌ Error al verificar existencia de Nora", "error")
            return redirect(request.url)

        # Crear nueva configuración en Supabase
        try:
            config = {
                "nombre_nora": nombre_interno,
                "nombre_visible": nombre_visible,
                "ia_activada": True,
                "modulos": modulos
            }
            response = supabase.table("configuracion_bot").insert(config).execute()
            if not response.data:
                flash("❌ Error al crear Nora", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al crear Nora: {str(e)}")
            flash("❌ Error al crear Nora", "error")
            return redirect(request.url)

        print(f"🆕 Nueva Nora creada: {nombre_interno} ({nombre_visible}) con módulos: {', '.join(modulos)}")

        flash("✅ Nora creada correctamente", "success")
        return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre_interno))

    return render_template(
        "admin_nora_nueva.html",
        modulos_disponibles=modulos_disponibles
    )


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar", methods=["GET", "POST"])
def entrenar_nora(nombre_nora):
    # Cargar configuración existente desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        # Obtener datos del formulario
        personalidad = request.form.get("personalidad", "").strip()
        respuestas_rapidas = request.form.get("respuestas_rapidas", "").strip()
        informacion_empresa = request.form.get("informacion_empresa", "").strip()

        # Actualizar configuración en Supabase
        try:
            config["personalidad"] = personalidad
            config["respuestas_rapidas"] = respuestas_rapidas.split(",")  # Convertir a lista
            config["informacion_empresa"] = informacion_empresa
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        print(f"🧠 Nora '{nombre_nora}' entrenada:")
        print(f"    ➤ Personalidad: {personalidad}")
        print(f"    ➤ Respuestas rápidas: {respuestas_rapidas}")
        print(f"    ➤ Información de la empresa: {informacion_empresa}")

        flash("✅ Nora entrenada correctamente", "success")
        return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

    return render_template(
        "admin_nora_entrenar.html",
        nombre_nora=nombre_nora,
        config=config
    )


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bienvenida", methods=["POST"])
def entrenar_bienvenida(nombre_nora):
    # Obtener el mensaje de bienvenida del formulario
    bienvenida = request.form.get("bienvenida", "").strip()

    if not bienvenida:
        error_msg = "❌ El mensaje de bienvenida no puede estar vacío."
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": error_msg
            }), 400
        
        flash(error_msg, "error")
        return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

    # Guardar el mensaje de bienvenida en la base de datos
    try:
        response = supabase.table("configuracion_bot").update({
            "bienvenida": bienvenida
        }).eq("nombre_nora", nombre_nora).execute()

        if not response.data:
            error_msg = "❌ Error al guardar el mensaje de bienvenida."
            
            # Si es una petición AJAX, retornar JSON de error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
                return jsonify({
                    "success": False,
                    "message": error_msg
                }), 500
            
            flash(error_msg, "error")
            return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

        # Si es una petición AJAX, retornar JSON de éxito
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": True,
                "message": "✅ Mensaje de bienvenida guardado correctamente."
            })
        
        flash("✅ Mensaje de bienvenida guardado correctamente.", "success")
    except Exception as e:
        print(f"❌ Error al guardar el mensaje de bienvenida: {str(e)}")
        error_msg = "❌ Error al guardar el mensaje de bienvenida."
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": error_msg
            }), 500
        
        flash(error_msg, "error")

    return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))


# Ruta para guardar estado de IA
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
def guardar_estado_ia(nombre_nora):
    try:
        ia_activa = request.form.get("ia_activa") == "true"
        supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
        
        # Si es una petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": True,
                "message": "✅ Estado de IA actualizado correctamente"
            })
        
        flash("✅ Estado de IA actualizado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar estado de IA: {str(e)}")
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": "❌ Error al actualizar estado de IA"
            }), 500
        
        flash("❌ Error al actualizar estado de IA", "error")
    
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para cambiar nombre
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/cambiar_nombre", methods=["POST"])
def cambiar_nombre_nora(nombre_nora):
    try:
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        if nuevo_nombre and nuevo_nombre != nombre_nora:
            supabase.table("configuracion_bot").update({"nombre_nora": nuevo_nombre}).eq("nombre_nora", nombre_nora).execute()
            flash("✅ Nombre de Nora actualizado correctamente", "success")
            return redirect(url_for("admin_nora.mostrar_lista"))
        flash("⚠️ El nuevo nombre no puede estar vacío o ser igual al actual", "warning")
    except Exception as e:
        print(f"❌ Error al cambiar nombre de Nora: {str(e)}")
        flash("❌ Error al cambiar nombre de Nora", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar personalidad
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/personalidad", methods=["POST"])
def guardar_personalidad(nombre_nora):
    try:
        personalidad = request.form.get("personalidad", "").strip()
        supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
        
        # Si es una petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": True,
                "message": "✅ Personalidad actualizada correctamente"
            })
        
        flash("✅ Personalidad actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar personalidad: {str(e)}")
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": "❌ Error al actualizar personalidad"
            }), 500
        
        flash("❌ Error al actualizar personalidad", "error")
    
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar instrucciones
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
def guardar_instrucciones(nombre_nora):
    try:
        instrucciones = request.form.get("instrucciones", "").strip()
        supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
        
        # Si es una petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": True,
                "message": "✅ Instrucciones actualizadas correctamente"
            })
        
        flash("✅ Instrucciones actualizadas correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar instrucciones: {str(e)}")
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": "❌ Error al actualizar instrucciones"
            }), 500
        
        flash("❌ Error al actualizar instrucciones", "error")
    
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar conocimiento
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/conocimiento", methods=["POST"])
def guardar_conocimiento(nombre_nora):
    try:
        conocimiento = request.form.get("base_conocimiento", "").strip()
        supabase.table("configuracion_bot").update({"base_conocimiento": conocimiento}).eq("nombre_nora", nombre_nora).execute()
        
        # Si es una petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": True,
                "message": "✅ Base de conocimiento actualizada correctamente"
            })
        
        flash("✅ Base de conocimiento actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar base de conocimiento: {str(e)}")
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({
                "success": False,
                "message": "❌ Error al actualizar base de conocimiento"
            }), 500
        
        flash("❌ Error al actualizar base de conocimiento", "error")
    
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# ==============================================================================
# 🔧 ENDPOINTS PARA GESTIÓN DE BLOQUES DE CONOCIMIENTO
# ==============================================================================

@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bloques", methods=["GET"])
def listar_bloques_conocimiento(nombre_nora):
    """Obtener todos los bloques de conocimiento activos para la Nora"""
    try:
        print(f"🔍 Buscando bloques para: {nombre_nora}")
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        print(f"✅ Resultado consulta: {len(res.data)} bloques encontrados")
        print(f"📄 Datos: {res.data}")
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        print(f"❌ Error al listar bloques: {str(e)}")
        return jsonify({"success": False, "message": f"Error al cargar los bloques: {str(e)}"}), 500


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bloques", methods=["POST"])
def crear_bloque_conocimiento(nombre_nora):
    """Crear un nuevo bloque de conocimiento"""
    try:
        data = request.get_json()
        contenido = data.get("contenido", "").strip()
        etiquetas = data.get("etiquetas", [])
        prioridad = data.get("prioridad", False)

        # Validaciones
        if not contenido:
            return jsonify({"success": False, "message": "El contenido es obligatorio"}), 400
        if len(contenido) > 500:
            return jsonify({"success": False, "message": "El contenido debe tener máximo 500 caracteres"}), 400
        if not etiquetas or not isinstance(etiquetas, list) or len(etiquetas) == 0:
            return jsonify({"success": False, "message": "Debes incluir al menos una etiqueta"}), 400

        # Crear el nuevo bloque (sin id y fecha_creacion, se generan automáticamente)
        nuevo_bloque = {
            "nombre_nora": nombre_nora,
            "contenido": contenido,
            "etiquetas": etiquetas,  # PostgreSQL text[] array
            "origen": "manual",
            "prioridad": bool(prioridad),
            "activo": True
        }
        
        print(f"🔧 Creando bloque: {nuevo_bloque}")
        res = supabase.table("conocimiento_nora").insert(nuevo_bloque).execute()
        print(f"✅ Bloque creado: {res.data}")
        return jsonify({"success": True, "data": res.data[0], "message": "✅ Bloque creado correctamente"})
        
    except Exception as e:
        print(f"❌ Error al crear bloque: {str(e)}")
        return jsonify({"success": False, "message": "Error al crear el bloque"}), 500


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bloques/<bloque_id>", methods=["PUT"])
def editar_bloque_conocimiento(nombre_nora, bloque_id):
    """Editar un bloque de conocimiento existente"""
    try:
        data = request.get_json()
        contenido = data.get("contenido", "").strip()
        etiquetas = data.get("etiquetas", [])
        prioridad = data.get("prioridad", False)

        # Validaciones
        if not contenido:
            return jsonify({"success": False, "message": "El contenido es obligatorio"}), 400
        if len(contenido) > 500:
            return jsonify({"success": False, "message": "El contenido debe tener máximo 500 caracteres"}), 400
        if not etiquetas or not isinstance(etiquetas, list) or len(etiquetas) == 0:
            return jsonify({"success": False, "message": "Debes incluir al menos una etiqueta"}), 400

        # Actualizar el bloque
        update_data = {
            "contenido": contenido,
            "etiquetas": etiquetas,
            "prioridad": bool(prioridad)
        }
        
        res = supabase.table("conocimiento_nora").update(update_data).eq("id", bloque_id).eq("nombre_nora", nombre_nora).execute()
        
        if not res.data:
            return jsonify({"success": False, "message": "Bloque no encontrado"}), 404
            
        return jsonify({"success": True, "data": res.data[0], "message": "✅ Bloque actualizado correctamente"})
        
    except Exception as e:
        print(f"❌ Error al editar bloque: {str(e)}")
        return jsonify({"success": False, "message": "Error al actualizar el bloque"}), 500


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bloques/<bloque_id>", methods=["DELETE"])
def eliminar_bloque_conocimiento(nombre_nora, bloque_id):
    """Eliminar (desactivar) un bloque de conocimiento"""
    try:
        res = supabase.table("conocimiento_nora").update({"activo": False}).eq("id", bloque_id).eq("nombre_nora", nombre_nora).execute()
        
        if not res.data:
            return jsonify({"success": False, "message": "Bloque no encontrado"}), 404
            
        return jsonify({"success": True, "message": "✅ Bloque eliminado correctamente"})
        
    except Exception as e:
        print(f"❌ Error al eliminar bloque: {str(e)}")
        return jsonify({"success": False, "message": "Error al eliminar el bloque"}), 500


# ==============================================================================

# Ruta para guardar límites de respuesta
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/limites", methods=["POST"])
def guardar_limites(nombre_nora):
    try:
        modo_respuesta = request.form.get("modo_respuesta", "flexible")
        mensaje_fuera_tema = request.form.get("mensaje_fuera_tema", "").strip()
        
        # Si no hay mensaje, usar uno por defecto
        if not mensaje_fuera_tema:
            mensaje_fuera_tema = "Lo siento, solo puedo ayudarte con consultas relacionadas a nuestra empresa. Un agente humano te contactará pronto para resolver tu consulta."
        
        update_data = {
            "modo_respuesta": modo_respuesta,
            "mensaje_fuera_tema": mensaje_fuera_tema
        }
        
        supabase.table("configuracion_bot").update(update_data).eq("nombre_nora", nombre_nora).execute()
        
        # Si es una petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "message": "✅ Límites de respuesta actualizados correctamente"
            })
        
        flash("✅ Límites de respuesta actualizados correctamente", "success")
        
    except Exception as e:
        print(f"❌ Error al actualizar límites: {str(e)}")
        
        # Si es una petición AJAX, retornar JSON de error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "message": "❌ Error al actualizar límites de respuesta"
            }), 500
        
        flash("❌ Error al actualizar límites de respuesta", "error")
    
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# ==============================================================================

# 🧪 ENDPOINT DE PRUEBA - TEMPORAL PARA DEBUG
@admin_nora_bp.route("/admin/nora/<nombre_nora>/test-db", methods=["GET"])
def test_db_connection(nombre_nora):
    """Endpoint temporal para probar conexión a base de datos"""
    try:
        # Verificar conexión general
        res_config = supabase.table("configuracion_bot").select("nombre_nora").eq("nombre_nora", nombre_nora).execute()
        print(f"🔍 Test configuracion_bot: {res_config.data}")
        
        # Verificar tabla conocimiento_nora
        res_conocimiento = supabase.table("conocimiento_nora").select("*").limit(5).execute()
        print(f"🔍 Test conocimiento_nora (todos): {res_conocimiento.data}")
        
        # Verificar tabla conocimiento_nora para esta nora específicamente
        res_nora = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).execute()
        print(f"🔍 Test conocimiento_nora ({nombre_nora}): {res_nora.data}")
        
        return jsonify({
            "success": True,
            "config_exists": len(res_config.data) > 0,
            "total_conocimiento": len(res_conocimiento.data),
            "conocimiento_nora": len(res_nora.data),
            "sample_data": res_conocimiento.data[:2],
            "nora_data": res_nora.data
        })
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# 🧪 ENDPOINT TEMPORAL PARA CREAR DATOS DE PRUEBA
@admin_nora_bp.route("/admin/nora/<nombre_nora>/test-create", methods=["POST"])
def test_create_knowledge(nombre_nora):
    """Endpoint temporal para crear datos de prueba"""
    try:
        # Crear algunos bloques de prueba
        bloques_prueba = [
            {
                "nombre_nora": nombre_nora,
                "contenido": "Somos una empresa especializada en marketing digital e inteligencia artificial.",
                "etiquetas": ["empresa", "marketing", "ia"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Nuestros horarios de atención son de lunes a viernes de 9:00 AM a 6:00 PM.",
                "etiquetas": ["horarios", "atencion"],
                "origen": "manual",
                "prioridad": False,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Ofrecemos planes desde $500 USD mensuales con consultoría personalizada incluida.",
                "etiquetas": ["precios", "planes", "consultoria"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            }
        ]
        
        resultados = []
        for bloque in bloques_prueba:
            res = supabase.table("conocimiento_nora").insert(bloque).execute()
            resultados.append(res.data)
            print(f"✅ Bloque creado: {res.data}")
        
        return jsonify({
            "success": True,
            "message": f"✅ {len(bloques_prueba)} bloques de prueba creados",
            "data": resultados
        })
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Alias para mostrar entrenamiento (para los redirects de formularios)
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/mostrar", methods=["GET"])
def mostrar_entrenamiento(nombre_nora):
    """Mostrar la página de entrenamiento (alias de entrenar_nora)"""
    return entrenar_nora(nombre_nora)


# ==============================================================================

# 🚨 ENDPOINTS DE DEBUG TEMPORALES (REMOVER EN PRODUCCIÓN)
# ==============================================================================

@admin_nora_bp.route("/admin/nora/<nombre_nora>/debug/bloques", methods=["GET"])
def debug_listar_bloques(nombre_nora):
    """DEBUG: Listar bloques sin autenticación"""
    try:
        print(f"🔍 DEBUG - Buscando bloques para: {nombre_nora}")
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        print(f"✅ DEBUG - Resultado: {len(res.data)} bloques")
        return jsonify({"success": True, "data": res.data, "debug": True})
    except Exception as e:
        print(f"❌ DEBUG - Error: {str(e)}")
        return jsonify({"success": False, "message": str(e), "debug": True}), 500

@admin_nora_bp.route("/admin/nora/<nombre_nora>/debug/test-data", methods=["POST"])
def debug_crear_datos_prueba(nombre_nora):
    """DEBUG: Crear datos de prueba"""
    try:
        datos_prueba = [
            {
                "nombre_nora": nombre_nora,
                "contenido": "Somos una empresa de marketing digital especializada en automatización con IA. Ofrecemos servicios de chatbots, análisis de datos y estrategias de contenido.",
                "etiquetas": ["servicios", "marketing", "ia"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Nuestro horario de atención es de lunes a viernes de 9:00 AM a 6:00 PM. Los fines de semana respondemos emergencias por WhatsApp.",
                "etiquetas": ["horarios", "contacto", "atencion"],
                "origen": "manual",
                "prioridad": False,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Ofrecemos planes desde $99/mes para pequeñas empresas hasta $999/mes para corporativos. Incluye chatbot, análisis mensual y soporte técnico.",
                "etiquetas": ["precios", "planes", "costos"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            }
        ]
        
        res = supabase.table("conocimiento_nora").insert(datos_prueba).execute()
        print(f"✅ DEBUG - Creados {len(res.data)} bloques de prueba")
        return jsonify({"success": True, "data": res.data, "debug": True})
    except Exception as e:
        print(f"❌ DEBUG - Error creando datos: {str(e)}")
        return jsonify({"success": False, "message": str(e), "debug": True}), 500


# ==============================================================================
# 🚨 ENDPOINTS DE DEBUG TEMPORALES FUERA DE /admin (REMOVER EN PRODUCCIÓN)
# ==============================================================================

@admin_nora_bp.route("/api/debug/<nombre_nora>/bloques", methods=["GET"])
def debug_api_listar_bloques(nombre_nora):
    """DEBUG: Listar bloques sin autenticación (fuera de /admin)"""
    try:
        print(f"🔍 DEBUG API - Buscando bloques para: {nombre_nora}")
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        print(f"✅ DEBUG API - Resultado: {len(res.data)} bloques")
        return jsonify({"success": True, "data": res.data, "debug_api": True})
    except Exception as e:
        print(f"❌ DEBUG API - Error: {str(e)}")
        return jsonify({"success": False, "message": str(e), "debug_api": True}), 500

@admin_nora_bp.route("/api/debug/<nombre_nora>/test-data", methods=["POST"])
def debug_api_crear_datos_prueba(nombre_nora):
    """DEBUG: Crear datos de prueba (fuera de /admin)"""
    try:
        datos_prueba = [
            {
                "nombre_nora": nombre_nora,
                "contenido": "Somos una empresa de marketing digital especializada en automatización con IA. Ofrecemos servicios de chatbots, análisis de datos y estrategias de contenido.",
                "etiquetas": ["servicios", "marketing", "ia"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Nuestro horario de atención es de lunes a viernes de 9:00 AM a 6:00 PM. Los fines de semana respondemos emergencias por WhatsApp.",
                "etiquetas": ["horarios", "contacto", "atencion"],
                "origen": "manual",
                "prioridad": False,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Ofrecemos planes desde $99/mes para pequeñas empresas hasta $999/mes para corporativos. Incluye chatbot, análisis mensual y soporte técnico.",
                "etiquetas": ["precios", "planes", "costos"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            }
        ]
        
        res = supabase.table("conocimiento_nora").insert(datos_prueba).execute()
        print(f"✅ DEBUG API - Creados {len(res.data)} bloques de prueba")
        return jsonify({"success": True, "data": res.data, "debug_api": True})
    except Exception as e:
        print(f"❌ DEBUG API - Error creando datos: {str(e)}")
        return jsonify({"success": False, "message": str(e), "debug_api": True}), 500
