

import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from clientes.aura.utils.supabase_client import supabase

# Definir blueprint antes de los decoradores
admin_creador_modulos_bp = Blueprint("admin_creador_modulos", __name__)

# Endpoint para edición de módulo vía AJAX
@admin_creador_modulos_bp.route("/editar_modulo", methods=["POST"])
def editar_modulo():
    try:
        data = request.get_json()
        id_modulo = data.get("id")
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        icono = data.get("icono", "🧩").strip() or "🧩"
        if not id_modulo or not nombre:
            return jsonify({"success": False, "error": "Faltan datos obligatorios"}), 400

        # Actualizar en Supabase
        res = supabase.table("modulos_disponibles").update({
            "nombre": nombre,
            "descripcion": descripcion,
            "icono": icono
        }).eq("id", id_modulo).execute()
        if hasattr(res, 'error') and res.error:
            return jsonify({"success": False, "error": str(res.error)}), 500
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_creador_modulos_bp.route("/gestionar", methods=["GET"])
def gestionar_modulos():
    """Vista para gestionar todos los módulos (submodulos, botones, vistas extra)"""

    # Cargar módulos registrados
    modulos_response = supabase.table("modulos_disponibles").select("*").execute()
    modulos = modulos_response.data if modulos_response.data else []

    # Cargar configuración de todas las Noras
    noras_response = supabase.table("configuracion_bot").select("nombre_nora, modulos").execute()
    configuraciones = noras_response.data if noras_response.data else []

    return render_template(
        "admin_modulos/gestionar_modulos.html",
        modulos=modulos,
        configuraciones=configuraciones
    )


@admin_creador_modulos_bp.route("/crear", methods=["GET", "POST"])
def crear_modulo():
    """Crea un nuevo módulo manualmente y lo registra en Supabase."""

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip().lower().replace(" ", "_")
        descripcion = request.form.get("descripcion", "").strip()
        icono = request.form.get("icono", "").strip() or "🧩"
        nombre_nora = request.form.get("nombre_nora", "").strip()

        if not nombre:
            flash("Nombre inválido", "error")
            return render_template("admin_modulos/crear_modulo.html")

        nombre_archivo = f"panel_cliente_{nombre}"
        carpeta_backend = f"clientes/aura/routes/{nombre_archivo}"
        archivo_py = f"{carpeta_backend}/{nombre_archivo}.py"
        ruta_templates = f"clientes/aura/templates/{nombre_archivo}"

        # Validar si ya existe en Supabase
        existe = supabase.table("modulos_disponibles").select("id").eq("nombre", nombre).execute()
        if existe.data:
            flash("Ya existe un módulo con ese nombre.", "error")
            return render_template("admin_modulos/crear_modulo.html")

        # Crear carpetas necesarias
        os.makedirs(carpeta_backend, exist_ok=True)
        os.makedirs(ruta_templates, exist_ok=True)

        # __init__.py con import del blueprint
        contenido_init = f"from .{nombre_archivo} import {nombre_archivo}_bp\n"
        with open(os.path.join(carpeta_backend, "__init__.py"), "w", encoding="utf-8") as f:
            f.write(contenido_init)

        # Código Python del módulo
        contenido_py = f"""from flask import Blueprint, render_template, request

{nombre_archivo}_bp = Blueprint("{nombre_archivo}_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/{nombre}")

@{nombre_archivo}_bp.route("/")
def panel_cliente_{nombre}():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("{nombre_archivo}/index.html", nombre_nora=nombre_nora)
"""
        with open(archivo_py, "w", encoding="utf-8") as f:
            f.write(contenido_py)

        # HTML base
        contenido_html = f"""{{% extends "base_cliente.html" %}}

{{% block contenido %}}
<div class="max-w-4xl mx-auto py-8">
  <h1 class="text-3xl font-bold mb-4">{icono} Módulo: {nombre.capitalize()}</h1>
  <p class="text-gray-700">Este es el módulo inicial para {nombre}.</p>
</div>
{{% endblock %}}
"""
        with open(os.path.join(ruta_templates, "index.html"), "w", encoding="utf-8") as f:
            f.write(contenido_html)

        # Registrar en Supabase
        supabase.table("modulos_disponibles").insert({
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "descripcion": descripcion,
            "icono": icono,
            "ruta": f"{nombre_archivo}.{nombre_archivo}_bp"
        }).execute()

        # Activar para Nora si se indicó

        if nombre_nora:
            resultado = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
            if not resultado.data:
                flash(f"No se encontró configuración para la Nora: {nombre_nora}", "error")
                return render_template("admin_modulos/crear_modulo.html")

            mod_actuales = resultado.data[0].get("modulos", {})
            if isinstance(mod_actuales, list):
                mod_actuales = {m: True for m in mod_actuales}
            if nombre not in mod_actuales:
                mod_actuales[nombre] = True
                supabase.table("configuracion_bot").update({"modulos": mod_actuales}).eq("nombre_nora", nombre_nora).execute()

        flash("Módulo creado correctamente", "success")
        return render_template("admin_modulos/crear_modulo.html")

    return render_template("admin_modulos/crear_modulo.html")