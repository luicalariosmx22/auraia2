Quiero agregar un nuevo módulo llamado [NOMBRE_DEL_MODULO] para AuraAI2.

Necesito que me generes el resultado en formato **GitHub Copilot EDIT**, sin explicaciones, solo el contenido de los archivos a modificar o crear.

Instrucciones clave que debes seguir:

1. El módulo siempre es para sistema Multi-Nora.
2. El backend va en `/clientes/aura/routes/panel_cliente_<nombre_modulo>/`
3. La ruta debe registrarse en `registro_dinamico.py`
4. También debe agregarse visualmente al panel del cliente (menú o dashboard).
5. Usa plantilla HTML en `/clientes/aura/templates/panel_cliente_<nombre_modulo>/index.html`
6. Usa el **CSS global** (aún no existe uno por módulo). No se debe crear un archivo CSS nuevo.
7. El módulo debe guardarse en la base `modulos_disponibles`, solo si no existe ya para esa `nombre_nora`.
8. También debe registrarse en la tabla `rutas_registradas` automáticamente al levantar el sistema (esto ya lo hace `app.py`).
9. El módulo se debe ocultar si no está activado en `modulos_disponibles`.
10. Estamos trabajando sobre Railway y Supabase.

Solo quiero el código listo para pegar en mis archivos, en formato de edición tipo:

```python
# ✅ Archivo: ruta/del/archivo.py
# 👉 Explicación corta en comentario (1 línea máximo)
# ...código aquí...
