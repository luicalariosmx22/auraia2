# 📊 Google Ads SQL Generator - Guía de Usuario

## 🚀 Introducción

Este sistema te permite convertir reportes de Google Ads (Excel) a SQL optimizado para Supabase, manteniendo automáticamente las relaciones jerárquicas entre campañas, anuncios y palabras clave.

## 🎯 Características Principales

- ✅ **Procesamiento Individual**: Convierte un archivo a la vez
- ✅ **Procesamiento Múltiple**: Procesa 3 archivos y mantiene relaciones automáticamente
- ✅ **Inserción Automática a Supabase**: Un solo clic para insertar todos los datos
- ✅ **IA Inteligente**: Mapeo automático de columnas usando OpenAI GPT-4
- ✅ **Relaciones Jerárquicas**: Mantiene automáticamente las FK entre tablas
- ✅ **Filtrado Automático**: Elimina filas de totales y resúmenes

## 📋 Prerrequisitos

1. **Python 3.8+** instalado
2. **Variables de entorno configuradas** en `.env`:
   ```
   OPENAI_API_KEY=tu_api_key_de_openai
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_ANON_KEY=tu_clave_de_supabase
   ```
3. **Tablas de Supabase** creadas con las columnas correctas

## 🛠️ Instalación

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno en `.env`

3. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

4. Abrir en navegador: `http://localhost:5001`

## 📁 Tipos de Archivos Soportados

### 📈 Campañas (136 columnas)
- Presupuesto, estrategias de puja, métricas de conversión
- Datos de share metrics y atribución
- Configuraciones de audiencias y ubicaciones

### 📺 Anuncios (65 columnas)
- Títulos, descripciones, URLs
- Métricas de rendimiento y calidad
- Estados y aprobaciones

### 🔑 Palabras Clave (21 columnas)
- Keywords, tipos de concordancia
- Métricas de rendimiento
- Pujas y URLs de destino

## 🎮 Modos de Uso

### Modo 1: Archivo Individual
1. Seleccionar "Archivo Individual"
2. Arrastrar o seleccionar tu archivo Excel
3. Elegir tipo de tabla de destino
4. Seleccionar generador (IA o Simple)
5. Hacer clic en "Generar SQL"
6. Descargar el archivo SQL generado

### Modo 2: Múltiples Archivos + Supabase
1. Seleccionar "Múltiples Archivos + Supabase"
2. Subir los 3 archivos (campañas, anuncios, palabras clave)
3. Hacer clic en "Procesar Todos los Archivos"
4. **Opcional**: Descargar los SQL files generados
5. Hacer clic en "Insertar a Supabase"

## 🔄 Flujo de Relaciones Jerárquicas

El sistema mantiene automáticamente las relaciones:

```
📈 Campañas (tabla principal)
├── 📂 Grupos de Anuncios
    ├── 📺 Anuncios (FK a Campaña)
    └── 🔑 Palabras Clave (FK a Campaña)
```

### Campos de Relación Automática
- `campaign_id` / `id_campaña`: Conecta todo con la campaña
- `ad_group_id` / `id_grupo_anuncios`: Agrupa anuncios y keywords
- La IA detecta automáticamente estas columnas

## 🧠 Generador con IA vs Simple

### 🤖 Generador con IA (Recomendado)
- **Ventajas**: Mapeo automático inteligente, detecta relaciones
- **Usa**: OpenAI GPT-4 para analizar columnas
- **Ideal para**: Archivos con columnas no estándar

### ⚡ Generador Simple
- **Ventajas**: Más rápido, sin costo de API
- **Usa**: Mapeo predefinido de columnas conocidas
- **Ideal para**: Archivos estándar de Google Ads

## 📊 Datos de Ejemplo

Puedes generar archivos de demo con:
```bash
python create_demo_files.py
```

Esto crea:
- `demo_campaigns.xlsx` (3 campañas)
- `demo_ads.xlsx` (7 anuncios)
- `demo_keywords.xlsx` (8 palabras clave)

## 🔧 Solución de Problemas

### Error: "Cliente de Supabase no disponible"
```bash
pip install supabase
```

### Error: "No se encontraron INSERT statements"
- Verifica que el archivo Excel tenga datos válidos
- Asegúrate de que no esté corrupto
- Verifica que tenga la estructura esperada

### Error de conexión a Supabase
- Verifica las variables de entorno en `.env`
- Confirma que las tablas existan en Supabase
- Verifica permisos de la API key

### Archivos muy grandes
- Límite actual: 16MB por archivo
- Para archivos más grandes, procesa en lotes

## 📋 Estructura de Tablas en Supabase

### google_ads_campañas
```sql
- id_campaña (TEXT, PRIMARY KEY)
- nombre_campaña (TEXT)
- presupuesto (NUMERIC)
- estado_campaña (TEXT)
- ... (133+ columnas más)
```

### google_ads_reporte_anuncios  
```sql
- id_anuncio (TEXT)
- id_campaña (TEXT, FOREIGN KEY)
- titular_1 (TEXT)
- descripcion_1 (TEXT)
- ... (62+ columnas más)
```

### google_ads_palabras_clave
```sql
- palabra_clave (TEXT)
- id_campaña (TEXT, FOREIGN KEY)
- tipo_concordancia (TEXT)
- puja_cpc (NUMERIC)
- ... (18+ columnas más)
```

## 🚨 Consideraciones Importantes

1. **Backup**: Siempre respalda tus datos antes de usar "Limpiar Tablas"
2. **Límites**: Respeta los límites de rate de Supabase
3. **Relaciones**: Las FK se mantienen automáticamente, no las modifiques manualmente
4. **Filtrado**: Los totales se eliminan automáticamente para evitar duplicados

## 📞 Soporte

Si encuentras problemas:
1. Verifica los logs de la consola del navegador
2. Revisa los logs del servidor Python
3. Confirma la configuración de variables de entorno
4. Verifica que las tablas de Supabase estén creadas correctamente

## 🔄 Actualizaciones

El sistema está diseñado para:
- Agregar nuevos tipos de reportes de Google Ads
- Soportar otras fuentes de datos (Facebook Ads, etc.)
- Conectar con otras bases de datos (PostgreSQL, MySQL, etc.)

---

**¡Disfruta convirtiendo tus datos de Google Ads a SQL de manera inteligente! 🎉**
