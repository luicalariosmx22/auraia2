#!/usr/bin/env python3
"""
🧪 DIAGNÓSTICO RÁPIDO DE FUNCIONES DE CONOCIMIENTO
=================================================
Script para verificar que todas las funciones necesarias estén disponibles.
"""

def create_diagnostic_js():
    """Crear script de diagnóstico que se puede ejecutar en la consola del navegador"""
    
    diagnostic_js = """
// 🧪 DIAGNÓSTICO DE FUNCIONES DE CONOCIMIENTO
console.log('🔍 INICIANDO DIAGNÓSTICO DE FUNCIONES...');
console.log('='.repeat(60));

// 1. Verificar funciones básicas
const funcionesRequeridas = [
    'escapeHtml',
    'formatDate', 
    'crearElementoBloque',
    'mostrarConocimiento',
    'cargarConocimiento',
    'agregarBloque',
    'eliminarBloque',
    'editarBloque'
];

console.log('\\n📋 VERIFICANDO FUNCIONES REQUERIDAS:');
funcionesRequeridas.forEach(funcion => {
    const disponible = typeof window[funcion] === 'function';
    const estado = disponible ? '✅' : '❌';
    console.log(`${estado} ${funcion}: ${typeof window[funcion]}`);
});

// 2. Test de funciones de formato
console.log('\\n📅 PROBANDO FUNCIONES DE FORMATO:');
if (typeof window.escapeHtml === 'function') {
    try {
        const test = window.escapeHtml('<test>');
        console.log('✅ escapeHtml funciona:', test);
    } catch (e) {
        console.log('❌ escapeHtml error:', e.message);
    }
}

if (typeof window.formatDate === 'function') {
    try {
        const test = window.formatDate(new Date().toISOString());
        console.log('✅ formatDate funciona:', test);
    } catch (e) {
        console.log('❌ formatDate error:', e.message);
    }
}

// 3. Test de creación de bloques
console.log('\\n📚 PROBANDO CREACIÓN DE BLOQUES:');
if (typeof window.crearElementoBloque === 'function') {
    try {
        const bloqueTest = {
            id: 'test-123',
            contenido: 'Contenido de prueba',
            etiquetas: ['test'],
            prioridad: false,
            fecha_creacion: new Date().toISOString()
        };
        const html = window.crearElementoBloque(bloqueTest);
        console.log('✅ crearElementoBloque funciona, HTML length:', html.length);
    } catch (e) {
        console.log('❌ crearElementoBloque error:', e.message);
    }
}

// 4. Verificar container
console.log('\\n🎯 VERIFICANDO ELEMENTOS DOM:');
const container = document.getElementById('lista-conocimiento');
console.log('📋 Container lista-conocimiento:', !!container);
if (container) {
    console.log('📋 Container innerHTML length:', container.innerHTML.length);
}

// 5. Test de mostrarConocimiento con datos mock
console.log('\\n🔄 PROBANDO mostrarConocimiento:');
if (typeof window.mostrarConocimiento === 'function' && container) {
    try {
        const bloquesMock = [
            {
                id: 'mock-1',
                contenido: 'Primer bloque de prueba',
                etiquetas: ['test', 'mock'],
                prioridad: true,
                fecha_creacion: '2025-06-28T10:30:00Z'
            },
            {
                id: 'mock-2', 
                contenido: 'Segundo bloque de prueba',
                etiquetas: ['test'],
                prioridad: false,
                fecha_creacion: '2025-06-28T11:00:00Z'
            }
        ];
        
        window.mostrarConocimiento(bloquesMock);
        console.log('✅ mostrarConocimiento ejecutado');
        console.log('📋 Container después:', container.innerHTML.length, 'chars');
        
    } catch (e) {
        console.log('❌ mostrarConocimiento error:', e.message);
    }
}

console.log('\\n🎉 DIAGNÓSTICO COMPLETADO');
console.log('='.repeat(60));
"""
    
    return diagnostic_js

def main():
    diagnostic_script = create_diagnostic_js()
    
    print("🧪 DIAGNÓSTICO DE FUNCIONES DE CONOCIMIENTO")
    print("=" * 60)
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Abre el navegador en http://localhost:5000")
    print("2. Inicia sesión en el sistema")  
    print("3. Ve a Panel Cliente > Entrenar Nora")
    print("4. Abre la consola del navegador (F12)")
    print("5. Copia y pega el siguiente script:")
    print()
    print("=" * 60)
    print(diagnostic_script)
    print("=" * 60)
    print()
    print("💡 RESULTADOS ESPERADOS:")
    print("✅ Todas las funciones deben mostrar como disponibles")
    print("✅ Los tests de formato deben funcionar")
    print("✅ mostrarConocimiento debe mostrar 2 bloques de prueba")
    print()
    print("❌ Si algo falla, revisa los imports de JS en el HTML")

if __name__ == "__main__":
    main()
