from flask import request, flash, redirect, url_for, jsonify, render_template
from supabase import create_client
from dotenv import load_dotenv
from .utils import normalizar_numero
from datetime import datetime
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_timestamp_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cargar_etiquetas():
    try:
        response = supabase.table("etiquetas").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar etiquetas: {not response.data}")
            return []
        return [e["nombre"] for e in response.data]
    except Exception as e:
        print(f"❌ Error al cargar etiquetas: {str(e)}")
        return []

def agregar_contacto_service(request):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        numero = request.form.get('numero', '').strip()
        etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

        if not nombre or not numero:
            flash('❌ Nombre y número son obligatorios', 'error')
            return redirect(url_for('panel_chat.agregar_contacto'))

        numero = normalizar_numero(numero)

        try:
            # Verificar si el contacto ya existe
            response = supabase.table("contactos").select("*").eq("numero", numero).execute()
            if response.data:
                flash('❌ El número ya está registrado', 'error')
                return redirect(url_for('panel_chat.agregar_contacto'))

            # Insertar nuevo contacto
            response = supabase.table("contactos").insert({
                "numero": numero,
                "nombre": nombre,
                "ia_activada": True,
                "etiquetas": etiquetas,
                "fecha_registro": obtener_timestamp_actual()
            }).execute()
            if not response.data:
                print(f"❌ Error al agregar contacto: {not response.data}")
                flash('❌ Error al agregar contacto', 'error')
            else:
                flash('✅ Contacto agregado correctamente', 'success')
        except Exception as e:
            print(f"❌ Error al agregar contacto: {str(e)}")
            flash('❌ Error al agregar contacto', 'error')

        return redirect(url_for('panel_chat.panel_chat'))

    return render_template('agregar_contacto.html', etiquetas_disponibles=cargar_etiquetas())

def editar_contacto_service(numero, request):
    numero = normalizar_numero(numero)

    try:
        # Obtener contacto desde Supabase
        response = supabase.table("contactos").select("*").eq("numero", numero).execute()
        if not response.data:
            flash('❌ Contacto no encontrado', 'error')
            return redirect(url_for('panel_chat.panel_chat'))

        contacto = response.data[0]

        if request.method == 'POST':
            nuevo_nombre = request.form.get('nombre', '').strip()
            nuevas_etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

            # Actualizar contacto
            response = supabase.table("contactos").update({
                "nombre": nuevo_nombre or contacto["nombre"],
                "etiquetas": nuevas_etiquetas
            }).eq("numero", numero).execute()
            if not response.data:
                print(f"❌ Error al actualizar contacto: {not response.data}")
                flash('❌ Error al actualizar contacto', 'error')
            else:
                flash('✅ Contacto actualizado', 'success')

            return redirect(url_for('panel_chat.panel_chat', numero=numero))

        return render_template('editar_contacto.html', contacto=contacto, numero=numero, etiquetas_disponibles=cargar_etiquetas())
    except Exception as e:
        print(f"❌ Error al editar contacto: {str(e)}")
        flash('❌ Error al editar contacto', 'error')
        return redirect(url_for('panel_chat.panel_chat'))

def eliminar_contacto_service(numero):
    numero = normalizar_numero(numero)

    try:
        # Eliminar contacto desde Supabase
        response = supabase.table("contactos").delete().eq("numero", numero).execute()
        if not response.data:
            print(f"❌ Error al eliminar contacto: {not response.data}")
            flash('❌ Error al eliminar contacto', 'error')
        else:
            flash('✅ Contacto eliminado', 'success')
    except Exception as e:
        print(f"❌ Error al eliminar contacto: {str(e)}")
        flash('❌ Error al eliminar contacto', 'error')

    return redirect(url_for('panel_chat.panel_chat'))

def toggle_ia_service(numero):
    numero = normalizar_numero(numero)

    try:
        # Obtener contacto desde Supabase
        response = supabase.table("contactos").select("*").eq("numero", numero).execute()
        if not response.data:
            flash('❌ Contacto no encontrado', 'error')
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)

        # Actualizar estado de IA
        response = supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("numero", numero).execute()
        if not response.data:
            print(f"❌ Error al cambiar estado de IA: {not response.data}")
            return jsonify({"success": False, "error": "Error al cambiar estado de IA"}), 500

        flash(f'IA {"activada" if nuevo_estado else "desactivada"} correctamente', 'success')
        return jsonify({"success": True, "nuevo_estado": nuevo_estado})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
