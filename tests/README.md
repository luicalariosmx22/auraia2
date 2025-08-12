# 🧪 Carpeta de Tests

Esta carpeta contiene todos los scripts de testing y debugging para el proyecto AuraAi2.

## 📋 Instrucciones de uso

### ✅ **Reglas para Testing Eficiente**

1. **SIEMPRE revisar tests existentes** antes de crear uno nuevo
   - Buscar archivos similares: `test_webhook_*`, `test_meta_*`, etc.
   - Reutilizar lógica existente cuando sea posible

2. **Testing sin cargar toda la app**:
   ```python
   # ❌ No cargar toda la app para tests simples
   from app import create_app  # Carga 90+ blueprints
   
   # ✅ Importar solo lo necesario
   from clientes.aura.utils.supabase_client import supabase
   from clientes.aura.utils.meta_webhook_helpers import verificar_webhook
   ```

3. **Funciones puras para testing**:
   ```python
   def calcular_estado_webhook(estado_db: str, tiene_actividad: bool) -> str:
       """Función pura sin dependencias de Flask"""
       return 'activa' if estado_db == 'activa' or tiene_actividad else 'inactiva'
   
   # Test directo sin Flask
   assert calcular_estado_webhook('activa', False) == 'activa'
   ```

4. **Usar mocks para dependencias**:
   ```python
   from unittest.mock import patch, MagicMock
   
   @patch('clientes.aura.utils.supabase_client.supabase')
   def test_funcion(mock_supabase):
       mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
       # Test rápido sin BD real
   ```

### 🗂️ **Categorías de tests**

- `test_webhook_*` - Testing de webhooks de Meta/Facebook
- `test_meta_*` - Testing de integración Meta Ads
- `test_sistema_*` - Testing de sistema completo
- `test_audiencias_*` - Testing de audiencias Meta
- `verificar_*` - Scripts de verificación específicos
- `diagnosticar_*` - Scripts de diagnóstico
- `probar_*` - Scripts de prueba funcional

### 🚀 **Mejores prácticas**

1. **Nombres descriptivos**: `test_webhook_suscripcion_facebook.py`
2. **Tests pequeños**: Una función específica por archivo
3. **Sin dependencias**: Solo importar lo necesario
4. **Documentación**: Docstring explicando qué se está probando
5. **Limpieza**: Borrar después de usar si es temporal

### 🔍 **Antes de crear un test nuevo**

1. Revisar archivos existentes con `ls test_*tema*`
2. Ver si ya existe lógica similar
3. Determinar si necesitas Flask o solo la función
4. Usar mocks para evitar carga de dependencias

---

**Nota**: Mantener esta carpeta organizada. Los tests temporales deben borrarse después de usar.
