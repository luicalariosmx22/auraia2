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
        print("🔍 Cargando etiquetas desde la tabla 'etiquetas'...")
        response = supabase.table("etiquetas").select("*").execute()
        if not response.data:
            print("⚠️ No se encontraron etiquetas.")
            return []
        etiquetas = [e["nombre"] for e in response.data]
        print(f"✅ Etiquetas cargadas: {etiquetas}")
        return etiquetas
    except Exception as e:
        print(f"❌ Error al cargar etiquetas: {str(e)}")
        return []

def agregar_contacto_service(request):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        numero = request.form.get('numero', '').strip()
        etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

        print(f"🔍 Datos recibidos para agregar contacto: Nombre: {nombre}, Número: {numero}, Etiquetas: {etiquetas}")

        if not nombre or not numero:
            flash('❌ Nombre y número son obligatorios', 'error')
            return redirect(url_for('panel_chat.agregar_contacto'))

        numero = normalizar_numero(numero)

        try:
            print(f"🔍 Verificando si el contacto ya existe: {numero}")
            response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
            if response.data:
                print("⚠️ El número ya está registrado.")
                flash('❌ El número ya está registrado', 'error')
                return redirect(url_for('panel_chat.agregar_contacto'))

            print(f"🔍 Insertando nuevo contacto: {nombre}, {numero}")
            response = supabase.table("contactos").insert({
                "telefono": numero,
                "nombre": nombre,
                "ia_activada": True,
                "etiquetas": etiquetas,
                "fecha_registro": obtener_timestamp_actual()
            }).execute()
            if not response.data:
                print("⚠️ No se pudo agregar el contacto.")
                flash('❌ Error al agregar contacto', 'error')
            else:
                print(f"✅ Contacto agregado correctamente: {response.data}")
                flash('✅ Contacto agregado correctamente', 'success')
        except Exception as e:
            print(f"❌ Error al agregar contacto: {str(e)}")
            flash('❌ Error al agregar contacto', 'error')

        return redirect(url_for('panel_chat.panel_chat'))

    return render_template('agregar_contacto.html', etiquetas_disponibles=cargar_etiquetas())

def editar_contacto_service(numero, request):
    numero = normalizar_numero(numero)
    print(f"🔍 Editando contacto con número: {numero}")

    try:
        print(f"🔍 Buscando contacto en la tabla 'contactos': {numero}")
        response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
        if not response.data:
            print("⚠️ Contacto no encontrado.")
            flash('❌ Contacto no encontrado', 'error')
            return redirect(url_for('panel_chat.panel_chat'))

        contacto = response.data[0]
        print(f"✅ Contacto encontrado: {contacto}")

        if request.method == 'POST':
            nuevo_nombre = request.form.get('nombre', '').strip()
            nuevas_etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

            print(f"🔍 Actualizando contacto: Nombre: {nuevo_nombre}, Etiquetas: {nuevas_etiquetas}")
            response = supabase.table("contactos").update({
                "nombre": nuevo_nombre or contacto["nombre"],
                "etiquetas": nuevas_etiquetas
            }).eq("telefono", numero).execute()
            if not response.data:
                print("⚠️ No se pudo actualizar el contacto.")
                flash('❌ Error al actualizar contacto', 'error')
            else:
                print(f"✅ Contacto actualizado correctamente: {response.data}")
                flash('✅ Contacto actualizado', 'success')

            return redirect(url_for('panel_chat.panel_chat', numero=numero))

        return render_template('editar_contacto.html', contacto=contacto, numero=numero, etiquetas_disponibles=cargar_etiquetas())
    except Exception as e:
        print(f"❌ Error al editar contacto: {str(e)}")
        flash('❌ Error al editar contacto', 'error')
        return redirect(url_for('panel_chat.panel_chat'))

def eliminar_contacto_service(numero):
    numero = normalizar_numero(numero)
    print(f"🔍 Eliminando contacto con número: {numero}")

    try:
        print(f"🔍 Intentando eliminar contacto: {numero}")
        response = supabase.table("contactos").delete().eq("telefono", numero).execute()
        if not response.data:
            print("⚠️ No se pudo eliminar el contacto.")
            flash('❌ Error al eliminar contacto', 'error')
        else:
            print(f"✅ Contacto eliminado correctamente: {response.data}")
            flash('✅ Contacto eliminado', 'success')
    except Exception as e:
        print(f"❌ Error al eliminar contacto: {str(e)}")
        flash('❌ Error al eliminar contacto', 'error')

    return redirect(url_for('panel_chat.panel_chat'))

def toggle_ia_service(numero):
    numero = normalizar_numero(numero)
    print(f"🔍 Cambiando estado de IA para el contacto con número: {numero}")

    try:
        print(f"🔍 Buscando contacto en la tabla 'contactos': {numero}")
        response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
        if not response.data:
            print("⚠️ Contacto no encontrado.")
            flash('❌ Contacto no encontrado', 'error')
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)
        print(f"🔍 Nuevo estado de IA: {'Activado' if nuevo_estado else 'Desactivado'}")

        response = supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", numero).execute()
        if not response.data:
            print("⚠️ No se pudo cambiar el estado de IA.")
            return jsonify({"success": False, "error": "Error al cambiar estado de IA"}), 500

        print(f"✅ Estado de IA cambiado correctamente: {response.data}")
        flash(f'IA {"activada" if nuevo_estado else "desactivada"} correctamente', 'success')
        return jsonify({"success": True, "nuevo_estado": nuevo_estado})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
