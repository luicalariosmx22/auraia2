// 🧪 SCRIPT DE PRUEBAS - Etiqueta "curso inteligencia artificial"
console.log('🧪 INICIANDO PRUEBAS DE ETIQUETAS - "curso inteligencia artificial"');
console.log('================================================================');

// 1. Verificar bloques existentes con esta etiqueta
console.log('\n1️⃣ VERIFICANDO BLOQUES CON ETIQUETA "curso inteligencia artificial":');

function buscarBloquesPorEtiqueta(etiquetaBuscada) {
    const bloques = document.querySelectorAll('.bloque-conocimiento');
    const bloquesEncontrados = [];
    
    console.log(`🔍 Buscando bloques con etiqueta: "${etiquetaBuscada}"`);
    console.log(`📊 Total de bloques en el DOM: ${bloques.length}`);
    
    bloques.forEach((bloque, index) => {
        const etiquetasElement = bloque.querySelector('.etiquetas-bloque, .badge, [class*="etiqueta"]');
        if (etiquetasElement) {
            const etiquetasTexto = etiquetasElement.textContent.toLowerCase();
            if (etiquetasTexto.includes(etiquetaBuscada.toLowerCase())) {
                bloquesEncontrados.push({
                    index: index + 1,
                    elemento: bloque,
                    etiquetas: etiquetasTexto,
                    contenido: bloque.querySelector('.contenido-bloque, .content, p')?.textContent?.substring(0, 100) + '...'
                });
            }
        }
    });
    
    console.log(`✅ Bloques encontrados con "${etiquetaBuscada}": ${bloquesEncontrados.length}`);
    
    bloquesEncontrados.forEach((bloque, i) => {
        console.log(`   Bloque ${i + 1}:`);
        console.log(`     - Posición en DOM: ${bloque.index}`);
        console.log(`     - Etiquetas: ${bloque.etiquetas}`);
        console.log(`     - Contenido: ${bloque.contenido}`);
    });
    
    return bloquesEncontrados;
}

// 2. Probar filtro por etiqueta
console.log('\n2️⃣ PROBANDO FILTRO POR ETIQUETA:');

function probarFiltroEtiqueta(etiqueta) {
    console.log(`🎯 Probando filtro con etiqueta: "${etiqueta}"`);
    
    // Verificar que existe la función de filtro
    if (typeof window.filtrarPorEtiqueta === 'function') {
        console.log('✅ Función filtrarPorEtiqueta disponible');
        
        // Ejecutar filtro
        window.filtrarPorEtiqueta(etiqueta);
        
        // Verificar resultado
        setTimeout(() => {
            const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
            const bloquesOcultos = document.querySelectorAll('.bloque-conocimiento[style*="display: none"]');
            
            console.log(`📊 Resultado del filtro:`);
            console.log(`   - Bloques visibles: ${bloquesVisibles.length}`);
            console.log(`   - Bloques ocultos: ${bloquesOcultos.length}`);
            
            // Verificar que los visibles contienen la etiqueta
            let correctos = 0;
            bloquesVisibles.forEach(bloque => {
                const etiquetasElement = bloque.querySelector('.etiquetas-bloque, .badge, [class*="etiqueta"]');
                if (etiquetasElement && etiquetasElement.textContent.toLowerCase().includes(etiqueta.toLowerCase())) {
                    correctos++;
                }
            });
            
            console.log(`   - Bloques correctamente filtrados: ${correctos}/${bloquesVisibles.length}`);
            
            if (correctos === bloquesVisibles.length) {
                console.log('✅ Filtro funcionando correctamente');
            } else {
                console.log('⚠️ Algunos bloques visibles no contienen la etiqueta');
            }
            
        }, 500);
        
    } else {
        console.log('❌ Función filtrarPorEtiqueta no disponible');
    }
}

// 3. Probar búsqueda por texto
console.log('\n3️⃣ PROBANDO BÚSQUEDA POR TEXTO:');

