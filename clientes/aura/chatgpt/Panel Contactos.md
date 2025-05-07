Perfecto, vamos con el siguiente:

---

## 📦 Módulo: `panel_cliente_contactos`

---

### 📍 **Ubicación**

`clientes/aura/routes/panel_cliente_contactos/`

---

### 🧠 **¿Qué hace?**

Este módulo gestiona la **lista de contactos del cliente**, vinculada a su Nora. Desde aquí se pueden:

* Ver todos los contactos registrados por la Nora
* Editar información del contacto
* Asignar o quitar etiquetas
* Ver estado de la IA por contacto (activada/desactivada)
* Activar/desactivar IA manualmente para cada contacto

---

### 👥 **¿Quién lo usa?**

🟢 **Cliente**

---

### 🔁 **¿Es dinámico por Nora?**

✅ Sí
Se registra desde `registro_dinamico.py` con la ruta:

```
/panel_cliente/<nombre_nora>/contactos
```

---

### 📄 **Vista esperada**

* Tabla o lista de contactos
* Filtros por etiquetas
* Botón para ver detalles del contacto
* Botón para desactivar IA individualmente
* Indicador de última interacción (último mensaje recibido)

---

### 🔗 Ruta esperada

```
/panel_cliente/<nombre_nora>/contactos
```

---

### ⚙️ Funciones clave disponibles

| Función                                            | Estado                  |
| -------------------------------------------------- | ----------------------- |
| Ver listado completo de contactos                  | ✅                       |
| Editar nombre/número/notas                         | ✅                       |
| Ver/administrar etiquetas                          | ✅                       |
| Desactivar IA solo para un contacto                | ✅                       |
| Buscar contacto por nombre o número                | ⚠️ (opcional, sugerido) |
| Ver historial de conversación (link a panel\_chat) | ✅                       |

---

### 📂 Archivos relacionados

* `vista_panel_cliente_contactos.py`
* Función desde `panel_cliente_contactos_bp`

---

¿Pasamos ahora a `panel_cliente_envios` o quieres incluir IA o respuestas primero?
