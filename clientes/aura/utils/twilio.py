from twilio.rest import Client
import os

def enviar_mensaje_twilio(telefono, mensaje, numero_whatsapp):
    """
    Envía un mensaje de WhatsApp utilizando Twilio.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    from_whatsapp_number = f"whatsapp:+{numero_whatsapp}"  # Usar el número de WhatsApp de la Nora
    to_whatsapp_number = f"whatsapp:+{telefono}"

    message = client.messages.create(
        body=mensaje,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )
    print(f"✅ Mensaje enviado desde {from_whatsapp_number} a {to_whatsapp_number}: {mensaje}")