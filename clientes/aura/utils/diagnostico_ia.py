# ✅ Archivo: clientes/aura/utils/diagnostico_ia.py
def diagnosticar_modulo(modulo: dict) -> dict:
    """
    Analiza el módulo y devuelve diagnóstico con posibles soluciones.
    """
    sugerencias = []
    nivel_confianza = "alto"
    
    if not modulo.get("carpeta_backend") and not modulo.get("existe_archivo"):
        return {
            "causa": "El módulo no tiene carpeta ni archivo principal.",
            "solucion": "Crea la carpeta backend con __init__.py y un archivo como panel_cliente_<modulo>.py.",
            "nivel": "alto"
        }

    if not modulo.get("archivo_principal") and modulo.get("existe_archivo"):
        sugerencias.append("Agrega el campo `archivo_principal` en Supabase con el nombre del archivo real (ej. panel_cliente_contactos.py).")

    if not modulo.get("registrado_codigo"):
        sugerencias.append("Asegúrate de que el archivo defina un Blueprint con `Blueprint('panel_cliente_contactos', ...)`.")

    if not modulo.get("registro_dinamico_detectado"):
        sugerencias.append("Agrega en `registro_dinamico.py` un bloque como:\n\n```python\nif 'contactos' in modulos:\n    from clientes.aura.routes.panel_cliente_contactos.panel_cliente_contactos import panel_cliente_contactos_bp\n    safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f\"/panel_cliente/{nombre_nora}/contactos\")\n```")

    if not modulo.get("menciones_en_init"):
        sugerencias.append("Agrega la importación en `__init__.py` para que Flask lo cargue en modo manual si se requiere.")

    if not modulo.get("existe_ruta") and modulo.get("respuesta_http") == 404:
        sugerencias.append("Agrega en el archivo principal una ruta raíz con:\n\n```python\n@panel_cliente_contactos_bp.route('/')\ndef panel_contactos():\n    return render_template('panel_cliente_contactos/index.html')\n```")

    if not modulo.get("template_html") or "index.html" not in str(modulo.get("templates_renderizados")):
        sugerencias.append("Crea el archivo `panel_cliente_contactos/index.html` dentro de la carpeta `templates`.")

    return {
        "causa": "Módulo incompleto o no registrado dinámicamente.",
        "solucion": "\n\n".join(sugerencias),
        "nivel": nivel_confianza
    }
