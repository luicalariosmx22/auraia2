import os
import openai
from twilio.rest import Client
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def revisar_todo():
    resultado = "📁 CONFIGURACIÓN Y TABLAS EN SUPABASE:\n"

    # Verificar tablas esenciales en Supabase
    tablas = {
        "settings": "Configuración de Nora",
        "bot_data": "Respuestas automáticas",
        "conocimiento": "Base de conocimiento"
    }

    for tabla, descripcion in tablas.items():
        try:
            response = supabase.table(tabla).select("*").limit(1).execute()
            if not response.data:
                resultado += f"❌ {descripcion} → Tabla '{tabla}' vacía o no encontrada.\n"
            else:
                resultado += f"✅ {descripcion} → Tabla '{tabla}' contiene datos.\n"
        except Exception as e:
            resultado += f"❌ Error al verificar tabla '{tabla}': {e}\n"

    # Verificar configuración en la tabla `settings`
    resultado += "\n🧠 CONFIGURACIÓN DE NORA:\n"
    try:
        response = supabase.table("settings").select("*").execute()
        settings = response.data[0] if response.data else {}

        for key in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            valor = settings.get(key, False)
            resultado += f"{'✅' if valor else '⚠️'} {key} → {valor}\n"
    except Exception as e:
        resultado += f"❌ Error al cargar configuración desde 'settings': {e}\n"

    # Revisar variables de entorno
    resultado += "\n🔐 VARIABLES DE ENTORNO:\n"
    claves_env = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    for clave in claves_env:
        valor = os.getenv(clave)
        if valor:
            resultado += f"✅ {clave} definida\n"
        else:
            resultado += f"❌ {clave} NO definida\n"

    # Validar formato del número de Twilio
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER", "")
    if not twilio_from.startswith("whatsapp:+521"):
        resultado += "❌ TWILIO_PHONE_NUMBER mal formateado (falta el +521...)\n"
        resultado += f"   Valor actual: {twilio_from}\n"
    else:
        resultado += "✅ TWILIO_PHONE_NUMBER con formato correcto (+521...)\n"

    # Probar conexión OpenAI
    resultado += "\n🔌 CONEXIÓN CON OPENAI:\n"
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        test = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=5
        )
        resultado += "✅ OpenAI respondió correctamente\n"
    except Exception as e:
        resultado += f"❌ Error al conectar con OpenAI: \n\n{e}\n"

    # Probar conexión Twilio
    resultado += "\n📞 CONEXIÓN CON TWILIO:\n"
    try:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(sid, token)
        acc = client.api.accounts(sid).fetch()
        resultado += f"✅ Twilio conectado correctamente\n"
    except Exception as e:
        resultado += f"❌ Error al conectar con Twilio: {e}\n"

    # Probar funciones clave
    resultado += "\n⚙️ FUNCIONES CLAVE DEL BOT:\n"
    try:
        r1 = manejar_respuesta_keywords("hola")
        if r1:
            resultado += f"✅ manejar_respuesta_keywords('hola') devolvió algo\n"
        else:
            resultado += f"⚠️ manejar_respuesta_keywords('hola') devolvió None\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_keywords: {e}\n"

    try:
        r2 = manejar_respuesta_ai("¿Qué servicios ofrecen?")
        if r2:
            resultado += f"✅ manejar_respuesta_ai() devolvió respuesta\n"
        else:
            resultado += f"⚠️ manejar_respuesta_ai() no devolvió respuesta\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_ai: {e}\n"

    return resultado
