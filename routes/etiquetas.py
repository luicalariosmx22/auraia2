from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import os
from utils.config import login_requerido

etiquetas_bp = Blueprint("etiquetas", __name__)
ARCHIVO_ETIQUETAS = "etiquetas.json"

# Funciones auxiliares
def cargar_etiquetas():
    if os.path.exists(ARCHIVO_ETIQUETAS):
        try:
            with open(ARCHIVO_ETIQUETAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_etiquetas(etiquetas):
    with open(ARCHIVO_ETIQUETAS, "w", encoding="utf-8") as f:
        json.dump(etiquetas, f, ensure_ascii=False, indent=2)

# Mostrar etiquetas
@etiquetas_bp.route("/etiquetas")
@login_requerido
def mostrar_etiquetas():
    etiquetas = cargar_etiquetas()
    return render_template("etiquetas.html", etiquetas=etiquetas)

# Agregar nueva etiqueta
@etiquetas_bp.route("/etiquetas/agregar", methods=["POST"])
@login_requerido
def agregar_etiqueta():
    nueva = request.form.get("etiqueta", "").strip()
    if not nueva:
        flash("Etiqueta no puede estar vacía", "danger")
        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    etiquetas = cargar_etiquetas()
    if nueva in etiquetas:
        flash("Esa etiqueta ya existe", "warning")
        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    etiquetas.append(nueva)
    guardar_etiquetas(etiquetas)
    flash("Etiqueta agregada correctamente", "success")
    return redirect(url_for("etiquetas.mostrar_etiquetas"))

# Editar etiqueta
@etiquetas_bp.route("/etiquetas/editar/<nombre>", methods=["GET", "POST"])
@login_requerido
def editar_etiqueta(nombre):
    etiquetas = cargar_etiquetas()
    if request.method == "POST":
        nueva = request.form.get("nueva_etiqueta", "").strip()
        if not nueva:
            flash("Etiqueta nueva no puede estar vacía", "danger")
            return redirect(url_for("etiquetas.mostrar_etiquetas"))

        if nueva != nombre and nueva in etiquetas:
            flash("Ya existe otra etiqueta con ese nombre", "warning")
            return redirect(url_for("etiquetas.mostrar_etiquetas"))

        # Reemplazar nombre
        etiquetas = [nueva if e == nombre else e for e in etiquetas]
        guardar_etiquetas(etiquetas)
        flash("Etiqueta editada correctamente", "success")
        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    return render_template("editar_etiqueta.html", nombre=nombre)

# Eliminar etiqueta
@etiquetas_bp.route("/etiquetas/eliminar/<nombre>", methods=["POST"])
@login_requerido
def eliminar_etiqueta(nombre):
    etiquetas = cargar_etiquetas()
    if nombre in etiquetas:
        etiquetas.remove(nombre)
        guardar_etiquetas(etiquetas)
        flash("Etiqueta eliminada correctamente", "success")
    else:
        flash("Etiqueta no encontrada", "danger")
    return redirect(url_for("etiquetas.mostrar_etiquetas"))
