#!/usr/bin/env python3
"""
Test del parser de consultas sin dependencias de Supabase
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ConsultorTareasSimple:
    """Versión simplificada solo para probar el parser"""
    
    def __init__(self, usuario_consultor, nombre_nora="aura"):
        self.usuario_consultor = usuario_consultor
        self.nombre_nora = nombre_nora
    
    def detectar_consulta_tareas(self, mensaje):
        """
        Detecta si el mensaje es una consulta sobre tareas y extrae parámetros
        """
        mensaje_lower = mensaje.lower().strip()
        
        # Patrones mejorados para mejor extracción de entidades
        patrones_tareas = [
            # Patrones específicos para empresas
            r"tareas?\s+de\s+(?:la\s+)?empresa\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\?|$)",
            r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:empresa|compañía)",
            r"tareas?\s+(?:activas?\s+)?(?:hay\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:la\s+)?empresa",
            
            # Patrones específicos para usuarios
            r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\s+tiene|\?|$)",
            r"qué\s+tareas?\s+tiene\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"cuáles?\s+son\s+las\s+tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"mostrar\s+tareas?\s+(?:de\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            r"ver\s+tareas?\s+(?:de\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
            
            # Patrón genérico (más restrictivo)
            r"tareas?\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{2,30})(?:\?|$)"
        ]
        
        for patron in patrones_tareas:
            match = re.search(patron, mensaje_lower)
            if match:
                # Extraer entidad y limpiarla
                if len(match.groups()) == 2:  # Patrón con filtro
                    filtro_extra = match.group(1)
                    entidad = match.group(2).strip()
                else:
                    entidad = match.group(1).strip()
                
                # Limpiar la entidad de palabras innecesarias
                entidad = self._limpiar_entidad(entidad)
                
                # Determinar tipo de consulta
                tipo_consulta = self._determinar_tipo_consulta(mensaje_lower, entidad)
                
                return {
                    "es_consulta_tareas": True,
                    "entidad": entidad,
                    "tipo": tipo_consulta,
                    "filtros": self._extraer_filtros(mensaje_lower)
                }
        
        return None
    
    def _limpiar_entidad(self, entidad):
        """Limpia la entidad extraída de palabras innecesarias"""
        # Remover palabras comunes al final
        palabras_remover = [
            "que", "tiene", "hay", "son", "están", "activas", "pendientes",
            "completadas", "urgentes", "vencidas", "empresa", "la empresa"
        ]
        
        entidad_limpia = entidad
        for palabra in palabras_remover:
            # Remover al final
            if entidad_limpia.endswith(" " + palabra):
                entidad_limpia = entidad_limpia[:-len(" " + palabra)]
            # Remover al inicio
            if entidad_limpia.startswith(palabra + " "):
                entidad_limpia = entidad_limpia[len(palabra + " "):]
        
        return entidad_limpia.strip()
    
    def _determinar_tipo_consulta(self, mensaje, entidad):
        """Determina si la consulta es por usuario o empresa"""
        
        # Indicadores de consulta por empresa
        indicadores_empresa = [
            "empresa", "compañía", "organización", "negocio", 
            "corporación", "firma", "s.a.", "s.l.", "inc", "ltda"
        ]
        
        # Indicadores de consulta por usuario
        indicadores_usuario = [
            "usuario", "empleado", "trabajador", "persona",
            "colaborador", "miembro", "staff"
        ]
        
        entidad_lower = entidad.lower()
        mensaje_lower = mensaje.lower()
        
        # Verificar indicadores explícitos
        if any(ind in mensaje_lower for ind in indicadores_empresa):
            return "empresa"
        if any(ind in mensaje_lower for ind in indicadores_usuario):
            return "usuario"
        
        # Verificar en la entidad misma
        if any(ind in entidad_lower for ind in indicadores_empresa):
            return "empresa"
        
        # Por defecto, asumir que es usuario si no hay indicadores claros
        return "usuario"
    
    def _extraer_filtros(self, mensaje):
        """Extrae filtros adicionales del mensaje"""
        filtros = {}
        
        # Filtros de estatus
        if "pendiente" in mensaje:
            filtros["estatus"] = "pendiente"
        elif "completada" in mensaje or "terminada" in mensaje:
            filtros["estatus"] = "completada"
        elif "en proceso" in mensaje or "progreso" in mensaje:
            filtros["estatus"] = "en_proceso"
        
        # Filtros de prioridad
        if "urgente" in mensaje or "alta" in mensaje:
            filtros["prioridad"] = "alta"
        elif "baja" in mensaje:
            filtros["prioridad"] = "baja"
        
        return filtros

def test_parser_simple():
    """Test del parser sin dependencias externas"""
    print("🔧 TEST PARSER SIMPLE")
    print("=" * 40)
    
    try:
        # Usuario de prueba
        usuario_test = {
            'id': 1,
            'nombre_completo': 'Test User',
            'telefono': '+56900000001',
            'email': 'test@test.com',
            'role': 'super_admin',
            'is_active': True,
            'cliente_id': 1
        }
        
        consultor = ConsultorTareasSimple(usuario_test, "aura")
        print("✅ ConsultorTareasSimple instanciado")
        
        # Casos de prueba problemáticos
        casos_test = [
            {
                "consulta": "tareas activas hay en suspiros pastelerias la empresa",
                "entidad_esperada": "suspiros pastelerias",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "tareas de la empresa Suspiros Pastelerías",
                "entidad_esperada": "suspiros pastelerías",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "tareas de María del departamento de ventas",
                "entidad_esperada": "maría del departamento de ventas",
                "tipo_esperado": "usuario"
            },
            {
                "consulta": "¿Qué tareas tiene José?",
                "entidad_esperada": "josé",
                "tipo_esperado": "usuario"
            }
        ]
        
        print("\n📝 CASOS DE PRUEBA:")
        print("-" * 40)
        
        for caso in casos_test:
            print(f"\n🔍 Consulta: '{caso['consulta']}'")
            resultado = consultor.detectar_consulta_tareas(caso['consulta'])
            
            if resultado:
                entidad_obtenida = resultado.get('entidad', '')
                tipo_obtenido = resultado.get('tipo', '')
                
                print(f"   📊 Resultado: {resultado}")
                print(f"   🎯 Entidad obtenida: '{entidad_obtenida}'")
                print(f"   🎯 Tipo obtenido: '{tipo_obtenido}'")
                
                # Verificaciones
                if entidad_obtenida.lower() == caso['entidad_esperada'].lower():
                    print(f"   ✅ ENTIDAD CORRECTA")
                else:
                    print(f"   ❌ ENTIDAD INCORRECTA (esperaba: '{caso['entidad_esperada']}')")
                
                if tipo_obtenido == caso['tipo_esperado']:
                    print(f"   ✅ TIPO CORRECTO")
                else:
                    print(f"   ❌ TIPO INCORRECTO (esperaba: '{caso['tipo_esperado']}')")
            else:
                print(f"   ❌ NO DETECTADA")
        
        print(f"\n" + "=" * 40)
        print("🎯 TEST COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser_simple()
