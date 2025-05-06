# Archivo: utils/meta_sync.py ✅

import os
import requests
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase  # ✅ Ya corregido
from clientes.aura.utils.whatsapp_sender import enviar_mensaje_whatsapp  # ✅ Ya corregido

# 🚀 Variables desde Railway
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_WHATSAPP_NUMBER')  # 👈 este es el que usarás para WhatsApp
DESTINO = os.getenv('NORA_NUMERO')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

GRAPH_URL = os.getenv('GRAPH_URL')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

supabase = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Mapeamos los estados a su significado
ESTADOS_MAPA = {
    1: '🟢 Activa',
    2: '🟡 Pausada',
    3: '🔴 Cerrada/Inhabilitada',
    7: '⚠️ En Revisión'
}

def normalizar_numero(numero):
    """
    Normaliza el número para WhatsApp:
    - Si ya empieza con '+', lo regresa igual.
    - Si es un número mexicano de 10 dígitos, le agrega +521.
    - Si no, le agrega un '+' al inicio.
    """
    if numero.startswith("+"):
        return numero
    else:
        if len(numero) == 10:
            return f"+521{numero}"
        return f"+{numero}"

def enviar_alerta_estado(nombre_cliente, nuevo_estado):
    """
    Enviar alerta de cambio de estado usando enviar_mensaje_whatsapp.
    """
    estado_desc = ESTADOS_MAPA.get(int(nuevo_estado), f'❓ Desconocido ({nuevo_estado})')
    mensaje = (
        f"🔔 *Cambio detectado en cuenta publicitaria*\n\n"
        f"*Nombre:* {nombre_cliente}\n"
        f"*Nuevo estado:* {estado_desc}"
    )
    try:
        enviar_mensaje_whatsapp(DESTINO, mensaje)
        print(f"✅ WhatsApp enviado a {DESTINO} para '{nombre_cliente}'.")
    except Exception as e:
        print(f"❌ Error enviando WhatsApp para '{nombre_cliente}': {e}")

def obtener_estado_cuenta(cuenta_id):
    print(f"[Meta] Consultando cuenta publicitaria {cuenta_id}")
    try:
        url = f"{GRAPH_URL}/act_{cuenta_id}?fields=account_status&access_token={META_ACCESS_TOKEN}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        estado = str(data.get("account_status"))
        print(f"[Meta] Estado recibido para {cuenta_id}: {estado}")
        return estado
    except requests.exceptions.RequestException as e:
        print(f"❌ [Meta Ads] Error al consultar estado de {cuenta_id}: {e}")
        if e.response is not None:
            print(f"⚠️ Respuesta completa: {e.response.text}")
        return None

def supabase_update_estado(nombre_cliente, nuevo_estado, fecha_notificacion):
    """
    Actualiza en Supabase el estado y la última notificación de una cuenta publicitaria.
    """
    try:
        print(f"🔄 [Supabase] Actualizando estado para '{nombre_cliente}' a {nuevo_estado} en {fecha_notificacion}")
        data = {
            "estado_actual": nuevo_estado,
            "ultima_notificacion": fecha_notificacion.strftime("%Y-%m-%dT%H:%M:%S")
        }
        response = supabase.table("meta_ads_cuentas").update(data).eq("nombre_cliente", nombre_cliente).execute()
        print(f"✅ [Supabase] Estado actualizado correctamente para '{nombre_cliente}'.")
    except Exception as e:
        print(f"❌ [Supabase] Error al actualizar estado para '{nombre_cliente}': {e}")

print("🚀 [Meta Sync] La sincronización comenzó correctamente...")

def sincronizar_datos_ads():
    """
    Sincroniza los datos de las cuentas publicitarias y envía notificaciones si hay cambios.
    """
    cuentas = supabase.table("meta_ads_cuentas").select("*").execute().data
    print("🚀 [Meta Sync] Iniciando la sincronización de cuentas publicitarias...")
    print(f"🔍 Revisando {len(cuentas)} cuentas publicitarias encontradas...")

    for cuenta in cuentas:
        id_cuenta = cuenta["id_cuenta_publicitaria"]
        nombre_cliente = cuenta["nombre_cliente"]
        estado_anterior = cuenta.get("estado_actual", None)
        ultima_notificacion = cuenta.get("ultima_notificacion", None)

        print(f"➡️ Cuenta: {nombre_cliente} | Antes: {estado_anterior}")

        nuevo_estado = obtener_estado_cuenta(id_cuenta)

        if nuevo_estado is None:
            print(f"⚠️ No se pudo obtener el estado para la cuenta {id_cuenta}.")
            continue

        print(f"➡️ Cuenta: {nombre_cliente} | Ahora: {nuevo_estado}")

        ahora = datetime.utcnow()

        if nuevo_estado != estado_anterior:
            if int(nuevo_estado) == 1 and int(estado_anterior) == 3:
                print(f"✅ La cuenta '{nombre_cliente}' volvió a estar activa (de rojo a verde).")
                enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
            else:
                print(f"📲 Cambio detectado en {nombre_cliente}: ahora está en estado {nuevo_estado}")
                enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
            supabase_update_estado(nombre_cliente, nuevo_estado, ahora)

        elif int(nuevo_estado) == 3:
            if ultima_notificacion:
                ultima_dt = datetime.strptime(ultima_notificacion, "%Y-%m-%dT%H:%M:%S")
                if ahora - ultima_dt >= timedelta(hours=24):
                    print(f"📲 Reenvío (24h) estado rojo persistente para {nombre_cliente}")
                    enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
                    supabase_update_estado(nombre_cliente, nuevo_estado, ahora)
            else:
                print(f"📲 Primer aviso rojo para {nombre_cliente}")
                enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
                supabase_update_estado(nombre_cliente, nuevo_estado, ahora)

    print("✅ [Meta Sync] Sincronización completada.")

if __name__ == "__main__":
    sincronizar_datos_ads()
