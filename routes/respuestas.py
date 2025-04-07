from flask import Blueprint, request, redirect, url_for, session, render_template
import json
from utils.config import login_requerido

respuestas_bp = Blueprint('respuestas', __name__)

@respuestas_bp.route('/guardar', methods=['POST'])
@login_requerido
def guardar():
    claves_raw = request.form['titulo'].strip().lower()
    palabras_clave = [x.strip() for x in claves_raw.split(',') if x.strip()]
    contenido = request.form['contenido'].strip()
    categoria = request.form['categoria']
    botones_json = request.form.get('botones_json', '[]')

    try:
        botones = json.loads(botones_json)
    except json.JSONDecodeError:
        botones = []

    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    id_respuesta = palabras_clave[0]
    data[id_respuesta] = {
        "palabras_clave": palabras_clave,
        "contenido": contenido,
        "categoria": categoria,
        "botones": botones
    }

    with open('bot_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return redirect(url_for('main.index'))

@respuestas_bp.route('/editar/<clave>', methods=['GET', 'POST'])
@login_requerido
def editar(clave):
    clave = clave.lower()
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if request.method == 'POST':
        claves_raw = request.form['titulo'].strip().lower()
        palabras_clave = [x.strip() for x in claves_raw.split(',') if x.strip()]
        nuevo_contenido = request.form['contenido']
        nueva_categoria = request.form['categoria']
        botones_json = request.form.get('botones_json', '[]')

        try:
            botones = json.loads(botones_json)
        except json.JSONDecodeError:
            botones = []

        id_respuesta = palabras_clave[0]
        data.pop(clave, None)
        data[id_respuesta] = {
            "palabras_clave": palabras_clave,
            "contenido": nuevo_contenido,
            "categoria": nueva_categoria,
            "botones": botones
        }

        with open('bot_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return redirect(url_for('main.index'))

    else:
        info = data.get(clave, {})
        palabras_clave = ', '.join(info.get("palabras_clave", [clave]))
        contenido = info.get("contenido", "")
        categoria = info.get("categoria", "")
        botones = info.get("botones", [])

        try:
            with open('categorias.json', 'r', encoding='utf-8') as f:
                categorias = json.load(f)
        except FileNotFoundError:
            categorias = []

        return render_template('editar.html', clave=clave, contenido=contenido, categoria=categoria, categorias=categorias, botones_json=json.dumps(botones), palabras_clave=palabras_clave)

@respuestas_bp.route('/eliminar/<clave>', methods=['POST'])
@login_requerido
def eliminar(clave):
    clave = clave.lower()
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if clave in data:
        del data[clave]
        with open('bot_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return redirect(url_for('main.index'))
