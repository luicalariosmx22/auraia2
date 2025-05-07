✅ Primera tabla: configuracion_bot
🔍 Detectado en el código:
Usada en:

process_message.py → para obtener el nombre_nora desde numero_nora

handle_ai.py → para obtener personalidad, instrucciones, y datos IA

app.py → para registrar dinámicamente las rutas

🧩 Campos que vi:
Campo	Tipo	Uso
id	UUID	Primaria
nombre_nora	text	Identificador lógico (ej. "aura")
numero_nora	text	Número oficial WhatsApp
mensaje_bienvenida	text	Se envía al primer mensaje
personalidad	text	IA
instrucciones	text	IA
foto_perfil	text	Opcional
created_at, updated_at	timestamp	Control automático

🔗 Relacionada con:
contactos

historial_conversaciones

Toda la arquitectura multi-nora

🧠 Mi veredicto técnico:
🔒 Tabla 100% necesaria y crítica
📌 NO se debe eliminar ni modificar sin control
✅ Perfecta para admin, IA y routing dinámico

Perfecto 💯, aquí tienes la descripción completa de la tabla `rutas_registradas`, en el mismo **formato de manual** que hemos estado construyendo para cada tabla del sistema.

---

## 🧾 Tabla: `rutas_registradas`

---

### 📍 ¿Qué guarda?

Registra todas las rutas activas del sistema Flask.
Se actualiza automáticamente cada vez que inicia la aplicación, como mecanismo de **auditoría interna** y verificación de estructura.

---

### 🧠 ¿Para qué sirve?

* Permite verificar que todos los blueprints están correctamente registrados.
* Ayuda al equipo técnico a detectar rutas faltantes, mal definidas o duplicadas.
* Facilita la creación de herramientas de monitoreo (como el HTML `debug_rutas.html`).
* Sirve como base para construir reportes de despliegue o dashboards administrativos.

---

### 📊 Campos principales

| Campo           | Tipo      | Descripción                                            |
| --------------- | --------- | ------------------------------------------------------ |
| `id`            | UUID      | Identificador único de la fila                         |
| `ruta`          | Texto     | Ruta completa, por ejemplo: `/panel_cliente/aura/chat` |
| `blueprint`     | Texto     | Nombre del blueprint al que pertenece la ruta          |
| `metodo`        | Texto     | Métodos HTTP permitidos (ej: GET, POST)                |
| `registrado_en` | Timestamp | Fecha y hora exacta de registro                        |

---

### 🔄 ¿Cómo se llena esta tabla?

* Al iniciar `app.py`, el sistema recorre todas las rutas de Flask (`app.url_map`) y las guarda automáticamente aquí.
* No se llena manualmente.
* La información registrada es un reflejo exacto de lo que está activo en el servidor en ese momento.

---

### 📏 Estándar para cada ruta registrada

Cada fila debe reflejar una ruta activa siguiendo esta estructura:

* Debe tener una **ruta legible y ordenada** (`/webhook`, `/admin/dashboard`, `/panel_cliente/aura/ia`)
* El blueprint debe indicar de qué módulo proviene (`panel_chat_bp`, `admin_dashboard_bp`)
* Debe quedar registrado el método o métodos válidos (`GET`, `POST`, etc.)

---

### 📌 Reglas internas para registrar rutas

* Toda nueva ruta debe estar incluida en algún archivo `registro_*.py`.
* Las rutas se deben registrar usando el sistema `safe_register_blueprint(...)`.
* El sistema debe poder levantar sin errores para que las rutas se capturen correctamente.
* Si se modifica el nombre del blueprint, debe reflejarse también en esta tabla.

---

### 🛡️ ¿Quién puede ver esta información?

* El administrador del sistema.
* Se recomienda proteger esta tabla para lectura solo desde el backend o panel seguro.
* No debe ser visible al cliente.

---

### 🛠 ¿Se puede eliminar?

No, **se recomienda conservar esta tabla** ya que forma parte del sistema de verificación interna.
Puede integrarse con herramientas como:

* `/debug_info`
* `/debug_rutas`
* Paneles admin de estado técnico

---

🧩 Tabla: modulos_disponibles
📍 ¿Qué guarda?
Define qué módulos están activos o disponibles para cada Nora AI.
Esta tabla es la que permite que no todas las Noras tengan que usar todos los módulos del sistema.

🧠 ¿Para qué sirve?
Activar o desactivar módulos por Nora desde el panel administrador.

Controlar qué funcionalidades aparecen en el panel del cliente.

