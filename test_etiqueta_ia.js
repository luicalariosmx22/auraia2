// 🧪 SCRIPT DE PRUEBAS - Etiqueta "Curso Inteligencia Artificial"
console.log('🧪 INICIANDO PRUEBAS DE ETIQUETA: "curso inteligencia artificial"');
console.log('======================================================================');

// Configuración de la etiqueta de prueba
const ETIQUETA_OBJETIVO = 'curso inteligencia artificial';
const ETIQUETAS_RELACIONADAS = ['curso', 'inteligencia', 'artificial', 'ia', 'machine learning', 'ai'];

// =============================================================================
// 🔍 FUNCIONES DE ANÁLISIS DE CONOCIMIENTO
// =============================================================================

/**
 * Analizar todos los bloques de conocimiento cargados
 */
function analizarConocimientoCargado() {
    console.log('\n1️⃣ ANALIZANDO CONOCIMIENTO CARGADO EN MEMORIA:');
    
    // Verificar si hay datos cargados
    const conocimientoData = window.conocimientoData || [];
    console.log(`   📊 Total de bloques en memoria: ${conocimientoData.length}`);
    
    if (conocimientoData.length === 0) {
        console.log('   ⚠️  No hay datos cargados. Intentando cargar...');
        if (typeof window.cargarConocimiento === 'function') {
            window.cargarConocimiento().then(() => {
                console.log('   ✅ Datos cargados, ejecuta analizarConocimientoCargado() nuevamente');
            });
        }
        return;
    }
    
    // Analizar etiquetas
    const todasLasEtiquetas = [];
    const bloquesConEtiquetaObjetivo = [];
    const bloquesConEtiquetasRelacionadas = [];
    
    conocimientoData.forEach((bloque, index) => {
        const etiquetas = bloque.etiquetas || [];
        todasLasEtiquetas.push(...etiquetas);
        
        console.log(`\n   📝 Bloque ${index + 1}:`);
        console.log(`      ID: ${bloque.id}`);
        console.log(`      Contenido: "${bloque.contenido.substring(0, 50)}..."`);
        console.log(`      Etiquetas: [${etiquetas.join(', ')}]`);
        console.log(`      Prioridad: ${bloque.prioridad ? 'Sí' : 'No'}`);
        console.log(`      Activo: ${bloque.activo ? 'Sí' : 'No'}`);
        
        // Verificar etiqueta objetivo
        const tieneEtiquetaObjetivo = etiquetas.some(etiqueta => 
            etiqueta.toLowerCase().includes(ETIQUETA_OBJETIVO.toLowerCase()) ||
            ETIQUETA_OBJETIVO.toLowerCase().includes(etiqueta.toLowerCase())
        );
        
        if (tieneEtiquetaObjetivo) {
            bloquesConEtiquetaObjetivo.push(bloque);
            console.log(`      🎯 CONTIENE ETIQUETA OBJETIVO: "${ETIQUETA_OBJETIVO}"`);
        }
        
        // Verificar etiquetas relacionadas
        const tieneEtiquetasRelacionadas = etiquetas.some(etiqueta =>
            ETIQUETAS_RELACIONADAS.some(relacionada =>
                etiqueta.toLowerCase().includes(relacionada.toLowerCase())
            )
        );
        
        if (tieneEtiquetasRelacionadas) {
            bloquesConEtiquetasRelacionadas.push(bloque);
            console.log(`      🔗 CONTIENE ETIQUETAS RELACIONADAS`);
        }
    });
    
    // Resumen de análisis
    console.log('\n📊 RESUMEN DEL ANÁLISIS:');
    console.log(`   Total de bloques: ${conocimientoData.length}`);
    console.log(`   Bloques con etiqueta objetivo: ${bloquesConEtiquetaObjetivo.length}`);
    console.log(`   Bloques con etiquetas relacionadas: ${bloquesConEtiquetasRelacionadas.length}`);
    
    // Estadísticas de etiquetas
    const conteoEtiquetas = {};
    todasLasEtiquetas.forEach(etiqueta => {
        conteoEtiquetas[etiqueta] = (conteoEtiquetas[etiqueta] || 0) + 1;
    });
    
    console.log('\n🏷️ TODAS LAS ETIQUETAS ENCONTRADAS:');
    Object.entries(conteoEtiquetas)
        .sort(([,a], [,b]) => b - a)
        .forEach(([etiqueta, count]) => {
            const esRelacionada = ETIQUETAS_RELACIONADAS.some(rel => 
                etiqueta.toLowerCase().includes(rel.toLowerCase())
            );
            const marca = esRelacionada ? '🎯' : '  ';
            console.log(`   ${marca} "${etiqueta}": ${count} bloques`);
        });
    
    return {
        total: conocimientoData.length,
        conEtiquetaObjetivo: bloquesConEtiquetaObjetivo,
        conEtiquetasRelacionadas: bloquesConEtiquetasRelacionadas,
        todasLasEtiquetas: Object.keys(conteoEtiquetas)
    };
}

