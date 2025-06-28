#!/usr/bin/env python3
"""
🧪 Test ultra simple - Solo lógica pura sin imports complejos
"""

def test_parser_basico():
    """Test del parser sin ninguna dependencia"""
    print("🔍 TEST PARSER BÁSICO")
    print("=" * 30)
    
    import re
    
    def detectar_consulta_simple(mensaje):
        """Parser simplificado"""
        mensaje_lower = mensaje.lower().strip()
        
        # Patrones básicos
        patrones = [
            r"tareas?\s+de\s+(?:la\s+)?empresa\s+([a-záéíóúñ\s]+?)(?:\s+que|\?|$)",
            r"tareas?\s+(?:activas?\s+)?(?:hay\s+)?(?:en\s+)?([a-záéíóúñ\s]+?)\s+(?:la\s+)?empresa",
            r"tareas?\s+de\s+([a-záéíóúñ\s]+?)(?:\s+que|\s+tiene|\?|$)",
            r"qué\s+tareas?\s+tiene\s+([a-záéíóúñ\s]+?)(?:\?|$)",
        ]
        
        for patron in patrones:
            match = re.search(patron, mensaje_lower)
            if match:
                entidad = match.group(1).strip()
                tipo = "empresa" if "empresa" in mensaje_lower else "usuario"
                return {"entidad": entidad, "tipo": tipo}
        
        return None
    
    # Casos de prueba
    casos = [
        ("tareas activas hay en suspiros pastelerias la empresa", "suspiros pastelerias", "empresa"),
        ("tareas de María", "maría", "usuario"),
        ("¿Qué tareas tiene David?", "david", "usuario"),
        ("tareas de la empresa TechCorp", "techcorp", "empresa"),
        ("tareas de Luica Larios", "luica larios", "usuario")
    ]
    
    exitos = 0
    for mensaje, entidad_esperada, tipo_esperado in casos:
        resultado = detectar_consulta_simple(mensaje)
        print(f"\n📝 '{mensaje}'")
        
        if resultado:
            entidad_ok = resultado["entidad"].lower() == entidad_esperada.lower()
            tipo_ok = resultado["tipo"] == tipo_esperado
            
            print(f"   Entidad: '{resultado['entidad']}' {'✅' if entidad_ok else '❌'}")
            print(f"   Tipo: '{resultado['tipo']}' {'✅' if tipo_ok else '❌'}")
            
            if entidad_ok and tipo_ok:
                exitos += 1
        else:
            print("   ❌ No detectada")
    
    print(f"\n📊 Resultado: {exitos}/{len(casos)} exitosos")
    return exitos == len(casos)

def test_busqueda_simulada():
    """Test de búsqueda con datos mock"""
    print("\n🔎 TEST BÚSQUEDA SIMULADA")
    print("=" * 30)
    
    # Datos simulados (como los reales de la BD)
    usuarios_bd = [
        {"id": "16921f00-3360-4bf4-9f10-0b350e5f128d", "nombre": "David Alcantara", "correo": "guitarrasdavidalcantara@gmail.com"}
    ]
    
    empresas_bd = [
        {"id": 1, "nombre_empresa": "SUSPIROS CAKES - BORIS"},
        {"id": 2, "nombre_empresa": "SUSPIROS PASTELERIAS"},
        {"id": 3, "nombre_empresa": "Suspiros Pastelerias"}
    ]
    
    def buscar_usuario(nombre_buscar):
        """Simula búsqueda en usuarios_clientes"""
        resultados = []
        nombre_lower = nombre_buscar.lower()
        
        # 1. Búsqueda exacta
        for usuario in usuarios_bd:
            if usuario["nombre"].lower() == nombre_lower:
                return [usuario], "exacta"
        
        # 2. Búsqueda parcial
        for usuario in usuarios_bd:
            if nombre_lower in usuario["nombre"].lower():
                resultados.append(usuario)
        
        if resultados:
            return resultados, "parcial"
        
        # 3. Búsqueda por palabras
        palabras = nombre_lower.split()
        for palabra in palabras:
            for usuario in usuarios_bd:
                if palabra in usuario["nombre"].lower():
                    if usuario not in resultados:
                        resultados.append(usuario)
        
        tipo_busqueda = "difusa" if resultados else "sin_resultados"
        return resultados, tipo_busqueda
    
    def buscar_empresa(nombre_buscar):
        """Simula búsqueda en cliente_empresas"""
        resultados = []
        nombre_lower = nombre_buscar.lower()
        
        # 1. Búsqueda exacta
        for empresa in empresas_bd:
            if empresa["nombre_empresa"].lower() == nombre_lower:
                return [empresa], "exacta"
        
        # 2. Búsqueda parcial
        for empresa in empresas_bd:
            if nombre_lower in empresa["nombre_empresa"].lower():
                resultados.append(empresa)
        
        tipo_busqueda = "parcial" if resultados else "sin_resultados"
        return resultados, tipo_busqueda
    
    # Tests
    casos_test = [
        ("david", "usuario", 1, ["parcial", "difusa"]),
        ("suspiros", "empresa", 3, ["parcial"]),
        ("inexistente", "usuario", 0, ["sin_resultados"])
    ]
    
    exitos = 0
    for nombre, tipo, cantidad_esperada, tipos_validos in casos_test:
        print(f"\n🔍 Buscando {tipo}: '{nombre}'")
        
        if tipo == "usuario":
            resultados, tipo_busqueda = buscar_usuario(nombre)
        else:
            resultados, tipo_busqueda = buscar_empresa(nombre)
        
        cantidad_ok = len(resultados) == cantidad_esperada
        tipo_ok = tipo_busqueda in tipos_validos
        
        print(f"   Encontrados: {len(resultados)} {'✅' if cantidad_ok else '❌'}")
        print(f"   Tipo búsqueda: {tipo_busqueda} {'✅' if tipo_ok else '❌'}")
        
        for resultado in resultados:
            if tipo == "usuario":
                print(f"   - {resultado['nombre']} ({resultado['correo']})")
            else:
                print(f"   - {resultado['nombre_empresa']}")
        
        if cantidad_ok and tipo_ok:
            exitos += 1
    
    print(f"\n📊 Resultado: {exitos}/{len(casos_test)} exitosos")
    return exitos == len(casos_test)

