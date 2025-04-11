import json
import os
from datetime import datetime

CONTACTOS_ARCHIVO = "contactos_data.json"

# Función para obtener los datos de un contacto
def obtener_datos_contacto(numero):
    if os.path.exists(CONTACTOS_ARCHIVO):
        with open(CONTACTOS_ARCHIVO, 'r', encoding='utf-8') as f:
            try:
                contactos = json.load(f)
            except json.JSONDecodeError:
                contactos = {}

    else:
        contactos = {}

    # Si el número no está en los contactos, lo inicializamos con valores predeterminados
    if numero not in contactos:
        contactos[numero] = {
            "nombre": "",
            "foto_perfil": "",
            "ia_activada": True,
            "primer_mensaje": datetime.now().isoformat(),
            "ultimo_mensaje": datetime.now().isoformat(),
            "cantidad_mensajes": 0,
            "etiquetas": []
        }

    return contactos

# Función para actualizar los datos de un contacto
def actualizar_datos_contacto(numero, nombre=None, foto_perfil=None, ia_activada=None, etiquetas=None):
    # Obtener los datos actuales
    contactos = obtener_datos_contacto(numero)

    # Actualizar los valores
    if nombre:
        contactos[numero]["nombre"] = nombre
    if foto_perfil:
        contactos[numero]["foto_perfil"] = foto_perfil
    if ia_activada is not None:
        contactos[numero]["ia_activada"] = ia_activada
    if etiquetas:
        contactos[numero]["etiquetas"] = etiquetas

    # Actualizar la cantidad de mensajes y las fechas de los mensajes
    contactos[numero]["cantidad_mensajes"] += 1
    contactos[numero]["ultimo_mensaje"] = datetime.now().isoformat()

    # Si es el primer mensaje, actualizar la fecha del primer mensaje
    if contactos[numero]["cantidad_mensajes"] == 1:
        contactos[numero]["primer_mensaje"] = datetime.now().isoformat()

    # Guardar los datos actualizados en el archivo
    with open(CONTACTOS_ARCHIVO, 'w', encoding='utf-8') as f:
        json.dump(contactos, f, ensure_ascii=False, indent=2)
