// 🧪 SCRIPT DE PRUEBAS - Etiqueta "curso inteligencia artificial"
console.log('🧪 INICIANDO PRUEBAS DE ETIQUETA: "curso inteligencia artificial"');
console.log('=================================================================');

// 1. Verificar bloques de conocimiento existentes
console.log('\n1️⃣ VERIFICANDO BLOQUES DE CONOCIMIENTO:');

async function obtenerBloques() {
    try {
        const response = await fetch('/aura/conocimiento/listar', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`   ✅ Total de bloques: ${data.conocimiento ? data.conocimiento.length : 0}`);
            return data.conocimiento || [];
        } else {
            console.error('   ❌ Error al obtener bloques:', response.status);
            return [];
        }
    } catch (error) {
        console.error('   ❌ Error de conexión:', error);
        return [];
    }
}

// 2. Filtrar bloques por etiqueta específica
function filtrarPorEtiqueta(bloques, etiqueta) {
    console.log(`\n2️⃣ FILTRANDO POR ETIQUETA: "${etiqueta}"`);
    
    const bloquesFiltrados = bloques.filter(bloque => {
        const etiquetas = bloque.etiquetas || '';
        const etiquetasArray = etiquetas.split(',').map(e => e.trim().toLowerCase());
        const etiquetaBuscada = etiqueta.toLowerCase();
        
        const coincidencia = etiquetasArray.some(e => 
            e.includes(etiquetaBuscada) || etiquetaBuscada.includes(e)
        );
        
        console.log(`   Bloque ID ${bloque.id}: "${bloque.pregunta.substring(0, 50)}..."`);
        console.log(`      Etiquetas: [${etiquetasArray.join(', ')}]`);
        console.log(`      Coincidencia: ${coincidencia ? '✅' : '❌'}`);
        
        return coincidencia;
    });
    
    console.log(`\n   📊 RESULTADO: ${bloquesFiltrados.length} bloques encontrados`);
    return bloquesFiltrados;
}

// 3. Probar diferentes variaciones de búsqueda
function probarVariacionesBusqueda(bloques) {
    console.log('\n3️⃣ PROBANDO VARIACIONES DE BÚSQUEDA:');
    
    const variaciones = [
        'curso inteligencia artificial',
        'curso ia',
        'inteligencia artificial',
        'curso',
        'ia',
        'artificial',
        'inteligencia'
    ];
    
    variaciones.forEach(variacion => {
        console.log(`\n   🔍 Buscando: "${variacion}"`);
        const resultados = filtrarPorEtiqueta(bloques, variacion);
        console.log(`      Encontrados: ${resultados.length} bloques`);
        
        if (resultados.length > 0) {
            resultados.forEach((bloque, index) => {
                console.log(`      ${index + 1}. ID: ${bloque.id}, Pregunta: "${bloque.pregunta.substring(0, 40)}..."`);
            });
        }
    });
}