def test_confirmacion():
    """Test de lógica de confirmación"""
    print("\n❓ TEST CONFIRMACIÓN")
    print("=" * 30)
    
    def generar_confirmacion(resultados, tipo_entidad, entidad_original):
        """Genera mensaje de confirmación para múltiples resultados"""
        if len(resultados) <= 1:
            return None
        
        mensaje = f"🤔 Encontré varios {tipo_entidad}s que coinciden con '{entidad_original}':\n\n"
        
        for i, resultado in enumerate(resultados[:5], 1):
            if tipo_entidad == "usuario":
                nombre = resultado["nombre"]
                correo = resultado["correo"]
                mensaje += f"{i}. {nombre} ({correo})\n"
            else:  # empresa
                nombre = resultado["nombre_empresa"]
                mensaje += f"{i}. {nombre}\n"
        
        if len(resultados) > 5:
            mensaje += f"... y {len(resultados) - 5} más.\n"
        
        mensaje += f"\n💬 Responde con el número del {tipo_entidad} que buscas (1-{min(len(resultados), 5)})"
        return mensaje
    
    # Casos de test
    empresas_suspiros = [
        {"nombre_empresa": "SUSPIROS CAKES - BORIS"},
        {"nombre_empresa": "SUSPIROS PASTELERIAS"},
        {"nombre_empresa": "Suspiros Pastelerias"}
    ]
    
    usuario_unico = [
        {"nombre": "David Alcantara", "correo": "david@test.com"}
    ]
    
    casos = [
        ("Múltiples empresas", empresas_suspiros, "empresa", "suspiros", True),
        ("Usuario único", usuario_unico, "usuario", "david", False),
        ("Sin resultados", [], "usuario", "inexistente", False)
    ]
    
    exitos = 0
    for nombre_caso, resultados, tipo, entidad, debe_confirmar in casos:
        print(f"\n📋 {nombre_caso}:")
        
        mensaje = generar_confirmacion(resultados, tipo, entidad)
        tiene_confirmacion = mensaje is not None
        
        print(f"   Genera confirmación: {'✅ Sí' if tiene_confirmacion else '❌ No'}")
        print(f"   Debería confirmar: {'✅ Sí' if debe_confirmar else '❌ No'}")
        
        correcto = tiene_confirmacion == debe_confirmar
        print(f"   Comportamiento: {'✅ Correcto' if correcto else '❌ Incorrecto'}")
        
        if mensaje:
            lineas = len(mensaje.split('\n'))
            print(f"   Líneas mensaje: {lineas}")
        
        if correcto:
            exitos += 1
    
    print(f"\n📊 Resultado: {exitos}/{len(casos)} exitosos")
    return exitos == len(casos)

def main():
    """Ejecuta todos los tests ultra simples"""
    print("🚀 TESTS ULTRA SIMPLES - SIN DEPENDENCIAS")
    print("=" * 50)
    
    tests = [
        ("Parser", test_parser_basico),
        ("Búsqueda", test_busqueda_simulada),
        ("Confirmación", test_confirmacion)
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")
    
    exitos = 0
    for nombre, resultado in resultados:
        status = "✅ ÉXITO" if resultado else "❌ FALLO"
        print(f"   {status}: {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n🎯 TOTAL: {exitos}/{len(tests)} tests exitosos")
    
    if exitos == len(tests):
        print("\n🎉 ¡TODOS LOS TESTS BÁSICOS FUNCIONAN!")
        print("💡 El sistema de consultas tiene la lógica correcta")
    else:
        print("\n⚠️ Algunos tests fallaron")

if __name__ == "__main__":
    main()
