from flask import Blueprint, render_template, request, flash, redirect, url_for
from clientes.aura.utils.login_required import login_required
from clientes.aura.utils.ai_modulos import sugerir_modulo, validar_modulo
from clientes.aura.utils.supabase_client import supabase
from pathlib import Path
import textwrap

admin_modulos_bp = Blueprint(
    "admin_modulos",
    __name__,
    template_folder="../../../templates/admin_modulos",
)

# Directorio donde se crean los nuevos módulos
MODULOS_PATH = Path("clientes/aura/routes")

# ──────────────────────────────────────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────────────────────────────────────

@admin_modulos_bp.route("/", methods=["GET"], strict_slashes=False)
@admin_modulos_bp.route("", methods=["GET"], strict_slashes=False)
@login_required
def index():
    """Dashboard de módulos disponibles."""
    modulos = supabase.table("modulos_disponibles").select("*").execute().data
    return render_template("admin_modulos/index.html", modulos=modulos)

@admin_modulos_bp.route("/generar", methods=["POST"])
@login_required
def generar():
    nombre_modulo = request.form.get("nombre_modulo", "").strip().lower()
    descripcion = request.form.get("descripcion", "").strip()
    icono = request.form.get("icono", "").strip() or "🧩"

    if not nombre_modulo:
        flash("Nombre de módulo vacío", "error")
        return redirect(url_for("admin_modulos.index"))

    # 1️⃣ Solicitar scaffold a la IA
    propuesta = sugerir_modulo(nombre_modulo, descripcion)
    if not propuesta.get("ok"):
        flash("IA no pudo generar módulo", "error")
        return redirect(url_for("admin_modulos.index"))

    codigo = propuesta["sugerencias"][0]

    # 2️⃣ Validar código sugerido
    validacion = validar_modulo(codigo)
    if not validacion.get("ok"):
        flash(f"Errores IA: {', '.join(validacion['errores'])}", "error")
        return redirect(url_for("admin_modulos.index"))

    # 3️⃣ Guardar archivo si la carpeta no existe
    carpeta = MODULOS_PATH / f"cliente_{nombre_modulo}"
    archivo_py = carpeta / f"panel_cliente_{nombre_modulo}.py"
    if not carpeta.exists():
        carpeta.mkdir(parents=True)
        archivo_py.write_text(textwrap.dedent(codigo))

    # 4️⃣ Upsert en modulos_disponibles
    supabase.table("modulos_disponibles").upsert({
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
    archivo = (
        MODULOS_PATH / f"panel_cliente_{nombre_modulo}" / f"vista_panel_cliente_{nombre_modulo}.py"
    )

    if not archivo.exists():
        flash("Módulo no encontrado", "error")
        return redirect(url_for("admin_modulos.index"))

    resultado = validar_modulo(archivo.read_text())
    if resultado.get("ok"):
        flash("Sin errores detectados por IA 🎉", "success")
    else:
        flash(f"Errores: {', '.join(resultado['errores'])}", "error")
    return redirect(url_for("admin_modulos.index"))