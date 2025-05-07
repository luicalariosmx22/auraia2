Excelente 🔥, vamos con el módulo **`panel_cliente`**, que es la entrada principal al CRM de cada Nora.

---

## 📦 Módulo: `panel_cliente`

---

### 📍 **Ubicación**

`clientes/aura/routes/panel_cliente/`

---

### 🧠 **¿Qué hace?**

Es el **módulo principal del cliente** al entrar a su panel. Funciona como “home” de la Nora asignada y normalmente muestra:

* Configuración inicial de la Nora
* Vista general del estado de la cuenta
* Accesos a los demás módulos: CRM, IA, envíos, etiquetas, etc.

> *Es como el "escritorio" del cliente cuando inicia sesión.*

---

### 👥 **¿Quién lo usa?**

🟢 **Cliente**, individualmente, asociado a una Nora específica.

---

### 🔁 **¿Es dinámico por Nora?**

✅ Sí, se registra en `registro_dinamico.py` con prefijo:

```
/panel_cliente/<nombre_nora>
```

---

### 📄 **Vista esperada**

* Muestra el nombre de la Nora en uso
* Muestra el nombre del usuario
* Panel con accesos rápidos a:

  * Chat
  * Contactos
  * IA
  * Etiquetas
  * Envíos
  * Estadísticas (opcional por Nora)
* Información general del sistema (estado de conexión IA, estado Twilio, etc.)

---

### 🛠 Funcionalidades relacionadas

Este módulo **no maneja lógica por sí solo**, pero es el punto de entrada que se comunica con:

* `panel_chat`
* `panel_cliente_contactos`
* `panel_cliente_ia`
* `panel_cliente_respuestas`
* `panel_cliente_envios`
* `panel_cliente_conocimiento`
* etc.

---

### 🔗 Ruta esperada

```
/panel_cliente/<nombre_nora>
```

---

### 📂 Archivos relacionados

* `vista_panel_cliente.py` (o similar dentro del módulo)
* Se registra como `panel_cliente_bp`

---

### ✅ ¿Qué se puede hacer desde aquí?

| Acción                                  | Estado        |
| --------------------------------------- | ------------- |
| Ver nombre de Nora                      | ✅             |
| Ver datos del cliente                   | ✅             |
| Acceder a módulos CRM                   | ✅             |
| Configurar comportamiento de Nora       | ⚠️ (opcional) |
| Estado de IA / Conexión / Integraciones | ✅             |

---
