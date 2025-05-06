# Archivo: clientes/aura/utils/whatsapp_utils.py

"""
✅ FUNCIONES WHATSAPP
Este módulo guarda mensajes en Supabase para ser enviados después (via trigger o función aparte).
"""

from clientes.aura.utils.supabase_utils import get_supabase_client

def enviar_mensaje_whatsapp(numero_destino, mensaje, cuenta_id=None):
    """
    Guardar un mensaje pendiente de enviar en Supabase.
    :param numero_destino: Ejemplo '+521XXXXXXXXXX'
    :param mensaje: Texto del mensaje
    :param cuenta_id: ID de la cuenta publicitaria (opcional)
    """
    supabase = get_supabase_client()
    try:
        data = {
            'numero_destino': numero_destino,
            'mensaje': mensaje,
            'estado': 'pendiente',  # Estado inicial
            'cuenta_id': cuenta_id
        }
        supabase.table('whatsapp_mensajes_pendientes').insert(data).execute()
        print(f"✅ Mensaje guardado en cola para {numero_destino}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar mensaje para {numero_destino}: {str(e)}")
        return False
