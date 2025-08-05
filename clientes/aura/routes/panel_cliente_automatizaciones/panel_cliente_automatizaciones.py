from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import json
import sys
import os
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.automatizaciones_ejecutor import ejecutor

# Importar el descubridor de funciones
sys.path.append('.')
try:
    from descubrir_funciones import DescubrirFunciones
except ImportError:
    print("⚠️ No se pudo importar DescubrirFunciones")
    DescubrirFunciones = None

panel_cliente_automatizaciones_bp = Blueprint("panel_cliente_automatizaciones_bp", __name__)

@panel_cliente_automatizaciones_bp.route("/")
def panel_cliente_automatizaciones():
    """Página principal de automatizaciones"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener todas las automatizaciones
        response = supabase.table("automatizaciones") \
            .select("*") \
            .order("creado_en", desc=True) \
            .execute()
        
        automatizaciones = response.data if response.data else []
        
        # Formatear las fechas para mostrar
        for auto in automatizaciones:
            if auto.get('ultima_ejecucion'):
                auto['ultima_ejecucion_formatted'] = datetime.fromisoformat(
                    auto['ultima_ejecucion'].replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M:%S')
            if auto.get('proxima_ejecucion'):
                auto['proxima_ejecucion_formatted'] = datetime.fromisoformat(
                    auto['proxima_ejecucion'].replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M:%S')
            
            # Formatear parámetros JSON para mostrar
            if auto.get('parametros_json'):
                try:
                    auto['parametros_formatted'] = json.dumps(auto['parametros_json'], indent=2)
                except:
                    auto['parametros_formatted'] = str(auto['parametros_json'])
        
        return render_template(
            "panel_cliente_automatizaciones/index.html", 
            nombre_nora=nombre_nora,
            automatizaciones=automatizaciones
        )
        
    except Exception as e:
        print(f"❌ Error al cargar automatizaciones: {e}")
        flash(f"Error al cargar automatizaciones: {e}", "error")
        return render_template(
            "panel_cliente_automatizaciones/index.html", 
            nombre_nora=nombre_nora,
            automatizaciones=[]
        )

@panel_cliente_automatizaciones_bp.route("/crear", methods=["GET", "POST"])
def crear_automatizacion():
    """Crear nueva automatización"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    if request.method == "GET":
        # Cargar funciones disponibles desde la base de datos
        try:
            response_funciones = supabase.table("funciones_automatizables") \
                .select("*") \
                .eq("activa", True) \
                .eq("es_automatizable", True) \
                .order("modulo, nombre_funcion") \
                .execute()
            
            funciones_disponibles = response_funciones.data if response_funciones.data else []
            
            # Agrupar funciones por módulo para mejor organización
            funciones_por_modulo = {}
            for func in funciones_disponibles:
                modulo = func['modulo']
                if modulo not in funciones_por_modulo:
                    funciones_por_modulo[modulo] = []
                funciones_por_modulo[modulo].append(func)
            
            print(f"🔧 Cargadas {len(funciones_disponibles)} funciones para el formulario")
            
        except Exception as e:
            print(f"⚠️ Error cargando funciones: {e}")
            funciones_disponibles = []
            funciones_por_modulo = {}
        
        return render_template(
            "panel_cliente_automatizaciones/crear.html", 
            nombre_nora=nombre_nora,
            funciones_disponibles=funciones_disponibles,
            funciones_por_modulo=funciones_por_modulo
        )
    
    try:
        # Obtener datos del formulario
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        frecuencia = request.form.get("frecuencia", "").strip()
        hora_ejecucion = request.form.get("hora_ejecucion", "").strip()
        modulo_relacionado = request.form.get("modulo_relacionado", "").strip()
        funcion_objetivo = request.form.get("funcion_objetivo", "").strip()
        parametros_raw = request.form.get("parametros_json", "").strip()
        
        # Agregar logging para debugging
        print(f"🔧 DEBUGGING - Datos del formulario:")
        print(f"   - nombre: '{nombre}'")
        print(f"   - modulo_relacionado: '{modulo_relacionado}'")
        print(f"   - funcion_objetivo: '{funcion_objetivo}'")
        
        # Validaciones básicas
        if not nombre:
            flash("El nombre es obligatorio", "error")
            return redirect(request.url)
        
        if not frecuencia:
            flash("La frecuencia es obligatoria", "error")
            return redirect(request.url)
        
        if not hora_ejecucion:
            flash("La hora de ejecución es obligatoria", "error")
            return redirect(request.url)
        
        if not modulo_relacionado:
            flash("El módulo es obligatorio", "error")
            return redirect(request.url)
        
        if not funcion_objetivo:
            flash("La función objetivo es obligatoria", "error")
            return redirect(request.url)
        
        # Procesar parámetros JSON
        parametros_json = {}
        if parametros_raw:
            try:
                parametros_json = json.loads(parametros_raw)
            except json.JSONDecodeError as e:
                flash(f"Error en el formato JSON de parámetros: {e}", "error")
                return redirect(request.url)
        
        # Calcular próxima ejecución
        proxima_ejecucion = calcular_proxima_ejecucion(frecuencia, hora_ejecucion)
        
        # Crear automatización en la base de datos
        nueva_automatizacion = {
            "nombre": nombre,
            "descripcion": descripcion,
            "frecuencia": frecuencia,
            "hora_ejecucion": hora_ejecucion,
            "modulo_relacionado": modulo_relacionado,
            "funcion_objetivo": funcion_objetivo,
            "parametros_json": parametros_json,
            "proxima_ejecucion": proxima_ejecucion.isoformat(),
            "activo": True
        }
        
        response = supabase.table("automatizaciones").insert(nueva_automatizacion).execute()
        
        if response.data:
            flash("Automatización creada exitosamente", "success")
            return redirect(url_for(
                "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
                nombre_nora=nombre_nora
            ))
        else:
            flash("Error al crear la automatización", "error")
            return redirect(request.url)
            
    except Exception as e:
        print(f"❌ Error al crear automatización: {e}")
        flash(f"Error al crear automatización: {e}", "error")
        return redirect(request.url)

