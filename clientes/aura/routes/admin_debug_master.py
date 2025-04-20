import os
import openai
import inspect
from flask import Blueprint, render_template, request, session
from dotenv import load_dotenv
from clientes.aura.routes import admin_debug_rutas
from clientes.aura.debug import debug_supabase
from clientes.aura.debug import debug_verificar

admin_debug_master_bp = Blueprint("admin_debug_master", __name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@admin_debug_master_bp.route("/admin/debug/master", methods=["GET", "POST"])
def debug_master():
    resultado_ai = ""
    prompt_enviado = ""
    error_usuario = request.form.get("error") if request.method == "POST" else None

    # Ejecutar todos los debugs
    rutas_html = admin_debug_rutas.extraer_rutas_desde_templates("clientes/aura/templates")
    rutas_flask = admin_debug_rutas.extraer_rutas_flask("clientes/aura/routes")
    no_definidas = [r for r in rutas_html if r not in rutas_flask]

    supabase_logs = debug_supabase.run_verificacion
    sistema_logs = debug_verificar.verificar_sistema()

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

    return render_template(
        "admin_debug_master.html",
        rutas_html=rutas_html,
        rutas_flask=rutas_flask,
        rutas_no_definidas=no_definidas,
        resultado_ai=resultado_ai,
        prompt_enviado=prompt_enviado,
        error_usuario=error_usuario,
        sistema_logs=sistema_logs
    )