Mantener el sistema escalable sin tener que duplicar código.

📊 Campos principales (según el dump que subiste)
Campo	Tipo	Descripción
id	UUID	Identificador único
nombre_nora	Texto	Identificador lógico de la Nora (ej. aura)
modulo	Texto	Nombre interno del módulo (ej. chat, ia, crm, ads, etc.)
activo	Booleano	true si el módulo está habilitado, false si está desactivado

🔄 ¿Cómo se usa?
El sistema consulta esta tabla cada vez que va a renderizar el panel del cliente.

Solo muestra y habilita los módulos que tienen activo = true.

Se puede usar también desde el backend para decidir si permitir ciertas rutas o funciones.

💡 Ejemplos de valores válidos en modulo:
Nombre del módulo	Funcionalidad esperada
chat	Panel de conversación tipo WhatsApp
ia	Acceso a funciones de inteligencia artificial
contactos	Gestión de contactos desde el panel
envios	Envíos masivos o programados
ads	Módulo de campañas y anuncios
respuestas	Configuración de respuestas automáticas
conocimiento	Base de datos de conocimiento cargado por el cliente

🔐 ¿Quién puede modificar esta tabla?
Solo el administrador del sistema desde el panel de administración de Noras.
No debe estar expuesta al cliente.

🛠 ¿Cómo se llena?
Puede llenarse manualmente desde Supabase o desde el panel admin.

Cada Nora debe tener su set de módulos configurado explícitamente.

Si no existe una entrada para un módulo específico, se puede asumir inactivo por defecto.

✅ ¿Por qué es importante?
Permite que AuraAI2 escale sin romperse.

Hace posible vender paquetes diferentes de funcionalidades a cada cliente.

Es fundamental para el concepto de Nora modular y personalizada.

ChatGPT dijo:
¡Perfecto, ya con el dump de contactos_rows.sql, vamos con la tabla más usada del sistema!
Aquí va tu manual oficial de la tabla contactos, en el mismo formato que los anteriores.

👤 Tabla: contactos
📍 ¿Qué guarda?
Almacena la información de cada persona que ha escrito a una Nora vía WhatsApp.
Es la base del sistema CRM de AuraAI2.

🧠 ¿Para qué sirve?
Permite mostrar los contactos en el panel del cliente.

Guarda información relevante del último mensaje, nombre y etiquetas.

Permite a Nora decidir si responder con IA o manual.

Sirve como punto de entrada a historial, etiquetas y personalización.

📊 Campos principales (según tu estructura real)
Campo	Tipo	Descripción
id	UUID	Identificador único
telefono	Texto	Número de WhatsApp del contacto
nombre	Texto	Nombre del contacto (si se obtiene desde el perfil)
nombre_nora	Texto	Nora a la que pertenece el contacto
mensaje_reciente	Texto	Último mensaje recibido por este contacto
ultimo_mensaje	Timestamp	Fecha y hora del último mensaje
imagen_perfil	Texto	URL de la foto de perfil (si la manda WhatsApp)
etiquetas	Texto o JSON	Lista de etiquetas asignadas al contacto
created_at, updated_at	Timestamp	Fecha de creación y modificación automática

🔄 ¿Cómo se usa?
Se consulta desde:

panel_chat (para mostrar el nombre y último mensaje)

panel_cliente_contactos (lista y edición)

process_message.py (cuando llega un nuevo mensaje)

Se actualiza cada vez que se recibe un mensaje nuevo.

Se puede editar desde el panel para cambiar nombre, etiquetas o bloquear IA por contacto.

🛠 Funcionalidades basadas en esta tabla
Función	Se hace con esta tabla
Ver contactos en panel cliente	✅
Ordenar por último mensaje recibido	✅
Mostrar etiqueta en lista de contactos	✅
Mostrar foto de perfil	✅
Detectar nuevos contactos automáticamente	✅
Editar datos del contacto desde el panel	✅
Desactivar IA por contacto (en campo booleano si se agrega)

🧩 Sugerencias para mejorar
Agregar campo ia_activa (boolean)
→ para controlar fácilmente si Nora responde o no a este contacto.

Agregar campo notas (texto)
→ para que el cliente agregue detalles personalizados.

ChatGPT dijo:
¡Perfecto! Vamos ahora con la tabla historial_conversaciones, que cierra el ciclo de cada mensaje.

Aquí tienes la documentación completa para integrarla al manual de Supabase 👇

