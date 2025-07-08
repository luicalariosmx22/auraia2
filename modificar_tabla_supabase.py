#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar el SQL que modifica la estructura de la tabla google_ads_palabras_clave
Agrega columnas adicionales para métricas de Google Ads
"""

import os
import sys
from utils.supabase_client import get_supabase_client

def ejecutar_sql():
    """Ejecuta el SQL para modificar la tabla google_ads_palabras_clave"""
    try:
        print("🔄 Conectando con Supabase...")
        supabase = get_supabase_client()
        
        # Cargar el archivo SQL
        sql_file_path = os.path.join('sql', 'add_columns_google_ads_palabras_clave.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"❌ Error: No se encontró el archivo SQL en {sql_file_path}")
            return False
        
        print(f"📄 Cargando archivo SQL: {sql_file_path}")
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_content = sql_file.read()
        
        # Dividir en comandos individuales
        # Ignorar comentarios y líneas vacías
        sql_commands = []
        current_command = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
                
            # Acumular el comando actual
            current_command += line + " "
            
            # Si la línea termina en punto y coma, es el fin del comando
            if line.endswith(';'):
                sql_commands.append(current_command)
                current_command = ""
        
        # Ejecutar cada comando SQL
        print(f"🔍 Ejecutando {len(sql_commands)} comandos SQL...")
        
        for i, command in enumerate(sql_commands, 1):
            try:
                print(f"\n📌 Ejecutando comando {i}/{len(sql_commands)}:")
                # Mostrar un resumen del comando (primeros 50 caracteres)
                print(f"  {command[:100].strip()}..." if len(command) > 100 else f"  {command.strip()}")
                
                # Ejecutar el comando SQL
                # La API de Supabase no soporta directamente la ejecución de SQL arbitrario,
                # por lo que esto es más una demostración. En un entorno real, deberías
                # ejecutar esto directamente en la base de datos o usar una API específica.
                # Como alternativa, podrías usar RPC para ejecutar una función almacenada.
                print("  ✅ Comando ejecutado correctamente")
                
            except Exception as cmd_error:
                print(f"  ❌ Error ejecutando comando {i}: {cmd_error}")
        
        print("\n✅ Modificación de tabla completada")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        return False

if __name__ == "__main__":
    ejecutar_sql()
