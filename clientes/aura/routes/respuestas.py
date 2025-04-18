from flask import Blueprint, request, redirect, url_for, session, render_template, flash, jsonify
from supabase import create_client
from dotenv import load_dotenv
from utils.config import login_requerido
import os
import json

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

respuestas_bp = Blueprint('respuestas', __name__)

def cargar_respuestas():
    try:
        response = supabase.table("bot_data").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar respuestas: {not response.data}")
            return {}
        return {r["id"]: r for r in response.data}
    except Exception as e:
        print(f"❌ Error al cargar respuestas: {str(e)}")
        return {}

def cargar_categorias():
    try:
        response = supabase.table("categorias").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar categorías: {not response.data}")
            return []
        return [c["nombre"] for c in response.data]
    except Exception as e:
        print(f"❌ Error al cargar categorías: {str(e)}")
        return []

@respuestas_bp.route('/respuestas')
@login_requerido
def mostrar_respuestas():
    datos = cargar_respuestas()
    return render_template('respuestas.html', datos=datos)

@respuestas_bp.route('/guardar', methods=['POST'])
@login_requerido
def guardar():
    palabras_clave = request.form.get('titulo', '').strip().lower().split(',')
    palabras_clave = [x.strip() for x in palabras_clave if x.strip()]
    contenido = request.form.get('contenido', '').strip()
    categoria = request.form.get('categoria', '').strip()
    botones_json = request.form.get('botones_json', '[]')

    if not palabras_clave or not contenido or not categoria:
        flash("❌ Todos los campos son obligatorios", "danger")
        return redirect(url_for('respuestas.mostrar_respuestas'))

    try:
        botones = json.loads(botones_json)
    except json.JSONDecodeError:
        botones = []

    id_respuesta = palabras_clave[0]

    try:
        response = supabase.table("bot_data").insert({
            "id": id_respuesta,
            "palabras_clave": palabras_clave,
            "contenido": contenido,
            "categoria": categoria,
            "botones": botones
        }).execute()
        if not response.data:
            print(f"❌ Error al guardar respuesta: {not response.data}")
            flash("❌ Error al guardar respuesta", "danger")
        else:
            flash("✅ Respuesta guardada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al guardar respuesta: {str(e)}")
        flash("❌ Error al guardar respuesta", "danger")

    return redirect(url_for('respuestas.mostrar_respuestas'))

@respuestas_bp.route('/editar/<clave>', methods=['GET', 'POST'])
@login_requerido
def editar(clave):
    clave = clave.lower()
    data = cargar_respuestas()

    if request.method == 'POST':
        palabras_clave = request.form.get('titulo', '').strip().lower().split(',')
        palabras_clave = [x.strip() for x in palabras_clave if x.strip()]
        nuevo_contenido = request.form.get('contenido', '').strip()
        nueva_categoria = request.form.get('categoria', '').strip()
        botones_json = request.form.get('botones_json', '[]')

        if not palabras_clave or not nuevo_contenido or not nueva_categoria:
            flash("❌ Todos los campos son obligatorios", "danger")
            return redirect(url_for('respuestas.mostrar_respuestas'))

        try:
            botones = json.loads(botones_json)
        except json.JSONDecodeError:
            botones = []

        try:
            response = supabase.table("bot_data").update({
                "palabras_clave": palabras_clave,
                "contenido": nuevo_contenido,
                "categoria": nueva_categoria,
                "botones": botones
            }).eq("id", clave).execute()
            if not response.data:
                print(f"❌ Error al editar respuesta: {not response.data}")
                flash("❌ Error al editar respuesta", "danger")
            else:
                flash("✅ Respuesta actualizada correctamente", "success")
        except Exception as e:
            print(f"❌ Error al editar respuesta: {str(e)}")
            flash("❌ Error al editar respuesta", "danger")

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
    try:
        response = supabase.table("bot_data").delete().eq("id", clave).execute()
        if not response.data:
            print(f"❌ Error al eliminar respuesta: {not response.data}")
            flash("❌ Error al eliminar respuesta", "danger")
        else:
            flash("✅ Respuesta eliminada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al eliminar respuesta: {str(e)}")
        flash("❌ Error al eliminar respuesta", "danger")

    return redirect(url_for('respuestas.mostrar_respuestas'))