💬 Tabla: historial_conversaciones
📍 ¿Qué guarda?
Registra todos los mensajes recibidos y enviados por cada Nora AI, contacto por contacto.
Es el registro cronológico de la conversación.

🧠 ¿Para qué sirve?
Mostrar el historial en panel_chat (formato WhatsApp).

Generar contexto para la IA (handle_ai.py).

Permite reconstruir conversaciones pasadas para auditoría, reportes o análisis.

📊 Campos principales (según tu dump)
Campo	Tipo	Descripción
id	UUID	Identificador único del mensaje
telefono	Texto	Número del contacto
mensaje	Texto	Contenido textual del mensaje
tipo	Texto (usuario / respuesta)	Indica si fue enviado por el usuario o Nora
origen	Texto	Número de WhatsApp desde donde se envió
nombre_nora	Texto	Nora a la que pertenece el mensaje
fecha_hora	Timestamp	Fecha y hora exacta del mensaje

🔄 ¿Cómo se usa?
Cada vez que se recibe un mensaje, se guarda un nuevo registro con tipo = usuario.

Cada vez que Nora responde, se guarda otro registro con tipo = respuesta.

Este historial se usa para:

Mostrar el chat completo

Generar contexto de IA (conversación previa)

Guardar logs de soporte o marketing

✅ Beneficios de mantener esta tabla
Ventaja	Uso
Registro legal y técnico de interacciones	✅
Entrenamiento de IA personalizado	✅
Soporte técnico (ver lo que se dijo)	✅
Posibilidad de visualización cronológica en el panel	✅

ChatGPT dijo:
Perfecto, ahora vamos con la tabla que acabas de subir:

📊 meta_ads_cuentas
Esta tabla está enfocada en la integración de campañas publicitarias, específicamente con Meta Ads (Facebook e Instagram). Aquí tienes su ficha completa:

📊 Tabla: meta_ads_cuentas
📍 ¿Qué guarda?
Información sobre las cuentas publicitarias conectadas a cada Nora o cliente, con sus credenciales, tokens y estado de sincronización.

🧠 ¿Para qué sirve?
Permite vincular la cuenta de Meta Ads (Facebook) de cada cliente/Nora.

Almacena el token necesario para conectarse a la API de Meta y generar reportes automatizados.

Permite al módulo de campañas (panel_cliente_ads) mostrar estadísticas personalizadas.

📊 Campos principales (según tu dump real)
Campo	Tipo	Descripción
id	UUID	Identificador único
nombre_nora	Texto	A qué Nora está asociada la cuenta
cliente_id	Texto	ID del cliente dentro del sistema
access_token	Texto	Token de acceso a la API de Meta (usualmente temporal)
page_id	Texto	ID de la página de Facebook conectada
ad_account_id	Texto	ID de la cuenta publicitaria
activo	Boolean	Indica si la integración está activa
created_at, updated_at	Timestamp	Control automático de creación y cambios

🔄 ¿Cómo se usa?
Se consulta desde el módulo ads (panel_cliente_ads) para:

Conectar a Meta API

Mostrar campañas activas

Generar reportes automatizados (ej. gasto semanal, CTR, etc.)

También puede ser consultada por el admin para verificar el estado de conexión.

🔐 Seguridad
access_token debe estar protegido y nunca ser expuesto al frontend.

Se recomienda rotar el token o verificar su vigencia con Meta periódicamente.

ChatGPT dijo:
Perfecto, ya con el archivo logs_errores_rows.sql, cerramos la parte de registros técnicos.
Aquí tienes el análisis completo de la tabla logs_errores, ideal para el sistema de depuración de AuraAI2.

🐞 Tabla: logs_errores
📍 ¿Qué guarda?
Cada vez que ocurre un error en el sistema (OpenAI, Supabase, Twilio, SocketIO, etc.), se guarda un registro con detalles clave del incidente.

🧠 ¿Para qué sirve?
Tener un registro técnico de errores que ocurren en producción.

Visualizar errores desde el panel de administrador.

Poder filtrar por tipo de error y detectar patrones o fallas recurrentes.

Facilitar el debug sin depender de logs locales o consola.

📊 Campos principales (según tu dump)
Campo	Tipo	Descripción
id	UUID	Identificador único del error
tipo	Texto	Categoría del error (ej: IA, Supabase, OpenAI, Webhook, SocketIO)
descripcion	Texto	Mensaje del error
fecha_hora	Timestamp	Cuándo ocurrió el error
origen	Texto (opcional)	Módulo o función donde ocurrió
nombre_nora	Texto (opcional)	Nora relacionada (si aplica)

