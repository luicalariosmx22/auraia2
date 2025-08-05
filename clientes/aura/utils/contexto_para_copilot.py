# clientes/aura/utils/contexto_para_copilot.py

"""
CONTEXTO AUTOMÁTICO PARA GITHUB COPILOT Y GPT
==============================================

Incluye este archivo como attachment en conversaciones para que 
GitHub Copilot y GPT siempre tengan contexto de los esquemas de Supabase.

INSTRUCCIÓN: Adjunta este archivo cuando preguntes sobre base de datos.
"""

# Esquemas actuales de Supabase (auto-actualizado)
from .supabase_schemas import SUPABASE_SCHEMAS

# Estado actual de la base de datos
ESTADO_BD = {
    "total_tablas": len(SUPABASE_SCHEMAS),
    "ultima_actualizacion": "2025-08-05",
    "tablas_principales": {
        "meta_ads_anuncios_detalle": 96,  # campos
        "meta_ads_reportes_semanales": 35,
        "clientes": 25,
        "google_ads_cuentas": 19,
        "configuracion_bot": 18,
        "contactos": 17,
        "google_ads_config": 16,
        "tareas": 16,
        "meta_ads_cuentas": 15,
        "pagos": 14,
        "servicios": 7,
        "modulos_disponibles": 6
    },
    "tablas_vacias": [
        "cursos", "estudiantes", "meta_ads_reportes", 
        "meta_webhook_eventos", "presupuestos", "whatsapp_mensajes"
    ]
}

# Esquemas más usados para referencia rápida
ESQUEMAS_FRECUENTES = {
    # Meta Ads - Marketing
    "meta_ads_cuentas": [
        "id", "ad_account_id", "nombre_visible", "nombre_cliente", 
        "conectada", "ads_activos", "estado_actual", "empresa_id"
    ],
    
    "meta_ads_anuncios_detalle": [
        "id", "ad_id", "campana_id", "nombre_anuncio", "nombre_campana",
        "importe_gastado", "impresiones", "clicks", "alcance", "ctr", "cpc"
    ],
    
    # Contactos - CRM
    "contactos": [
        "id", "nombre", "telefono", "correo", "empresa", "ciudad",
        "creado_en", "actualizado_en", "nombre_nora", "etiquetas_string"
    ],
    
    # Clientes - Gestión
    "clientes": [
        "id", "nombre_cliente", "telefono", "email", "ciudad", "estado",
        "creado_en", "actualizado_en", "activo", "tipo", "etapa"
    ],
    
    # Configuración - Core
    "configuracion_bot": [
        "id", "nombre_nora", "nombre_visible", "numero_nora", 
        "bienvenida", "instrucciones", "modulos", "ia_activa"
    ],
    
    # Google Ads - Marketing
    "google_ads_cuentas": [
        "id", "customer_id", "nombre_cliente", "nombre_visible",
        "conectada", "activa", "anuncios_activos", "empresa_id"
    ],
    
    # Tareas - Productividad
    "tareas": [
        "id", "titulo", "descripcion", "estatus", "prioridad",
        "fecha_limite", "empresa_id", "creado_por", "asignada_a_empresa"
    ],
    
    # Pagos - Facturación
    "pagos": [
        "id", "cliente_id", "monto", "concepto", "estatus",
        "fecha_pago", "fecha_vencimiento", "forma_pago_id"
    ]
}

# Tipos de datos más comunes
TIPOS_COMUNES = {
    "id": "integer (primary key)",
    "nombre": "text",
    "telefono": "text", 
    "correo": "text",
    "creado_en": "timestamp",
    "actualizado_en": "timestamp",
    "activo": "boolean",
    "empresa_id": "integer (foreign key)",
    "monto": "numeric/decimal",
    "fecha": "date",
    "estatus": "text/enum"
}

# Patrones de nombres de columnas
PATRONES_COLUMNAS = {
    "identificadores": ["id", "customer_id", "ad_account_id", "empresa_id"],
    "nombres": ["nombre", "nombre_cliente", "nombre_visible", "nombre_nora"],
    "contacto": ["telefono", "correo", "email", "direccion"],
    "fechas": ["creado_en", "actualizado_en", "fecha_pago", "fecha_limite"],
    "estados": ["activo", "conectada", "estatus", "estado_actual"],
    "meta_ads": ["importe_gastado", "impresiones", "clicks", "alcance", "ctr"],
    "monetarios": ["monto", "costo", "importe_gastado"]
}

# Validaciones comunes que debes hacer
VALIDACIONES_RECOMENDADAS = """
SIEMPRE hacer estas validaciones antes de usar esquemas:

1. Verificar tabla existe:
   if 'tabla_name' in SUPABASE_SCHEMAS:

2. Verificar columna existe:
   if 'columna' in SUPABASE_SCHEMAS['tabla']:

3. Usar funciones helper:
   from clientes.aura.utils.quick_schemas import existe, columnas
   if existe('tabla', 'columna'):

4. Construcción segura de queries:
   columnas_validas = columnas('tabla')
   datos_filtrados = {k:v for k,v in datos.items() if k in columnas_validas}
"""

# Para GitHub Copilot: contexto inmediato
print(f"📋 Contexto BD cargado: {ESTADO_BD['total_tablas']} tablas disponibles")
print(f"📊 Principales: {list(ESTADO_BD['tablas_principales'].keys())}")
print(f"📦 Vacías: {ESTADO_BD['tablas_vacias']}")
