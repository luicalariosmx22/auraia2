# Guía de Configuración de Google Ads API

Este documento proporciona instrucciones paso a paso para configurar la integración con Google Ads API desde cero.

## 1. Requisitos Previos

Antes de comenzar, necesitas:

- Una cuenta de Google Ads con acceso administrativo
- Un proyecto en Google Cloud Platform (GCP)
- Una cuenta de Supabase configurada

## 2. Crear Proyecto en Google Cloud Platform

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Activa la API de Google Ads en "APIs y servicios > Biblioteca"
4. Configura las credenciales de OAuth:
   - Ve a "APIs y servicios > Credenciales"
   - Haz clic en "Crear credenciales" y selecciona "ID de cliente de OAuth"
   - Selecciona "Aplicación web" como tipo
   - Agrega URLs de redirección autorizadas (incluyendo `http://localhost:8080/oauth2callback` para desarrollo)
   - Toma nota del Client ID y Client Secret generados

## 3. Obtener Developer Token de Google Ads

1. Inicia sesión en tu [cuenta de Google Ads](https://ads.google.com/)
2. Ve a "Herramientas y configuración > Configuración > API Center"
3. Solicita un developer token si no lo tienes
4. Una vez aprobado, toma nota del Developer Token

## 4. Crear Tabla en Supabase

Existen dos formas de crear la tabla necesaria:

### Opción 1: Usando el Script SQL

1. Accede al panel de control de tu proyecto en Supabase
2. Ve a "SQL Editor"
3. Copia y pega el contenido del archivo `scripts/crear_tabla_google_ads_config.sql`
4. Ejecuta el script

### Opción 2: Usando el Script Python

1. Ejecuta el script de configuración:
   ```bash
   python configurar_google_ads.py
   ```
2. Sigue las instrucciones para crear la tabla manualmente en la consola de Supabase

## 5. Configurar Credenciales

1. Ejecuta el script de configuración (si no lo has hecho ya):
   ```bash
   python configurar_google_ads.py
   ```
2. Ingresa cuando se te solicite:
   - Client ID de OAuth (de GCP)
   - Client Secret de OAuth (de GCP)
   - Developer Token (de Google Ads)
   - Login Customer ID (opcional, el ID del MCC si lo usas)

## 6. Obtener Token de Acceso

1. Ejecuta el script para renovar el token:
   ```bash
   python renovar_token_google_ads.py --renew-token
   ```
2. Se abrirá un navegador web para autorizar la aplicación
3. Inicia sesión con la cuenta de Google asociada a tu cuenta de Google Ads
4. Autoriza los permisos solicitados
5. El token se guardará automáticamente en la base de datos

## 7. Verificar la Configuración

1. Ejecuta el diagnóstico para confirmar que todo está configurado correctamente:
   ```bash
   python diagnostico_token_google_ads.py
   ```
2. Deberías ver un mensaje confirmando que el token es válido y se pueden listar cuentas

## 8. Prueba la Integración

1. Ve a la interfaz web del panel de Google Ads
2. Haz clic en el botón "Actualizar datos últimos 7 días"
3. Verifica que los datos se actualicen correctamente

## Solución de Problemas

### Si la tabla no se crea correctamente

- Verifica los permisos en Supabase
- Intenta ejecutar el SQL manualmente en la consola de Supabase
- Asegúrate de que la extensión uuid-ossp está habilitada

### Si el token no se obtiene correctamente

- Verifica que el Client ID y Client Secret sean correctos
- Asegúrate de que las URLs de redirección en GCP incluyen `http://localhost:8080/oauth2callback`
- Revisa los logs para ver si hay errores específicos

### Si la actualización de datos falla

- Ejecuta el diagnóstico para verificar el estado del token
- Revisa los logs del servidor para ver errores detallados
- Asegúrate de que el Developer Token es válido y está aprobado para producción

## Referencias

- [Documentación oficial de Google Ads API](https://developers.google.com/google-ads/api/docs/start)
- [OAuth 2.0 para aplicaciones web](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Guía de Supabase para SQL](https://supabase.com/docs/guides/database/sql-queries)
