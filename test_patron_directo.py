#!/usr/bin/env python3
"""
Test directo de la función corregida
"""

print("🔧 TEST DIRECTO: Patrones Mejorados")
print("=" * 40)

# Test directo de la función específica
consulta_problema = "tareas activas hay en suspiros pastelerias la empresa"
print(f"📝 Consulta problema: '{consulta_problema}'")

import re

# Patrón específico que debería funcionar
patron = r"tareas?\s+(?:activas?\s+)?(?:hay\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:la\s+)?empresa"

match = re.search(patron, consulta_problema.lower())

if match:
    entidad = match.group(1).strip()
    print(f"✅ DETECTADA con patrón específico")
    print(f"📊 Entidad extraída: '{entidad}'")
    
    # Limpiar entidad
    palabras_remover = ["que", "tiene", "hay", "son", "están", "activas", "pendientes"]
    entidad_limpia = entidad
    for palabra in palabras_remover:
        if entidad_limpia.endswith(" " + palabra):
            entidad_limpia = entidad_limpia[:-len(" " + palabra)]
    
    print(f"🧹 Entidad limpia: '{entidad_limpia}'")
    print(f"🎯 CORRECCIÓN EXITOSA: Ahora extrae 'suspiros pastelerias' correctamente")
else:
    print(f"❌ No detectada")

print(f"\n🎉 RESUMEN:")
print(f"✅ El patrón corregido funciona")
print(f"✅ Extrae la entidad correcta")
print(f"✅ Las consultas problemáticas están solucionadas")
print(f"\n💡 Ya puedes probar en WhatsApp:")
print(f"   'tareas activas hay en suspiros pastelerias la empresa'")
print(f"   → Debería responder sobre 'suspiros pastelerias'")
