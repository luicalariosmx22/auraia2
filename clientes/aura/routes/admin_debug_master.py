import os
import openai
from flask import Blueprint, render_template, request, current_app
from dotenv import load_dotenv
from clientes.aura.routes import admin_debug_rutas
from clientes.aura.debug import debug_supabase
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.routes.debug_verificar import verificar_sistema

admin_debug_master_bp = Blueprint("admin_debug_master", __name__)

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@admin_debug_master_bp.route("/admin/debug/master", methods=["GET", "POST"])
def debug_master():
    try:
        # Inicialización de variables
        resultado_ai = ""
        prompt_enviado = ""
        error_usuario = request.form.get("error") if request.method == "POST" else None
        rutas_html, rutas_flask, no_definidas = [], [], []
        supabase_logs, sistema_logs, rutas_registradas_html = "", "", ""

        # Validar clave de API de OpenAI
        if not openai.api_key:
            return "❌ Error: No se configuró la clave de API de OpenAI."

        # 1️⃣ Rutas HTML y Flask
        try:
            rutas_html = admin_debug_rutas.extraer_rutas_desde_templates("clientes/aura/templates")
            rutas_flask = admin_debug_rutas.extraer_rutas_flask("clientes/aura/routes")
            no_definidas = [r for r in rutas_html if r not in rutas_flask]
        except Exception as e:
            print(f"❌ Error al procesar rutas HTML y Flask: {str(e)}")

        # 2️⃣ Verificar Supabase
        try:
            supabase_logs = debug_supabase.run_verificacion()
        except Exception as e:
            supabase_logs = f"❌ Error al verificar Supabase: {str(e)}"

        # 3️⃣ Verificar el sistema
        try:
            sistema_logs = verificar_sistema()
        except Exception as e:
            sistema_logs = f"❌ Error al verificar el sistema: {str(e)}"

        # 4️⃣ Generar HTML con rutas registradas
        try:
            rutas_registradas_html = generar_html_rutas(current_app)
        except RuntimeError as e:
            rutas_registradas_html = f"❌ Error al generar rutas: {str(e)}"

        # 5️⃣ OpenAI para analizar errores proporcionados por el usuario
        if error_usuario:
            prompt_enviado = f"""
Tengo un proyecto Flask y recibí este error:
{error_usuario}

Basado en este contexto, ¿cuál podría ser la causa probable?
Evita suposiciones, responde como experto en debug de Flask y Python.
            """.strip()

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un experto en detectar errores de programación en Flask y Supabase."},
                        {"role": "user", "content": prompt_enviado}
                    ],
                    max_tokens=500,
                    temperature=0.2
                )
                resultado_ai = response.choices[0].message.content.strip()
            except openai.error.OpenAIError as e:
                resultado_ai = f"❌ Error en OpenAI: {e.__class__.__name__} - {str(e)}"
            except Exception as e:
                resultado_ai = f"❌ Error desconocido: {str(e)}"

        # Renderizar resultados en la plantilla
        return render_template(
            "admin_debug_master.html",
            rutas_html=rutas_html,
            rutas_flask=rutas_flask,
            rutas_no_definidas=no_definidas,
            rutas_registradas_html=rutas_registradas_html,
            resultado_ai=resultado_ai,
            prompt_enviado=prompt_enviado,
            error_usuario=error_usuario,
            sistema_logs=sistema_logs,
            supabase_logs=supabase_logs
        )
    except Exception as e:
        # Registrar errores críticos
        print(f"❌ Error crítico en debug_master: {str(e)}")
        return "❌ Error crítico en el servidor. Por favor, contacta al administrador."