/**
 * Probar sistema de filtrado por etiquetas
 */
function probarFiltradoPorEtiquetas() {
    console.log('\n2️⃣ PROBANDO SISTEMA DE FILTRADO:');
    
    // Cambiar a pestaña ver conocimiento
    if (typeof window.switchTab === 'function') {
        const botones = document.querySelectorAll('.tab-button');
        const contenidos = document.querySelectorAll('.tab-content');
        window.switchTab('ver-conocimiento', botones, contenidos);
        console.log('   ✅ Cambiado a pestaña "Ver Conocimiento"');
    }
    
    setTimeout(() => {
        // Probar filtro de etiquetas
        const filtroEtiqueta = document.getElementById('filtro-etiqueta');
        if (filtroEtiqueta) {
            console.log('   📋 Opciones disponibles en filtro:');
            Array.from(filtroEtiqueta.options).forEach((option, index) => {
                console.log(`      ${index}: "${option.value}" - ${option.text}`);
            });
            
            // Buscar opciones relacionadas
            const opcionesRelacionadas = Array.from(filtroEtiqueta.options).filter(option =>
                ETIQUETAS_RELACIONADAS.some(rel =>
                    option.value.toLowerCase().includes(rel.toLowerCase())
                )
            );
            
            console.log('\n   🎯 Opciones relacionadas con IA encontradas:');
            opcionesRelacionadas.forEach(option => {
                console.log(`      ✅ "${option.value}"`);
            });
            
            // Probar filtrado automático
            if (opcionesRelacionadas.length > 0) {
                const primeraOpcion = opcionesRelacionadas[0];
                console.log(`\n   🧪 Probando filtro con: "${primeraOpcion.value}"`);
                
                filtroEtiqueta.value = primeraOpcion.value;
                filtroEtiqueta.dispatchEvent(new Event('change'));
                
                setTimeout(() => {
                    verificarResultadosFiltro(primeraOpcion.value);
                }, 500);
            }
            
        } else {
            console.log('   ❌ Filtro de etiquetas no encontrado');
        }
    }, 1000);
}

/**
 * Verificar resultados del filtro aplicado
 */
function verificarResultadosFiltro(etiquetaFiltrada) {
    console.log(`\n🔍 VERIFICANDO RESULTADOS PARA: "${etiquetaFiltrada}"`);
    
    const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
    const bloquesOcultos = document.querySelectorAll('.bloque-conocimiento[style*="display: none"]');
    
    console.log(`   📊 Bloques visibles: ${bloquesVisibles.length}`);
    console.log(`   📊 Bloques ocultos: ${bloquesOcultos.length}`);
    
    if (bloquesVisibles.length > 0) {
        console.log('\n   📝 CONTENIDO DE BLOQUES VISIBLES:');
        bloquesVisibles.forEach((bloque, index) => {
            const contenido = bloque.querySelector('.contenido-bloque')?.textContent?.substring(0, 50) || 'Sin contenido';
            const etiquetas = bloque.querySelector('.etiquetas-bloque')?.textContent || 'Sin etiquetas';
            console.log(`      ${index + 1}. "${contenido}..." | Etiquetas: ${etiquetas}`);
        });
    } else {
        console.log('   ⚠️  No hay bloques visibles con esta etiqueta');
    }
}

