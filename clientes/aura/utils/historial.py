from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_en_historial(remitente, mensaje, tipo="recibido", nombre=None, ia_activada=True, etiquetas=[]):
    """
    Guarda un mensaje en el historial de conversaciones y actualiza la información del contacto en Supabase.
    :param remitente: Número del remitente.
    :param mensaje: Contenido del mensaje.
    :param tipo: Tipo de mensaje ('recibido' o 'enviado').
    :param nombre: Nombre del remitente (opcional).
    :param ia_activada: Estado de la IA para el contacto.
    :param etiquetas: Etiquetas asociadas al contacto.
    """
    # Guardar en la tabla `historial_conversaciones`
    try:
        historial_entry = {
            "telefono": remitente,
            "mensaje": mensaje,
            "tipo": tipo,
            "timestamp": datetime.now().isoformat(),
            "ia_activada": ia_activada,
            **({"nombre": nombre} if nombre else {})
        }
        response = supabase.table("historial_conversaciones").insert(historial_entry).execute()
        if not response.data:
            print(f"❌ Error al guardar en historial_conversaciones: {not response.data}")
        else:
            print(f"✅ Mensaje guardado en historial_conversaciones: {historial_entry}")
    except Exception as e:
        print(f"❌ Error al guardar en historial_conversaciones: {str(e)}")

    # Actualizar la tabla `contactos`
    try:
        # Obtener el contacto actual
        response = supabase.table("contactos").select("*").eq("numero", remitente).execute()
        if not response.data:
            print(f"❌ Error al obtener contacto: {not response.data}")
            return

        contacto = response.data[0] if response.data else None

        if not contacto:
            # Crear un nuevo contacto si no existe
            nuevo_contacto = {
                "numero": remitente,
                "nombre": nombre,
                "ia_activada": ia_activada,
                "etiquetas": etiquetas,
                "mensaje_count": 1,
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat()
            }
            response = supabase.table("contactos").insert(nuevo_contacto).execute()
            if not response.data:
                print(f"❌ Error al crear nuevo contacto: {not response.data}")
            else:
                print(f"✅ Nuevo contacto creado: {nuevo_contacto}")
        else:
            # Actualizar el contacto existente
            contacto_actualizado = {
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_count": contacto.get("mensaje_count", 0) + 1,
                "ia_activada": ia_activada
            }
            response = supabase.table("contactos").update(contacto_actualizado).eq("numero", remitente).execute()
            if not response.data:
                print(f"❌ Error al actualizar contacto: {not response.data}")
            else:
                print(f"✅ Contacto actualizado: {contacto_actualizado}")
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")