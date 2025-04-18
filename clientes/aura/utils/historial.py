# clientes/aura/utils/db/historial.py

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
    :param ia_activada: Estado de la IA para el contacto (solo para contactos, no historial).
    :param etiquetas: Etiquetas asociadas al contacto.
    """

    print(f"🔍 Iniciando guardado en historial para {remitente}...")

    # ✅ Guardar solo campos válidos en historial_conversaciones
    try:
        historial_entry = {
            "telefono": remitente,
            "mensaje": mensaje,
            "emisor": tipo,
            "timestamp": datetime.now().isoformat(),
            "hora": datetime.now().strftime("%H:%M"),
            "nombre_nora": "aura"  # Ajusta según sea dinámico si lo necesitas
        }
        print(f"📋 Datos a guardar en historial_conversaciones: {historial_entry}")

        response = supabase.table("historial_conversaciones").insert(historial_entry).execute()
        if not response.data:
            print(f"❌ Error al guardar en historial_conversaciones: {response}")
        else:
            print(f"✅ Mensaje guardado en historial_conversaciones: {historial_entry}")
    except Exception as e:
        print(f"❌ Error al guardar en historial_conversaciones: {str(e)}")

    # ✅ Actualizar o crear contacto
    try:
        print(f"🔍 Buscando contacto existente para {remitente}...")
        response = supabase.table("contactos").select("*").eq("numero", remitente).execute()
        contacto = response.data[0] if response.data else None

        if not contacto:
            print(f"⚠️ Contacto no encontrado. Creando nuevo contacto para {remitente}...")
            nuevo_contacto = {
                "numero": remitente,
                "nombre": nombre,
                "ia_activada": ia_activada,
                "etiquetas": etiquetas,
                "mensaje_count": 1,
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat()
            }
            print(f"📋 Datos del nuevo contacto: {nuevo_contacto}")
            response = supabase.table("contactos").insert(nuevo_contacto).execute()
            if not response.data:
                print(f"❌ Error al crear nuevo contacto: {response}")
            else:
                print(f"✅ Nuevo contacto creado: {nuevo_contacto}")
        else:
            print(f"✅ Contacto encontrado. Actualizando información para {remitente}...")
            contacto_actualizado = {
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_count": contacto.get("mensaje_count", 0) + 1,
                "ia_activada": ia_activada
            }
            print(f"📋 Datos a actualizar en contacto: {contacto_actualizado}")
            response = supabase.table("contactos").update(contacto_actualizado).eq("numero", remitente).execute()
            if not response.data:
                print(f"❌ Error al actualizar contacto: {response}")
            else:
                print(f"✅ Contacto actualizado: {contacto_actualizado}")
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")
