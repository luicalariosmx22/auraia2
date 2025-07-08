# 📁 Estructura de Registro de Blueprints en AuraAI2

Este archivo documenta cómo se organiza el registro de blueprints dentro del proyecto **AuraAI2**, utilizando una arquitectura modular por tipo de funcionalidad.

Cada archivo de la carpeta `registro/` tiene una única responsabilidad clara, lo cual permite mantener el código limpio, escalable y fácil de extender.

---

## 🧭 Objetivo de cada archivo

---

### 🔐 `registro_login.py`

- **Función:** Manejar el login con Google y controlar acceso según tipo de usuario.
- **Incluye:** `login_bp`
- **Rutas típicas:**  
  `/login`

---

### 🌐 `registro_invitado.py`

- **Función:** Mostrar landings, demos u otras páginas accesibles sin iniciar sesión.
- **Incluye:** `landing_bp` (u otros públicos)
- **Rutas típicas:**  
  `/`, `/demo`

---

### 🧱 `registro_base.py`

- **Función:** Registrar funcionalidades globales que no dependen de roles o Noras.
- **Incluye:** `webhook_bp`
- **Rutas típicas:**  
  `/webhook`

---

### 🛠️ `registro_admin.py`

- **Función:** Registrar todas las herramientas internas de administración del sistema y las Noras.
- **Incluye:**  
  - `admin_noras_bp`  
  - `admin_nora_bp`  
  - `admin_dashboard_bp`  
  - `admin_nora_dashboard_bp`  
  - `admin_debug_master_bp`  
  - `admin_actualizar_contactos_bp`
- **Rutas típicas:**  
  `/admin/...`

---

### 🧪 `registro_debug.py`

- **Función:** Registrar herramientas de diagnóstico del sistema (OpenAI, Supabase, etc.)
- **Incluye:** `debug_verificar_bp`
- **Rutas típicas:**  
  `/debug/verificar`, `/debug_info`

---

### 🤖 `registro_dinamico.py`

- **Función:** Registrar rutas dinámicas del panel de cliente para cada Nora AI (`nombre_nora`).
- **Incluye:**  
  - `panel_cliente_bp`  
  - `panel_cliente_contactos_bp`  
  - `panel_cliente_envios_bp`  
  - `panel_cliente_ia_bp`  
  - `panel_cliente_respuestas_bp`  
  - `etiquetas_bp`  
  - `panel_chat_bp`  
  - `panel_cliente_conocimiento_bp`  
  - `panel_cliente_ads_bp` (como URL personalizada)
- **Rutas típicas:**  
  `/panel_cliente/<nombre_nora>/...`

---

## ❌ `registro_comercial.py` (Eliminado)

- **Motivo:** Todas las rutas originalmente previstas aquí ya se gestionan dinámicamente por Nora.
- **Resultado:** Eliminado para evitar duplicación de rutas y mantener una arquitectura limpia.

---

## 🧩 Consideraciones para `app.py`

- `app.py` no debe registrar rutas directamente.
- Solo debe importar y ejecutar funciones como:  
  ```python
  registrar_blueprints_admin(app, safe_register_blueprint)
  registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint)
