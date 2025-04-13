from flask import Blueprint, request, redirect, url_for, render_template
import json
from utils.config import login_requerido

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias')
@login_requerido
def mostrar_categorias():
    try:
        with open('categorias.json', 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    except FileNotFoundError:
        categorias = []
    return render_template('categorias.html', categorias=categorias)

@categorias_bp.route('/categorias/agregar', methods=['POST'])
@login_requerido
def agregar_categoria():
    nueva = request.form['nueva_categoria'].strip()
    try:
        with open('categorias.json', 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    except FileNotFoundError:
        categorias = []

    if nueva and nueva not in categorias:
        categorias.append(nueva)
        with open('categorias.json', 'w', encoding='utf-8') as f:
            json.dump(categorias, f, ensure_ascii=False, indent=4)

    return redirect(url_for('categorias.mostrar_categorias'))

@categorias_bp.route('/categorias/eliminar/<categoria>', methods=['POST'])
@login_requerido
def eliminar_categoria(categoria):
    try:
        with open('categorias.json', 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    except FileNotFoundError:
        categorias = []

    categoria = categoria.strip()
    if categoria in categorias:
        categorias.remove(categoria)
        with open('categorias.json', 'w', encoding='utf-8') as f:
            json.dump(categorias, f, ensure_ascii=False, indent=4)

    return redirect(url_for('categorias.mostrar_categorias'))

@categorias_bp.route('/categorias/editar/<nombre>', methods=['GET', 'POST'])
@login_requerido
def editar_categoria(nombre):
    nombre = nombre.strip()

    try:
        with open('categorias.json', 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    except FileNotFoundError:
        categorias = []

    if request.method == 'POST':
        nuevo_nombre = request.form['nuevo_nombre'].strip()

        if nuevo_nombre and nuevo_nombre != nombre and nuevo_nombre not in categorias:
            # Cambiar en la lista de categorías
            categorias = [nuevo_nombre if cat == nombre else cat for cat in categorias]
            with open('categorias.json', 'w', encoding='utf-8') as f:
                json.dump(categorias, f, ensure_ascii=False, indent=4)

            # Cambiar en las respuestas que usan esa categoría
            try:
                with open('bot_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {}

            for clave in data:
                if data[clave].get("categoria") == nombre:
                    data[clave]["categoria"] = nuevo_nombre

            with open('bot_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return redirect(url_for('categorias.mostrar_categorias'))

    return render_template('editar_categoria.html', nombre=nombre)