@panel_cliente_automatizaciones_bp.route("/editar/<automatizacion_id>", methods=["GET", "POST"])
def editar_automatizacion(automatizacion_id):
    """Editar automatización existente"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener la automatización actual
        response = supabase.table("automatizaciones") \
            .select("*") \
            .eq("id", automatizacion_id) \
            .execute()
        
        if not response.data:
            flash("Automatización no encontrada", "error")
            return redirect(url_for(
                "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
                nombre_nora=nombre_nora
            ))
        
        automatizacion = response.data[0]
        
        if request.method == "GET":
            # Formatear parámetros JSON para el formulario
            if automatizacion.get('parametros_json'):
                automatizacion['parametros_formatted'] = json.dumps(
                    automatizacion['parametros_json'], indent=2
                )
            
            return render_template(
                "panel_cliente_automatizaciones/editar.html", 
                nombre_nora=nombre_nora,
                automatizacion=automatizacion
            )
        
        # POST - Actualizar automatización
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        frecuencia = request.form.get("frecuencia", "").strip()
        hora_ejecucion = request.form.get("hora_ejecucion", "").strip()
        modulo_relacionado = request.form.get("modulo_relacionado", "").strip()
        funcion_objetivo = request.form.get("funcion_objetivo", "").strip()
        parametros_raw = request.form.get("parametros_json", "").strip()
        activo = request.form.get("activo") == "on"
        
        # Validaciones básicas
        if not nombre:
            flash("El nombre es obligatorio", "error")
            return redirect(request.url)
        
        if not frecuencia:
            flash("La frecuencia es obligatoria", "error")
            return redirect(request.url)
        
        if not hora_ejecucion:
            flash("La hora de ejecución es obligatoria", "error")
            return redirect(request.url)
        
        # Procesar parámetros JSON
        parametros_json = {}
        if parametros_raw:
            try:
                parametros_json = json.loads(parametros_raw)
            except json.JSONDecodeError as e:
                flash(f"Error en el formato JSON de parámetros: {e}", "error")
                return redirect(request.url)
        
        # Recalcular próxima ejecución si cambió la frecuencia o hora
        proxima_ejecucion = None
        if (frecuencia != automatizacion['frecuencia'] or 
            hora_ejecucion != automatizacion['hora_ejecucion']):
            proxima_ejecucion = calcular_proxima_ejecucion(frecuencia, hora_ejecucion)
        
        # Actualizar automatización
        datos_actualizacion = {
            "nombre": nombre,
            "descripcion": descripcion,
            "frecuencia": frecuencia,
            "hora_ejecucion": hora_ejecucion,
            "modulo_relacionado": modulo_relacionado,
            "funcion_objetivo": funcion_objetivo,
            "parametros_json": parametros_json,
            "activo": activo,
            "actualizado_en": datetime.now().isoformat()
        }
        
        if proxima_ejecucion:
            datos_actualizacion["proxima_ejecucion"] = proxima_ejecucion.isoformat()
        
        response = supabase.table("automatizaciones") \
            .update(datos_actualizacion) \
            .eq("id", automatizacion_id) \
            .execute()
        
        if response.data:
            flash("Automatización actualizada exitosamente", "success")
            return redirect(url_for(
                "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
                nombre_nora=nombre_nora
            ))
        else:
            flash("Error al actualizar la automatización", "error")
            return redirect(request.url)
            
    except Exception as e:
        print(f"❌ Error al editar automatización: {e}")
        flash(f"Error al editar automatización: {e}", "error")
        return redirect(url_for(
            "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
            nombre_nora=nombre_nora
        ))

@panel_cliente_automatizaciones_bp.route("/eliminar/<automatizacion_id>", methods=["POST"])
def eliminar_automatizacion(automatizacion_id):
    """Eliminar automatización"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        response = supabase.table("automatizaciones") \
            .delete() \
            .eq("id", automatizacion_id) \
            .execute()
        
        if response.data:
            flash("Automatización eliminada exitosamente", "success")
        else:
            flash("Error al eliminar la automatización", "error")
            
    except Exception as e:
        print(f"❌ Error al eliminar automatización: {e}")
        flash(f"Error al eliminar automatización: {e}", "error")
    
    return redirect(url_for(
        "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
        nombre_nora=nombre_nora
    ))

