from flask import Blueprint, render_template, request, redirect, url_for
import json
import os
from utils.config import login_requerido

etiquetas_bp = Blueprint("etiquetas", __name__)

@etiquetas_bp.route("/etiquetas")
@login_requerido
def mostrar_etiquetas():
    etiquetas_unicas = set()

    try:
        with open("contactos_info.json", "r", encoding="utf-8") as f:
            contactos = json.load(f)
        for info in contactos.values():
            etiquetas_unicas.update(info.get("etiquetas", []))
    except Exception:
        contactos = {}

    return render_template("etiquetas.html", etiquetas=sorted(etiquetas_unicas))

@etiquetas_bp.route("/etiquetas/editar/<nombre>", methods=["GET", "POST"])
@login_requerido
def editar_etiqueta(nombre):
    if request.method == "POST":
        nuevo_nombre = request.form["nuevo_nombre"].strip()
        if nuevo_nombre:
            with open("contactos_info.json", "r", encoding="utf-8") as f:
                contactos = json.load(f)

            for info in contactos.values():
                etiquetas = info.get("etiquetas", [])
                if nombre in etiquetas:
                    info["etiquetas"] = [nuevo_nombre if e == nombre else e for e in etiquetas]

            with open("contactos_info.json", "w", encoding="utf-8") as f:
                json.dump(contactos, f, indent=2, ensure_ascii=False)

        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    return render_template("editar_etiqueta.html", etiqueta=nombre)

@etiquetas_bp.route("/etiquetas/eliminar/<nombre>", methods=["POST"])
@login_requerido
def eliminar_etiqueta(nombre):
    with open("contactos_info.json", "r", encoding="utf-8") as f:
        contactos = json.load(f)

    for info in contactos.values():
        etiquetas = info.get("etiquetas", [])
        if nombre in etiquetas:
            info["etiquetas"] = [e for e in etiquetas if e != nombre]

    with open("contactos_info.json", "w", encoding="utf-8") as f:
        json.dump(contactos, f, indent=2, ensure_ascii=False)

    return redirect(url_for("etiquetas.mostrar_etiquetas"))
