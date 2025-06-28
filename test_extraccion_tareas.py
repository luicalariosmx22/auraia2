#!/usr/bin/env python3
"""
Test rápido para verificar la extracción mejorada de entidades en consultas de tareas
"""

import re
from typing import Optional, Dict

def limpiar_entidad(entidad: str) -> str:
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

def detectar_consulta_tareas_mejorado(mensaje: str) -> Optional[Dict]:
    """
    Versión mejorada de detección de consultas de tareas
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
        
        # Patrones con filtros integrados
        r"tareas?\s+(pendientes?|completadas?|urgentes?|en\s+proceso)\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
        r"(?:tiene|hay)\s+tareas?\s+(?:activas?\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
        
        # Patrones para empresas con S.A., Corp, etc.
        r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+)\s+(?:s\.a\.|inc|corp|ltd)\.?",
        
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
            entidad = limpiar_entidad(entidad)
            
            return {
                "es_consulta_tareas": True,
                "entidad": entidad,
                "patron_usado": patron
            }
    
    return None

def test_extraccion_entidades():
    """Test de extracción de entidades mejorado"""
    print("🧪 TEST: EXTRACCIÓN MEJORADA DE ENTIDADES")
    print("=" * 50)
    
    # Casos de test problemáticos
    consultas_test = [
        "tareas activas hay en suspiros pastelerias la empresa",
        "tareas de la empresa Suspiros Pastelerías",
        "¿Qué tareas tiene Juan Pérez?",
        "Tareas pendientes de María García",
        "Ver tareas de TechCorp empresa",
        "Mostrar tareas de Innovation Corp",
        "¿Hay tareas activas en Digital Solutions?",
        "Tareas urgentes de Luis Rodriguez",
        "Consultar tareas de la empresa ABC S.A."
    ]
    
    for i, consulta in enumerate(consultas_test, 1):
        print(f"\n📝 Test {i}: '{consulta}'")
        
        resultado = detectar_consulta_tareas_mejorado(consulta)
        
        if resultado:
            print(f"   ✅ DETECTADA")
            print(f"   📊 Entidad extraída: '{resultado['entidad']}'")
            print(f"   🔧 Patrón usado: {resultado['patron_usado']}")
        else:
            print(f"   ❌ NO DETECTADA")
    
    print(f"\n" + "=" * 50)
    print("🎯 COMPARACIÓN CON CASO PROBLEMÁTICO:")
    
    caso_problema = "tareas activas hay en suspiros pastelerias la empresa"
    print(f"   Consulta original: '{caso_problema}'")
    
    resultado = detectar_consulta_tareas_mejorado(caso_problema)
    if resultado:
        print(f"   ✅ Entidad corregida: '{resultado['entidad']}'")
        print(f"   📈 Mejora: Extrae 'suspiros pastelerias' en lugar de texto completo")
    else:
        print(f"   ❌ Aún no detectada")

if __name__ == "__main__":
    test_extraccion_entidades()
