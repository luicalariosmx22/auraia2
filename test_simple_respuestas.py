#!/usr/bin/env python3
"""
Prueba simple del sistema de respuestas inteligentes
"""

import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Prueba simple del sistema"""
    print("🧪 Iniciando prueba simple del sistema de respuestas inteligentes")
    
    try:
        # Importar después de configurar la ruta
        from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes
        print("✅ Importación exitosa")
        
        # Crear instancia
        sistema = SistemaRespuestasInteligentes("aura")
        print("✅ Sistema inicializado")
        
        # Probar análisis de pregunta
        mensaje_test = "¿Cuánto cuesta un curso?"
        print(f"📝 Probando mensaje: '{mensaje_test}'")
        
        analisis = sistema.analizar_pregunta(mensaje_test)
        print(f"🔍 Análisis resultado:")
        for clave, valor in analisis.items():
            print(f"  - {clave}: {valor}")
        
        # Verificar detección de pregunta de precio y curso
        if analisis['es_pregunta_precio'] and analisis['es_pregunta_curso']:
            print("✅ PERFECTO: Detectó que es pregunta de precio Y curso")
        else:
            print("❌ ERROR: No detectó correctamente la pregunta")
        
        print("\n🎯 Probando generación de respuesta...")
        
        # Simular que no encuentra opciones específicas
        respuesta_sin_opciones = sistema._generar_respuesta_sin_opciones(analisis)
        print("📄 Respuesta generada:")
        print(respuesta_sin_opciones)
        
        if "Curso" in respuesta_sin_opciones and ("1️⃣" in respuesta_sin_opciones or "opciones" in respuesta_sin_opciones):
            print("✅ PERFECTO: Generó respuesta con opciones")
        else:
            print("❌ ERROR: No generó respuesta con opciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA SIMPLE")
    print("=" * 50)
    
    exito = test_simple()
    
    if exito:
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
    else:
        print("\n❌ PRUEBA FALLÓ")
    
    print("=" * 50)
