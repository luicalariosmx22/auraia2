# Archivo: utils/meta_sync.py ✅

import os
from twilio.rest import Client
from supabase import create_client

# 🚀 Variables desde Railway
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_WHATSAPP_NUMBER')  # 👈 este es el que usarás para WhatsApp
DESTINO = os.getenv('NORA_NUMERO')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_alerta_cambio(nombre_cliente, estado_anterior, estado_actual):
    mensaje = f"🔔 La cuenta '{nombre_cliente}' cambió de estado: {estado_anterior} ➔ {estado_actual}."
    twilio_client.messages.create(
        body=mensaje,
        from_=f'whatsapp:{TWILIO_FROM}',
        to=f'whatsapp:{DESTINO}'
    )

def sincronizar_datos_ads():
    cuentas = supabase.table("meta_ads_cuentas").select("*").execute().data
    for cuenta in cuentas:
        id_cuenta = cuenta["id_cuenta_publicitaria"]
        estado_anterior = cuenta.get("estado_actual", None)

        # Aquí debes tener ya tu función de obtención, ejemplo 👇
        datos = obtener_datos_cuenta(id_cuenta)

        nuevo_estado = datos["estado"]
        if estado_anterior and nuevo_estado != estado_anterior:
            enviar_alerta_cambio(cuenta["nombre_cliente"], estado_anterior, nuevo_estado)

        supabase.table("meta_ads_cuentas").update({
            "estado_actual": nuevo_estado,
            "campanas_activas": datos["campanas_activas"],
            "anuncios_activos": datos["anuncios_activos"],
            "gasto_7_dias": datos["gasto_7_dias"]
        }).eq("id_cuenta_publicitaria", id_cuenta).execute()
