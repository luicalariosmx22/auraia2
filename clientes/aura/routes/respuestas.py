from flask import Blueprint, request, redirect, url_for, session, render_template, flash
import json
import os
from utils.config import login_requerido

respuestas_bp = Blueprint('respuestas', __name__)

BOT_DATA_FILE = 'bot_data.json'
CATEGORIAS_FILE = 'categorias.json'

def cargar_respuestas():
    if not os.path.exists(BOT_DATA_FILE):
        return {}
    with open(BOT_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_respuestas(data):
    with open(BOT_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def cargar_categorias():
    if not os.path.exists(CATEGORIAS_FILE):
        return []
    with open(CATEGORIAS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@respuestas_bp.route('/respuestas')
@login_requerido
def mostrar_respuestas():
    datos = cargar_respuestas()
    return render_template('respuestas.html', datos=datos)

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

    data = cargar_respuestas()
    id_respuesta = palabras_clave[0]
    data[id_respuesta] = {
        "palabras_clave": palabras_clave,
        "contenido": contenido,
        "categoria": categoria,
        "botones": botones
    }

    guardar_respuestas(data)
    return redirect(url_for('respuestas.mostrar_respuestas'))

@respuestas_bp.route('/editar/<clave>', methods=['GET', 'POST'])
@login_requerido
def editar(clave):
    clave = clave.lower()
    data = cargar_respuestas()

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

        guardar_respuestas(data)
        return redirect(url_for('respuestas.mostrar_respuestas'))

    else:
        info = data.get(clave, {})
        palabras_clave = ', '.join(info.get("palabras_clave", [clave]))
        contenido = info.get("contenido", "")
        categoria = info.get("categoria", "")
        botones = info.get("botones", [])

        categorias = cargar_categorias()

        return render_template('editar.html',
                               clave=clave,
                               contenido=contenido,
                               categoria=categoria,
                               categorias=categorias,
                               botones_json=json.dumps(botones),
                               palabras_clave=palabras_clave)

@respuestas_bp.route('/eliminar/<clave>', methods=['POST'])
@login_requerido
def eliminar(clave):
    clave = clave.lower()
    data = cargar_respuestas()
    if clave in data:
        del data[clave]
        guardar_respuestas(data)
    return redirect(url_for('respuestas.mostrar_respuestas'))
