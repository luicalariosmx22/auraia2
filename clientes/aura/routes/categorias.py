from flask import Blueprint, request, redirect, url_for, render_template
from supabase import create_client
from dotenv import load_dotenv
from utils.config import login_requerido
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias')
@login_requerido
def mostrar_categorias():
    try:
        response = supabase.table("categorias").select("*").execute()
        if response.error:
            print(f"❌ Error al cargar categorías: {response.error}")
            categorias = []
        else:
            categorias = [cat["nombre"] for cat in response.data]
    except Exception as e:
        print(f"❌ Error al cargar categorías: {str(e)}")
        categorias = []

    return render_template('categorias.html', categorias=categorias)

@categorias_bp.route('/categorias/agregar', methods=['POST'])
@login_requerido
def agregar_categoria():
    nueva = request.form['nueva_categoria'].strip()

    if nueva:
        try:
            response = supabase.table("categorias").insert({"nombre": nueva}).execute()
            if response.error:
                print(f"❌ Error al agregar categoría: {response.error}")
        except Exception as e:
            print(f"❌ Error al agregar categoría: {str(e)}")

    return redirect(url_for('categorias.mostrar_categorias'))

@categorias_bp.route('/categorias/eliminar/<categoria>', methods=['POST'])
@login_requerido
def eliminar_categoria(categoria):
    categoria = categoria.strip()

    try:
        response = supabase.table("categorias").delete().eq("nombre", categoria).execute()
        if response.error:
            print(f"❌ Error al eliminar categoría: {response.error}")
    except Exception as e:
        print(f"❌ Error al eliminar categoría: {str(e)}")

    return redirect(url_for('categorias.mostrar_categorias'))

@categorias_bp.route('/categorias/editar/<nombre>', methods=['GET', 'POST'])
@login_requerido
def editar_categoria(nombre):
    nombre = nombre.strip()

    if request.method == 'POST':
        nuevo_nombre = request.form['nuevo_nombre'].strip()

        if nuevo_nombre and nuevo_nombre != nombre:
            # Actualizar la categoría en la tabla `categorias`
            try:
                response = supabase.table("categorias").update({"nombre": nuevo_nombre}).eq("nombre", nombre).execute()
                if response.error:
                    print(f"❌ Error al actualizar categoría: {response.error}")
            except Exception as e:
                print(f"❌ Error al actualizar categoría: {str(e)}")

            # Actualizar las respuestas en la tabla `bot_data`
            try:
                response = supabase.table("bot_data").select("*").execute()
                if response.error:
                    print(f"❌ Error al cargar datos del bot: {response.error}")
                else:
                    data = response.data
                    for item in data:
                        if item.get("categoria") == nombre:
                            item["categoria"] = nuevo_nombre
                            supabase.table("bot_data").update({"categoria": nuevo_nombre}).eq("id", item["id"]).execute()
            except Exception as e:
                print(f"❌ Error al actualizar datos del bot: {str(e)}")

        return redirect(url_for('categorias.mostrar_categorias'))

    return render_template('editar_categoria.html', nombre=nombre)