/**
 * Probar búsqueda de texto
 */
function probarBusquedaTexto() {
    console.log('\n3️⃣ PROBANDO BÚSQUEDA DE TEXTO:');
    
    const buscarInput = document.getElementById('buscar-conocimiento');
    if (buscarInput) {
        const terminosBusqueda = ['inteligencia artificial', 'curso', 'ia', 'machine learning'];
        
        terminosBusqueda.forEach((termino, index) => {
            setTimeout(() => {
                console.log(`\n   🔍 Buscando: "${termino}"`);
                buscarInput.value = termino;
                buscarInput.dispatchEvent(new Event('input'));
                
                setTimeout(() => {
                    const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
                    console.log(`      📊 Resultados encontrados: ${bloquesVisibles.length}`);
                    
                    if (bloquesVisibles.length > 0) {
                        bloquesVisibles.forEach((bloque, i) => {
                            const contenido = bloque.querySelector('.contenido-bloque')?.textContent?.substring(0, 40) || '';
                            console.log(`         ${i + 1}. "${contenido}..."`);
                        });
                    }
                }, 300);
                
            }, index * 2000);
        });
        
        // Limpiar búsqueda al final
        setTimeout(() => {
            buscarInput.value = '';
            buscarInput.dispatchEvent(new Event('input'));
            console.log('\n   🧹 Búsqueda limpiada');
        }, terminosBusqueda.length * 2000 + 1000);
        
    } else {
        console.log('   ❌ Campo de búsqueda no encontrado');
    }
}

/**
 * Crear bloque de prueba con etiqueta objetivo
 */
function crearBloqueEtiquetaObjetivo() {
    console.log('\n4️⃣ CREANDO BLOQUE DE PRUEBA CON ETIQUETA OBJETIVO:');
    
    // Cambiar a pestaña agregar
    if (typeof window.switchTab === 'function') {
        const botones = document.querySelectorAll('.tab-button');
        const contenidos = document.querySelectorAll('.tab-content');
        window.switchTab('agregar-conocimiento', botones, contenidos);
        console.log('   ✅ Cambiado a pestaña "Agregar Nuevo"');
    }
    
    setTimeout(() => {
        const contenido = document.getElementById('nuevo-contenido');
        const etiquetas = document.getElementById('nuevas-etiquetas');
        const prioridad = document.getElementById('nueva-prioridad');
        
        if (contenido && etiquetas) {
            const contenidoPrueba = `Este es un bloque de prueba sobre ${ETIQUETA_OBJETIVO}. ` +
                `Contiene información sobre inteligencia artificial, machine learning, ` +
                `deep learning y tecnologías de IA. Creado automáticamente para pruebas ` +
                `el ${new Date().toLocaleString()}.`;
            
            contenido.value = contenidoPrueba;
            etiquetas.value = `${ETIQUETA_OBJETIVO}, ia, machine learning, prueba, automatico`;
            if (prioridad) prioridad.checked = true;
            
            console.log('   ✅ Formulario llenado con:');
            console.log(`      📝 Contenido: "${contenidoPrueba.substring(0, 50)}..."`);
            console.log(`      🏷️ Etiquetas: "${etiquetas.value}"`);
            console.log(`      ⭐ Prioridad: ${prioridad?.checked ? 'Sí' : 'No'}`);
            
            // Disparar evento de contador de caracteres
            contenido.dispatchEvent(new Event('input'));
            
            console.log('\n   💡 LISTO PARA ENVIAR:');
            console.log('      - Revisa el contenido y etiquetas');
            console.log('      - Ejecuta enviarBloqueEtiquetaObjetivo() para crear el bloque');
            
        } else {
            console.log('   ❌ Campos del formulario no encontrados');
        }
    }, 1000);
}

/**
 * Enviar bloque con etiqueta objetivo
 */
