#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa del sistema de conocimiento
con los datos reales de Supabase, específicamente los registros de 'Curso Inteligencia Artificial'
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import json

def main():
    print("🧪 PRUEBA COMPLETA DEL SISTEMA DE CONOCIMIENTO")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    try:
        # 1. Simular la consulta del endpoint obtener_bloques_conocimiento
        print("1️⃣ Simulando consulta de bloques de conocimiento...")
        
        # Replicar la query exacta del endpoint
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        if res.data:
            print(f"✅ Consulta exitosa: {len(res.data)} bloques encontrados")
            
            # Mostrar estadísticas
            total_bloques = len(res.data)
            etiquetas_unicas = set()
            bloques_prioritarios = 0
            bloques_ia = []
            
            for bloque in res.data:
                etiquetas = bloque.get('etiquetas', [])
                if isinstance(etiquetas, list):
                    etiquetas_unicas.update(etiquetas)
                
                if bloque.get('prioridad', False):
                    bloques_prioritarios += 1
                
                # Buscar bloques de IA
                for etiqueta in etiquetas:
                    if 'inteligencia' in etiqueta.lower() or 'artificial' in etiqueta.lower():
                        bloques_ia.append(bloque)
                        break
            
            print(f"📊 Estadísticas:")
            print(f"   - Total bloques: {total_bloques}")
            print(f"   - Etiquetas únicas: {len(etiquetas_unicas)}")
            print(f"   - Bloques prioritarios: {bloques_prioritarios}")
            print(f"   - Bloques de IA: {len(bloques_ia)}")
            
            # 2. Analizar bloques de Inteligencia Artificial
            print(f"\n2️⃣ Analizando bloques de 'Curso Inteligencia Artificial'...")
            
            if bloques_ia:
                for i, bloque in enumerate(bloques_ia):
                    print(f"\n📋 Bloque {i+1}:")
                    print(f"   ID: {bloque['id']}")
                    print(f"   Etiquetas: {bloque['etiquetas']}")
                    print(f"   Prioridad: {bloque.get('prioridad', False)}")
                    print(f"   Fecha: {bloque.get('fecha_creacion', 'N/A')}")
                    
                    # Mostrar preview del contenido
                    contenido = bloque.get('contenido', '')
                    preview = contenido[:150] + "..." if len(contenido) > 150 else contenido
                    print(f"   Contenido: {preview}")
                    
                    # Verificar estructura requerida por el JS
                    campos_js = ['id', 'contenido', 'etiquetas', 'fecha_creacion', 'prioridad', 'activo']
                    campos_faltantes = [campo for campo in campos_js if campo not in bloque]
                    
                    if campos_faltantes:
                        print(f"   ⚠️ Campos faltantes para JS: {campos_faltantes}")
                    else:
                        print(f"   ✅ Estructura compatible con JS")
            else:
                print("   ❌ No se encontraron bloques de IA")
            
            # 3. Simular filtrado por etiqueta (como lo haría el JS)
            print(f"\n3️⃣ Simulando filtrado JavaScript...")
            
            # Función de filtrado similar al JS
            def filtrar_por_etiqueta(bloques, etiqueta_buscar):
                """Simula el filtrado del JS"""
                resultados = []
                for bloque in bloques:
                    etiquetas = bloque.get('etiquetas', [])
                    if isinstance(etiquetas, list):
                        for etiqueta in etiquetas:
                            if etiqueta_buscar.lower() in etiqueta.lower():
                                resultados.append(bloque)
                                break
                return resultados
            
            # Probar diferentes búsquedas
            busquedas = [
                "inteligencia artificial",
                "curso",
                "artificial",
                "inteligencia",
                "Curso Inteligencia Artificial"
            ]
            
            for busqueda in busquedas:
                resultados = filtrar_por_etiqueta(res.data, busqueda)
                print(f"   Búsqueda '{busqueda}': {len(resultados)} resultados")
                
                if resultados and busqueda == "inteligencia artificial":
                    print(f"     📝 Primer resultado:")
                    primer_resultado = resultados[0]
                    print(f"     - Etiquetas: {primer_resultado['etiquetas']}")
                    preview = primer_resultado.get('contenido', '')[:100] + "..."
                    print(f"     - Preview: {preview}")
            
            # 4. Generar datos de prueba para el JS (formato JSON)
            print(f"\n4️⃣ Generando datos de prueba para JavaScript...")
            
            # Crear formato compatible con el JS
            datos_js = []
            for bloque in res.data:
                bloque_formateado = {
                    "id": bloque['id'],
                    "contenido": bloque.get('contenido', ''),
                    "etiquetas": bloque.get('etiquetas', []),
                    "fecha_creacion": bloque.get('fecha_creacion', ''),
                    "prioridad": bloque.get('prioridad', False),
                    "activo": bloque.get('activo', True),
                    "nombre_nora": bloque.get('nombre_nora', ''),
                    "origen": bloque.get('origen', 'manual')
                }
                datos_js.append(bloque_formateado)
            
            # Guardar datos de prueba en archivo JSON
            with open('datos_prueba_conocimiento.json', 'w', encoding='utf-8') as f:
                json.dump(datos_js, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Datos guardados en 'datos_prueba_conocimiento.json'")
            print(f"   Total registros: {len(datos_js)}")
            
            # 5. Verificar compatibilidad con el sistema actual
            print(f"\n5️⃣ Verificación de compatibilidad...")
            
            # Verificar que todos los campos esperados existen
            campos_requeridos = ['id', 'contenido', 'etiquetas', 'fecha_creacion', 'activo']
            compatible = True
            
            for bloque in datos_js:
                for campo in campos_requeridos:
                    if campo not in bloque or bloque[campo] is None:
                        print(f"   ❌ Campo faltante '{campo}' en bloque {bloque.get('id', 'desconocido')}")
                        compatible = False
            
            if compatible:
                print(f"   ✅ Todos los bloques son compatibles con el sistema")
            else:
                print(f"   ⚠️ Algunos bloques tienen problemas de compatibilidad")
            
            print(f"\n" + "=" * 60)
            print(f"🎉 PRUEBA COMPLETADA")
            print(f"   - Conexión a Supabase: ✅")
            print(f"   - Datos de conocimiento: ✅ ({total_bloques} bloques)")
            print(f"   - Bloques de IA: ✅ ({len(bloques_ia)} bloques)")
            print(f"   - Compatibilidad JS: ✅" if compatible else "   - Compatibilidad JS: ⚠️")
            print(f"   - Archivo de prueba: ✅ datos_prueba_conocimiento.json")
            
            return True
            
        else:
            print("❌ No se obtuvieron datos de la consulta")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
