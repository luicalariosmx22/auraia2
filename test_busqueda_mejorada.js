/**
 * Script de prueba para las mejoras del sistema de búsqueda de conocimiento
 * Carga este archivo en la consola del navegador en el panel de entrenamiento
 */

console.log('🧪 INICIANDO PRUEBA DE BÚSQUEDA MEJORADA');
console.log('=' * 50);

// Función principal de prueba de búsqueda
async function probarBusquedaMejorada() {
    try {
        console.log('1️⃣ Verificando funciones de búsqueda...');
        
        const funcionesBusqueda = [
            'filtrarConocimiento',
            'limpiarBusqueda', 
            'busquedaAvanzada',
            'mostrarTodosLosBloques',
            'actualizarOpcionesDropdown',
            'actualizarEstadoFiltros',
            'filtrarPorEtiqueta'
        ];
        
        const funcionesDisponibles = [];
        const funcionesFaltantes = [];
        
        funcionesBusqueda.forEach(func => {
            if (typeof window[func] === 'function') {
                funcionesDisponibles.push(func);
            } else {
                funcionesFaltantes.push(func);
            }
        });
        
        console.log(`✅ Funciones disponibles: ${funcionesDisponibles.join(', ')}`);
        if (funcionesFaltantes.length > 0) {
            console.log(`❌ Funciones faltantes: ${funcionesFaltantes.join(', ')}`);
        }
        
        // 2. Cargar datos si es necesario
        console.log('\n2️⃣ Verificando datos de conocimiento...');
        
        if (!window.conocimientoData || window.conocimientoData.length === 0) {
            console.log('📥 Cargando datos de conocimiento...');
            if (typeof window.cargarConocimiento === 'function') {
                await window.cargarConocimiento();
            }
        }
        
        if (window.conocimientoData && window.conocimientoData.length > 0) {
            console.log(`✅ Datos disponibles: ${window.conocimientoData.length} bloques`);
            
            // Analizar etiquetas disponibles
            const etiquetas = new Set();
            window.conocimientoData.forEach(bloque => {
                (bloque.etiquetas || []).forEach(e => etiquetas.add(e));
            });
            
            console.log(`🏷️ Etiquetas disponibles: ${Array.from(etiquetas).join(', ')}`);
            
        } else {
            console.log('❌ No hay datos de conocimiento disponibles');
            return;
        }
        
        // 3. Probar búsqueda de texto
        console.log('\n3️⃣ Probando búsqueda de texto...');
        await probarBusquedaTexto();
        
        // 4. Probar filtro por etiquetas
        console.log('\n4️⃣ Probando filtro por etiquetas...');
        await probarFiltroEtiquetas();
        
        // 5. Probar funciones de limpieza
        console.log('\n5️⃣ Probando funciones de limpieza...');
        await probarLimpieza();
        
        // 6. Probar búsqueda avanzada
        console.log('\n6️⃣ Probando búsqueda avanzada...');
        await probarBusquedaAvanzadaCompleta();
        
        console.log('\n🎉 PRUEBA DE BÚSQUEDA COMPLETADA');
        
    } catch (error) {
        console.error('❌ Error durante la prueba de búsqueda:', error);
    }
}

// Función para probar búsqueda de texto
async function probarBusquedaTexto() {
    const terminos = [
        'curso',
        'inteligencia artificial', 
        'presencial',
        'duración',
        'costo',
        'módulo',
        'julio',
        'AI' // término que podría no encontrar resultados
    ];
    
    console.log('🔍 Probando términos de búsqueda...');
    
    for (const termino of terminos) {
        console.log(`\n   Buscando: "${termino}"`);
        
        // Simular búsqueda
        if (typeof window.filtrarConocimiento === 'function') {
            window.filtrarConocimiento(termino);
            
            // Contar resultados visibles
            await new Promise(resolve => setTimeout(resolve, 100)); // Esperar renderizado
            
            const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
            console.log(`     Resultados: ${bloquesVisibles.length} bloques`);
            
        } else {
            console.log('     ❌ Función filtrarConocimiento no disponible');
        }
    }
    
    // Limpiar búsqueda al final
    if (typeof window.limpiarBusqueda === 'function') {
        window.limpiarBusqueda();
        console.log('✅ Búsqueda limpiada');
    }
}

