#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear la tabla facebook_paginas en Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

def crear_tabla_facebook_paginas():
    """Crea la tabla facebook_paginas ejecutando SQL directamente"""
    
    load_dotenv()
    
    print("🔧 Creando tabla facebook_paginas en Supabase...")
    
    # SQL para crear la tabla
    sql_crear_tabla = """
    -- Crear tabla para páginas de Facebook
    CREATE TABLE IF NOT EXISTS facebook_paginas (
        id SERIAL PRIMARY KEY,
        page_id VARCHAR(50) UNIQUE NOT NULL,
        nombre_pagina VARCHAR(255) NOT NULL,
        username VARCHAR(100),
        categoria VARCHAR(100),
        descripcion TEXT,
        seguidores INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        website VARCHAR(500),
        telefono VARCHAR(50),
        email VARCHAR(100),
        direccion TEXT,
        ciudad VARCHAR(100),
        pais VARCHAR(100),
        foto_perfil_url TEXT,
        foto_portada_url TEXT,
        verificada BOOLEAN DEFAULT FALSE,
        activa BOOLEAN DEFAULT TRUE,
        
        -- Estado para webhook (similar a cuentas publicitarias)
        estado_webhook VARCHAR(20) DEFAULT 'activa' CHECK (estado_webhook IN ('activa', 'pausada', 'excluida')),
        
        -- Campos de control
        creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        -- Metadatos adicionales
        access_token_valido BOOLEAN DEFAULT TRUE,
        ultima_sincronizacion TIMESTAMP WITH TIME ZONE,
        permisos_disponibles TEXT[], -- Array de permisos que tiene la app
        
        -- Información del cliente (opcional)
        nombre_cliente VARCHAR(255),
        empresa VARCHAR(255),
        
        CONSTRAINT unique_page_id UNIQUE (page_id)
    );
    """
    
    try:
        # Ejecutar SQL usando supabase
        resultado = supabase.rpc('exec_sql', {'sql': sql_crear_tabla}).execute()
        
        if resultado.data:
            print("✅ Tabla facebook_paginas creada exitosamente")
            return True
        else:
            print("❌ Error creando tabla")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        print("\n💡 Opciones alternativas:")
        print("1. Ejecuta manualmente el SQL en Supabase Dashboard")
        print("2. O usa el archivo sql/crear_tabla_facebook_paginas.sql")
        return False

def verificar_tabla_existe():
    """Verifica si la tabla facebook_paginas ya existe"""
    try:
        resultado = supabase.table('facebook_paginas').select('count').execute()
        print("✅ La tabla facebook_paginas ya existe")
        return True
    except Exception as e:
        print("❌ La tabla facebook_paginas no existe aún")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando y creando tabla facebook_paginas...")
    
    if verificar_tabla_existe():
        print("🎉 ¡La tabla ya existe! Puedes ejecutar el gestor directamente.")
        return
    
    print("\n🔧 Creando tabla...")
    if crear_tabla_facebook_paginas():
        print("\n🎉 ¡Tabla creada! Ahora puedes ejecutar:")
        print("   python gestor_paginas_facebook.py")
    else:
        print("\n❌ No se pudo crear la tabla automáticamente")
        print("🔧 SOLUCIÓN MANUAL:")
        print("1. Ve a Supabase Dashboard → SQL Editor")
        print("2. Ejecuta el contenido de: sql/crear_tabla_facebook_paginas.sql")
        print("3. Luego ejecuta: python gestor_paginas_facebook.py")

if __name__ == "__main__":
    main()
