/**
 * Script especializado para probar el filtrado de conocimiento
 * con los datos reales de "Curso Inteligencia Artificial" desde Supabase
 * 
 * Carga este archivo en la consola del navegador en el panel de entrenamiento
 */

// Función principal de prueba
async function probarConocimientoIA() {
    console.log('🧪 INICIANDO PRUEBA DE CONOCIMIENTO IA');
    console.log('=' * 50);
    
    try {
        // 1. Verificar que las funciones principales estén disponibles
        console.log('1️⃣ Verificando funciones disponibles...');
        
        const funcionesRequeridas = [
            'cargarConocimiento',
            'filtrarPorEtiqueta', 
            'buscarConocimiento',
            'mostrarConocimiento',
            'actualizarEstadisticas'
        ];
        
        const funcionesDisponibles = [];
        const funcionesFaltantes = [];
        
        funcionesRequeridas.forEach(func => {
            if (typeof window[func] === 'function') {
                funcionesDisponibles.push(func);
            } else {
                funcionesFaltantes.push(func);
            }
        });
        
        console.log(`✅ Funciones disponibles: ${funcionesDisponibles.join(', ')}`);
        if (funcionesFaltantes.length > 0) {
            console.log(`⚠️ Funciones faltantes: ${funcionesFaltantes.join(', ')}`);
        }
        
        // 2. Cargar datos de conocimiento desde el servidor
        console.log('\n2️⃣ Cargando datos de conocimiento...');
        
        if (typeof window.cargarConocimiento === 'function') {
            await window.cargarConocimiento();
            
            // Verificar que se cargaron datos
            if (window.conocimientoData && window.conocimientoData.length > 0) {
                console.log(`✅ Datos cargados: ${window.conocimientoData.length} bloques`);
                
                // Analizar los datos cargados
                const datosAnalisis = analizarDatosConocimiento(window.conocimientoData);
                mostrarAnalisisDetallado(datosAnalisis);
                
            } else {
                console.log('❌ No se cargaron datos de conocimiento');
                console.log('🔄 Intentando cargar datos de prueba...');
                await cargarDatosPrueba();
            }
        } else {
            console.log('❌ Función cargarConocimiento no disponible');
            console.log('🔄 Cargando datos de prueba...');
            await cargarDatosPrueba();
        }
        
        // 3. Probar filtrado específico para IA
        console.log('\n3️⃣ Probando filtrado de Inteligencia Artificial...');
        await probarFiltradoIA();
        
        // 4. Probar búsqueda de texto
        console.log('\n4️⃣ Probando búsqueda de texto...');
        await probarBusquedaTexto();
        
        // 5. Probar actualización de estadísticas
        console.log('\n5️⃣ Probando actualización de estadísticas...');
        await probarEstadisticas();
        
        console.log('\n🎉 PRUEBA COMPLETADA EXITOSAMENTE');
        
    } catch (error) {
        console.error('❌ Error durante la prueba:', error);
        console.log('🔧 Intentando diagnóstico...');
        await diagnosticarProblemas();
    }
}

// Función para analizar los datos de conocimiento
function analizarDatosConocimiento(datos) {
    const analisis = {
        total: datos.length,
        conIA: 0,
        conPrioridad: 0,
        etiquetasUnicas: new Set(),
        fechaMinima: null,
        fechaMaxima: null,
        longitudPromedio: 0,
        bloquesIA: []
    };
    
    let longitudTotal = 0;
    
    datos.forEach(bloque => {
        // Contar contenido
        const contenido = bloque.contenido || '';
        longitudTotal += contenido.length;
        
        // Verificar prioridad
        if (bloque.prioridad) {
            analisis.conPrioridad++;
        }
        
        // Procesar etiquetas
        if (bloque.etiquetas && Array.isArray(bloque.etiquetas)) {
            bloque.etiquetas.forEach(etiqueta => {
                analisis.etiquetasUnicas.add(etiqueta);
                
                // Verificar si es de IA
                if (etiqueta.toLowerCase().includes('inteligencia') || 
                    etiqueta.toLowerCase().includes('artificial')) {
                    analisis.conIA++;
                    analisis.bloquesIA.push(bloque);
                }
            });
        }
        
        // Procesar fechas
        if (bloque.fecha_creacion) {
            const fecha = new Date(bloque.fecha_creacion);
            if (!analisis.fechaMinima || fecha < analisis.fechaMinima) {
                analisis.fechaMinima = fecha;
            }
            if (!analisis.fechaMaxima || fecha > analisis.fechaMaxima) {
                analisis.fechaMaxima = fecha;
            }
        }
    });
    
    analisis.longitudPromedio = datos.length > 0 ? Math.round(longitudTotal / datos.length) : 0;
    analisis.etiquetasArray = Array.from(analisis.etiquetasUnicas);
    
    return analisis;
}