// Función para probar filtro por etiquetas
async function probarFiltroEtiquetas() {
    // Obtener etiquetas disponibles
    const etiquetasDisponibles = new Set();
    if (window.conocimientoData) {
        window.conocimientoData.forEach(bloque => {
            (bloque.etiquetas || []).forEach(e => etiquetasDisponibles.add(e));
        });
    }
    
    const etiquetas = Array.from(etiquetasDisponibles);
    console.log(`🏷️ Probando filtros con ${etiquetas.length} etiquetas...`);
    
    for (const etiqueta of etiquetas.slice(0, 3)) { // Probar solo las primeras 3
        console.log(`\n   Filtrando por: "${etiqueta}"`);
        
        if (typeof window.filtrarPorEtiqueta === 'function') {
            window.filtrarPorEtiqueta(etiqueta);
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
            console.log(`     Resultados: ${bloquesVisibles.length} bloques`);
            
        } else {
            console.log('     ❌ Función filtrarPorEtiqueta no disponible');
        }
    }
    
    // Probar "mostrar todas"
    console.log('\n   Filtrando por: "todas"');
    if (typeof window.filtrarPorEtiqueta === 'function') {
        window.filtrarPorEtiqueta(null);
        console.log('     ✅ Filtro "todas" aplicado');
    }
}

// Función para probar limpieza
async function probarLimpieza() {
    console.log('🧹 Probando funciones de limpieza...');
    
    // Aplicar una búsqueda primero
    if (typeof window.filtrarConocimiento === 'function') {
        window.filtrarConocimiento('curso');
        console.log('   📝 Búsqueda aplicada: "curso"');
        
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Limpiar
        if (typeof window.limpiarBusqueda === 'function') {
            window.limpiarBusqueda();
            console.log('   ✅ Búsqueda limpiada');
            
            // Verificar que el input está limpio
            const buscarInput = document.getElementById('buscar-conocimiento');
            if (buscarInput && buscarInput.value === '') {
                console.log('   ✅ Input de búsqueda limpio');
            } else {
                console.log('   ⚠️ Input de búsqueda no está limpio');
            }
            
        } else {
            console.log('   ❌ Función limpiarBusqueda no disponible');
        }
    }
    
    // Probar mostrar todos los bloques
    if (typeof window.mostrarTodosLosBloques === 'function') {
        window.mostrarTodosLosBloques();
        console.log('   ✅ Función mostrarTodosLosBloques ejecutada');
    }
}

// Función para probar búsqueda avanzada
async function probarBusquedaAvanzadaCompleta() {
    console.log('🔬 Probando búsqueda avanzada...');
    
    const terminosAvanzados = [
        'inteligencia artificial',
        'curso presencial',
        'duración costo'
    ];
    
    for (const termino of terminosAvanzados) {
        console.log(`\n   Búsqueda avanzada: "${termino}"`);
        
        if (typeof window.busquedaAvanzada === 'function') {
            const resultados = window.busquedaAvanzada(termino);
            console.log(`     Resultados: ${resultados.length} bloques`);
            
            if (resultados.length > 0) {
                console.log(`     Primer resultado relevancia: ${resultados[0].relevancia || 'N/A'}`);
            }
            
        } else {
            console.log('     ❌ Función busquedaAvanzada no disponible');
        }
    }
}

