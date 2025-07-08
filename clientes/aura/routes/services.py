from flask import request, flash, redirect, url_for, jsonify, render_template
from supabase import create_client
from dotenv import load_dotenv
from .utils import normalizar_numero
from datetime import datetime
import os
import uuid

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
        response = supabase.table("etiquetas").select("id, nombre, color").eq("activa", True).execute()
        if not response.data:
            print("⚠️ No se encontraron etiquetas.")
            return []
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar etiquetas: {str(e)}")
        return []

def obtener_etiquetas_asignadas(contacto_id):
    try:
        response = supabase.table("contacto_etiquetas").select("etiqueta_id").eq("contacto_id", contacto_id).execute()
        return [r["etiqueta_id"] for r in response.data] if response.data else []
    except Exception as e:
        print(f"❌ Error al obtener etiquetas del contacto: {str(e)}")
        return []

def asignar_etiquetas(contacto_id, etiquetas_ids, nombre_nora):
    try:
        for etiqueta_id in etiquetas_ids:
            supabase.table("contacto_etiquetas").insert({
                "id": str(uuid.uuid4()),
                "contacto_id": contacto_id,
                "etiqueta_id": etiqueta_id,
                "nombre_nora": nombre_nora
            }).execute()
    except Exception as e:
        print(f"❌ Error al asignar etiquetas: {str(e)}")

def remover_etiquetas(contacto_id):
    try:
        supabase.table("contacto_etiquetas").delete().eq("contacto_id", contacto_id).execute()
    except Exception as e:
        print(f"❌ Error al eliminar etiquetas existentes: {str(e)}")

def agregar_contacto_service(request):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        numero = request.form.get('numero', '').strip()
        etiquetas = request.form.getlist('etiquetas')
        nombre_nora = request.form.get('nombre_nora', '')

        print(f"🔍 Datos recibidos para agregar contacto: Nombre: {nombre}, Número: {numero}, Etiquetas: {etiquetas}")

        if not nombre or not numero:
            flash('❌ Nombre y número son obligatorios', 'error')
            return redirect(url_for('panel_chat.agregar_contacto'))

        numero = normalizar_numero(numero)

        try:
            response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
            if response.data:
                flash('❌ El número ya está registrado', 'error')
                return redirect(url_for('panel_chat.agregar_contacto'))

            contacto_data = {
                "telefono": numero,
                "nombre": nombre,
                "ia_activada": True,
                "fecha_registro": obtener_timestamp_actual(),
                "nombre_nora": nombre_nora
            }
            contacto_response = supabase.table("contactos").insert(contacto_data).execute()
            if contacto_response.data:
                contacto_id = contacto_response.data[0]["id"]
                asignar_etiquetas(contacto_id, etiquetas, nombre_nora)
                flash('✅ Contacto agregado correctamente', 'success')
            else:
                flash('❌ Error al agregar contacto', 'error')
        except Exception as e:
            print(f"❌ Error al agregar contacto: {str(e)}")
            flash('❌ Error al agregar contacto', 'error')

        return redirect(url_for('panel_chat.panel_chat'))

    return render_template('agregar_contacto.html', etiquetas_disponibles=cargar_etiquetas())

def editar_contacto_service(numero, request):
    numero = normalizar_numero(numero)

    try:
        response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
        if not response.data:
            flash('❌ Contacto no encontrado', 'error')
            return redirect(url_for('panel_chat.panel_chat'))

        contacto = response.data[0]
        contacto_id = contacto["id"]

        if request.method == 'POST':
            # Crear el diccionario con los datos actualizados
            update_data = {
                "nombre": request.form.get("nombre", contacto.get("nombre", "")).strip(),
                "correo": request.form.get("correo", contacto.get("correo", "")).strip(),
                "empresa": request.form.get("empresa", contacto.get("empresa", "")).strip(),
                "rfc": request.form.get("rfc", contacto.get("rfc", "")).strip(),
                "direccion": request.form.get("direccion", contacto.get("direccion", "")).strip(),
                "ciudad": request.form.get("ciudad", contacto.get("ciudad", "")).strip(),
                "cumpleanos": request.form.get("cumpleanos", contacto.get("cumpleanos", "")),
                "notas": request.form.get("notas", contacto.get("notas", "")).strip(),
            }

            # Actualizar los datos del contacto
            supabase.table("contactos").update(update_data).eq("telefono", numero).execute()

            # Manejar etiquetas
            nuevas_etiquetas = request.form.getlist('etiquetas')
            nombre_nora = contacto.get("nombre_nora", "")
            remover_etiquetas(contacto_id)
            asignar_etiquetas(contacto_id, nuevas_etiquetas, nombre_nora)

            flash('✅ Contacto actualizado', 'success')
            return redirect(url_for('panel_chat.panel_chat', numero=numero))

        etiquetas_actuales = obtener_etiquetas_asignadas(contacto_id)
        return render_template('editar_contacto.html', contacto=contacto, numero=numero, etiquetas_disponibles=cargar_etiquetas(), etiquetas_asignadas=etiquetas_actuales)
    except Exception as e:
        print(f"❌ Error al editar contacto: {str(e)}")
        flash('❌ Error al editar contacto', 'error')
        return redirect(url_for('panel_chat.panel_chat'))

def eliminar_contacto_service(numero):
    numero = normalizar_numero(numero)
    try:
        response = supabase.table("contactos").delete().eq("telefono", numero).execute()
        if response.data:
            flash('✅ Contacto eliminado', 'success')
        else:
            flash('❌ Error al eliminar contacto', 'error')
    except Exception as e:
        print(f"❌ Error al eliminar contacto: {str(e)}")
        flash('❌ Error al eliminar contacto', 'error')

    return redirect(url_for('panel_chat.panel_chat'))

def toggle_ia_service(numero):
    numero = normalizar_numero(numero)
    try:
        response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
        if not response.data:
            flash('❌ Contacto no encontrado', 'error')
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)

        response = supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", numero).execute()
        if response.data:
            flash(f'IA {"activada" if nuevo_estado else "desactivada"} correctamente', 'success')
            return jsonify({"success": True, "nuevo_estado": nuevo_estado})
        else:
            return jsonify({"success": False, "error": "No se pudo actualizar estado"}), 500
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500