// Función para mostrar análisis detallado
function mostrarAnalisisDetallado(analisis) {
    console.log('📊 ANÁLISIS DETALLADO DE DATOS:');
    console.log(`   - Total bloques: ${analisis.total}`);
    console.log(`   - Bloques de IA: ${analisis.conIA}`);
    console.log(`   - Bloques prioritarios: ${analisis.conPrioridad}`);
    console.log(`   - Etiquetas únicas: ${analisis.etiquetasArray.length}`);
    console.log(`   - Longitud promedio: ${analisis.longitudPromedio} caracteres`);
    
    if (analisis.fechaMinima && analisis.fechaMaxima) {
        console.log(`   - Rango fechas: ${analisis.fechaMinima.toLocaleDateString()} - ${analisis.fechaMaxima.toLocaleDateString()}`);
    }
    
    console.log('🏷️ Etiquetas encontradas:');
    analisis.etiquetasArray.forEach(etiqueta => {
        console.log(`   - "${etiqueta}"`);
    });
    
    if (analisis.bloquesIA.length > 0) {
        console.log('\n🤖 Bloques de Inteligencia Artificial:');
        analisis.bloquesIA.forEach((bloque, index) => {
            const preview = (bloque.contenido || '').substring(0, 100) + '...';
            console.log(`   ${index + 1}. ${preview}`);
            console.log(`      Etiquetas: ${bloque.etiquetas?.join(', ') || 'Sin etiquetas'}`);
        });
    }
}

// Función para probar filtrado específico de IA
async function probarFiltradoIA() {
    const terminosIA = [
        'inteligencia artificial',
        'artificial',
        'inteligencia', 
        'curso',
        'Curso Inteligencia Artificial'
    ];
    
    console.log('🔍 Probando filtrado por términos de IA...');
    
    terminosIA.forEach(termino => {
        try {
            // Simular filtrado manual
            const resultados = window.conocimientoData.filter(bloque => {
                if (!bloque.etiquetas || !Array.isArray(bloque.etiquetas)) {
                    return false;
                }
                
                return bloque.etiquetas.some(etiqueta => 
                    etiqueta.toLowerCase().includes(termino.toLowerCase())
                );
            });
            
            console.log(`   "${termino}": ${resultados.length} resultados`);
            
            if (resultados.length > 0 && termino === 'inteligencia artificial') {
                console.log('     📝 Primer resultado:');
                const primer = resultados[0];
                console.log(`     - ID: ${primer.id}`);
                console.log(`     - Etiquetas: ${primer.etiquetas?.join(', ')}`);
                console.log(`     - Preview: ${(primer.contenido || '').substring(0, 80)}...`);
            }
            
        } catch (error) {
            console.error(`   ❌ Error filtrando "${termino}":`, error);
        }
    });
    
    // Probar función de filtrado del sistema si existe
    if (typeof window.filtrarPorEtiqueta === 'function') {
        console.log('\n🔧 Probando función filtrarPorEtiqueta del sistema...');
        try {
            window.filtrarPorEtiqueta('Curso Inteligencia Artificial');
            console.log('✅ Función filtrarPorEtiqueta ejecutada correctamente');
        } catch (error) {
            console.error('❌ Error en filtrarPorEtiqueta:', error);
        }
    }
}

// Función para probar búsqueda de texto
async function probarBusquedaTexto() {
    const terminosBusqueda = [
        'curso',
        'presencial',
        'duración',
        'costo',
        'módulo',
        'julio'
    ];
    
    console.log('🔎 Probando búsqueda de texto en contenido...');
    
    terminosBusqueda.forEach(termino => {
        try {
            const resultados = window.conocimientoData.filter(bloque => {
                const contenido = (bloque.contenido || '').toLowerCase();
                return contenido.includes(termino.toLowerCase());
            });
            
            console.log(`   "${termino}": ${resultados.length} resultados`);
            
        } catch (error) {
            console.error(`   ❌ Error buscando "${termino}":`, error);
        }
    });
    
    // Probar función de búsqueda del sistema si existe
    if (typeof window.buscarConocimiento === 'function') {
        console.log('\n🔧 Probando función buscarConocimiento del sistema...');
        try {
            const input = document.getElementById('buscar-conocimiento');
            if (input) {
                input.value = 'curso inteligencia artificial';
                window.buscarConocimiento();
                console.log('✅ Función buscarConocimiento ejecutada correctamente');
            } else {
                console.log('⚠️ Input de búsqueda no encontrado');
            }
        } catch (error) {
            console.error('❌ Error en buscarConocimiento:', error);
        }
    }
}

