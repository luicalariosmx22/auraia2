Perfecto, ya revisé los 3 archivos: `webhook.py`, `process_message.py` y `handle_ai.py`.
Te dejo aquí la **documentación corregida y completa** del flujo de procesamiento, con Supabase como fuente principal de datos.

---

## 🧠 FLUJO DE PROCESAMIENTO DE MENSAJES EN AURAAI2

> Este flujo representa cómo se procesan los mensajes entrantes desde WhatsApp vía Twilio, cómo se conecta con Supabase y cómo se usa IA para responder automáticamente.

---

### 1️⃣ `webhook.py`

📍 **Ubicación:** `clientes/aura/routes/webhook.py`
📌 **Ruta:** `/webhook`

* Punto de entrada del sistema.
* Recibe los datos del mensaje desde Twilio.
* Convierte `request.form` en diccionario.
* Llama directamente a `procesar_mensaje(data)` del archivo `process_message.py`.

---

### 2️⃣ `process_message.py`

📍 **Ubicación:** `clientes/aura/handlers/process_message.py`

Esta es la **pieza central del sistema**, y se encarga de:

#### 🔄 Normalizar y limpiar datos:

* Normaliza los números del remitente (`From`) y receptor (`To`).
* Limpia el cuerpo del mensaje.

#### 🧠 Identificar la Nora:

* Usa el número receptor (`To`) para buscar en Supabase la configuración de Nora (`nombre_nora`, `numero_nora`).

#### 👤 Actualizar contacto:

* Si ya existe el contacto en la tabla `contactos` de Supabase:

  * Se actualiza `ultimo_mensaje`, `mensaje_reciente` y `imagen_perfil` (si está disponible).
* Si no existe:

  * Se crea automáticamente un nuevo registro con los datos mínimos.

#### 👋 Enviar mensaje de bienvenida:

* Si el contacto no tiene historial previo, y la configuración incluye `mensaje_bienvenida`, lo envía.

#### 📝 Guardar historial:

* Guarda el mensaje entrante como tipo `"usuario"`.
* Guarda la respuesta como tipo `"respuesta"`.

#### 🧠 Llamar a la IA:

* Llama a `manejar_respuesta_ai(...)` para generar la respuesta usando OpenAI.

#### 📤 Enviar respuesta:

* Envía el mensaje generado con `enviar_mensaje(...)`.

---

### 3️⃣ `handle_ai.py`

📍 **Ubicación:** `clientes/aura/handlers/handle_ai.py`

Encargado de generar una respuesta inteligente usando OpenAI.

#### 🧠 Proceso:

1. **Carga la base de conocimiento**:

   * Llama a `obtener_base_conocimiento(numero_nora)` (con textos definidos por Nora).
2. **Consulta Supabase**:

   * Para obtener la `personalidad` y `instrucciones` definidas en `configuracion_bot`.
3. **Construye prompt**:

   * Combina personalidad + instrucciones + historial + base de conocimiento.
4. **Llama a OpenAI**:

   * Usa `gpt-3.5-turbo` para generar la respuesta.
5. **Devuelve**:

   * Texto de la respuesta.
   * Historial actualizado (incluyendo rol `"assistant"`).

---

## 🔗 FLUJO RESUMIDO

```mermaid
flowchart TD
    A[Twilio WhatsApp] --> B[/webhook]
    B --> C[procesar_mensaje()]
    C --> D[buscar nombre_nora en Supabase]
    C --> E[actualizar o crear contacto en Supabase]
    C --> F[guardar mensaje entrante en historial]
    C --> G[manejar_respuesta_ai()]
    G --> H[consultar configuracion_bot]
    G --> I[cargar base_conocimiento]
    G --> J[Llamar a OpenAI]
    G --> K[devolver respuesta]
    C --> L[guardar respuesta en historial]
    C --> M[enviar_mensaje()]
```

---

## ✅ Tecnologías involucradas

| Función                     | Tecnología                            |
| --------------------------- | ------------------------------------- |
| Mensajería                  | Twilio WhatsApp                       |
| Base de datos               | Supabase                              |
| Inteligencia artificial     | OpenAI (gpt-3.5-turbo)                |
| Backend                     | Flask                                 |
| Webhook                     | `/webhook`                            |
| Almacenamiento de historial | Supabase (`historial_conversaciones`) |
| Contactos                   | Supabase (`contactos`)                |

---

