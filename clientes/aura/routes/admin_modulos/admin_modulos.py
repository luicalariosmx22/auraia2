from flask import Blueprint, render_template, request, redirect, url_for, flash
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.login_required import login_required

admin_modulos_bp = Blueprint(
    "admin_modulos",
    __name__,
    template_folder="../../../templates/admin_modulos"
)


@admin_modulos_bp.route("/configuracion/<nombre_nora>", methods=["GET"])
@login_required
def configuracion(nombre_nora):
    """Ver configuración de módulos activos para una Nora"""
    resultado = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()

    if not resultado.data or len(resultado.data) == 0:
        flash(f"No se encontró configuración para la Nora: {nombre_nora}", "error")
        return redirect(url_for("admin_modulos.index"))

    configuracion = resultado.data[0]
    return render_template("admin_modulos/configuracion.html", configuracion=configuracion)

@admin_modulos_bp.route("/")
def index():
    """Vista principal del gestor de módulos."""
    try:
        # Obtener Noras
        response_noras = supabase.table("configuracion_bot").select("nombre_nora, nombre_visible").execute()
        noras = response_noras.data if hasattr(response_noras, 'data') else []
        # Obtener módulos (puedes ajustar el origen según tu modelo de datos)
        response_modulos = supabase.table("modulos_disponibles").select("nombre, descripcion, tipo, icono").execute()
        modulos = response_modulos.data if hasattr(response_modulos, 'data') else []
        if not modulos:
            flash("No se encontraron módulos disponibles. Verifica la tabla 'modulos_disponibles' en Supabase.", "warning")
        return render_template('admin_modulos/index.html', noras=noras, modulos=modulos)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return render_template('admin_modulos/index.html', noras=[], modulos=[])
