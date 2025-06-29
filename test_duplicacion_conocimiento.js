// 🧪 SCRIPT DE PRUEBA - Prevención de Duplicación de Conocimiento
console.log('🧪 INICIANDO PRUEBA DE DUPLICACIÓN...');
console.log('============================================');

// 1. Verificar estado inicial
console.log('\n1️⃣ VERIFICANDO ESTADO INICIAL:');
console.log('   eventosConfigurados:', typeof eventosConfigurados !== 'undefined' ? eventosConfigurados : 'Variable no definida');
console.log('   configurarEventosConocimiento:', typeof window.configurarEventosConocimiento);
console.log('   reinicializarEventosConocimiento:', typeof window.reinicializarEventosConocimiento);

// 2. Verificar formulario
console.log('\n2️⃣ VERIFICANDO FORMULARIO:');
const formulario = document.getElementById('form-agregar-conocimiento');
console.log('   Formulario encontrado:', !!formulario);

if (formulario) {
    // Verificar listeners actuales
    const listeners = getEventListeners ? getEventListeners(formulario) : 'getEventListeners no disponible';
    console.log('   Event listeners actuales:', listeners);
}

// 3. Función de prueba para simular múltiples configuraciones
function simularConfiguracionMultiple() {
    console.log('\n🧪 SIMULANDO CONFIGURACIÓN MÚLTIPLE...');
    
    for (let i = 1; i <= 3; i++) {
        console.log(`   Intento ${i}:`);
        if (typeof window.configurarEventosConocimiento === 'function') {
            window.configurarEventosConocimiento();
        }
    }
    
    console.log('   ✅ Simulación completada');
}

// 4. Función de prueba para el formulario
function probarEnvioMultiple() {
    console.log('\n📝 PROBANDO ENVÍO MÚLTIPLE...');
    
    // Llenar formulario
    const contenido = document.getElementById('nuevo-contenido');
    const etiquetas = document.getElementById('nuevas-etiquetas');
    
    if (contenido && etiquetas) {
        contenido.value = 'CONTENIDO DE PRUEBA - ' + new Date().toLocaleTimeString();
        etiquetas.value = 'prueba, duplicacion, test';
        
        console.log('   📝 Formulario llenado');
        console.log('   🚨 ATENCIÓN: El siguiente envío debe crear SOLO UN bloque');
        
        // Simular submit del formulario
        const formulario = document.getElementById('form-agregar-conocimiento');
        if (formulario) {
            console.log('   🚀 Disparando evento submit...');
            formulario.dispatchEvent(new Event('submit'));
        }
    } else {
        console.log('   ❌ Campos del formulario no encontrados');
    }
}

// 5. Función para contar bloques actuales
function contarBloques() {
    const bloques = document.querySelectorAll('.bloque-conocimiento');
    const totalElement = document.getElementById('total-bloques');
    
    console.log(`   📊 Bloques en DOM: ${bloques.length}`);
    console.log(`   📊 Total mostrado: ${totalElement ? totalElement.textContent : 'No disponible'}`);
    
    return bloques.length;
}

// 6. Función de prueba completa
function pruebaCompleta() {
    console.log('\n🎯 EJECUTANDO PRUEBA COMPLETA...');
    
    // Contar bloques antes
    console.log('\n📊 ANTES del envío:');
    const bloquesAntes = contarBloques();
    
    // Simular configuración múltiple
    simularConfiguracionMultiple();
    
    // Probar envío
    probarEnvioMultiple();
    
    // Esperar y contar después
    setTimeout(() => {
        console.log('\n📊 DESPUÉS del envío (después de 3 segundos):');
        const bloquesDespues = contarBloques();
        
        const diferencia = bloquesDespues - bloquesAntes;
        console.log(`\n🎯 RESULTADO:`);
        console.log(`   Bloques agregados: ${diferencia}`);
        
        if (diferencia === 1) {
            console.log('   ✅ ÉXITO: Solo se agregó 1 bloque (sin duplicación)');
        } else if (diferencia > 1) {
            console.log(`   ❌ PROBLEMA: Se agregaron ${diferencia} bloques (duplicación detectada)`);
        } else {
            console.log('   ⚠️  No se agregaron bloques (posible error en el envío)');
        }
        
    }, 3000);
}

// 7. Función para reinicializar en caso de problemas
function limpiarYReinicializar() {
    console.log('\n🧹 LIMPIANDO Y REINICIALIZANDO...');
    
    if (typeof window.reinicializarEventosConocimiento === 'function') {
        window.reinicializarEventosConocimiento();
        console.log('   ✅ Eventos reinicializados');
    } else {
        console.log('   ❌ reinicializarEventosConocimiento no disponible');
    }
}

// Exportar funciones de prueba
window.simularConfiguracionMultiple = simularConfiguracionMultiple;
window.probarEnvioMultiple = probarEnvioMultiple;
window.contarBloques = contarBloques;
window.pruebaCompleta = pruebaCompleta;
window.limpiarYReinicializar = limpiarYReinicializar;

console.log('\n💡 COMANDOS DISPONIBLES:');
console.log('   - simularConfiguracionMultiple() : Simula configuración repetida');
console.log('   - probarEnvioMultiple()          : Prueba envío del formulario');
console.log('   - contarBloques()                : Cuenta bloques actuales');
console.log('   - pruebaCompleta()               : Ejecuta prueba completa');
console.log('   - limpiarYReinicializar()        : Limpia y reinicializa eventos');

console.log('\n⚠️  IMPORTANTE:');
console.log('   - Cambiar a pestaña "Agregar Nuevo" antes de probar');
console.log('   - El envío debe crear SOLO 1 bloque, no 3');
console.log('   - Si hay problemas, ejecutar limpiarYReinicializar()');

console.log('\n============================================');
console.log('🧪 SCRIPT DE PRUEBA CARGADO');
console.log('🎯 Ejecuta pruebaCompleta() para probar');

// Auto-verificación inicial
setTimeout(() => {
    console.log('\n🔍 VERIFICACIÓN AUTOMÁTICA:');
    if (typeof eventosConfigurados !== 'undefined') {
        console.log(`   Estado eventos: ${eventosConfigurados ? 'Configurados' : 'No configurados'}`);
    }
    
    const formulario = document.getElementById('form-agregar-conocimiento');
    if (formulario) {
        console.log('   ✅ Formulario encontrado y listo para pruebas');
    } else {
        console.log('   ⚠️  Formulario no encontrado - cambiar a pestaña "Agregar Nuevo"');
    }
}, 1000);
