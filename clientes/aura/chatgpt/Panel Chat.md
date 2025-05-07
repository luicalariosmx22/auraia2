¡Excelente! 🎯 Con eso acabas de definir una **versión pro del módulo `panel_chat`**, digna de una plataforma tipo CRM inteligente. Te lo voy a documentar como debe ser, para que se integre a la enciclopedia y también sirva como guía de implementación para ti o quien entre al proyecto.

---

## 📦 Módulo: `panel_chat` (versión corregida)

---

### 📍 **Ubicación**

`clientes/aura/routes/panel_chat/`

---

### 🧠 **¿Qué hace?**

Este módulo representa el **centro de mensajería** del cliente, inspirado en WhatsApp Web, con control total de cada conversación:

---

### 🧱 **Estructura de UI (dividido en 3 columnas)**

#### 🟩 **Columna 1: Contactos**

* Lista de contactos ordenada por **último mensaje recibido (más reciente arriba)**.
* Para cada contacto mostrar:

  * Nombre del contacto
  * Último mensaje enviado (truncado)
  * Fecha del último mensaje (solo **día y mes**)
  * **Etiqueta activa**
* Filtro por etiqueta disponible en la parte superior.

#### 🟦 **Columna 2: Chat**

* Muestra la conversación completa con ese contacto en **formato tipo WhatsApp Web**.
* Diferenciar claramente:

  * Mensajes del **contacto** (entrada)
  * Respuestas de **Nora AI** (salida)
* Abajo, un **input para enviar mensaje manual**.
* Incluye botón para **intervenir** y **desactivar AI** solo para ese contacto.

#### 🟨 **Columna 3: Información del contacto**

* Campos editables:

  * Nombre
  * Número
  * Notas o datos adicionales
* Gestión de etiquetas:

  * Agregar / Editar / Eliminar etiquetas
* Mostrar un **resumen automático generado por AI** de la conversación (opcional pero clave).

---

### 👥 **¿Quién lo usa?**

🟢 **Cliente** (desde el panel de su Nora)

---

### 🔁 **¿Es dinámico por Nora?**

✅ Sí, se registra en `registro_dinamico.py`

---

### 🌐 **Ruta esperada**

```
/panel_cliente/<nombre_nora>/chat
```

---

### 📤 **Acciones disponibles**

| Función                            | Acción                          |
| ---------------------------------- | ------------------------------- |
| Ver mensajes anteriores            | ✅                               |
| Ver/filtrar contactos por etiqueta | ✅                               |
| Intervenir manualmente             | ✅                               |
| Desactivar AI por contacto         | ✅                               |
| Editar info del contacto           | ✅                               |
| Agregar/eliminar etiquetas         | ✅                               |
| Ver resumen AI de la conversación  | ✅                               |
| Programar mensajes                 | ❌ (✖️ No disponible desde aquí) |

---

### 🗂 Archivos que deben mantenerse/modificarse

* `vista_panel_chat.py` → carga del HTML principal (3 columnas)
* `vista_enviar_mensaje.py` → intervención manual + toggle IA
* `vista_api_chat.py` → endpoint para cargar historial
* `vista_gestion_etiqueta.py` → gestión de etiquetas por contacto
* `vista_toggle_ia.py` → botón de activar/desactivar AI
* `vista_programar_envio.py` → ❌ posiblemente eliminar o mover a otro módulo si ya no se usa

