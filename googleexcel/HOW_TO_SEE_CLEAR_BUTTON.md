# 🔍 CÓMO VER EL BOTÓN "LIMPIAR TABLAS"

## 📍 UBICACIÓN DEL BOTÓN

El botón **"Limpiar Tablas"** está ubicado en la sección de **"Múltiples Archivos + Supabase"**.

### 🎯 PASOS PARA VERLO:

1. **Ir a la aplicación**: http://localhost:5001

2. **Cambiar de modo**: 
   - En la parte superior verás dos opciones:
     - 🔘 **Archivo Individual** (por defecto)
     - ⭕ **Múltiples Archivos + Supabase** ← **¡SELECCIONA ESTA!**

3. **Seleccionar modo múltiple**:
   - Haz clic en el botón **"Múltiples Archivos + Supabase"**
   - La interfaz cambiará para mostrar la sección de múltiples archivos

4. **Ver los botones**:
   En la fila de controles verás 4 botones:
   ```
   [Procesar Archivos] [Descargar SQL] [Insertar Supabase] [🗑️ Limpiar Tablas]
        (amarillo)         (azul)          (verde)         (ROJO)
   ```

## 🧪 PÁGINA DE PRUEBA

Si quieres probar solo el botón, ve a:
**http://localhost:5001/test-button**

Esta página muestra los 4 botones directamente sin necesidad de cambiar de modo.

## ✅ VERIFICACIÓN

### El botón debe verse así:
- **Color**: Rojo con borde (btn-outline-danger)
- **Icono**: 🗑️ (trash-alt)
- **Texto**: "Limpiar Tablas"
- **Posición**: Cuarta columna en la fila de controles

### Si NO lo ves:
1. ✅ Verifica que estés en modo "Múltiples Archivos + Supabase"
2. ✅ Refresca la página (Ctrl+F5 para limpiar caché)
3. ✅ Verifica que el servidor esté ejecutándose
4. ✅ Prueba la página de test: http://localhost:5001/test-button

## 🔄 FUNCIONAMIENTO

Una vez que veas el botón:

1. **Clic en "Limpiar Tablas"**
2. **Confirmación**: Aparecerá un diálogo de advertencia
3. **Confirmar**: Si das "Aceptar", limpiará las 3 tablas
4. **Resultado**: Te mostrará cuántos registros se eliminaron

---

**🎯 IMPORTANTE: El botón SOLO aparece en el modo "Múltiples Archivos + Supabase", no en el modo individual.**
