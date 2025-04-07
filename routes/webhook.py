from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import openai
import traceback
from utils.text_reader import cargar_conocimiento_desde_txt, buscar_respuesta_en_txt
from utils.config_helper import cargar_configuracion
from utils.memoria import guardar_memoria, obtener_memoria, limpiar_memoria
from utils.historial import guardar_en_historial
from utils.error_logger import registrar_error  # ✅ Corrección aquí

webhook = Blueprint("webhook", __name__)

@webhook.route("/", methods=["POST"])  # 👈 CAMBIO: antes era '/webhook', ahora es solo '/'
def whatsapp_webhook():
    try:
        mensaje_usuario = request.form.get('Body', '').strip().lower()
        numero_usuario = request.form.get('From')
        respuesta = MessagingResponse()

        print(f"📩 Mensaje recibido: {mensaje_usuario}")
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido")

        # Mensaje de bienvenida
        if mensaje_usuario in ['hola', 'buenas', 'hi', 'hello']:
            texto_bienvenida = (
                "👋 ¡Hola! Soy *Aura AI*, la inteligencia artificial de *Aura Marketing* 🤖\n\n"
                "Estoy aquí para ayudarte con información sobre nuestros servicios y productos.\n\n"
                "Puedes escribirme una palabra clave como:\n"
                "📄 *Presentación*\n"
                "📢 *Anuncios*\n"
                "🎓 *Cursos*\n"
                "📅 *Citas*\n\n"
                "¿Con qué te gustaría comenzar?"
            )
            respuesta.message(texto_bienvenida)
            return str(respuesta)

        # Confirmaciones sí/no
        memoria = obtener_memoria(numero_usuario)
        if mensaje_usuario in ["sí", "si", "no"] and "esperando_confirmacion" in memoria:
            tema = memoria["esperando_confirmacion"]
            if mensaje_usuario.startswith("s"):
                respuesta.message(f"✅ ¡Gracias! Te anotamos para recibir {tema}.")
            else:
                respuesta.message(f"👍 Entendido, no recibirás {tema}.")
            limpiar_memoria(numero_usuario)
            return str(respuesta)

        # Base de datos
        try:
            with open('bot_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            registrar_error("webhook", "Error al leer bot_data.json", tipo="JSON", detalles=str(e))
            data = {}

        for _, info in data.items():
            claves = info.get("palabras_clave", [])
            if any(k in mensaje_usuario for k in claves):
                contenido = info.get("contenido", "")
                botones = info.get("botones", [])
                msg = respuesta.message(contenido)

                if botones:
                    texto_extra = ""
                    for boton in botones:
                        if boton["tipo"] == "link":
                            texto_extra += f"\n🔗 {boton['texto']}: {boton['url']}"
                        else:
                            texto_extra += f"\n✅ {boton['texto']}"
                    msg.body(f"{contenido}{texto_extra}")

                if "promociones" in mensaje_usuario:
                    guardar_memoria(numero_usuario, {"esperando_confirmacion": "promociones y contenido gratuito"})

                return str(respuesta)

        # TXT
        try:
            conocimiento = cargar_conocimiento_desde_txt()
            resultado_txt = buscar_respuesta_en_txt(mensaje_usuario, conocimiento)
            if resultado_txt:
                print(f"🧠 Respuesta del TXT:\n{resultado_txt}")
                respuesta.message(resultado_txt)
                return str(respuesta)
        except Exception as e:
            registrar_error("webhook", "Error al procesar archivo TXT", tipo="TXT", detalles=str(e))

        # OpenAI
        config = cargar_configuracion()
        if config.get("usar_openai", False):
            try:
                contexto = ""
                for clave, info in data.items():
                    pregunta = ", ".join(info.get("palabras_clave", [clave]))
                    respuesta_contextual = info.get("contenido", "")
                    contexto += f"🔹 *{pregunta}*: {respuesta_contextual}\n"

                prompt = (
                    f"Eres Aura AI, la inteligencia artificial de Aura Marketing. "
                    f"Tu trabajo es responder a clientes usando solo la información que te proporcionamos.\n\n"
                    f"Base de conocimientos:\n{contexto}\n\n"
                    f"Mensaje del usuario: \"{mensaje_usuario}\"\n\n"
                    f"Responde de forma amable, clara y profesional. Si no sabes la respuesta, puedes decir que se le puede apoyar por medio de asesoría humana."
                )

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                respuesta_ia = completion.choices[0].message.content.strip()
                respuesta.message(respuesta_ia)
                return str(respuesta)
            except Exception as e:
                registrar_error("webhook", "Error al consultar OpenAI", tipo="OpenAI", detalles=str(e))
                respuesta.message("❌ No fue posible obtener una respuesta de la IA.")
                return str(respuesta)
        else:
            respuesta.message("🤖 Lo siento, no tengo información sobre eso todavía.")
            return str(respuesta)

    except Exception as e:
        traceback.print_exc()
        registrar_error("webhook", "Error inesperado general", tipo="General", detalles=str(e))
        respuesta = MessagingResponse()
        respuesta.message("❌ Error inesperado en el bot. Por favor intenta más tarde.")
        return str(respuesta)
