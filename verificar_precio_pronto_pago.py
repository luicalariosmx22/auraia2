#!/usr/bin/env python3
# ✅ Script para verificar que la columna precio_pronto_pago funciona correctamente
# 👉 Ejecutar para probar la funcionalidad

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def verificar_columna_precio_pronto_pago():
    """Verificar que la columna precio_pronto_pago existe y funciona"""
    print("🔍 Verificando columna precio_pronto_pago...")
    
    try:
        # 1. Verificar que la tabla cursos tenga la columna
        print("\n1. Verificando estructura de tabla cursos...")
        
        # Obtener un curso existente para probar
        cursos_response = supabase.table('cursos').select('*').limit(1).execute()
        
        if not cursos_response.data:
            print("❌ No hay cursos en la base de datos para probar")
            return False
            
        curso = cursos_response.data[0]
        print(f"✅ Curso encontrado: {curso.get('titulo', 'Sin título')}")
        
        # 2. Verificar si el campo precio_pronto_pago existe
        tiene_campo = 'precio_pronto_pago' in curso
        print(f"{'✅' if tiene_campo else '❌'} Campo precio_pronto_pago {'existe' if tiene_campo else 'NO EXISTE'}")
        
        if tiene_campo:
            valor_actual = curso.get('precio_pronto_pago')
            print(f"💰 Valor actual: {valor_actual}")
        
        # 3. Intentar actualizar el campo
        print("\n2. Probando actualización del campo...")
        
        curso_id = curso['id']
        nuevo_precio_pronto = 99.99
        
        update_response = supabase.table('cursos').update({
            'precio_pronto_pago': nuevo_precio_pronto
        }).eq('id', curso_id).execute()
        
        if update_response.data:
            print(f"✅ Campo actualizado correctamente a ${nuevo_precio_pronto}")
            
            # Verificar que se guardó
            verify_response = supabase.table('cursos').select('precio_pronto_pago').eq('id', curso_id).execute()
            if verify_response.data:
                valor_guardado = verify_response.data[0].get('precio_pronto_pago')
                print(f"✅ Valor verificado en BD: ${valor_guardado}")
                
                if float(valor_guardado) == nuevo_precio_pronto:
                    print("🎉 ¡La columna precio_pronto_pago funciona perfectamente!")
                    return True
                else:
                    print(f"❌ Error: Valor esperado ${nuevo_precio_pronto}, pero se guardó ${valor_guardado}")
                    return False
            else:
                print("❌ Error al verificar el valor guardado")
                return False
        else:
            print("❌ Error al actualizar el campo")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False

def verificar_cursos_con_precio_pronto():
    """Mostrar cursos que tienen precio de pronto pago configurado"""
    print("\n🔍 Verificando cursos con precio de pronto pago...")
    
    try:
        cursos_response = supabase.table('cursos').select('titulo, precio, precio_pronto_pago').execute()
        
        if not cursos_response.data:
            print("❌ No hay cursos en la base de datos")
            return
            
        cursos_con_pronto_pago = [
            c for c in cursos_response.data 
            if c.get('precio_pronto_pago') and c.get('precio_pronto_pago') > 0
        ]
        
        print(f"📊 Total de cursos: {len(cursos_response.data)}")
        print(f"💨 Cursos con pronto pago: {len(cursos_con_pronto_pago)}")
        
        if cursos_con_pronto_pago:
            print("\n💰 Cursos con precio de pronto pago:")
            for curso in cursos_con_pronto_pago:
                titulo = curso.get('titulo', 'Sin título')
                precio_regular = curso.get('precio', 0)
                precio_pronto = curso.get('precio_pronto_pago', 0)
                ahorro = precio_regular - precio_pronto if precio_regular > precio_pronto else 0
                
                print(f"  📚 {titulo}")
                print(f"    💰 Precio regular: ${precio_regular}")
                print(f"    ⚡ Precio pronto pago: ${precio_pronto}")
                print(f"    💵 Ahorro: ${ahorro}")
                print()
        else:
            print("ℹ️  Ningún curso tiene precio de pronto pago configurado")
            
    except Exception as e:
        print(f"❌ Error al verificar cursos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando verificación de precio de pronto pago...")
    print("=" * 60)
    
    # Verificar funcionalidad
    funciona = verificar_columna_precio_pronto_pago()
    
    if funciona:
        # Mostrar estadísticas
        verificar_cursos_con_precio_pronto()
        print("\n" + "=" * 60)
        print("✅ ¡Verificación completada exitosamente!")
        print("💡 El campo precio_pronto_pago está funcionando correctamente")
    else:
        print("\n" + "=" * 60)
        print("❌ La verificación falló")
        print("🔧 Posibles soluciones:")
        print("   1. Verificar que la columna precio_pronto_pago existe en Supabase")
        print("   2. Ejecutar el script SQL: agregar_precio_pronto_pago.sql")
        print("   3. Verificar permisos de la tabla cursos")
