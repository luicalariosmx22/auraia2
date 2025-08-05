#!/usr/bin/env python3
"""
Script final para crear tablas de automatización usando solo Supabase client
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

def crear_tablas_automatizacion():
    """
    Crea las tablas ejecutando cada SQL individualmente
    """
    print("🛠️ Creando tablas de automatización...")
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Definir cada tabla por separado
        tablas_sql = {
            'meta_ads_automatizaciones': """
                CREATE TABLE IF NOT EXISTS meta_ads_automatizaciones (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_nora VARCHAR(100) NOT NULL,
                    nombre VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT true,
                    pagina_id VARCHAR(50) NOT NULL,
                    conjunto_anuncios_id VARCHAR(50) NOT NULL,
                    filtros_contenido JSONB DEFAULT '{}',
                    configuracion_anuncio JSONB DEFAULT '{}',
                    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'meta_publicaciones_webhook': """
                CREATE TABLE IF NOT EXISTS meta_publicaciones_webhook (
                    id BIGSERIAL PRIMARY KEY,
                    webhook_id VARCHAR(100) UNIQUE NOT NULL,
                    pagina_id VARCHAR(50) NOT NULL,
                    publicacion_id VARCHAR(50) NOT NULL,
                    tipo_contenido VARCHAR(20) NOT NULL,
                    contenido_texto TEXT,
                    url_imagen VARCHAR(500),
                    url_video VARCHAR(500),
                    fecha_publicacion TIMESTAMP WITH TIME ZONE,
                    fecha_recepcion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    procesado BOOLEAN DEFAULT false,
                    datos_webhook JSONB
                );
            """,
            
            'meta_anuncios_automatizados': """
                CREATE TABLE IF NOT EXISTS meta_anuncios_automatizados (
                    id BIGSERIAL PRIMARY KEY,
                    automatizacion_id BIGINT NOT NULL,
                    publicacion_webhook_id BIGINT NOT NULL,
                    anuncio_id VARCHAR(50),
                    creative_id VARCHAR(50),
                    estado VARCHAR(20) DEFAULT 'pending',
                    error_mensaje TEXT,
                    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    datos_meta_response JSONB
                );
            """,
            
            'meta_paginas_webhook': """
                CREATE TABLE IF NOT EXISTS meta_paginas_webhook (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_nora VARCHAR(100) NOT NULL,
                    pagina_id VARCHAR(50) NOT NULL,
                    nombre_pagina VARCHAR(200),
                    access_token TEXT NOT NULL,
                    webhook_activo BOOLEAN DEFAULT true,
                    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(nombre_nora, pagina_id)
                );
            """,
            
            'meta_plantillas_anuncios': """
                CREATE TABLE IF NOT EXISTS meta_plantillas_anuncios (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_nora VARCHAR(100) NOT NULL,
                    nombre VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    plantilla_json JSONB NOT NULL,
                    activa BOOLEAN DEFAULT true,
                    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        # Ejecutar cada tabla
        for nombre_tabla, sql_statement in tablas_sql.items():
            try:
                print(f"   📝 Creando tabla: {nombre_tabla}")
                
                # Intentar usando diferentes métodos de Supabase
                try:
                    # Método 1: RPC con función personalizada
                    resultado = supabase.rpc('execute_sql', {'query': sql_statement}).execute()
                    print(f"   ✅ Tabla {nombre_tabla} creada (método RPC)")
                except:
                    try:
                        # Método 2: Query directo
                        resultado = supabase.postgrest.schema().execute(sql_statement)
                        print(f"   ✅ Tabla {nombre_tabla} creada (método directo)")
                    except:
                        print(f"   ⚠️ No se pudo crear tabla {nombre_tabla} automáticamente")
                        print(f"   📋 SQL para ejecutar manualmente:")
                        print(f"   {sql_statement}")
                        
            except Exception as e:
                print(f"   ❌ Error creando tabla {nombre_tabla}: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def crear_indices():
    """
    Crea índices para optimización
    """
    print("📊 Creando índices...")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_automatizaciones_pagina_activa ON meta_ads_automatizaciones(pagina_id, activa);",
        "CREATE INDEX IF NOT EXISTS idx_publicaciones_pagina_procesado ON meta_publicaciones_webhook(pagina_id, procesado);",
        "CREATE INDEX IF NOT EXISTS idx_publicaciones_webhook_id ON meta_publicaciones_webhook(webhook_id);",
        "CREATE INDEX IF NOT EXISTS idx_anuncios_automatizacion ON meta_anuncios_automatizados(automatizacion_id);",
        "CREATE INDEX IF NOT EXISTS idx_paginas_webhook_nora_activo ON meta_paginas_webhook(nombre_nora, webhook_activo);"
    ]
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        for i, indice_sql in enumerate(indices, 1):
            try:
                print(f"   🔧 Creando índice {i}/{len(indices)}")
                # Intentar crear índice
                supabase.rpc('execute_sql', {'query': indice_sql}).execute()
                print(f"   ✅ Índice {i} creado")
            except Exception as e:
                print(f"   ⚠️ Índice {i} puede que ya exista o error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando índices: {e}")
        return False

def insertar_datos_iniciales():
    """
    Inserta datos iniciales de ejemplo
    """
    print("💾 Insertando datos de ejemplo...")
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Plantilla de anuncio por defecto
        plantilla_default = {
            'nombre_nora': 'nora_default',
            'nombre': 'Plantilla Automática por Defecto',
            'descripcion': 'Plantilla base para anuncios automáticos',
            'plantilla_json': {
                'headline': '¡Descubre lo nuevo!',
                'description': 'No te pierdas nuestras últimas novedades',
                'call_to_action': 'LEARN_MORE',
                'mensaje_personalizado': 'Conoce más sobre esto'
            },
            'activa': True
        }
        
        try:
            resultado = supabase.table('meta_plantillas_anuncios').insert(plantilla_default).execute()
            
            if resultado.data:
                print("   ✅ Plantilla por defecto insertada")
            else:
                print("   ⚠️ Plantilla no insertada - puede que ya exista")
                
        except Exception as e:
            print(f"   ⚠️ Error insertando plantilla: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        return False

def mostrar_sql_manual():
    """
    Muestra el SQL para ejecutar manualmente si es necesario
    """
    print("\n" + "="*60)
    print("📋 SQL PARA EJECUTAR MANUALMENTE EN SUPABASE (si es necesario)")
    print("="*60)
    
    sql_completo = """
-- 1. Tabla de automatizaciones
CREATE TABLE IF NOT EXISTS meta_ads_automatizaciones (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activa BOOLEAN DEFAULT true,
    pagina_id VARCHAR(50) NOT NULL,
    conjunto_anuncios_id VARCHAR(50) NOT NULL,
    filtros_contenido JSONB DEFAULT '{}',
    configuracion_anuncio JSONB DEFAULT '{}',
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de publicaciones webhook
CREATE TABLE IF NOT EXISTS meta_publicaciones_webhook (
    id BIGSERIAL PRIMARY KEY,
    webhook_id VARCHAR(100) UNIQUE NOT NULL,
    pagina_id VARCHAR(50) NOT NULL,
    publicacion_id VARCHAR(50) NOT NULL,
    tipo_contenido VARCHAR(20) NOT NULL,
    contenido_texto TEXT,
    url_imagen VARCHAR(500),
    url_video VARCHAR(500),
    fecha_publicacion TIMESTAMP WITH TIME ZONE,
    fecha_recepcion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    procesado BOOLEAN DEFAULT false,
    datos_webhook JSONB
);

-- 3. Tabla de anuncios automatizados
CREATE TABLE IF NOT EXISTS meta_anuncios_automatizados (
    id BIGSERIAL PRIMARY KEY,
    automatizacion_id BIGINT NOT NULL,
    publicacion_webhook_id BIGINT NOT NULL,
    anuncio_id VARCHAR(50),
    creative_id VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'pending',
    error_mensaje TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    datos_meta_response JSONB
);

-- 4. Tabla de páginas webhook
CREATE TABLE IF NOT EXISTS meta_paginas_webhook (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    pagina_id VARCHAR(50) NOT NULL,
    nombre_pagina VARCHAR(200),
    access_token TEXT NOT NULL,
    webhook_activo BOOLEAN DEFAULT true,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nombre_nora, pagina_id)
);

-- 5. Tabla de plantillas de anuncios
CREATE TABLE IF NOT EXISTS meta_plantillas_anuncios (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    plantilla_json JSONB NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Índices para optimización
CREATE INDEX IF NOT EXISTS idx_automatizaciones_pagina_activa ON meta_ads_automatizaciones(pagina_id, activa);
CREATE INDEX IF NOT EXISTS idx_publicaciones_pagina_procesado ON meta_publicaciones_webhook(pagina_id, procesado);
CREATE INDEX IF NOT EXISTS idx_publicaciones_webhook_id ON meta_publicaciones_webhook(webhook_id);
CREATE INDEX IF NOT EXISTS idx_anuncios_automatizacion ON meta_anuncios_automatizados(automatizacion_id);
CREATE INDEX IF NOT EXISTS idx_paginas_webhook_nora_activo ON meta_paginas_webhook(nombre_nora, webhook_activo);
"""
    
    print(sql_completo)
    print("="*60)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CONFIGURADOR DE AUTOMATIZACIÓN META ADS")
    print("=" * 60)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Paso 1: Crear tablas
        print("\n🏗️ PASO 1: Creando tablas...")
        crear_tablas_automatizacion()
        
        # Paso 2: Crear índices
        print("\n📊 PASO 2: Creando índices...")
        crear_indices()
        
        # Paso 3: Insertar datos iniciales
        print("\n💾 PASO 3: Insertando datos iniciales...")
        insertar_datos_iniciales()
        
        print("\n✅ ¡CONFIGURACIÓN COMPLETADA!")
        print("\n🎯 Próximos pasos:")
        print("   1. Ir a http://localhost:5000/automatizacion")
        print("   2. Configurar tu primera automatización")
        print("   3. Probar con una publicación de prueba")
        print("   4. Verificar que los anuncios se crean automáticamente")
        
        # Mostrar SQL manual como respaldo
        mostrar_sql_manual()
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        print("\n💡 Solución: Ejecuta el SQL manualmente en Supabase")
        mostrar_sql_manual()
    
    print("\n" + "=" * 60)