function probarBusquedaTexto(termino) {
    console.log(`🔍 Probando búsqueda con término: "${termino}"`);
    
    // Verificar que existe la función de búsqueda
    if (typeof window.filtrarConocimiento === 'function') {
        console.log('✅ Función filtrarConocimiento disponible');
        
        // Obtener el campo de búsqueda
        const campoBusqueda = document.getElementById('buscar-conocimiento');
        if (campoBusqueda) {
            // Llenar el campo
            campoBusqueda.value = termino;
            
            // Ejecutar búsqueda
            window.filtrarConocimiento(termino);
            
            // Verificar resultado
            setTimeout(() => {
                const bloquesVisibles = document.querySelectorAll('.bloque-conocimiento:not([style*="display: none"])');
                console.log(`📊 Bloques encontrados con "${termino}": ${bloquesVisibles.length}`);
                
                // Listar los bloques encontrados
                bloquesVisibles.forEach((bloque, i) => {
                    const contenido = bloque.querySelector('.contenido-bloque, .content, p')?.textContent?.substring(0, 80);
                    const etiquetas = bloque.querySelector('.etiquetas-bloque, .badge, [class*="etiqueta"]')?.textContent;
                    console.log(`   ${i + 1}. ${contenido}... | Etiquetas: ${etiquetas}`);
                });
                
            }, 500);
            
        } else {
            console.log('❌ Campo de búsqueda no encontrado');
        }
    } else {
        console.log('❌ Función filtrarConocimiento no disponible');
    }
}

// 4. Probar dropdown de etiquetas
console.log('\n4️⃣ PROBANDO DROPDOWN DE ETIQUETAS:');

function verificarDropdownEtiquetas() {
    console.log('🎯 Verificando dropdown de etiquetas...');
    
    const dropdown = document.getElementById('filtro-etiqueta');
    if (dropdown) {
        console.log('✅ Dropdown encontrado');
        
        const opciones = dropdown.querySelectorAll('option');
        console.log(`📊 Opciones disponibles: ${opciones.length}`);
        
        // Listar opciones
        opciones.forEach((opcion, i) => {
            console.log(`   ${i + 1}. "${opcion.value}" - ${opcion.textContent}`);
        });
        
        // Buscar la opción de "curso inteligencia artificial"
        const opcionCurso = Array.from(opciones).find(opt => 
            opt.value.toLowerCase().includes('curso') && 
            opt.value.toLowerCase().includes('inteligencia')
        );
        
        if (opcionCurso) {
            console.log(`✅ Opción encontrada: "${opcionCurso.value}"`);
            
            // Probar seleccionar esta opción
            dropdown.value = opcionCurso.value;
            dropdown.dispatchEvent(new Event('change'));
            console.log('🎯 Opción seleccionada programáticamente');
            
        } else {
            console.log('⚠️ Opción "curso inteligencia artificial" no encontrada en dropdown');
            
            // Sugerir opciones similares
            const opcionesSimilares = Array.from(opciones).filter(opt => 
                opt.value.toLowerCase().includes('curso') || 
                opt.value.toLowerCase().includes('inteligencia') ||
                opt.value.toLowerCase().includes('artificial')
            );
            
            if (opcionesSimilares.length > 0) {
                console.log('💡 Opciones similares encontradas:');
                opcionesSimilares.forEach(opt => {
                    console.log(`   - "${opt.value}"`);
                });
            }
        }
        
    } else {
        console.log('❌ Dropdown de etiquetas no encontrado');
    }
}

// 5. Crear nuevo bloque con la etiqueta
console.log('\n5️⃣ FUNCIÓN PARA CREAR BLOQUE CON ETIQUETA DE PRUEBA:');

function crearBloqueConEtiqueta() {
    console.log('📝 Creando bloque de prueba con etiqueta "curso inteligencia artificial"...');
    
    // Cambiar a pestaña agregar
    if (typeof window.switchTab === 'function') {
        const botones = document.querySelectorAll('.tab-button');
        const contenidos = document.querySelectorAll('.tab-content');
        window.switchTab('agregar-conocimiento', botones, contenidos);
    }
    
    setTimeout(() => {
        // Llenar formulario
        const contenido = document.getElementById('nuevo-contenido');
        const etiquetas = document.getElementById('nuevas-etiquetas');
        const prioridad = document.getElementById('nueva-prioridad');
        
        if (contenido && etiquetas) {
            contenido.value = `Bloque de prueba para curso de inteligencia artificial. Este contenido incluye información sobre machine learning, deep learning, redes neuronales y aplicaciones prácticas de IA. Creado: ${new Date().toLocaleString()}`;
            
            etiquetas.value = 'curso inteligencia artificial, machine learning, deep learning, IA, educacion';
            
            if (prioridad) {
                prioridad.checked = true;
            }
            
            console.log('✅ Formulario llenado con datos de prueba');
            console.log('💡 Ahora puedes enviar el formulario manualmente o ejecutar enviarFormulario()');
            
            // Disparar evento input para contador
            contenido.dispatchEvent(new Event('input'));
            
        } else {
            console.log('❌ Campos del formulario no encontrados');
        }
    }, 1000);
}

