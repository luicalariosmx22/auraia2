#!/usr/bin/env python3
"""
Script simplificado para crear las tablas de automatización usando SQL directo
"""
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

def crear_conexion_postgresql():
    """
    Crea conexión directa a PostgreSQL usando las credenciales de Supabase
    """
    try:
        # Variables de entorno de Supabase
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
        
        if not supabase_url or not supabase_key:
            print("❌ Variables de entorno SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no encontradas")
            return None
        
        # Extraer parámetros de conexión de la URL de Supabase
        # Formato típico: https://abc.supabase.co
        host = supabase_url.replace('https://', '').replace('http://', '')
        
        # Parámetros de conexión
        conn_params = {
            'host': host,
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': supabase_key  # En Supabase, a veces el service key funciona como password
        }
        
        print(f"🔌 Conectando a PostgreSQL en {host}...")
        conn = psycopg2.connect(**conn_params)
        print("✅ Conexión establecida exitosamente")
        return conn
        
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        print("💡 Tip: Asegúrate de tener las variables SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY configuradas")
        return None

def ejecutar_sql_manual():
    """
    Ejecuta las declaraciones SQL manualmente una por una
    """
    print("🛠️ Ejecutando creación de tablas manualmente...")
    
    # SQL statements separados
    sql_statements = [
        # 1. Tabla de automatizaciones
        """
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
            fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nombre_nora) REFERENCES nora_whatsapp_tokens(nombre) ON DELETE CASCADE
        );
        """,
        
        # 2. Tabla de publicaciones webhook
        """
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
        
        # 3. Tabla de anuncios automatizados
        """
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
            datos_meta_response JSONB,
            FOREIGN KEY (automatizacion_id) REFERENCES meta_ads_automatizaciones(id) ON DELETE CASCADE,
            FOREIGN KEY (publicacion_webhook_id) REFERENCES meta_publicaciones_webhook(id) ON DELETE CASCADE
        );
        """,
        
        # 4. Tabla de páginas webhook
        """
        CREATE TABLE IF NOT EXISTS meta_paginas_webhook (
            id BIGSERIAL PRIMARY KEY,
            nombre_nora VARCHAR(100) NOT NULL,
            pagina_id VARCHAR(50) NOT NULL,
            nombre_pagina VARCHAR(200),
            access_token TEXT NOT NULL,
            webhook_activo BOOLEAN DEFAULT true,
            fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nombre_nora) REFERENCES nora_whatsapp_tokens(nombre) ON DELETE CASCADE,
            UNIQUE(nombre_nora, pagina_id)
        );
        """,
        
        # 5. Tabla de plantillas de anuncios
        """
        CREATE TABLE IF NOT EXISTS meta_plantillas_anuncios (
            id BIGSERIAL PRIMARY KEY,
            nombre_nora VARCHAR(100) NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            descripcion TEXT,
            plantilla_json JSONB NOT NULL,
            activa BOOLEAN DEFAULT true,
            fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nombre_nora) REFERENCES nora_whatsapp_tokens(nombre) ON DELETE CASCADE
        );
        """,
        
        # 6. Índices para optimización
        """
        CREATE INDEX IF NOT EXISTS idx_automatizaciones_pagina_activa 
        ON meta_ads_automatizaciones(pagina_id, activa);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_publicaciones_pagina_procesado 
        ON meta_publicaciones_webhook(pagina_id, procesado);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_publicaciones_webhook_id 
        ON meta_publicaciones_webhook(webhook_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_anuncios_automatizacion 
        ON meta_anuncios_automatizados(automatizacion_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_paginas_webhook_nora_activo 
        ON meta_paginas_webhook(nombre_nora, webhook_activo);
        """
    ]
    
    try:
        # Usar supabase client para ejecutar SQL
        from clientes.aura.utils.supabase_client import supabase
        
        for i, statement in enumerate(sql_statements, 1):
            try:
                print(f"   ⚡ Ejecutando declaración {i}/{len(sql_statements)}")
                
                # Ejecutar directamente con supabase
                resultado = supabase.rpc('exec_sql', {'sql': statement}).execute()
                
                print(f"   ✅ Declaración {i} ejecutada exitosamente")
                
            except Exception as e:
                print(f"   ❌ Error en declaración {i}: {e}")
                # Intentar continuar con las siguientes
                continue
        
        print("✅ Todas las declaraciones SQL procesadas")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        return False

def verificar_tablas_simples():
    """
    Verificación simple de tablas
    """
    print("🔍 Verificando tablas...")
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        tablas = [
            'meta_ads_automatizaciones',
            'meta_publicaciones_webhook',
            'meta_anuncios_automatizados',
            'meta_paginas_webhook', 
            'meta_plantillas_anuncios'
        ]
        
        for tabla in tablas:
            try:
                resultado = supabase.table(tabla).select('*').limit(1).execute()
                print(f"   ✅ Tabla '{tabla}' existe")
            except Exception as e:
                print(f"   ❌ Tabla '{tabla}' no existe o error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 CONFIGURACIÓN SIMPLIFICADA DE AUTOMATIZACIÓN")
    print("=" * 60)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Ejecutar creación de tablas
    if ejecutar_sql_manual():
        print("\n✅ Proceso de creación completado")
        
        # Verificar tablas
        verificar_tablas_simples()
        
        print("\n🎉 ¡Configuración completada!")
        print("\n📋 Próximos pasos:")
        print("   1. Acceder al panel de automatización en /automatizacion")
        print("   2. Configurar primera automatización")
        print("   3. Probar con webhook de prueba")
        
    else:
        print("\n❌ Error en el proceso de configuración")
    
    print("\n" + "=" * 60)
