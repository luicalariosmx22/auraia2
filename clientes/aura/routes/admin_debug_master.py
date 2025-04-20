import os
import openai
from flask import Blueprint, render_template, request
from dotenv import load_dotenv
from clientes.aura.routes import admin_debug_rutas
from clientes.aura.debug import debug_supabase
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.routes.debug_verificar import verificar_sistema

admin_debug_master_bp = Blueprint("admin_debug_master", __name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@admin_debug_master_bp.route("/admin/debug/master", methods=["GET", "POST"])
def debug_master():
    resultado_ai = ""
    prompt_enviado = ""
    error_usuario = request.form.get("error") if request.method == "POST" else None

    # 1️⃣ Rutas HTML y Flask
    rutas_html = admin_debug_rutas.extraer_rutas_desde_templates("clientes/aura/templates")
    rutas_flask = admin_debug_rutas.extraer_rutas_flask("clientes/aura/routes")
    no_definidas = [r for r in rutas_html if r not in rutas_flask]

    # 2️⃣ Verificar Supabase
    supabase_logs = debug_supabase.run_verificacion()  # Corre la verificación completa de Supabase

    # 3️⃣ Verificar el sistema
    sistema_logs = verificar_sistema()

    # 4️⃣ Generar HTML con rutas registradas
    rutas_registradas_html = generar_html_rutas()

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
        except Exception as e:
            resultado_ai = f"❌ Error al consultar OpenAI: {e}"

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