---
applyTo: "**"
---

# Contexto del proyecto

- **Backend de WhatsApp**: servidor Node.js que usa Express, Socket.IO y `whatsapp-web.js` para interactuar con WhatsApp Web (ver `railway-whatsapp-server.js` y `railway-package.json`).
- **Panel Aura**: aplicación web en Flask para administración. Conecta a Supabase, integra Twilio y OpenAI y gestiona rutas en `clientes/aura/routes/` y utilidades en `clientes/aura/utils/`.
- **Variables de entorno**: todas las credenciales (OpenAI, Supabase, Twilio, WhatsApp) se cargan mediante `dotenv`. No deben quedar expuestas en el código.

## Librerías y frameworks

- **Node.js/JavaScript**: Express, Socket.IO, `whatsapp-web.js`, `qrcode`, `cors`, `dotenv`.
- **Python/Flask**: Flask, Flask‑SocketIO, supabase-py, Twilio, OpenAI y otras librerías listadas en `requirements.txt`:contentReference[oaicite:0]{index=0}.

## Guías de codificación y mejores prácticas

1. **Lee el contexto antes de generar código**. Revisa la estructura del repositorio y las dependencias para integrarte sin romper la funcionalidad existente:contentReference[oaicite:1]{index=1}.
2. **Pruebas sin proliferación de archivos**: cuando implementes una función o endpoint nuevo, crea o modifica pruebas en los archivos de test ya existentes en lugar de generar muchos archivos nuevos. Aprovecha las suites de pruebas actuales.
3. **Haz preguntas si hay dudas**: si no entiendes el propósito de una función, la estructura de datos o la API, pide aclaración antes de generar código o revisar cambios. Y no hables en ingles
4. **Python**:
   - Sigue la guía PEP 8 (indentación de 4 espacios, nombres en `snake_case`).
   - Documenta funciones y clases con docstrings.
   - Maneja errores con `try/except` y registra mensajes claros.
   - Extrae claves y tokens con `os.getenv()`; no las codifiques en el repositorio.
5. **Node/JavaScript**:
   - Usa `const` y `let` en lugar de `var`.
   - Emplea `async/await` para código asíncrono y captura errores con bloques `try/catch`.
   - Sigue el estilo `camelCase` para nombres y mantén la estructura de carpetas coherente con lo existente.
6. **Revisiones de código**:
   - Verifica que no se agreguen archivos `.env` ni credenciales.
   - Asegúrate de que el código implementado no genere artefactos innecesarios.
   - Comprueba que las nuevas pruebas cubren la funcionalidad y que no se multiplican sin necesidad.
