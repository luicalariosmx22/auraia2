# 🚀 Google Ads Excel to SQL Generator - Frontend Web

¡Tu frontend web está **funcionando en localhost:5001**! 🎉

## ✨ Lo que has conseguido:

### 🌐 **Interfaz Web Moderna**
- **Drag & Drop**: Arrastra archivos Excel directamente
- **Proceso Visual**: Barra de progreso animada
- **Vista Previa**: Ve el SQL antes de descargar
- **Testing Integrado**: Prueba con datos de ejemplo
- **Responsive**: Funciona en móvil y desktop

### 🤖 **Dos Generadores Disponibles**
1. **IA Inteligente**: Usa OpenAI para mapeo automático
2. **Simple Rápido**: Mapeos predefinidos comunes

### 📊 **Funcionalidades Completas**
- ✅ Análisis de 65 columnas de Google Ads
- ✅ Generación de SQL para Supabase
- ✅ Validación y limpieza de datos
- ✅ Manejo de errores robusto
- ✅ Descarga directa de archivos
- ✅ Interfaz multiidioma (español)

## 🔗 **Enlaces Rápidos**

- **🌐 Aplicación Web**: http://localhost:5001
- **📝 Generador Principal**: `python google_ads_sql_generator.py`
- **⚡ Generador Simple**: `python simple_excel_to_sql.py`
- **🖥️ Menú CLI**: `python main.py`

## 🛠️ **Comandos de Inicio**

```bash
# Interfaz Web (Recomendado)
run_web.bat

# O manualmente
python app.py

# CLI tradicional
run.bat
```

## 📁 **Estructura de Archivos**

```
📦 googleexcel/
├── 🌐 Frontend Web
│   ├── app.py                 # Aplicación Flask
│   ├── templates/            # Plantillas HTML
│   │   ├── index.html        # Página principal
│   │   ├── preview.html      # Vista previa SQL
│   │   └── test.html         # Página de testing
│   ├── static/              # CSS personalizado
│   └── run_web.bat          # Ejecutor web
├── 🤖 Generadores
│   ├── google_ads_sql_generator.py  # Con IA
│   ├── simple_excel_to_sql.py      # Simple
│   └── main.py                     # Menú CLI
├── 🔧 Configuración
│   ├── requirements.txt
│   ├── .env                 # APIs configuradas
│   └── run.bat             # Ejecutor CLI
└── 📚 Otros
    ├── test_generators.py   # Tests
    └── README.md           # Documentación
```

## 🎯 **Casos de Uso**

### Para Usuarios No Técnicos:
1. Abre `http://localhost:5001`
2. Arrastra tu Excel de Google Ads
3. Selecciona "IA" o "Simple"
4. Descarga el SQL generado
5. Ejecuta en Supabase

### Para Desarrolladores:
1. Usa la API `/upload` para integrar
2. Personaliza mapeos en `simple_excel_to_sql.py`
3. Modifica prompts de IA en `google_ads_sql_generator.py`
4. Extiende templates para más funcionalidades

## 🔑 **Tu Configuración Actual**

- ✅ **OpenAI API**: Configurada y funcionando
- ✅ **Supabase**: URLs configuradas
- ✅ **Dependencies**: Todas instaladas
- ✅ **Servidor Web**: Corriendo en puerto 5001
- ✅ **Entorno Virtual**: Activo y funcionando

## 🎉 **¡Listo para usar!**

Tu sistema está **completamente funcional**. Puedes:

1. **Subir archivos Excel** de Google Ads
2. **Generar SQL automáticamente** 
3. **Ejecutar en Supabase** directamente
4. **Escalar** para procesamiento masivo

¡Disfruta tu nuevo generador de SQL con interfaz web moderna! 🚀
