# clientes/aura/utils/db/historial.py

from datetime import datetime
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.error_logger import registrar_error

def guardar_en_historial(telefono, mensaje, origen, nombre_nora, tipo="desconocido"):
    """
    Guarda un mensaje en el historial de conversaciones en Supabase.

    Args:
        telefono (str): Número de teléfono del destinatario.
        mensaje (str): Mensaje enviado o recibido.
        origen (str): Número del remitente.
        nombre_nora (str): Nombre de la instancia de Nora.
        tipo (str): Tipo de mensaje (e.g., "recibido", "enviado").

    Returns:
        dict: Resultado de la operación con éxito o error.
    """
    try:
        # Validar datos requeridos
        if not telefono or not mensaje or not origen or not nombre_nora:
            return {"success": False, "error": "Datos insuficientes para guardar en historial"}

        # Normalizar números
        telefono = normalizar_numero(telefono)
        origen = normalizar_numero(origen)

        # Preparar datos para insertar
        data = {
            "telefono": telefono,
            "emisor": origen,
            "mensaje": mensaje,
            "hora": datetime.now().isoformat(),
            "tipo": tipo,
            "nombre_nora": nombre_nora.lower()
        }

        # Insertar en la tabla historial_conversaciones
        response = supabase.table("historial_conversaciones").insert(data).execute()

        # Verificar respuesta de Supabase
        if not response.data:
            print(f"❌ Error al guardar en historial_conversaciones: {response}")
            return {"success": False, "error": "No se pudo guardar en la base de datos"}

        print(f"✅ Historial guardado para {telefono}: {mensaje}")
        return {"success": True, "data": response.data}

    except Exception as e:
        # Registrar error y devolver mensaje estructurado
        registrar_error("historial", f"No se pudo guardar historial: {e}", tipo="Supabase")
        print(f"❌ Error al guardar en historial: {e}")
        return {"success": False, "error": str(e)}