function enviarFormulario() {
    console.log('🚀 Enviando formulario...');
    
    if (typeof window.agregarBloque === 'function') {
        window.agregarBloque();
        console.log('✅ Función agregarBloque ejecutada');
    } else {
        console.log('❌ Función agregarBloque no disponible');
    }
}

// 6. Limpiar filtros
function limpiarFiltros() {
    console.log('🧹 Limpiando filtros...');
    
    // Limpiar búsqueda
    const campoBusqueda = document.getElementById('buscar-conocimiento');
    if (campoBusqueda) {
        campoBusqueda.value = '';
        if (typeof window.filtrarConocimiento === 'function') {
            window.filtrarConocimiento('');
        }
    }
    
    // Limpiar dropdown
    const dropdown = document.getElementById('filtro-etiqueta');
    if (dropdown) {
        dropdown.value = '';
        if (typeof window.filtrarPorEtiqueta === 'function') {
            window.filtrarPorEtiqueta('');
        }
    }
    
    console.log('✅ Filtros limpiados');
}

// Exportar funciones para uso manual
window.buscarBloquesPorEtiqueta = buscarBloquesPorEtiqueta;
window.probarFiltroEtiqueta = probarFiltroEtiqueta;
window.probarBusquedaTexto = probarBusquedaTexto;
window.verificarDropdownEtiquetas = verificarDropdownEtiquetas;
window.crearBloqueConEtiqueta = crearBloqueConEtiqueta;
window.enviarFormulario = enviarFormulario;
window.limpiarFiltros = limpiarFiltros;

// Función principal de pruebas
function ejecutarPruebasEtiquetas() {
    console.log('\n🚀 EJECUTANDO SUITE COMPLETA DE PRUEBAS...');
    
    // Asegurar que estamos en la pestaña correcta
    if (typeof window.switchTab === 'function') {
        const botones = document.querySelectorAll('.tab-button');
        const contenidos = document.querySelectorAll('.tab-content');
        window.switchTab('ver-conocimiento', botones, contenidos);
    }
    
    setTimeout(() => {
        // 1. Buscar bloques existentes
        buscarBloquesPorEtiqueta('curso inteligencia artificial');
        
        setTimeout(() => {
            // 2. Probar filtro
            probarFiltroEtiqueta('curso inteligencia artificial');
            
            setTimeout(() => {
                // 3. Probar búsqueda
                probarBusquedaTexto('inteligencia artificial');
                
                setTimeout(() => {
                    // 4. Verificar dropdown
                    verificarDropdownEtiquetas();
                    
                    setTimeout(() => {
                        // 5. Limpiar al final
                        limpiarFiltros();
                        console.log('\n🎉 SUITE DE PRUEBAS COMPLETADA');
                    }, 2000);
                }, 2000);
            }, 2000);
        }, 1000);
    }, 1000);
}

window.ejecutarPruebasEtiquetas = ejecutarPruebasEtiquetas;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - buscarBloquesPorEtiqueta("curso inteligencia artificial")');
console.log('   - probarFiltroEtiqueta("curso inteligencia artificial")');
console.log('   - probarBusquedaTexto("inteligencia artificial")');
console.log('   - verificarDropdownEtiquetas()');
console.log('   - crearBloqueConEtiqueta()');
console.log('   - enviarFormulario()');
console.log('   - limpiarFiltros()');
console.log('   - ejecutarPruebasEtiquetas()');

console.log('\n🎯 PRUEBAS ESPECÍFICAS RECOMENDADAS:');
console.log('   1. ejecutarPruebasEtiquetas() - Suite completa');
console.log('   2. buscarBloquesPorEtiqueta("curso inteligencia artificial") - Ver bloques existentes');
console.log('   3. probarFiltroEtiqueta("curso inteligencia artificial") - Probar filtrado');
console.log('   4. crearBloqueConEtiqueta() - Crear bloque de prueba');

console.log('\n================================================================');
console.log('🧪 SCRIPT DE PRUEBAS DE ETIQUETAS CARGADO Y LISTO');

// Auto-ejecutar búsqueda inicial
setTimeout(() => {
    console.log('\n🔍 EJECUTANDO BÚSQUEDA INICIAL...');
    buscarBloquesPorEtiqueta('curso inteligencia artificial');
    buscarBloquesPorEtiqueta('inteligencia artificial');
    buscarBloquesPorEtiqueta('curso');
}, 1000);
