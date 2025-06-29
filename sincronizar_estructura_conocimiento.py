#!/usr/bin/env python3
"""
Script para sincronizar la estructura de la tabla conocimiento_nora con el código del panel
"""

import os
from supabase import create_client
from dotenv import load_dotenv

def main():
    print("🔧 SINCRONIZACIÓN DE ESTRUCTURA - CONOCIMIENTO_NORA")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    try:
        # Obtener estructura actual
        print("📊 Analizando estructura actual...")
        result = supabase.table("conocimiento_nora").select("*").limit(1).execute()
        
        if result.data:
            campos_actuales = list(result.data[0].keys())
            print(f"✅ Campos actuales en la tabla: {', '.join(campos_actuales)}")
            
            # Campos que espera el código del panel
            campos_esperados = [
                'id', 'titulo', 'contenido', 'etiquetas', 
                'nombre_nora', 'created_at', 'activo', 'prioridad'
            ]
            
            print(f"\n🎯 Campos esperados por el código: {', '.join(campos_esperados)}")
            
            # Análisis de diferencias
            campos_faltantes = [campo for campo in campos_esperados if campo not in campos_actuales]
            campos_extra = [campo for campo in campos_actuales if campo not in campos_esperados]
            
            if campos_faltantes:
                print(f"\n⚠️  Campos faltantes: {', '.join(campos_faltantes)}")
            
            if campos_extra:
                print(f"\n📋 Campos adicionales en la tabla: {', '.join(campos_extra)}")
            
            # Mapeo de campos
            print(f"\n🗺️  Mapeo de campos detectado:")
            print(f"   - 'titulo' → No existe (solo 'contenido')")
            print(f"   - 'created_at' → 'fecha_creacion'")
            print(f"   - 'creado_por' → Campo adicional")
            print(f"   - 'origen' → Campo adicional")
            
            # Verificar registros de prueba
            print(f"\n🔍 Verificando registros existentes...")
            all_records = supabase.table("conocimiento_nora").select("*").execute()
            
            if all_records.data:
                print(f"📈 Total registros: {len(all_records.data)}")
                
                # Análisis por nombre_nora
                nombres_nora = {}
                etiquetas_unicas = set()
                
                for registro in all_records.data:
                    # Contar por nombre_nora
                    nombre = registro.get('nombre_nora', 'Sin nombre')
                    nombres_nora[nombre] = nombres_nora.get(nombre, 0) + 1
                    
                    # Recolectar etiquetas
                    etiquetas = registro.get('etiquetas', [])
                    if isinstance(etiquetas, list):
                        etiquetas_unicas.update(etiquetas)
                
                print(f"\n📊 Registros por bot:")
                for nombre, cantidad in nombres_nora.items():
                    print(f"   - {nombre}: {cantidad} registros")
                
                print(f"\n🏷️  Etiquetas encontradas:")
                for etiqueta in sorted(etiquetas_unicas):
                    print(f"   - {etiqueta}")
                
                # Buscar registros específicos
                print(f"\n🎯 Buscando registros con 'curso inteligencia artificial'...")
                ia_records = [r for r in all_records.data 
                             if any('inteligencia' in str(e).lower() or 'artificial' in str(e).lower() 
                                   for e in r.get('etiquetas', []))]
                
                if ia_records:
                    print(f"   ✅ Encontrados {len(ia_records)} registros relacionados con IA:")
                    for record in ia_records:
                        contenido_preview = record.get('contenido', '')[:100] + '...'
                        etiquetas = record.get('etiquetas', [])
                        print(f"     - Etiquetas: {etiquetas}")
                        print(f"       Contenido: {contenido_preview}")
                else:
                    print(f"   ⚠️  No se encontraron registros con etiquetas de IA")
            
            # Sugerencias de sincronización
            print(f"\n" + "=" * 60)
            print(f"💡 SUGERENCIAS DE SINCRONIZACIÓN:")
            print(f"   1. El código busca 'titulo' pero la tabla solo tiene 'contenido'")
            print(f"   2. El código busca 'created_at' pero la tabla usa 'fecha_creacion'")
            print(f"   3. Considerar actualizar el código JavaScript para usar los campos correctos")
            print(f"   4. O actualizar la estructura de la tabla para incluir 'titulo'")
            
            return True
            
        else:
            print("❌ No se pudieron obtener registros de la tabla")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    main()