🔄 ¿Cómo se llena?
Se utiliza la función registrar_error(tipo, descripcion, nombre_nora=None, origen=None)

Esta función se llama desde múltiples lugares:

handle_ai.py (cuando falla la API de OpenAI)

process_message.py (errores en Supabase)

Webhook y otros módulos cuando hay fallas técnicas

🛠 Funcionalidades relacionadas
Uso	Resultado
Panel admin de errores	✅ Muestra errores categorizados
Filtros por tipo o Nora	✅ Posibles desde panel
Historial exportable para debug	✅ Sí, desde Supabase Studio

✅ Recomendaciones
Establecer una política de retención (ej. limpiar logs de más de 90 días).

Incluir un campo resuelto (booleano) para marcar errores ya tratados (si vas a usarlo en un sistema tipo soporte).

Crear una vista resumida en el panel de admin (/admin/debug).

ChatGPT dijo:
Perfecto, ahora cerramos con una de las tablas más importantes para el funcionamiento inteligente de Nora:

📚 Tabla: conocimiento_nora
📍 ¿Qué guarda?
Fragmentos de conocimiento cargado manualmente por el cliente o por el admin.
Esta base de conocimiento se integra al contexto cuando la IA responde preguntas del usuario.

🧠 ¿Para qué sirve?
Personaliza las respuestas de la IA según el negocio del cliente.

Permite que cada Nora tenga "su propia forma de pensar", con datos cargados desde su empresa.

Fortalece respuestas ante preguntas frecuentes (servicios, políticas, procesos, ubicación, etc.).

📊 Campos principales (según tu dump)
Campo	Tipo	Descripción
id	UUID	Identificador único
nombre_nora	Texto	Nora a la que pertenece este bloque
contenido	Texto	Información textual que se integrará como contexto
created_at, updated_at	Timestamp	Control automático de cambios

🔄 ¿Cómo se usa?
Al generar una respuesta con IA (handle_ai.py), el sistema llama a obtener_base_conocimiento(nombre_nora).

Se cargan todos los registros relacionados a esa Nora.

Se agregan al contexto como mensajes de tipo system para que OpenAI los tome en cuenta.

🛠 Funcionalidades relacionadas
Función	Descripción
Panel cliente IA > “Base de Conocimiento”	Permite agregar, editar o eliminar bloques
Panel admin de Noras	También puede gestionar conocimiento de cada Nora
Auditoría de respuestas	Permite saber de dónde salió la info que usó la IA

✅ Recomendaciones
Usar bloques breves y bien escritos (máximo 1000 caracteres cada uno).

Agregar validación para evitar contenido duplicado o vacío.

Si creas una función de búsqueda interna, usa este contenido como fuente base.

📦 Tablas Meta Ads – Gestión y Reportes
Aunque estas tablas están vacías actualmente, su estructura sugiere una intención clara para manejo de reportes, destinatarios y trazabilidad de campañas.

🧾 meta_ads_logs_cambios
¿Qué guarda?
Historial de cambios en campañas publicitarias: presupuesto, fecha, segmentación, etc.

¿Para qué sirve?

Auditar modificaciones hechas desde el panel

Registrar ediciones de campañas ejecutadas por el cliente o admin

Mantener trazabilidad ante ajustes inesperados

¿Quién lo usa?
Panel admin, módulo ads

👥 meta_ads_receptores
¿Qué guarda?
Personas o entidades que deben recibir el reporte de campañas.

¿Para qué sirve?

Enviar automáticamente el resumen de campañas a los correos correctos

Determinar si el cliente quiere que el reporte vaya a él, a su cliente final, o a ambos

¿Quién lo usa?
Módulo ads, programador de reportes (apscheduler)

📈 meta_ads_reportes
¿Qué guarda?
Los reportes generados automáticamente por el sistema con datos de Meta Ads.

¿Para qué sirve?

Mostrar histórico de rendimiento publicitario en el panel

Archivar cada envío realizado

Permitir descarga o reenvío del reporte desde el panel

¿Quién lo usa?
Cliente desde panel_cliente_ads, y admin desde /admin/ads

🧠 Sugerencias generales
Tabla	Acción recomendada
meta_ads_logs_cambios	Mantener activa – útil para auditoría interna
meta_ads_receptores	Usar con lógica clara de a quién se reporta cada campaña
meta_ads_reportes	Mantener – base para resumen histórico del panel de Ads

