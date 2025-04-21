# clientes/aura/utils/db/historial.py

from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.normalizador import normalizar_numero
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_en_historial(remitente, mensaje, tipo="recibido", nombre=None, nombre_nora="Nora", ia_activada=True, etiquetas=[]):
    """
    Guarda un mensaje en el historial de conversaciones y actualiza la información del contacto en Supabase.
    """
    if not remitente or not mensaje:
        print("⚠️ El remitente o el mensaje están vacíos. No se puede guardar en el historial.")
        return {"success": False, "error": "Remitente o mensaje vacío"}

    telefono = normalizar_numero(remitente)
    print(f"🔍 Iniciando guardado en historial para {telefono}...")

    try:
        # Guardar en historial de conversaciones
        historial_entry = {
            "telefono": telefono,
            "mensaje": mensaje,
            "emisor": tipo,
            "timestamp": datetime.now().isoformat(),
            "hora": datetime.now().isoformat(),
            "nombre_nora": nombre_nora
        }
        print(f"📋 Datos a guardar en historial_conversaciones: {historial_entry}")

        response = supabase.table("historial_conversaciones").insert(historial_entry).execute()
        if not response.data:
            print(f"❌ Error al guardar en historial_conversaciones: {response}")
            return {"success": False, "error": "Error al guardar en historial"}
        print(f"✅ Mensaje guardado en historial_conversaciones: {historial_entry}")
    except Exception as e:
        print(f"❌ Error al guardar en historial_conversaciones: {str(e)}")
        return {"success": False, "error": str(e)}

    # Actualizar o crear contacto
    try:
        print(f"🔍 Buscando contacto existente para {telefono}...")
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        contacto = response.data[0] if response.data else None

        if not contacto:
            print(f"⚠️ Contacto no encontrado. Creando nuevo contacto para {telefono}...")
            nuevo_contacto = {
                "telefono": telefono,
                "nombre": nombre or "Desconocido",
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
                return {"success": False, "error": "Error al crear nuevo contacto"}
            print(f"✅ Nuevo contacto creado: {nuevo_contacto}")
        else:
            print(f"✅ Contacto encontrado. Actualizando información para {telefono}...")
            contacto_actualizado = {
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_count": contacto.get("mensaje_count", 0) + 1,
                "ia_activada": ia_activada
            }
            print(f"📋 Datos a actualizar en contacto: {contacto_actualizado}")
            response = supabase.table("contactos").update(contacto_actualizado).eq("telefono", telefono).execute()
            if not response.data:
                print(f"❌ Error al actualizar contacto: {response}")
                return {"success": False, "error": "Error al actualizar contacto"}
            print(f"✅ Contacto actualizado: {contacto_actualizado}")
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")
        return {"success": False, "error": str(e)}

    return {"success": True}

# Ejemplo de uso de la función guardar_en_historial
nora_numero = "+123456789"
respuesta = "Hola, ¿cómo estás?"
nombre_nora = "Nora"

guardar_en_historial(
    remitente=nora_numero,
    mensaje=respuesta,
    tipo="enviado",
    nombre=nombre_nora
)