function enviarBloqueEtiquetaObjetivo() {
    console.log('\n🚀 ENVIANDO BLOQUE CON ETIQUETA OBJETIVO:');
    
    if (typeof window.agregarBloque === 'function') {
        console.log('   📤 Ejecutando agregarBloque()...');
        window.agregarBloque();
        
        // Verificar resultado después de un tiempo
        setTimeout(() => {
            console.log('\n   🔍 Verificando resultado del envío...');
            if (typeof window.cargarConocimiento === 'function') {
                window.cargarConocimiento().then(() => {
                    console.log('   ✅ Conocimiento recargado');
                    setTimeout(() => {
                        analizarConocimientoCargado();
                    }, 1000);
                });
            }
        }, 3000);
        
    } else {
        console.log('   ❌ Función agregarBloque no disponible');
    }
}

/**
 * Ejecutar suite completa de pruebas
 */
function ejecutarPruebasCompletas() {
    console.log('\n🎯 EJECUTANDO SUITE COMPLETA DE PRUEBAS...');
    console.log('===============================================');
    
    // Paso 1: Cargar conocimiento
    console.log('\n📚 PASO 1: Cargando conocimiento...');
    if (typeof window.cargarConocimiento === 'function') {
        window.cargarConocimiento().then(() => {
            console.log('✅ Conocimiento cargado');
            
            // Paso 2: Analizar conocimiento
            setTimeout(() => {
                console.log('\n🔍 PASO 2: Analizando conocimiento...');
                analizarConocimientoCargado();
                
                // Paso 3: Probar filtrado
                setTimeout(() => {
                    console.log('\n🔧 PASO 3: Probando filtrado...');
                    probarFiltradoPorEtiquetas();
                    
                    // Paso 4: Probar búsqueda
                    setTimeout(() => {
                        console.log('\n🔍 PASO 4: Probando búsqueda...');
                        probarBusquedaTexto();
                    }, 3000);
                    
                }, 2000);
                
            }, 1000);
            
        }).catch(error => {
            console.error('❌ Error cargando conocimiento:', error);
        });
    } else {
        console.log('❌ Función cargarConocimiento no disponible');
    }
}

// =============================================================================
// 🌍 EXPORTAR FUNCIONES GLOBALMENTE
// =============================================================================

window.analizarConocimientoCargado = analizarConocimientoCargado;
window.probarFiltradoPorEtiquetas = probarFiltradoPorEtiquetas;
window.probarBusquedaTexto = probarBusquedaTexto;
window.crearBloqueEtiquetaObjetivo = crearBloqueEtiquetaObjetivo;
window.enviarBloqueEtiquetaObjetivo = enviarBloqueEtiquetaObjetivo;
window.ejecutarPruebasCompletas = ejecutarPruebasCompletas;
window.verificarResultadosFiltro = verificarResultadosFiltro;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - ejecutarPruebasCompletas()     : Suite completa de pruebas');
console.log('   - analizarConocimientoCargado()  : Analiza bloques en memoria');
console.log('   - probarFiltradoPorEtiquetas()   : Prueba filtros de etiquetas');
console.log('   - probarBusquedaTexto()          : Prueba búsqueda de texto');
console.log('   - crearBloqueEtiquetaObjetivo()  : Crea bloque de prueba');
console.log('   - enviarBloqueEtiquetaObjetivo() : Envía bloque creado');

console.log('\n🎯 OBJETIVO PRINCIPAL:');
console.log(`   Probar etiqueta: "${ETIQUETA_OBJETIVO}"`);
console.log(`   Etiquetas relacionadas: [${ETIQUETAS_RELACIONADAS.join(', ')}]`);

console.log('\n======================================================================');
console.log('🧪 SCRIPT DE PRUEBAS CARGADO - Ejecuta ejecutarPruebasCompletas()');

// Auto-ejecución si se desea
setTimeout(() => {
    console.log('\n🚀 INICIANDO PRUEBAS AUTOMÁTICAS EN 3 SEGUNDOS...');
    console.log('   (Puedes cancelar ejecutando: clearTimeout() en consola)');
    
    const autoTimeout = setTimeout(() => {
        ejecutarPruebasCompletas();
    }, 3000);
    
    window.cancelarAutoPruebas = () => {
        clearTimeout(autoTimeout);
        console.log('⏹️ Pruebas automáticas canceladas');
    };
    
}, 1000);
