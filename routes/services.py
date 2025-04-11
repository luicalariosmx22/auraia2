from flask import request, flash, redirect, url_for, jsonify
from .utils import cargar_json, guardar_json, normalizar_numero
from datetime import datetime

CONTACTOS_INFO = "contactos_info.json"
ETIQUETAS_DISPONIBLES = "etiquetas.json"

def obtener_timestamp_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def agregar_contacto_service(request):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        numero = request.form.get('numero', '').strip()
        etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

        if not nombre or not numero:
            flash('❌ Nombre y número son obligatorios', 'error')
            return redirect(url_for('panel_chat.agregar_contacto'))

        numero = normalizar_numero(numero)
        contactos_info = cargar_json(CONTACTOS_INFO, {})

        if numero in contactos_info:
            flash('❌ El número ya está registrado', 'error')
        else:
            contactos_info[numero] = {
                "nombre": nombre,
                "ia_activada": True,
                "etiquetas": etiquetas,
                "fecha_registro": obtener_timestamp_actual()
            }
            guardar_json(CONTACTOS_INFO, contactos_info)
            flash('✅ Contacto agregado correctamente', 'success')
            return redirect(url_for('panel_chat.panel_chat'))

    return render_template('agregar_contacto.html', 
                          etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []))

def editar_contacto_service(numero, request):
    contactos_info = cargar_json(CONTACTOS_INFO, {})
    contacto = contactos_info.get(numero)

    if not contacto:
        flash('❌ Contacto no encontrado', 'error')
        return redirect(url_for('panel_chat.panel_chat'))

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevas_etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]

        if nuevo_nombre:
            contacto['nombre'] = nuevo_nombre
        contacto['etiquetas'] = nuevas_etiquetas

        guardar_json(CONTACTOS_INFO, contactos_info)
        flash('✅ Contacto actualizado', 'success')
        return redirect(url_for('panel_chat.panel_chat', numero=numero))

    return render_template('editar_contacto.html', 
                          contacto=contacto,
                          numero=numero,
                          etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []))

def eliminar_contacto_service(numero):
    contactos_info = cargar_json(CONTACTOS_INFO, {})

    if numero in contactos_info:
        del contactos_info[numero]
        guardar_json(CONTACTOS_INFO, contactos_info)
        flash('✅ Contacto eliminado', 'success')
    else:
        flash('❌ Contacto no encontrado', 'error')

    return redirect(url_for('panel_chat.panel_chat'))

def toggle_ia_service(numero):
    try:
        contactos_info = cargar_json(CONTACTOS_INFO, {})
        numero = normalizar_numero(numero)
        estado_actual = contactos_info.get(numero, {}).get("ia_activada", True)
        nuevo_estado = not estado_actual

        if numero not in contactos_info:
            contactos_info[numero] = {"ia_activada": nuevo_estado}
        else:
            contactos_info[numero]["ia_activada"] = nuevo_estado

        guardar_json(CONTACTOS_INFO, contactos_info)
        flash(f'IA {"activada" if nuevo_estado else "desactivada"} correctamente', 'success')
        return jsonify({"success": True, "nuevo_estado": nuevo_estado})

    except Exception as e:
        flash(f'Error al cambiar estado de IA: {str(e)}', 'error')
        return jsonify({"success": False, "error": str(e)}), 500
