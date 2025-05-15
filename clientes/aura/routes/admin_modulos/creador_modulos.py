from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from clientes.aura.utils.login_required import login_required
import textwrap
from pathlib import Path
from supabase import create_client
import os

admin_modulos_bp = Blueprint("admin_modulos", __name__)
MODULOS_PATH = Path("/path/to/modulos")

# ✅ Usar variables reales de entorno definidas en Railway
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise Exception("❌ Variables SUPABASE_URL o SUPABASE_KEY no definidas.")

supabase = create_client(supabase_url, supabase_key)

def sugerir_modulo(nombre_modulo, descripcion):
    # Implementación de la función para sugerir módulo
    pass

def validar_modulo(codigo):
    # Implementación de la función para validar módulo
    pass

@admin_modulos_bp.route("/admin/modulos", methods=["GET"])
@login_required
def ver_modulos():
    # ejemplo para mostrar módulos disponibles
    modulos = supabase.table("modulos_disponibles").select("*").execute().data
    return render_template("admin_modulos/ver_modulos.html", modulos=modulos)

@admin_modulos_bp.route("/generar", methods=["POST"])
@login_required
def generar():
    nombre_modulo = request.form.get("nombre_modulo", "").strip().lower()
    descripcion  = request.form.get("descripcion", "").strip()
    icono        = request.form.get("icono", "").strip() or "🧩"
    if not nombre_modulo:
        flash("Nombre de módulo vacío", "error")
        return redirect(url_for("admin_modulos.index"))

    # ✔️ IA sugiere esqueleto
    propuesta = sugerir_modulo(nombre_modulo, descripcion)
    if not propuesta.get("ok"):
        flash("IA no pudo generar módulo", "error")
        return redirect(url_for("admin_modulos.index"))

    codigo = propuesta["sugerencias"][0]
    # ✔️ IA auto-valida el snippet
    validacion = validar_modulo(codigo)
    if not validacion.get("ok"):
        flash(f"Errores IA: {', '.join(validacion['errores'])}", "error")
        return redirect(url_for("admin_modulos.index"))

    # ✔️ Guarda archivo scaffold (solo si no existe)
    carpeta = MODULOS_PATH / f"cliente_{nombre_modulo}"
    archivo_py = carpeta / f"panel_cliente_{nombre_modulo}.py"
    if not carpeta.exists():
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo_py.write_text(textwrap.dedent(codigo))

    # ✔️ Registra módulo en Supabase (modulos_disponibles)
    supabase.table("modulos_disponibles").insert({
        "nombre": nombre_modulo,
        "descripcion": descripcion or f"Módulo {nombre_modulo}",
        "icono": icono,
        "ruta": f"panel_cliente_{nombre_modulo}.panel_cliente_{nombre_modulo}",
    }).execute()

    flash("Módulo creado y validado por IA ✅", "success")
    return redirect(url_for("admin_modulos.index"))

@admin_modulos_bp.route("/verificar", methods=["POST"])
@login_required
def verificar_existente():
    nombre_modulo = request.form.get("nombre_modulo_verificar", "").strip().lower()
    archivo = MODULOS_PATH / f"panel_cliente_{nombre_modulo}" / f"vista_panel_cliente_{nombre_modulo}.py"
    if not archivo.exists():
        flash("Módulo no encontrado", "error")
        return redirect(url_for("admin_modulos.index"))

    resultado = validar_modulo(archivo.read_text())
    if resultado.get("ok"):
        flash("Sin errores detectados por IA 🎉", "success")
    else:
        flash(f"Errores: {', '.join(resultado['errores'])}", "error")
    return redirect(url_for("admin_modulos.index"))