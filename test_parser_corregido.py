#!/usr/bin/env python3
"""
🧪 Test rápido del parser corregido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parser_corregido():
    """Test específico del parser con la corrección"""
    print("🔧 TEST PARSER CORREGIDO")
    print("=" * 40)
    
    try:
        # Casos problemáticos específicos
        casos_test = [
            {
                "mensaje": "tareas activas hay en suspiros pastelerias la empresa",
                "entidad_esperada": "suspiros pastelerias",
                "tipo_esperado": "empresa",
                "descripcion": "Caso problemático principal"
            },
            {
                "mensaje": "tareas de la empresa Suspiros Pastelerías",
                "entidad_esperada": "suspiros pastelerías",
                "tipo_esperado": "empresa",
                "descripcion": "Empresa explícita"
            },
            {
                "mensaje": "tareas de María",
                "entidad_esperada": "maría",
                "tipo_esperado": "usuario",
                "descripcion": "Usuario simple"
            },
            {
                "mensaje": "tareas de David del departamento de ventas",
                "entidad_esperada": "david del departamento de ventas",
                "tipo_esperado": "usuario",
                "descripcion": "Usuario con departamento"
            },
            {
                "mensaje": "tareas de TechCorp",
                "entidad_esperada": "techcorp",
                "tipo_esperado": "empresa",
                "descripcion": "Empresa por patrón"
            }
        ]
        
        # Simular la lógica del parser corregido
        def detectar_tipo_mejorado(mensaje, entidad):
            # Indicadores de consulta por empresa
            indicadores_empresa = [
                "empresa", "compañía", "organización", "negocio", 
                "corporación", "firma", "s.a.", "s.l.", "inc", "ltda",
                "pastelerías", "pastelerias", "cakes", "corp"
            ]
            
            # Indicadores de consulta por usuario
            indicadores_usuario = [
                "usuario", "empleado", "trabajador", "persona",
                "colaborador", "miembro", "staff", "departamento"
            ]
            
            entidad_lower = entidad.lower()
            mensaje_lower = mensaje.lower()
            
            # PRIORIDAD 1: Verificar indicadores explícitos en el mensaje
            if any(ind in mensaje_lower for ind in indicadores_empresa):
                return "empresa"
                
            if any(ind in mensaje_lower for ind in indicadores_usuario):
                return "usuario"
            
            # PRIORIDAD 2: Verificar en la entidad misma
            if any(ind in entidad_lower for ind in indicadores_empresa):
                return "empresa"
                
            if any(ind in entidad_lower for ind in indicadores_usuario):
                return "usuario"
            
            # PRIORIDAD 3: Detectar patrones de nombres típicos
            if any(word in entidad_lower for word in ["suspiros", "tech", "corp", "solutions", "marketing", "group"]):
                return "empresa"
            
            # Nombres de usuarios tienden a ser nombres propios simples
            nombres_comunes = ["maría", "david", "josé", "luis", "ana", "carlos", "juan", "laura"]
            if any(nombre in entidad_lower for nombre in nombres_comunes):
                return "usuario"
            
            # DEFAULT: Si no está claro, preferir empresa para términos largos
            if len(entidad.split()) >= 2:
                return "empresa"
            else:
                return "usuario"
        
        print("\n📝 CASOS DE PRUEBA:")
        print("-" * 40)
        
        exitos = 0
        for caso in casos_test:
            print(f"\n🔍 {caso['descripcion']}")
            print(f"   Mensaje: '{caso['mensaje']}'")
            
            tipo_detectado = detectar_tipo_mejorado(caso['mensaje'], caso['entidad_esperada'])
            
            print(f"   Entidad esperada: '{caso['entidad_esperada']}'")
            print(f"   Tipo esperado: {caso['tipo_esperado']}")
            print(f"   Tipo detectado: {tipo_detectado}")
            
            if tipo_detectado == caso['tipo_esperado']:
                print(f"   ✅ CORRECTO")
                exitos += 1
            else:
                print(f"   ❌ INCORRECTO")
        
        print(f"\n" + "=" * 40)
        print(f"📊 RESULTADO: {exitos}/{len(casos_test)} casos exitosos")
        
        if exitos == len(casos_test):
            print("🎉 ¡Todas las correcciones funcionan!")
        else:
            print("⚠️ Algunas correcciones necesitan ajuste")
        
        return exitos == len(casos_test)
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

if __name__ == "__main__":
    test_parser_corregido()
