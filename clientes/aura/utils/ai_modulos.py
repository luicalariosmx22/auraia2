# ✅ Archivo: clientes/aura/utils/ai_modulos.py
# 👉 IA genera/verifica módulos sin romper la app
import os, openai, json, textwrap

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_MSG = textwrap.dedent("""
Eres el asistente técnico de AuraAI2. Tu tarea es:
1. Analizar el snippet de código o descripción de módulo que te pase el usuario.
2. Detectar dependencias (blueprints, tablas Supabase, rutas, variables de entorno).
3. Predecir si la inserción del módulo romperá imports, rutas duplicadas o dependencias.
4. Responder JSON con:
   ok: true|false
   errores: [lista corta]
   sugerencias: [lista corta]
No agregues texto fuera del JSON.
""")

def _llamada_ai(user_content: str) -> dict:
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":SYSTEM_MSG},
                  {"role":"user","content":user_content}],
        temperature=0.0,
    )
    try:
        return json.loads(rsp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"ok": False, "errores": ["Respuesta IA inválida"], "sugerencias": []}

def validar_modulo(snippet: str) -> dict:
    return _llamada_ai(f"VALIDA ESTE MODULO\n```python\n{snippet}\n```")

def sugerir_modulo(nombre: str, descripcion: str) -> dict:
    return _llamada_ai(f"PROPON CODIGO PARA {nombre}\n{descripcion}")
