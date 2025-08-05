# Documentación del Módulo Meta Ads

## Estructura General

### Frontend (Templates)
#### 1. Vista Principal (`reportes_meta_ads.html`)
- **Ubicación**: `/templates/reportes_meta_ads/reportes_meta_ads.html`
- **Funcionalidad**: 
  - Página principal del módulo Meta Ads
  - Muestra lista de reportes generados
  - Botones para generar nuevos reportes
  - Vista general de todos los reportes disponibles

#### 2. Vista de Estadísticas (`estadisticas_ads.html`)
- **Ubicación**: `/templates/reportes_meta_ads/estadisticas_ads.html`
- **Funcionalidad**:
  - Muestra estadísticas detalladas y gráficas
  - Botones para:
    - Generar/Actualizar reportes
    - Eliminar reportes
    - Actualizar nombres de empresas
  - Gráficas de gastos e impresiones

### JavaScript
#### 1. Estadísticas (`estadisticas_ads.js`)
- **Ubicación**: `/static/js/estadisticas_ads.js`
- **Funcionalidades**:
  - Carga automática de estadísticas
  - Manejo de reportes (generación, eliminación)
  - Actualización de nombres de empresas
  - Generación de gráficas con Chart.js
  - Manejo de interacciones de usuario
  - Llamadas a la API

### Backend (Python)
#### 1. Vistas Principales (`vistas.py`)
- **Ubicación**: `/routes/reportes_meta_ads/vistas.py`
- **Endpoints**:
  - `/panel_cliente/<nombre_nora>/meta_ads/`: Vista principal de reportes
  - `/estadisticas/<nombre_nora>`: Vista de estadísticas
  - `/descargar/<reporte_id>/<nombre_nora>`: Descarga de reportes

## Rutas API y Endpoints

### Endpoints Principales
1. **Vista Principal Meta Ads**
   ```
   GET /panel_cliente/<nombre_nora>/meta_ads/
   ```
   - Muestra la lista de reportes y opciones principales

2. **Estadísticas**
   ```
   GET /panel_cliente/<nombre_nora>/meta_ads/estadisticas
   ```
   - Muestra gráficas y estadísticas detalladas

3. **Descarga de Reportes**
   ```
   GET /panel_cliente/<nombre_nora>/meta_ads/descargar/<reporte_id>
   ```
   - Descarga reportes específicos

### Endpoints de Acciones
1. **Generación de Reportes**
   ```
   POST /panel_cliente/<nombre_nora>/meta_ads/estadisticas
   ```
   - Genera un nuevo reporte

2. **Eliminación de Reportes**
   ```
   POST /panel_cliente/<nombre_nora>/meta_ads/estadisticas/eliminar_reportes
   ```
   - Elimina todos los reportes

3. **Actualización de Nombres**
   ```
   POST /panel_cliente/<nombre_nora>/meta_ads/estadisticas/actualizar_nombres_empresas
   ```
   - Actualiza nombres de empresas en reportes

## Flujo de Datos

1. **Generación de Reportes**
   - Usuario solicita generar reporte
   - Backend consulta API de Meta Ads
   - Datos se procesan y almacenan en Supabase
   - Frontend actualiza vista con nuevos datos

2. **Visualización de Estadísticas**
   - Frontend solicita datos
   - Backend consulta Supabase
   - Datos se procesan y formatean
   - Frontend genera gráficas y tablas

## Tablas en Supabase

1. **meta_ads_reportes**
   - Almacena reportes generados
   - Campos principales:
     - id
     - nombre_nora
     - fecha_generacion
     - tipo_reporte
     - datos_reporte

2. **meta_ads_cuentas**
   - Almacena información de cuentas publicitarias
   - Campos principales:
     - id
     - nombre_nora
     - id_cuenta_publicitaria
     - nombre_empresa

## Flujo de Trabajo Típico

1. Usuario accede a la vista principal
2. Puede:
   - Ver reportes existentes
   - Generar nuevos reportes
   - Ver estadísticas detalladas
   - Actualizar nombres de empresas
   - Descargar reportes específicos

## Manejo de Errores

- Errores de API se capturan y muestran en la UI
- Logs detallados para debugging
- Mensajes de error amigables para el usuario
- Fallbacks para datos no disponibles

## Dependencias

- **Frontend**:
  - Chart.js para gráficas
  - TailwindCSS para estilos
  - Font Awesome para iconos

- **Backend**:
  - Flask para el servidor
  - Supabase para base de datos
  - Facebook Business SDK para API de Meta Ads

## Notas de Mantenimiento

- Los reportes se almacenan permanentemente en Supabase
- La actualización de nombres es manual pero puede automatizarse
- Las gráficas se regeneran en cada carga
- Los logs ayudan en el debugging
