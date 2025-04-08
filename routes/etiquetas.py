from flask import Blueprint, render_template, request, redirect, url_for
import json
import os
from utils.config import login_requerido

etiquetas_bp = Blueprint('etiquetas', __name__)

ARCHIVO_CONTACTOS = "contactos_info.json"

def obtener_etiquetas_unicas():
    if not os.path.exists(ARCHIVO_CONTACTOS):
        return []
    with open(ARCHIVO_CONTACTOS, 'r', encoding='utf-8') as f:
        data = json.load(f)
    etiquetas = set()
    for info in data.values():
        etiquetas.update(info.get("etiquetas", []))
    return sorted(etiquetas)

@etiquetas_bp.route('/etiquetas')
@login_requerido
def mostrar_etiquetas():
    etiquetas = obtener_etiquetas_unicas()
    return render_template("etiquetas.html", etiquetas=etiquetas)

@etiquetas_bp.route('/etiquetas/editar/<nombre>', methods=['GET', 'POST'])
@login_requerido
def editar_etiqueta(nombre):
    if request.method == 'POST':
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        if not nuevo_nombre:
            return redirect(url_for('etiquetas.mostrar_etiquetas'))

        if os.path.exists(ARCHIVO_CONTACTOS):
            with open(ARCHIVO_CONTACTOS, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for contacto in data.values():
                etiquetas = contacto.get("etiquetas", [])
                contacto["etiquetas"] = [nuevo_nombre if e == nombre else e for e in etiquetas]

            with open(ARCHIVO_CONTACTOS, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        return redirect(url_for('etiquetas.mostrar_etiquetas'))

    return render_template("editar_etiqueta.html", etiqueta=nombre)

@etiquetas_bp.route('/etiquetas/eliminar/<nombre>', methods=['POST'])
@login_requerido
def eliminar_etiqueta(nombre):
    if os.path.exists(ARCHIVO_CONTACTOS):
        with open(ARCHIVO_CONTACTOS, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for contacto in data.values():
            if "etiquetas" in contacto:
                contacto["etiquetas"] = [e for e in contacto["etiquetas"] if e != nombre]

        with open(ARCHIVO_CONTACTOS, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return redirect(url_for('etiquetas.mostrar_etiquetas'))
