# Botón de Actualización de Google Ads

Este documento explica cómo integrar y utilizar el botón de actualización de datos de Google Ads en el panel de administración.

## Descripción

El botón de actualización de Google Ads permite a los usuarios actualizar manualmente los datos de Google Ads de los últimos 7 días con un solo clic. Esto es útil para ver los datos más recientes sin esperar a la actualización automática semanal.

## Componentes Implementados

### Backend

1. **Endpoint**: `/api/google-ads/actualizar-ultimos-7-dias` (POST)
   - Ubicación: `routes/google_ads.py`
   - Función: `actualizar_ultimos_7_dias_endpoint()`
   - Parámetros JSON opcionales:
     - `incluir_mcc`: Boolean (default: false)
     - `incluir_anuncios`: Boolean (default: true)

2. **Función de actualización**: 
   - Ubicación: `actualizar_google_ads_cuentas.py`
   - Función: `actualizar_ultimos_7_dias()`
   - Actualiza los datos de Google Ads de los últimos 7 días

### Frontend

1. **Componente JavaScript**:
   - Ubicación: `static/js/components/google_ads_update_button.js`
   - Clase: `GoogleAdsUpdateButton`
   - Crea un botón que, al hacer clic, llama al endpoint para actualizar los datos

2. **Ejemplo de integración**:
   - Ubicación: `templates/components/google_ads_update_button_example.html`
   - Muestra cómo integrar el botón en una página existente

## Integración en una Página Existente

Para añadir el botón a una página existente:

1. **HTML**: Añadir un contenedor para el botón

```html
<!-- Contenedor para el botón de actualización -->
<div id="google-ads-update-container" class="mb-3">
    <!-- El botón se generará aquí mediante JavaScript -->
</div>
```

2. **JavaScript**: Cargar e inicializar el componente

```html
<!-- Cargar el script del componente -->
<script src="/static/js/components/google_ads_update_button.js"></script>

<!-- Inicializar el componente -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Inicializar el botón de actualización
        const updateButton = new GoogleAdsUpdateButton('google-ads-update-container');
    });
</script>
```

## Flujo de Funcionamiento

1. El usuario hace clic en el botón "Actualizar datos últimos 7 días"
2. Se muestra un diálogo de confirmación
3. Se envía una petición al endpoint `/api/google-ads/actualizar-ultimos-7-dias`
4. El botón se deshabilita y muestra un indicador de carga
5. El endpoint procesa la petición y actualiza los datos de Google Ads
6. Se muestra un mensaje con el resultado de la actualización
7. Se notifica al usuario que debe actualizar la página para ver los cambios

## Pruebas

Para probar el endpoint sin usar el frontend:

1. Ejecutar el script de prueba: `python test_endpoint_actualizar_7_dias.py`
2. Verificar la respuesta del endpoint

## Notas Adicionales

- El proceso de actualización puede tardar varios minutos dependiendo de la cantidad de cuentas y datos.
- Se generan logs detallados en la carpeta `logs` con el formato `google_ads_actualizacion_endpoint_YYYYMMDD_HHMMSS.log`.
- Se generan informes en formato JSON en la carpeta `informes` con el formato `google_ads_informe_endpoint_YYYYMMDD_HHMMSS.json`.
