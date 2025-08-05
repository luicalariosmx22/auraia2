# 🧩 Webhook Meta - Primeros pasos

## ✅ Introducción

Este documento explica cómo iniciar y verificar correctamente un **webhook** de Meta desde tu app en desarrollo. Incluye los pasos básicos para configuración, validación y pruebas.

---

## 1️⃣ Configurar el Webhook en el Dashboard

1. Ingresa a [https://developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Selecciona tu App > Producto: **Webhooks**
3. Selecciona un objeto (por ejemplo, `Ad Account` o `Page`)
4. Define:
   - **URL de devolución de llamada** → `https://<TU_DOMINIO>/meta/webhook`
   - **Token de verificación** → `<TU_TOKEN_PERSONALIZADO>`

---

## 2️⃣ Implementar la verificación inicial

Cuando configures el webhook, Meta enviará una solicitud `GET` para verificar que tu servidor está activo.

Ejemplo de solicitud:

