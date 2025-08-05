# 🔧 COLUMNAS FALTANTES EN SUPABASE - GUÍA DE SOLUCIÓN

## 📊 **PROBLEMA IDENTIFICADO**

Después de los cambios realizados, **faltan 68 columnas** en las tablas de Supabase:

- **✅ google_ads_campañas**: Completa (0 columnas faltantes)
- **❌ google_ads_reporte_anuncios**: 65 columnas faltantes
- **❌ google_ads_palabras_clave**: 3 columnas faltantes

## 🚀 **SOLUCIÓN AUTOMÁTICA**

Se ha generado el archivo `fix_missing_columns.sql` que contiene todos los comandos SQL necesarios.

### **PASOS PARA SOLUCIONARLO:**

1. **📂 Abre Supabase Dashboard**
   - Ve a [https://supabase.com/dashboard](https://supabase.com/dashboard)
   - Entra a tu proyecto

2. **🔧 Ve al SQL Editor**
   - En el menú lateral, haz clic en "SQL Editor"
   - Haz clic en "New query"

3. **📋 Copia el contenido del archivo**
   - Abre el archivo `fix_missing_columns.sql`
   - Copia todo su contenido
   - Pégalo en el SQL Editor

4. **▶️ Ejecuta el script**
   - Haz clic en "Run" o presiona Ctrl+Enter
   - Espera a que termine (debería tomar unos segundos)

5. **✅ Verifica que funcionó**
   - Ejecuta la consulta de verificación al final del script
   - Deberías ver todas las columnas listadas

## 🧪 **PROBAR LA INSERCIÓN**

Una vez agregadas las columnas, puedes probar la inserción:

```bash
cd "c:\Users\PC\PYTHON\AuraAi2\googleexcel"
python test_demo_insertion.py
```

## 📝 **¿QUÉ COLUMNAS SE ESTÁN AGREGANDO?**

### **Para google_ads_reporte_anuncios (65 columnas):**
- Títulos de anuncio (titulo_1 a titulo_15)
- Posiciones de título (pos_titulo_1 a pos_titulo_15)
- Descripciones (descripcion_1 a descripcion_4)
- URLs y rutas
- Métricas (clics, impresiones, CTR, etc.)
- **IDs relacionales**: id_campaña, id_grupo_anuncios, id_anuncio

### **Para google_ads_palabras_clave (3 columnas):**
- **id_campaña**: Para relacionar con campañas
- **id_grupo_anuncios**: Para relacionar con grupos de anuncios
- **id_palabra_clave**: ID único de cada palabra clave

## 🔗 **RELACIONES JERÁRQUICAS**

Estas columnas permiten mantener la estructura jerárquica:

```
📈 Campaña (id_campaña)
  └── 📂 Grupo de Anuncios (id_grupo_anuncios)
      ├── 📺 Anuncio (id_anuncio)
      └── 🔑 Palabra Clave (id_palabra_clave)
```

## ❓ **SI ALGO FALLA**

1. **Error de permisos**: Verifica que tu usuario tiene permisos de administrador en Supabase
2. **Error de sintaxis**: Copia exactamente el contenido del archivo SQL
3. **Tablas no existen**: Verifica que las tablas `google_ads_campañas`, `google_ads_reporte_anuncios`, y `google_ads_palabras_clave` existen

## 🎯 **DESPUÉS DE AGREGAR LAS COLUMNAS**

1. Las inserciones deberían funcionar correctamente
2. Los datos mantendrán las relaciones jerárquicas
3. Podrás hacer consultas relacionales entre campañas, anuncios y palabras clave
4. El sistema web funcionará completamente

---

**💡 TIP**: Una vez que esto funcione, todas las futuras inserciones mantendrán automáticamente las relaciones jerárquicas gracias a la IA y los generadores.
