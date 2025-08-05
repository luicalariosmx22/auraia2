from flask import Blueprint, render_template, flash, redirect, url_for, request, session, jsonify
from pathlib import Path
import json
import os
from datetime import datetime
import traceback

from clientes.aura.utils.login_required import login_required
from .analizador import analizar_modulo, analizar_modulo_antiguo
from .ia_utils import generar_explicacion_errores
from clientes.aura.utils.diagnostico_ia import diagnosticar_modulo

# Definición del blueprint
verificador_modulos_bp = Blueprint(
    "verificador_modulos",
    __name__,
    template_folder="../templates"
)


# --- CACHÉ SIMPLE EN MEMORIA PARA OPTIMIZAR EL FRONTEND ---
_cache_modulos = {"timestamp": 0, "modulos": []}
_cache_tiempo_vida = 120  # segundos

@verificador_modulos_bp.route("/", methods=["GET"])
@login_required
def index():
    """Dashboard principal del verificador de módulos."""
    import time
    global _cache_modulos
    ahora = time.time()
    # Si el caché está vacío o expirado, recargar
    if not _cache_modulos["modulos"] or (ahora - _cache_modulos["timestamp"]) > _cache_tiempo_vida:
        try:
            from clientes.aura.utils.db import get_supabase_client
            supabase = get_supabase_client()
            response = supabase.table("modulos_disponibles").select("nombre").execute()
            if not response.data:
                flash("No hay módulos registrados en la base de datos.", "warning")
                _cache_modulos["modulos"] = []
                _cache_modulos["timestamp"] = ahora
                return render_template("admin_modulos/index.html", modulos=[], titulo="Verificador de Módulos")

            modulos = []
            for row in response.data:
                nombre = row["nombre"]
                info = analizar_modulo(nombre)
                if info:
                    modulos.append(info)

            # Ordenar por nombre
            modulos.sort(key=lambda x: x["nombre"])
            _cache_modulos["modulos"] = modulos
            _cache_modulos["timestamp"] = ahora
        except Exception as e:
            print(f"❌ Error en verificador index: {str(e)}")
            flash(f"❌ Error al cargar módulos: {str(e)}", "error")
            _cache_modulos["modulos"] = []
            _cache_modulos["timestamp"] = ahora
            return render_template("admin_modulos/index.html", modulos=[], error=str(e))

    # Siempre pasar una lista (aunque vacía)
    return render_template(
        "admin_modulos/index.html",
        modulos=_cache_modulos["modulos"],
        titulo="Verificador de Módulos"
    )

@verificador_modulos_bp.route("/<nombre_modulo>", methods=["GET"])
@login_required
def ver_modulo(nombre_modulo):
    """Vista detallada de un módulo específico."""
    try:
        modulo = analizar_modulo(nombre_modulo)
        
        # Obtener contenido del archivo principal
        if modulo.get("path_archivo") and os.path.exists(modulo["path_archivo"]):
            try:
                with open(modulo["path_archivo"], "r", encoding="utf-8", errors="ignore") as f:
                    modulo["archivo_contenido"] = f.read()
                modulo["existe_archivo"] = True
            except Exception as e:
                print(f"❌ Error al leer archivo: {e}")
                modulo["archivo_contenido"] = None
                modulo["existe_archivo"] = False
        else:
            print(f"❌ Error al obtener archivo principal: Archivo no encontrado")
            modulo["archivo_contenido"] = None
            modulo["existe_archivo"] = False

        # Buscar archivos candidatos para este módulo
        modulo["archivos_candidatos"] = buscar_archivos_candidatos(nombre_modulo)

        # Agregar explicaciones generadas por IA
        modulo["explicaciones_ai"] = generar_explicacion_errores(modulo)
        
        # Diagnóstico adicional con IA
        modulo["diagnostico_ia"] = diagnosticar_modulo(modulo)
        
        # Renderizar template con los datos del módulo
        return render_template(
            "admin_modulos/detalle.html",
            modulo=modulo,
            titulo=f"Módulo: {nombre_modulo}",
            modo="verificador"
        )

    except Exception as e:
        import traceback
        print(f"❌ Error detallado al cargar módulo {nombre_modulo}:")
        print(traceback.format_exc())
        flash(f"❌ Error al cargar módulo {nombre_modulo}: {str(e)}", "error")
        return redirect(url_for("verificador_modulos.index"))

@verificador_modulos_bp.route("/<nombre_modulo>/archivo_principal", methods=["POST"])
@login_required
def definir_archivo_principal(nombre_modulo):
    """Guarda el archivo principal elegido manualmente para un módulo."""
    archivo = request.form.get("archivo_principal")
    if not archivo:
        flash("❌ No se seleccionó ningún archivo", "error")
        return redirect(url_for("verificador_modulos.ver_modulo", nombre_modulo=nombre_modulo))

    try:
        # Guardar en sesión
        if "archivos_principales" not in session:
            session["archivos_principales"] = {}
        
        session["archivos_principales"][nombre_modulo] = archivo
        session.modified = True
        
        # Guardar en archivo de configuración para persistencia
        config_path = "clientes/aura/routes/admin_modulos/verificador/config"
        os.makedirs(config_path, exist_ok=True)
        
        config_file = os.path.join(config_path, "archivos_principales.json")
        
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            else:
                config_data = {}
        except Exception:
            config_data = {}
        
        config_data[nombre_modulo] = archivo
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        
        flash(f"✅ Archivo principal '{archivo}' definido correctamente", "success")
    except Exception as e:
        flash(f"❌ Error al definir archivo principal: {str(e)}", "error")
    
    return redirect(url_for("verificador_modulos.ver_modulo", nombre_modulo=nombre_modulo))

