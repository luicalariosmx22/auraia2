# Google Ads Excel to SQL Generator con Relaciones Jerárquicas

Este proyecto contiene scripts para convertir archivos Excel de Google Ads en sentencias SQL INSERT para tablas de Supabase, **manteniendo automáticamente las relaciones jerárquicas** entre campañas, grupos de anuncios, anuncios y palabras clave.

## 🌐 **NUEVO: Interfaz Web con Detección Automática de Relaciones**

¡Ahora disponible con una interfaz web moderna en `http://localhost:5001` que **detecta automáticamente las relaciones jerárquicas**!

### 🚀 Inicio Rápido Web
```bash
# Doble clic en:
run_web.bat

# O desde PowerShell:
python app.py
```

**Características del Frontend:**
- ✅ Interfaz drag & drop para archivos Excel
- ✅ Selección de generador (IA vs Simple)
- ✅ **NUEVO: Detección automática de relaciones jerárquicas**
- ✅ Generación automática de IDs relacionales (`id_campaña`, `id_grupo_anuncios`, `id_anuncio`, `id_palabra_clave`)
- ✅ Soporte para múltiples tipos de tabla (Campañas, Anuncios, Palabras Clave)
- ✅ Vista previa del SQL generado
- ✅ Descarga directa de archivos
- ✅ Testing integrado
- ✅ Responsive design
- ✅ Indicadores de estado en tiempo real

## 🔗 **NUEVA FUNCIONALIDAD: Relaciones Jerárquicas Automáticas**

El sistema ahora detecta automáticamente las relaciones jerárquicas en los datos de Google Ads:

### 📊 **Estructura Jerárquica Soportada:**
```
📈 CAMPAÑA (1)
├── 📂 GRUPO DE ANUNCIOS (1.1)
│   ├── 📺 ANUNCIO (1.1.1)
│   ├── 📺 ANUNCIO (1.1.2)
│   ├── 🔑 PALABRA CLAVE (1.1.3)
│   └── 🔑 PALABRA CLAVE (1.1.4)
└── 📂 GRUPO DE ANUNCIOS (1.2)
    ├── 📺 ANUNCIO (1.2.1)
    └── 🔑 PALABRA CLAVE (1.2.2)
```

### 🆔 **IDs Relacionales Generados Automáticamente:**
- **`id_campaña`**: ID único para cada campaña
- **`id_grupo_anuncios`**: ID único para cada grupo de anuncios
- **`id_anuncio`**: ID único para cada anuncio (solo en tabla de anuncios)
- **`id_palabra_clave`**: ID único para cada palabra clave (solo en tabla de palabras clave)

### 🧠 **Detección Inteligente:**
La IA detecta automáticamente:
- ✅ Nombres de campañas en columnas como "Campaign", "Campaña", "Campaign name"
- ✅ Nombres de grupos de anuncios en columnas como "Ad group", "Grupo de anuncios", "AdGroup"
- ✅ Identificadores únicos de anuncios (títulos, URLs, tipos)
- ✅ Palabras clave en columnas como "Keyword", "Palabra clave"

### 🎯 **Tipos de Tabla Soportados:**
1. **📈 Campañas** (136 columnas) - `google_ads_campañas`
2. **📺 Anuncios** (65 columnas) - `google_ads_reporte_anuncios`  
3. **🔑 Palabras Clave** (21 columnas) - `google_ads_palabras_clave`

## 📁 Archivos

### 🌐 **Frontend Web:**
- **`app.py`** - Aplicación Flask principal
- **`templates/`** - Plantillas HTML
- **`static/`** - Archivos CSS y JS
- **`run_web.bat`** - Ejecutor rápido para Windows

### 🖥️ **CLI (Línea de comandos):**
1. **`google_ads_sql_generator.py`** - Script completo con IA
2. **`simple_excel_to_sql.py`** - Versión simplificada sin IA  
3. **`main.py`** - Interfaz de menú CLI

### 🔧 **Configuración:**
4. **`requirements.txt`** - Dependencias de Python
5. **`.env`** - Variables de entorno
6. **`run.bat`** - Script CLI para Windows

### 📚 **Testing y documentación:**
7. **`test_generators.py`** - Suite de pruebas
8. **`README.md`** - Esta documentación

## 🚀 Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Edita el archivo `.env` y agrega tu API key de OpenAI:
```
OPENAI_API_KEY=tu_api_key_aqui
```

## 💻 Uso

### 🌐 Opción 1: Interfaz Web (Recomendado)
```bash
# Windows:
run_web.bat

# O manualmente:
python app.py
```

Luego ve a: `http://localhost:5001`

### 🖥️ Opción 2: Línea de comandos

#### Con IA (Recomendado)
```bash
python google_ads_sql_generator.py
```

#### Simple (Sin IA)
```bash
python simple_excel_to_sql.py
```

#### Menú interactivo
```bash
python main.py
```

## 📊 Tablas de destino con relaciones

### 📈 **Tabla Campañas** (`google_ads_campañas`)
**136 columnas** incluyendo:
- **Relaciones:** `id_campaña` (PK)
- **Estados:** estado_campaña, estado, motivos_estado  
- **Presupuesto:** presupuesto, nombre_presupuesto, tipo_presupuesto
- **Estrategia:** estrategia_oferta, cpa_objetivo, roas_objetivo
- **Métricas:** impresiones, clics, ctr, costo, conversiones, etc.

