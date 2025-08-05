from twilio.rest import Client
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.error_logger import registrar_error
import os
import re

load_dotenv()

# 🔐 Configurar credenciales
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

def normalizar_numero(numero):
    """
    Convierte cualquier formato a 'whatsapp:521XXXXXXXXXX' o similar.
    """
    numero = str(numero).strip().replace("whatsapp:", "").replace("+", "")
    digitos = re.sub(r"\D", "", numero)
    if digitos.startswith("521") and len(digitos) == 13:
        return f"whatsapp:{digitos}"
    if digitos.startswith("52") and len(digitos) == 12:
        return f"whatsapp:521{digitos[2:]}"
    if len(digitos) == 10:
        return f"whatsapp:521{digitos}"
    if digitos.startswith("1") and len(digitos) == 11:
        return f"whatsapp:{digitos}"
    return ""

def registrar_envio(numero, mensaje, sid, tipo="enviado"):
    try:
        # Usar las columnas correctas de la tabla historial_conversaciones
        supabase.table("historial_conversaciones").insert({
            "telefono": numero,
            "mensaje": mensaje,
            "tipo": tipo,
            "emisor": numero,  # Usar emisor en lugar de sid
            # "sid": sid  # Esta columna no existe en la tabla
        }).execute()
    except Exception as e:
        print("❌ Error registrando historial:", e)
        registrar_error("Historial", f"Error al registrar mensaje: {e}")

def enviar_mensaje(destino, mensaje):
    """
    Envía un mensaje normalizando emisor y receptor.
    """
    try:
        from_normalizado = normalizar_numero(TWILIO_WHATSAPP_NUMBER)
        to_normalizado = normalizar_numero(destino)

        print(f"📤 Enviando mensaje:")
        print(f"   ➤ From: {from_normalizado}")
        print(f"   ➤ To:   {to_normalizado}")
        print(f"   ➤ Texto: {mensaje}")

        message = client.messages.create(
            body=mensaje,
            from_=from_normalizado,
            to=to_normalizado
        )

        print(f"✅ Mensaje enviado correctamente. SID: {message.sid}")
        registrar_envio(to_normalizado, mensaje, message.sid, "enviado")

    except Exception as e:
        error_message = str(e)
        print(f"❌ Error enviando mensaje a {destino}: {error_message}")
        
        # Detectar errores específicos de Twilio
        if "insufficient funds" in error_message.lower() or "balance" in error_message.lower():
            error_tipo = "TWILIO_SALDO_INSUFICIENTE"
            error_detalle = f"⚠️ SALDO INSUFICIENTE EN TWILIO - No se pudo enviar mensaje a {destino}"
            print(f"🚨 {error_detalle}")
            
            # Registrar error crítico
            registrar_error(error_tipo, error_detalle)
            
            # Intentar registrar el problema en una tabla específica si existe
            try:
                supabase.table("alertas_sistema").insert({
                    "tipo": "TWILIO_SALDO_BAJO",
                    "mensaje": error_detalle,
                    "urgencia": "CRITICA",
                    "fecha": "now()"
                }).execute()
            except:
                pass  # Si no existe la tabla, continuar
        
        elif "authentication" in error_message.lower() or "credentials" in error_message.lower():
            error_tipo = "TWILIO_CREDENCIALES"
            error_detalle = f"🔐 ERROR DE CREDENCIALES TWILIO - Verificar ACCOUNT_SID y AUTH_TOKEN"
            print(f"🚨 {error_detalle}")
            registrar_error(error_tipo, error_detalle)
        
        elif "invalid" in error_message.lower() and "number" in error_message.lower():
            error_tipo = "TWILIO_NUMERO_INVALIDO"
            error_detalle = f"📞 NÚMERO INVÁLIDO - No se pudo enviar a {destino}"
            print(f"⚠️ {error_detalle}")
            registrar_error(error_tipo, error_detalle)
        
        else:
            # Error genérico
            registrar_error("Twilio", f"Error al enviar mensaje a {destino}: {error_message}")

def verificar_estado_twilio():
    """
    Verifica el estado y saldo de Twilio
    """
    try:
        # Verificar que las credenciales estén configuradas
        if not TWILIO_SID or not TWILIO_TOKEN:
            return {"error": "Credenciales no configuradas", "estado": "ERROR"}
        
        # Obtener información de la cuenta
        account = client.api.accounts(TWILIO_SID).fetch()
        balance = client.api.accounts(TWILIO_SID).balance.fetch()
        
        saldo = float(balance.balance)
        
        estado = "BUENO"
        if saldo < 1:
            estado = "CRITICO"
        elif saldo < 5:
            estado = "BAJO"
        elif saldo < 10:
            estado = "ADVERTENCIA"
        
        return {
            "saldo": saldo,
            "moneda": balance.currency,
            "estado": estado,
            "cuenta_estado": account.status
        }
    
    except Exception as e:
        print(f"❌ Error verificando estado de Twilio: {e}")
        return {"error": str(e), "estado": "ERROR"}