@verificador_modulos_bp.route("/<nombre_modulo>/verificar_http", methods=["POST"])
@login_required
def verificar_http_modulo(nombre_modulo):
    """Fuerza la verificación HTTP de un módulo."""
    try:
        modulo = analizar_modulo(nombre_modulo)
        return jsonify({
            "success": True,
            "respuesta_http": modulo.get("respuesta_http"),
            "existe_ruta": modulo.get("existe_ruta", False),
            "explicacion_http": modulo.get("explicacion_http", "No se pudo verificar"),
            "redirige_a": modulo.get("redirige_a")
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@verificador_modulos_bp.route("/<nombre_modulo>/guardar_en_supabase", methods=["POST"])
@login_required
def guardar_en_supabase(nombre_modulo):
    """Guarda la configuración del módulo en la tabla modulos_disponibles de Supabase."""
    try:
        archivo = request.form.get("archivo_principal")
        if not archivo:
            return jsonify({
                "success": False,
                "message": "No se proporcionó un archivo principal"
            })
        
        # Obtener cliente Supabase
        from clientes.aura.utils.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Obtener información del módulo para datos adicionales
        modulo = analizar_modulo(nombre_modulo)
        
        # Preparar datos para Supabase
        data = {
            "nombre": nombre_modulo,
            "archivo_principal": archivo,
            "descripcion": modulo.get("descripcion", f"Módulo {nombre_modulo.capitalize()}"),
            "icono": modulo.get("icono", "fa-cube"),
            "ruta": modulo.get("ruta_base", f"/panel_cliente/{nombre_modulo}")
        }
        
        # Verificar si ya existe una entrada para este módulo
        response = supabase.table("modulos_disponibles").select("id").eq("nombre", nombre_modulo).execute()
        
        if response.data:
            # Actualizar registro existente
            supabase.table("modulos_disponibles").update(data).eq("nombre", nombre_modulo).execute()
            accion = "actualizado"
        else:
            # Crear nuevo registro
            supabase.table("modulos_disponibles").insert(data).execute()
            accion = "creado"
        
        
        # Guardar también en archivo local para redundancia
        config_path = "clientes/aura/routes/admin_modulos/verificador/config"
        os.makedirs(config_path, exist_ok=True)
        config_file = os.path.join(config_path, "archivos_principales.json")
        
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            else:
                config_data = {}
        except Exception:
            config_data = {}
        
        config_data[nombre_modulo] = archivo
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        
        flash(f"✅ Módulo '{nombre_modulo}' {accion} en Supabase correctamente", "success")
        return jsonify({
            "success": True,
            "message": f"Módulo '{nombre_modulo}' {accion} correctamente"
        })
    
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error al guardar en Supabase: {str(e)}", "error")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })

def buscar_archivos_candidatos(nombre_modulo):
    """
    Busca archivos candidatos para ser el archivo principal de un módulo.
    
    Args:
        nombre_modulo (str): Nombre del módulo
        
    Returns:
        list: Lista de rutas a archivos candidatos
    """
    candidatos = []
    
    # Buscar en la carpeta routes
    rutas_a_revisar = [
        f"clientes/aura/routes/panel_cliente_{nombre_modulo}.py",
        f"clientes/aura/routes/panel_cliente_{nombre_modulo}/__init__.py",
        f"clientes/aura/routes/panel_cliente_{nombre_modulo}/blueprint.py",
        f"clientes/aura/routes/panel_cliente_{nombre_modulo}/panel_cliente_{nombre_modulo}.py",
        f"clientes/aura/routes/panel_cliente_{nombre_modulo}/vista_panel_cliente_{nombre_modulo}.py",
    ]
    
    # Para el módulo de pagos, revisar ubicaciones específicas
    if nombre_modulo == "pagos":
        rutas_a_revisar.extend([
            "clientes/aura/routes/panel_cliente_pagos/vista_pagos.py",
            "clientes/aura/routes/panel_cliente_pagos/modulos/pagos.py",
            "clientes/aura/routes/panel_cliente_pagos/vista_panel_cliente_pagos.py"
        ])
    
    # Verificar existencia y añadir a candidatos
    for ruta in rutas_a_revisar:
        if os.path.exists(ruta):
            candidatos.append(ruta)
    
    # Buscar en el directorio del módulo si existe
    directorio_modulo = f"clientes/aura/routes/panel_cliente_{nombre_modulo}"
    if os.path.isdir(directorio_modulo):
        for archivo in os.listdir(directorio_modulo):
            if archivo.endswith(".py") and not archivo.startswith("__"):
                ruta_completa = os.path.join(directorio_modulo, archivo)
                if ruta_completa not in candidatos:
                    candidatos.append(ruta_completa)
    
    return candidatos