// 4. Probar filtro de UI (si existe)
function probarFiltroUI() {
    console.log('\n4️⃣ PROBANDO FILTRO DE UI:');
    
    const filtroInput = document.querySelector('#filtro-conocimiento');
    const selectEtiquetas = document.querySelector('#filtro-etiquetas');
    
    if (filtroInput) {
        console.log('   ✅ Campo de filtro encontrado');
        
        // Simular búsqueda
        filtroInput.value = 'curso inteligencia artificial';
        
        // Disparar evento de input
        const evento = new Event('input', { bubbles: true });
        filtroInput.dispatchEvent(evento);
        
        console.log('   🔄 Búsqueda simulada en campo de filtro');
        
        // Verificar resultados después de un momento
        setTimeout(() => {
            const filasVisibles = document.querySelectorAll('#tabla-conocimiento tbody tr:not(.hidden)');
            console.log(`   📊 Filas visibles después del filtro: ${filasVisibles.length}`);
            
            filasVisibles.forEach((fila, index) => {
                const pregunta = fila.querySelector('td:first-child')?.textContent || 'N/A';
                const etiquetas = fila.querySelector('td:nth-child(2)')?.textContent || 'N/A';
                console.log(`      ${index + 1}. Pregunta: "${pregunta.substring(0, 40)}...", Etiquetas: "${etiquetas}"`);
            });
        }, 500);
    } else {
        console.log('   ❌ Campo de filtro no encontrado');
    }
    
    if (selectEtiquetas) {
        console.log('   ✅ Select de etiquetas encontrado');
        
        // Buscar opción que contenga "curso" o "inteligencia"
        const opciones = selectEtiquetas.querySelectorAll('option');
        const opcionCurso = Array.from(opciones).find(opt => 
            opt.textContent.toLowerCase().includes('curso') || 
            opt.textContent.toLowerCase().includes('inteligencia')
        );
        
        if (opcionCurso) {
            console.log(`   🎯 Opción encontrada: "${opcionCurso.textContent}"`);
            selectEtiquetas.value = opcionCurso.value;
            
            // Disparar evento de cambio
            const evento = new Event('change', { bubbles: true });
            selectEtiquetas.dispatchEvent(evento);
            
            console.log('   🔄 Filtro de etiquetas activado');
        } else {
            console.log('   ❌ No se encontró opción relacionada con curso/IA');
        }
    } else {
        console.log('   ❌ Select de etiquetas no encontrado');
    }
}

// 5. Analizar estructura de etiquetas
function analizarEstructuraEtiquetas(bloques) {
    console.log('\n5️⃣ ANALIZANDO ESTRUCTURA DE ETIQUETAS:');
    
    const todasLasEtiquetas = new Set();
    const estadisticas = {
        conEtiquetas: 0,
        sinEtiquetas: 0,
        etiquetasUnicas: new Set(),
        etiquetasFrecuencia: {}
    };
    
    bloques.forEach(bloque => {
        const etiquetas = bloque.etiquetas || '';
        
        if (etiquetas.trim()) {
            estadisticas.conEtiquetas++;
            const etiquetasArray = etiquetas.split(',').map(e => e.trim().toLowerCase());
            
            etiquetasArray.forEach(etiqueta => {
                if (etiqueta) {
                    estadisticas.etiquetasUnicas.add(etiqueta);
                    estadisticas.etiquetasFrecuencia[etiqueta] = 
                        (estadisticas.etiquetasFrecuencia[etiqueta] || 0) + 1;
                }
            });
        } else {
            estadisticas.sinEtiquetas++;
        }
    });
    
    console.log(`   📊 Bloques con etiquetas: ${estadisticas.conEtiquetas}`);
    console.log(`   📊 Bloques sin etiquetas: ${estadisticas.sinEtiquetas}`);
    console.log(`   📊 Etiquetas únicas: ${estadisticas.etiquetasUnicas.size}`);
    
    console.log('\n   🏷️  ETIQUETAS MÁS FRECUENTES:');
    const etiquetasOrdenadas = Object.entries(estadisticas.etiquetasFrecuencia)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);
    
    etiquetasOrdenadas.forEach(([etiqueta, frecuencia]) => {
        const destacar = etiqueta.includes('curso') || etiqueta.includes('inteligencia') || etiqueta.includes('ia');
        console.log(`      ${destacar ? '🎯' : '  '} "${etiqueta}": ${frecuencia} veces`);
    });
    
    // Buscar etiquetas relacionadas con IA/curso
    console.log('\n   🔍 ETIQUETAS RELACIONADAS CON IA/CURSO:');
    const relacionadas = Array.from(estadisticas.etiquetasUnicas).filter(etiqueta =>
        etiqueta.includes('curso') || 
        etiqueta.includes('inteligencia') || 
        etiqueta.includes('ia') || 
        etiqueta.includes('artificial')
    );
    
    relacionadas.forEach(etiqueta => {
        const frecuencia = estadisticas.etiquetasFrecuencia[etiqueta];
        console.log(`      🎯 "${etiqueta}": ${frecuencia} bloques`);
    });
}

