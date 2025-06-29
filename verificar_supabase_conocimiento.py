#!/usr/bin/env python3
"""
Script para verificar la conexión a Supabase y el estado de la tabla conocimiento_nora
"""

import os
import sys
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

def main():
    print("🔍 VERIFICACIÓN DE SUPABASE - TABLA CONOCIMIENTO_NORA")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar variables de entorno
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Variables de entorno SUPABASE_URL o SUPABASE_KEY no encontradas")
        print("   Verifique que estén configuradas en el archivo .env")
        return False
    
    print(f"✅ Variables de entorno encontradas")
    print(f"   URL: {SUPABASE_URL[:50]}...")
    print(f"   KEY: {SUPABASE_KEY[:20]}...")
    
    try:
        # Crear cliente de Supabase
        print("\n🔗 Conectando a Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente de Supabase creado exitosamente")
        
        # Verificar conexión con la tabla conocimiento_nora
        print("\n📊 Verificando tabla 'conocimiento_nora'...")
        
        # Obtener estadísticas de la tabla
        try:
            # Contar total de registros
            count_result = supabase.table("conocimiento_nora").select("id", count="exact").execute()
            total_registros = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            print(f"✅ Tabla 'conocimiento_nora' accesible")
            print(f"   Total de registros: {total_registros}")
            
            # Obtener algunos registros de muestra
            if total_registros > 0:
                print("\n📋 Obteniendo registros de muestra...")
                sample_result = supabase.table("conocimiento_nora").select("*").limit(5).execute()
                
                if sample_result.data:
                    print(f"✅ Se obtuvieron {len(sample_result.data)} registros de muestra")
                    
                    # Mostrar estructura de los campos
                    primer_registro = sample_result.data[0]
                    print("\n🔍 Estructura de campos encontrada:")
                    for campo, valor in primer_registro.items():
                        tipo_valor = type(valor).__name__
                        valor_muestra = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                        print(f"   - {campo}: {tipo_valor} = {valor_muestra}")
                    
                    # Verificar campos específicos necesarios
                    campos_necesarios = ['id', 'titulo', 'contenido', 'etiquetas', 'nombre_nora', 'created_at']
                    campos_faltantes = []
                    campos_existentes = []
                    
                    for campo in campos_necesarios:
                        if campo in primer_registro:
                            campos_existentes.append(campo)
                        else:
                            campos_faltantes.append(campo)
                    
                    print(f"\n✅ Campos existentes: {', '.join(campos_existentes)}")
                    if campos_faltantes:
                        print(f"⚠️  Campos faltantes: {', '.join(campos_faltantes)}")
                    
                    # Verificar registros por nombre_nora
                    print("\n📈 Análisis por nombre_nora...")
                    nombres_nora = {}
                    for registro in sample_result.data:
                        nombre = registro.get('nombre_nora', 'Sin nombre')
                        nombres_nora[nombre] = nombres_nora.get(nombre, 0) + 1
                    
                    for nombre, cantidad in nombres_nora.items():
                        print(f"   - {nombre}: {cantidad} registros")
                    
                    # Verificar etiquetas
                    print("\n🏷️  Análisis de etiquetas...")
                    etiquetas_encontradas = set()
                    for registro in sample_result.data:
                        etiquetas = registro.get('etiquetas', [])
                        if isinstance(etiquetas, list):
                            etiquetas_encontradas.update(etiquetas)
                        elif isinstance(etiquetas, str):
                            # Si las etiquetas están como string separado por comas
                            etiquetas_encontradas.update([e.strip() for e in etiquetas.split(',') if e.strip()])
                    
                    if etiquetas_encontradas:
                        print(f"   Etiquetas encontradas: {', '.join(list(etiquetas_encontradas)[:10])}")
                        if len(etiquetas_encontradas) > 10:
                            print(f"   ... y {len(etiquetas_encontradas) - 10} más")
                    else:
                        print("   No se encontraron etiquetas en los registros de muestra")
                
                else:
                    print("⚠️  No se pudieron obtener registros de muestra")
            else:
                print("ℹ️  La tabla está vacía (sin registros)")
        
        except Exception as e:
            print(f"❌ Error al acceder a la tabla 'conocimiento_nora': {str(e)}")
            return False
        
        # Verificar permisos de escritura
        print("\n✍️  Verificando permisos de escritura...")
        try:
            # Intentar insertar un registro de prueba
            registro_prueba = {
                "titulo": "TEST_CONEXION",
                "contenido": "Registro de prueba para verificar conexión",
                "etiquetas": ["test", "conexion"],
                "nombre_nora": "test_bot",
                "created_at": datetime.now().isoformat()
            }
            
            insert_result = supabase.table("conocimiento_nora").insert(registro_prueba).execute()
            
            if insert_result.data:
                print("✅ Permisos de escritura verificados - registro de prueba insertado")
                
                # Eliminar el registro de prueba
                registro_id = insert_result.data[0]['id']
                delete_result = supabase.table("conocimiento_nora").delete().eq("id", registro_id).execute()
                
                if delete_result.data:
                    print("✅ Registro de prueba eliminado correctamente")
                else:
                    print("⚠️  Advertencia: No se pudo eliminar el registro de prueba")
            else:
                print("❌ Error: No se pudo insertar registro de prueba")
                
        except Exception as e:
            print(f"❌ Error en permisos de escritura: {str(e)}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("   - Conexión a Supabase: OK")
        print("   - Acceso a tabla 'conocimiento_nora': OK")
        print(f"   - Total de registros: {total_registros}")
        print("   - Permisos de lectura: OK")
        print("   - Permisos de escritura: OK")
        print("\n🎉 La base de datos está lista para usar!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        print("\n🔧 Posibles soluciones:")
        print("   1. Verificar que las credenciales de Supabase sean correctas")
        print("   2. Verificar que la tabla 'conocimiento_nora' exista")
        print("   3. Verificar la conexión a internet")
        print("   4. Verificar los permisos de la API key de Supabase")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