@panel_cliente_automatizaciones_bp.route("/toggle/<automatizacion_id>", methods=["POST"])
def toggle_automatizacion(automatizacion_id):
    """Activar/desactivar automatización"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Obtener estado actual
        response = supabase.table("automatizaciones") \
            .select("activo") \
            .eq("id", automatizacion_id) \
            .execute()
        
        if not response.data:
            flash("Automatización no encontrada", "error")
        else:
            nuevo_estado = not response.data[0]['activo']
            
            # Actualizar estado
            update_response = supabase.table("automatizaciones") \
                .update({
                    "activo": nuevo_estado,
                    "actualizado_en": datetime.now().isoformat()
                }) \
                .eq("id", automatizacion_id) \
                .execute()
            
            if update_response.data:
                estado_texto = "activada" if nuevo_estado else "desactivada"
                flash(f"Automatización {estado_texto} exitosamente", "success")
            else:
                flash("Error al cambiar el estado de la automatización", "error")
                
    except Exception as e:
        print(f"❌ Error al cambiar estado de automatización: {e}")
        flash(f"Error al cambiar estado: {e}", "error")
    
    return redirect(url_for(
        "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
        nombre_nora=nombre_nora
    ))

@panel_cliente_automatizaciones_bp.route("/ejecutar/<automatizacion_id>", methods=["POST"])
def ejecutar_automatizacion_manual(automatizacion_id):
    """Ejecutar automatización manualmente"""
    nombre_nora = request.path.split('/')[2] if len(request.path.split('/')) > 2 else None
    
    try:
        # Usar el ejecutor de automatizaciones
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        
        resultado = ejecutor.ejecutar_por_id(automatizacion_id)
        
        if resultado['success']:
            flash(f"Automatización ejecutada exitosamente: {resultado.get('resultado', 'Completada')}", "success")
        else:
            flash(f"Error al ejecutar automatización: {resultado.get('error', 'Error desconocido')}", "error")
                
    except Exception as e:
        print(f"❌ Error al ejecutar automatización: {e}")
        flash(f"Error al ejecutar automatización: {e}", "error")
    
    return redirect(url_for(
        "panel_cliente_automatizaciones_bp.panel_cliente_automatizaciones",
        nombre_nora=nombre_nora
    ))

@panel_cliente_automatizaciones_bp.route("/api/automatizaciones", methods=["GET"])
def api_listar_automatizaciones():
    """API para obtener lista de automatizaciones"""
    try:
        response = supabase.table("automatizaciones") \
            .select("*") \
            .order("creado_en", desc=True) \
            .execute()
        
        return jsonify({
            "success": True,
            "data": response.data if response.data else []
        })
        
    except Exception as e:
        print(f"❌ Error en API automatizaciones: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_automatizaciones_bp.route("/api/ejecutar-pendientes", methods=["POST"])
def api_ejecutar_pendientes():
    """API para ejecutar todas las automatizaciones pendientes"""
    try:
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        
        resultado = ejecutor.ejecutar_automatizaciones_pendientes()
        
        return jsonify({
            "success": resultado['success'],
            "ejecutadas": resultado['ejecutadas'],
            "fallidas": resultado['fallidas'],
            "resultados": resultado['resultados']
        })
        
    except Exception as e:
        print(f"❌ Error en API ejecutar pendientes: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_automatizaciones_bp.route("/api/ejecutar/<automatizacion_id>", methods=["POST"])
def api_ejecutar_automatizacion(automatizacion_id):
    """API para ejecutar una automatización específica"""
    try:
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        
        resultado = ejecutor.ejecutar_por_id(automatizacion_id)
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ Error en API ejecutar automatización: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def calcular_proxima_ejecucion(frecuencia, hora_ejecucion):
    """
    Calcular la próxima fecha/hora de ejecución basada en frecuencia y hora
    """
    try:
        # Parsear hora de ejecución (formato HH:MM)
        hora_parts = hora_ejecucion.split(":")
        hora = int(hora_parts[0])
        minuto = int(hora_parts[1]) if len(hora_parts) > 1 else 0
        
        ahora = datetime.now()
        proxima = None
        
        if frecuencia == "diaria":
            # Próxima ejecución: mañana a la hora especificada
            proxima = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            if proxima <= ahora:
                proxima += timedelta(days=1)
                
        elif frecuencia == "semanal":
            # Próxima ejecución: próximo lunes a la hora especificada
            dias_hasta_lunes = (7 - ahora.weekday()) % 7
            if dias_hasta_lunes == 0:  # Es lunes
                proxima = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                if proxima <= ahora:
                    dias_hasta_lunes = 7
            
            if dias_hasta_lunes > 0:
                proxima = (ahora + timedelta(days=dias_hasta_lunes)).replace(
                    hour=hora, minute=minuto, second=0, microsecond=0
                )
                
        elif frecuencia == "mensual":
            # Próxima ejecución: día 1 del próximo mes
            if ahora.month == 12:
                proxima = ahora.replace(year=ahora.year+1, month=1, day=1, 
                                      hour=hora, minute=minuto, second=0, microsecond=0)
            else:
                proxima = ahora.replace(month=ahora.month+1, day=1,
                                      hour=hora, minute=minuto, second=0, microsecond=0)
        
        else:
            # Por defecto, ejecutar mañana
            proxima = (ahora + timedelta(days=1)).replace(
                hour=hora, minute=minuto, second=0, microsecond=0
            )
        
        return proxima
        
    except Exception as e:
        print(f"❌ Error al calcular próxima ejecución: {e}")
        # En caso de error, programar para mañana a las 9:00 AM
        return (datetime.now() + timedelta(days=1)).replace(
            hour=9, minute=0, second=0, microsecond=0
        )

@panel_cliente_automatizaciones_bp.route("/api/funciones/<modulo>")
def api_funciones_por_modulo(modulo):
    """API: Obtener funciones disponibles por módulo"""
    try:
        response = supabase.table("funciones_automatizables") \
            .select("nombre_funcion, descripcion, parametros, categoria, envia_notificacion, ejemplo_uso") \
            .eq("modulo", modulo) \
            .eq("activa", True) \
            .eq("es_automatizable", True) \
            .order("nombre_funcion") \
            .execute()
        
        funciones = response.data if response.data else []
        return jsonify({"success": True, "funciones": funciones})
        
    except Exception as e:
        print(f"❌ Error API funciones: {e}")
        return jsonify({"success": False, "error": str(e)})

@panel_cliente_automatizaciones_bp.route("/api/funcion/<modulo>/<nombre_funcion>")
def api_detalle_funcion(modulo, nombre_funcion):
    """API: Obtener detalles de una función específica"""
    try:
        response = supabase.table("funciones_automatizables") \
            .select("*") \
            .eq("modulo", modulo) \
            .eq("nombre_funcion", nombre_funcion) \
            .eq("activa", True) \
            .limit(1) \
            .execute()
        
        if response.data:
            funcion = response.data[0]
            return jsonify({"success": True, "funcion": funcion})
        else:
            return jsonify({"success": False, "error": "Función no encontrada"})
        
    except Exception as e:
        print(f"❌ Error API detalle función: {e}")
        return jsonify({"success": False, "error": str(e)})

@panel_cliente_automatizaciones_bp.route("/api/modulos-disponibles")
def api_modulos_disponibles():
    """API: Obtener lista de módulos disponibles con conteo de funciones"""
    try:
        response = supabase.table("funciones_automatizables") \
            .select("modulo") \
            .eq("activa", True) \
            .eq("es_automatizable", True) \
            .execute()
        
        if response.data:
            # Contar funciones por módulo
            modulos_count = {}
            for func in response.data:
                modulo = func['modulo']
                modulos_count[modulo] = modulos_count.get(modulo, 0) + 1
            
            # Formatear respuesta
            modulos = [
                {
                    "nombre": modulo,
                    "total_funciones": count
                }
                for modulo, count in sorted(modulos_count.items())
            ]
            
            return jsonify({
                "success": True, 
                "modulos": modulos,
                "total_modulos": len(modulos)
            })
        else:
            return jsonify({
                "success": True, 
                "modulos": [],
                "total_modulos": 0
            })
        
    except Exception as e:
        print(f"❌ Error API módulos disponibles: {e}")
        return jsonify({"success": False, "error": str(e)})

@panel_cliente_automatizaciones_bp.route("/api/descubrir-funciones", methods=["POST"])
def api_descubrir_funciones():
    """API: Ejecutar descubrimiento automático de funciones"""
    try:
        if not DescubrirFunciones:
            return jsonify({
                "success": False,
                "error": "Sistema de descubrimiento no disponible"
            }), 500
        
        descubridor = DescubrirFunciones()
        print("🔍 Iniciando descubrimiento de funciones...")
        
        resultado = descubridor.ejecutar_descubrimiento_completo()
        
        return jsonify({
            "success": True,
            "mensaje": "Descubrimiento completado exitosamente",
            "funciones_encontradas": resultado.get('total_funciones', 0),
            "nuevas_funciones": resultado.get('nuevas_funciones', 0),
            "actualizadas": resultado.get('actualizadas', 0)
        })
        
    except Exception as e:
        print(f"❌ Error en descubrimiento de funciones: {e}")
        return jsonify({
            "success": False,
            "error": f"Error en descubrimiento: {str(e)}"
        }), 500

@panel_cliente_automatizaciones_bp.route("/api/refrescar-funciones", methods=["POST"])
def api_refrescar_funciones():
    """API: Refrescar lista de funciones desde la base de datos"""
    try:
        response = supabase.table("funciones_automatizables") \
            .select("*") \
            .eq("activa", True) \
            .eq("es_automatizable", True) \
            .order("modulo, nombre_funcion") \
            .execute()
        
        funciones = response.data if response.data else []
        
        # Agrupar por módulo
        funciones_por_modulo = {}
        for func in funciones:
            modulo = func['modulo']
            if modulo not in funciones_por_modulo:
                funciones_por_modulo[modulo] = []
            funciones_por_modulo[modulo].append(func)
        
        return jsonify({
            "success": True,
            "funciones": funciones,
            "funciones_por_modulo": funciones_por_modulo,
            "total_funciones": len(funciones),
            "total_modulos": len(funciones_por_modulo)
        })
        
    except Exception as e:
        print(f"❌ Error al refrescar funciones: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_automatizaciones_bp.route("/api/modulos-disponibles", methods=["GET"])
def api_modulos_disponibles():
    """API: Obtener lista de módulos con funciones disponibles"""
    try:
        response = supabase.table("funciones_automatizables") \
            .select("modulo") \
            .eq("activa", True) \
            .eq("es_automatizable", True) \
            .execute()
        
        modulos = set()
        if response.data:
            for func in response.data:
                modulos.add(func['modulo'])
        
        modulos_lista = sorted(list(modulos))
        
        return jsonify({
            "success": True,
            "modulos": modulos_lista,
            "total_modulos": len(modulos_lista)
        })
        
    except Exception as e:
        print(f"❌ Error al obtener módulos: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_automatizaciones_bp.route("/api/probar-sistema", methods=["POST"])
def api_probar_sistema():
    """API: Ejecutar pruebas completas del sistema de automatizaciones"""
    try:
        import subprocess
        import sys
        import json
        from datetime import datetime
        
        print("🧪 Iniciando pruebas del sistema...")
        
        # Ejecutar el script de pruebas
        ruta_script = os.path.join(os.getcwd(), "probar_automatizaciones.py")
        
        # Ejecutar script con captura de salida
        resultado = subprocess.run(
            [sys.executable, ruta_script],
            capture_output=True,
            text=True,
            timeout=60  # Timeout de 60 segundos
        )
        
        # Procesar resultado
        salida_completa = resultado.stdout
        errores = resultado.stderr
        codigo_salida = resultado.returncode
        
        # Analizar la salida para extraer estadísticas
        lineas = salida_completa.split('\n')
        pruebas_exitosas = 0
        total_pruebas = 0
        estado_sistema = "desconocido"
        
        for linea in lineas:
            if "Pruebas exitosas:" in linea:
                try:
                    partes = linea.split(": ")[1].split("/")
                    pruebas_exitosas = int(partes[0])
                    total_pruebas = int(partes[1])
                except:
                    pass
            elif "SISTEMA COMPLETAMENTE FUNCIONAL" in linea:
                estado_sistema = "completamente_funcional"
            elif "SISTEMA MAYORMENTE FUNCIONAL" in linea:
                estado_sistema = "mayormente_funcional"
            elif "SISTEMA CON PROBLEMAS" in linea:
                estado_sistema = "con_problemas"
        
        # Extraer resumen de pruebas individuales
        pruebas_detalle = []
        seccion_resumen = False
        
        for linea in lineas:
            if "RESUMEN DE PRUEBAS" in linea:
                seccion_resumen = True
                continue
            elif seccion_resumen and linea.strip():
                if linea.startswith("✅") or linea.startswith("❌"):
                    icono = "✅" if linea.startswith("✅") else "❌"
                    nombre = linea[2:].strip()
                    exitosa = linea.startswith("✅")
                    if nombre and "Pruebas exitosas:" not in nombre:
                        pruebas_detalle.append({
                            "nombre": nombre,
                            "exitosa": exitosa,
                            "icono": icono
                        })
                elif "Pruebas exitosas:" in linea:
                    break
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "codigo_salida": codigo_salida,
            "pruebas_exitosas": pruebas_exitosas,
            "total_pruebas": total_pruebas,
            "estado_sistema": estado_sistema,
            "pruebas_detalle": pruebas_detalle,
            "salida_completa": salida_completa,
            "errores": errores,
            "porcentaje_exito": round((pruebas_exitosas / total_pruebas * 100) if total_pruebas > 0 else 0, 1)
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Las pruebas tardaron demasiado tiempo (timeout de 60 segundos)",
            "timestamp": datetime.now().isoformat()
        }), 408
        
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return jsonify({
            "success": False,
            "error": f"Error ejecutando pruebas: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500
