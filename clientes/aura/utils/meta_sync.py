# Archivo: utils/meta_sync.py ✅

import os
import requests
from twilio.rest import Client
from supabase import create_client

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
        to=f'whatsapp:{DESTINO}'
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
    except Exception as e:
        print(f"[Meta] Error al consultar estado de {cuenta_id}: {e}")
        return None

def sincronizar_datos_ads():
    cuentas = supabase.table("meta_ads_cuentas").select("*").execute().data
    for cuenta in cuentas:
        id_cuenta = cuenta["id_cuenta_publicitaria"]
        estado_anterior = cuenta.get("estado_actual", None)

        print(f"➡️ Revisando cuenta {cuenta['nombre_cliente']} (ID: {id_cuenta})")

        nuevo_estado = obtener_estado_cuenta(id_cuenta)

        if nuevo_estado is None:
            print(f"⚠️ No se pudo obtener el estado para la cuenta {id_cuenta}.")
            continue

        if estado_anterior is not None and nuevo_estado != estado_anterior:
            estado_desc = ESTADOS_MAPA.get(int(nuevo_estado), f"❓ Desconocido ({nuevo_estado})")
            print(f"⚠️ Cambio detectado: {estado_anterior} -> {nuevo_estado} ({estado_desc})")
            enviar_alerta_estado(cuenta["nombre_cliente"], int(nuevo_estado))

        supabase.table("meta_ads_cuentas").update({
            "estado_actual": nuevo_estado,
            "campanas_activas": cuenta.get("campanas_activas", 0),  # Placeholder for actual data
            "anuncios_activos": cuenta.get("anuncios_activos", 0),  # Placeholder for actual data
            "gasto_7_dias": cuenta.get("gasto_7_dias", 0.0)        # Placeholder for actual data
        }).eq("id_cuenta_publicitaria", id_cuenta).execute()

if __name__ == "__main__":
    sincronizar_datos_ads()
