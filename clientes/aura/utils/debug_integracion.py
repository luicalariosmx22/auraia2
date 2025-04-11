# 📁 Archivo: clientes/aura/utils/debug_integracion.py

import os
import json
import openai
from datetime import datetime
from twilio.rest import Client
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

# Utilidades comunes

def check_archivo(path, descripcion):
    if not os.path.exists(path):
        return f"❌ {descripcion} → No encontrado ({path})"
    return f"✅ {descripcion} → OK"

# 1. Verificar archivos y estructura base

def revisar_archivos():
    resultados = []
    resultados.append("📁 ARCHIVOS Y CONFIGURACIÓN:")
    resultados.append(check_archivo("clientes/aura/config/settings.json", "settings.json"))
    resultados.append(check_archivo("clientes/aura/config/bot_data.json", "bot_data.json"))
    resultados.append(check_archivo("clientes/aura/config/servicios_conocimiento.txt", "Base de conocimiento IA"))
    resultados.append(check_archivo("clientes/aura/database/historial", "Carpeta historial"))
    return resultados

# 2. Verificar settings.json

def revisar_settings():
    ruta = "clientes/aura/config/settings.json"
    resultados = ["\n🧠 CONFIGURACIÓN DE NORA:"]
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        for clave in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            estado = data.get(clave, False)
            resultados.append(f"{'✅' if estado else '⚠️'} {clave} → {estado}")
    except Exception as e:
        resultados.append(f"❌ Error al leer settings.json: {e}")
    return resultados

# 3. Verificar variables de entorno

def revisar_variables_entorno():
    resultados = ["\n🔐 VARIABLES DE ENTORNO:"]
    claves = ["OPENAI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    for clave in claves:
        valor = os.getenv(clave)
        if valor:
            resultados.append(f"✅ {clave} definida")
        else:
            resultados.append(f"❌ {clave} FALTANTE")
    return resultados

# 4. Verificar conexión con OpenAI

def probar_openai():
    resultados = ["\n🔌 CONEXIÓN CON OPENAI:"]
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola, ¿puedes responderme?"}],
            max_tokens=10
        )
        if respuesta.choices:
            resultados.append("✅ OpenAI respondió correctamente")
        else:
            resultados.append("❌ OpenAI no devolvió respuesta")
    except Exception as e:
        resultados.append(f"❌ Error al conectar con OpenAI: {e}")
    return resultados

# 5. Verificar conexión con Twilio

def probar_twilio():
    resultados = ["\n📞 CONEXIÓN CON TWILIO:"]
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        cuentas = client.api.accounts.list(limit=1)
        if cuentas:
            resultados.append("✅ Twilio conectado correctamente")
        else:
            resultados.append("❌ Twilio no devolvió cuentas")
    except Exception as e:
        resultados.append(f"❌ Error al conectar con Twilio: {e}")
    return resultados

# 6. Probar funciones clave de Nora

def probar_funciones_bot():
    resultados = ["\n⚙️ FUNCIONES CLAVE DEL BOT:"]
    try:
        respuesta_kw = manejar_respuesta_keywords("hola")
        if respuesta_kw:
            resultados.append("✅ manejar_respuesta_keywords('hola') devolvió respuesta")
        else:
            resultados.append("⚠️ manejar_respuesta_keywords('hola') devolvió None")
    except Exception as e:
        resultados.append(f"❌ Error en manejar_respuesta_keywords: {e}")

    try:
        respuesta_ai = manejar_respuesta_ai("¿Qué servicios ofrecen?")
        if respuesta_ai:
            resultados.append("✅ manejar_respuesta_ai() devolvió respuesta")
        else:
            resultados.append("⚠️ manejar_respuesta_ai() devolvió None")
    except Exception as e:
        resultados.append(f"❌ Error en manejar_respuesta_ai: {e}")

    return resultados

# 7. Historial

def revisar_historial():
    ruta = "clientes/aura/database/historial"
    resultados = ["\n🕑 HISTORIAL DE CONVERSACIONES:"]
    try:
        archivos = os.listdir(ruta)
        if archivos:
            resultados.append(f"✅ {len(archivos)} archivos de historial encontrados")
        else:
            resultados.append("⚠️ Carpeta de historial vacía")
    except Exception as e:
        resultados.append(f"❌ Error al leer historial: {e}")
    return resultados

# Función principal unificada

def revisar_todo():
    secciones = []
    secciones.extend(revisar_archivos())
    secciones.extend(revisar_settings())
    secciones.extend(revisar_variables_entorno())
    secciones.extend(probar_openai())
    secciones.extend(probar_twilio())
    secciones.extend(probar_funciones_bot())
    secciones.extend(revisar_historial())
    return "\n".join(secciones)