// Función para probar interacciones con elementos del DOM
function probarInteraccionesDOM() {
    console.log('\n7️⃣ Probando interacciones con DOM...');
    
    // Probar input de búsqueda
    const buscarInput = document.getElementById('buscar-conocimiento');
    if (buscarInput) {
        console.log('   ✅ Input de búsqueda encontrado');
        
        // Simular escritura
        buscarInput.value = 'inteligencia artificial';
        buscarInput.dispatchEvent(new Event('input'));
        console.log('   ✅ Evento input simulado');
        
        // Simular Enter
        buscarInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
        console.log('   ✅ Evento Enter simulado');
        
        // Simular Escape
        setTimeout(() => {
            buscarInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
            console.log('   ✅ Evento Escape simulado');
        }, 1000);
        
    } else {
        console.log('   ❌ Input de búsqueda no encontrado');
    }
    
    // Probar dropdown de filtros
    const filtroEtiqueta = document.getElementById('filtro-etiqueta');
    if (filtroEtiqueta) {
        console.log('   ✅ Dropdown de filtros encontrado');
        console.log(`   📊 Opciones disponibles: ${filtroEtiqueta.options.length}`);
        
        // Mostrar algunas opciones
        for (let i = 0; i < Math.min(3, filtroEtiqueta.options.length); i++) {
            console.log(`     - ${filtroEtiqueta.options[i].text}`);
        }
        
    } else {
        console.log('   ❌ Dropdown de filtros no encontrado');
    }
}

// Función para generar reporte de prueba
function generarReportePrueba() {
    console.log('\n📊 REPORTE DE PRUEBA DE BÚSQUEDA');
    console.log('=' * 40);
    
    const reporte = {
        timestamp: new Date().toISOString(),
        funcionesDisponibles: [],
        elementosDOM: {},
        datosConocimiento: {
            total: window.conocimientoData ? window.conocimientoData.length : 0,
            etiquetas: 0,
            bloquesIA: 0
        }
    };
    
    // Verificar funciones
    const funciones = ['filtrarConocimiento', 'limpiarBusqueda', 'busquedaAvanzada', 'filtrarPorEtiqueta'];
    funciones.forEach(func => {
        if (typeof window[func] === 'function') {
            reporte.funcionesDisponibles.push(func);
        }
    });
    
    // Verificar elementos DOM
    const elementos = ['buscar-conocimiento', 'filtro-etiqueta', 'conocimiento-list'];
    elementos.forEach(id => {
        reporte.elementosDOM[id] = document.getElementById(id) !== null;
    });
    
    // Analizar datos
    if (window.conocimientoData) {
        const etiquetas = new Set();
        let bloquesIA = 0;
        
        window.conocimientoData.forEach(bloque => {
            (bloque.etiquetas || []).forEach(e => etiquetas.add(e));
            if (bloque.etiquetas && bloque.etiquetas.some(e => 
                e.toLowerCase().includes('inteligencia') || e.toLowerCase().includes('artificial')
            )) {
                bloquesIA++;
            }
        });
        
        reporte.datosConocimiento.etiquetas = etiquetas.size;
        reporte.datosConocimiento.bloquesIA = bloquesIA;
    }
    
    console.log('📋 Funciones disponibles:', reporte.funcionesDisponibles.join(', '));
    console.log('🖥️ Elementos DOM:', Object.entries(reporte.elementosDOM).map(([k,v]) => `${k}: ${v ? '✅' : '❌'}`).join(', '));
    console.log('📊 Datos:', `${reporte.datosConocimiento.total} bloques, ${reporte.datosConocimiento.etiquetas} etiquetas, ${reporte.datosConocimiento.bloquesIA} bloques IA`);
    
    return reporte;
}

// Exportar funciones
window.probarBusquedaMejorada = probarBusquedaMejorada;
window.probarBusquedaTexto = probarBusquedaTexto;
window.probarFiltroEtiquetas = probarFiltroEtiquetas;
window.probarInteraccionesDOM = probarInteraccionesDOM;
window.generarReportePrueba = generarReportePrueba;

// Ejecutar automáticamente si estamos en el panel
if (document.getElementById('buscar-conocimiento')) {
    console.log('🎯 Panel de búsqueda detectado - ejecutando prueba automática');
    setTimeout(() => {
        probarBusquedaMejorada().then(() => {
            probarInteraccionesDOM();
            const reporte = generarReportePrueba();
            console.log('\n🎉 PRUEBA COMPLETA FINALIZADA');
        });
    }, 2000);
} else {
    console.log('📝 Para ejecutar la prueba manualmente, usa: probarBusquedaMejorada()');
    console.log('📝 Para probar interacciones DOM, usa: probarInteraccionesDOM()');
    console.log('📝 Para generar reporte, usa: generarReportePrueba()');
}