// 6. Función principal de pruebas
async function ejecutarPruebas() {
    console.log('\n🚀 EJECUTANDO PRUEBAS COMPLETAS...');
    
    const bloques = await obtenerBloques();
    
    if (bloques.length === 0) {
        console.log('   ❌ No se encontraron bloques de conocimiento');
        return;
    }
    
    // Analizar estructura
    analizarEstructuraEtiquetas(bloques);
    
    // Probar filtrado específico
    const bloquesCursoIA = filtrarPorEtiqueta(bloques, 'curso inteligencia artificial');
    
    // Probar variaciones
    probarVariacionesBusqueda(bloques);
    
    // Probar UI
    probarFiltroUI();
    
    console.log('\n✅ PRUEBAS COMPLETADAS');
    
    return {
        totalBloques: bloques.length,
        bloquesCursoIA: bloquesCursoIA.length,
        bloques: bloques
    };
}

// 7. Funciones de utilidad para pruebas manuales
function buscarPorTexto(texto) {
    console.log(`\n🔍 BÚSQUEDA MANUAL: "${texto}"`);
    
    obtenerBloques().then(bloques => {
        const resultados = bloques.filter(bloque => {
            const buscarEn = [
                bloque.pregunta || '',
                bloque.respuesta || '',
                bloque.etiquetas || ''
            ].join(' ').toLowerCase();
            
            return buscarEn.includes(texto.toLowerCase());
        });
        
        console.log(`   📊 Encontrados: ${resultados.length} bloques`);
        resultados.forEach((bloque, index) => {
            console.log(`   ${index + 1}. ID: ${bloque.id}`);
            console.log(`      Pregunta: "${bloque.pregunta}"`);
            console.log(`      Etiquetas: "${bloque.etiquetas}"`);
            console.log('      ---');
        });
    });
}

function mostrarBloquesConEtiqueta(etiqueta) {
    console.log(`\n📋 BLOQUES CON ETIQUETA: "${etiqueta}"`);
    
    obtenerBloques().then(bloques => {
        const filtrados = filtrarPorEtiqueta(bloques, etiqueta);
        
        filtrados.forEach((bloque, index) => {
            console.log(`\n   ${index + 1}. BLOQUE ID: ${bloque.id}`);
            console.log(`      Pregunta: "${bloque.pregunta}"`);
            console.log(`      Respuesta: "${bloque.respuesta.substring(0, 100)}..."`);
            console.log(`      Etiquetas: "${bloque.etiquetas}"`);
            console.log(`      Fecha: ${bloque.fecha_creacion}`);
        });
    });
}

// Hacer funciones disponibles globalmente
window.ejecutarPruebasEtiqueta = ejecutarPruebas;
window.buscarPorTexto = buscarPorTexto;
window.mostrarBloquesConEtiqueta = mostrarBloquesConEtiqueta;
window.filtrarPorEtiqueta = filtrarPorEtiqueta;
window.obtenerBloques = obtenerBloques;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - ejecutarPruebasEtiqueta() // Ejecutar todas las pruebas');
console.log('   - buscarPorTexto("curso inteligencia artificial") // Búsqueda libre');
console.log('   - mostrarBloquesConEtiqueta("curso") // Ver bloques específicos');
console.log('   - obtenerBloques() // Obtener todos los bloques');

console.log('\n=================================================================');
console.log('🧪 SCRIPT DE PRUEBAS CARGADO - Listo para probar etiquetas');

// Auto-ejecutar pruebas básicas
console.log('\n🔄 EJECUTANDO PRUEBAS AUTOMÁTICAS...');
setTimeout(() => {
    ejecutarPruebas();
}, 1000);