### 📺 **Tabla Anuncios** (`google_ads_reporte_anuncios`)
**65 columnas** incluyendo:
- **Relaciones:** `id_campaña` (FK), `id_grupo_anuncios` (FK), `id_anuncio` (PK)
- **Estados:** estado_anuncio, estado, motivos_estado
- **URLs:** url_final, url_final_movil, plantilla_seguimiento
- **Títulos:** titulo_1 a titulo_15 con sus posiciones
- **Descripciones:** descripcion_1 a descripcion_4 con posiciones
- **Rutas:** ruta_1, ruta_2
- **Configuración:** campaña, grupo_anuncios, tipo_anuncio
- **Métricas:** clics, impresiones, ctr, costo, conversiones, etc.

### 🔑 **Tabla Palabras Clave** (`google_ads_palabras_clave`)
**21 columnas** incluyendo:
- **Relaciones:** `id_campaña` (FK), `id_grupo_anuncios` (FK), `id_palabra_clave` (PK)
- **Identificación:** palabra_clave, tipo_concordancia
- **Configuración:** campaña, grupo_anuncios, estado
- **URLs:** url_final, url_final_movil
- **Métricas:** impresiones, clics, ctr, costo, conversiones, etc.

## 🔄 Proceso con Detección de Relaciones

1. **Lectura:** El script lee el archivo Excel
2. **Análisis:** OpenAI analiza la estructura y mapea columnas
3. **🔗 Detección de Relaciones:** Se identifican automáticamente las jerarquías
4. **🆔 Generación de IDs:** Se crean IDs únicos para campañas, grupos, anuncios y palabras clave
5. **Mapeo:** Se aplican las correspondencias encontradas
6. **🔗 Asignación de Relaciones:** Se asignan los IDs relacionales a cada registro
7. **Limpieza:** Los datos se validan y limpian
8. **SQL:** Se generan sentencias INSERT con relaciones completas
9. **Guardado:** El resultado se guarda en un archivo .sql

## 📝 Ejemplo de uso con relaciones

```python
from google_ads_sql_generator import GoogleAdsExcelAnalyzer

# Para anuncios con relaciones automáticas
analyzer = GoogleAdsExcelAnalyzer()
analyzer.set_table_type('anuncios')  # o 'palabras_clave' o 'campañas'

result = analyzer.process_excel_to_sql(
    excel_file="mi_reporte_google_ads.xlsx",
    output_file="inserts_supabase.sql",
    table_type='anuncios'
)

if result['success']:
    print(f"✅ {result['total_records']} registros con relaciones generados")
```

### 🔍 **Ejemplo de SQL generado con relaciones:**

```sql
-- Anuncio con relaciones jerárquicas
INSERT INTO public.google_ads_reporte_anuncios (
    titulo_1, titulo_2, campaña, grupo_anuncios, 
    clics, impresiones, costo, conversiones,
    id_campaña, id_grupo_anuncios, id_anuncio
) VALUES (
    'Compra Jade Natural', 'Envío Gratis', 'SaldeJade - Search', 'Jade Keywords',
    '250', '5000', '125.5', '8',
    1, 1, 1  -- ← IDs relacionales generados automáticamente
);

-- Palabra clave con relaciones jerárquicas
INSERT INTO public.google_ads_palabras_clave (
    palabra_clave, tipo_concordancia, campaña, grupo_anuncios,
    clics, impresiones, costo, conversiones,
    id_campaña, id_grupo_anuncios, id_palabra_clave
) VALUES (
    'jade natural', 'Broad match', 'SaldeJade - Search', 'Jade Keywords',
    '125', '2500', '62.5', '4',
    1, 1, 1  -- ← IDs relacionales generados automáticamente
);
```

## 🛠️ Personalización

### Mapeos manuales
Puedes modificar los mapeos en `simple_excel_to_sql.py` en la función `create_manual_mapping()`.

### Columnas de destino
Las columnas de la tabla están definidas en `self.target_columns` en ambos scripts.

## ⚠️ Consideraciones

- **Backup:** Siempre haz backup antes de ejecutar los SQL generados
- **Validación:** Revisa los datos antes de la inserción masiva
- **🔗 Relaciones:** Los IDs relacionales se generan automáticamente - no los modifiques manualmente
- **🆔 Integridad:** Asegúrate de insertar primero las campañas, luego grupos de anuncios, luego anuncios/palabras clave
- **Codificación:** Los archivos usan UTF-8 para caracteres especiales
- **Límites:** OpenAI tiene límites de tokens, archivos muy grandes pueden requerir división
- **🔄 Jerarquía:** Los nombres de campañas y grupos de anuncios deben ser consistentes entre archivos para mantener relaciones

## 🔧 Troubleshooting

### Error de API Key
```
❌ Error: No se encontró OPENAI_API_KEY
```
**Solución:** Configura tu API key en el archivo `.env`

### Error de lectura Excel
```
❌ Error al leer el archivo Excel
```
**Solución:** Verifica que el archivo existe y es un Excel válido (.xlsx, .xls)

### Mapeo incompleto
Si el mapeo automático no es perfecto, puedes:
1. Usar el script simple con mapeos predefinidos
2. Editar manualmente el mapeo en el código
3. Ajustar el prompt de OpenAI

## 📞 Soporte

Para problemas o mejoras, revisa:
1. Los logs detallados en consola
2. El archivo de salida SQL generado
3. La documentación de la API de OpenAI