// Función para probar estadísticas
async function probarEstadisticas() {
    if (typeof window.actualizarEstadisticas === 'function') {
        try {
            window.actualizarEstadisticas();
            console.log('✅ Función actualizarEstadisticas ejecutada correctamente');
            
            // Verificar que los elementos se actualizaron
            const elementos = [
                'total-bloques',
                'total-etiquetas'
            ];
            
            elementos.forEach(id => {
                const elemento = document.getElementById(id);
                if (elemento) {
                    console.log(`   - ${id}: ${elemento.textContent}`);
                } else {
                    console.log(`   ⚠️ Elemento ${id} no encontrado`);
                }
            });
            
        } catch (error) {
            console.error('❌ Error en actualizarEstadisticas:', error);
        }
    } else {
        console.log('⚠️ Función actualizarEstadisticas no disponible');
    }
}

// Función para cargar datos de prueba si es necesario
async function cargarDatosPrueba() {
    console.log('📂 Cargando datos de prueba...');
    
    // Datos de prueba basados en la estructura real de Supabase
    const datosPrueba = [
        {
            id: "test-1",
            contenido: "🚨 Curso Intensivo Presencial\n🕒 Duración: 6 horas\n📍 Modalidad: Presencial\n💰 Costo: $1490",
            etiquetas: ["Curso Inteligencia Artificial"],
            fecha_creacion: new Date().toISOString(),
            prioridad: true,
            activo: true,
            nombre_nora: "aura"
        },
        {
            id: "test-2", 
            contenido: "📘 Módulo 1 (2h): Estructura de contenido viral\n🤖 Módulo 2 (4h): IA para marketing",
            etiquetas: ["Curso Inteligencia Artificial"],
            fecha_creacion: new Date().toISOString(),
            prioridad: true,
            activo: true,
            nombre_nora: "aura"
        }
    ];
    
    window.conocimientoData = datosPrueba;
    console.log(`✅ Datos de prueba cargados: ${datosPrueba.length} bloques`);
}

// Función para diagnosticar problemas
async function diagnosticarProblemas() {
    console.log('🔧 DIAGNÓSTICO DE PROBLEMAS:');
    
    // Verificar elementos del DOM
    const elementosRequeridos = [
        'conocimiento-list',
        'total-bloques',
        'total-etiquetas',
        'buscar-conocimiento'
    ];
    
    console.log('📋 Verificando elementos del DOM:');
    elementosRequeridos.forEach(id => {
        const elemento = document.getElementById(id);
        console.log(`   - ${id}: ${elemento ? '✅' : '❌'}`);
    });
    
    // Verificar variables globales
    console.log('\n🌍 Verificando variables globales:');
    const variablesGlobales = [
        'conocimientoData',
        'PANEL_CONFIG',
        'PANEL_STATE'
    ];
    
    variablesGlobales.forEach(variable => {
        console.log(`   - ${variable}: ${window[variable] ? '✅' : '❌'}`);
    });
    
    // Verificar consola por errores
    console.log('\n⚠️ Revisa la consola por errores adicionales');
    console.log('💡 Asegúrate de estar en la página del panel de entrenamiento');
}

// Función auxiliar para ejecutar la prueba paso a paso
window.probarConocimientoIAPasos = async function() {
    console.clear();
    console.log('🚀 Iniciando prueba paso a paso...');
    
    try {
        // Paso 1: Cargar conocimiento
        console.log('\n📥 Paso 1: Cargando conocimiento...');
        if (typeof window.cargarConocimiento === 'function') {
            await window.cargarConocimiento();
        }
        
        // Paso 2: Verificar datos
        console.log('\n🔍 Paso 2: Verificando datos...');
        if (window.conocimientoData) {
            console.log(`Datos disponibles: ${window.conocimientoData.length} bloques`);
            
            // Paso 3: Filtrar por IA
            console.log('\n🤖 Paso 3: Filtrando por IA...');
            const bloquesIA = window.conocimientoData.filter(b => 
                b.etiquetas && b.etiquetas.some(e => 
                    e.toLowerCase().includes('inteligencia') || 
                    e.toLowerCase().includes('artificial')
                )
            );
            console.log(`Bloques de IA encontrados: ${bloquesIA.length}`);
            
            if (bloquesIA.length > 0) {
                console.log('📝 Primer bloque de IA:');
                console.log(bloquesIA[0]);
            }
        }
        
        console.log('\n✅ Prueba paso a paso completada');
        
    } catch (error) {
        console.error('❌ Error en prueba paso a paso:', error);
    }
};

// Exportar funciones principales
window.probarConocimientoIA = probarConocimientoIA;
window.analizarDatosConocimiento = analizarDatosConocimiento;

// Ejecutar automáticamente si se está en el panel
if (document.getElementById('conocimiento-list')) {
    console.log('🎯 Panel de conocimiento detectado - ejecutando prueba automática');
    setTimeout(() => probarConocimientoIA(), 2000);
} else {
    console.log('📝 Para ejecutar la prueba manualmente, usa: probarConocimientoIA()');
    console.log('📝 Para prueba paso a paso, usa: probarConocimientoIAPasos()');
}
