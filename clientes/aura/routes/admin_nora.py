# 📁 clientes/aura/routes/admin_nora.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import os
import json

admin_nora_bp = Blueprint("admin_nora", __name__)

@admin_nora_bp.route("/admin/nora/<nombre_carpeta>", methods=["GET", "POST"])
def ver_nora(nombre_carpeta):
    ruta_config = f"clientes/{nombre_carpeta}/config.json"

    if not os.path.exists(ruta_config):
        abort(404, description="Nora no encontrada")

    if request.method == "POST":
        # Recibir formulario y guardar cambios
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        estado = request.form.get("estado", "").strip()
        modulos = request.form.getlist("modulos")

        nuevos_datos = {
            "nombre": nombre,
            "telefono": telefono,
            "estado": estado,
            "modulos": modulos
        }

        with open(ruta_config, "w", encoding="utf-8") as f:
            json.dump(nuevos_datos, f, indent=4, ensure_ascii=False)

        flash("✅ Datos actualizados correctamente.")
        return redirect(url_for("admin_nora.ver_nora", nombre_carpeta=nombre_carpeta))

    # GET: cargar info para editar
    with open(ruta_config, "r", encoding="utf-8") as f:
        datos = json.load(f)

    return render_template("admin_nora.html", nora=datos, carpeta=nombre_carpeta)
