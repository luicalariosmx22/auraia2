# 📚 Guía oficial de desarrollo Nora AI

Este documento  contiene las reglas, estructuras y ejemplos para trabajar en módulos de Nora AI.

📜 Cómo se usará esta biblia principal
Función principal

Este biblia será el índice maestro de toda la documentación de Nora AI.

Contiene reglas básicas al inicio (onboarding rápido) y luego un índice enlazado a la carpeta docs/ donde estará la guía completa dividida en 15 archivos.

Ubicación

Guardar este archivo en la raíz del repositorio (misma carpeta que registro_dinamico.py y registro_admin.py).

Crear carpeta docs/ y ahí poner los 15 .md separados (contenido completo de cada sección).

Relación con otros archivos

El archivo para hacer un nuevo modulo o corregir uno.md ([41†source]) servirá como checklist técnico cuando agregues nuevos módulos, pero las reglas generales estarán en README.md → sección “Reglas básicas de desarrollo”.

El archivo estructura_submodulo_tareas.txt ([42†source]) es un ejemplo específico que se puede enlazar desde docs/10_estructura_avanzada_tareas.md.

Los archivos registro_dinamico.py ([43†source]) y registro_admin.py ([44†source]) se usarán como referencia en varias secciones (Registro del módulo, Módulos activos).

Cómo trabajar con él

Si quieres crear un módulo:

Lees las Reglas básicas (inicio de README.md).

Sigues el índice hasta docs/04_estructura_modulo.md y docs/05_registro_modulo.md.

Usas como plantilla el archivo para hacer un nuevo modulo o corregir uno.md.

Si quieres diagnosticar un módulo:

Vas a docs/07_diagnostico_automatico.md.

Revisas también docs/06_archivos_clave.md para saber dónde buscar errores.

Si quieres trabajar con submódulos complejos (como tareas):

Lees docs/10_estructura_avanzada_tareas.md.

Consultas estructura_submodulo_tareas.txt para detalles exactos.

Uso en GitHub Copilot Edit

Copilot/Edit podrá usar este README.md como índice y resumen para responder preguntas rápidas.

Cuando pidas algo muy específico, Copilot seguirá los enlaces internos (docs/*.md) para usar el contenido exacto.

Formato y estilo

Todo en Markdown estándar (compatible con GitHub y VS Code).

El índice usa rutas relativas para que funcionen tanto en GitHub como localmente.



---

## 🚀 Reglas básicas de desarrollo

1. **Variables de entorno**  
   - En local usa `.env.local`  
   - En Railway configura las variables en el panel  
   - Nunca pongas claves directamente en el código (`os.getenv(...)` siempre).

2. **Estructura de módulos**  
   - Cada módulo va en `clientes/aura/routes/panel_cliente_<modulo>/`  
   - Template principal en `clientes/aura/templates/panel_cliente_<modulo>/index.html`

3. **Registro y activación**  
   - Registra el módulo en `modulos_disponibles` (Supabase)  
   - Actívalo en `configuracion_bot`  
   - Añade el blueprint en `registro_dinamico.py`

4. **Rutas Flask**  
   - Siempre incluir `<nombre_nora>` en `url_prefix`  
   - Usar `request.view_args.get("nombre_nora")` en lugar de parámetros directos.

5. **Testing**  
   - Guarda tests en `tests/`  
   - Evita cargar toda la app para pruebas simples  
   - Usa mocks para no depender de servicios externos.

6. **Buenas prácticas**  
   - Python: `snake_case`, docstrings, `try/except`, sin hardcodear secretos.  
   - JS: `let`/`const`, modular, evitar inline scripts.  

7. **⚠️ VERIFICACIÓN DE TEMPLATES**  
   - **SIEMPRE** leer `base_cliente.html` antes de crear templates  
   - Solo usar bloques que existen: `head_extra`, `contenido`, `scripts`  
   - **NUNCA** inventar bloques como `estilos_adicionales` o `scripts_adicionales`
   - Ver [Errores críticos a evitar](docs/14_errores_criticos_evitar.md) para casos reales  

---

## 📑 Índice detallado
1. [Variables de entorno](docs/01_variables_entorno.md)
2. [Testing y Desarrollo](docs/02_testing_desarrollo.md)
3. [Multi-Nora y nombre_nora](docs/03_multi_nora_nombre_nora.md)
4. [Estructura de un módulo](docs/04_estructura_modulo.md)
5. [Registro del módulo](docs/05_registro_modulo.md)
6. [Archivos clave por carpeta](docs/06_archivos_clave.md)
7. [Diagnóstico automático](docs/07_diagnostico_automatico.md)
8. [Buenas prácticas](docs/08_buenas_practicas.md)
9. [Ejemplo completo de módulo](docs/09_ejemplo_modulo.md)
10. [Estructura avanzada (tareas)](docs/10_estructura_avanzada_tareas.md)
11. [Integración con APIs externas](docs/11_integracion_apis.md)
12. [Webhook de Meta Ads - Implementación y Verificación](docs/12_webhook_meta_ads.md)
13. [Checklist antes de subir a Railway](docs/13_checklist_railway.md)
14. [🚨 Errores críticos a evitar](docs/14_errores_criticos_evitar.md)
