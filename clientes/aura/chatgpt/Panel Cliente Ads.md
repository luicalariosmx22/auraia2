¡Perfecto! Vamos con el módulo `panel_cliente_ads`, que forma parte del sistema de campañas gestionadas para cada Nora.

---

## 📦 Módulo: `panel_cliente_ads`

---

### 📍 **Ubicación**

`clientes/aura/routes/panel_cliente_ads/`
(*y también está conectado a* `clientes/aura/modules/ads.py`)

---

### 🧠 **¿Qué hace?**

Este módulo muestra al cliente un panel de anuncios donde puede:

* Ver el estado de sus campañas activas
* Ver resultados de campañas en Meta Ads, Google Ads, etc.
* Consultar reportes automatizados generados por Nora
* Visualizar estadísticas de inversión, alcance, interacciones

---

### 👥 **¿Quién lo usa?**

🟢 **Cliente**, dentro de su panel Nora.

---

### 🔁 **¿Es dinámico por Nora?**

✅ Sí, se registra desde `registro_dinamico.py`, **pero de forma especial**:
En lugar de ser un blueprint completo, se registra usando `app.add_url_rule(...)` porque comparte lógica con `ads_bp` (el módulo central de campañas).

---

### 🧩 ¿Por qué se registra así?

Porque **`ads_bp` es un módulo compartido entre Noras**, pero la vista se personaliza por cada `nombre_nora`, así que se registra como:

```python
/panel_cliente/<nombre_nora>/ads
```

con el endpoint personalizado:

```python
endpoint = f"{nombre_nora}_ads"
```

Esto evita que Flask intente registrar dos veces el mismo blueprint si varias Noras están activas.

---

### 🌐 **Ruta esperada**

```
/panel_cliente/<nombre_nora>/ads
```

---

### 📄 **Vista esperada**

* Gráficas de campañas
* KPIs por plataforma (Meta, Google, YouTube, etc.)
* Histórico de inversión
* Mensajes de Nora con recomendaciones
* Posible botón para solicitar nueva campaña (futuro)

---

### 📂 Archivos relacionados

* `panel_cliente_ads.py` → vista por Nora
* `modules/ads.py` → lógica compartida para todas las Noras (reportes, estadísticas, etc.)

---

### ⚙️ Funciones clave disponibles

| Función                           | Estado                |
| --------------------------------- | --------------------- |
| Ver campañas activas              | ✅                     |
| Ver estadísticas por plataforma   | ✅                     |
| Ver inversión semanal/mensual     | ✅                     |
| Consultar recomendaciones de Nora | ⚠️ (opcional)         |
| Solicitar nueva campaña           | ❌ (sugerido a futuro) |

---

¿Pasamos a `panel_cliente_envios` o prefieres revisar `panel_cliente_respuestas` o `panel_cliente_ia`?
