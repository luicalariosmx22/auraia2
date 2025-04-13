from flask import Blueprint, render_template, request, redirect, url_for
import json
import os

panel_errores_bp = Blueprint("panel_errores", __name__)

@panel_errores_bp.route("/panel/errores", endpoint="ver_errores")
def ver_errores():
    errores = []
    ruta = "logs_errores.json"

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                errores = json.load(f)
            except Exception:
                errores = []

    return render_template("panel_errores.html", errores=errores)

@panel_errores_bp.route("/panel/errores/limpiar", methods=["POST"])
def limpiar_errores():
    ruta = "logs_errores.json"
    if os.path.exists(ruta):
        os.remove(ruta)
    return redirect(url_for("panel_errores.ver_errores"))

# Función auxiliar para usar en el context processor
def contar_errores():
    ruta = "logs_errores.json"
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                errores = json.load(f)
                return len(errores)
        except:
            return 0
    return 0

# ✅ Alias para importar como 'error_panel_bp' desde app.py
error_panel_bp = panel_errores_bp
