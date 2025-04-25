# clientes/aura/utils/db/historial.py

from datetime import datetime
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.error_logger import registrar_error

def guardar_en_historial(telefono, mensaje, origen, nombre_nora, tipo="mensaje", nombre=None):
    """
    Guarda un mensaje en el historial de conversaciones en Supabase.

    Args:
        telefono (str): Número de teléfono del destinatario.
        mensaje (str): Mensaje enviado o recibido.
        origen (str): Número del remitente.
        nombre_nora (str): Nombre de la instancia de Nora.
        tipo (str): Tipo de mensaje (e.g., "recibido", "enviado").
        nombre (str, optional): Nombre del remitente o destinatario.

    Returns:
        dict: Resultado de la operación con éxito o error.
    """
    try:
        # Normalizar números
        telefono = normalizar_numero(telefono)
        origen = normalizar_numero(origen)

        # Preparar datos para insertar
        nuevo_mensaje = {
            "telefono": telefono,
            "mensaje": mensaje,
            "origen": origen,
            "nombre_nora": nombre_nora.lower(),
            "tipo": tipo,
            "nombre": nombre,
            "hora": datetime.now().isoformat()        }

        # Eliminar claves con valor None
        nuevo_mensaje = {k: v for k, v in nuevo_mensaje.items() if v is not None}

        # Insertar en la tabla historial_conversaciones
        response = supabase.table("historial_conversaciones").insert(nuevo_mensaje).execute()

        # Verificar respuesta de Supabase
        if not response.data:
            print("⚠️ No se pudo registrar en el historial.")
            return {"success": False, "error": "No se pudo guardar en la base de datos"}

        print(f"✅ Historial registrado: {nuevo_mensaje}")
        return {"success": True, "data": response.data}

    except Exception as e:
        # Registrar error y devolver mensaje estructurado
        registrar_error("historial", f"No se pudo guardar historial: {e}", tipo="Supabase")
        print(f"❌ Error al guardar en historial: {e}")
        return {"success": False, "error": str(e)}

def guardar_en_historial_batch(mensajes):
    """
    Guarda múltiples mensajes en el historial de la base de datos.
    """
    try:
        # Lógica para guardar los mensajes en la base de datos
        for mensaje in mensajes:
            supabase.table("historial_conversaciones").insert(mensaje).execute()
        print("✅ Mensajes guardados en el historial.")
    except Exception as e:
        print(f"❌ Error al guardar mensajes en el historial: {e}")