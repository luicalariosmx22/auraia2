# Archivo: utils/meta_sync.py ✅

import os
import requests
from twilio.rest import Client
from supabase import create_client
from datetime import datetime, timedelta

# 🚀 Variables desde Railway
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_WHATSAPP_NUMBER')  # 👈 este es el que usarás para WhatsApp
DESTINO = os.getenv('NORA_NUMERO')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

GRAPH_URL = os.getenv('GRAPH_URL')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
    estado_desc = ESTADOS_MAPA.get(nuevo_estado, f'❓ Desconocido ({nuevo_estado})')
    mensaje = (
        f"🔔 *Cambio detectado en cuenta publicitaria*\n\n"
        f"*Nombre:* {nombre_cliente}\n"
        f"*Nuevo estado:* {estado_desc}"
    )
    twilio_client.messages.create(
        body=mensaje,
        from_=f'whatsapp:{TWILIO_FROM}',
        to=f'whatsapp:{normalizar_numero(DESTINO)}'
    )

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

print("🚀 [Meta Sync] La sincronización comenzó correctamente...")

def sincronizar_datos_ads():
    cuentas = supabase.table("meta_ads_cuentas").select("*").execute().data
    print(f"🔍 Revisando {len(cuentas)} cuentas publicitarias encontradas...")

    for cuenta in cuentas:
        id_cuenta = cuenta["id_cuenta_publicitaria"]
        nombre_cliente = cuenta["nombre_cliente"]
        estado_anterior = cuenta.get("estado_actual", None)
        ultima_notificacion = cuenta.get("ultima_notificacion", None)  # Nueva columna para track de última alerta

        print(f"➡️ Cuenta: {nombre_cliente} | Estado anterior: {estado_anterior}")

        nuevo_estado = obtener_estado_cuenta(id_cuenta)

        if nuevo_estado is None:
            print(f"⚠️ No se pudo obtener el estado para la cuenta {id_cuenta}.")
            continue

        print(f"➡️ Cuenta: {nombre_cliente} | Estado nuevo: {nuevo_estado}")

        ahora = datetime.utcnow()

        if nuevo_estado != estado_anterior:
            # Hubo cambio de estado → actualizamos y notificamos
            print(f"📲 Enviando WhatsApp por cambio de estado en {nombre_cliente} a {nuevo_estado}")
            enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
            supabase.table("meta_ads_cuentas").update({
                "estado_actual": nuevo_estado,
                "ultima_notificacion": ahora.isoformat()
            }).eq("id_cuenta_publicitaria", id_cuenta).execute()

        elif int(nuevo_estado) == 3:
            # Estado rojo persistente: revisa si pasaron más de 24h desde la última notificación
            if ultima_notificacion:
                ultima_dt = datetime.strptime(ultima_notificacion, "%Y-%m-%dT%H:%M:%S")
                if ahora - ultima_dt >= timedelta(hours=24):
                    print(f"📲 Reenvío (24h) por estado rojo persistente para {nombre_cliente}")
                    enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
                    supabase.table("meta_ads_cuentas").update({
                        "ultima_notificacion": ahora.isoformat()
                    }).eq("id_cuenta_publicitaria", id_cuenta).execute()
            else:
                # Por si no hay registro previo (primer rojo)
                print(f"📲 Primera notificación de estado rojo para {nombre_cliente}")
                enviar_alerta_estado(nombre_cliente, int(nuevo_estado))
                supabase.table("meta_ads_cuentas").update({
                    "ultima_notificacion": ahora.isoformat()
                }).eq("id_cuenta_publicitaria", id_cuenta).execute()

    print("✅ [Meta Sync] Sincronización finalizada.")

if __name__ == "__main__":
    sincronizar_datos_ads()
