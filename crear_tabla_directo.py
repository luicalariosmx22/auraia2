#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script minimalista para crear la tabla google_ads_config en Supabase
usando SQL directo
"""

import sys
import os
import time
import requests
import json

# Leer credenciales de Supabase desde el entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: No se encontraron las credenciales de Supabase en el entorno.")
    print("Asegúrate de que las variables SUPABASE_URL y SUPABASE_KEY estén definidas.")
    sys.exit(1)

# SQL para crear la tabla
SQL_CREATE_TABLE = """
-- Crear extensión UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla para configuración de Google Ads
CREATE TABLE IF NOT EXISTS google_ads_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID,
    cliente_id VARCHAR,
    developer_token VARCHAR,
    developer_token_valid BOOLEAN DEFAULT FALSE,
    client_id VARCHAR,
    client_secret VARCHAR,
    login_customer_id VARCHAR,
    refresh_token VARCHAR,
    refresh_token_valid BOOLEAN DEFAULT FALSE,
    access_token VARCHAR,
    token_type VARCHAR DEFAULT 'Bearer',
    expires_in INTEGER DEFAULT 3600,
    activo BOOLEAN DEFAULT TRUE
);

-- Crear o reemplazar la función para actualizar el timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear o reemplazar el trigger para actualizar 'updated_at' automáticamente
DROP TRIGGER IF EXISTS set_updated_at ON google_ads_config;
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON google_ads_config
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
"""

# Datos de ejemplo para insertar
EXAMPLE_DATA = {
    "client_id": "ejemplo-client-id.apps.googleusercontent.com",
    "client_secret": "GOCSPX-ejemplo-client-secret",
    "developer_token": "ejemplo-developer-token",
    "login_customer_id": "1234567890",
    "developer_token_valid": True
}

def ejecutar_sql(sql):
    """Ejecuta SQL en Supabase usando la API REST"""
    print(f"Ejecutando SQL en {SUPABASE_URL}...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec",
            headers=headers,
            json={"query": sql}
        )
        
        # Verificar respuesta
        if response.status_code in (200, 201):
            print("✅ SQL ejecutado correctamente.")
            return True
        else:
            print(f"❌ Error ejecutando SQL: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def insertar_datos_ejemplo():
    """Inserta datos de ejemplo en la tabla"""
    print("\nInsertando datos de ejemplo...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/google_ads_config",
            headers=headers,
            json=EXAMPLE_DATA
        )
        
        # Verificar respuesta
        if response.status_code in (200, 201):
            print("✅ Datos de ejemplo insertados correctamente.")
            return True
        else:
            print(f"❌ Error insertando datos: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_tabla():
    """Verifica si la tabla existe y muestra su contenido"""
    print("\nVerificando tabla google_ads_config...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/google_ads_config?select=id,client_id,developer_token_valid",
            headers=headers
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tabla verificada. Encontrados {len(data)} registros.")
            
            if data:
                print("\nPrimer registro:")
                print(json.dumps(data[0], indent=2))
            
            return True
        else:
            print(f"❌ Error verificando tabla: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("\nCREACIÓN DE TABLA GOOGLE ADS CONFIG\n")
    print("=" * 50)
    
    # Crear tabla
    if ejecutar_sql(SQL_CREATE_TABLE):
        print("\n✅ La tabla google_ads_config ha sido creada correctamente.")
        
        # Esperar un momento para que la tabla esté disponible
        print("Esperando 3 segundos para que la tabla esté disponible...")
        time.sleep(3)
        
        # Verificar si la tabla existe
        if verificar_tabla():
            # Preguntar si insertar datos de ejemplo
            insertar = input("\n¿Deseas insertar datos de ejemplo? (s/n): ")
            if insertar.lower() == 's':
                insertar_datos_ejemplo()
        
        print("\n✅ Proceso completado.")
    else:
        print("\n❌ No se pudo crear la tabla.")

if __name__ == "__main__":
    main()
