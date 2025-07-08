print("✅ cliente_nora.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from clientes.aura.utils.auth_supabase import login_required_supabase, login_required_ajax_supabase
from clientes.aura.utils.login_required import login_required_cliente, login_required_ajax, login_required_ajax_debug

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

cliente_nora_bp = Blueprint("cliente_nora", __name__, 
                           static_folder='../static',
                           template_folder='../templates')

# Ruta para entrenamiento (personalidad, instrucciones, IA, nombre_nora)
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar", methods=["GET"])
@login_required_supabase
def panel_entrenamiento(nombre_nora):
    try:
        config_res = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        if not config_res.data:
            print(f"⚠️ No se encontró configuración para {nombre_nora}, creando configuración por defecto...")
            
            # Crear configuración por defecto
            config_default = {
                "nombre_nora": nombre_nora,
                "personalidad": "Soy un asistente virtual amigable y profesional.",
                "instrucciones": "Ayudo con consultas generales sobre la empresa.",
                "ia_activa": True,
                "modo_respuesta": "flexible",
                "mensaje_fuera_tema": "Lo siento, solo puedo ayudarte con consultas relacionadas a nuestra empresa.",
                "bienvenida": f"¡Hola! 👋 Soy {nombre_nora.capitalize()}, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            }
            
            # Insertar configuración por defecto
            insert_res = supabase.table("configuracion_bot").insert(config_default).execute()
            
            if insert_res.data:
                print(f"✅ Configuración por defecto creada para {nombre_nora}")
                config = insert_res.data[0]
            else:
                print(f"❌ Error al crear configuración por defecto para {nombre_nora}")
                flash("❌ Error al crear configuración por defecto", "error")
                return redirect(url_for("index"))  # Redirect a página principal
        else:
            config = config_res.data
        return render_template("admin_nora_entrenar.html", nombre_nora=nombre_nora, config=config)

    except Exception as e:
        print(f"❌ Error al cargar entrenamiento: {e}")
        flash("❌ Error al cargar entrenamiento", "error")
        return redirect(url_for("index"))  # Redirect a página principal

# Ruta para actualizar la personalidad
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/personalidad", methods=["POST"])
@login_required_ajax_supabase
def personalidad(nombre_nora):
    try:
        personalidad = request.form.get("personalidad", "").strip()
        print(f"🔧 Actualizando personalidad para {nombre_nora}: {personalidad[:100]}...")
        
        result = supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
        print(f"✅ Resultado de actualización: {result}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result.data:
                return jsonify({"success": True, "message": "Personalidad actualizada correctamente"})
            else:
                return jsonify({"success": False, "message": "No se encontró el registro para actualizar"}), 400
        
        # Si no es AJAX, hacer redirect normal
        if result.data:
            print("✅ Personalidad actualizada correctamente en BD")
        else:
            print("⚠️ No se encontró registro para actualizar")
            
    except Exception as e:
        print(f"❌ Error al actualizar personalidad: {str(e)}")
        print(f"❌ Traceback completo: {e}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
    
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para actualizar las instrucciones
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
@login_required_ajax_supabase
def instrucciones(nombre_nora):
    try:
        instrucciones = request.form.get("instrucciones", "").strip()
        print(f"🔧 Actualizando instrucciones para {nombre_nora}: {instrucciones[:100]}...")
        
        result = supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
        print(f"✅ Resultado de actualización: {result}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result.data:
                return jsonify({"success": True, "message": "Instrucciones actualizadas correctamente"})
            else:
                return jsonify({"success": False, "message": "No se encontró el registro para actualizar"}), 400
        
        # Si no es AJAX, hacer redirect normal
        if result.data:
            print("✅ Instrucciones actualizadas correctamente en BD")
        else:
            print("⚠️ No se encontró registro para actualizar")
            
    except Exception as e:
        print(f"❌ Error al actualizar instrucciones: {str(e)}")
        print(f"❌ Traceback completo: {e}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
    
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para activar o desactivar la IA
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
@login_required_ajax_supabase
def estado_ia(nombre_nora):
    try:
        ia_activa = request.form.get("ia_activa") == "true"
        print(f"🔧 Actualizando estado IA para {nombre_nora}: {ia_activa}")
        
        result = supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
        print(f"✅ Resultado de actualización: {result}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result.data:
                return jsonify({"success": True, "message": "Estado de IA actualizado correctamente"})
            else:
                return jsonify({"success": False, "message": "No se encontró el registro para actualizar"}), 400
        
        # Si no es AJAX, hacer redirect normal
        if result.data:
            print("✅ Estado de IA actualizado correctamente en BD")
        else:
            print("⚠️ No se encontró registro para actualizar")
            
    except Exception as e:
        print(f"❌ Error al actualizar estado de IA: {str(e)}")
        print(f"❌ Traceback completo: {e}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
    
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))


# ========================================
# 🧠 GESTIÓN DE BLOQUES DE CONOCIMIENTO
# ========================================

# ✅ Endpoint: Obtener bloques de conocimiento activos
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/bloques", methods=["GET"])
@login_required_ajax_debug
def obtener_bloques_conocimiento(nombre_nora):
    try:
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ✅ Endpoint: Agregar nuevo bloque de conocimiento
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/bloques", methods=["POST"])
@login_required_ajax
def agregar_bloque_conocimiento(nombre_nora):
    try:
        body = request.get_json()
        contenido = body.get("contenido", "").strip()
        etiquetas = body.get("etiquetas", [])
        prioridad = bool(body.get("prioridad", False))

        if not contenido or len(contenido) > 500:
            return jsonify({"success": False, "message": "Contenido inválido"}), 400

        nuevo_bloque = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "contenido": contenido,
            "etiquetas": etiquetas,
            "origen": "manual",
            "prioridad": prioridad,
            "activo": True,
            "fecha_creacion": datetime.utcnow().isoformat()
        }

        res = supabase.table("conocimiento_nora").insert(nuevo_bloque).execute()
        return jsonify({"success": True, "data": res.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ✅ Endpoint: Eliminar (desactivar) un bloque de conocimiento
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/bloques/<id_bloque>", methods=["DELETE"])
@login_required_ajax
def eliminar_bloque_conocimiento(nombre_nora, id_bloque):
    try:
        res = supabase.table("conocimiento_nora") \
            .update({"activo": False}) \
            .eq("id", id_bloque) \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========================================
# 🎯 ENDPOINTS ADICIONALES PARA FORMULARIOS
# ========================================

# Ruta para actualizar límites de respuesta
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/limites", methods=["POST"])
@login_required_ajax_supabase
def limites(nombre_nora):
    try:
        modo_respuesta = request.form.get("modo_respuesta", "flexible")
        mensaje_fuera_tema = request.form.get("mensaje_fuera_tema", "").strip()
        
        print(f"🔧 Actualizando límites para {nombre_nora}: modo={modo_respuesta}")
        
        result = supabase.table("configuracion_bot").update({
            "modo_respuesta": modo_respuesta,
            "mensaje_fuera_tema": mensaje_fuera_tema
        }).eq("nombre_nora", nombre_nora).execute()
        
        print(f"✅ Resultado de actualización: {result}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result.data:
                return jsonify({"success": True, "message": "Límites actualizados correctamente"})
            else:
                return jsonify({"success": False, "message": "No se encontró el registro para actualizar"}), 400
        
        # Si no es AJAX, hacer redirect normal
        if result.data:
            print("✅ Límites actualizados correctamente en BD")
        else:
            print("⚠️ No se encontró registro para actualizar")
            
    except Exception as e:
        print(f"❌ Error al actualizar límites: {str(e)}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
    
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para actualizar mensaje de bienvenida
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/bienvenida", methods=["POST"])
@login_required_ajax_supabase
def bienvenida(nombre_nora):
    try:
        bienvenida = request.form.get("bienvenida", "").strip()
        print(f"🔧 Actualizando bienvenida para {nombre_nora}: {bienvenida[:100]}...")
        
        result = supabase.table("configuracion_bot").update({"bienvenida": bienvenida}).eq("nombre_nora", nombre_nora).execute()
        print(f"✅ Resultado de actualización: {result}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result.data:
                return jsonify({"success": True, "message": "Mensaje de bienvenida actualizado correctamente"})
            else:
                return jsonify({"success": False, "message": "No se encontró el registro para actualizar"}), 400
        
        # Si no es AJAX, hacer redirect normal
        if result.data:
            print("✅ Bienvenida actualizada correctamente en BD")
        else:
            print("⚠️ No se encontró registro para actualizar")
            
    except Exception as e:
        print(f"❌ Error al actualizar bienvenida: {str(e)}")
        
        # Verificar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
    
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))


# ========================================
# 🧪 ENDPOINTS TEMPORALES PARA TESTING - ⚠️ ELIMINAR EN PRODUCCIÓN
# ========================================
# ⚠️ ADVERTENCIA: Estos endpoints NO requieren autenticación
# ⚠️ Solo para testing y desarrollo, DEBEN SER ELIMINADOS antes de producción

@cliente_nora_bp.route("/test/bloques/<nombre_nora>", methods=["GET"])
def test_bloques_sin_auth(nombre_nora):
    """⚠️ TEMPORAL: Endpoint para testing sin autenticación - ELIMINAR EN PRODUCCIÓN"""
    try:
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        # Retornar HTML simple para verificar
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Bloques - {nombre_nora}</title>
        </head>
        <body>
            <h1>🧪 Test Bloques de Conocimiento - {nombre_nora}</h1>
            <p><strong>Total bloques:</strong> {len(res.data)}</p>
            <div id="bloques">
                {''.join([f'<div style="border:1px solid #ccc; margin:10px; padding:10px;"><strong>ID:</strong> {b["id"]}<br><strong>Contenido:</strong> {b["contenido"]}<br><strong>Etiquetas:</strong> {b.get("etiquetas", [])}</div>' for b in res.data])}
            </div>
            
            <h2>🔧 Test AJAX</h2>
            <button onclick="cargarBloques()">Cargar Bloques vía AJAX</button>
            <div id="resultado"></div>
            
            <script>
            async function cargarBloques() {{
                try {{
                    const response = await fetch('/panel_cliente/{nombre_nora}/entrenar/bloques');
                    const data = await response.json();
                    document.getElementById('resultado').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }} catch (error) {{
                    document.getElementById('resultado').innerHTML = 
                        '<p style="color:red;">Error: ' + error.message + '</p>';
                }}
            }}
            </script>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"


# ========================================
# 🧪 ENDPOINT PRINCIPAL SIN AUTENTICACIÓN - ⚠️ ELIMINAR EN PRODUCCIÓN
# ========================================

@cliente_nora_bp.route("/entrenar/<nombre_nora>", methods=["GET"])
def panel_entrenamiento_sin_auth(nombre_nora):
    """⚠️ TEMPORAL: Versión sin autenticación para testing - ELIMINAR EN PRODUCCIÓN"""
    try:
        config_res = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        if not config_res.data:
            # Crear configuración por defecto si no existe
            config = {
                "nombre_nora": nombre_nora,
                "personalidad": "Amigable y profesional",
                "instrucciones": "Soy un asistente de IA",
                "ia_activa": True,
                "modo_respuesta": "flexible",
                "mensaje_fuera_tema": "Lo siento, no puedo ayudarte con eso",
                "bienvenida": f"¡Hola! Soy {nombre_nora.capitalize()}, ¿en qué puedo ayudarte?"
            }
        else:
            config = config_res.data
            
        return render_template("admin_nora_entrenar.html", nombre_nora=nombre_nora, config=config)

    except Exception as e:
        print(f"❌ Error al cargar entrenamiento: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p><p><a href='/test/bloques/{nombre_nora}'>Ir a test de bloques</a></p>"


# ========================================
# 🔧 BYPASS DE AUTENTICACIÓN - ⚠️ SOLO PARA DESARROLLO - ELIMINAR EN PRODUCCIÓN
# ========================================

@cliente_nora_bp.route("/dev/entrenar/<nombre_nora>", methods=["GET"])
def panel_entrenamiento_dev(nombre_nora):
    """⚠️ TEMPORAL: Versión para desarrollo con sesión simulada - ELIMINAR EN PRODUCCIÓN"""
    try:
        # Simular sesión de desarrollo
        session['email'] = 'dev@test.com'
        session['is_admin'] = False
        session['nombre_nora'] = nombre_nora
        session['user'] = {'email': 'dev@test.com', 'name': 'Dev User'}
        
        config_res = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        if not config_res.data:
            # Crear configuración por defecto si no existe
            config = {
                "nombre_nora": nombre_nora,
                "personalidad": "Amigable y profesional",
                "instrucciones": "Soy un asistente de IA",
                "ia_activa": True,
                "modo_respuesta": "flexible",
                "mensaje_fuera_tema": "Lo siento, no puedo ayudarte con eso",
                "bienvenida": f"¡Hola! Soy {nombre_nora.capitalize()}, ¿en qué puedo ayudarte?"
            }
        else:
            config = config_res.data
            
        return render_template("admin_nora_entrenar.html", nombre_nora=nombre_nora, config=config)

    except Exception as e:
        print(f"❌ Error al cargar entrenamiento: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p><p><a href='/test/bloques/{nombre_nora}'>Ir a test de bloques</a></p>"

# ========================================
# 🔍 ENDPOINT DE DEBUG - para diagnosticar problemas de sesión
# ========================================

@cliente_nora_bp.route("/debug/session", methods=["GET"])
def debug_session():
    """Debug de sesión"""
    return jsonify({
        "session_keys": list(session.keys()),
        "email": session.get("email"),
        "nombre_nora": session.get("nombre_nora"),
        "user": session.get("user"),
        "is_admin": session.get("is_admin"),
        "name": session.get("name"),
        "all_session_data": dict(session)
    })

# ========================================
# 🔍 ENDPOINT DE DEBUG - test directo de bloques sin autenticación
@cliente_nora_bp.route("/test/conocimiento-debug", methods=["GET"])
def test_conocimiento_debug():
    """Test completo de la funcionalidad de conocimiento con UI"""
    try:
        with open('test_conocimiento_debug.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error</h1><p>No se pudo cargar test_conocimiento_debug.html: {str(e)}</p>"

# 🔍 ENDPOINT DE DEBUG - test directo de bloques sin autenticación
# ========================================

@cliente_nora_bp.route("/debug/bloques/<nombre_nora>", methods=["GET"])
def debug_bloques_directo(nombre_nora):
    """Test directo de bloques sin decorador de auth"""
    try:
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        return jsonify({
            "success": True, 
            "data": res.data,
            "count": len(res.data),
            "debug_info": "Acceso directo sin autenticación"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 🔍 ENDPOINT DE DEBUG COMPLETO - para diagnosticar problemas de frontend
@cliente_nora_bp.route("/debug/request", methods=["GET"])
def debug_request():
    """Debug completo de request y sesión"""
    from flask import request
    return jsonify({
        "session_data": dict(session),
        "cookies": dict(request.cookies),
        "headers": dict(request.headers),
        "user_agent": request.headers.get('User-Agent'),
        "method": request.method,
        "url": request.url,
        "referrer": request.referrer,
        "session_id": session.get('_id'),
        "login_status": {
            "has_email": bool(session.get("email")),
            "has_nombre_nora": bool(session.get("nombre_nora")),
            "email": session.get("email"),
            "nombre_nora": session.get("nombre_nora")
        }
    })

# 🔍 ENDPOINT DE DEBUG - verificar configuración de cookies
@cliente_nora_bp.route("/debug/config", methods=["GET"])
def debug_config():
    """Debug de configuración de cookies y sesión"""
    from flask import current_app
    return jsonify({
        "cookie_config": {
            "SESSION_COOKIE_NAME": current_app.config.get('SESSION_COOKIE_NAME'),
            "SESSION_COOKIE_HTTPONLY": current_app.config.get('SESSION_COOKIE_HTTPONLY'),
            "SESSION_COOKIE_SECURE": current_app.config.get('SESSION_COOKIE_SECURE'),
            "SESSION_COOKIE_SAMESITE": current_app.config.get('SESSION_COOKIE_SAMESITE'),
            "SESSION_PERMANENT": current_app.config.get('SESSION_PERMANENT'),
            "PERMANENT_SESSION_LIFETIME": str(current_app.config.get('PERMANENT_SESSION_LIFETIME')),
            "SESSION_TYPE": current_app.config.get('SESSION_TYPE'),
            "SECRET_KEY_EXISTS": bool(current_app.config.get('SECRET_KEY'))
        },
        "session_info": {
            "session_keys": list(session.keys()),
            "has_email": bool(session.get("email")),
            "has_nombre_nora": bool(session.get("nombre_nora")),
            "session_permanent": session.permanent
        }
    })

# 🧪 RUTA PARA SERVIR EL ARCHIVO DE DEBUG HTML
@cliente_nora_bp.route("/test_frontend_debug.html", methods=["GET"])
def serve_debug_html():
    """Servir archivo de debug HTML"""
    import os
    debug_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_frontend_debug.html")
    if os.path.exists(debug_file):
        with open(debug_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    else:
        return "Archivo de debug no encontrado", 404

# ========================================
# 🔧 ENDPOINT DE PRUEBA PARA VERIFICAR JAVASCRIPT
# ========================================

@cliente_nora_bp.route("/test_js/<nombre_nora>", methods=["GET"])
def test_javascript(nombre_nora):
    """Endpoint para probar el funcionamiento de JavaScript"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test JS - {nombre_nora}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold mb-6">🧪 Test JavaScript - {nombre_nora}</h1>
            
            <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Pruebas de Funciones</h2>
                
                <div class="space-y-4">
                    <button onclick="testScrollToSection()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test scrollToSection()
                    </button>
                    
                    <button onclick="testToggleExamples()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Test toggleExamples()
                    </button>
                    
                    <button onclick="testPanelConfig()" class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                        Test PANEL_CONFIG
                    </button>
                    
                    <button onclick="testCargarConocimiento()" class="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">
                        Test cargarConocimiento()
                    </button>
                </div>
            </div>
            
            <div id="test-section" class="bg-yellow-100 p-4 rounded-lg mb-6">
                <h3 class="font-semibold">Sección de Prueba</h3>
                <p>Esta sección se usa para probar el scroll.</p>
            </div>
            
            <div id="examples-container" class="hidden bg-green-100 p-4 rounded-lg mb-6">
                <h3 class="font-semibold">Ejemplos Container</h3>
                <p>Este container se muestra/oculta con toggleExamples().</p>
            </div>
            
            <div id="output" class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">Output de Pruebas:</h3>
                <pre id="output-content" class="text-sm"></pre>
            </div>
        </div>
        
        <!-- Cargar JavaScript modules -->
        <script src="/clientes/aura/static/js/panel-entrenamiento-core.js"></script>
        <script src="/clientes/aura/static/js/ui-utils.js"></script>
        <script src="/clientes/aura/static/js/conocimiento-manager.js"></script>
        <script src="/clientes/aura/static/js/form-handlers.js"></script>
        
        <script>
        // Configurar variables desde template
        if (typeof PANEL_CONFIG !== 'undefined') {{
            PANEL_CONFIG.nombreNora = '{nombre_nora}';
            PANEL_CONFIG.endpoints = {{
                bloques: '/panel_cliente/{nombre_nora}/entrenar/bloques',
                personalidad: '/panel_cliente/{nombre_nora}/entrenar/personalidad',
                instrucciones: '/panel_cliente/{nombre_nora}/entrenar/instrucciones',
                estadoIA: '/panel_cliente/{nombre_nora}/entrenar/estado_ia',
                limites: '/panel_cliente/{nombre_nora}/entrenar/limites',
                bienvenida: '/panel_cliente/{nombre_nora}/entrenar/bienvenida'
            }};
        }}
        
        function log(message) {{
            const output = document.getElementById('output-content');
            output.textContent += new Date().toLocaleTimeString() + ': ' + message + '\\n';
        }}
        
        function testScrollToSection() {{
            log('Probando scrollToSection...');
            if (typeof scrollToSection === 'function') {{
                scrollToSection('test-section');
                log('✅ scrollToSection ejecutada');
            }} else {{
                log('❌ scrollToSection no está definida');
            }}
        }}
        
        function testToggleExamples() {{
            log('Probando toggleExamples...');
            if (typeof toggleExamples === 'function') {{
                toggleExamples();
                log('✅ toggleExamples ejecutada');
            }} else {{
                log('❌ toggleExamples no está definida');
            }}
        }}
        
        function testPanelConfig() {{
            log('Probando PANEL_CONFIG...');
            if (typeof PANEL_CONFIG !== 'undefined') {{
                log('✅ PANEL_CONFIG definido: ' + JSON.stringify(PANEL_CONFIG, null, 2));
            }} else {{
                log('❌ PANEL_CONFIG no está definido');
            }}
        }}
        
        function testCargarConocimiento() {{
            log('Probando cargarConocimiento...');
            if (typeof cargarConocimiento === 'function') {{
                cargarConocimiento();
                log('✅ cargarConocimiento ejecutada');
            }} else {{
                log('❌ cargarConocimiento no está definida');
            }}
        }}
        
        // Log inicial
        log('🚀 Página de prueba cargada');
        log('Verificando funciones disponibles...');
        
        window.addEventListener('load', function() {{
            log('📋 Funciones disponibles:');
            log('scrollToSection: ' + (typeof scrollToSection));
            log('toggleExamples: ' + (typeof toggleExamples));
            log('PANEL_CONFIG: ' + (typeof PANEL_CONFIG));
            log('cargarConocimiento: ' + (typeof cargarConocimiento));
        }});
        </script>
    </body>
    </html>
    '''

# Ruta estática para servir archivos JavaScript y CSS del cliente
@cliente_nora_bp.route('/clientes/aura/static/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos del cliente"""
    import os
    from flask import send_from_directory
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_folder, filename)

# ========================================
# 🔧 RUTA ALTERNATIVA PARA ARCHIVOS ESTÁTICOS
# ========================================

@cliente_nora_bp.route('/static/js/<filename>')
def serve_js_file(filename):
    """Servir archivos JavaScript con ruta alternativa"""
    import os
    from flask import send_from_directory, current_app
    
    # Ruta absoluta al directorio de archivos estáticos
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')
    static_folder = os.path.abspath(static_folder)
    
    print(f"🔍 Intentando servir: {filename}")
    print(f"📂 Desde carpeta: {static_folder}")
    
    try:
        return send_from_directory(static_folder, filename)
    except Exception as e:
        print(f"❌ Error sirviendo {filename}: {e}")
        return f"Error: {e}", 404

# ========================================
# 🔧 RUTAS DE DEBUG PARA VERIFICAR ARCHIVOS JS
# ========================================

@cliente_nora_bp.route("/debug/js/<filename>", methods=["GET"])
def debug_js_file(filename):
    """Debug para verificar archivos JavaScript"""
    import os
    from flask import send_from_directory, jsonify
    
    js_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')
    file_path = os.path.join(js_folder, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si contiene funciones
        functions = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'function ' in line and not line.strip().startswith('//'):
                functions.append(f"Línea {i+1}: {line.strip()}")
        
        return jsonify({
            "exists": True,
            "size": len(content),
            "functions": functions[:10],  # Primeras 10 funciones
            "total_functions": len(functions),
            "first_100_chars": content[:100]
        })
    else:
        return jsonify({
            "exists": False,
            "path_checked": file_path,
            "js_folder": js_folder
        })


# ========================================
# 🔧 ENDPOINT DE DIAGNÓSTICO COMPLETO
# ========================================

@cliente_nora_bp.route("/diagnostico/<nombre_nora>", methods=["GET"])
def diagnostico_completo(nombre_nora):
    """Página de diagnóstico completa para verificar el panel"""
    import os
    
    # Verificar archivos JavaScript
    js_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'js')
    archivos_js = [
        'panel-entrenamiento-core.js',
        'ui-utils.js',
        'conocimiento-manager.js',
        'form-handlers.js'
    ]
    
    archivos_estado = {}
    for archivo in archivos_js:
        path = os.path.join(js_folder, archivo)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            archivos_estado[archivo] = {
                'existe': True,
                'tamaño': len(contenido),
                'funciones': contenido.count('function '),
                'primeras_100': contenido[:100].replace('\n', '\\n')
            }
        else:
            archivos_estado[archivo] = {'existe': False}
    
    # Generar HTML de estado de archivos
    archivos_html = ""
    for archivo, info in archivos_estado.items():
        if info.get('existe'):
            estado_icon = "✅"
            estado_color = "text-green-600"
            detalles = f"({info.get('tamaño', 0)} chars, {info.get('funciones', 0)} functions)"
        else:
            estado_icon = "❌"
            estado_color = "text-red-600"
            detalles = ""
        
        archivos_html += f'''
        <div class="flex items-center space-x-2">
            <span class="{estado_color}">{estado_icon}</span>
            <span class="font-mono">{archivo}</span>
            <span class="text-gray-500">{detalles}</span>
        </div>
        '''
    
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔍 Diagnóstico Panel - {nombre_nora}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl font-bold mb-6">🔍 Diagnóstico Panel - {nombre_nora}</h1>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-xl font-semibold mb-4">📁 Estado de Archivos</h2>
                    <div class="space-y-2 text-sm">
                        {archivos_html}
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-xl font-semibold mb-4">🧪 Pruebas de Función</h2>
                    <div class="space-y-2">
                        <button onclick="testCargarConocimiento()" class="w-full bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                            🎯 Test cargarConocimiento()
                        </button>
                        <button onclick="testScrollToSection()" class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Test scrollToSection()
                        </button>
                        <button onclick="testToggleExamples()" class="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                            Test toggleExamples()
                        </button>
                        <button onclick="testAllFunctions()" class="w-full bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                            Test Todas las Funciones
                        </button>
                        <button onclick="reloadScripts()" class="w-full bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">
                            Recargar Scripts
                        </button>
                    </div>
                </div>
            </div>
            
            <div id="test-section" class="bg-yellow-100 p-4 rounded-lg mb-6">
                <h3 class="font-semibold">🎯 Sección de Prueba</h3>
                <p>Esta sección es para probar scrollToSection().</p>
            </div>
            
            <div id="examples-container" class="hidden bg-green-100 p-4 rounded-lg mb-6">
                <h3 class="font-semibold">📝 Contenedor de Ejemplos</h3>
                <p>Este contenedor se muestra/oculta con toggleExamples().</p>
            </div>
            
            <div class="bg-black text-green-400 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">📊 Log de Diagnóstico:</h3>
                <pre id="diagnostic-log" class="text-xs max-h-96 overflow-auto"></pre>
            </div>
        </div>
        
        <!-- Cargar scripts con logging detallado -->
        <script>
        function log(message, type = 'info') {{
            const logElement = document.getElementById('diagnostic-log');
            const timestamp = new Date().toLocaleTimeString();
            const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '📝';
            logElement.textContent += `${{timestamp}} ${{icon}} ${{message}}\\n`;
            logElement.scrollTop = logElement.scrollHeight;
            console.log(`${{icon}} ${{message}}`);
        }}
        
        log('🚀 Iniciando diagnóstico...');
        log('📂 Archivos JavaScript a cargar: panel-entrenamiento-core.js, ui-utils.js, conocimiento-manager.js, form-handlers.js');
        
        // Definir PANEL_CONFIG antes de cargar los archivos
        window.PANEL_CONFIG = {{
            nombreNora: '{nombre_nora}',
            endpoints: {{
                bloques: '/panel_cliente/{nombre_nora}/entrenar/bloques',
                personalidad: '/panel_cliente/{nombre_nora}/entrenar/personalidad',
                instrucciones: '/panel_cliente/{nombre_nora}/entrenar/instrucciones',
                estadoIA: '/panel_cliente/{nombre_nora}/entrenar/estado_ia',
                limites: '/panel_cliente/{nombre_nora}/entrenar/limites',
                bienvenida: '/panel_cliente/{nombre_nora}/entrenar/bienvenida'
            }},
            limits: {{
                maxContentLength: 500,
                maxTags: 10
            }}
        }};
        log('✅ PANEL_CONFIG definido', 'success');
        </script>
        
        <script src="/static/js/panel-entrenamiento-core.js" 
                onload="log('✅ panel-entrenamiento-core.js cargado', 'success')"
                onerror="log('❌ Error cargando panel-entrenamiento-core.js', 'error')"></script>
        <script src="/static/js/ui-utils.js" 
                onload="log('✅ ui-utils.js cargado', 'success')"
                onerror="log('❌ Error cargando ui-utils.js', 'error')"></script>
        <script src="/static/js/conocimiento-manager.js" 
                onload="log('✅ conocimiento-manager.js cargado', 'success')"
                onerror="log('❌ Error cargando conocimiento-manager.js', 'error')"></script>
        <script src="/static/js/form-handlers.js" 
                onload="log('✅ form-handlers.js cargado', 'success')"
                onerror="log('❌ Error cargando form-handlers.js', 'error')"></script>
        
        <script>
        // Verificar después de cargar scripts
        setTimeout(() => {{
            log('🔍 Verificando funciones después de cargar scripts...');
            
            // Verificar PANEL_CONFIG
            if (typeof window.PANEL_CONFIG !== 'undefined') {{
                log('✅ PANEL_CONFIG disponible', 'success');
            }} else {{
                log('❌ PANEL_CONFIG no disponible', 'error');
            }}
            
            // Verificar funciones específicamente
            const funciones = [
                'scrollToSection', 
                'toggleExamples', 
                'initializeTabs', 
                'initializeFormHandlers',
                'cargarConocimiento',
                'agregarBloque',
                'eliminarBloque',
                'mostrarToast'
            ];
            
            funciones.forEach(fn => {{
                const disponible = typeof window[fn] === 'function';
                log(`${{disponible ? '✅' : '❌'}} ${{fn}}: ${{typeof window[fn]}}`, disponible ? 'success' : 'error');
            }});
            
            // Debug específico para cargarConocimiento
            if (typeof window.cargarConocimiento === 'undefined') {{
                log('🔍 Buscando cargarConocimiento en window...', 'warning');
                const funcionesCargar = Object.keys(window).filter(key => key.includes('cargar'));
                log(`🔍 Funciones que contienen 'cargar': ${{funcionesCargar.join(', ')}}`, 'warning');
            }}
            
        }}, 1500);
        
        function testCargarConocimiento() {{
            log('🎯 Probando cargarConocimiento específicamente...');
            if (typeof window.cargarConocimiento === 'function') {{
                log('✅ cargarConocimiento encontrada, ejecutando...', 'success');
                try {{
                    window.cargarConocimiento();
                    log('✅ cargarConocimiento ejecutada sin errores', 'success');
                }} catch (error) {{
                    log(`❌ Error ejecutando cargarConocimiento: ${{error.message}}`, 'error');
                }}
            }} else {{
                log('❌ cargarConocimiento no está disponible', 'error');
                log(`🔍 Tipo: ${{typeof window.cargarConocimiento}}`, 'warning');
                log(`🔍 En window: ${{window.hasOwnProperty('cargarConocimiento')}}`, 'warning');
                
                // Buscar todas las funciones que contengan 'cargar'
                const funcionesCargar = Object.keys(window).filter(key => 
                    typeof window[key] === 'function' && key.toLowerCase().includes('cargar')
                );
                log(`🔍 Funciones con 'cargar': ${{funcionesCargar.join(', ')}}`, 'warning');
                
                // Buscar todas las funciones del conocimiento-manager
                const funcionesConocimiento = Object.keys(window).filter(key => 
                    typeof window[key] === 'function' && 
                    (key.includes('conocimiento') || key.includes('Conocimiento') || key.includes('bloque') || key.includes('Bloque'))
                );
                log(`🔍 Funciones de conocimiento: ${{funcionesConocimiento.join(', ')}}`, 'warning');
            }}
        }}
        
        function testScrollToSection() {{
            log('🧪 Probando scrollToSection...');
            if (typeof scrollToSection === 'function') {{
                scrollToSection('test-section');
                log('✅ scrollToSection ejecutada correctamente', 'success');
            }} else {{
                log('❌ scrollToSection no está disponible', 'error');
            }}
        }}
        
        function testToggleExamples() {{
            log('🧪 Probando toggleExamples...');
            if (typeof toggleExamples === 'function') {{
                toggleExamples();
                log('✅ toggleExamples ejecutada correctamente', 'success');
            }} else {{
                log('❌ toggleExamples no está disponible', 'error');
            }}
        }}
        
        function testAllFunctions() {{
            log('=== PRUEBA COMPLETA DE FUNCIONES ===');
            const funciones = ['scrollToSection', 'toggleExamples', 'initializeTabs', 'initializeFormHandlers', 'cargarConocimiento'];
            funciones.forEach(fn => {{
                const disponible = typeof window[fn] === 'function';
                log(`${{fn}}: ${{disponible ? 'DISPONIBLE' : 'NO DISPONIBLE'}}`, disponible ? 'success' : 'error');
            }});
            log('=== PRUEBA COMPLETADA ===');
        }}
        
        function reloadScripts() {{
            log('🔄 Recargando página para recargar scripts...');
            window.location.reload();
        }}
        </script>
    </body>
    </html>
    '''
    
    return html_template

# Ruta de diagnóstico simple
@cliente_nora_bp.route('/diagnostico-simple')
def diagnostico_simple():
    """Página de diagnóstico simple para JS"""
    return send_from_directory('.', 'diagnostico_simple.html')


# Temporary endpoint removed - authentication is now working properly
# The proper authenticated endpoint is: /panel_cliente/<nombre_nora>/entrenar/bloques
